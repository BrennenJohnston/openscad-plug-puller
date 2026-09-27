#!/usr/bin/env python3
"""Build the dial reference: one page per Customizer dial of both pullers.

Reads ``dial_catalog.json``, the two parameter mappings and the diagram
index (``docs/dials/dial_diagrams_index.json``) and writes, from the same
data:

* ``docs/guides/dial-reference.md``: the Markdown twin (H1, H2 per file,
  H3 per Customizer section, H4 per dial with its diagram, its sentence,
  the mapping's default / range / step / unit, its caution note, the
  features its trace moves and the warning tags it can trip);
* ``docs/Plug_Puller_Dial_Reference.pdf``: a title page, a contents page
  with a link per dial, then one page per dial, printed with headless
  Edge/Chrome through the outline-sheets pipeline (210 x 279 mm pages,
  the browser's document outline as bookmarks).

The date is never printed, so the PDF is reproducible. The SVGs are inlined
into the HTML, which keeps each diagram's <title>/<desc> text equivalent in
the page.

The per-tool guide packets (R3): ``--tool one-sided`` or ``--tool two-sided``
writes that tool's Markdown twins under ``docs/guides/<tool>/`` from the same
data plus the storyboard index and the catalog's ``measure`` rows: the quick
start (the opener, the storyboard, the four steps' dials), the dial guide
(every dial of the file) and the measuring guide (one section per measured
dial, in the measuring form's order). ``--part`` picks one of them.

Usage:
    python scripts/build_dial_reference.py                 # both files
    python scripts/build_dial_reference.py --markdown-only # no browser needed
    python scripts/build_dial_reference.py --tool one-sided --markdown-only

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import argparse
import html
import json
import logging
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.build_outline_sheets_pdf import (  # noqa: E402
    PAGE_H_MM,
    PAGE_W_MM,
    print_to_pdf,
    verify_pdf,
)
from scripts.generate_dial_diagrams import LEGEND_LINE  # noqa: E402
from scripts.generate_outline_sheets import MODEL_VERSION  # noqa: E402

logger = logging.getLogger(__name__)

CATALOG = PROJECT_ROOT / "dial_catalog.json"
MAPPINGS = {
    "one-sided": PROJECT_ROOT / "parameter_mapping.json",
    "two-sided": PROJECT_ROOT / "parameter_mapping_two_sided.json",
}
DIALS_DIR = PROJECT_ROOT / "docs" / "dials"
INDEX = DIALS_DIR / "dial_diagrams_index.json"
STORYBOARDS = DIALS_DIR / "storyboards_index.json"
OUT_PDF = PROJECT_ROOT / "docs" / "Plug_Puller_Dial_Reference.pdf"
OUT_MD = PROJECT_ROOT / "docs" / "guides" / "dial-reference.md"
SCRATCH = PROJECT_ROOT / "tmp_renders" / "dial_reference"
EDGE_PROFILE = PROJECT_ROOT / "tmp_renders" / "edge_profile"

FILE_LABELS = {"one-sided": "One-sided puller", "two-sided": "Two-sided puller"}
FILE_ORDER = ("one-sided", "two-sided")
TITLE = "Plug Puller Dial Reference"
DESCRIPTION = (
    "Every dial of the one-sided puller and the two-sided puller on its own page: "
    "what it moves, in a picture and a sentence, with the numbers the Customizer allows."
)
CONTENTS_HEADING = "Contents"
LEGEND = "black = the tool at its defaults; teal = the plug you measured; red dashed = what this dial moves"
NO_SHAPE = "This dial changes no shape."
MOVES_LABEL = "Moves"
TRIPS_LABEL = "Can trip"

# The quick-start cut: the Steps 1-4 dials only, with an opener page.
QUICK_TITLE = "Plug Puller Dial Quick Start"
QUICK_DESCRIPTION = (
    "The dials of the four Customizer steps of both pullers, one per page: which file to open, "
    "then what each step's dial moves."
)
QUICK_OUT_PDF = PROJECT_ROOT / "docs" / "Plug_Puller_Dial_Quick_Start.pdf"
QUICK_OUT_MD = PROJECT_ROOT / "docs" / "guides" / "dial-quick-start.md"
OPENER_HEADING = "Which file to open"
OPENER = (
    "Measure your plug's thickness. Up to 24 mm: open the one-sided puller, "
    "src/Plug_Puller_Parametric.scad. Thicker than 24 mm, or a plug you want held from both "
    "sides such as a USB-C tip or a round extension-cord plug: open the two-sided puller, "
    "src/Plug_Puller_Two_Sided.scad.",
    "Each file has four steps at the top of its Customizer: your plug, your size, the "
    "attachment, and one last choice (the hook hand in the one-sided file; the print layout "
    "in the two-sided file). The dials on the next pages are those steps and nothing else.",
)
RED_TEXT = (
    "If red text appears beside the part in the preview, read it: it names the measurement "
    "to fix, and the part will not fit until it is gone."
)

# The per-tool guide packets (R3, FD-44): one folder of Markdown twins per
# tool, the prose blocks below as their own strings rows.
TOOL_WORDS = {"one-sided": "one-sided puller", "two-sided": "two-sided puller"}
PACKET_DIRS = {
    "one-sided": PROJECT_ROOT / "docs" / "guides" / "one-sided",
    "two-sided": PROJECT_ROOT / "docs" / "guides" / "two-sided",
}
PACKET_PARTS = ("quick-start", "dial-guide", "measuring-guide")
PART_TITLES = {"quick-start": "Quick start", "dial-guide": "Dial guide", "measuring-guide": "Measuring guide"}
PACKET_TITLES = {"one-sided": "Plug Puller: the one-sided puller", "two-sided": "Plug Puller: the two-sided puller"}
PACKET_PDFS = {"one-sided": "docs/Plug_Puller_One_Sided_Guide.pdf", "two-sided": "docs/Plug_Puller_Two_Sided_Guide.pdf"}
PACKET_OPENER_HEADING = "Which tool this is"
PACKET_OPENERS = {
    "one-sided": (
        "This packet is for the one-sided puller, src/Plug_Puller_Parametric.scad: the tool for a wall plug up to "
        "24 mm thick, a pocket around the plug's back and sides with two finger holes below it, pulled with one "
        "hand. Measure your plug's thickness first. Thicker than 24 mm, or a plug you want held from both sides "
        "such as a USB-C tip or a round extension-cord plug, is the two-sided puller's job, and that tool has its "
        "own packet.",
        "The Customizer's four steps are your plug, your size, the attachment and the hook's side. The quick "
        "start below shows each step's dials, the dial guide every dial of the file, the measuring guide how to "
        "take each number, and the measuring form is the sheet you fill in first.",
    ),
    "two-sided": (
        "This packet is for the two-sided puller, src/Plug_Puller_Two_Sided.scad: two serrated plates that "
        "zip-tie around the plug and close across it, for a plug 24 mm thick or more and for a plug held from "
        "both sides, a USB-C tip or a round extension-cord plug. A thinner wall plug is the one-sided puller's "
        "job, and that tool has its own packet.",
        "The Customizer's four steps are your plug, your size, the attachment and the print layout. The quick "
        "start below shows each step's dials, the dial guide every dial of the file, the measuring guide how to "
        "take each number, and the measuring form is the sheet you fill in first.",
    ),
}
STEP_CAPTIONS = {
    "one-sided": ("Step 1: type your plug's numbers", "Step 2: pick your hand size",
                  "Step 3: pick how it attaches", "Step 4: pick the hook's side"),
    "two-sided": ("Step 1: type your plug's numbers and pick Rounded sides or Flat sides", "Step 2: pick your hand size",
                  "Step 3: pick how it attaches; a plug this short gets no strap slot", "Step 4: both plates in one file"),
}
MEASURING_INTRO = (
    "Everything here is in mm: a US plug is about 25 mm wide, so a 1 on your paper means you measured in inches. "
    "You need a caliper or a ruler with mm marks, the plug in its outlet, and your own hand only if you pick "
    "Measure my hand. Print the measuring form at 100 % and fill it in as you go: the sections below are the "
    "form's rows, in the same order, and the card names (R1, C1, F1 / F2) are the cards of the printed "
    "[measuring stencil](../print-preview-outlines.md)."
)
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

# The title page and the contents pages. Measured on the first print of the
# 118-row catalog (the contents flow over two pages in two columns); the verify
# step asserts the total. The quick-start cut: the opener page (its title page)
# and one contents page for 28 dials.
FRONT_MATTER_PAGES = 3
QUICK_FRONT_MATTER_PAGES = 2
FIGURE_W_MM = 170.0
FIGURE_MAX_H_MM = 140.0
FIGURE_MAX_SCALE = 2.0  # a cropped detail is drawn at most twice its 1:1 size

# Which warning tags name a dial in docs/guides/fit-troubleshooting.md (its
# "What to do" column, where the dial is written in backticks). Kept by hand
# from that guide, read on 2026-09-26; a dial without an entry shows no
# "Can trip" line.
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


def grouped(rows: Sequence[Dict[str, Any]], mappings: Dict[str, Dict[str, Dict[str, Any]]]):
    """Yield (file_key, [(section, [rows])]) in Customizer order."""
    for file_key in FILE_ORDER:
        file_rows = [r for r in rows if r["file"] == file_key]
        if not file_rows:
            continue
        groups = []
        for section in sections_in_order(file_rows, mappings.get(file_key, {})):
            in_section = [r for r in file_rows if r["section"] == section]
            if in_section:
                groups.append((section, in_section))
        yield file_key, groups


def fmt(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def mapping_cells(mrow: Optional[Dict[str, Any]]) -> Tuple[str, str, str, str]:
    """Default, range, step, unit; an em dash where a field does not apply.
    A dropdown's range cell counts its options (the doc standard keeps
    table cells short); ``options_text()`` lists them in prose."""
    if not mrow:
        return ("—", "—", "—", "—")
    default = fmt(mrow.get("default"))
    if mrow.get("type") == "enum":
        rng = f"{len(mrow.get('values', []))} options"
    elif mrow.get("type") == "boolean":
        rng = "true / false"
    elif mrow.get("range"):
        lo, hi = mrow["range"]
        rng = f"{fmt(lo)} to {fmt(hi)}"
    else:
        rng = "—"
    step = fmt(mrow["step"]) if mrow.get("step") is not None else "—"
    unit = mrow.get("unit") or "—"
    return (default, rng, step, unit)


def options_text(mrow: Optional[Dict[str, Any]]) -> str:
    """The options of a dropdown as a sentence; empty for other dials."""
    if mrow and mrow.get("type") == "enum":
        return "Options: " + ", ".join(mrow.get("values", [])) + "."
    return ""


def context_text(row: Dict[str, Any], code: bool = True) -> str:
    ctx = row["diagram"].get("context") or {}
    if not ctx:
        return ""
    wrap = (lambda k: f"`{k}`") if code else (lambda k: k)
    return "Context: " + ", ".join(f"{wrap(k)} = {fmt(v)}" for k, v in ctx.items()) + "."


def values_text(row: Dict[str, Any], code: bool = True) -> str:
    d = row["diagram"]
    if d["view"] == "none":
        return f"{NO_SHAPE} {row.get('note') or ''}".strip()
    parts = [f"Before: {fmt(d['before'])}. After: {fmt(d['after'])}."]
    ctx = context_text(row, code)
    if ctx:
        parts.append(ctx)
    if d["view"] in ("section-x", "section-y"):
        axis = "x" if d["view"] == "section-x" else "y"
        parts.append(f"Section at {axis} = {fmt(d.get('at') or 0)} mm.")
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Markdown twin
# ---------------------------------------------------------------------------


def quick_rows(rows: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [r for r in rows if r.get("quick_start")]


def numbers_line(mrow: Optional[Dict[str, Any]]) -> str:
    """The mapping's numbers as one line of prose, never a table cell (and
    never "Step 0.5": the docs gate reads "step 0" as the retired section
    name)."""
    default, rng, step, unit = mapping_cells(mrow)
    if mrow and mrow.get("type") in ("enum", "boolean"):
        return f"Default {default} · {rng}"
    return f"Default {default} · Range {rng} · Step size {step} · Unit {unit}"


def dial_card(row: Dict[str, Any], mrow: Optional[Dict[str, Any]], entry: Dict[str, Any],
              rel: str = "../../dials") -> List[str]:
    """One dial's card in Markdown: H3 name, the title, the picture with the
    index's alt text and its long description right under it, the changes
    sentence, the numbers line, the options, the values and context line,
    the note, Moves and Can trip."""
    alt = entry.get("alt") or row["changes"]
    lines = [f"### `{row['name']}`", "", row["title"], "",
             f"![{alt}]({rel}/{row['file']}/{row['name']}.svg)", ""]
    long = entry.get("long_description") or ""
    if long:
        lines += [long, ""]
    if row["changes"] not in long:
        lines += [row["changes"], ""]
    lines += [numbers_line(mrow), ""]
    if options_text(mrow):
        lines += [options_text(mrow), ""]
    if row["diagram"]["view"] != "none":
        lines += [values_text(row), ""]
        if row.get("note"):
            lines += [row["note"], ""]
    elif not entry.get("long_description") and row.get("note"):
        lines += [values_text(row), ""]
    features = entry.get("features") or []
    if features and features != ["none"]:
        lines += [f"{MOVES_LABEL}: {', '.join(features)}.", ""]
    tags = TAGS_BY_DIAL.get((row["file"], row["name"]))
    if tags:
        lines += [f"{TRIPS_LABEL}: " + "; ".join(f"`{t}`" for t in tags) + ".", ""]
    return lines


def _sections(rows_of_file: Sequence[Dict[str, Any]], mapping: Dict[str, Dict[str, Any]]):
    for section in sections_in_order(rows_of_file, mapping):
        in_section = [r for r in rows_of_file if r["section"] == section]
        if in_section:
            yield section, in_section


def _packet_head(tool: str, part: str, blurb: str) -> List[str]:
    return [f"# {PART_TITLES[part]}, {TOOL_WORDS[tool]}", "", blurb, "",
            f"Model version {MODEL_VERSION}. The printable packet is `{PACKET_PDFS[tool]}`; its parts are "
            "[the quick start](quick-start.md), [the dial guide](dial-guide.md), [the measuring guide](measuring-guide.md) "
            "and [the measuring form](measuring-form.md). The dial names are written exactly as the Customizer shows them.", ""]


def quick_start_markdown(rows, mappings, index, storyboards, tool: str) -> str:
    idx = {(e["file"], e["name"]): e for e in index}
    mapping = mappings.get(tool, {})
    quick = [r for r in rows if r["file"] == tool and r.get("quick_start")]
    lines = _packet_head(tool, "quick-start",
                         f"The four Customizer steps of the {TOOL_WORDS[tool]}, dial by dial: what each dial moves, "
                         "in a picture and a sentence, with the numbers the Customizer allows.")
    lines += [f"## {PACKET_OPENER_HEADING}", "", PACKET_OPENERS[tool][0], "", PACKET_OPENERS[tool][1], "",
              RED_TEXT, "", f"In every picture: {LEGEND_LINE}.", ""]
    board = storyboards.get(tool)
    if board:
        lines += [f"![{board['alt']}](../../dials/{tool}/storyboard.svg)", "", board["long_description"], ""]
        lines += [f"- {caption}" for caption in STEP_CAPTIONS[tool]] + [""]
    for section, in_section in _sections(quick, mapping):
        lines += [f"## {section}", ""]
        for row in in_section:
            lines += dial_card(row, mapping.get(row["name"]), idx.get((tool, row["name"]), {}))
    return "\n".join(lines).rstrip("\n") + "\n"


def dial_guide_markdown(rows, mappings, index, tool: str) -> str:
    idx = {(e["file"], e["name"]): e for e in index}
    mapping = mappings.get(tool, {})
    of_file = [r for r in rows if r["file"] == tool]
    lines = _packet_head(tool, "dial-guide",
                         f"Every dial of the {TOOL_WORDS[tool]} in the Customizer's order: what it moves, in a picture "
                         "and a sentence, with the numbers the Customizer allows.")
    lines += [f"In every picture: {LEGEND_LINE}.", ""]
    for section, in_section in _sections(of_file, mapping):
        lines += [f"## {section}", ""]
        for row in in_section:
            lines += dial_card(row, mapping.get(row["name"]), idx.get((tool, row["name"]), {}))
    return "\n".join(lines).rstrip("\n") + "\n"


def measuring_guide_markdown(rows, mappings, tool: str) -> str:
    mapping = mappings.get(tool, {})
    step_names = [name for name, mrow in mapping.items() if mrow["section"].startswith("Step")]
    measured = [r for r in rows if r["file"] == tool and r.get("measure")]
    lines = _packet_head(tool, "measuring-guide",
                         f"How to take each number the {TOOL_WORDS[tool]} asks for, in the measuring form's order, "
                         "with the typical range and an example.")
    lines += [MEASURING_INTRO, ""]
    if tool == "two-sided":
        lines += [TWO_SIDED_WIDTHS, ""]
    for row in measured:
        m = row["measure"]
        k = step_names.index(row["name"]) + 1 if row["name"] in step_names else None
        where = f"row {k} of the form" if k else "not on the form"
        lines += [f"## {k}. {row['title']}" if k else f"## {row['title']}", "",
                  f"Customizer name `{row['name']}`, {where}.", "", m["how"], ""]
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
    lines += [SANITY_CHECK, "", FOR_SOMEONE_ELSE, "",
              "Print the form and fill it in as you measure: [the measuring form](measuring-form.md)."]
    return "\n".join(lines) + "\n"


def build_markdown(rows: Sequence[Dict[str, Any]], mappings: Dict[str, Dict[str, Dict[str, Any]]],
                   index: Sequence[Dict[str, Any]], quick: bool = False, tool: Optional[str] = None,
                   part: Optional[str] = None, storyboards: Optional[Dict[str, Dict[str, Any]]] = None) -> str:
    """The combined twins (no ``tool``: the dial reference, or the quick-start
    cut with ``quick``), or one part of a tool's packet."""
    if tool is not None:
        if part == "quick-start":
            return quick_start_markdown(rows, mappings, index, storyboards or {}, tool)
        if part == "dial-guide":
            return dial_guide_markdown(rows, mappings, index, tool)
        if part == "measuring-guide":
            return measuring_guide_markdown(rows, mappings, tool)
        raise ValueError(f"unknown packet part {part!r}")
    idx = {(e["file"], e["name"]): e for e in index}
    if quick:
        rows = quick_rows(rows)
        lines = [
            f"# {QUICK_TITLE}", "",
            QUICK_DESCRIPTION, "",
            f"Model version {MODEL_VERSION}. The printable twin is `docs/Plug_Puller_Dial_Quick_Start.pdf`; "
            "every dial of both files is in `docs/guides/dial-reference.md`. The dial names are written "
            "exactly as the Customizer shows them.", "",
            f"## {OPENER_HEADING}", "",
            OPENER[0], "",
            OPENER[1], "",
            RED_TEXT, "",
            f"In every picture: {LEGEND}.", "",
        ]
    else:
        lines = [
            f"# {TITLE}", "",
            DESCRIPTION, "",
            f"Model version {MODEL_VERSION}. The printable twin is `docs/Plug_Puller_Dial_Reference.pdf` "
            "(one dial per page, with bookmarks and a linked contents page). The dial names are written "
            "exactly as the Customizer shows them.", "",
            f"In every picture: {LEGEND}.", "",
        ]
    for file_key, groups in grouped(rows, mappings):
        lines += [f"## {FILE_LABELS[file_key]}", ""]
        for section, in_section in groups:
            lines += [f"### {section}", ""]
            for row in in_section:
                entry = idx.get((row["file"], row["name"]), {})
                mrow = mappings.get(file_key, {}).get(row["name"])
                default, rng, step, unit = mapping_cells(mrow)
                lines += [
                    f"#### `{row['name']}`", "",
                    row["title"], "",
                    f"![{row['changes']}](../dials/{row['file']}/{row['name']}.svg)", "",
                    row["changes"], "",
                    "| Default | Range | Step | Unit |",
                    "|---|---|---|---|",
                    f"| {default} | {rng} | {step} | {unit} |", "",
                ]
                if options_text(mrow):
                    lines += [options_text(mrow), ""]
                lines += [values_text(row), ""]
                if row["diagram"]["view"] != "none" and row.get("note"):
                    lines += [row["note"], ""]
                features = entry.get("features") or []
                if features and features != ["none"]:
                    lines += [f"{MOVES_LABEL}: {', '.join(features)}.", ""]
                tags = TAGS_BY_DIAL.get((row["file"], row["name"]))
                if tags:
                    lines += [f"{TRIPS_LABEL}: " + "; ".join(f"`{t}`" for t in tags) + ".", ""]
    return "\n".join(lines).rstrip("\n") + "\n"


