#!/usr/bin/env python3
"""Build a tool's two guide documents: the quick start and the full guide,
each as a Markdown page and a printed PDF.

``--tool one-sided`` or ``--tool two-sided`` reads ``dial_catalog.json``
(its ``measure`` rows too), the two parameter mappings, the diagram index
(``docs/dials/dial_diagrams_index.json``), the storyboard index, the
measuring form (``scripts/generate_measuring_form.py`` supplies its text)
and the hand-written sources under ``docs/guides/source/`` (one topic each,
written once; ``scripts/guide_text.py`` loads and converts them). From those
it assembles, in the same order for the page and the print:

* the quick start (``docs/guides/<tool>/quick-start.md``): which tool this
  is, get the file, measure (with the stencil cards and the form), the four
  Customizer steps with one card per dial, render and print, assemble, use,
  safety, and where to look when the print does not fit;
* the full guide (``docs/guides/<tool>/full-guide.md``): the same, plus the
  browser notes, the outline sheets, every optional dial, what to buy, care,
  the fit table, every red warning tag, printing problems, how the advanced
  dials work, saved settings and the command line, and where to go deeper.

Each dial's card carries its plain title, the name the Customizer shows, the
sentence of what it does, its picture (or, for a dial that changes no
shape, why there is none) and its numbers in plain words. ``--document``
picks one of the two.

Without ``--markdown-only`` each document is also printed as a PDF
(``docs/Plug_Puller_<Tool>_Quick_Start.pdf`` and ``..._Full_Guide.pdf``) on
US Letter pages: a cover, a contents page with page numbers, the same
sections as cards and prose that flow down the pages (never a picture
above 1:1), and, at exactly 210 × 279 mm centered on the last pages, the
measuring form and the paper stencil sheets. Each flowing page carries the
document's name at the top and the picture key line and the page number at
the bottom. The PDF is printed until its page numbers settle: the first
print finds the page of every contents entry, the next one prints them.

The date is never printed, so the PDF is reproducible. The SVGs are inlined
into the HTML, which keeps each diagram's <title>/<desc> text equivalent in
the page.

Usage:
    python scripts/build_dial_reference.py --tool one-sided                  # both pages and both PDFs
    python scripts/build_dial_reference.py --tool two-sided --markdown-only  # the pages only, no browser
    python scripts/build_dial_reference.py --tool two-sided --document quick-start

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import argparse
import html
import json
import logging
import math
import re
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.build_outline_sheets_pdf import (  # noqa: E402
    ACCENT,
    ACCENT_TINT,
    BORDER_GRAY,
    PAGE_H_MM,
    PAGE_W_MM,
    RULE_GRAY,
    TEXT_GRAY,
    print_to_pdf,
    verify_pdf,
)
from scripts.generate_dial_diagrams import (  # noqa: E402
    COLOR_PLUG,
    COLOR_TRACE,
    LEGEND_LINE,
    MARK_DASH,
    MARK_W,
)
from scripts.generate_outline_sheets import MODEL_VERSION  # noqa: E402
from scripts.guide_text import anchor, headings, load_source, markdown_to_blocks  # noqa: E402

logger = logging.getLogger(__name__)

CATALOG = PROJECT_ROOT / "dial_catalog.json"
MAPPINGS = {
    "one-sided": PROJECT_ROOT / "parameter_mapping.json",
    "two-sided": PROJECT_ROOT / "parameter_mapping_two_sided.json",
}
DIALS_DIR = PROJECT_ROOT / "docs" / "dials"
INDEX = DIALS_DIR / "dial_diagrams_index.json"
STORYBOARDS = DIALS_DIR / "storyboards_index.json"
SCRATCH = PROJECT_ROOT / "tmp_renders" / "dial_reference"
EDGE_PROFILE = PROJECT_ROOT / "tmp_renders" / "edge_profile"

CONTENTS_HEADING = "Contents"
NAME_LABEL = "Customizer name"
MOVES_LABEL = "Moves"
WARNINGS_LABEL = "Red warnings"
NOTE_LABEL = "Note"
NO_PICTURE = "No picture."
KEY_TITLE = "How to read the pictures"
UNIT_WORDS = {"deg": "degrees"}

RED_TEXT = (
    "If red text appears beside the part in the preview, read it: it names the measurement "
    "to fix, and the part will not fit until it is gone."
)

# The packets print on US Letter (8.5 × 11 in), the owner's choice of
# 2026-09-28; the measuring form keeps its 210 × 279 mm sheet, centered at 1:1.
LETTER_W_MM, LETTER_H_MM = 215.9, 279.4

# The per-tool guide packets (R3, FD-44): one folder of Markdown twins per
# tool, the prose blocks below as their own strings rows.
TOOL_WORDS = {"one-sided": "one-sided puller", "two-sided": "two-sided puller"}
PACKET_DIRS = {
    "one-sided": PROJECT_ROOT / "docs" / "guides" / "one-sided",
    "two-sided": PROJECT_ROOT / "docs" / "guides" / "two-sided",
}
PACKET_EYEBROW = "Plug Puller"
PACKET_FIGURE_MAX_SCALE = 1.0  # a packet never draws a picture above 1:1 (D-022)
PACKET_TALL_MM = 120.0  # a card whose figure is taller than this starts a new page
PACKET_STORY_MAX_H_MM = 96.0  # the storyboard's height cap, so the opener fits on one page
PACKET_OPENER_HEADING = "Which tool this is"
PACKET_OPENERS = {
    "one-sided": (
        "This guide is for the one-sided puller, src/Plug_Puller_Parametric.scad: the tool for a wall plug up to "
        "24 mm thick, a pocket around the plug's back and sides with two finger holes below it, pulled with one "
        "hand. Measure your plug's thickness first. Thicker than 24 mm, or a plug you want held from both sides "
        "such as a USB-C tip or a round extension-cord plug, is the two-sided puller's job, and that tool has its "
        "own guide.",
        "your plug, your size, the attachment and the hook's side",
    ),
    "two-sided": (
        "This guide is for the two-sided puller, src/Plug_Puller_Two_Sided.scad: two serrated plates that "
        "zip-tie around the plug and close across it, for a plug 24 mm thick or more and for a plug held from "
        "both sides, a USB-C tip or a round extension-cord plug. A thinner wall plug is the one-sided puller's "
        "job, and that tool has its own guide.",
        "your plug, your size, the attachment and the print layout",
    ),
}
# The opener's second paragraph: what the document covers, with the tool's
# four steps filled in from PACKET_OPENERS.
OPENER_SCOPE = {
    "quick-start": ("The Customizer's four steps are {steps}. This quick start covers getting the file, measuring "
                    "your plug and your hand or matching a card, each step's dials with a picture, then printing, "
                    "assembly and use."),
    "full-guide": ("The Customizer's four steps are {steps}. This full guide covers getting the file, measuring "
                   "your plug and your hand or matching a card, every dial with a picture, printing, assembly, use "
                   "and care, what to do when a print does not fit, every warning, and how the advanced dials work."),
}


def opener_paragraphs(tool: str, kind: str) -> Tuple[str, str]:
    """Which tool this is, and what this document covers."""
    return PACKET_OPENERS[tool][0], OPENER_SCOPE[kind].format(steps=PACKET_OPENERS[tool][1])
STEP_CAPTIONS = {
    "one-sided": ("Step 1: type your plug's numbers", "Step 2: pick your hand size",
                  "Step 3: pick how it attaches", "Step 4: pick the hook's side"),
    "two-sided": ("Step 1: type your plug's numbers and pick Rounded sides or Flat sides", "Step 2: pick your hand size",
                  "Step 3: pick how it attaches; a plug this short gets no strap slot", "Step 4: both plates in one file"),
}
# One line under each Step heading of the quick start, in the Step sections'
# order. No default is named here: the card below it prints the default from
# the mapping, so a changed default cannot leave this line stale.
STEP_INTROS = {
    "one-sided": (
        "Pick a plug preset, or leave it on Measure my plug and type your plug's numbers.",
        "Pick your hand size, or pick Measure my hand and type your hand's numbers.",
        "Pick how the tool attaches.",
        "Pick the hook's side.",
    ),
    "two-sided": (
        "Pick a plug preset, or leave it on Measure my plug and type your plug's numbers; then pick Rounded "
        "sides or Flat sides.",
        "Pick your hand size, or pick Measure my hand and type your finger width.",
        "Pick how the tool attaches.",
        "Pick whether the file holds both plates or one.",
    ),
}
MEASURING_INTRO = (
    "Everything here is in mm: a US plug is about 25 mm wide, so a 1 on your paper means you measured in inches. "
    "You need a caliper or a ruler with mm marks, the plug in its outlet, and your own hand only if you pick "
    "Measure my hand. Print the measuring form at 100 % and fill it in as you go: the sections below are the "
    "form's rows, in the same order, and the card names (R1, C1, F1 / F2) are the cards of the printed "
    "measuring stencil, described under Match a card instead of measuring."
)
MEASURING_INTRO_PLAIN = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", MEASURING_INTRO)
SANITY_CHECK = (
    "Sanity check: each plug width is a two-digit number, roughly 12 to 45, and the prong-end width is usually "
    "the bigger one; the finger width is roughly 14 to 32. A number like 1.3 is inches: measure again with the "
    "mm side."
)
RING_TRICK = "No caliper? Take a ring that fits that finger snugly, measure the ring's inner diameter in mm and add 1.5 mm."
FOR_SOMEONE_ELSE = (
    "When you measure for someone else, a relative or a client, measure their hand for the finger and hand rows "
    "and their outlet and plug for the plug rows. Doubtful between two values? Round up: a slightly roomy fit "
    "works, a tight one does not."
)
TWO_SIDED_WIDTHS = (
    "The two-sided puller's widths are the size the two plates close across, so measure across the plug the way "
    "the plates will grip it. The thickness pair, the wall plate style and the hand width belong to the one-sided "
    "puller only."
)

FIGURE_W_MM = 170.0
FIGURE_MAX_H_MM = 140.0
FIGURE_MAX_SCALE = 2.0  # a cropped detail is drawn at most twice its 1:1 size

# Which warning tags name a dial in the red warning tag tables of the full
# guides (docs/guides/source/tags-one-sided.md and tags-two-sided.md, their
# "What to do" column). Kept by hand from those tables; a dial without an
# entry shows no "Red warnings" row.
TAGS_BY_DIAL: Dict[Tuple[str, str], List[str]] = {
    ("one-sided", "strap_width"): ["WING OPENING SMALLER THAN STRAP WIDTH", "WING WEB COLLAPSED - NO ROOM FOR STRAP"],
    ("one-sided", "velcro_style"): ["WING OPENING SMALLER THAN STRAP WIDTH"],
    ("one-sided", "zip_pos_1"): ["ZIP TIE HOLES HIT FINGER HOLES", "ZIP TIE ROWS OVERLAP EACH OTHER", "ZIP TIE HOLES HIT VELCRO SLOTS"],
    ("one-sided", "zip_pos_2"): ["ZIP TIE HOLES HIT FINGER HOLES", "ZIP TIE ROWS OVERLAP EACH OTHER", "ZIP TIE HOLES HIT VELCRO SLOTS"],
    ("one-sided", "zip_pos_3"): ["ZIP TIE HOLES HIT FINGER HOLES", "ZIP TIE ROWS OVERLAP EACH OTHER", "ZIP TIE HOLES HIT VELCRO SLOTS"],
    ("one-sided", "velcro_pos"): ["ZIP TIE HOLES HIT VELCRO SLOTS"],
    ("one-sided", "custom_enable_auto_fit"): [
        "ZIP TIE HOLES HIT FINGER HOLES", "FINGER HOLES OUTSIDE BODY", "POCKET SEAT WIDER THAN TOP EDGE",
        "POCKET WIDER THAN BODY", "WALL NOTCH WIDER THAN TOP EDGE",
    ],
    ("two-sided", "plate_cable_clearance"): ["CORD TOO THICK FOR CABLE CHANNEL", "PLUG NARROWER THAN THE CORD CHANNEL - ARMS CANNOT TOUCH IT"],
    ("two-sided", "plate_grip_bite"): ["NO GRIP BITE - PLUG WONT BE HELD"],
    ("two-sided", "plate_thickness"): ["PLATE THINNER THAN 2MM - TOO FLIMSY"],
    ("two-sided", "plate_zip_pos_1"): ["ZIP STATION OFF THE ARM", "ZIP STATIONS OVERLAP EACH OTHER", "STRAP WIDER THAN ARM SLOT WINDOW - NARROW THE STRAP"],
    ("two-sided", "plate_zip_pos_2"): ["ZIP STATION OFF THE ARM", "ZIP STATIONS OVERLAP EACH OTHER", "ZIP STATION HITS VELCRO SLOT", "STRAP WIDER THAN ARM SLOT WINDOW - NARROW THE STRAP"],
    ("two-sided", "plate_zip_pos_3"): ["ZIP STATION OFF THE ARM", "ZIP STATIONS OVERLAP EACH OTHER", "ZIP STATION HITS VELCRO SLOT", "STRAP WIDER THAN ARM SLOT WINDOW - NARROW THE STRAP"],
    ("two-sided", "strap_width"): ["STRAP WIDER THAN ARM SLOT WINDOW - NARROW THE STRAP"],
    ("two-sided", "plate_velcro_slot_length"): ["STRAP WIDER THAN ARM SLOT WINDOW - NARROW THE STRAP"],
    ("two-sided", "plate_cradle_depth"): ["CRADLE SHALLOWER THAN ASKED - PLUG NARROW"],
}


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------


def load_catalog() -> List[Dict[str, Any]]:
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def load_mappings() -> Dict[str, Dict[str, Dict[str, Any]]]:
    out = {}
    for key, path in MAPPINGS.items():
        data = json.loads(path.read_text(encoding="utf-8"))
        out[key] = {row["openscad_name"]: row for row in data["parameters"]}
    return out


def load_index() -> List[Dict[str, Any]]:
    return json.loads(INDEX.read_text(encoding="utf-8"))


def load_storyboards() -> Dict[str, Dict[str, Any]]:
    """The storyboard index keyed by tool; empty when the file is missing."""
    if not STORYBOARDS.exists():
        return {}
    return {e["file"]: e for e in json.loads(STORYBOARDS.read_text(encoding="utf-8"))}


def load_svgs(rows: Sequence[Dict[str, Any]]) -> Dict[Tuple[str, str], str]:
    return {
        (r["file"], r["name"]): (DIALS_DIR / r["file"] / f"{r['name']}.svg").read_text(encoding="utf-8")
        for r in rows
    }


def sections_in_order(rows: Sequence[Dict[str, Any]], mapping: Dict[str, Dict[str, Any]]) -> List[str]:
    order: List[str] = []
    for mrow in mapping.values():
        if mrow["section"] not in order:
            order.append(mrow["section"])
    for r in rows:
        if r["section"] not in order:
            order.append(r["section"])
    return order


def fmt(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _with_unit(value: Any, unit: str) -> str:
    return f"{fmt(value)} {unit}".rstrip()


def settings_rows(mrow: Optional[Dict[str, Any]]) -> List[Tuple[str, str]]:
    """The numbers the Customizer allows, as (label, value) pairs in plain
    words: the default, then the range with its step or the choices. A check
    box reads On or Off, never true or false, and a step is written "in steps
    of", never "Step 0.5" (the docs gate reads "step 0" as the retired
    section name)."""
    if not mrow:
        return []
    kind = mrow.get("type")
    if kind == "boolean":
        return [("Default", "On" if mrow.get("default") else "Off"), ("Choices", "On or off (a check box)")]
    if kind == "enum":
        return [("Default", fmt(mrow.get("default"))), ("Choices", ", ".join(mrow.get("values", [])))]
    unit = UNIT_WORDS.get(mrow.get("unit") or "", mrow.get("unit") or "")
    out = [("Default", _with_unit(mrow.get("default"), unit))]
    if mrow.get("range"):
        lo, hi = mrow["range"]
        text = f"{fmt(lo)} to {_with_unit(hi, unit)}"
        if mrow.get("step") is not None:
            text += f", in steps of {_with_unit(mrow['step'], unit)}"
        out.append(("Range", text))
    return out


def card_facts(row: Dict[str, Any], mrow: Optional[Dict[str, Any]], entry: Dict[str, Any]) -> List[Tuple[str, str]]:
    """The card's facts: the numbers, then the parts the dial moves."""
    facts = settings_rows(mrow)
    features = entry.get("features") or []
    if features and features != ["none"]:
        facts.append((MOVES_LABEL, ", ".join(features)))
    return facts


