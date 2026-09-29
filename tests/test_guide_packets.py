"""Quick-lane rules for the two guide documents of each tool, the pages
``docs/guides/<tool>/quick-start.md`` and ``full-guide.md`` written by
``scripts/build_dial_reference.py --tool <t> --markdown-only`` from the
catalog, the mappings, the diagram index, the storyboard index, the
measuring form's text and the sources under ``docs/guides/source/``, and
for the HTML the same script prints.

Each page is the text a screen-reader user gets instead of the printed
document, so these tests hold the pages to the same data as the pictures:
the sections in reading order, the dials in Customizer order, every dial
headed by its plain title with the name the Customizer shows and the
sentence of what it does under it, every picture with the index's alt text
and its description right under it (a dial that changes no shape shows no
picture and says why), the measuring section and the form in both pages,
the numbers in plain words, and no heading deeper than H3.

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

from scripts.build_dial_reference import build_html, build_markdown, dial_line, load_catalog, settings_rows
from tests.test_dial_catalog import _mapping_rows

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GUIDES = PROJECT_ROOT / "docs" / "guides"
INDEX = PROJECT_ROOT / "docs" / "dials" / "dial_diagrams_index.json"
STORYBOARDS = PROJECT_ROOT / "docs" / "dials" / "storyboards_index.json"
TOOLS = ("one-sided", "two-sided")
OPENER_HEADING = "Which tool this is"
MEASURE_HEADING = "Measure your plug and your hand"
STEPS_HEADING = "The four Customizer steps"
FRONT_H2 = ["Which tool this is", "Get the file", MEASURE_HEADING]
# The quick start's steps are one H2 with an H3 per step; the full guide's
# are an H2 each. Safety, care and the quick start's fit note are H3s
# under "Use it".
QUICK_START_H2 = FRONT_H2 + [STEPS_HEADING, "Render, export and print", "Assemble", "Use it"]
QUICK_START_H3_TAIL = ["Safety", "If it does not fit"]
FULL_GUIDE_TAIL = ["Render, export and print", "Assemble", "Use it", "If the print does not fit",
                   "Advanced settings", "Going deeper"]
FULL_GUIDE_H3 = ["Working in the browser", "Try it on paper first", "What to buy", "Safety", "Care",
                 "Red warning tags", "Printing problems", "Saved settings", "The command line"]

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
SAMPLE_FORM = "| # | Customizer name | What you measure | Default | Yours |\n|---|---|---|---|---|\n| 1 | `measure_plug_length` | The plug's length. | 25.5 mm | ________ |"


def _headings(text: str) -> List[Tuple[int, str]]:
    out, in_fence = [], False
    for ln in text.splitlines():
        if ln.startswith("```"):
            in_fence = not in_fence
        m = re.match(r"^(#{1,6}) (.+)$", ln)
        if m and not in_fence:
            out.append((len(m.group(1)), m.group(2).strip()))
    return out


def _index() -> Dict[Tuple[str, str], Dict]:
    return {(e["file"], e["name"]): e for e in json.loads(INDEX.read_text(encoding="utf-8"))}


def _storyboards() -> Dict[str, Dict]:
    return {e["file"]: e for e in json.loads(STORYBOARDS.read_text(encoding="utf-8"))}


def _images_with_descriptions(text: str) -> List[Tuple[str, str, str]]:
    """(alt, target, the first non-empty line within two lines after the image)."""
    lines = text.splitlines()
    out = []
    for i, line in enumerate(lines):
        m = re.match(r"\s*!\[(.*)\]\((.*)\)$", line)
        if m:
            following = [ln for ln in lines[i + 1:i + 3] if ln.strip()]
            out.append((m.group(1), m.group(2), following[0].strip() if following else ""))
    return out


def _expected_caption(row: Dict, entry: Dict) -> str:
    """The index's long description less the clause that repeats the card's
    sentence of what the dial does, which the card prints above the picture."""
    core = row["changes"].rstrip(".")
    return entry["long_description"].replace(f": {core[:1].lower()}{core[1:]}.", ".", 1)


# A card's second line; a measuring section's says "`name`. Row N of the form".
_CARD_NAME = re.compile(r"^Customizer name: `[a-z_0-9]+`$")


def _check_cards(text: str, tool: str, rows: List[Dict], idx: Dict[Tuple[str, str], Dict]) -> None:
    """Every dial: an H3 with its plain title, then the name the Customizer
    shows, then the sentence of what it does; then its picture with the
    index's alt text and the caption right under it or, for a dial that
    changes no shape, no picture and the line that says why."""
    lines = text.splitlines()
    heads = {}
    for i, line in enumerate(lines):
        if line.startswith("### ") and i + 2 < len(lines) and _CARD_NAME.match(lines[i + 2]):
            heads[line[4:]] = i
    images = {target: (alt, desc) for alt, target, desc in _images_with_descriptions(text)}
    for row in rows:
        assert row["title"] in heads, f"{tool}: no card for {row['name']}"
        following = [ln for ln in lines[heads[row["title"]] + 1:] if ln.strip()][:2]
        assert following == [f"Customizer name: `{row['name']}`", row["changes"]], (
            f"{tool} {row['name']}: the Customizer name and the sentence of what it does under the heading")
        entry = idx[(tool, row["name"])]
        target = f"../../dials/{tool}/{row['name']}.svg"
        if row["diagram"]["view"] == "none":
            assert target not in images, f"{tool}: {row['name']} changes no shape but shows a picture"
            reason = row["note"] or entry["long_description"]
            assert f"No picture. {reason}" in text, f"{tool}: {row['name']} does not say why it has no picture"
        else:
            assert target in images, f"{tool}: no image for {row['name']}"
            alt, desc = images[target]
            assert alt == entry["alt"], f"{tool} {row['name']}: alt {alt!r}"
            assert desc == _expected_caption(row, entry), f"{tool} {row['name']}: the description does not follow the image"


def _card_titles(text: str) -> List[str]:
    lines = text.splitlines()
    return [line[4:] for i, line in enumerate(lines)
            if line.startswith("### ") and i + 2 < len(lines) and _CARD_NAME.match(lines[i + 2])]


def _check_measuring(text: str, tool: str) -> None:
    """The measuring section: an H3 per measure row of the catalog in
    mapping order, each with the Customizer name and the form row, the how
    text and either the typical range with the example or the choices, and
    the stencil card; then the form and its table, then the cards."""
    catalog = load_catalog()
    measured = [r for r in catalog if r["file"] == tool and r["measure"] is not None]
    section = text[text.index(f"## {MEASURE_HEADING}"):text.index("### The measuring form")]
    h3 = [h[1] for h in _headings(section) if h[0] == 3]
    assert h3 == [r["title"] for r in measured], f"{tool}: an H3 per measured dial, its plain title, in order"
    chunks = re.split(r"^### ", section, flags=re.M)[1:]
    for chunk, row in zip(chunks, measured):
        assert f"Customizer name: `{row['name']}`." in chunk, f"{tool}: {row['name']} not named in its section"
        assert re.search(r"(Row \d+ of|Not on) the measuring form\.", chunk), f"{tool}: {row['name']} without its form row"
        m = row["measure"]
        assert m["how"] in chunk, f"{tool}: {row['name']} without its how text"
        if m["typical"] is None:
            assert "The choices:" in chunk, f"{tool}: {row['name']} without its choices"
        else:
            lo, hi = m["typical"]
            assert f"Typical: {lo:g} to {hi:g} mm. Example: {m['example']:g} mm." in chunk, f"{tool}: {row['name']} numbers"
        if m["stencil"]:
            assert f"card {m['stencil']}" in chunk, f"{tool}: {row['name']} without its stencil card"
    form = text[text.index("### The measuring form"):text.index("### Match a card instead of measuring")]
    assert "[measuring-form.svg](measuring-form.svg)" in form and "| # | Customizer name |" in form, f"{tool}: the form"
    assert "[stencil-sheet.svg](../stencil-sheet.svg)" in form, f"{tool}: the paper stencil sheet"


def _check_steps(text: str, tool: str, quick: List[Dict], mapping: Dict[str, Dict]) -> None:
    """The quick start's steps: one H2, an H3 per Step section in mapping
    order, each followed by its line and one list item per quick_start
    dial in order (the plain title, the Customizer name, the sentence of
    what it does, the numbers in plain words), no picture and no card."""
    section = text[text.index(f"## {STEPS_HEADING}"):text.index("## Render, export and print")]
    sections = []
    for r in quick:
        if r["section"] not in sections:
            sections.append(r["section"])
    assert [h[1] for h in _headings(section) if h[0] == 3] == sections, f"{tool}: an H3 per Step section, in order"
    assert "![" not in section and not _card_titles(section), f"{tool}: the quick start's steps carry no picture and no card"
    chunks = re.split(r"^### ", section, flags=re.M)[1:]
    for chunk, name in zip(chunks, sections):
        rows = [r for r in quick if r["section"] == name]
        items = [ln for ln in chunk.splitlines() if ln.startswith("- ")]
        assert items == [dial_line(r, mapping.get(r["name"])) for r in rows], f"{tool} {name}: one item per dial, in order"
        for row, item in zip(rows, items):
            assert item.startswith(f"- **{row['title']}**, `{row['name']}`: {row['changes']}"), f"{tool} {row['name']}"
            assert re.search(r" Default [^;]+(; (range|choices) .+)?\.$", item), f"{tool} {row['name']}: the numbers"


def test_quick_start_page() -> None:
    """Per tool: one H1, the sections in reading order, the storyboard with
    its alt and long description, the measuring section, the four steps as
    lists, safety and the fit note as H3s under Use it, no other dial named
    in backticks, no H4."""
    catalog = load_catalog()
    boards = _storyboards()
    for tool in TOOLS:
        text = (GUIDES / tool / "quick-start.md").read_text(encoding="utf-8")
        heads = _headings(text)
        assert [h for h in heads if h[0] == 1] == [heads[0]] and heads[0] == (1, f"Quick start, {tool} puller"), f"{tool}: one H1 first"
        assert max(level for level, _ in heads) <= 3, f"{tool}: no H4"
        assert [h[1] for h in heads if h[0] == 2] == QUICK_START_H2, f"{tool}: the H2s in order"
        use_it = text[text.index("## Use it"):]
        assert [h[1] for h in _headings(use_it) if h[0] == 3] == QUICK_START_H3_TAIL, f"{tool}: safety and the fit note under Use it"
        board = boards[tool]
        images = _images_with_descriptions(text)
        story = [im for im in images if im[1] == f"../../dials/{tool}/storyboard.svg"]
        assert len(story) == 1 and story[0][0] == board["alt"] and story[0][2] == board["long_description"], (
            f"{tool}: the storyboard image and its long description")
        _check_measuring(text, tool)
        quick = [r for r in catalog if r["file"] == tool and r["quick_start"]]
        mapping = {r["openscad_name"]: r for r in _mapping_rows(tool)}
        _check_steps(text, tool, quick, mapping)
        all_names = {r["name"] for r in catalog if r["file"] == tool}
        quick_names = {r["name"] for r in quick}
        for name in re.findall(r"`([a-z_0-9]+)`", text):
            if name in all_names:
                assert name in quick_names, f"{tool}: {name} is not a quick-start dial"
        assert "](full-guide.md)" in text, f"{tool}: the quick start points at the full guide"


def test_full_guide_page() -> None:
    """Per tool: every catalog row of that file as a card under its
    section's H2, in mapping order (the Steps, then the optional sections),
    with one Default line per dial; the measuring section; the sections
    after the dials in order; a link to the quick start; no H4."""
    catalog = load_catalog()
    idx = _index()
    for tool in TOOLS:
        text = (GUIDES / tool / "full-guide.md").read_text(encoding="utf-8")
        heads = _headings(text)
        assert sum(1 for h in heads if h[0] == 1) == 1 and heads[0] == (1, f"Full guide, {tool} puller"), f"{tool}: one H1"
        assert max(h[0] for h in heads) <= 3, f"{tool}: H1 to H3 only"
        rows = [r for r in catalog if r["file"] == tool]
        ordered = [r for r in rows if r["quick_start"]] + [r for r in rows if not r["quick_start"]]
        assert _card_titles(text) == [r["title"] for r in ordered], f"{tool}: a card per dial in order"
        sections = []
        for r in ordered:
            if r["section"] not in sections:
                sections.append(r["section"])
        h2 = [h[1] for h in heads if h[0] == 2]
        assert h2 == FRONT_H2 + sections[:4] + ["The optional dials"] + sections[4:] + FULL_GUIDE_TAIL, f"{tool}: the H2s in order"
        h3 = [h[1] for h in heads if h[0] == 3]
        assert [h for h in h3 if h in FULL_GUIDE_H3] == FULL_GUIDE_H3, f"{tool}: the full guide's own H3 sections, in order"
        optional = text[text.index("## The optional dials"):text.index(f"## {sections[4]}")]
        counts = {s: sum(1 for r in ordered if r["section"] == s) for s in sections[4:]}
        assert [ln for ln in optional.splitlines() if ln.startswith("- **")] == [
            f"- **{s}**, {counts[s]} dial{'s' if counts[s] != 1 else ''}: "
            + ", ".join(r["title"] for r in ordered if r["section"] == s) + "." for s in sections[4:]], (
            f"{tool}: the optional dials page lists each section with its dials")
        defaults = re.findall(r"^- Default: .+$", text, re.M)
        assert len(defaults) == len(rows), f"{tool}: {len(defaults)} Default lines for {len(rows)} dials"
        _check_measuring(text, tool)
        _check_cards(text, tool, rows, idx)
        assert "](quick-start.md)" in text, f"{tool}: the full guide points at the quick start"


def test_card_numbers_in_plain_words() -> None:
    """A check box reads On or Off, never true or false; a range reads "in
    steps of"; degrees are spelled out; and no page keeps the old
    code-style numbers line or the "Can trip" label."""
    assert settings_rows({"type": "boolean", "default": True}) == [("Default", "On"), ("Choices", "On or off (a check box)")]
    assert settings_rows({"type": "enum", "default": "Medium", "values": ["Small", "Medium"]}) == [
        ("Default", "Medium"), ("Choices", "Small, Medium")]
    assert settings_rows({"type": "float", "default": 25.5, "range": [12.0, 85.0], "step": 0.5, "unit": "mm"}) == [
        ("Default", "25.5 mm"), ("Range", "12 to 85 mm, in steps of 0.5 mm")]
    assert settings_rows({"type": "integer", "default": 2, "range": [1, 3], "step": 1, "unit": None}) == [
        ("Default", "2"), ("Range", "1 to 3, in steps of 1")]
    assert settings_rows({"type": "float", "default": 0, "range": [0, 45], "step": 1, "unit": "deg"})[0] == ("Default", "0 degrees")
    for tool in TOOLS:
        for kind in ("quick-start", "full-guide"):
            text = (GUIDES / tool / f"{kind}.md").read_text(encoding="utf-8")
            assert not re.search(r"^- Default: (true|false)$", text, re.M), f"{tool} {kind}: true/false for a check box"
            assert "Step size" not in text and "Can trip" not in text, f"{tool} {kind}: an old label"


def test_builder_tool_filter() -> None:
    """build_markdown with a tool and a document keeps that tool's rows
    only, as full cards with the numbers, the moved parts, the red warnings
    and the note in plain words, and its sources filled for that tool."""
    md = build_markdown(SAMPLE_ROWS, SAMPLE_MAPPINGS, SAMPLE_INDEX, tool="two-sided", kind="full-guide", form_section=SAMPLE_FORM)
    assert "### Plate thickness" in md
    assert "Customizer name: `plate_thickness`" in md
    assert "measure_plug_length`" not in md.replace("`measure_plug_length` | The plug's length.", "")
    assert "- Default: 4 mm" in md and "- Range: 2 to 8 mm, in steps of 0.25 mm" in md
    assert "- Moves: cord channel, finger lobes" in md
    assert "- Red warnings: PLATE THINNER THAN 2MM - TOO FLIMSY" in md
    assert "Note: The finished sandwich is twice this." in md
    assert "![Plate thickness: before and after, 4 to 6 mm; red marks the cord channel and the finger lobes.](../../dials/two-sided/plate_thickness.svg)" in md
    assert "Two vertical slices of one plate of the two-sided puller." in md
    assert "#### " not in md
    assert "src/Plug_Puller_Two_Sided.scad" in md and "Plug_Puller_Parametric" not in md, "the sources are filled for the tool"


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


def _sections_of(html: str) -> List[str]:
    """The major sections of the print in order, by the id of the H2 each opens with."""
    return re.findall(r'<section class="section">\s*(?:<section class="opener" id="([^"]+)"|(?:<div class="[a-z]+">\s*)*<h2 id="([^"]+)")', html)


def test_document_html() -> None:
    """The full guide's HTML, in order: the cover, the contents, the opener
    with the storyboard figure, the get-the-file prose, the measuring
    section as a table, the card (the plain title, the Customizer name, a
    figure holding the SVG with the long description as its caption), the
    assembly prose, and last the form page and a stencil page with their
    SVGs at 210 mm; every H2 opening a section of its own; a photo from a
    source as an absolute file path; a link to another file kept as words;
    US Letter pages; no figure scaled above 1:1; the picture key in the
    page foot; and the contents printing the page numbers it is given."""
    args = dict(rows=SAMPLE_ROWS, mappings=SAMPLE_MAPPINGS, index=SAMPLE_INDEX, svgs=SAMPLE_SVGS, tool="one-sided",
                kind="full-guide", storyboards=SAMPLE_STORYBOARDS, storyboard_svg=SAMPLE_STORYBOARD_SVG,
                form_svg=SAMPLE_FORM_SVG, stencil_svgs=[SAMPLE_FORM_SVG], form_section=SAMPLE_FORM)
    html = build_html(**args)
    order = [html.index(s) for s in ('class="page cover"', 'class="front contents"', 'class="opener"', 'id="get-the-file"',
                                     'id="measure-your-plug-and-your-hand"', '<table class="grid measures">',
                                     'id="dial-one-sided-measure_plug_length"', 'id="assemble"',
                                     'class="page form" id="part-form"')]
    assert order == sorted(order), "the document's sections are out of order"
    assert html.count('<section class="card"') == 1 and html.count('class="page form"') == 2
    assert "<h3>Plug length</h3>" in html and "Customizer name: <b>measure_plug_length</b>" in html
    assert "plate_thickness" not in html
    assert "<figcaption>Two top views of the one-sided puller, before left and after right.</figcaption>" in html
    assert "<figcaption>Five stages of the one-sided puller, left to right.</figcaption>" in html
    opened = [a or b for a, b in _sections_of(html)]
    assert opened == ["which-tool-this-is", "get-the-file", "measure-your-plug-and-your-hand", "sec-step-1---your-plug",
                      "the-optional-dials", "render-export-and-print", "assemble", "use-it", "if-the-print-does-not-fit",
                      "advanced-settings", "going-deeper"], "every H2 opens a section of its own"
    assert html.count("<h2") == len(opened), "an H2 outside its section"
    assert "| # | Customizer name |" not in html and "________" not in html, "the print carries the sheet, not its text twin"
    assert 'src="file:///' in html and "one-sided-lamp-plug-medium.jpg" in html, "a photo by its absolute path"
    assert '<div class="photo-row">' in html, "photos that follow each other stand in a row"
    assert "bill of materials</a>" not in html and "bill of materials" in html, "a file link keeps its words"
    assert 'href="https://openscad.org/downloads.html"' in html, "a web link stays a link"
    assert "size: 215.9mm 279.4mm" in html, "the pages are not US Letter"
    assert "@bottom-left" in html and "In every picture" in html, "the full guide's pages carry the picture key"
    figures = re.findall(r'<figure[^>]*>\s*<svg[^>]*viewBox="0 0 ([\d.]+) [\d.]+"[^>]*width="([\d.]+)mm"', html)
    assert len(figures) == 2, "the card figure and the storyboard"
    for vb_w, width in figures:
        assert float(width) <= float(vb_w) + 1e-6, "a figure is scaled above 1:1"
    anchors = re.findall(r'<a href="#([^"]+)">', html)
    assert "part-form" not in anchors and len(anchors) == len(set(anchors)), "each contents entry once"
    pages = {a: i + 3 for i, a in enumerate(anchors)}
    pages["part-form"] = len(anchors) + 3
    numbered = build_html(**args, pages=pages)
    assert (f'<a href="#assemble"><span class="t">Assemble</span><span class="dots"></span><span class="pg">{pages["assemble"]}</span></a>'
            in numbered)
    assert f"printed at true size on page {pages['part-form']}" in numbered


def test_quick_start_html() -> None:
    """The quick start's HTML: the four steps as one section with a table
    per step (the sample's one Step), the dial as a row with its title, its
    Customizer name, its sentence and its numbers, no card and no dial
    figure; the steps and their dials in the contents; no picture key in
    the page foot."""
    html = build_html(rows=SAMPLE_ROWS, mappings=SAMPLE_MAPPINGS, index=SAMPLE_INDEX, svgs=SAMPLE_SVGS, tool="one-sided",
                      kind="quick-start", storyboards=SAMPLE_STORYBOARDS, storyboard_svg=SAMPLE_STORYBOARD_SVG,
                      form_svg=SAMPLE_FORM_SVG, stencil_svgs=[SAMPLE_FORM_SVG], form_section=SAMPLE_FORM)
    opened = [a or b for a, b in _sections_of(html)]
    assert opened == ["which-tool-this-is", "get-the-file", "measure-your-plug-and-your-hand", "the-four-customizer-steps",
                      "render-export-and-print", "assemble", "use-it"], "every H2 opens a section of its own"
    assert '<section class="card"' not in html and html.count("<figure") == 1 + html.count('<figure class="photo">'), (
        "the quick start draws the storyboard and the photos only")
    assert ('<div class="keep"><h2 id="the-four-customizer-steps">The four Customizer steps</h2>' in html
            and '<h3 id="sec-step-1---your-plug">Step 1 - Your Plug</h3>'
            '<p class="step-intro">Pick a plug preset, or leave it on Measure my plug and type your plug\'s numbers.</p>'
            '<table class="grid dials">' in html), "the section heading, its line and the first step in one box"
    assert ('<tr id="dial-one-sided-measure_plug_length"><th scope="row">Plug length<span class="cname">measure_plug_length</span></th>'
            "<td>Runs the pocket farther toward the finger holes.</td>"
            "<td><b>Default:</b> 25.5 mm<br><b>Range:</b> 12 to 85 mm, in steps of 0.5 mm</td></tr>") in html
    assert '<a href="#sec-step-1---your-plug"><span class="t">Step 1 - Your Plug</span>' in html and '<p class="dials">Plug length</p>' in html
    assert '<h3 id="safety">' in html and "@bottom-left" not in html
