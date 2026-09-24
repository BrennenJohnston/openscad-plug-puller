"""Two-sided puller: both plates in one download (R1 phase B3).

The owner chose "Both plates in one STL" (Q-04): with the default
``print_layout = "Both plates"`` the file exports the two identical plates
side by side, so one file prints the whole tool. ``"One plate"`` keeps the
single plate, which is also what the hidden ``render_mode = "One plate"``
renders for the golden fixture.

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TWO_SIDED_SCAD = PROJECT_ROOT / "src" / "Plug_Puller_Two_Sided.scad"
FIXTURE_STL = PROJECT_ROOT / "tests" / "fixtures" / "two_sided_plate" / "reference.stl"
HD_PRESET = "Heavy-duty extension cord - NEMA 5-15"
LAYOUT_LINE = "PRINT LAYOUT: both plates side by side - flip one after printing"


def _render(runner, tmp_path: Path, name: str, layout: str):
    import trimesh

    assert TWO_SIDED_SCAD.exists(), f"SCAD file missing: {TWO_SIDED_SCAD}"
    out = tmp_path / f"{name}.stl"
    params = {"plug_preset": HD_PRESET, "render_mode": "Full", "print_layout": layout}
    result = runner.generate_stl(scad_file=TWO_SIDED_SCAD, output_stl=out, parameters=params)
    assert result.success, f"Render failed (returncode={result.returncode}):\n{result.stderr}"
    console = (result.stdout or "") + (result.stderr or "")
    return trimesh.load(out, force="mesh"), console


@pytest.mark.requires_openscad
@pytest.mark.slow
def test_both_plates_by_default(openscad_runner, tmp_path) -> None:
    import trimesh

    mesh, console = _render(openscad_runner, tmp_path, "pair", "Both plates")
    bodies = mesh.split(only_watertight=False)
    assert len(bodies) == 2, f"Expected the two plates as 2 bodies, got {len(bodies)}."
    assert all(b.is_watertight for b in bodies), "Every plate in the pair must be watertight."
    reference = trimesh.load(FIXTURE_STL, force="mesh")
    total = sum(b.volume for b in bodies)
    assert total == pytest.approx(2 * reference.volume, rel=1e-3), (
        f"The pair must be two fixture plates: {total:.3f} vs 2 x {reference.volume:.3f} mm^3"
    )
    left, right = sorted(bodies, key=lambda b: b.bounds[0][0])
    assert left.bounds[1][0] < right.bounds[0][0], "The two plates must not touch."
    assert LAYOUT_LINE in console, "The console must say the pair was built and one plate flips."


@pytest.mark.requires_openscad
@pytest.mark.slow
def test_one_plate_layout(openscad_runner, tmp_path) -> None:
    import trimesh

    mesh, console = _render(openscad_runner, tmp_path, "single", "One plate")
    assert len(mesh.split(only_watertight=False)) == 1, "One plate must be one body."
    reference = trimesh.load(FIXTURE_STL, force="mesh")
    assert abs(mesh.volume - reference.volume) < 1e-6
    assert abs(mesh.area - reference.area) < 1e-6
    assert LAYOUT_LINE not in console