# ---------------------------------------------------------------------------
# HTML for the PDF
# ---------------------------------------------------------------------------

_SVG_ROOT = re.compile(r"<svg\b[^>]*>", re.S)
_VIEWBOX = re.compile(r'viewBox="([^"]+)"')


def _esc(text: Any) -> str:
    return html.escape(str(text), quote=False)


def figure_svg(svg_text: str) -> str:
    """The SVG element sized for the page: 170 mm wide, or less when its
    height would pass 140 mm or the scale would pass 2:1; the XML
    declaration dropped."""
    text = re.sub(r"<\?xml[^>]*\?>\s*", "", svg_text)
    m = _SVG_ROOT.search(text)
    if not m:
        raise ValueError("no <svg> root in the diagram")
    root = m.group(0)
    vb = _VIEWBOX.search(root)
    if not vb:
        raise ValueError("the diagram has no viewBox")
    _x, _y, w, h = (float(v) for v in vb.group(1).split())
    scale = min(FIGURE_W_MM / w, FIGURE_MAX_H_MM / h, FIGURE_MAX_SCALE)
    width, height = w * scale, h * scale
    new_root = re.sub(r'\s(width|height)="[^"]*"', "", root)
    new_root = new_root[:-1] + f' width="{width:.2f}mm" height="{height:.2f}mm">'
    return text[:m.start()] + new_root + text[m.end():]


