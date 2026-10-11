"""Every two-sided `plug_preset` renders clean with its own numbers and sides.

The two-sided puller's dropdown carries the plugs the owner chose, with
the labels the owner wrote. Each preset fills in the numbers measured with a
caliper on its own plug: the length, the width at the prong end and at the
cord end, how far the head keeps the prong-end width, and the cord; and it
carries its own sides: the heavy-duty extension cord keeps Flat sides and
the grip bite (its plate is the golden fixture), the USB-C laptop tip builds
Rounded sides with its own cradle depth, the lamp and standard plugs build
Flat sides.

For every preset this suite renders one plate and reads the derived-values
echo block: no ``WARNING:`` line, a watertight mesh, the grip gap at each end
equal to the preset's width there plus twice its grip term (the default
``plate_grip_clearance`` / 2 per side with Rounded sides, the default
``plate_grip_bite`` per side with Flat sides) or the cord channel plus 1 mm
per side where that floor is wider, the head length, and the cradle depth
the preset carries.

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TWO_SIDED_SCAD = PROJECT_ROOT / "src" / "Plug_Puller_Two_Sided.scad"

# The dropdown's presets in Customizer order (the owner's choice of plugs and labels), with the
# plug numbers each fills in (mm: length, width at the prong end, width at the
# cord end, head length, cord), its sides and, with Rounded sides, its cradle.
PRESETS: Dict[str, Dict[str, object]] = {
    "Heavy-duty extension cord - NEMA 5-15": {
        "length": 51.0, "width_prong_end": 26.56, "width_cord_end": 24.5, "head": 23.0, "cord": 8.25,
        "sides": "Flat sides", "cradle": 0.0,
    },
    "USB-C laptop tip": {
        "length": 17.0, "width_prong_end": 10.25, "width_cord_end": 10.25, "head": 0.0, "cord": 6.1,
        "sides": "Rounded sides", "cradle": 1.9,
    },
    "Flat 2-prong lamp plug - NEMA 1-15": {
        "length": 32.5, "width_prong_end": 20.0, "width_cord_end": 11.1, "head": 15.2, "cord": 7.0,
        "sides": "Flat sides", "cradle": 0.0,
    },
    "Standard 3-prong plug - NEMA 5-15": {
        "length": 46.1, "width_prong_end": 24.66, "width_cord_end": 13.6, "head": 15.6, "cord": 9.25,
        "sides": "Flat sides", "cradle": 0.0,
    },
}

# The file's defaults the grip term comes from (the presets never change them).
DEFAULT_GRIP_BITE = -1.0          # per side, Flat sides and presets with Flat sides
DEFAULT_GRIP_CLEARANCE = 0.5      # total, Rounded sides: half per side
DEFAULT_CABLE_CLEARANCE = 0.8     # added to the cord for the cord channel
GAP_TOLERANCE = 0.05


def _grip_term(sides: str) -> float:
    return DEFAULT_GRIP_CLEARANCE / 2 if sides == "Rounded sides" else DEFAULT_GRIP_BITE


def _expected_gap(spec: Dict[str, object], width: float) -> float:
    """The grip gap at one end: the plug's width there plus twice the grip
    term, never closer than 1 mm per side outside the cord channel."""
    channel = max(2.0, spec["cord"] + DEFAULT_CABLE_CLEARANCE)
    return max(channel + 2.0, width + 2 * _grip_term(spec["sides"]))


def _echo_value(console: str, label: str) -> float:
    match = re.search(rf'"\s*{re.escape(label)} = ([-\d.]+)', console)
    assert match, f"the console has no line for {label!r}:\n{console[-1500:]}"
    return float(match.group(1))


def _render(runner, tmp_path: Path, label: str):
    assert TWO_SIDED_SCAD.exists(), f"SCAD file missing: {TWO_SIDED_SCAD}"
    out = tmp_path / "preset_plate.stl"
    result = runner.generate_stl(
        scad_file=TWO_SIDED_SCAD,
        output_stl=out,
        parameters={"plug_preset": label, "render_mode": "One plate", "quality": 64},
    )
    assert result.success, f"Render failed (returncode={result.returncode}):\n{result.stderr}"
    console = (result.stdout or "") + (result.stderr or "")
    return out, console


def test_preset_table_labels_have_no_parentheses() -> None:
    offenders = [label for label in PRESETS if "(" in label or ")" in label]
    assert not offenders, f"dropdown labels must not contain parentheses: {offenders}"


@pytest.mark.requires_openscad
@pytest.mark.slow
@pytest.mark.parametrize("label", list(PRESETS))
def test_preset_renders_clean_with_its_own_numbers_and_sides(openscad_runner, tmp_path, label) -> None:
    import trimesh

    spec = PRESETS[label]
    out, console = _render(openscad_runner, tmp_path, label)

    warnings: List[str] = [line.strip() for line in console.splitlines() if "WARNING:" in line]
    assert not warnings, f"{label}: the preset prints a tag: {warnings}"

    mesh = trimesh.load(out, force="mesh")
    assert mesh.is_watertight, f"{label}: the plate is not watertight"

    expected_gap = _expected_gap(spec, spec["width_prong_end"])
    gap = _echo_value(console, "grip gap at the prong end")
    assert abs(gap - expected_gap) <= GAP_TOLERANCE, (
        f"{label}: grip gap at the prong end {gap} mm, expected {expected_gap} mm "
        f"(width {spec['width_prong_end']} plus 2 x the {spec['sides']} grip term)")

    expected_cord_gap = _expected_gap(spec, spec["width_cord_end"])
    cord_gap = _echo_value(console, "grip gap at the cord end")
    assert abs(cord_gap - expected_cord_gap) <= GAP_TOLERANCE, (
        f"{label}: grip gap at the cord end {cord_gap} mm, expected {expected_cord_gap} mm")

    head = _echo_value(console, "plug head length")
    assert abs(head - spec["head"]) <= GAP_TOLERANCE, (
        f"{label}: plug head length {head} mm, expected {spec['head']} mm")

    cradle = _echo_value(console, "cradle depth per side")
    assert abs(cradle - spec["cradle"]) <= GAP_TOLERANCE, (
        f"{label}: cradle depth per side {cradle} mm, expected {spec['cradle']} mm for {spec['sides']}")

    plate_length = _echo_value(console, "plate length")
    assert plate_length >= spec["length"] + 11 - GAP_TOLERANCE, (
        f"{label}: plate length {plate_length} mm is shorter than the plug plus its 11 mm run")
