"""Two-sided puller extraction parity (R1 phase A2).

``src/Plug_Puller_Two_Sided.scad`` is the clamshell lifted out of the unified
``src/Plug_Puller_Parametric.scad``. At the heavy-duty preset its plate must
be the same object as the golden fixture
``tests/fixtures/two_sided_plate/reference.stl`` (a byte copy of the
``clamshell_plate`` fixture) and as the unified file's own render of the same
parameters. "Same" means the fixture comparator passes and volume, surface
area and bounds agree to 6 decimals. STL bytes and facet counts are never
compared: identical renders triangulate differently.

The finger-bore table renders both files at Small / Medium / Large and prints
the six bore widths (run with ``-s``). Medium must match; a Small or Large
difference is not a failure here but the finding the owner decides at Gate A.

These tests FAIL, never skip, when the two-sided file is missing.

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import pytest

from tests.test_clamshell_parity import _classify

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TWO_SIDED_SCAD = PROJECT_ROOT / "src" / "Plug_Puller_Two_Sided.scad"
FIXTURE_STL = PROJECT_ROOT / "tests" / "fixtures" / "two_sided_plate" / "reference.stl"
HD_PRESET = "Heavy-duty extension cord - NEMA 5-15"
# Each file names its single-plate mode differently until the clamshell leaves
# the unified file (phase C1).
PRESET_PARAMS = {"plug_preset": HD_PRESET, "render_mode": "One plate", "quality": 64}
UNIFIED_PARAMS = {"plug_preset": HD_PRESET, "render_mode": "Clamshell Plate", "quality": 64}
SIZES = ["Small", "Medium", "Large"]


def _require_two_sided_scad() -> Path:
    assert TWO_SIDED_SCAD.exists(), f"SCAD file missing: {TWO_SIDED_SCAD}"
    return TWO_SIDED_SCAD


def _render(runner, scad: Path, out: Path, params: Dict[str, object]):
    import trimesh

    result = runner.generate_stl(scad_file=scad, output_stl=out, parameters=params)
    assert result.success, (
        f"Render of {scad.name} failed (returncode={result.returncode}):\n{result.stderr}"
    )
    return trimesh.load(out, force="mesh")


def _assert_same_geometry(a, b, label: str) -> None:
    assert abs(a.volume - b.volume) < 1e-6, f"{label}: volume {a.volume:.6f} vs {b.volume:.6f}"
    assert abs(a.area - b.area) < 1e-6, f"{label}: area {a.area:.6f} vs {b.area:.6f}"
    bounds_diff = float(abs(a.bounds - b.bounds).max())
    assert bounds_diff < 1e-6, f"{label}: bounds differ by {bounds_diff:.6f} mm"


@pytest.mark.requires_openscad
@pytest.mark.slow
def test_preset_plate_matches_fixture(openscad_runner, mesh_comparator, tmp_path) -> None:
    import trimesh

    scad = _require_two_sided_scad()
    out = tmp_path / "two_sided_preset.stl"
    plate = _render(openscad_runner, scad, out, PRESET_PARAMS)
    comparison = mesh_comparator.compare(FIXTURE_STL, out)
    assert comparison.passed, "; ".join(comparison.failures)
    _assert_same_geometry(plate, trimesh.load(FIXTURE_STL, force="mesh"), "two-sided vs fixture")


@pytest.mark.requires_openscad
@pytest.mark.slow
def test_preset_plate_matches_unified_file(scad_file, openscad_runner, tmp_path) -> None:
    scad = _require_two_sided_scad()
    new = _render(openscad_runner, scad, tmp_path / "two_sided.stl", PRESET_PARAMS)
    old = _render(openscad_runner, scad_file, tmp_path / "unified.stl", UNIFIED_PARAMS)
    _assert_same_geometry(new, old, "two-sided vs unified file")


@pytest.mark.requires_openscad
@pytest.mark.slow
def test_finger_bore_table(scad_file, openscad_runner, tmp_path) -> None:
    scad = _require_two_sided_scad()
    bores: Dict[tuple, float] = {}
    for size in SIZES:
        for label, path, base in (("unified", scad_file, UNIFIED_PARAMS), ("two-sided", scad, PRESET_PARAMS)):
            params = {**base, "size": size}
            mesh = _render(openscad_runner, path, tmp_path / f"{label}_{size}.stl", params)
            fingers = _classify(mesh)["finger"]
            assert len(fingers) == 2, f"{label} {size}: expected 2 finger bores, got {len(fingers)}"
            bores[(label, size)] = sum(f["w"] for f in fingers) / 2
    print("\nFinger bore width at the heavy-duty preset (mm):")
    for size in SIZES:
        print(
            f"  {size:6s}  unified {bores[('unified', size)]:.3f}"
            f"  two-sided {bores[('two-sided', size)]:.3f}"
        )
    assert bores[("two-sided", "Medium")] == pytest.approx(
        bores[("unified", "Medium")], abs=1e-6
    )
