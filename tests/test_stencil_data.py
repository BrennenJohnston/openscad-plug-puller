"""Static drift guard for the plug numbers on the stencil's P cards (no OpenSCAD needed).

Each P card of ``Measuring_Stencil.scad`` (``PLUG_PRESET_DIMS``: length,
width at the prong end and at the cord end, thickness at both ends, cord)
copies the preset of the tool file that offers its plug:

* P1 (lamp) and P4 (wide appliance plug) from the one-sided puller,
  ``src/Plug_Puller_Parametric.scad``, all six numbers;
* P2 (standard 3-prong plug) and P3 (heavy-duty extension cord) from the
  two-sided puller, ``src/Plug_Puller_Two_Sided.scad``, the length, both
  widths and the cord (that file reads no thickness).

The preset ternaries of each file are the authority: the model builds from
them. A card whose plug has left its tool file's dropdown fails here.

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ONE_SIDED_SCAD = PROJECT_ROOT / "src" / "Plug_Puller_Parametric.scad"
TWO_SIDED_SCAD = PROJECT_ROOT / "src" / "Plug_Puller_Two_Sided.scad"
STENCIL_SCAD = PROJECT_ROOT / "Measuring_Stencil.scad"

# _eff_* variable per PLUG_PRESET_DIMS column, per tool file; None = the file
# reads no such number.
EFF_VARS: Dict[Path, List[Optional[str]]] = {
    ONE_SIDED_SCAD: [
        "_eff_plug_length",
        "_eff_plug_width_wall",
        "_eff_plug_width_cable",
        "_eff_plug_thickness_wall",
        "_eff_plug_thickness_cable",
        "_eff_cord_thickness",
    ],
    TWO_SIDED_SCAD: [
        "_eff_plug_length",
        "_eff_plug_width_prong_end",
        "_eff_plug_width_cord_end",
        None,
        None,
        "_eff_cord_thickness",
    ],
}

# Card id -> (tool file, preset label in that file's dropdown).
CARDS: Dict[str, Tuple[Path, str]] = {
    "P1": (ONE_SIDED_SCAD, "Flat 2-prong lamp plug - NEMA 1-15"),
    "P2": (TWO_SIDED_SCAD, "Standard 3-prong plug - NEMA 5-15"),
    "P3": (TWO_SIDED_SCAD, "Heavy-duty extension cord - NEMA 5-15"),
    "P4": (ONE_SIDED_SCAD, "Wide 2-prong appliance plug - NEMA 1-15"),
}

Dims = Tuple[float, ...]


def _dropdown(scad: Path) -> List[str]:
    text = scad.read_text(encoding="utf-8")
    match = re.search(r'^plug_preset\s*=\s*"[^"]+"\s*;\s*//\s*\[([^\]]+)\]', text, re.M)
    assert match, f"Could not find the `plug_preset` dropdown in {scad.name}"
    return [opt.strip() for opt in match.group(1).split(",")]


def _preset_value(scad: Path, var: str, label: str) -> float:
    text = scad.read_text(encoding="utf-8")
    block_match = re.search(rf"^{var}\s*=\s*\n(.*?);", text, flags=re.S | re.M)
    assert block_match, f"Could not find the `{var}` ternary in {scad.name}"
    value_match = re.search(rf'==\s*"{re.escape(label)}"\s*\?\s*([0-9.]+)', block_match.group(1))
    assert value_match, f"`{var}` has no ternary arm for preset {label!r} in {scad.name}"
    return float(value_match.group(1))


def _stencil_cards() -> Dict[str, Dims]:
    text = STENCIL_SCAD.read_text(encoding="utf-8")
    block_match = re.search(r"PLUG_PRESET_DIMS\s*=\s*\[(.*?)\];", text, flags=re.S)
    assert block_match, f"PLUG_PRESET_DIMS not found in {STENCIL_SCAD.name}"
    rows = re.findall(r'\[\s*"([^"]+)"\s*,([^\]]+)\]', block_match.group(1))
    assert rows, f"No PLUG_PRESET_DIMS rows in {STENCIL_SCAD.name}"
    return {card: tuple(float(v) for v in values.split(",")) for card, values in rows}


def test_stencil_carries_exactly_the_mapped_cards() -> None:
    assert list(_stencil_cards()) == list(CARDS), (
        "Measuring_Stencil.scad's P cards and this test's card map disagree")


@pytest.mark.parametrize("card", list(CARDS))
def test_card_plug_is_in_its_tool_files_dropdown(card: str) -> None:
    scad, label = CARDS[card]
    assert label in _dropdown(scad), f"{card}: {label!r} is not a preset of {scad.name}"


@pytest.mark.parametrize("card", list(CARDS))
def test_card_numbers_match_the_tool_file(card: str) -> None:
    scad, label = CARDS[card]
    got = _stencil_cards()[card]
    assert len(got) == 6, f"{card}: {got}"
    for column, var in enumerate(EFF_VARS[scad]):
        if var is None:
            continue
        want = _preset_value(scad, var, label)
        assert got[column] == pytest.approx(want), (
            f"{card} column {column} is {got[column]}, but {scad.name} says {var} = {want} "
            f"for {label!r}: the copies have drifted")


@pytest.mark.parametrize("card", list(CARDS))
def test_card_dims_are_plausible(card: str) -> None:
    """Cheap sanity net: every number physically plausible for a US plug.
    Presets can sit outside the Customizer slider ranges (the standard
    plug's measured 9.25 mm cord is past the one-sided 9 mm cord slider), so
    these are looser physical bounds, not the slider ranges."""
    length, ww, wc, tw, tc, cord = _stencil_cards()[card]
    assert 12 <= length <= 85
    assert 8 <= ww <= 45 and 8 <= wc <= 45
    assert 6 <= tw <= 40 and 6 <= tc <= 40
    assert 2 <= cord <= 9.5
