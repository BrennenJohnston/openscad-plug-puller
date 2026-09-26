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

Usage:
    python scripts/build_dial_reference.py                 # both files
    python scripts/build_dial_reference.py --markdown-only # no browser needed

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
from scripts.generate_outline_sheets import MODEL_VERSION  # noqa: E402

logger = logging.getLogger(__name__)

CATALOG = PROJECT_ROOT / "dial_catalog.json"
MAPPINGS = {
    "one-sided": PROJECT_ROOT / "parameter_mapping.json",
    "two-sided": PROJECT_ROOT / "parameter_mapping_two_sided.json",
}
DIALS_DIR = PROJECT_ROOT / "docs" / "dials"
INDEX = DIALS_DIR / "dial_diagrams_index.json"
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

# The title page and the contents pages. Measured on the first print of the
# 118-row catalog (the contents flow over two pages in two columns); the verify
# step asserts the total.
FRONT_MATTER_PAGES = 3
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


def build_markdown(rows: Sequence[Dict[str, Any]], mappings: Dict[str, Dict[str, Dict[str, Any]]],
                   index: Sequence[Dict[str, Any]]) -> str:
    idx = {(e["file"], e["name"]): e for e in index}
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


def title_page_html() -> str:
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
               index: Sequence[Dict[str, Any]], svgs: Dict[Tuple[str, str], str]) -> str:
    idx = {(e["file"], e["name"]): e for e in index}
    pages = [title_page_html(), contents_html(rows, mappings)]
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
<html lang="en"><head><meta charset="utf-8"><title>{_esc(TITLE)}</title>
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


def expected_pages(rows: Sequence[Dict[str, Any]]) -> int:
    return len(rows) + FRONT_MATTER_PAGES


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


def verify_reference_pdf(pdf: Path, rows: Sequence[Dict[str, Any]]) -> None:
    verify_pdf(pdf, expected_pages(rows))
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
    parser.add_argument("--out", type=Path, default=OUT_PDF, help="the PDF path")
    parser.add_argument("--markdown", type=Path, default=OUT_MD, help="the Markdown twin's path")
    parser.add_argument("--markdown-only", action="store_true", help="write the Markdown twin only (no browser)")
    parser.add_argument("--keep-html", action="store_true", help="keep the HTML under tmp_renders/dial_reference/")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(message)s")

    rows = load_catalog()
    mappings = load_mappings()
    index = load_index()
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.write_text(build_markdown(rows, mappings, index), encoding="utf-8")
    logger.info("Wrote %s (%d dials)", args.markdown, len(rows))
    if args.markdown_only:
        return 0

    svgs = load_svgs(rows)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    html_path = SCRATCH / "dial_reference.html"
    html_path.write_text(build_html(rows, mappings, index, svgs), encoding="utf-8")
    print_to_pdf(html_path, args.out, outline=True, user_data_dir=EDGE_PROFILE)
    if not args.keep_html:
        html_path.unlink()
    verify_reference_pdf(args.out, rows)
    logger.info("Wrote %s (%.1f KB)", args.out, args.out.stat().st_size / 1024)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