def dial_id(row: Dict[str, Any]) -> str:
    return f"{row['file']}-{row['name']}"


def title_page_html(quick: bool = False) -> str:
    if quick:
        return f"""
<section class="page front opener">
  <h1>{_esc(QUICK_TITLE)}</h1>
  <p class="subtitle">{_esc(QUICK_DESCRIPTION)}</p>
  <p class="version">Model version {_esc(MODEL_VERSION)}</p>
  <p class="opener-heading">{_esc(OPENER_HEADING)}</p>
  <p class="opener">{_esc(OPENER[0])}</p>
  <p class="opener">{_esc(OPENER[1])}</p>
  <p class="opener red">{_esc(RED_TEXT)}</p>
  <p class="legend">In every picture: {_esc(LEGEND)}.</p>
  <p class="hint">The dial names are written exactly as the Customizer shows them. Every dial of both files is in the full dial reference.</p>
</section>
"""
    return f"""
<section class="page front">
  <h1>{_esc(TITLE)}</h1>
  <p class="subtitle">{_esc(DESCRIPTION)}</p>
  <p class="version">Model version {_esc(MODEL_VERSION)}</p>
  <p class="legend">In every picture: {_esc(LEGEND)}.</p>
  <p class="hint">The dial names are written exactly as the Customizer shows them. Use the bookmarks or the contents page to jump to a dial.</p>
</section>
"""


