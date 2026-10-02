"""Quick-lane checks on the committed 1:1 outline sheets under
``docs/guides/outline-sheets/`` (written by ``scripts/generate_outline_sheets.py``).

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import re
from pathlib import Path

from scripts.build_outline_sheets_pdf import SHEET_ORDER, SIZES

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SHEETS_DIR = PROJECT_ROOT / "docs" / "guides" / "outline-sheets"
TEXT = re.compile(r"<text[^>]*>([^<]*)</text>")


def test_no_label_reads_negative() -> None:
    """A dimension on a 1:1 sheet is a length: no label may print a minus
    sign, whichever of a dimension's two ends the generator found first."""
    sheets = sorted(SHEETS_DIR.glob("outline_*.svg"))
    assert len(sheets) == len(SHEET_ORDER) * len(SIZES)
    negative = [(p.name, label) for p in sheets
                for label in TEXT.findall(p.read_text(encoding="utf-8"))
                if re.match(r"\s*[-−]\s*\d", label)]
    assert not negative, f"labels that read negative: {negative}"
