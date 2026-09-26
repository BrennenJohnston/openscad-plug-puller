"""Static drift guard for the plug preset dimensions (no OpenSCAD needed).

The preset plug numbers (length, width at the prong end and at the cord end,
thickness at both ends, cord) live in three places:

1. the ``_eff_*`` preset ternaries in ``src/Plug_Puller_Parametric.scad``
   (the authority — the model builds from these);
2. ``PLUG_PRESET_DIMS`` in ``Measuring_Stencil.scad`` (the printable P-card
   silhouettes);
3. ``PLUG_PRESET_DIMS`` in ``scripts/generate_stencil_sheet.py`` (the 1:1
   paper stencil sheet).

The preset list itself is read from the one-sided file's ``plug_preset``
dropdown (every label but "Measure my plug"), so adding a preset to the
dropdown is enough to put it under this guard: the two copies must then
carry a row for it, in the dropdown's order, with the same six numbers.

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Tuple

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MAIN_SCAD = PROJECT_ROOT / "src" / "Plug_Puller_Parametric.scad"
STENCIL_SCAD = PROJECT_ROOT / "Measuring_Stencil.scad"
SHEET_SCRIPT = PROJECT_ROOT / "scripts" / "generate_stencil_sheet.py"

# _eff_* variable per dimension, in PLUG_PRESET_DIMS column order.
EFF_VARS = [
    "_eff_plug_length",
    "_eff_plug_width_wall",
    "_eff_plug_width_cable",
    "_eff_plug_thickness_wall",
    "_eff_plug_thickness_cable",
    "_eff_cord_thickness",
]

Dims = Tuple[float, float, float, float, float, float]


def _preset_labels() -> List[str]:
    """The one-sided dropdown's presets in Customizer order (P1, P2, ...)."""
    text = MAIN_SCAD.read_text(encoding="utf-8")
    match = re.search(r'^plug_preset\s*=\s*"[^"]+"\s*;\s*//\s*\[([^\]]+)\]', text, re.M)
    assert match, f"Could not find the `plug_preset` dropdown in {MAIN_SCAD.name}"
    labels = [opt.strip() for opt in match.group(1).split(",")]
    assert labels and labels[0] == "Measure my plug", f"unexpected dropdown: {labels}"
    return labels[1:]


PRESET_LABELS = _preset_labels()


def _main_scad_dims() -> Dict[str, Dims]:
    """Parse the preset ternaries: one number per (preset, _eff_ variable)."""
    text = MAIN_SCAD.read_text(encoding="utf-8")
    per_preset: Dict[str, List[float]] = {label: [] for label in PRESET_LABELS}
    for var in EFF_VARS:
        block_match = re.search(
            rf"^{var}\s*=\s*\n(.*?);", text, flags=re.S | re.M
        )
        assert block_match, f"Could not find the `{var}` ternary in {MAIN_SCAD.name}"
        block = block_match.group(1)
        for label in PRESET_LABELS:
            value_match = re.search(
                rf'==\s*"{re.escape(label)}"\s*\?\s*([0-9.]+)', block
            )
            assert value_match, (
                f"`{var}` has no ternary arm for preset {label!r} in "
                f"{MAIN_SCAD.name}"
            )
            per_preset[label].append(float(value_match.group(1)))
    return {label: tuple(vals) for label, vals in per_preset.items()}


def _stencil_scad_dims() -> List[Dims]:
    """Parse the PLUG_PRESET_DIMS rows out of Measuring_Stencil.scad."""
    text = STENCIL_SCAD.read_text(encoding="utf-8")
    block_match = re.search(r"PLUG_PRESET_DIMS\s*=\s*\[(.*?)\];", text, flags=re.S)
    assert block_match, f"PLUG_PRESET_DIMS not found in {STENCIL_SCAD.name}"
    rows = re.findall(r'\[\s*"[^"]+"\s*,([^\]]+)\]', block_match.group(1))
    assert rows, f"No PLUG_PRESET_DIMS rows in {STENCIL_SCAD.name}"
    return [tuple(float(v) for v in row.split(",")) for row in rows]