def contents_html(rows: Sequence[Dict[str, Any]], mappings) -> str:
    parts = ['<section class="page front contents">', f"<h1>{_esc(CONTENTS_HEADING)}</h1>", '<div class="columns">']
    for file_key, groups in grouped(rows, mappings):
        parts.append(f'<p class="file">{_esc(FILE_LABELS[file_key])}</p>')
        for section, in_section in groups:
            parts.append(f'<p class="section">{_esc(section)}</p><ul>')
            for row in in_section:
                parts.append(f'<li><a href="#{dial_id(row)}">{_esc(row["name"])}</a>: {_esc(row["title"])}</li>')
            parts.append("</ul>")
    parts += ["</div>", "</section>"]
    return "\n".join(parts)


def dial_page_html(row: Dict[str, Any], mrow: Optional[Dict[str, Any]], entry: Dict[str, Any],
                   svg_text: str, first_of_file: bool) -> str:
    default, rng, step, unit = mapping_cells(mrow)
    parts = ['<section class="page dial">']
    if first_of_file:
        parts.append(f"<h2>{_esc(FILE_LABELS[row['file']])}</h2>")
    parts += [
        f'<h3 id="{dial_id(row)}">{_esc(row["name"])}</h3>',
        f'<p class="where">{_esc(FILE_LABELS[row["file"]])} · {_esc(row["section"])}</p>',
        f'<p class="title">{_esc(row["title"])}</p>',
        f'<div class="figure">{figure_svg(svg_text)}</div>',
        f'<p class="changes">{_esc(row["changes"])}</p>',
        "<table><tr><th>Default</th><th>Range</th><th>Step</th><th>Unit</th></tr>"
        f"<tr><td>{_esc(default)}</td><td>{_esc(rng)}</td><td>{_esc(step)}</td><td>{_esc(unit)}</td></tr></table>",
    ]
    if options_text(mrow):
        parts.append(f'<p class="options">{_esc(options_text(mrow))}</p>')
    parts.append(f'<p class="values">{_esc(values_text(row, code=False))}</p>')
    if row["diagram"]["view"] != "none" and row.get("note"):
        parts.append(f'<p class="note">{_esc(row["note"])}</p>')
    features = entry.get("features") or []
    if features and features != ["none"]:
        parts.append(f'<p class="moves">{_esc(MOVES_LABEL)}: {_esc(", ".join(features))}.</p>')
    tags = TAGS_BY_DIAL.get((row["file"], row["name"]))
    if tags:
        parts.append(f'<p class="trips">{_esc(TRIPS_LABEL)}: ' + "; ".join(f"<span class=\"tag\">{_esc(t)}</span>" for t in tags) + ".</p>")
    parts.append("</section>")
    return "\n".join(parts)


