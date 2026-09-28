"""Quick-lane rules for the per-tool guide packets' Markdown twins under
``docs/guides/one-sided/`` and ``docs/guides/two-sided/`` (the quick start,
the dial guide and the measuring guide), written by
``scripts/build_dial_reference.py --tool <t> --markdown-only`` from the
catalog, the mappings, the diagram index, the storyboard index and the
catalog's ``measure`` rows.

Each twin is the text a screen-reader user gets instead of the printed
packet, so these tests hold the twins to the same data as the pictures: the
dials in Customizer order, every image with the index's alt text and its
long description right under it, and no heading deeper than H3.

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

from scripts.build_dial_reference import build_html, build_markdown, load_catalog
from tests.test_dial_catalog import _mapping_rows

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GUIDES = PROJECT_ROOT / "docs" / "guides"
INDEX = PROJECT_ROOT / "docs" / "dials" / "dial_diagrams_index.json"
STORYBOARDS = PROJECT_ROOT / "docs" / "dials" / "storyboards_index.json"
TOOLS = ("one-sided", "two-sided")
OPENER_HEADING = "Which tool this is"

SAMPLE_ROWS = [
    {
        "file": "one-sided", "name": "measure_plug_length", "section": "Step 1 - Your Plug",
        "tier": "step", "quick_start": True, "title": "Plug length",
        "changes": "Runs the pocket farther toward the finger holes.",
        "diagram": {"view": "top", "style": "fill", "before": 25.5, "after": 40, "context": {},
                    "plug": "default", "crop": None, "dimension": {"kind": "v", "at": "plug_length"}},
        "note": None,
        "measure": {"how": "With the plug in the outlet, ruler from the wall plate face to the plug's back face.",
                    "typical": [20, 50], "example": 38, "stencil": "R1", "anchor": "plug_length"},
    },
    {
        "file": "two-sided", "name": "plate_thickness", "section": "Advanced - Two-Sided Puller",
        "tier": "advanced", "quick_start": False, "title": "Plate thickness",
        "changes": "Thickens each plate.",
        "diagram": {"view": "section-y", "style": "fill", "before": 4, "after": 6, "context": {},
                    "plug": "default", "crop": None, "at": 3, "dimension": None},
        "note": "The finished sandwich is twice this.",
        "measure": None,
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
     "features": ["body edge", "seat"], "alt": "Plug length: before and after, 25.5 to 40 mm; red marks the body edge and the seat.",
     "long_description": "Two top views of the one-sided puller, before left and after right."},
    {"file": "two-sided", "name": "plate_thickness", "view": "section-y", "style": "fill",
     "before": 4, "after": 6, "context": {}, "plug": "default", "regions": 4,
     "changed_area_mm2": 75.1, "tags": [], "svg": "two-sided/plate_thickness.svg",
     "features": ["cord channel", "finger lobes"], "alt": "Plate thickness: before and after, 4 to 6 mm; red marks the cord channel and the finger lobes.",
     "long_description": "Two vertical slices of one plate of the two-sided puller."},
]


def _headings(text: str) -> List[Tuple[int, str]]:
    return [(len(m.group(1)), m.group(2).strip()) for m in re.finditer(r"^(#{1,6}) (.+)$", text, re.M)]


def _index() -> Dict[Tuple[str, str], Dict]:
    return {(e["file"], e["name"]): e for e in json.loads(INDEX.read_text(encoding="utf-8"))}


def _storyboards() -> Dict[str, Dict]:
    return {e["file"]: e for e in json.loads(STORYBOARDS.read_text(encoding="utf-8"))}


def _images_with_descriptions(text: str) -> List[Tuple[str, str, str]]:
    """(alt, target, the first non-empty line within two lines after the image)."""
    lines = text.splitlines()
    out = []
    for i, line in enumerate(lines):
        m = re.match(r"!\[(.*)\]\((.*)\)$", line)
        if m:
            following = [ln for ln in lines[i + 1:i + 3] if ln.strip()]
            out.append((m.group(1), m.group(2), following[0] if following else ""))
    return out


def _check_dial_images(text: str, tool: str, rows: List[Dict], idx: Dict[Tuple[str, str], Dict]) -> None:
    images = {target: (alt, desc) for alt, target, desc in _images_with_descriptions(text)}
    for row in rows:
        target = f"../../dials/{tool}/{row['name']}.svg"
        assert target in images, f"{tool}: no image for {row['name']}"
        alt, desc = images[target]
        entry = idx[(tool, row["name"])]
        assert alt == entry["alt"], f"{tool} {row['name']}: alt {alt!r}"
        assert desc == entry["long_description"], f"{tool} {row['name']}: the long description does not follow the image"


def test_quick_start_twin() -> None:
    """Per tool: one H1, the opener H2, the storyboard with its alt and long
    description, then an H2 per Step section and an H3 per quick_start row
    of that file in mapping order; every dial image carries the index's alt
    with the long description under it; no other dial named in backticks;
    no H4."""
    catalog = load_catalog()
    idx, boards = _index(), _storyboards()
    for tool in TOOLS:
        text = (GUIDES / tool / "quick-start.md").read_text(encoding="utf-8")
        heads = _headings(text)
        assert [h for h in heads if h[0] == 1] == [heads[0]] and heads[0][0] == 1, f"{tool}: one H1 first"
        assert max(level for level, _ in heads) <= 3, f"{tool}: no H4"
        assert heads[1] == (2, OPENER_HEADING), f"{tool}: the opener H2 comes first"
        board = boards[tool]
        images = _images_with_descriptions(text)
        story = [im for im in images if im[1] == f"../../dials/{tool}/storyboard.svg"]
        assert len(story) == 1 and story[0][0] == board["alt"] and story[0][2] == board["long_description"], (
            f"{tool}: the storyboard image and its long description")
        step_rows = [r for r in _mapping_rows(tool) if r["section"].startswith("Step")]
        sections = []
        for r in step_rows:
            if r["section"] not in sections:
                sections.append(r["section"])
        assert [h[1] for h in heads if h[0] == 2][1:] == sections, f"{tool}: an H2 per Step section in order"
        quick = [r for r in catalog if r["file"] == tool and r["quick_start"]]
        assert [h[1] for h in heads if h[0] == 3] == [f"`{r['name']}`" for r in quick], f"{tool}: an H3 per quick-start dial in order"
        _check_dial_images(text, tool, quick, idx)
        all_names = {r["name"] for r in catalog if r["file"] == tool}
        quick_names = {r["name"] for r in quick}
        for name in re.findall(r"`([a-z_0-9]+)`", text):
            if name in all_names:
                assert name in quick_names, f"{tool}: {name} is not a quick-start dial"


def test_dial_guide_twin() -> None:
    """Per tool: every catalog row of that file as an H3 under its section's
    H2, in mapping order, with the numbers line, the index's alt and the
    long description under the image; no H4."""
    catalog = load_catalog()
    idx = _index()
    for tool in TOOLS:
        text = (GUIDES / tool / "dial-guide.md").read_text(encoding="utf-8")
        heads = _headings(text)
        assert sum(1 for h in heads if h[0] == 1) == 1 and max(h[0] for h in heads) <= 3, f"{tool}: H1 to H3 only"
        rows = [r for r in catalog if r["file"] == tool]
        assert [h[1] for h in heads if h[0] == 3] == [f"`{r['name']}`" for r in rows], f"{tool}: an H3 per dial in order"
        sections = []
        for r in rows:
            if r["section"] not in sections:
                sections.append(r["section"])
        assert [h[1] for h in heads if h[0] == 2] == sections, f"{tool}: an H2 per section in order"
        numbers = re.findall(r"^Default .+ · .+$", text, re.M)
        assert len(numbers) == len(rows), f"{tool}: {len(numbers)} numbers lines for {len(rows)} dials"
        _check_dial_images(text, tool, rows, idx)


def test_measuring_guide_twin() -> None:
    """Per tool: one H2 per non-null measure row in mapping order, each with
    the how text and either the typical range with the example or the
    dropdown's choices; the page ends with a link to the form's twin."""
    catalog = load_catalog()
    for tool in TOOLS:
        text = (GUIDES / tool / "measuring-guide.md").read_text(encoding="utf-8")
        heads = _headings(text)
        assert sum(1 for h in heads if h[0] == 1) == 1 and max(h[0] for h in heads) <= 3, f"{tool}: H1 to H3 only"
        measured = [r for r in catalog if r["file"] == tool and r["measure"] is not None]
        h2 = [h[1] for h in heads if h[0] == 2]
        assert len(h2) == len(measured), f"{tool}: {len(h2)} sections for {len(measured)} measured dials"
        chunks = re.split(r"^## ", text, flags=re.M)[1:]
        for chunk, row in zip(chunks, measured):
            assert chunk.startswith(h2[measured.index(row)]), f"{tool}: sections out of order at {row['name']}"
            assert f"`{row['name']}`" in chunk, f"{tool}: {row['name']} not named in its section"
            m = row["measure"]
            assert m["how"] in chunk, f"{tool}: {row['name']} without its how text"
            if m["typical"] is None:
                assert "The choices:" in chunk, f"{tool}: {row['name']} without its choices"
            else:
                lo, hi = m["typical"]
                assert f"Typical: {lo:g} to {hi:g} mm. Example: {m['example']:g} mm." in chunk, f"{tool}: {row['name']} numbers"
            if m["stencil"]:
                assert f"card {m['stencil']}" in chunk, f"{tool}: {row['name']} without its stencil card"
        assert "](measuring-form.md)" in text.rstrip().splitlines()[-1], f"{tool}: the last line links the form twin"


def test_builder_tool_filter() -> None:
    """build_markdown with a tool and a part keeps that tool's rows only."""
    md = build_markdown(SAMPLE_ROWS, SAMPLE_MAPPINGS, SAMPLE_INDEX, tool="two-sided", part="dial-guide")
    assert "### `plate_thickness`" in md
    assert "measure_plug_length" not in md
    assert "Default 4 · Range 2 to 8 · Step size 0.25 · Unit mm" in md
    assert "![Plate thickness: before and after, 4 to 6 mm; red marks the cord channel and the finger lobes.](../../dials/two-sided/plate_thickness.svg)" in md
    assert "Two vertical slices of one plate of the two-sided puller." in md
    assert "#### " not in md


