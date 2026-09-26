"""The Starter Guide's two copies name the same stencil cards and presets.

The starter guide exists twice: ``docs/guides/starter-guide.md`` (the page a
reader opens on GitHub) and the typeset text inside
``scripts/build_starter_guide_pdf.py`` (the printable PDF's first two pages).
They drifted once (R1 found the PDF still describing a retired model). This
suite ties them to each other and to the model:

* the P cards the stencil offers (``Measuring_Stencil.scad``'s ``export_card``
  list) are exactly the P cards both texts explain in their card legend;
* the preset each P card stands for (the one-sided ``plug_preset`` dropdown,
  in the same order as the stencil's ``PLUG_PRESET_DIMS`` rows) is exactly
  the label both texts tell the reader to pick in Path A.

No rendering: every fact is parsed from the files.

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MAIN_SCAD = PROJECT_ROOT / "src" / "Plug_Puller_Parametric.scad"
STENCIL_SCAD = PROJECT_ROOT / "Measuring_Stencil.scad"
GUIDE_MD = PROJECT_ROOT / "docs" / "guides" / "starter-guide.md"
PDF_SCRIPT = PROJECT_ROOT / "scripts" / "build_starter_guide_pdf.py"


def _dropdown(text: str, name: str) -> List[str]:
    match = re.search(rf'^{name}\s*=\s*"[^"]+"\s*;\s*//\s*\[([^\]]+)\]', text, re.M)
    assert match, f"Could not find the `{name}` dropdown"
    return [opt.strip() for opt in match.group(1).split(",")]


def stencil_p_cards() -> List[str]:
    """P1, P2, ... from the stencil's export_card list, in card order."""
    options = _dropdown(STENCIL_SCAD.read_text(encoding="utf-8"), "export_card")
    return [opt for opt in options if re.fullmatch(r"P\d+", opt)]


def card_to_preset() -> Dict[str, str]:
    """P card -> the one-sided preset label it stands for (the dropdown's
    presets after "Measure my plug", in stencil card order)."""
    labels = _dropdown(MAIN_SCAD.read_text(encoding="utf-8"), "plug_preset")[1:]
    cards = stencil_p_cards()
    assert len(labels) == len(cards), (
        f"{len(cards)} P cards for {len(labels)} one-sided presets: {cards} vs {labels}")
    return dict(zip(cards, labels))


def _legend_cards_md() -> List[str]:
    text = GUIDE_MD.read_text(encoding="utf-8")
    return re.findall(r"^- \*\*(P\d+)\*\* — plug silhouette card", text, re.M)


def _path_a_md() -> Dict[str, str]:
    text = GUIDE_MD.read_text(encoding="utf-8")
    return dict(re.findall(r"^\s+- (P\d+) → .*?`plug_preset` =\s*`([^`]+)`", text, re.M | re.S))


def _legend_cards_pdf() -> List[str]:
    text = PDF_SCRIPT.read_text(encoding="utf-8")
    return re.findall(r"<tr><th>(P\d+)</th><td>plug silhouette:", text)


def _path_a_pdf() -> Dict[str, str]:
    text = PDF_SCRIPT.read_text(encoding="utf-8")
    return dict(re.findall(r"<li>(P\d+) → <span class=\"mono\">([^<]+)</span>", text))


def test_legends_name_every_p_card() -> None:
    cards = stencil_p_cards()
    assert cards, "the stencil offers no P cards"
    assert _legend_cards_md() == cards, (
        f"starter-guide.md's card legend lists {_legend_cards_md()}, the stencil offers {cards}")
    assert _legend_cards_pdf() == cards, (
        f"build_starter_guide_pdf.py's card legend lists {_legend_cards_pdf()}, the stencil offers {cards}")


def test_path_a_names_every_preset() -> None:
    expected = card_to_preset()
    assert _path_a_md() == expected, (
        f"starter-guide.md Path A maps {_path_a_md()}, the model says {expected}")
    assert _path_a_pdf() == expected, (
        f"build_starter_guide_pdf.py Path A maps {_path_a_pdf()}, the model says {expected}")


def test_both_copies_take_the_same_cards_to_the_plug() -> None:
    cards = stencil_p_cards()
    md = GUIDE_MD.read_text(encoding="utf-8")
    pdf = PDF_SCRIPT.read_text(encoding="utf-8")
    for card in cards:
        assert f"**{card}**" in md, f"starter-guide.md never bolds the card {card}"
        assert f"<b>{card}</b>" in pdf, f"build_starter_guide_pdf.py never bolds the card {card}"
