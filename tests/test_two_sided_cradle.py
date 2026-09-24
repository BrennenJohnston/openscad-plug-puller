"""Two-sided puller: the cradle edge for Rounded sides (R1 phase B5).

With ``plug_sides = "Rounded sides"`` the gap between the arms is widest on
the face where the two plates meet (the plug's width plus
``plate_grip_clearance``) and narrows in a straight slope toward the outer
face, by the cradle depth on each side, so two stacked plates form a
diamond-shaped channel that centres a rounded plug. The teeth ride the slope.

The depth guard (plan section 4.3, row 3, as the owner set it at Q-20) lets
the outer-face gap come down to the cord channel's width but never below it:
cradle per side = min(plate_cradle_depth, plate_thickness,
                      (mating-face gap - cord channel) / 2).

* File defaults (20 mm wide, 4 mm cord): mating face 20 + 0.5 = 20.5 mm; the
  guard allows (20.5 - 4.8) / 2 = 7.85, so the full 2.5 mm applies.
* The owner's USB-C numbers (13 mm wide, 7 mm cord): mating face 13.5 mm;
  the guard allows (13.5 - 7.8) / 2 = 2.85, so the full 2.5 mm applies:
  8.5 mm at the outer face, 11.0 mm half way, 13.5 mm where the plates meet.

The gap at height z (Z = 0 is the outer face, the plate is 4 mm thick) is
mating gap - 2 x cradle x (1 - z / 4). The slope is built from 10 slices of
0.4 mm at the default quality, each cut at its mid-height value, so the
sections sit at slice mid-heights (1.4, 2.6 and 3.8 mm), all above the
1.2 mm roundover on the outer-face edge, and are measured on a line just past
the plug's back end, clear of the teeth. The heavy-duty preset keeps its
straight, biting edge (Q-08).

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TWO_SIDED_SCAD = PROJECT_ROOT / "src" / "Plug_Puller_Two_Sided.scad"
FIXTURE = PROJECT_ROOT / "tests" / "fixtures" / "two_sided_plate"
USB_C = {
    "plug_preset": "Measure my plug",
    "measure_plug_length": 23,
    "measure_plug_width_prong_end": 13,
    "measure_plug_width_cord_end": 13,
    "measure_cord_thickness": 7,
    "plug_sides": "Rounded sides",
    "attachment": "Zip ties",
}
WC13 = "CRADLE SHALLOWER THAN ASKED - PLUG NARROW"
NO_BITE = "NO GRIP BITE - PLUG WONT BE HELD"
HEIGHTS = (1.4, 2.6, 3.8)
CASES = {
    # name: (parameters, plug length, expected gaps at HEIGHTS in mm)
    "file_defaults": ({}, 25.5, (17.25, 18.75, 20.25)),
    "usb_c": (USB_C, 23, (10.25, 11.75, 13.25)),
}


def _render(runner, tmp_path: Path, name: str, params: Dict[str, object]):
    import trimesh

    assert TWO_SIDED_SCAD.exists(), f"SCAD file missing: {TWO_SIDED_SCAD}"
    out = tmp_path / f"{name}.stl"
    result = runner.generate_stl(scad_file=TWO_SIDED_SCAD, output_stl=out, parameters=params)
    assert result.success, f"Render failed (returncode={result.returncode}):\n{result.stderr}"
    return trimesh.load(out, force="mesh"), (result.stdout or "") + (result.stderr or "")


def _plates(mesh, count: int):
    """The ``count`` largest bodies: the plates, without any warning text."""
    parts = sorted(mesh.split(only_watertight=False), key=lambda p: abs(p.volume), reverse=True)
    return parts[:count]


def _warnings(console: str):
    return [line.strip() for line in console.splitlines() if "WARNING:" in line]


def _gap(plate, z: float, y: float) -> float:
    """Gap between the arms (2 x the inner edge nearest the mirror line) on the
    line at height z and distance y from the cord end."""
    from shapely.geometry import LineString, Polygon
    from shapely.ops import unary_union

    section = plate.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    assert section is not None, f"No section at z = {z}"
    loops = [np.asarray(p)[:, :2] for p in section.discrete]
    region = unary_union([Polygon(lp).buffer(0) for lp in loops if len(lp) >= 3])
    cut = region.boundary.intersection(LineString([(-60, y), (60, y)]))
    xs = [abs(x) for g in getattr(cut, "geoms", [cut]) for x in np.asarray(g.coords)[:, 0]]
    assert xs, f"No arm edge on the line y = {y} at z = {z}"
    return 2 * min(xs)


@pytest.mark.requires_openscad
@pytest.mark.slow
@pytest.mark.parametrize("case", sorted(CASES))
def test_cradle_gaps_at_three_heights(openscad_runner, tmp_path, case) -> None:
    params, plug_length, expected = CASES[case]
    mesh, console = _render(openscad_runner, tmp_path, case, {**params, "render_mode": "One plate"})
    plate = _plates(mesh, 1)[0]
    length = float(re.search(r"plate length = ([0-9.]+)", console).group(1))
    y = length - plug_length + 0.6
    measured = {z: round(_gap(plate, z, y), 3) for z in HEIGHTS}
    print(f"\n{case}: gap between the arms at y = {y:.1f} mm, by height (mm): {measured}")
    for z, want in zip(HEIGHTS, expected):
        assert measured[z] == pytest.approx(want, abs=0.3), (
            f"{case}: at z = {z} mm the gap is {measured[z]} mm; the cradle expects {want} mm."
        )


@pytest.mark.requires_openscad
@pytest.mark.slow
def test_both_layouts_watertight(openscad_runner, tmp_path) -> None:
    pair, _ = _render(openscad_runner, tmp_path, "usbc_pair", {**USB_C, "render_mode": "Full"})
    plates = _plates(pair, 2)
    assert len(plates) == 2 and all(p.is_watertight for p in plates), (
        "The cradled pair must be two watertight plates."
    )
    one, _ = _render(openscad_runner, tmp_path, "usbc_one", {**USB_C, "render_mode": "One plate"})
    assert _plates(one, 1)[0].is_watertight, "The cradled single plate must be watertight."


@pytest.mark.requires_openscad
@pytest.mark.slow
def test_wc13_when_the_guard_clamps(openscad_runner, tmp_path) -> None:
    params = {
        "measure_plug_width_prong_end": 8,
        "measure_plug_width_cord_end": 8,
        "measure_cord_thickness": 4,
        "plate_cradle_depth": 3.5,
        "attachment": "Zip ties",
        "render_mode": "One plate",
    }
    _mesh, console = _render(openscad_runner, tmp_path, "clamped", params)
    assert any(WC13 in line for line in _warnings(console)), (
        f"A cradle deeper than the plug allows must print WC-13; warnings: {_warnings(console)}"
    )
    _mesh, console = _render(openscad_runner, tmp_path, "defaults", {"render_mode": "One plate"})
    assert not any(WC13 in line for line in _warnings(console)), (
        "At the defaults the cradle fits; WC-13 must stay silent."
    )


@pytest.mark.requires_openscad
@pytest.mark.slow
def test_bite_warning_only_where_the_bite_applies(openscad_runner, tmp_path) -> None:
    base = {"plate_grip_bite": 0, "render_mode": "One plate"}
    _mesh, console = _render(openscad_runner, tmp_path, "rounded", {**base, "plug_sides": "Rounded sides"})
    assert not any(NO_BITE in line for line in _warnings(console)), (
        "Rounded sides ignore plate_grip_bite, so its warning must stay silent."
    )
    _mesh, console = _render(openscad_runner, tmp_path, "flat", {**base, "plug_sides": "Flat sides"})
    assert any(NO_BITE in line for line in _warnings(console)), (
        "Flat sides with a zero bite must still print the no-bite warning."
    )


@pytest.mark.requires_openscad
@pytest.mark.slow
def test_preset_plate_unchanged(openscad_runner, tmp_path) -> None:
    import trimesh

    params = json.loads((FIXTURE / "params.json").read_text(encoding="utf-8"))["parameters"]
    got, _ = _render(openscad_runner, tmp_path, "preset", params)
    ref = trimesh.load(FIXTURE / "reference.stl", force="mesh")
    assert abs(got.volume - ref.volume) < 1e-6 and abs(got.area - ref.area) < 1e-6, (
        "The heavy-duty preset keeps its straight, biting edge (Q-08)."
    )
