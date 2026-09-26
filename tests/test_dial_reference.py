"""Tests for ``scripts/build_dial_reference.py``: the dial reference's
Markdown twin and HTML (quick lane, no Edge, no OpenSCAD)."""

from __future__ import annotations

import re
from pathlib import Path

from scripts.build_dial_reference import (
    FRONT_MATTER_PAGES,
    build_html,
    build_markdown,
    expected_pages,
    load_catalog,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MARKDOWN = PROJECT_ROOT / "docs" / "guides" / "dial-reference.md"

SAMPLE_ROWS = [
    {
        "file": "one-sided", "name": "measure_plug_length", "section": "Step 1 - Your Plug",
        "tier": "step", "quick_start": True, "title": "Plug length",
        "changes": "Runs the pocket farther toward the finger holes.",
        "diagram": {"view": "top", "style": "fill", "before": 25.5, "after": 40, "context": {},
                    "plug": "default", "crop": None},
        "note": None,
    },
    {
        "file": "two-sided", "name": "plate_thickness", "section": "Advanced - Two-Sided Puller",
        "tier": "advanced", "quick_start": False, "title": "Plate thickness",
        "changes": "Thickens each plate.",
        "diagram": {"view": "section-y", "style": "fill", "before": 4, "after": 6, "context": {},
                    "plug": "default", "crop": None, "at": 3},
        "note": "The finished sandwich is twice this.",
    },
]
SAMPLE_MAPPINGS = {
    "one-sided": {"measure_plug_length": {"openscad_name": "measure_plug_length", "type": "float",
                                          "default": 25.5, "range": [12.0, 85.0], "step": 0.5,
                                          "unit": "mm", "section": "Step 1 - Your Plug",
                                          "description": "How long the plug is."}},
    "two-sided": {"plate_thickness": {"openscad_name": "plate_thickness", "type": "float",
                                      "default": 4, "range": [2, 8], "step": 0.25, "unit": "mm",
                                      "section": "Advanced - Two-Sided Puller",
                                      "description": "Thickness of each plate."}},
}
SAMPLE_INDEX = [
    {"file": "one-sided", "name": "measure_plug_length", "view": "top", "style": "fill",
     "before": 25.5, "after": 40, "context": {}, "plug": "default", "regions": 5,
     "changed_area_mm2": 1182.9, "tags": [], "svg": "one-sided/measure_plug_length.svg",
     "features": ["body edge", "seat"]},
    {"file": "two-sided", "name": "plate_thickness", "view": "section-y", "style": "fill",
     "before": 4, "after": 6, "context": {}, "plug": "default", "regions": 4,
     "changed_area_mm2": 75.1, "tags": [], "svg": "two-sided/plate_thickness.svg",
     "features": ["cord channel", "finger lobes"]},
]
SAMPLE_SVGS = {
    ("one-sided", "measure_plug_length"): '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><title>Plug length</title></svg>',
    ("two-sided", "plate_thickness"): '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><title>Plate thickness</title></svg>',
}


def test_markdown_lists_every_row() -> None:
    md = build_markdown(SAMPLE_ROWS, SAMPLE_MAPPINGS, SAMPLE_INDEX)
    levels = [len(m.group(1)) for m in re.finditer(r"^(#{1,6}) ", md, re.M)]
    assert levels.count(1) == 1
    assert "## One-sided puller" in md and "## Two-sided puller" in md
    assert "### Step 1 - Your Plug" in md and "### Advanced - Two-Sided Puller" in md
    assert "#### `measure_plug_length`" in md and "#### `plate_thickness`" in md
    assert "![Runs the pocket farther toward the finger holes.](../dials/one-sided/measure_plug_length.svg)" in md
    assert "| Default | Range | Step | Unit |" in md
    assert "| 25.5 | 12 to 85 | 0.5 | mm |" in md
    assert "Moves: body edge, seat." in md
    assert "The finished sandwich is twice this." in md


def test_html_one_section_per_row() -> None:
    html = build_html(SAMPLE_ROWS, SAMPLE_MAPPINGS, SAMPLE_INDEX, SAMPLE_SVGS)
    assert html.count('<h3 id="one-sided-measure_plug_length">') == 1
    assert html.count('<h3 id="two-sided-plate_thickness">') == 1
    assert html.count('href="#one-sided-measure_plug_length"') == 1
    assert html.count('href="#two-sided-plate_thickness"') == 1
    assert html.count('class="page dial"') == 2
    assert "<title>Plug length</title>" in html


def test_expected_pages() -> None:
    assert expected_pages(SAMPLE_ROWS) == len(SAMPLE_ROWS) + FRONT_MATTER_PAGES


def test_reference_markdown_matches_catalog() -> None:
    """The committed Markdown twin names every catalog row, in Customizer
    order, with its diagram and its sentence as alt text."""
    text = MARKDOWN.read_text(encoding="utf-8")
    names = re.findall(r"^#### `([a-z_0-9]+)`", text, re.M)
    rows = load_catalog()
    assert names == [r["name"] for r in rows]
    for row in rows:
        assert f"![{row['changes']}](../dials/{row['file']}/{row['name']}.svg)" in text, row["name"]
