"""Trimesh-based mesh comparison for plug-puller v5 STL validation.

The plug-puller pipeline only has one generator (OpenSCAD itself), so the
"comparison" is really determinism / regression: assert that re-rendering the
same parameter set produces the same volume, surface area, bounding-box
extent, and watertightness as the committed golden fixture.

Tolerances are intentionally tight (see ``tests/compare_config.json``) because
OpenSCAD with the Manifold backend is deterministic up to floating-point noise
within a single version. The thresholds exist to absorb future toolchain
updates rather than to admit large drifts.

CloudCompare numeric-deviation (Hausdorff-like) is intentionally omitted here;
the braille generator needs it because it compares two independent code paths
(SCAD vs. JS web renderer). Plug-puller does not.

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
import trimesh

logger = logging.getLogger(__name__)


def binary_stl_facets(path: Path) -> Optional[int]:
    """The facet count of a binary STL, or None when the file is not one: a
    binary STL is an 80-byte header, a 4-byte facet count and 50 bytes per
    facet, so its size is exactly 84 plus 50 times the count."""
    size = Path(path).stat().st_size
    if size < 84:
        return None
    with Path(path).open("rb") as fh:
        fh.seek(80)
        count = int.from_bytes(fh.read(4), "little")
    return count if size == 84 + 50 * count else None


STL_RECORD = np.dtype([("normal", "<f4", (3,)), ("corners", "<f4", (3, 3)), ("attribute", "<u2")])


def drop_collapsed_triangles(path: Path) -> int:
    """Rewrite a binary STL without the triangles whose corners coincide.
    Binary STL stores 32-bit coordinates, so an edge of OpenSCAD's shorter
    than about 0.00001 mm collapses into a triangle with no area, which opens
    the mesh where it meets its neighbors; dropping it closes the mesh again
    and moves no surface. Returns how many triangles were dropped; the header
    and every other triangle stay byte for byte."""
    path = Path(path)
    if binary_stl_facets(path) is None:
        raise ValueError(f"not a binary STL: {path}")
    data = path.read_bytes()
    records = np.frombuffer(data, dtype=STL_RECORD, offset=84)
    c = records["corners"]
    collapsed = (np.all(c[:, 0] == c[:, 1], axis=1) | np.all(c[:, 1] == c[:, 2], axis=1)
                 | np.all(c[:, 2] == c[:, 0], axis=1))
    dropped = int(collapsed.sum())
    if dropped:
        kept = records[~collapsed]
        path.write_bytes(data[:80] + len(kept).to_bytes(4, "little") + kept.tobytes())
    return dropped


def same_shape(a: Union[Path, trimesh.Trimesh], b: Union[Path, trimesh.Trimesh],
               rel: float = 1e-6, bounds_mm: float = 1e-4) -> bool:
    """True when two meshes are the same shape for the purpose of keeping a
    committed STL: both watertight, volume and surface area equal to one part
    in a million, and every bound within 0.0001 mm. Two renders of the same
    model meet this, and so does a text STL beside its binary copy, whose
    coordinates are 32-bit floats."""
    meshes = [m if isinstance(m, trimesh.Trimesh) else trimesh.load(m, force="mesh") for m in (a, b)]
    if not all(isinstance(m, trimesh.Trimesh) and m.is_watertight for m in meshes):
        return False
    ma, mb = meshes

    def close(x: float, y: float) -> bool:
        return abs(x - y) <= rel * max(abs(x), abs(y))

    return (close(float(ma.volume), float(mb.volume)) and close(float(ma.area), float(mb.area))
            and bool(np.all(np.abs(ma.bounds - mb.bounds) <= bounds_mm)))


@dataclass
class MeshProperties:
    """Aggregate of trimesh measurements that survive STL round-trip."""

    volume: float
    surface_area: float
    bounding_box: np.ndarray  # shape (2, 3): [[xmin, ymin, zmin], [xmax, ymax, zmax]]
    face_count: int
    vertex_count: int
    is_watertight: bool
    centroid: np.ndarray

    def bbox_extent(self) -> np.ndarray:
        return self.bounding_box[1] - self.bounding_box[0]


@dataclass
class ComparisonResult:
    """Outcome of comparing a freshly-rendered mesh against the golden fixture."""

    passed: bool
    reference_properties: MeshProperties
    test_properties: MeshProperties

    volume_diff_percent: float
    surface_area_diff_percent: float
    bounding_box_diff_mm: float
    face_count_diff: int
    vertex_count_diff: int
    watertightness_match: bool

    failures: List[str] = field(default_factory=list)
    comparison_time_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        def props_to_dict(p: MeshProperties) -> Dict[str, Any]:
            return {
                "volume_mm3": p.volume,
                "surface_area_mm2": p.surface_area,
                "bounding_box_mm": p.bounding_box.tolist(),
                "bbox_extent_mm": p.bbox_extent().tolist(),
                "face_count": p.face_count,
                "vertex_count": p.vertex_count,
                "is_watertight": p.is_watertight,
                "centroid_mm": p.centroid.tolist(),
            }

        return {
            "passed": self.passed,
            "reference_properties": props_to_dict(self.reference_properties),
            "test_properties": props_to_dict(self.test_properties),
            "differences": {
                "volume_diff_percent": self.volume_diff_percent,
                "surface_area_diff_percent": self.surface_area_diff_percent,
                "bounding_box_diff_mm": self.bounding_box_diff_mm,
                "face_count_diff": self.face_count_diff,
                "vertex_count_diff": self.vertex_count_diff,
                "watertightness_match": self.watertightness_match,
            },
            "failures": self.failures,
            "comparison_time_seconds": self.comparison_time_seconds,
        }


class MeshComparator:
    """Configurable trimesh comparator.

    Args:
        config: Dict parsed from ``tests/compare_config.json``. Expected keys:
            ``tolerances`` (volume.percent, surface_area.percent,
            bounding_box.mm) and ``required_checks`` (per-metric ``required``
            booleans).
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.tolerances = config["tolerances"]
        self.required_checks = config["required_checks"]

    @staticmethod
    def load_mesh(stl_path: Path) -> trimesh.Trimesh:
        if not stl_path.exists():
            raise FileNotFoundError(f"STL file not found: {stl_path}")
        try:
            mesh = trimesh.load(stl_path, force="mesh")
        except Exception as exc:  # noqa: BLE001
            raise ValueError(f"Failed to load STL {stl_path}: {exc}") from exc
        if not isinstance(mesh, trimesh.Trimesh):
            raise ValueError(
                f"STL did not load as a Trimesh (got {type(mesh).__name__}): {stl_path}"
            )
        logger.debug(
            "Loaded mesh: %d faces, %d vertices",
            mesh.faces.shape[0],
            mesh.vertices.shape[0],
        )
        return mesh

    @staticmethod
    def extract_properties(mesh: trimesh.Trimesh) -> MeshProperties:
        return MeshProperties(
            volume=float(mesh.volume),
            surface_area=float(mesh.area),
            bounding_box=np.asarray(mesh.bounds, dtype=float),
            face_count=int(len(mesh.faces)),
            vertex_count=int(len(mesh.vertices)),
            is_watertight=bool(mesh.is_watertight),
            centroid=np.asarray(mesh.centroid, dtype=float),
        )

    def compare(self, reference_stl: Path, test_stl: Path) -> ComparisonResult:
        start = time.time()

        ref_mesh = self.load_mesh(reference_stl)
        test_mesh = self.load_mesh(test_stl)
        ref_props = self.extract_properties(ref_mesh)
        test_props = self.extract_properties(test_mesh)

        volume_diff_pct = (
            abs(ref_props.volume - test_props.volume) / ref_props.volume * 100.0
            if ref_props.volume > 0
            else 0.0
        )
        area_diff_pct = (
            abs(ref_props.surface_area - test_props.surface_area)
            / ref_props.surface_area
            * 100.0
            if ref_props.surface_area > 0
            else 0.0
        )

        ref_extent = ref_props.bbox_extent()
        test_extent = test_props.bbox_extent()
        bbox_diff = float(np.max(np.abs(ref_extent - test_extent)))

        face_diff = abs(ref_props.face_count - test_props.face_count)
        vertex_diff = abs(ref_props.vertex_count - test_props.vertex_count)
        watertight_match = ref_props.is_watertight == test_props.is_watertight

        failures: List[str] = []

        if self.required_checks.get("volume", {}).get("required", True):
            tol = self.tolerances["volume"]["percent"]
            if volume_diff_pct > tol:
                failures.append(
                    f"Volume difference {volume_diff_pct:.3f}% exceeds "
                    f"tolerance {tol}%"
                )

        if self.required_checks.get("surface_area", {}).get("required", True):
            tol = self.tolerances["surface_area"]["percent"]
            if area_diff_pct > tol:
                failures.append(
                    f"Surface area difference {area_diff_pct:.3f}% exceeds "
                    f"tolerance {tol}%"
                )

        if self.required_checks.get("bounding_box", {}).get("required", True):
            tol = self.tolerances["bounding_box"]["mm"]
            if bbox_diff > tol:
                failures.append(
                    f"Bounding-box extent difference {bbox_diff:.4f}mm exceeds "
                    f"tolerance {tol}mm"
                )

        watertight_cfg = self.required_checks.get("watertightness", {})
        if watertight_cfg.get("required", True):
            # `must_match: true` means the test mesh must NOT regress to a
            # less-watertight state than the reference. A reference that is
            # itself non-watertight (e.g. a model with a known tessellation
            # artifact) still produces a meaningful regression test as long
            # as the new render reproduces the same defect.
            if not watertight_match:
                if ref_props.is_watertight and not test_props.is_watertight:
                    failures.append(
                        "Watertightness regression: reference is watertight but "
                        "test mesh is not — likely a real defect introduced "
                        "since the golden STL was committed."
                    )
                else:
                    failures.append(
                        "Watertightness mismatch: "
                        f"ref={ref_props.is_watertight}, "
                        f"test={test_props.is_watertight}"
                    )
            if (
                watertight_cfg.get("require_test_watertight", False)
                and not test_props.is_watertight
            ):
                failures.append(
                    "Test mesh is not watertight; the comparison config "
                    "has `required_checks.watertightness.require_test_watertight` "
                    "set, which forbids any non-watertight output."
                )

        duration = time.time() - start
        return ComparisonResult(
            passed=len(failures) == 0,
            reference_properties=ref_props,
            test_properties=test_props,
            volume_diff_percent=volume_diff_pct,
            surface_area_diff_percent=area_diff_pct,
            bounding_box_diff_mm=bbox_diff,
            face_count_diff=face_diff,
            vertex_count_diff=vertex_diff,
            watertightness_match=watertight_match,
            failures=failures,
            comparison_time_seconds=duration,
        )


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Compare two STL meshes (trimesh).")
    parser.add_argument("reference", type=Path, help="Reference STL")
    parser.add_argument("test", type=Path, help="Test STL")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("tests/compare_config.json"),
        help="Comparison config JSON",
    )
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        with open(args.config, "r", encoding="utf-8") as fh:
            config = json.load(fh)
        comparator = MeshComparator(config)
        logger.info("Comparing: %s vs %s", args.reference.name, args.test.name)
        result = comparator.compare(args.reference, args.test)

        print("\n" + "=" * 70)
        print("MESH COMPARISON RESULTS")
        print("=" * 70)
        print(f"Status: {'PASS' if result.passed else 'FAIL'}")
        print(f"Volume difference:       {result.volume_diff_percent:.3f}%")
        print(f"Surface area difference: {result.surface_area_diff_percent:.3f}%")
        print(f"Bounding box difference: {result.bounding_box_diff_mm:.4f} mm")
        print(f"Face count difference:   {result.face_count_diff}")
        print(f"Vertex count difference: {result.vertex_count_diff}")
        print(f"Watertightness match:    {'Yes' if result.watertightness_match else 'No'}")
        if result.failures:
            print("\nFailures:")
            for f in result.failures:
                print(f"  - {f}")
        print(f"\nComparison time: {result.comparison_time_seconds:.2f}s")
        print("=" * 70)

        if args.output_json:
            with open(args.output_json, "w", encoding="utf-8") as fh:
                json.dump(result.to_dict(), fh, indent=2)
            logger.info("Results saved to %s", args.output_json)

        return 0 if result.passed else 1
    except Exception as exc:  # noqa: BLE001
        logger.error("Error: %s", exc, exc_info=args.verbose)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