def _sheet_script_dims() -> List[Dims]:
    """Parse the PLUG_PRESET_DIMS constant out of generate_stencil_sheet.py."""
    text = SHEET_SCRIPT.read_text(encoding="utf-8")
    block_match = re.search(r"PLUG_PRESET_DIMS\s*=\s*\[(.*?)\]\n", text, flags=re.S)
    assert block_match, f"PLUG_PRESET_DIMS not found in {SHEET_SCRIPT.name}"
    rows = re.findall(r'\(\s*"[^"]+"\s*,\s*"[^"]+"\s*,([^)]+)\)', block_match.group(1))
    assert rows, f"No PLUG_PRESET_DIMS rows in {SHEET_SCRIPT.name}"
    return [tuple(float(v) for v in row.split(",") if v.strip()) for row in rows]


class TestStencilData:
    """The three copies of the preset plug numbers must be identical."""

    def test_main_scad_has_every_preset(self) -> None:
        main = _main_scad_dims()
        assert list(main) == PRESET_LABELS
        for label, dims in main.items():
            assert len(dims) == len(EFF_VARS), f"{label!r}: {dims}"

    def test_stencil_scad_carries_a_row_per_preset(self) -> None:
        """The stencil has exactly one card row per dropdown preset."""
        stencil = _stencil_scad_dims()
        assert len(stencil) == len(PRESET_LABELS), (
            f"Measuring_Stencil.scad PLUG_PRESET_DIMS has {len(stencil)} rows for "
            f"{len(PRESET_LABELS)} dropdown presets {PRESET_LABELS}"
        )

    def test_sheet_script_carries_a_row_per_preset(self) -> None:
        """The paper sheet has exactly one silhouette row per dropdown preset."""
        sheet = _sheet_script_dims()
        assert len(sheet) == len(PRESET_LABELS), (
            f"generate_stencil_sheet.py PLUG_PRESET_DIMS has {len(sheet)} rows for "
            f"{len(PRESET_LABELS)} dropdown presets {PRESET_LABELS}"
        )

    def test_stencil_scad_matches_main_scad(self) -> None:
        main = _main_scad_dims()
        stencil = _stencil_scad_dims()
        for label, got in zip(PRESET_LABELS, stencil):
            assert got == pytest.approx(main[label]), (
                f"Measuring_Stencil.scad PLUG_PRESET_DIMS for {label!r} is "
                f"{got}, but the main SCAD says {main[label]} — the copies "
                f"have drifted."
            )

    def test_sheet_script_matches_main_scad(self) -> None:
        if not SHEET_SCRIPT.exists():
            pytest.fail(f"Missing paper-stencil script: {SHEET_SCRIPT}")
        main = _main_scad_dims()
        sheet = _sheet_script_dims()
        for label, got in zip(PRESET_LABELS, sheet):
            assert got == pytest.approx(main[label]), (
                f"generate_stencil_sheet.py PLUG_PRESET_DIMS for {label!r} is "
                f"{got}, but the main SCAD says {main[label]} — the copies "
                f"have drifted."
            )

    def test_dims_are_plausible(self) -> None:
        """Cheap sanity net: every dimension physically plausible for a US
        plug. (Presets can sit below the Customizer slider floors — e.g.
        P1's cord-end width is 11.2 mm against a 12 mm slider minimum of the
        old range — so these are looser physical bounds, not the slider
        ranges.)"""
        for dims in list(_main_scad_dims().values()) + _stencil_scad_dims():
            length, ww, wc, tw, tc, cord = dims
            assert 12 <= length <= 85
            assert 8 <= ww <= 45 and 8 <= wc <= 45
            assert 6 <= tw <= 40 and 6 <= tc <= 40
            assert 2 <= cord <= 9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
