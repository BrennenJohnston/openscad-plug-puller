"""Two-sided puller extraction parity (R1 phase A2).

``src/Plug_Puller_Two_Sided.scad`` is the clamshell lifted out of the unified
``src/Plug_Puller_Parametric.scad``. At the heavy-duty preset its plate must
be the same object as the golden fixture
``tests/fixtures/two_sided_plate/reference.stl`` (a byte copy of the old
``clamshell_plate`` fixture). "Same" means the fixture comparator passes and
volume, surface area and bounds agree to 6 decimals. STL bytes and facet
counts are never compared: identical renders triangulate differently.

The finger-bore table renders the two-sided file at Small / Medium / Large at
the preset and prints the three bore widths (run with ``-s``): 17.5 / 21.0 /
24.0 mm, the numbers phase A2 measured in both files. Since phase C1 the
clamshell is gone from the unified file, so its old side-by-side comparison
lives on only as those numbers.

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
PRESET_PARAMS = {"plug_preset": HD_PRESET, "render_mode": "One plate", "quality": 64}
# Finger bore at the preset, as A2 measured it in both files (mm).
BORES = {"Small": 17.5, "Medium": 21.0, "Large": 24.0}


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
def test_finger_bore_table(openscad_runner, tmp_path) -> None:
    scad = _require_two_sided_scad()
    bores: Dict[str, float] = {}
    for size in BORES:
        mesh = _render(openscad_runner, scad, tmp_path / f"two_sided_{size}.stl", {**PRESET_PARAMS, "size": size})
        fingers = _classify(mesh)["finger"]
        assert len(fingers) == 2, f"{size}: expected 2 finger bores, got {len(fingers)}"
        bores[size] = sum(f["w"] for f in fingers) / 2
    print("\nFinger bore width at the heavy-duty preset (mm):")
    for size, width in bores.items():
        print(f"  {size:6s}  two-sided {width:.3f}")
    for size, expected in BORES.items():
        assert bores[size] == pytest.approx(expected, abs=1e-3), (
            f"{size}: finger bore {bores[size]:.3f} mm, A2 measured {expected} mm"
        )