def warnings_for(row: Dict[str, Any]) -> List[str]:
    return TAGS_BY_DIAL.get((row["file"], row["name"])) or []


def no_picture_text(row: Dict[str, Any], entry: Dict[str, Any]) -> str:
    """Why a dial that changes no shape has no picture: its note, or the
    index's long description when the row has no note."""
    return f"{NO_PICTURE} {row.get('note') or entry.get('long_description') or ''}".strip()


def caption_text(row: Dict[str, Any], entry: Dict[str, Any]) -> str:
    """The picture's long description without the clause that repeats the
    card's sentence of what the dial does, which the card prints just above
    the picture (63 of the 118 descriptions quote it after a colon)."""
    long = entry.get("long_description") or ""
    core = row["changes"].rstrip(".")
    return long.replace(f": {core[:1].lower()}{core[1:]}.", ".", 1)


def form_row_text(k: Optional[int]) -> str:
    return f"Row {k} of the measuring form." if k else "Not on the measuring form."


# ---------------------------------------------------------------------------
# The two documents of a tool, as blocks shared by the page and the print
# ---------------------------------------------------------------------------

DOCUMENTS = ("quick-start", "full-guide")
DOC_TITLES = {"quick-start": "Quick start", "full-guide": "Full guide"}
DOC_PDFS = {
    ("one-sided", "quick-start"): "docs/Plug_Puller_One_Sided_Quick_Start.pdf",
    ("one-sided", "full-guide"): "docs/Plug_Puller_One_Sided_Full_Guide.pdf",
    ("two-sided", "quick-start"): "docs/Plug_Puller_Two_Sided_Quick_Start.pdf",
    ("two-sided", "full-guide"): "docs/Plug_Puller_Two_Sided_Full_Guide.pdf",
}
DOC_BLURBS = {
    "quick-start": ("The shortest path from a stuck plug to a printed {tool} that fits it and your hand: get the "
                    "file, measure, fill in the four Customizer steps, print, assemble, use."),
    "full-guide": ("Everything about the {tool}: getting the file, measuring, every dial with a picture, printing, "
                   "assembly, use and care, what to do when a print does not fit, every warning, and how the "
                   "advanced dials work."),
}
DOC_OTHER = {"quick-start": ("full-guide", "the full guide"), "full-guide": ("quick-start", "the quick start")}
STENCIL_SHEETS = {"one-sided": ("stencil-sheet.svg", "stencil-sheet-2.svg"), "two-sided": ("stencil-sheet.svg",)}
MEASURE_HEADING = "Measure your plug and your hand"
FORM_HEADING = "The measuring form"
OPTIONAL_HEADING = "The optional dials"
OPTIONAL_INTRO = ("Everything below Step 4 in the Customizer is optional. These dials apply in every hand size, except "
                  "the sections marked (Custom size only), which do nothing until Step 2's hand size is Custom. The "
                  "sections follow in the Customizer's order; how they work together is explained after the "
                  "troubleshooting sections.")