SAMPLE_SVGS = {
    ("one-sided", "measure_plug_length"): '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 80"><title>Plug length</title></svg>',
    ("two-sided", "plate_thickness"): '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 60"><title>Plate thickness</title></svg>',
}
SAMPLE_STORYBOARDS = {
    "one-sided": {"file": "one-sided", "name": "storyboard", "key": "one-sided-vacuum-plug", "svg": "one-sided/storyboard.svg",
                  "title": "The four steps on a US vacuum plug", "stages": [0, 3, 8, 2, 1],
                  "alt": "The one-sided puller, the four Customizer steps on a US vacuum plug, five stages left to right.",
                  "long_description": "Five stages of the one-sided puller, left to right."},
}
SAMPLE_STORYBOARD_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 184.5 120.37"><title>The four steps</title></svg>'
SAMPLE_FORM_SVG = '<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="279mm" viewBox="0 0 210 279"><rect width="210" height="279" fill="white"/></svg>'


def test_packet_html() -> None:
    """The packet's HTML, in order: a title section, a contents section, an
    opener section with the storyboard figure, then one card per row for
    the quick start and the dial guide (a figure holding the SVG with a
    figcaption equal to the long description; the ids qs- and ref-), a
    measuring-guide section with an h3 per measure row, and last the form
    page with the form SVG at 210 mm; no figure scaled above 1:1."""
    html = build_html(SAMPLE_ROWS, SAMPLE_MAPPINGS, SAMPLE_INDEX, SAMPLE_SVGS, tool="one-sided",
                      storyboards=SAMPLE_STORYBOARDS, storyboard_svg=SAMPLE_STORYBOARD_SVG, form_svg=SAMPLE_FORM_SVG)
    order = [html.index(s) for s in ('class="page front title"', 'class="page front contents"', 'class="page front opener"',
                                     'id="qs-one-sided-measure_plug_length"', 'id="ref-one-sided-measure_plug_length"',
                                     'class="flow measuring"', 'class="page form"')]
    assert order == sorted(order), "the packet's sections are out of order"
    assert html.count('<section class="card"') == 2
    assert "plate_thickness" not in html
    assert html.count("<figcaption>Two top views of the one-sided puller, before left and after right.</figcaption>") == 2
    assert html.count("<title>Plug length</title>") == 2
    assert 'class="page front opener"' in html and "<title>The four steps</title>" in html
    assert "<figcaption>Five stages of the one-sided puller, left to right.</figcaption>" in html
    measuring = html[html.index('class="flow measuring"'):html.index('class="page form"')]
    assert measuring.count("<h3") == 1 and "measure_plug_length" in measuring
    form = html[html.index('class="page form"'):]
    assert 'width="210mm"' in form and 'height="279mm"' in form
    figures = re.findall(r'<figure[^>]*>\s*<svg[^>]*viewBox="0 0 ([\d.]+) [\d.]+"[^>]*width="([\d.]+)mm"', html)
    assert len(figures) == 3, "two card figures and the storyboard"
    for vb_w, width in figures:
        assert float(width) <= float(vb_w) + 1e-6, "a figure is scaled above 1:1"
