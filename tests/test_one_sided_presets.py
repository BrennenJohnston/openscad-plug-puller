"""Every one-sided `plug_preset` thinner than 24 mm renders clean with its own numbers.

The one-sided puller's dropdown carries the plugs the owner chose at R2's
Gate A (Q-38) with the labels of Q-39. Each preset fills in the plug's six
numbers (length; width at the prong end and at the cord end; thickness at
both ends; cord). Only plugs thinner than 24 mm belong here: the heavy-duty
extension cord stays in the dropdown as the signpost to the two-sided file
and prints W-20 by design, so it is not in this table.

The green confirmation tag is preview-only geometry and never reaches a CLI
render or its console, so this suite reads the derived-values echo block
instead: the pocket runs the plug's length (D-19b), the hook slot is the cord
plus its 0.7625 mm clearance (D-3), and the wall notch is the prong-end width
plus twice the 0.835 mm sliding clearance (D-12). Together they prove the
preset's numbers reached the routing.

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ONE_SIDED_SCAD = PROJECT_ROOT / "src" / "Plug_Puller_Parametric.scad"

# Presets thinner than 24 mm, in Customizer order, with their six numbers (mm).
PRESETS: Dict[str, Dict[str, float]] = {
    "Flat 2-prong lamp plug - NEMA 1-15": {
        "length": 37.0, "width_prong_end": 25.0, "width_cord_end": 11.2,
        "thickness_prong_end": 18.6, "thickness_cord_end": 8.6, "cord": 3.6,
    },
    "Standard 3-prong plug - NEMA 5-15": {
        "length": 46.2, "width_prong_end": 26.6, "width_cord_end": 13.4,
        "thickness_prong_end": 18.9, "thickness_cord_end": 15.0, "cord": 7.0,
    },
    "Wide 2-prong appliance plug - NEMA 1-15": {
        "length": 38, "width_prong_end": 34, "width_cord_end": 34,
        "thickness_prong_end": 16, "thickness_cord_end": 16, "cord": 5,
    },
}

FIT_CORD_CLEARANCE = 0.7625    # src/fit_measured.scad, D-3
FIT_SLIDE_CLEARANCE = 0.835    # src/fit_measured.scad, D-12 (per side)
TOLERANCE = 1e-3


def _derived(console: str, key: str) -> float:
    match = re.search(rf'"fit_derived: {re.escape(key)}=([-\d.]+)"', console)
    assert match, f"the console has no fit_derived line for {key!r}:\n{console[-1500:]}"
    return float(match.group(1))


def _render(runner, tmp_path: Path, label: str):
    assert ONE_SIDED_SCAD.exists(), f"SCAD file missing: {ONE_SIDED_SCAD}"
    out = tmp_path / "preset_full.stl"
    result = runner.generate_stl(
        scad_file=ONE_SIDED_SCAD,
        output_stl=out,
        parameters={"plug_preset": label, "size": "Medium", "render_mode": "Full", "quality": 64},
    )
    assert result.success, f"Render failed (returncode={result.returncode}):\n{result.stderr}"
    console = (result.stdout or "") + (result.stderr or "")
    return out, console


def test_preset_table_labels_have_no_parentheses() -> None:
    offenders = [label for label in PRESETS if "(" in label or ")" in label]
    assert not offenders, f"dropdown labels must not contain parentheses: {offenders}"


def test_preset_table_plugs_are_thinner_than_24_mm() -> None:
    thick = [label for label, spec in PRESETS.items()
             if max(spec["thickness_prong_end"], spec["thickness_cord_end"]) >= 24]
    assert not thick, f"a plug 24 mm thick or more belongs to the two-sided file: {thick}"


@pytest.mark.requires_openscad
@pytest.mark.slow
@pytest.mark.parametrize("label", list(PRESETS))
def test_preset_renders_clean_with_its_own_numbers(openscad_runner, tmp_path, label) -> None:
    import trimesh

    spec = PRESETS[label]
    out, console = _render(openscad_runner, tmp_path, label)

    warnings: List[str] = [line.strip() for line in console.splitlines() if "WARNING:" in line]
    assert not warnings, f"{label}: the preset prints a tag: {warnings}"

    mesh = trimesh.load(out, force="mesh")
    assert mesh.is_watertight, f"{label}: the tool is not watertight"

    pocket_depth = _derived(console, "pocket_depth")
    assert abs(pocket_depth - spec["length"]) <= TOLERANCE, (
        f"{label}: pocket depth {pocket_depth} mm, expected the plug length {spec['length']} mm")

    hook_slot = _derived(console, "t_hook_base_gap")
    assert abs(hook_slot - (spec["cord"] + FIT_CORD_CLEARANCE)) <= TOLERANCE, (
        f"{label}: hook slot {hook_slot} mm, expected the cord {spec['cord']} plus {FIT_CORD_CLEARANCE}")

    notch = _derived(console, "plug_wall_notch_width")
    expected_notch = spec["width_prong_end"] + 2 * FIT_SLIDE_CLEARANCE
    assert abs(notch - expected_notch) <= TOLERANCE, (
        f"{label}: wall notch {notch} mm, expected the prong-end width plus clearance {expected_notch} mm")