def build_html(rows: Sequence[Dict[str, Any]], mappings: Dict[str, Dict[str, Dict[str, Any]]],
               index: Sequence[Dict[str, Any]], svgs: Dict[Tuple[str, str], str],
               quick: bool = False) -> str:
    idx = {(e["file"], e["name"]): e for e in index}
    if quick:
        rows = quick_rows(rows)
    pages = [title_page_html(quick), contents_html(rows, mappings)]
    for file_key, groups in grouped(rows, mappings):
        first = True
        for _section, in_section in groups:
            for row in in_section:
                pages.append(dial_page_html(
                    row, mappings.get(file_key, {}).get(row["name"]), idx.get((row["file"], row["name"]), {}),
                    svgs[(row["file"], row["name"])], first))
                first = False
    body = "\n".join(pages)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>{_esc(QUICK_TITLE if quick else TITLE)}</title>
<style>
  @page {{ size: {PAGE_W_MM:g}mm {PAGE_H_MM:g}mm; margin: 0; }}
  html, body {{ margin: 0; padding: 0; font-family: Helvetica, Arial, sans-serif; color: black; }}
  .page {{
    width: {PAGE_W_MM:g}mm; height: {PAGE_H_MM:g}mm; box-sizing: border-box;
    padding: 18mm 20mm 16mm; overflow: hidden; page-break-after: always; position: relative;
  }}
  .page:last-child {{ page-break-after: auto; }}
  .front h1 {{ font-size: 7mm; text-align: center; margin: 30mm 0 6mm; }}
  .contents {{ height: auto; min-height: {PAGE_H_MM:g}mm; overflow: visible; }}
  .contents h1 {{ margin: 0 0 5mm; }}
  .front .subtitle {{ font-size: 3.6mm; text-align: center; margin: 0 10mm 6mm; }}
  .front .version {{ font-size: 3.2mm; text-align: center; margin: 0 0 12mm; color: #444; }}
  .front .legend {{ font-size: 3.2mm; text-align: center; margin: 0 8mm 4mm; }}
  .front .hint {{ font-size: 3mm; text-align: center; color: #444; margin: 0 8mm; }}
  .opener h1 {{ margin: 14mm 0 5mm; }}
  .opener .version {{ margin-bottom: 8mm; }}
  .opener .opener-heading {{ font-size: 4.2mm; font-weight: bold; margin: 0 0 3mm; }}
  .opener .opener {{ font-size: 3.4mm; text-align: left; margin: 0 0 3.5mm; line-height: 1.4; }}
  .opener .red {{ border: 0.5mm solid black; padding: 3mm 4mm; margin: 4mm 0 8mm; }}
  .contents .columns {{ column-count: 2; column-gap: 8mm; font-size: 2.7mm; }}
  .contents .file {{ font-weight: bold; font-size: 3.4mm; margin: 2mm 0 1mm; break-after: avoid; }}
  .contents .section {{ font-weight: bold; margin: 2mm 0 0.8mm; break-after: avoid; }}
  .contents ul {{ margin: 0 0 1mm; padding-left: 4mm; }}
  .contents li {{ margin: 0 0 0.6mm; }}
  .contents a {{ color: #0b4f8a; text-decoration: none; font-family: Consolas, monospace; }}
  .dial h2 {{ font-size: 3.2mm; color: #444; margin: 0 0 2mm; font-weight: normal; }}
  .dial h3 {{ font-size: 6mm; font-family: Consolas, monospace; margin: 0 0 1.5mm; word-break: break-all; }}
  .dial .where {{ font-size: 3mm; color: #444; margin: 0 0 1mm; }}
  .dial .title {{ font-size: 4.2mm; font-weight: bold; margin: 0 0 4mm; }}
  .dial .figure {{ text-align: center; margin: 0 0 4mm; }}
  .dial .figure svg {{ display: inline-block; }}
  .dial .changes {{ font-size: 3.4mm; margin: 0 0 3mm; }}
  .dial table {{ border-collapse: collapse; font-size: 3mm; margin: 0 0 3mm; }}
  .dial th, .dial td {{ border: 0.2mm solid #888; padding: 1.2mm 2.5mm; text-align: left; font-weight: normal; }}
  .dial th {{ font-weight: bold; }}
  .dial .values, .dial .note, .dial .moves, .dial .trips, .dial .options {{ font-size: 3mm; margin: 0 0 2mm; }}
  .dial .note {{ color: #444; }}
  .dial .tag {{ font-family: Consolas, monospace; }}
</style></head>
<body>{body}</body></html>
"""


def expected_pages(rows: Sequence[Dict[str, Any]], front_matter: int = FRONT_MATTER_PAGES) -> int:
    return len(rows) + front_matter


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


def verify_reference_pdf(pdf: Path, rows: Sequence[Dict[str, Any]],
                         front_matter: int = FRONT_MATTER_PAGES) -> None:
    verify_pdf(pdf, expected_pages(rows, front_matter))
    titles = outline_titles(pdf)
    want = 2 + len(FILE_ORDER) + len(rows)  # the title, Contents, one per file, one per dial
    if len(titles) != want:
        raise AssertionError(f"Expected {want} outline entries, found {len(titles)}")
    names = {r["name"] for r in rows}
    missing = names - set(titles)
    if missing:
        raise AssertionError(f"{len(missing)} dial names missing from the outline, e.g. {sorted(missing)[:3]}")
    links = link_count(pdf)
    if links < len(rows):
        raise AssertionError(f"Expected at least {len(rows)} link annotations, found {links}")
    logger.info("Verified: %d outline entries, %d link annotations.", len(titles), links)


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--quick", action="store_true", help="the quick-start cut: the Steps 1-4 dials only, with the opener page")
    parser.add_argument("--tool", choices=sorted(PACKET_DIRS), help="one tool's guide packet: its Markdown twins under docs/guides/<tool>/")
    parser.add_argument("--part", choices=PACKET_PARTS + ("all",), default="all", help="one part of the packet (default: all)")
    parser.add_argument("--out", type=Path, default=None, help="the PDF path (default: docs/Plug_Puller_Dial_Reference.pdf, or the quick-start PDF with --quick)")
    parser.add_argument("--markdown", type=Path, default=None, help="the Markdown twin's path (default: docs/guides/dial-reference.md, or the quick-start twin with --quick)")
    parser.add_argument("--markdown-only", action="store_true", help="write the Markdown twin only (no browser)")
    parser.add_argument("--keep-html", action="store_true", help="keep the HTML under tmp_renders/dial_reference/")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(message)s")

    if args.tool:
        if not args.markdown_only:
            parser.error("--tool writes the Markdown twins only for now: pass --markdown-only")
        rows = load_catalog()
        mappings = load_mappings()
        index = load_index()
        storyboards = load_storyboards()
        out_dir = PACKET_DIRS[args.tool]
        out_dir.mkdir(parents=True, exist_ok=True)
        for part in (PACKET_PARTS if args.part == "all" else (args.part,)):
            text = build_markdown(rows, mappings, index, tool=args.tool, part=part, storyboards=storyboards)
            (out_dir / f"{part}.md").write_text(text, encoding="utf-8", newline="\n")
            logger.info("Wrote %s (%d lines)", out_dir / f"{part}.md", text.count("\n"))
        return 0

    quick = args.quick
    out_pdf = args.out or (QUICK_OUT_PDF if quick else OUT_PDF)
    out_md = args.markdown or (QUICK_OUT_MD if quick else OUT_MD)
    front_matter = QUICK_FRONT_MATTER_PAGES if quick else FRONT_MATTER_PAGES
    rows = load_catalog()
    mappings = load_mappings()
    index = load_index()
    built = quick_rows(rows) if quick else rows
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(build_markdown(rows, mappings, index, quick=quick), encoding="utf-8")
    logger.info("Wrote %s (%d dials)", out_md, len(built))
    if args.markdown_only:
        return 0

    svgs = load_svgs(built)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    html_path = SCRATCH / ("dial_quick_start.html" if quick else "dial_reference.html")
    html_path.write_text(build_html(rows, mappings, index, svgs, quick=quick), encoding="utf-8")
    print_to_pdf(html_path, out_pdf, outline=True, user_data_dir=EDGE_PROFILE)
    if not args.keep_html:
        html_path.unlink()
    verify_reference_pdf(out_pdf, built, front_matter)
    logger.info("Wrote %s (%.1f KB)", out_pdf, out_pdf.stat().st_size / 1024)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