FORM_NOTE = ("Print the form at 100 % (actual size, never fit to page) and check its 50 mm bar with a ruler before you "
             "trust it. Fill in the blanks top to bottom as you measure, then type the numbers into the Customizer in "
             "the same order.")
FORM_WHERE_PDF = "The form is printed at true size on page {page}, at the end of this guide; the paper stencil sheets follow it."
FORM_WHERE_MD = "The form is the sheet [measuring-form.svg](measuring-form.svg); the paper stencil sheets are {sheets}."


def _step_sections(quick: Sequence[Dict[str, Any]], mapping: Dict[str, Dict[str, Any]], tool: str):
    """The quick start's Step sections, each with its line from STEP_INTROS,
    matched by the number in "Step N - ..."."""
    out = []
    for section, in_section in _sections(quick, mapping):
        m = re.match(r"Step (\d+) - ", section)
        if not m or not 1 <= int(m.group(1)) <= len(STEP_INTROS[tool]):
            raise ValueError(f"{tool}: no line in STEP_INTROS for the section {section!r}")
        out.append(((section, in_section), STEP_INTROS[tool][int(m.group(1)) - 1]))
    return out


def _optional_rows(rows: Sequence[Dict[str, Any]], tool: str) -> List[Dict[str, Any]]:
    """The dials after the four steps: the tool's rows the quick start does
    not show."""
    return [r for r in rows if r["file"] == tool and not r.get("quick_start")]


def document_blocks(kind: str, tool: str, rows: Sequence[Dict[str, Any]],
                    mapping: Dict[str, Dict[str, Any]]) -> List[tuple]:
    """The blocks of one document in reading order. Each is a tuple whose
    first item names its kind: head, opener, source (a file under
    docs/guides/source/), text (Markdown made here), measuring, form,
    cards (one Customizer section) or sheets (the 1:1 pages at the end)."""
    if kind not in DOCUMENTS:
        raise ValueError(f"unknown document {kind!r}")
    quick = [r for r in rows if r["file"] == tool and r.get("quick_start")]
    full = kind == "full-guide"
    blocks: List[tuple] = [("head",), ("opener",), ("source", "get-the-file")]
    if full:
        blocks.append(("source", "browser-notes"))
    blocks += [("measuring",), ("source", "stencil-cards")]
    if full:
        blocks.append(("source", f"outline-sheets-{tool}"))
    blocks.append(("form",))
    for (section, in_section), intro in _step_sections(quick, mapping, tool):
        blocks.append(("cards", section, in_section, intro))
    if full:
        blocks.append(("text", f"## {OPTIONAL_HEADING}\n\n{OPTIONAL_INTRO}"))
        for section, in_section in _sections(_optional_rows(rows, tool), mapping):
            blocks.append(("cards", section, in_section, ""))
    blocks.append(("source", "render-and-print"))
    if full:
        blocks.append(("source", "what-to-buy"))
    blocks += [("source", f"assemble-{tool}"), ("source", f"use-{tool}"), ("source", "safety")]
    if full:
        blocks += [("source", "care"), ("source", f"fit-{tool}"), ("source", f"tags-{tool}"),
                   ("source", "printing-problems"), ("source", f"advanced-{tool}"),
                   ("source", "workflow-tools"), ("source", "going-deeper")]
    else:
        blocks.append(("source", "if-it-does-not-fit"))
    blocks.append(("sheets",))
    return blocks


def _measured_rows(rows: Sequence[Dict[str, Any]], tool: str) -> List[Dict[str, Any]]:
    return [r for r in rows if r["file"] == tool and r.get("measure")]


def _form_row(mapping: Dict[str, Dict[str, Any]], name: str) -> Optional[int]:
    step_names = [n for n, mrow in mapping.items() if mrow["section"].startswith("Step")]
    return step_names.index(name) + 1 if name in step_names else None


# ---------------------------------------------------------------------------
# The Markdown page
# ---------------------------------------------------------------------------


def dial_card(row: Dict[str, Any], mrow: Optional[Dict[str, Any]], entry: Dict[str, Any],
              rel: str = "../../dials") -> List[str]:
    """One dial's card in Markdown: an H3 with the plain title, the name the
    Customizer shows, the sentence of what the dial does, the picture with
    the index's alt text and its description right under it (or, for a dial
    that changes no shape, why there is no picture), the numbers and the
    moved parts as a list with the red warnings, then the note."""
    lines = [f"### {row['title']}", "", f"{NAME_LABEL}: `{row['name']}`", "", row["changes"], ""]
    if row["diagram"]["view"] == "none":
        lines += [no_picture_text(row, entry), ""]
    else:
        alt = entry.get("alt") or row["changes"]
        lines += [f"![{alt}]({rel}/{row['file']}/{row['name']}.svg)", ""]
        caption = caption_text(row, entry)
        if caption:
            lines += [caption, ""]
    items = [f"- {label}: {value}" for label, value in card_facts(row, mrow, entry)]
    tags = warnings_for(row)
    if tags:
        items.append(f"- {WARNINGS_LABEL}: " + "; ".join(tags))
    if items:
        lines += items + [""]
    if row.get("note") and row["diagram"]["view"] != "none":
        lines += [f"{NOTE_LABEL}: {row['note']}", ""]
    return lines


def _sections(rows_of_file: Sequence[Dict[str, Any]], mapping: Dict[str, Dict[str, Any]]):
    for section in sections_in_order(rows_of_file, mapping):
        in_section = [r for r in rows_of_file if r["section"] == section]
        if in_section:
            yield section, in_section


