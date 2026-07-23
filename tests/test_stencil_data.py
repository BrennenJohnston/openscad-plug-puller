"""Static drift guard for the plug preset dimensions (no OpenSCAD needed).

The preset plug numbers (length, width wall/cable, thickness wall/cable,
cord) live in three places:

1. the ``_eff_*`` preset ternaries in ``src/Plug_Puller_Parametric.scad``
   (the authority — the model builds from these);
2. ``PLUG_PRESET_DIMS`` in ``Measuring_Stencil.scad`` (the printable P1/P2/P3
   silhouette cards);
3. ``PLUG_PRESET_DIMS`` in ``scripts/generate_stencil_sheet.py`` (the 1:1
   paper stencil sheet).

This suite regex-extracts all three and asserts they are identical, so the
copies cannot drift apart.

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

# Step 1 dropdown order (P1, P2, P3).
PRESET_LABELS = [
    "Flat 2-prong lamp plug - NEMA 1-15",
    "Standard 3-prong plug - NEMA 5-15",
    "Heavy-duty extension cord - NEMA 5-15",
]
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
    assert len(rows) == 3, f"Expected 3 PLUG_PRESET_DIMS rows, got {len(rows)}"
    return [tuple(float(v) for v in row.split(",")) for row in rows]


def _sheet_script_dims() -> List[Dims]:
    """Parse the PLUG_PRESET_DIMS constant out of generate_stencil_sheet.py."""
    text = SHEET_SCRIPT.read_text(encoding="utf-8")
    block_match = re.search(r"PLUG_PRESET_DIMS\s*=\s*\[(.*?)\]\n", text, flags=re.S)
    assert block_match, f"PLUG_PRESET_DIMS not found in {SHEET_SCRIPT.name}"
    rows = re.findall(r'\(\s*"[^"]+"\s*,\s*"[^"]+"\s*,([^)]+)\)', block_match.group(1))
    assert len(rows) == 3, f"Expected 3 PLUG_PRESET_DIMS rows, got {len(rows)}"
    return [tuple(float(v) for v in row.split(",") if v.strip()) for row in rows]


class TestStencilData:
    """The three copies of the preset plug numbers must be identical."""

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
        P1's cable-side width is 11.2 mm against a 12 mm slider minimum —
        so these are looser physical bounds, not the slider ranges.)"""
        for dims in _stencil_scad_dims():
            length, ww, wc, tw, tc, cord = dims
            assert 12 <= length <= 85
            assert 8 <= ww <= 45 and 8 <= wc <= 45
            assert 6 <= tw <= 40 and 6 <= tc <= 40
            assert 2 <= cord <= 9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
