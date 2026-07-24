"""Static drift guard for the Grade 2 braille flap titles (no OpenSCAD needed).

The pre-translated braille strings live in two places:

1. ``scripts/braille_labels.json`` — written by
   ``scripts/generate_braille_labels.mjs`` (the Liblouis UEB Grade 2
   translation authority, run manually and committed);
2. ``BRAILLE_LABELS`` in ``Measuring_Stencil.scad`` (the hardcoded copy the
   Tactile-mode braille flaps build from).

This suite regex-extracts the SCAD constant and asserts:

* the two copies are identical (same drift-lock pattern as
  ``test_stencil_data.py``);
* every codepoint is Unicode braille (U+2800-U+28FF — the generator replaces
  ASCII spaces with U+2800 blanks);
* every line fits its card's Tactile-mode width
  (``cells * 7 + 2 * 4 <= card width``), re-deriving the simple card width
  formulas from the SCAD so an over-wide line fails here before it ever
  reaches a printer.

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STENCIL_SCAD = PROJECT_ROOT / "Measuring_Stencil.scad"
LABELS_JSON = PROJECT_ROOT / "scripts" / "braille_labels.json"

# Card order of BRAILLE_LABELS rows (= the SCAD's fixed card list).
CARD_ORDER = ["P1", "P2", "P3", "R1", "C1", "F1", "F2"]

# Layout constants duplicated from Measuring_Stencil.scad — keep in lock-step.
CARD_MARGIN = 6
P_WEB = 8
F_EDGE = 7
F_HOLE_GAP = 7
RULER_LEN = 100
CORD_GAUGE_DIAS = [3, 4, 5, 6, 7, 8, 9]
C1_GAP_TACTILE = 8
F1_ROWS = [[15, 16, 17, 18, 19, 20], [21, 22, 23, 24, 25]]
F2_ROWS = [[26, 27, 28, 29], [30, 31, 32]]
BRL_CELL_SP = 7.0
FLAP_MARGIN = 4


def _scad_braille_labels() -> List[List[str]]:
    """Parse the BRAILLE_LABELS rows out of Measuring_Stencil.scad."""
    text = STENCIL_SCAD.read_text(encoding="utf-8")
    block_match = re.search(r"BRAILLE_LABELS\s*=\s*\[(.*?)\n\];", text, flags=re.S)
    assert block_match, f"BRAILLE_LABELS not found in {STENCIL_SCAD.name}"
    rows = re.findall(r"\[([^\[\]]*)\]", block_match.group(1))
    assert len(rows) == len(CARD_ORDER), (
        f"Expected {len(CARD_ORDER)} BRAILLE_LABELS rows, got {len(rows)}"
    )
    return [re.findall(r'"([^"]*)"', row) for row in rows]


def _json_braille_labels() -> List[List[str]]:
    """Load the generator output in the same card order."""
    payload = json.loads(LABELS_JSON.read_text(encoding="utf-8"))
    cards = payload["cards"]
    missing = [c for c in CARD_ORDER if c not in cards]
    assert not missing, f"braille_labels.json is missing cards: {missing}"
    return [cards[card]["braille"] for card in CARD_ORDER]


def _stencil_plug_dims() -> List[List[float]]:
    """Parse PLUG_PRESET_DIMS (already drift-locked by test_stencil_data)."""
    text = STENCIL_SCAD.read_text(encoding="utf-8")
    block_match = re.search(r"PLUG_PRESET_DIMS\s*=\s*\[(.*?)\];", text, flags=re.S)
    assert block_match, f"PLUG_PRESET_DIMS not found in {STENCIL_SCAD.name}"
    rows = re.findall(r'\[\s*"[^"]+"\s*,([^\]]+)\]', block_match.group(1))
    assert len(rows) == 3
    return [[float(v) for v in row.split(",")] for row in rows]


def _f_card_width(rows: List[List[int]]) -> float:
    return max(
        2 * F_EDGE + (len(row) - 1) * F_HOLE_GAP + sum(row) for row in rows
    )


def _tactile_card_widths() -> List[float]:
    """Tactile-mode card widths in CARD_ORDER, mirroring the SCAD formulas."""
    plug_widths = [
        2 * CARD_MARGIN + max(wc, ww) + P_WEB + max(tw, tc) + P_WEB + cord
        for (_length, ww, wc, tw, tc, cord) in _stencil_plug_dims()
    ]
    c1_width = (
        2 * CARD_MARGIN
        + sum(CORD_GAUGE_DIAS)
        + (len(CORD_GAUGE_DIAS) - 1) * C1_GAP_TACTILE
    )
    return [
        *plug_widths,
        RULER_LEN,
        c1_width,
        _f_card_width(F1_ROWS),
        _f_card_width(F2_ROWS),
    ]


class TestBrailleLabels:
    """SCAD copy, generator output, and card widths must stay consistent."""

    def test_scad_matches_generator_json(self) -> None:
        if not LABELS_JSON.exists():
            pytest.fail(f"Missing generator output: {LABELS_JSON}")
        scad = _scad_braille_labels()
        generated = _json_braille_labels()
        for card, scad_lines, json_lines in zip(CARD_ORDER, scad, generated):
            assert scad_lines == json_lines, (
                f"BRAILLE_LABELS for {card} is {scad_lines!r} in the SCAD but "
                f"{json_lines!r} in braille_labels.json — the copies have "
                f"drifted. Re-run scripts/generate_braille_labels.mjs and "
                f"paste its output into Measuring_Stencil.scad."
            )

    def test_every_codepoint_is_unicode_braille(self) -> None:
        for card, lines in zip(CARD_ORDER, _scad_braille_labels()):
            assert lines, f"{card} has no braille lines"
            for line in lines:
                assert line, f"{card} has an empty braille line"
                for ch in line:
                    assert 0x2800 <= ord(ch) <= 0x28FF, (
                        f"{card} line {line!r} contains non-braille "
                        f"character {ch!r} (U+{ord(ch):04X}). The generator "
                        f"must emit Unicode braille only (spaces become "
                        f"U+2800)."
                    )

    def test_every_line_fits_its_card(self) -> None:
        widths = _tactile_card_widths()
        for card, lines, width in zip(CARD_ORDER, _scad_braille_labels(), widths):
            for line in lines:
                needed = len(line) * BRL_CELL_SP + 2 * FLAP_MARGIN
                assert needed <= width, (
                    f"{card} braille line {line!r} needs {needed} mm "
                    f"({len(line)} cells) but the Tactile card is only "
                    f"{width} mm wide. Shorten the wording in "
                    f"scripts/generate_braille_labels.mjs and regenerate."
                )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