def _document_head(kind: str, tool: str) -> List[str]:
    other_kind, other_words = DOC_OTHER[kind]
    pdf = Path(DOC_PDFS[(tool, kind)]).name
    return [f"# {DOC_TITLES[kind]}, {TOOL_WORDS[tool]}", "", DOC_BLURBS[kind].format(tool=TOOL_WORDS[tool]), "",
            f"Model version {MODEL_VERSION}. [The printable {DOC_TITLES[kind].lower()}](../../{pdf}) has the same "
            "text, with the measuring form and the paper stencil sheets at true size as its last pages. The other "
            f"document for this tool is [{other_words}]({other_kind}.md). Each dial is headed by its plain name, "
            "with the name the Customizer shows on the line under it.", ""]


def _opener_markdown(tool: str, kind: str, storyboards: Dict[str, Dict[str, Any]]) -> List[str]:
    which, scope = opener_paragraphs(tool, kind)
    lines = [f"## {PACKET_OPENER_HEADING}", "", which, "", scope, "",
             RED_TEXT, "", f"In every picture: {LEGEND_LINE}.", ""]
    board = storyboards.get(tool)
    if board:
        lines += [f"![{board['alt']}](../../dials/{tool}/storyboard.svg)", "", board["long_description"], ""]
        lines += [f"- {caption}" for caption in STEP_CAPTIONS[tool]] + [""]
    return lines


def _measuring_markdown(rows, mapping, tool: str) -> List[str]:
    lines = [f"## {MEASURE_HEADING}", "", MEASURING_INTRO, ""]
    if tool == "two-sided":
        lines += [TWO_SIDED_WIDTHS, ""]
    for row in _measured_rows(rows, tool):
        m = row["measure"]
        k = _form_row(mapping, row["name"])
        lines += [f"### {row['title']}", "", f"{NAME_LABEL}: `{row['name']}`. {form_row_text(k)}", "", m["how"], ""]
        if m["typical"] is None:
            mrow = mapping.get(row["name"]) or {}
            lines += ["The choices: " + ", ".join(mrow.get("values", [])) + ".", ""]
        else:
            lo, hi = m["typical"]
            lines += [f"Typical: {lo:g} to {hi:g} mm. Example: {m['example']:g} mm.", ""]
        if m.get("stencil"):
            lines += [f"With the stencil: card {m['stencil']}.", ""]
        if row["name"] == "measure_finger_width":
            lines += [RING_TRICK, ""]
    lines += [SANITY_CHECK, "", FOR_SOMEONE_ELSE, ""]
    return lines


def _form_markdown(tool: str, form_section: str) -> List[str]:
    sheets = " and ".join(f"[{name}](../{name})" for name in STENCIL_SHEETS[tool])
    return [f"### {FORM_HEADING}", "", FORM_WHERE_MD.format(sheets=sheets) + " " + FORM_NOTE, "", form_section, ""]


def build_markdown(rows: Sequence[Dict[str, Any]], mappings: Dict[str, Dict[str, Dict[str, Any]]],
                   index: Sequence[Dict[str, Any]], tool: str, kind: str,
                   storyboards: Optional[Dict[str, Dict[str, Any]]] = None,
                   form_section: Optional[str] = None) -> str:
    """One document of a tool as its Markdown page. ``form_section`` is the
    measuring form's text (the rows and what the sheet shows); without it
    the form generator supplies it."""
    idx = {(e["file"], e["name"]): e for e in index}
    mapping = mappings.get(tool, {})
    if form_section is None:
        form_section = measuring_form_section(tool)
    lines: List[str] = []
    for block in document_blocks(kind, tool, rows, mapping):
        if block[0] == "head":
            lines += _document_head(kind, tool)
        elif block[0] == "opener":
            lines += _opener_markdown(tool, kind, storyboards or {})
        elif block[0] == "source":
            lines += [load_source(block[1], tool), ""]
        elif block[0] == "text":
            lines += [block[1], ""]
        elif block[0] == "measuring":
            lines += _measuring_markdown(rows, mapping, tool)
        elif block[0] == "form":
            lines += _form_markdown(tool, form_section)
        elif block[0] == "cards":
            _kind, section, in_section, intro = block
            lines += [f"## {section}", ""] + ([intro, ""] if intro else [])
            for row in in_section:
                lines += dial_card(row, mapping.get(row["name"]), idx.get((tool, row["name"]), {}))
        elif block[0] == "sheets":
            pass
    return "\n".join(lines).rstrip("\n") + "\n"


def measuring_form_section(tool: str) -> str:
    """The measuring form's text section, from the form generator."""
    from scripts.generate_measuring_form import build_sheet, load_catalog as load_form_catalog
    _sheet, section, _summary = build_sheet(tool, load_form_catalog())
    return section

# ---------------------------------------------------------------------------
# HTML for the PDF
# ---------------------------------------------------------------------------

_SVG_ROOT = re.compile(r"<svg\b[^>]*>", re.S)
_VIEWBOX = re.compile(r'viewBox="([^"]+)"')


def _esc(text: Any) -> str:
    return html.escape(str(text), quote=False)


def figure_svg(svg_text: str, max_scale: float = FIGURE_MAX_SCALE) -> str:
    """The SVG element sized for the page: 170 mm wide, or less when its
    height would pass 140 mm or the scale would pass ``max_scale`` (2:1 for
    the combined reference, 1:1 for the packets); the XML declaration
    dropped."""
    return figure_svg_sized(svg_text, max_scale)[0]


def figure_svg_sized(svg_text: str, max_scale: float = FIGURE_MAX_SCALE,
                     max_h_mm: float = FIGURE_MAX_H_MM) -> Tuple[str, float, float]:
    """``figure_svg`` plus the drawn width and height in mm; ``max_h_mm``
    caps the height (the opener's storyboard shares its page with text)."""
    text = re.sub(r"<\?xml[^>]*\?>\s*", "", svg_text)
    m = _SVG_ROOT.search(text)
    if not m:
        raise ValueError("no <svg> root in the diagram")
    root = m.group(0)
    vb = _VIEWBOX.search(root)
    if not vb:
        raise ValueError("the diagram has no viewBox")
    _x, _y, w, h = (float(v) for v in vb.group(1).split())
    scale = min(FIGURE_W_MM / w, max_h_mm / h, max_scale)
    width, height = w * scale, h * scale
    new_root = re.sub(r'\s(width|height)="[^"]*"', "", root)
    new_root = new_root[:-1] + f' width="{width:.2f}mm" height="{height:.2f}mm">'
    return text[:m.start()] + new_root + text[m.end():], width, height


def sheet_svg(svg_text: str) -> str:
    """A full-page sheet (the measuring form, a stencil sheet) at exactly
    210 × 279 mm."""
    text = re.sub(r"<\?xml[^>]*\?>\s*", "", svg_text)
    m = _SVG_ROOT.search(text)
    if not m:
        raise ValueError("no <svg> root in the sheet")
    root = re.sub(r'\s(width|height)="[^"]*"', "", m.group(0))
    root = root[:-1] + f' width="{PAGE_W_MM:g}mm" height="{PAGE_H_MM:g}mm">'
    return text[:m.start()] + root + text[m.end():]


def dial_id(row: Dict[str, Any]) -> str:
    return f"dial-{row['file']}-{row['name']}"


def _css_string(text: str) -> str:
    """A CSS string literal, for the page margin boxes."""
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def legend_items() -> List[Tuple[str, str, str]]:
    """The picture key as (swatch SVG, color word, meaning), read from
    LEGEND_LINE so the key box and the key printed in every picture agree."""
    parts = LEGEND_LINE.split("; ")
    swatches = (
        '<line x1="1" y1="3" x2="11" y2="3" stroke="#000" stroke-width="0.5"/>',
        f'<rect x="1" y="0.8" width="10" height="4.4" fill="{COLOR_PLUG}"/>',
        f'<line x1="0.8" y1="3" x2="11.2" y2="3" stroke="{COLOR_TRACE}" stroke-width="{MARK_W:g}" '
        f'stroke-dasharray="{MARK_DASH}"/>',
        f'<circle cx="6" cy="3" r="2.3" fill="white" stroke="{COLOR_TRACE}" stroke-width="0.35"/>'
        f'<text x="6" y="4.05" font-size="3" text-anchor="middle" fill="{COLOR_TRACE}" '
        'font-family="Helvetica, Arial, sans-serif">1</text>',
    )
    if len(parts) != len(swatches):
        raise ValueError(f"LEGEND_LINE has {len(parts)} parts but the key box draws {len(swatches)} swatches")
    items = []
    for part, swatch in zip(parts, swatches):
        word, sep, meaning = part.partition(" = ")
        if not sep:
            word, meaning = "", part
        svg = f'<svg aria-hidden="true" width="12mm" height="6mm" viewBox="0 0 12 6">{swatch}</svg>'
        items.append((svg, word[:1].upper() + word[1:], meaning))
    return items


