"""Regenerate the golden STL fixtures under tests/fixtures/<name>/.

For each fixture directory containing a ``params.json``, this script:

1. Renders ``src/Plug_Puller_Parametric.scad`` with the fixture
   parameters via ``tests.openscad_runner.OpenSCADRunner``.
2. Writes the resulting STL to ``<fixture>/reference.stl``.
3. Updates ``<fixture>/metadata.json`` with provenance: OpenSCAD version,
   Manifold backend flag, current ISO date, and the trimesh-measured volume,
   surface area, bounding box, and watertightness so reviewers can sanity
   check a regeneration without re-running pytest.

Run manually after intentional SCAD changes:

    python scripts/regenerate_fixtures.py

Or to limit which fixtures are regenerated:

    python scripts/regenerate_fixtures.py --only standard small_plug

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import logging
import sys
from pathlib import Path
from typing import List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tests.openscad_runner import OpenSCADRunner  # noqa: E402

logger = logging.getLogger(__name__)


def regenerate(only: List[str] | None = None, verbose: bool = False) -> int:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    runner = OpenSCADRunner()
    logger.info("OpenSCAD: %s", runner.version_string)
    logger.info("Manifold backend: %s", runner.use_manifold)

    scad = PROJECT_ROOT / "src" / "Plug_Puller_Parametric.scad"
    if not scad.exists():
        logger.error("SCAD not found: %s", scad)
        return 2

    fixtures_dir = PROJECT_ROOT / "tests" / "fixtures"
    fixture_dirs = sorted(p for p in fixtures_dir.iterdir() if p.is_dir())
    if only:
        wanted = set(only)
        fixture_dirs = [p for p in fixture_dirs if p.name in wanted]
        missing = wanted - {p.name for p in fixture_dirs}
        if missing:
            logger.error("Unknown fixtures: %s", sorted(missing))
            return 2

    failures: list[str] = []
    for fixture in fixture_dirs:
        params_path = fixture / "params.json"
        if not params_path.exists():
            logger.warning("Skipping %s (no params.json)", fixture.name)
            continue
        with open(params_path, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
        parameters = payload.get("parameters", payload)

        output = fixture / "reference.stl"
        logger.info("Rendering fixture '%s' -> %s", fixture.name, output)
        result = runner.generate_stl(scad, output, parameters)
        if not result.success:
            failures.append(fixture.name)
            logger.error(
                "  FAILED (rc=%s) %s", result.returncode, result.stderr[-400:]
            )
            continue

        # Compute provenance + sanity metrics.
        try:
            import trimesh

            mesh = trimesh.load(output, force="mesh")
            volume = float(mesh.volume) if isinstance(mesh, trimesh.Trimesh) else None
            area = float(mesh.area) if isinstance(mesh, trimesh.Trimesh) else None
            bbox = mesh.bounds.tolist() if isinstance(mesh, trimesh.Trimesh) else None
            watertight = (
                bool(mesh.is_watertight) if isinstance(mesh, trimesh.Trimesh) else None
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("trimesh measurement failed for %s: %s", fixture.name, exc)
            volume = area = bbox = watertight = None

        metadata = {
            "fixture": fixture.name,
            "generated_at_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(),
            "openscad_version": runner.version_string,
            "manifold_backend": runner.use_manifold,
            "render_duration_seconds": round(result.duration_seconds, 3),
            "stl_size_bytes": output.stat().st_size if output.exists() else 0,
            "trimesh_properties": {
                "volume_mm3": volume,
                "surface_area_mm2": area,
                "bounding_box_mm": bbox,
                "is_watertight": watertight,
            },
            "parameters": parameters,
        }
        with open(fixture / "metadata.json", "w", encoding="utf-8") as fh:
            json.dump(metadata, fh, indent=2)
        logger.info(
            "  OK (rc=0, %.2fs, %d bytes, watertight=%s)",
            result.duration_seconds,
            output.stat().st_size,
            watertight,
        )

    if failures:
        logger.error("Failed fixtures: %s", failures)
        return 1
    logger.info("All fixtures regenerated successfully.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--only",
        nargs="+",
        help="Limit regeneration to these fixture names (default: all).",
    )
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    return regenerate(only=args.only, verbose=args.verbose)


if __name__ == "__main__":
    raise SystemExit(main())
