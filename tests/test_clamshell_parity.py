"""Heavy-duty clamshell parity: the rendered plate must approximate the
idealized reference plate.

The authoritative reference is the idealized heavy-duty plate under
``plug references/3 Prong Heavy Ideal Sample/`` ("...Plug_Bottom.stl",
66.6 x 73.7 x 4.5 mm). This suite renders the v7 model as a single clamshell
plate at the heavy-duty plug preset and asserts *loose* parity: the clamshell
is a fresh parametric re-derivation of the reference, not a mesh clone, so
only the gross envelope, the feature inventory (finger / zip / velcro
cutouts), and the two grip gaps are pinned — and those with generous
tolerances.

Skips (rather than fails) when OpenSCAD or the reference STL is unavailable.

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
IDEAL_PLATE = (
    PROJECT_ROOT
    / "plug references"
    / "3 Prong Heavy Ideal Sample"
    / "Plug Puller_3_Prong_Idealized_Sample_Plug_Bottom.stl"
)
HD_PRESET = "Heavy-duty extension cord - NEMA 5-15"


def _loop_area(loop: np.ndarray) -> float:
    x, y = loop[:, 0], loop[:, 1]
    return abs(0.5 * np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))


def _classify(mesh) -> Dict[str, Any]:
    """Measure a clamshell plate mesh in the reference frame (X centred,
    Y/Z minima at 0): envelope, watertightness, and the interior cutout
    inventory (finger lobes, zip holes, velcro slots) sliced mid-thickness."""
    lo, hi = mesh.bounds
    mesh.apply_translation([-(lo[0] + hi[0]) / 2, -lo[1], -lo[2]])
    lo, hi = mesh.bounds
    env = (hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2])

    section = mesh.section(plane_origin=[0, 0, env[2] / 2], plane_normal=[0, 0, 1])
    loops = sorted(
        (np.asarray(p)[:, :2] for p in section.discrete),
        key=_loop_area,
        reverse=True,
    )
    # Drop the two largest loops (the arm outlines); the rest are cutouts.
    cutouts = loops[2:]
    finger, ziph, velcro = [], [], []
    for lp in cutouts:
        area = _loop_area(lp)
        w = float(lp[:, 0].max() - lp[:, 0].min())
        h = float(lp[:, 1].max() - lp[:, 1].min())
        cx, cy = float(lp[:, 0].mean()), float(lp[:, 1].mean())
        aspect = max(w, h) / max(1e-6, min(w, h))
        entry = {"area": area, "w": w, "h": h, "cx": cx, "cy": cy}
        if aspect > 1.6:
            velcro.append(entry)
        elif max(w, h) > 12:
            finger.append(entry)
        elif area > 3:
            ziph.append(entry)
    return {
        "envelope": env,
        "watertight": bool(mesh.is_watertight),
        "finger": finger,
        "zip": ziph,
        "velcro": velcro,
        "section_poly": loops,
    }


def _gap_at(loops: List[np.ndarray], y: float) -> float:
    """Inner-edge gap (= 2 * minimum |x| of the solid boundary) at height y."""
    from shapely.geometry import LineString, Polygon
    from shapely.ops import unary_union

    solids = [Polygon(lp).buffer(0) for lp in loops[:2]]
    poly = unary_union(solids)
    cut = poly.boundary.intersection(LineString([(-40, y), (40, y)]))
    if cut.is_empty:
        return float("nan")
    xs = []
    for g in getattr(cut, "geoms", [cut]):
        xs.extend(np.asarray(g.coords)[:, 0].tolist())
    xs = [abs(x) for x in xs]
    return 2 * min(xs) if xs else float("nan")


@pytest.fixture(scope="module")
def ideal_dims() -> Dict[str, Any]:
    if not IDEAL_PLATE.exists():
        pytest.skip(f"Idealized clamshell plate missing: {IDEAL_PLATE}")
    import trimesh

    return _classify(trimesh.load(IDEAL_PLATE, force="mesh"))


@pytest.fixture(scope="module")
def rendered_dims(scad_file: Path, openscad_runner, tmp_path_factory) -> Dict[str, Any]:
    import trimesh

    out = tmp_path_factory.mktemp("clamshell_parity") / "plate.stl"
    result = openscad_runner.generate_stl(
        scad_file=scad_file,
        output_stl=out,
        parameters={
            "plug_preset": HD_PRESET,
            "render_mode": "Clamshell Plate",
            "quality": 64,
        },
    )
    assert result.success, (
        f"Clamshell plate render failed (returncode={result.returncode}):\n"
        f"{result.stderr}"
    )
    return _classify(trimesh.load(out, force="mesh"))


@pytest.mark.requires_openscad
@pytest.mark.slow
class TestClamshellParity:
    """Loose envelope + feature-inventory parity vs the idealized plate."""

    def test_watertight(self, rendered_dims) -> None:
        assert rendered_dims["watertight"], "Rendered clamshell plate is not watertight."

    def test_envelope(self, ideal_dims, rendered_dims) -> None:
        ref, got = ideal_dims["envelope"], rendered_dims["envelope"]
        assert got[0] == pytest.approx(ref[0], abs=2.5), (
            f"Plate width X {got[0]:.2f} vs ideal {ref[0]:.2f} (> 2.5 mm)"
        )
        assert got[1] == pytest.approx(ref[1], abs=2.5), (
            f"Plate length Y {got[1]:.2f} vs ideal {ref[1]:.2f} (> 2.5 mm)"
        )
        assert got[2] == pytest.approx(ref[2], abs=1.0), (
            f"Plate thickness Z {got[2]:.2f} vs ideal {ref[2]:.2f} (> 1.0 mm)"
        )

    def test_feature_inventory(self, ideal_dims, rendered_dims) -> None:
        assert len(rendered_dims["finger"]) == 2, (
            f"Expected 2 finger lobes, got {len(rendered_dims['finger'])}."
        )
        assert len(rendered_dims["zip"]) == len(ideal_dims["zip"]) == 6, (
            f"Expected 6 zip holes on both plates "
            f"(ideal {len(ideal_dims['zip'])}, got {len(rendered_dims['zip'])})."
        )
        assert len(rendered_dims["velcro"]) == 2, (
            f"Expected 2 velcro / reduction slots, got "
            f"{len(rendered_dims['velcro'])}."
        )

    def test_finger_diameter(self, ideal_dims, rendered_dims) -> None:
        ref_d = np.mean([f["w"] for f in ideal_dims["finger"]])
        got_d = np.mean([f["w"] for f in rendered_dims["finger"]])
        assert got_d == pytest.approx(ref_d, abs=2.5), (
            f"Finger bore diameter {got_d:.2f} vs ideal {ref_d:.2f} (> 2.5 mm)"
        )

    def test_grip_gaps(self, ideal_dims, rendered_dims) -> None:
        ref_loops, got_loops = ideal_dims["section_poly"], rendered_dims["section_poly"]
        # Cable channel (near the cord end) and the grip zone (near the tip).
        for label, y, tol in [("cable channel", 15.0, 2.5), ("grip zone", 55.0, 3.5)]:
            ref_gap = _gap_at(ref_loops, y)
            got_gap = _gap_at(got_loops, y)
            assert got_gap == pytest.approx(ref_gap, abs=tol), (
                f"{label} gap at y={y}: {got_gap:.2f} vs ideal {ref_gap:.2f} "
                f"(> {tol} mm)"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