def _facts_table(facts: Sequence[Tuple[str, str]], tags: Sequence[str] = ()) -> str:
    cells = [f'<tr><th scope="row">{_esc(label)}</th><td>{_esc(value)}</td></tr>' for label, value in facts]
    if tags:
        cells.append(f'<tr><th scope="row">{_esc(WARNINGS_LABEL)}</th><td><ul class="tags">'
                     + "".join(f"<li>{_esc(t)}</li>" for t in tags) + "</ul></td></tr>")
    return '<table class="facts">' + "".join(cells) + "</table>" if cells else ""


def packet_card_html(row: Dict[str, Any], mrow: Optional[Dict[str, Any]], entry: Dict[str, Any],
                     svg_text: str, level: int = 3) -> str:
    """One dial's card for the print: the plain title as a heading (h3 under
    a section's h2), the name the Customizer shows, the sentence of what the
    dial does, the picture with its description as the caption (or why there
    is no picture), the facts table with the red warnings, then the note."""
    classes = "card"
    if row["diagram"]["view"] == "none":
        reason = row.get("note") or entry.get("long_description") or ""
        shown = f'<p class="nopic"><b>{_esc(NO_PICTURE)}</b> {_esc(reason)}</p>'
    else:
        figure, _w, h = figure_svg_sized(svg_text, PACKET_FIGURE_MAX_SCALE)
        if h > PACKET_TALL_MM:
            classes += " tall"
        caption = caption_text(row, entry)
        shown = f"<figure>{figure}" + (f"<figcaption>{_esc(caption)}</figcaption>" if caption else "") + "</figure>"
    parts = [f'<section class="{classes}" id="{dial_id(row)}">',
             f'<h{level}>{_esc(row["title"])}</h{level}>',
             f'<p class="cname">{_esc(NAME_LABEL)}: <b>{_esc(row["name"])}</b></p>',
             f'<p class="lead">{_esc(row["changes"])}</p>',
             shown,
             _facts_table(card_facts(row, mrow, entry), warnings_for(row))]
    if row.get("note") and row["diagram"]["view"] != "none":
        parts.append(f'<p class="note"><b>{_esc(NOTE_LABEL)}:</b> {_esc(row["note"])}</p>')
    parts.append("</section>")
    return "\n".join(p for p in parts if p)


def _page_of(pages: Optional[Dict[str, int]], anchor_id: str, offset: int = 0) -> str:
    """The page an anchor landed on in the last print, plus ``offset``; "00"
    before the first print, which keeps most numbers' width."""
    return str(pages[anchor_id] + offset) if pages and anchor_id in pages else "00"


def _print_image_src(tool: str) -> Callable[[str], str]:
    """A picture path as the page under docs/guides/<tool>/ writes it, made
    absolute for the print."""
    def src(path: str) -> str:
        return (PACKET_DIRS[tool] / path).resolve().as_uri()
    return src


def _print_link(href: str) -> Optional[str]:
    """Only web links stay links in the print; a link to another file of the
    project keeps its words."""
    return href if href.startswith(("http://", "https://")) else None


def _measuring_html(rows, mapping, tool: str) -> List[str]:
    m = [f'<h2 id="{anchor(MEASURE_HEADING)}">{_esc(MEASURE_HEADING)}</h2>',
         f'<p class="intro">{_esc(MEASURING_INTRO_PLAIN)}</p>']
    if tool == "two-sided":
        m.append(f'<p class="prose">{_esc(TWO_SIDED_WIDTHS)}</p>')
    for row in _measured_rows(rows, tool):
        mm = row["measure"]
        k = _form_row(mapping, row["name"])
        if mm["typical"] is None:
            facts = [("Choices", ", ".join((mapping.get(row["name"]) or {}).get("values", [])))]
        else:
            lo, hi = mm["typical"]
            facts = [("Typical", f"{lo:g} to {hi:g} mm"), ("Example", f"{mm['example']:g} mm")]
        if mm.get("stencil"):
            facts.append(("Stencil", f"card {mm['stencil']}"))
        m += [f'<section class="measure" id="mg-{dial_id(row)}">', f"<h3>{_esc(row['title'])}</h3>",
              f'<p class="cname"><span>{_esc(NAME_LABEL)}: <b>{_esc(row["name"])}</b></span>'
              f'<span class="formrow">{_esc(f"Form row {k}" if k else "Not on the form")}</span></p>',
              f'<p class="prose">{_esc(mm["how"])}</p>', _facts_table(facts)]
        if row["name"] == "measure_finger_width":
            m.append(f'<p class="prose">{_esc(RING_TRICK)}</p>')
        m.append("</section>")
    m += [f'<p class="callout">{_esc(SANITY_CHECK)}</p>', f'<p class="prose">{_esc(FOR_SOMEONE_ELSE)}</p>']
    return m


def _keep_together(blocks: Sequence[str]) -> List[str]:
    """A heading and the block after it in one unbreakable box, so no
    heading is left alone at the bottom of a page."""
    out: List[str] = []
    i = 0
    while i < len(blocks):
        if blocks[i].startswith(("<h2", "<h3")) and i + 1 < len(blocks):
            out.append('<div class="keep">' + blocks[i] + "\n" + blocks[i + 1] + "</div>")
            i += 2
        else:
            out.append(blocks[i])
            i += 1
    return out


def _prose_html(md: str, tool: str) -> str:
    blocks = markdown_to_blocks(md, image_src=_print_image_src(tool), link_src=_print_link)
    return '<div class="prose">' + "\n".join(_keep_together(blocks)) + "</div>"


def _contents_html(entries: Sequence[tuple], pages: Optional[Dict[str, int]]) -> str:
    """The contents page: every H2 with its page, its H3s indented, and the
    dial titles of a card section in small type."""
    def link(anchor_id: str, text: str) -> str:
        return (f'<a href="#{anchor_id}"><span class="t">{_esc(text)}</span><span class="dots"></span>'
                f'<span class="pg">{_page_of(pages, anchor_id)}</span></a>')
    out = ['<section class="front contents">', f"<h1>{_esc(CONTENTS_HEADING)}</h1>", '<ol class="toc">']
    for anchor_id, text, subs, dials in entries:
        out.append(f"<li>{link(anchor_id, text)}")
        if dials:
            out.append(f'<p class="dials">{_esc(", ".join(dials))}</p>')
        if subs:
            out.append("<ol>" + "".join(f"<li>{link(a, t)}</li>" for a, t in subs) + "</ol>")
        out.append("</li>")
    out += ["</ol>", "</section>"]
    return "\n".join(out)


def _toc_entries_of_source(md: str) -> List[tuple]:
    """Contents entries of a source: each H2 with its H3s; H3s with no H2
    before them hang off the previous block's entry (the caller merges)."""
    entries: List[tuple] = []
    for level, text in headings(md):
        if level == 2:
            entries.append([anchor(text), text, [], []])
        elif level == 3:
            if entries:
                entries[-1][2].append((anchor(text), text))
            else:
                entries.append([None, None, [(anchor(text), text)], []])
    return entries


def document_html(kind: str, tool: str, rows, mappings, index, svgs, storyboards, storyboard_svg: str,
                  form_svg: str, stencil_svgs: Sequence[str], form_section: str,
                  pages: Optional[Dict[str, int]] = None) -> str:
    """One document as the HTML the print is made from."""
    idx = {(e["file"], e["name"]): e for e in index}
    mapping = mappings.get(tool, {})
    title = f"{DOC_TITLES[kind]}, {TOOL_WORDS[tool]}"
    key_line = f"In every picture: {LEGEND_LINE}."
    entries: List[list] = []
    flow: List[str] = []

    def add_entry(anchor_id: str, text: str, dials: Sequence[str] = ()) -> None:
        entries.append([anchor_id, text, [], list(dials)])

    def add_source_entries(md: str) -> None:
        for anchor_id, text, subs, dials in _toc_entries_of_source(md):
            if anchor_id is None:
                if entries:
                    entries[-1][2].extend(subs)
            else:
                entries.append([anchor_id, text, subs, dials])

    for block in document_blocks(kind, tool, rows, mapping):
        if block[0] == "head":
            continue
        if block[0] == "opener":
            board = storyboards.get(tool) or {}
            story_fig, _sw, _sh = figure_svg_sized(storyboard_svg, PACKET_FIGURE_MAX_SCALE, PACKET_STORY_MAX_H_MM)
            key = "".join(f"<li>{svg}<span>" + (f"<b>{_esc(word)}:</b> " if word else "") + f"{_esc(meaning)}</span></li>"
                          for svg, word, meaning in legend_items())
            opener_id = anchor(PACKET_OPENER_HEADING)
            flow.append("\n".join(
                [f'<section class="opener" id="{opener_id}">', f"<h2>{_esc(PACKET_OPENER_HEADING)}</h2>"]
                + [f'<p class="prose">{_esc(par)}</p>' for par in opener_paragraphs(tool, kind)]
                + [f'<p class="callout">{_esc(RED_TEXT)}</p>',
                   f'<div class="key"><p class="key-title">{_esc(KEY_TITLE)}</p><ul>{key}</ul></div>',
                   f'<figure class="story">{story_fig}<figcaption>{_esc(board.get("long_description", ""))}</figcaption></figure>',
                   '<ul class="captions">' + "".join(f"<li>{_esc(cap)}</li>" for cap in STEP_CAPTIONS[tool]) + "</ul>",
                   "</section>"]))
            add_entry(opener_id, PACKET_OPENER_HEADING)
        elif block[0] in ("source", "text"):
            md = load_source(block[1], tool) if block[0] == "source" else block[1]
            flow.append(_prose_html(md, tool))
            add_source_entries(md)
        elif block[0] == "measuring":
            flow += _measuring_html(rows, mapping, tool)
            add_entry(anchor(MEASURE_HEADING), MEASURE_HEADING, [r["title"] for r in _measured_rows(rows, tool)])
        elif block[0] == "form":
            where = FORM_WHERE_PDF.format(page=_page_of(pages, "part-form"))
            flow += [f'<div class="keep"><h3 id="{anchor(FORM_HEADING)}">{_esc(FORM_HEADING)}</h3>'
                     f'<p class="callout">{_esc(where)} {_esc(FORM_NOTE)}</p></div>',
                     _prose_html(form_section, tool)]
            if entries:
                entries[-1][2].append((anchor(FORM_HEADING), FORM_HEADING))
        elif block[0] == "cards":
            _kind, section, in_section, intro = block
            sec_id = f"sec-{anchor(section)}"
            cards = [packet_card_html(row, mapping.get(row["name"]), idx.get((tool, row["name"]), {}),
                                      svgs[(tool, row["name"])]) for row in in_section]
            head = [f'<h2 id="{sec_id}">{_esc(section)}</h2>']
            if intro:
                head.append(f'<p class="step-intro">{_esc(intro)}</p>')
            # The heading, its line and the first card stay on one page.
            flow.append('<div class="keep">' + "\n".join(head + cards[:1]) + "</div>")
            flow += cards[1:]
            add_entry(sec_id, section, [r["title"] for r in in_section])
        elif block[0] == "sheets":
            pass
    # The fixed pages: the cover, the contents, then the flow, then the sheets.
    cover = "\n".join([
        '<section class="page cover">', '<div class="band"></div>', '<div class="cover-body">',
        f'<p class="eyebrow">{_esc(PACKET_EYEBROW)} · {_esc(TOOL_WORDS[tool])}</p>',
        f"<h1>{_esc(title)}</h1>", '<div class="rule"></div>',
        f'<p class="subtitle">{_esc(DOC_BLURBS[kind].format(tool=TOOL_WORDS[tool]))}</p>', "</div>",
        f'<p class="version">Model version {_esc(MODEL_VERSION)}</p>', "</section>"])
    sheets = [f'<section class="page form" id="part-form">{sheet_svg(form_svg)}</section>']
    sheets += [f'<section class="page form">{sheet_svg(svg)}</section>' for svg in stencil_svgs]
    body = [cover, _contents_html(entries, pages), '<div class="flow">'] + flow + ["</div>"] + sheets
    page_w, page_h = f"{LETTER_W_MM:g}mm", f"{LETTER_H_MM:g}mm"
    font = "Helvetica, Arial, sans-serif"
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>{_esc(title)}</title>
<style>
  @page {{ size: {page_w} {page_h}; margin: 0; }}
  @page cover {{ margin: 0; }}
  @page form {{ margin: 0; }}
  @page front {{
    margin: 20mm 22mm 18mm;
    @bottom-right {{ content: "Page " counter(page) " of " counter(pages); font: 2.6mm {font}; color: {TEXT_GRAY}; }}
  }}
  @page flow {{
    margin: 20mm 20mm 18mm;
    @top-left {{ content: {_css_string(f"Plug Puller · {TOOL_WORDS[tool]} · {DOC_TITLES[kind].lower()}")}; font: 2.6mm {font}; color: {TEXT_GRAY}; }}
    @bottom-left {{ content: {_css_string(key_line)}; font: 2.3mm {font}; color: {TEXT_GRAY}; }}
    @bottom-right {{ content: "Page " counter(page) " of " counter(pages); font: 2.6mm {font}; color: {TEXT_GRAY}; }}
  }}
  html, body {{ margin: 0; padding: 0; font-family: {font}; color: #111; }}
  .page {{
    width: {page_w}; height: {page_h}; box-sizing: border-box;
    overflow: hidden; position: relative; break-after: page;
  }}
  .page.cover {{ page: cover; display: flex; flex-direction: column; }}
  .cover .band {{ height: 9mm; background: {ACCENT}; }}
  .cover .cover-body {{ flex: 1; display: flex; flex-direction: column; justify-content: center; padding: 0 26mm 20mm; }}
  .cover .eyebrow {{
    font-size: 4mm; font-weight: bold; letter-spacing: 0.5mm; text-transform: uppercase;
    color: {TEXT_GRAY}; margin: 0 0 3mm;
  }}
  .cover h1 {{ font-size: 11mm; line-height: 1.1; margin: 0; }}
  .cover .rule {{ width: 32mm; height: 1.2mm; background: {ACCENT}; margin: 8mm 0 7mm; }}
  .cover .subtitle {{ font-size: 4.2mm; line-height: 1.45; margin: 0; }}
  .cover .version {{
    font-size: 3.2mm; color: {TEXT_GRAY}; margin: 0 26mm 20mm; padding-top: 3mm;
    border-top: 0.25mm solid {RULE_GRAY};
  }}
  .page.form {{ page: form; display: flex; align-items: center; justify-content: center; break-after: auto; }}
  .page.form svg {{ display: block; }}
  .front {{ page: front; }}
  .opener .key, .opener figure, .opener .captions {{ break-inside: avoid; }}
  .contents h1, .opener h2, .flow > h2, .prose h2 {{ font-size: 8mm; line-height: 1.15; margin: 0 0 6mm; }}
  .contents h1::after, .opener h2::after, .flow > h2::after, .prose h2::after {{
    content: ""; display: block; width: 22mm; height: 1mm; background: {ACCENT}; margin: 3mm 0 0;
  }}
  .flow > h2, .prose h2 {{ margin-top: 10mm; break-after: avoid; }}
  .flow > h2:first-child, .prose:first-child h2 {{ margin-top: 0; }}
  .contents h1 {{ margin-bottom: 5mm; }}
  .contents ol {{ list-style: none; margin: 0; padding: 0; }}
  .contents a {{ display: flex; align-items: baseline; color: inherit; text-decoration: none; }}
  .contents .t {{ flex: none; }}
  .contents .dots {{ flex: 1; min-width: 6mm; margin: 0 2mm; border-bottom: 0.3mm dotted #777; }}
  .contents .pg {{ flex: none; min-width: 7mm; text-align: right; }}
  .contents .toc > li {{ margin: 0 0 2.6mm; break-inside: avoid; }}
  .contents .toc > li > a {{ font-size: 4mm; font-weight: bold; }}
  .contents .toc ol {{ margin: 1mm 0 0 7mm; }}
  .contents .toc ol li {{ margin: 0 0 1mm; }}
  .contents .toc ol a {{ font-size: 3.2mm; }}
  .contents .dials {{ font-size: 2.5mm; line-height: 1.3; color: {TEXT_GRAY}; margin: 0.4mm 9mm 0 0; }}
  .prose, .intro, .prose p, .prose li {{ font-size: 3.4mm; line-height: 1.45; }}
  .prose p, .intro {{ margin: 0 0 3mm; }}
  .intro {{ margin-bottom: 5mm; }}
  .prose h3, .flow > h3 {{ font-size: 5.2mm; margin: 8mm 0 2.5mm; break-after: avoid; }}
  .prose ol, .prose ul {{ margin: 0 0 3.5mm; padding-left: 6mm; }}
  .prose li {{ margin: 0 0 1.5mm; }}
  .prose table {{ border-collapse: collapse; width: 100%; font-size: 3mm; line-height: 1.35; margin: 2mm 0 4mm; }}
  .prose th, .prose td {{ text-align: left; vertical-align: top; padding: 1.3mm 2.5mm; border-bottom: 0.25mm solid {RULE_GRAY}; }}
  .prose th {{ background: {ACCENT_TINT}; border-bottom: 0.4mm solid {ACCENT}; }}
  .prose tr {{ break-inside: avoid; }}
  .prose code {{ font-family: Consolas, Menlo, monospace; font-size: 0.92em; }}
  .prose pre {{ font-family: Consolas, Menlo, monospace; font-size: 2.7mm; line-height: 1.4; background: #f3f4f4; padding: 2.5mm 3.5mm; margin: 0 0 3.5mm; white-space: pre-wrap; }}
  .prose blockquote, .callout {{
    font-size: 3.3mm; line-height: 1.45; background: {ACCENT_TINT}; border-left: 1.2mm solid {ACCENT};
    padding: 2.5mm 4mm; margin: 3mm 0 5mm; break-inside: avoid;
  }}
  .prose blockquote p {{ margin: 0; }}
  .prose a {{ color: #0b4f8a; text-decoration: none; }}
  figure.photo {{ margin: 2mm 0 4mm; text-align: center; break-inside: avoid; }}
  figure.photo img {{ display: block; margin: 0 auto; max-width: 110mm; max-height: 70mm; }}
  figure.photo figcaption, .opener figcaption, .card figcaption {{
    font-size: 2.6mm; line-height: 1.35; color: {TEXT_GRAY}; text-align: left; margin: 2mm 0 0;
  }}
  .prose li figure.photo {{ margin: 2mm 0 3mm; }}
  .key {{ border: 0.3mm solid {BORDER_GRAY}; border-radius: 1.5mm; padding: 2.5mm 4mm 1mm; margin: 0 0 4mm; break-inside: avoid; }}
  .key .key-title {{ font-size: 3.4mm; font-weight: bold; margin: 0 0 1.5mm; }}
  .key ul {{ list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: 1fr 1fr; column-gap: 6mm; }}
  .key li {{ display: flex; align-items: center; font-size: 3.1mm; line-height: 1.3; margin: 0 0 1.5mm; }}
  .key li svg {{ flex: none; margin-right: 2.5mm; }}
  .opener figure {{ margin: 0; text-align: center; break-inside: avoid; }}
  .opener figure svg, .card figure svg {{ display: inline-block; }}
  .opener .captions {{ font-size: 3.1mm; margin: 3mm 0 3mm; padding-left: 5mm; }}
  .flow {{ page: flow; }}
  .keep {{ break-inside: avoid; }}
  .keep .card {{ border-top: 0; }}
  .step-intro {{ font-size: 3.4mm; line-height: 1.45; margin: 0 0 1mm; break-after: avoid; }}
  .card {{ break-inside: avoid; padding: 5mm 0 3mm; border-top: 0.25mm solid {RULE_GRAY}; }}
  h2 + .card, .step-intro + .card {{ border-top: 0; padding-top: 2mm; }}
  .card.tall {{ break-before: page; }}
  .card h3 {{ font-size: 4.8mm; margin: 0; }}
  .cname {{ font-size: 2.8mm; color: {TEXT_GRAY}; margin: 1mm 0 2.5mm; }}
  .cname b {{ color: #111; }}
  .card .lead {{ font-size: 3.5mm; line-height: 1.45; margin: 0 0 3.5mm; }}
  .card figure {{ margin: 0 0 3mm; text-align: center; }}
  .nopic {{
    font-size: 3.1mm; line-height: 1.4; background: #f3f4f4; border-left: 1.2mm solid {BORDER_GRAY};
    padding: 2.2mm 3.5mm; margin: 0 0 3mm;
  }}
  .facts {{ border-collapse: collapse; width: 100%; font-size: 3mm; line-height: 1.35; margin: 0 0 2.5mm; background: #f6f7f7; }}
  .facts th, .facts td {{ text-align: left; vertical-align: top; padding: 1.3mm 3mm; border-bottom: 0.3mm solid #fff; }}
  .facts th {{ width: 26mm; font-weight: bold; color: #333; }}
  .facts .tags {{ list-style: none; margin: 0; padding: 0; }}
  .facts .tags li {{
    display: inline-block; font-size: 2.5mm; letter-spacing: 0.1mm; background: #fff;
    border: 0.25mm solid {COLOR_TRACE}; border-radius: 0.8mm; padding: 0.3mm 1.5mm; margin: 0.3mm 1.5mm 0.6mm 0;
  }}
  .note {{
    font-size: 3.1mm; line-height: 1.4; background: {ACCENT_TINT}; border-left: 1.2mm solid {ACCENT};
    padding: 2mm 3.5mm; margin: 0 0 1mm;
  }}
  .measure {{ break-inside: avoid; padding: 4mm 0 1mm; border-top: 0.25mm solid {RULE_GRAY}; }}
  .measure h3 {{ font-size: 4.8mm; margin: 0; padding: 0; border: 0; }}
  .measure .cname {{ display: flex; justify-content: space-between; align-items: baseline; }}
  .measure .formrow {{ font-size: 2.7mm; color: #111; border: 0.3mm solid {ACCENT}; border-radius: 3mm; padding: 0.4mm 2.5mm; }}
</style></head>
<body>{chr(10).join(body)}</body></html>
"""


def build_html(rows: Sequence[Dict[str, Any]], mappings: Dict[str, Dict[str, Dict[str, Any]]],
               index: Sequence[Dict[str, Any]], svgs: Dict[Tuple[str, str], str], tool: str, kind: str,
               storyboards=None, storyboard_svg: Optional[str] = None, form_svg: Optional[str] = None,
               stencil_svgs: Optional[Sequence[str]] = None, form_section: Optional[str] = None,
               pages: Optional[Dict[str, int]] = None) -> str:
    """One document of a tool as HTML for the print (the storyboard, the
    form sheet, the stencil sheets and the form's text are read from the
    tree unless given). ``pages`` maps each contents anchor to its page in
    the last print; without it the contents shows "00"."""
    if storyboards is None:
        storyboards = load_storyboards()
    if storyboard_svg is None:
        storyboard_svg = (DIALS_DIR / tool / "storyboard.svg").read_text(encoding="utf-8")
    if form_svg is None:
        form_svg = (PACKET_DIRS[tool] / "measuring-form.svg").read_text(encoding="utf-8")
    if stencil_svgs is None:
        stencil_svgs = [(PROJECT_ROOT / "docs" / "guides" / name).read_text(encoding="utf-8")
                        for name in STENCIL_SHEETS[tool]]
    if form_section is None:
        form_section = measuring_form_section(tool)
    return document_html(kind, tool, rows, mappings, index, svgs, storyboards, storyboard_svg, form_svg,
                         stencil_svgs, form_section, pages)

# ---------------------------------------------------------------------------
# PDF checks beyond the sheets' (standard library only)
# ---------------------------------------------------------------------------

_OBJ = re.compile(rb"\d+\s+\d+\s+obj(.*?)endobj", re.S)


def outline_titles(pdf: Path) -> List[str]:
    """The titles of the PDF's outline items (objects carrying /Title and
    /Parent); UTF-16BE hex strings decoded."""
    data = pdf.read_bytes()
    titles: List[str] = []
    for m in _OBJ.finditer(data):
        body = m.group(1)
        if b"/Title" not in body or b"/Parent" not in body:
            continue
        t = re.search(rb"/Title\s*(<([0-9A-Fa-f\s]+)>|\(((?:\\.|[^\\)])*)\))", body)
        if not t:
            continue
        if t.group(2) is not None:
            raw = bytes.fromhex(re.sub(rb"\s", b"", t.group(2)).decode("ascii"))
            titles.append(raw.decode("utf-16-be") if raw.startswith(b"\xfe\xff") else raw.decode("latin-1"))
        else:
            titles.append(t.group(3).decode("latin-1"))
    return titles


def link_count(pdf: Path) -> int:
    return len(re.findall(rb"/Subtype\s*/Link", pdf.read_bytes()))


def pdf_page_count(pdf: Path) -> int:
    data = pdf.read_bytes()
    return data.count(b"/Type /Page") - data.count(b"/Type /Pages")


_OBJ_NUMBERED = re.compile(rb"(\d+)\s+\d+\s+obj(.*?)endobj", re.S)
_REF = rb"(\d+)\s+\d+\s+R"


def dest_pages(pdf: Path) -> Dict[str, int]:
    """Every named destination of the PDF (an ``id`` that a link points at)
    with the page it lands on, counted from 1 in the page tree's order."""
    objs = {int(m.group(1)): m.group(2) for m in _OBJ_NUMBERED.finditer(pdf.read_bytes())}
    catalogs = [body for body in objs.values() if re.search(rb"/Type\s*/Catalog\b", body)]
    if len(catalogs) != 1:
        raise AssertionError(f"{pdf.name}: expected one catalog, found {len(catalogs)}")
    order: List[int] = []

    def walk(num: int) -> None:
        body = objs[num]
        if re.search(rb"/Type\s*/Pages\b", body):
            kids = re.search(rb"/Kids\s*\[([^\]]*)\]", body)
            if not kids:
                raise AssertionError(f"{pdf.name}: page tree node {num} has no /Kids")
            for kid in re.findall(_REF, kids.group(1)):
                walk(int(kid))
        else:
            order.append(num)

    root = re.search(rb"/Pages\s+" + _REF, catalogs[0])
    dests = re.search(rb"/Dests\s+" + _REF, catalogs[0])
    if not root or not dests:
        raise AssertionError(f"{pdf.name}: the catalog names no page tree or no named destinations")
    walk(int(root.group(1)))
    page_no = {num: i + 1 for i, num in enumerate(order)}
    return {name.decode("latin-1"): page_no[int(ref)]
            for name, ref in re.findall(rb"/([^\s/\[\]<>()]+)\s*\[\s*" + _REF, objs[int(dests.group(1))])}


def contents_anchors(html_text: str) -> List[str]:
    return re.findall(r'<a href="#([^"]+)">', html_text)


def verify_document_pdf(pdf: Path, cards: Sequence[Dict[str, Any]], html_text: str,
                        pages: Optional[Dict[str, int]] = None, prose_pages: int = 30) -> Dict[str, int]:
    """The document's PDF: every page US Letter; the page count between a
    third of the cards plus the fixed pages and every card on its own page
    plus the prose; one outline entry per heading the HTML carries (h1 to
    h4), every dial's title among them; a link annotation for every
    contents entry; and, given ``pages``, every contents page number equal
    to the page its anchor landed on."""
    n_pages = pdf_page_count(pdf)
    verify_pdf(pdf, n_pages, page_w_mm=LETTER_W_MM, page_h_mm=LETTER_H_MM)
    fixed = 5  # the cover, the contents, the opener, the form, a stencil sheet
    lo, hi = math.ceil(len(cards) / 3) + fixed, len(cards) + fixed + prose_pages
    if not lo <= n_pages <= hi:
        raise AssertionError(f"{n_pages} pages, expected between {lo} and {hi}")
    want = len(re.findall(r"<h[1-4][ >]", html_text))
    titles = outline_titles(pdf)
    if len(titles) != want:
        raise AssertionError(f"Expected {want} outline entries (the HTML's h1 to h4), found {len(titles)}")
    missing = {r["title"] for r in cards} - set(titles)
    if missing:
        raise AssertionError(f"{len(missing)} dial titles missing from the outline, e.g. {sorted(missing)[:3]}")
    anchors = contents_anchors(html_text)
    links = link_count(pdf)
    if links < len(anchors):
        raise AssertionError(f"Expected at least {len(anchors)} link annotations, found {links}")
    if pages is not None:
        found = dest_pages(pdf)
        wrong = {a: (pages.get(a), found.get(a)) for a in anchors if pages.get(a) != found.get(a)}
        if wrong:
            raise AssertionError(f"Contents page numbers (printed, actual) that do not match: {wrong}")
    logger.info("Verified: %d pages, %d outline entries, %d link annotations.", n_pages, len(titles), links)
    return {"pages": n_pages, "outline": len(titles), "links": links, "cards": len(cards)}


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def print_document(kind: str, tool: str, rows, mappings, index, svgs, storyboards, form_section: str,
                   out_pdf: Path, keep_html: bool = False) -> Dict[str, int]:
    """Print one document: twice at least, until the contents' page numbers
    settle, then verify it."""
    SCRATCH.mkdir(parents=True, exist_ok=True)
    html_path = SCRATCH / f"{tool}_{kind}.html"
    pages: Optional[Dict[str, int]] = None
    for prints in range(1, 4):
        html_text = build_html(rows, mappings, index, svgs, tool=tool, kind=kind, storyboards=storyboards,
                               form_section=form_section, pages=pages)
        html_path.write_text(html_text, encoding="utf-8")
        print_to_pdf(html_path.resolve(), out_pdf, outline=True, user_data_dir=EDGE_PROFILE)
        landed = dest_pages(out_pdf)
        anchors = contents_anchors(html_text)
        unplaced = [a for a in anchors if a not in landed]
        if unplaced:
            raise AssertionError(f"The PDF has no destination for the contents links {unplaced}")
        found = {a: landed[a] for a in anchors}
        if found == pages:
            break
        pages = found
    else:
        raise AssertionError("The contents page numbers still moved after three prints")
    if not keep_html:
        html_path.unlink()
    of_file = [r for r in rows if r["file"] == tool]
    cards = [r for r in of_file if r.get("quick_start")] if kind == "quick-start" else of_file
    counts = verify_document_pdf(out_pdf, cards, html_text, pages)
    counts["prints"] = prints
    return counts


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tool", choices=sorted(PACKET_DIRS), required=True,
                        help="the tool whose documents to build: the pages under docs/guides/<tool>/ and the PDFs")
    parser.add_argument("--document", choices=DOCUMENTS + ("all",), default="all",
                        help="the quick start, the full guide, or both (default)")
    parser.add_argument("--out", type=Path, default=None,
                        help="the PDF path, for one document (default: the document's PDF under docs/)")
    parser.add_argument("--markdown-only", action="store_true", help="write the pages only (no browser)")
    parser.add_argument("--keep-html", action="store_true", help="keep the HTML under tmp_renders/dial_reference/")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(message)s")
    kinds = DOCUMENTS if args.document == "all" else (args.document,)
    if args.out and len(kinds) != 1:
        parser.error("--out needs --document quick-start or --document full-guide")

    rows = load_catalog()
    mappings = load_mappings()
    index = load_index()
    storyboards = load_storyboards()
    form_section = measuring_form_section(args.tool)
    out_dir = PACKET_DIRS[args.tool]
    out_dir.mkdir(parents=True, exist_ok=True)
    for kind in kinds:
        text = build_markdown(rows, mappings, index, tool=args.tool, kind=kind, storyboards=storyboards,
                              form_section=form_section)
        (out_dir / f"{kind}.md").write_text(text, encoding="utf-8", newline="\n")
        logger.info("Wrote %s (%d lines)", out_dir / f"{kind}.md", text.count("\n"))
    if args.markdown_only:
        return 0
    svgs = load_svgs([r for r in rows if r["file"] == args.tool])
    for kind in kinds:
        out_pdf = args.out or (PROJECT_ROOT / DOC_PDFS[(args.tool, kind)])
        started = time.perf_counter()
        counts = print_document(kind, args.tool, rows, mappings, index, svgs, storyboards, form_section,
                                out_pdf, keep_html=args.keep_html)
        logger.info("Wrote %s (%.1f KB, %d pages, %d outline entries, %d links, %d cards; %d prints in %.1f s)",
                    out_pdf, out_pdf.stat().st_size / 1024, counts["pages"], counts["outline"], counts["links"],
                    counts["cards"], counts["prints"], time.perf_counter() - started)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
