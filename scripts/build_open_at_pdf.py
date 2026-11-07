#!/usr/bin/env python3
"""Print the Plug Puller's document set as accessible PDFs, one per page.

Each Markdown page under ``Documentation/`` (``DOCUMENTS`` lists them) becomes
one HTML file: a cover with its title and opening paragraph, a contents page
with page numbers, then the sections one after another, each heading on the
page of what follows it, each picture in a figure with the paragraph after
it as the figure's caption, and the By touch, Check and Careful paragraphs
as marked callouts. Headless Microsoft Edge or Google Chrome prints it to a
tagged PDF: screen readers get the headings, lists, tables, links, the alt
text of every picture and its caption, and the PDF names its language and
title and has a bookmark for every heading. Comments in the Markdown (the
shot requests) never print. A link to another file of the project points at
that file's page on GitHub.

The print repeats until the contents' page numbers settle (at most three
prints), then the PDF is checked: every page US Letter, the bookmarks equal
to the headings, a link for every link of the page, the contents' page
numbers, the tags, the language, the title and every picture's alt text.
Last, the script writes ``scripts/pdf_records/<document>_pdf.json``: the
SHA-256 of the PDF and of each file it was printed from (the page, its
pictures and this script). The quick test lane
(``tests/test_open_at_pdf.py``) compares them with the files as they are,
so a change to any of them without a new print fails.

Run from the repository root after changing a page, its pictures or this
script, then commit the PDFs and their records:

    python scripts/build_open_at_pdf.py --document all
    python scripts/build_open_at_pdf.py --document user-guide

The browser is Edge or Chrome where they install by default, or the one the
CHROMIUM_PATH environment variable names. The HTML it printed stays in
``build/open_at_pdf/`` for checking. Ported from the Accessible Open AT
Documentation Template's builder (the Custom Braille Embosser's), with this
project's documents and names.

Needs pypdf for the fitting pass; otherwise standard library only. License:
PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import posixpath
import re
import shutil
import string
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parent.parent
REPO = "https://github.com/BrennenJohnston/openscad-plug-puller"
PROJECT = "Plug Puller"
LANG = "en-US"

# The documents this builder prints, each from its own Markdown page to its
# own PDF, with its own record. ``configure()`` picks one. The guides carry
# the step they belong to in their file names: Step 1 makes the tool in a
# customizer, Step 2 builds it, Step 3 uses it.
_DOC = "Plug_Puller_"


def _files(stem: str) -> Dict[str, str]:
    return {"source": f"{stem}.md", "pdf": f"{stem}.pdf"}


DOCUMENTS: Dict[str, Dict[str, str]] = {
    "browser-guide": {**_files(f"Step_1_Guide_Option_1_{_DOC}Browser_Customizer_Guide"),
                      "record": "browser_guide_pdf.json", "head": "Browser customizer guide"},
    "openscad-guide": {**_files(f"Step_1_Guide_Option_2_{_DOC}OpenSCAD_Guide"),
                       "record": "openscad_guide_pdf.json", "head": "OpenSCAD guide"},
    "makerworld-guide": {**_files(f"Step_1_Guide_Option_3_{_DOC}MakerWorld_Guide"),
                         "record": "makerworld_guide_pdf.json", "head": "MakerWorld guide"},
    "visual-guide": {**_files(f"Step_2_Guide_Option_1_{_DOC}Visual_Assembly_Guide"),
                     "record": "visual_guide_pdf.json", "head": "Visual assembly guide"},
    "assembly-guide": {**_files(f"Step_2_Guide_Option_2_{_DOC}Assembly_Guide_By_Touch"),
                       "record": "assembly_guide_by_touch_pdf.json", "head": "Assembly guide by touch"},
    "maker-guide": {**_files(f"Step_2_Guide_Option_3_{_DOC}Maker_Guide"),
                    "record": "maker_guide_pdf.json", "head": "Maker guide"},
    "user-guide": {**_files(f"Step_3_Guide_{_DOC}User_Guide"),
                   "record": "user_guide_pdf.json", "head": "User guide"},
    "device-summary": {**_files(f"{_DOC}Device_Summary"),
                       "record": "device_summary_pdf.json", "head": "Device summary"},
    "design-rationale": {**_files(f"{_DOC}Design_Rationale"),
                         "record": "design_rationale_pdf.json", "head": "Design rationale"},
}
# A compact document prints with no cover and no contents page: its H1 heads
# the first page and the sections follow, for a document meant to be one
# sheet. None at present.
COMPACT: set = set()
# A poster cover: the first section prints on the cover under the subtitle
# and there is no contents page. The Visual Assembly Guide opens with its
# parts panel that way.
COVER_HOLDS_FIRST_SECTION = {"visual-guide"}
# A screenshot guide prints its pictures at the full text width (164 mm)
# so the controls in them can be read; the other documents keep the
# standard's 110 x 70 mm figures.
WIDE_FIGURES: set = set()
DOCUMENT = "maker-guide"
COMPACT_DOC = DOCUMENT in COMPACT
RECORDS = ROOT / "scripts" / "pdf_records"
SOURCE = ROOT / "Documentation" / DOCUMENTS[DOCUMENT]["source"]
OUT_PDF = ROOT / "Documentation" / DOCUMENTS[DOCUMENT]["pdf"]
RECORD = RECORDS / DOCUMENTS[DOCUMENT]["record"]
HEAD = DOCUMENTS[DOCUMENT]["head"]
TITLE = f"{HEAD}, {PROJECT}"
SCRATCH = ROOT / "build" / "open_at_pdf"
EDGE_PROFILE = SCRATCH / "edge_profile"


def configure(document: str) -> None:
    """Point the module at one of the documents in ``DOCUMENTS``."""
    global DOCUMENT, COMPACT_DOC, SOURCE, OUT_PDF, RECORD, HEAD, TITLE
    if document not in DOCUMENTS:
        raise ValueError(f"unknown document {document!r}; one of {list(DOCUMENTS)}")
    spec = DOCUMENTS[document]
    DOCUMENT = document
    COMPACT_DOC = document in COMPACT
    SOURCE = ROOT / "Documentation" / spec["source"]
    OUT_PDF = ROOT / "Documentation" / spec["pdf"]
    RECORD = RECORDS / spec["record"]
    HEAD = spec["head"]
    TITLE = f"{HEAD}, {PROJECT}"
CONTENTS = "Contents"
COVER_SOURCE = "Online, with the printable files and both customizers:"
PROJECT_EYEBROW = "Plug Puller · Version 1"
MODEL_VERSION = "1.0.0"  # the release in CHANGES.txt; tests/test_open_at_pdf.py holds it to the model's
KEY_TITLE = "How to read the pictures"
# The marks a document's pictures use that a reader must know to follow
# the directions (an arrow, a numbered box), as the key box under its first
# heading; a document with no entry prints no box. What the pictures look
# like (the mat, the colours, the screen) is not in the key: it changes
# nothing a reader does (the owner's relevancy directive, 2026-10-06, D66).
PICTURE_KEYS: Dict[str, Sequence[Tuple[str, str]]] = {}
PAGE_W_MM, PAGE_H_MM = 215.9, 279.4  # US Letter, the CSS page size "letter"
PAGE_FOOT_MM = 18.0                  # --space-page-foot in the CSS below
MM_TO_PT = 72 / 25.4
SHORT_BLOCK = 6  # a list or table of at most this many items or rows stays on one page
PRINT_TIMEOUT_S = 300  # forty pages with fifty photographs, printed up to three times
ROW_FIGURES = 2  # pictures that follow each other share a row, at most this many

# The page shape and type sizes are the project's printed-guide standard,
# set by the OpenSCAD plug puller's builder: US Letter, 3.4 mm body text,
# every section on its own page, 110 x 70 mm figures with grey captions.
# The accent is decorative only, never text: on white it measures 2.6:1,
# below the 4.5:1 minimum for text.
PAGE = string.Template("""<!DOCTYPE html>
<html lang="$lang"><head><meta charset="utf-8"><title>$title</title>
<style>
  :root {
    --color-page: #fff;
    --color-text: #111;
    --color-muted: #444;
    --color-link: #0b4f8a;
    --color-accent: #20b2aa;
    --color-tint: #eaf7f6;
    --color-warn: #b8860b;
    --color-warn-tint: #fdf6e3;
    --color-rule: #ccc;
    --color-border: #999;
    --font: Helvetica, Arial, sans-serif;
    --font-code: Consolas, "Courier New", monospace;
    --size-body: 3.4mm;
    --size-small: 2.6mm;
    --size-table: 3mm;
    --size-callout: 3.3mm;
    --size-h1: 8mm;
    --size-h2: 8mm;
    --size-h3: 5.2mm;
    --size-toc: 4mm;
    --size-toc-sub: 3.2mm;
    --size-title: $size_title;
    --size-eyebrow: 4mm;
    --size-subtitle: 4.2mm;
    --size-version: 3.2mm;
    --space-1: 1.5mm;
    --space-2: 3mm;
    --space-3: 6mm;
    --space-4: 9mm;
    --space-band: 9mm;
    --space-page-top: 20mm;
    --space-page-side: 20mm;
    --space-page-foot: 18mm;
    --space-cover: 26mm;
    --figure-w: 110mm;
    --figure-h: 70mm;
    --row-figure-h: 62mm;
  }
  @page { size: letter; margin: 0; }
  @page cover { margin: 0; }
  @page front {
    margin: var(--space-page-top) 22mm var(--space-page-foot);
    @bottom-right { content: "Page " counter(page) " of " counter(pages); font: var(--size-small) var(--font); color: var(--color-muted); }
  }
  @page flow {
    margin: var(--space-page-top) var(--space-page-side) var(--space-page-foot);
    @top-left { content: "$running_head"; font: var(--size-small) var(--font); color: var(--color-muted); }
    @bottom-right { content: "Page " counter(page) " of " counter(pages); font: var(--size-small) var(--font); color: var(--color-muted); }
  }
  html, body { margin: 0; padding: 0; background: var(--color-page); }
  body { font: var(--size-body)/1.45 var(--font); color: var(--color-text); }
  .cover {
    page: cover; width: 215.9mm; height: 279.4mm; box-sizing: border-box; overflow: hidden;
    display: flex; flex-direction: column; break-after: page;
  }
  .cover .band { height: var(--space-band); background: var(--color-accent); }
  .cover-body { flex: 1; display: flex; flex-direction: column; justify-content: center; padding: 0 var(--space-cover) var(--space-page-top); }
  .eyebrow { font-size: var(--size-eyebrow); font-weight: bold; letter-spacing: 0.5mm; text-transform: uppercase; color: var(--color-muted); margin: 0 0 var(--space-2); }
  .cover h1 { font-size: var(--size-title); line-height: 1.1; margin: 0; }
  .cover h1::after { content: ""; display: block; width: 32mm; height: 1.2mm; background: var(--color-accent); margin: 8mm 0 7mm; }
  .subtitle { font-size: var(--size-subtitle); line-height: 1.45; margin: 0; }
  .cover figure.photo { margin: 10mm 0 0; }
  .cover figure.photo img { max-width: 164mm; max-height: 125mm; }
  .cover figure.photo figcaption { max-width: 164mm; }
  .cover.poster .cover-body { justify-content: flex-start; padding-top: 12mm; }
  .cover.poster h1::after { margin: 5mm 0 4mm; }
  .cover.poster h2 { margin: 5mm 0 3mm; font-size: 6mm; }
  .cover.poster figure.photo { margin: 0 0 3mm; }
  .cover.poster figure.photo img { max-width: 150mm; max-height: 100mm; }
  .cover.poster .key { margin: 0; }
  .version { font-size: var(--size-version); color: var(--color-muted); margin: 0 var(--space-cover) var(--space-page-top); padding-top: var(--space-2); border-top: 0.25mm solid var(--color-rule); }
  .version a { color: inherit; }
  .contents { page: front; break-after: page; }
  .contents ol { list-style: none; margin: 0; padding: 0; }
  .contents li { margin: 0 0 2.6mm; break-inside: avoid; }
  .contents ol ol { margin: 1mm 0 0 7mm; }
  .contents ol ol li { margin: 0 0 1mm; }
  .contents a { display: flex; align-items: baseline; color: inherit; text-decoration: none; }
  .contents .toc > li > a { font-size: var(--size-toc); font-weight: bold; }
  .contents .toc ol a { font-size: var(--size-toc-sub); }
  .contents .dots { flex: 1; min-width: var(--space-3); margin: 0 2mm; border-bottom: 0.3mm dotted var(--color-muted); }
  .contents .pg { flex: none; min-width: 7mm; text-align: right; }
  .flow { page: flow; }
  .flow section + section { margin-top: 7mm; }
  .flow section > h2 { break-after: avoid; }
  .flow h1 { font-size: var(--size-h1); line-height: 1.15; margin: 0 0 var(--space-3); }
  .flow h1::after { content: ""; display: block; width: 32mm; height: 1.2mm; background: var(--color-accent); margin: var(--space-2) 0 0; }
  h2 { font-size: var(--size-h2); line-height: 1.15; margin: 0 0 var(--space-3); break-after: avoid; }
  h2::after { content: ""; display: block; width: 22mm; height: 1mm; background: var(--color-accent); margin: var(--space-2) 0 0; }
  h3 { font-size: var(--size-h3); margin: 8mm 0 2.5mm; break-after: avoid; }
  p { margin: 0 0 var(--space-2); }
  ol, ul { margin: 0 0 3.5mm; padding-left: var(--space-3); }
  li { margin: 0 0 var(--space-1); }
  a { color: var(--color-link); text-decoration: none; }
  code { font-family: var(--font-code); font-size: 0.92em; }
  pre { font-family: var(--font-code); font-size: 2.7mm; line-height: 1.4; background: #f3f4f4; padding: 2.5mm 3.5mm; white-space: pre-wrap; margin: 0 0 3.5mm; }
  table { border-collapse: collapse; width: 100%; font-size: var(--size-table); line-height: 1.35; margin: 2mm 0 4mm; }
  th, td { text-align: left; vertical-align: top; padding: 1.3mm 2.5mm; border-bottom: 0.25mm solid var(--color-rule); }
  thead th { background: var(--color-tint); border-bottom: 0.4mm solid var(--color-accent); }
  thead { display: table-header-group; }
  blockquote { font-size: var(--size-callout); background: var(--color-tint); border-left: 1.2mm solid var(--color-accent); padding: 2.5mm 4mm; margin: var(--space-2) 0 5mm; }
  blockquote p { margin: 0; }
  p.touch, p.check { font-size: var(--size-callout); background: var(--color-tint); border-left: 1.2mm solid var(--color-accent); padding: 2.5mm 4mm; margin: var(--space-2) 0 5mm; }
  p.careful { font-size: var(--size-callout); background: var(--color-warn-tint); border-left: 1.2mm solid var(--color-warn); padding: 2.5mm 4mm; margin: var(--space-2) 0 5mm; }
  .key { border: 0.3mm solid var(--color-border); border-radius: 1.5mm; padding: 2.5mm 4mm 1mm; margin: 0 0 4mm; }
  .key .key-title { font-size: var(--size-body); font-weight: bold; margin: 0 0 var(--space-1); }
  .key ul { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: 1fr 1fr; column-gap: 6mm; }
  .key li { font-size: 3.1mm; line-height: 1.3; margin: 0 0 var(--space-1); }
  figure.photo { margin: 2mm 0 4mm; padding: 0; text-align: center; }
  figure.photo img { display: block; margin: 0 auto; max-width: var(--figure-w); max-height: var(--figure-h); }
  figure.photo figcaption { font-size: var(--size-small); line-height: 1.35; color: var(--color-muted); text-align: left; margin: 2mm auto 0; max-width: var(--figure-w); }
  .photo-row { display: flex; gap: 4mm; align-items: flex-start; margin: 2mm 0 4mm; }
  .photo-row figure.photo { flex: 1 1 0; min-width: 0; margin: 0; }
  .photo-row figure.photo img { max-width: 100%; max-height: var(--row-figure-h); }
  .photo-row figure.photo figcaption { max-width: none; }
  body.wide-figures figure.photo img { max-width: 164mm; max-height: 125mm; }
  body.wide-figures figure.photo figcaption { max-width: 164mm; }
  .keep, .short, li, tr, blockquote, figure.photo, .photo-row, p.touch, p.check, p.careful, .key { break-inside: avoid; }
  .cluster { display: block; }
  .cluster.keep { break-inside: avoid; }
</style></head>
<body class="$body_class">
$body
</body></html>
""")

_HEADING = re.compile(r"^(#{1,6}) (.+?)\s*#*$")
_LIST_ITEM = re.compile(r"^(\s*)(?:[-*]|(\d+)\.) (.*)$")
_IMAGE_LINE = re.compile(r"^!\[([^\]]*)\]\(([^)\s]+)\)$")
_IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)")
_TABLE_SEP = re.compile(r"^\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?$")
_PAGE_ONLY = re.compile(r"<!-- page-only -->.*?<!-- /page-only -->", re.S)
_COMMENT = re.compile(r"<!--.*?-->", re.S)
_INLINE_CODE = re.compile(r"`([^`]+)`")
_BOLD = re.compile(r"\*\*(.+?)\*\*")
_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
_AUTOLINK = re.compile(r"&lt;(https?://[^&\s]+)&gt;")
_FIGURE = '<figure class="photo">'
# A paragraph whose first words are one of these labels prints as a callout.
CALLOUTS = (("<p><strong>By touch:</strong>", "touch"), ("<p><strong>Check:</strong>", "check"), ("<p><strong>Careful:", "careful"))


# ---------------------------------------------------------------------------
# The page's Markdown
# ---------------------------------------------------------------------------

def printable_markdown(text: Optional[str] = None) -> str:
    """The guide as it prints: page-only blocks and comments dropped."""
    if text is None:
        text = SOURCE.read_text(encoding="utf-8")
    return _COMMENT.sub("", _PAGE_ONLY.sub("", text.replace("\r\n", "\n")))


def plain(text: str) -> str:
    """A heading's words without Markdown: no backticks, bold or link targets."""
    return re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", re.sub(r"[`*]", "", text))


def anchor(text: str) -> str:
    """A heading's id, as GitHub makes them: lower case, punctuation dropped,
    spaces to hyphens."""
    return re.sub(r"[^a-z0-9 _-]", "", plain(text).lower()).replace(" ", "-")


def headings(md: str) -> List[Tuple[int, str]]:
    """(level, text) of every heading, fenced code left out."""
    out = []
    in_fence = False
    for line in md.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        m = _HEADING.match(line.strip())
        if m and not in_fence:
            out.append((len(m.group(1)), m.group(2)))
    return out


def section_titles() -> List[str]:
    """The guide's section (H2) titles, as the PDF's bookmarks show them."""
    return [plain(text) for level, text in headings(printable_markdown()) if level == 2]


def image_alts() -> List[str]:
    """The alt text of every picture the guide prints."""
    return [alt for alt, _src in _IMAGE.findall(printable_markdown())]


# ---------------------------------------------------------------------------
# Markdown to HTML: exactly what the guide uses
# ---------------------------------------------------------------------------

def link_target(href: str) -> str:
    """Where a link points in the print: a web link or a section of this
    guide as written; another file of the project, its page on GitHub."""
    if href.startswith(("http://", "https://", "#")):
        return href
    path, sep, fragment = href.partition("#")
    target = posixpath.normpath(posixpath.join(SOURCE.parent.relative_to(ROOT).as_posix(), path))
    if target.startswith(".."):
        raise ValueError(f"{href} points outside the repository")
    return f"{REPO}/blob/main/{target}{sep}{fragment}"


def inline(text: str) -> str:
    if "![" in text:
        raise ValueError(f"a picture must stand on a line of its own: {text[:60]}")
    out = html.escape(text, quote=False)
    out = _INLINE_CODE.sub(lambda m: f"<code>{m.group(1)}</code>", out)
    out = _BOLD.sub(r"<strong>\1</strong>", out)
    out = _LINK.sub(lambda m: f'<a href="{html.escape(link_target(html.unescape(m.group(2))))}">{m.group(1)}</a>', out)
    return _AUTOLINK.sub(r'<a href="\1">\1</a>', out)


def table(rows: Sequence[str]) -> str:
    """A pipe table, its first column as row headers."""
    cells = [[c.strip() for c in row.strip().strip("|").split("|")] for row in rows]
    head, body = cells[0], cells[2:]
    out = ["<table><thead><tr>" + "".join(f'<th scope="col">{inline(c)}</th>' for c in head) + "</tr></thead><tbody>"]
    for row in body:
        out.append(f'<tr><th scope="row">{inline(row[0])}</th>' + "".join(f"<td>{inline(c)}</td>" for c in row[1:]) + "</tr>")
    out.append("</tbody></table>")
    return "".join(out)


def picture(alt: str, src: str) -> str:
    path = (SOURCE.parent / src).resolve()
    if not alt:
        raise ValueError(f"the picture {src} has no alt text")
    if not path.exists():
        raise FileNotFoundError(f"the picture {src} does not exist")
    return f'{_FIGURE}<img src="{html.escape(path.as_uri())}" alt="{html.escape(alt)}"></figure>'


def _top_item(line: str) -> Optional[re.Match]:
    m = _LIST_ITEM.match(line)
    return m if m and not m.group(1) else None


def blocks(md: str) -> List[str]:
    """The HTML of each block of a Markdown text: a heading, a paragraph, a
    list, a table, a block quote, fenced code or a picture on its own line."""
    lines = md.splitlines()
    out: List[str] = []
    i, n = 0, len(lines)
    while i < n:
        stripped = lines[i].strip()
        if not stripped:
            i += 1
            continue
        if stripped.startswith("```"):
            code: List[str] = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            out.append("<pre><code>" + html.escape("\n".join(code), quote=False) + "</code></pre>")
            continue
        m = _HEADING.match(stripped)
        if m:
            level, text = len(m.group(1)), m.group(2)
            out.append(f'<h{level} id="{anchor(text)}">{inline(text)}</h{level}>')
            i += 1
            continue
        if stripped.startswith("|") and i + 1 < n and _TABLE_SEP.match(lines[i + 1].strip()):
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append(lines[i])
                i += 1
            out.append(table(rows))
            continue
        if stripped.startswith(">"):
            quote = []
            while i < n and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip()[1:].strip())
                i += 1
            out.append("<blockquote><p>" + inline(" ".join(q for q in quote if q)) + "</p></blockquote>")
            continue
        m = _IMAGE_LINE.match(stripped)
        if m:
            out.append(picture(m.group(1), m.group(2)))
            i += 1
            continue
        m = _top_item(lines[i])
        if m:
            ordered = m.group(2) is not None
            items: List[str] = []
            while i < n:
                item = _top_item(lines[i])
                if item and (item.group(2) is not None) == ordered:
                    words = [item.group(3)]
                    i += 1
                    while i < n and lines[i].startswith(" ") and lines[i].strip():
                        if _LIST_ITEM.match(lines[i]):
                            raise ValueError(f"nested lists do not print: {lines[i].strip()[:60]}")
                        words.append(lines[i].strip())
                        i += 1
                    items.append("<li>" + inline(" ".join(words)) + "</li>")
                elif not lines[i].strip() and i + 1 < n and _top_item(lines[i + 1]):
                    i += 1
                else:
                    break
            tag = "ol" if ordered else "ul"
            start = f' start="{m.group(2)}"' if ordered and m.group(2) != "1" else ""
            out.append(f"<{tag}{start}>" + "".join(items) + f"</{tag}>")
            continue
        para: List[str] = []
        while i < n and lines[i].strip() and not (
                _HEADING.match(lines[i].strip()) or lines[i].strip().startswith(("```", ">", "|"))
                or _top_item(lines[i]) or _IMAGE_LINE.match(lines[i].strip())):
            para.append(lines[i].strip())
            i += 1
        if not para:
            para.append(stripped)
            i += 1
        text = "<p>" + inline(" ".join(para)) + "</p>"
        for prefix, cls in CALLOUTS:
            if text.startswith(prefix):
                text = f'<p class="{cls}">' + text[len("<p>"):]
                break
        out.append(text)
    return out


def _caption_figures(section: Sequence[str]) -> List[str]:
    """Each figure takes the plain paragraph after it as its caption: the
    long description a screen reader hears after the alt text, and the
    text under the picture on the page."""
    out: List[str] = []
    i = 0
    while i < len(section):
        block = section[i]
        if block.startswith(_FIGURE) and i + 1 < len(section) and section[i + 1].startswith("<p>"):
            caption = section[i + 1][len("<p>"):-len("</p>")]
            out.append(block[:-len("</figure>")] + f"<figcaption>{caption}</figcaption></figure>")
            i += 2
        else:
            out.append(block)
            i += 1
    return out


def _photo_rows(section: Sequence[str]) -> List[str]:
    """Figures that follow each other stand side by side, two to a row; a
    third starts a new row, so no picture prints under 65 mm wide."""
    out: List[str] = []
    i = 0
    while i < len(section):
        if section[i].startswith(_FIGURE):
            j = i
            while j < len(section) and section[j].startswith(_FIGURE):
                j += 1
            run = section[i:j]
            for k in range(0, len(run), ROW_FIGURES):
                pair = run[k:k + ROW_FIGURES]
                out.append('<div class="photo-row">' + "\n".join(pair) + "</div>" if len(pair) > 1 else pair[0])
            i = j
            continue
        out.append(section[i])
        i += 1
    return out


def _keep_pairs(section: Sequence[str], first: Tuple[str, ...], second: Tuple[str, ...] = ("",)) -> List[str]:
    """Each block that starts with ``first`` and the block after it, when
    that one starts with ``second``, in one box that stays on one page."""
    out: List[str] = []
    i = 0
    while i < len(section):
        if section[i].startswith(first) and i + 1 < len(section) and section[i + 1].startswith(second):
            out.append('<div class="keep">' + "\n".join(section[i:i + 2]) + "</div>")
            i += 2
        else:
            out.append(section[i])
            i += 1
    return out


def layout(section: Sequence[str]) -> List[str]:
    """Print classes on a section's blocks: a short list or table stays on
    one page, every figure carries its caption, figures that follow each
    other share a row, and a heading stays on the page of what follows it."""
    marked = []
    for block in section:
        tag = block[1:3]
        if tag in ("ol", "ul") and block.count("<li>") <= SHORT_BLOCK:
            block = block.replace(f"<{tag}", f'<{tag} class="short"', 1)
        elif block.startswith("<table>") and block.count("<tr>") <= SHORT_BLOCK + 1:
            block = '<table class="short">' + block[len("<table>"):]
        marked.append(block)
    return _clusters(_keep_pairs(_photo_rows(_caption_figures(marked)), ("<h2", "<h3")))


_HEADING_START = ('<div class="keep"><h2', '<div class="keep"><h3', "<h2", "<h3")


def _clusters(section: Sequence[str]) -> List[str]:
    """A heading, the blocks after it and the first picture that follows, in
    one ``cluster`` box named by the heading's id, so the fitting pass can
    see the three as one unit of information (the owner's layout rule,
    2026-10-06, D68): the picture is shrunk to the room left under the words
    rather than pushed to the next page."""
    out: List[str] = []
    i = 0
    while i < len(section):
        block = section[i]
        if block.startswith(_HEADING_START):
            j = i + 1
            while j < len(section) and not section[j].startswith(_HEADING_START + (_FIGURE, '<div class="photo-row">')):
                j += 1
            if j < len(section) and section[j].startswith((_FIGURE, '<div class="photo-row">')):
                ident = re.search(r'<h[23] id="([^"]+)"', block)
                if ident:
                    out.append(f'<div class="cluster" data-cluster="{ident.group(1)}">' + "\n".join(section[i:j + 1]) + "</div>")
                    i = j + 1
                    continue
        out.append(block)
        i += 1
    return out


def _number_figures(text: str) -> str:
    """Every figure numbered in document order, the order the PDF draws its pictures."""
    count = 0

    def tag(m: re.Match) -> str:
        nonlocal count
        count += 1
        return f'<figure class="photo" data-figure="{count - 1}">'

    return re.sub(re.escape(_FIGURE), tag, text)


def _apply_fit(text: str, fit: Dict[int, float], move: set) -> str:
    """The fitting pass's decisions in the HTML: a picture's height in mm,
    and the clusters that print as one unbreakable block."""
    for k, height in fit.items():
        head = f'<figure class="photo" data-figure="{k}">'
        start = text.find(head)
        if start < 0:
            raise ValueError(f"no figure {k} to fit")
        img = text.find("<img ", start)
        text = text[:img] + f'<img style="max-height: {height:.1f}mm" ' + text[img + len("<img "):]
    for ident in move:
        text = text.replace(f'<div class="cluster" data-cluster="{ident}">', f'<div class="cluster keep" data-cluster="{ident}">', 1)
    return text


def contents_html(entries: Sequence[Tuple[int, str]], pages: Optional[Dict[str, int]]) -> str:
    """The contents page: every section with its page, its subsections
    indented. Before the first print every page shows "00"."""
    def link(text: str) -> str:
        page = str(pages[anchor(text)]) if pages and anchor(text) in pages else "00"
        return (f'<a href="#{anchor(text)}"><span>{html.escape(plain(text))}</span>'
                f'<span class="dots"></span><span class="pg">{page}</span></a>')
    tree: List[Tuple[str, List[str]]] = []
    for level, text in entries:
        if level == 2:
            tree.append((text, []))
        elif level == 3 and tree:
            tree[-1][1].append(text)
    out = ['<section class="contents">', f'<h2 id="{anchor(CONTENTS)}">{CONTENTS}</h2>', '<ol class="toc">']
    for text, subs in tree:
        sub = "<ol>" + "".join(f"<li>{link(s)}</li>" for s in subs) + "</ol>" if subs else ""
        out.append(f"<li>{link(text)}{sub}</li>")
    out += ["</ol>", "</section>"]
    return "\n".join(out)


def document_html(md: str, pages: Optional[Dict[str, int]] = None, fit: Optional[Dict[int, float]] = None,
                  move: Optional[set] = None) -> str:
    """The guide as the HTML the PDF is printed from. ``pages`` maps each
    heading's id to its page in the last print; ``fit`` and ``move`` are the
    fitting pass's decisions (``fit_pass``)."""
    head, sep, body = md.partition("\n## ")
    body = sep.lstrip("\n") + body
    cover = blocks(head)
    if len(cover) < 2 or not cover[0].startswith("<h1") or not cover[1].startswith("<p>"):
        raise ValueError("the guide must open with its H1 and one paragraph before the first H2")
    # One picture with its caption may follow the opening paragraph: it
    # prints on the cover under the subtitle (the User Guide's panel of what
    # the guide covers, the owner's request of 2026-10-06).
    if cover[2:] and not (cover[2].startswith(_FIGURE) and len(cover) in (3, 4)):
        raise ValueError("only one picture, with its caption, may stand between the opening paragraph and the first H2")
    cover_figure = layout(cover[2:]) if cover[2:] else []
    sections: List[List[str]] = []
    for block in blocks(body):
        if block.startswith("<h2") or not sections:
            sections.append([])
        sections[-1].append(block)
    poster = DOCUMENT in COVER_HOLDS_FIRST_SECTION
    if COMPACT_DOC:
        parts = ['<div class="flow">', "<section>", *_keep_pairs(cover, ("<h1",)), "</section>"]
    else:
        # A poster cover carries the first section (the parts panel) under
        # its subtitle and the document has no contents page (the owner's
        # choice for the Visual Assembly Guide, 2026-10-06).
        on_cover = layout(sections[0]) + ([key_box_html()] if key_box_html() else []) if poster else []
        parts = [
            f'<section class="cover{" poster" if poster else ""}"><div class="band"></div><div class="cover-body">',
            f'<p class="eyebrow">{html.escape(PROJECT_EYEBROW)}</p>', cover[0],
            '<p class="subtitle">' + cover[1][len("<p>"):], *cover_figure, *on_cover, "</div>",
            f'<p class="version">Model version {html.escape(MODEL_VERSION)}. {html.escape(COVER_SOURCE)} '
            f'<a href="{REPO}">{REPO.split("://", 1)[1]}</a></p>',
            "</section>",
            *([] if poster else [contents_html(headings(body), pages)]),
            '<div class="flow">',
        ]
        if poster:
            sections = sections[1:]
    key = "" if poster else key_box_html()
    for n, section in enumerate(sections):
        laid = layout(section)
        if n == 0 and key and not COMPACT_DOC:
            # The picture key sits right under the first flow section's
            # heading, inside the box that keeps the heading with what follows.
            laid = [laid[0].replace("</h2>", "</h2>\n" + key, 1)] + laid[1:]
        parts += ["<section>", *laid, "</section>"]
    parts.append("</div>")
    text = _apply_fit(_number_figures("\n".join(parts)), fit or {}, move or set())
    ids = re.findall(r'id="([^"]+)"', text)
    duplicates = sorted({x for x in ids if ids.count(x) > 1})
    if duplicates:
        raise ValueError(f"two headings share an id: {duplicates}")
    dead = sorted(set(re.findall(r'href="#([^"]+)"', text)) - set(ids))
    if dead:
        raise ValueError(f"links to sections that do not exist: {dead}")
    return PAGE.substitute(lang=LANG, title=html.escape(TITLE), running_head=f"{PROJECT_EYEBROW} · {HEAD.lower()}",
                           body=text, body_class="wide-figures" if DOCUMENT in WIDE_FIGURES else "",
                           size_title=cover_title_size(plain(head.split("\n", 1)[0].lstrip("# "))))


def key_box_html() -> str:
    """The "How to read the pictures" box of the current document, or an
    empty string when its pictures follow no convention worth a key."""
    items = PICTURE_KEYS.get(DOCUMENT)
    if not items:
        return ""
    lis = "".join(f"<li><b>{html.escape(term)}:</b> {html.escape(meaning)}</li>" for term, meaning in items)
    return f'<div class="key"><p class="key-title">{html.escape(KEY_TITLE)}</p><ul>{lis}</ul></div>'


def cover_title_size(title: str) -> str:
    """The cover title's size, chosen so the H1 stays on ONE line: when it
    wraps, the PDF's outline joins the lines without the space between
    them ("Version 2Assembly Guide"), which a screen reader voices as one
    word. Helvetica averages about half an em per character, and the cover
    body is 164 mm wide. The standard's size is 11 mm."""
    for size in (11, 9.5, 8.5, 7.5, 6.5, 5.5):
        if len(title) * size * 0.52 <= 164:
            return f"{size}mm"
    return "5mm"


# ---------------------------------------------------------------------------
# Printing
# ---------------------------------------------------------------------------

def find_browser() -> Path:
    env = os.environ.get("CHROMIUM_PATH")
    if env:
        if not Path(env).exists():
            raise FileNotFoundError(f"CHROMIUM_PATH names {env}, which does not exist")
        return Path(env)
    pf = os.environ.get("ProgramFiles", r"C:\Program Files")
    pf86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
    local = os.environ.get("LocalAppData", "")
    candidates = [
        Path(pf) / "Microsoft" / "Edge" / "Application" / "msedge.exe",
        Path(pf86) / "Microsoft" / "Edge" / "Application" / "msedge.exe",
        Path(pf) / "Google" / "Chrome" / "Application" / "chrome.exe",
        Path(pf86) / "Google" / "Chrome" / "Application" / "chrome.exe",
        Path(local) / "Google" / "Chrome" / "Application" / "chrome.exe",
        Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
        Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
    ]
    for path in candidates:
        if path.exists():
            return path
    for name in ("microsoft-edge", "google-chrome", "chromium", "chromium-browser"):
        found = shutil.which(name)
        if found:
            return Path(found)
    raise FileNotFoundError("No Microsoft Edge or Google Chrome found to print the PDF; set CHROMIUM_PATH to one.")


def print_to_pdf(html_path: Path, out_pdf: Path) -> None:
    """Print ``html_path`` to ``out_pdf`` with headless Edge or Chrome, with
    bookmarks from the headings. The scratch profile keeps the call from
    attaching to a browser that is already open, where it never returns."""
    browser = find_browser()
    EDGE_PROFILE.mkdir(parents=True, exist_ok=True)
    cmd = [str(browser), "--headless", "--disable-gpu", "--no-first-run", "--disable-extensions",
           "--no-pdf-header-footer", "--generate-pdf-document-outline", f"--user-data-dir={EDGE_PROFILE}",
           f"--print-to-pdf={out_pdf}", html_path.as_uri()]
    before = out_pdf.stat().st_mtime_ns if out_pdf.exists() else None
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=PRINT_TIMEOUT_S)
    if not out_pdf.exists():
        raise RuntimeError(f"PDF printing failed (exit {result.returncode}): {result.stderr[-500:]}")
    # The browser exits cleanly when a PDF viewer holds the old file open.
    if before is not None and out_pdf.stat().st_mtime_ns == before:
        raise RuntimeError(f"PDF printing did not replace {out_pdf.name}; close it in any PDF viewer "
                           f"(exit {result.returncode}): {result.stderr[-500:]}")


# ---------------------------------------------------------------------------
# Reading the PDF back (enough of the format for the checks)
# ---------------------------------------------------------------------------

_OBJ = re.compile(rb"(\d+)\s+\d+\s+obj(.*?)endobj", re.S)
_REF = rb"(\d+)\s+\d+\s+R"
_STRING = rb"\s*(\((?:\\.|[^\\)])*\)|<[0-9A-Fa-f\s]*>)"
_ESCAPE = re.compile(rb"\\([0-7]{1,3}|\r\n|.)", re.S)
_ESCAPED = {b"n": b"\n", b"r": b"\r", b"t": b"\t", b"b": b"\b", b"f": b"\f", b"\n": b"", b"\r": b"", b"\r\n": b""}


def _decode(token: bytes) -> str:
    """A PDF string token, literal ``(...)`` or hex ``<...>``, as text."""
    if token.startswith(b"<"):
        raw = bytes.fromhex(re.sub(rb"\s", b"", token[1:-1]).decode("ascii"))
    else:
        def one(m: re.Match) -> bytes:
            e = m.group(1)
            return bytes([int(e, 8) & 0xFF]) if e[0] in b"01234567" else _ESCAPED.get(e, e)
        raw = _ESCAPE.sub(one, token[1:-1])
    return raw[2:].decode("utf-16-be") if raw.startswith(b"\xfe\xff") else raw.decode("latin-1")


def pdf_strings(data: bytes, key: bytes) -> List[str]:
    """Every text string the PDF gives for the key ``/key``, decoded."""
    return [_decode(m.group(1)) for m in re.finditer(rb"/" + key + _STRING, data, re.S)]


def _objects(data: bytes) -> Dict[int, bytes]:
    return {int(m.group(1)): m.group(2) for m in _OBJ.finditer(data)}


def _catalog(objs: Dict[int, bytes]) -> bytes:
    catalogs = [body for body in objs.values() if re.search(rb"/Type\s*/Catalog\b", body)]
    if len(catalogs) != 1:
        raise AssertionError(f"expected one catalog in the PDF, found {len(catalogs)}")
    return catalogs[0]


def outline_titles(pdf: Path) -> List[str]:
    """The titles of the PDF's bookmarks, in reading order."""
    objs = _objects(pdf.read_bytes())
    root = re.search(rb"/Outlines\s+" + _REF, _catalog(objs))
    titles: List[str] = []

    def walk(num: int) -> None:
        child = re.search(rb"/First\s+" + _REF, objs[num])
        while child:
            item = objs[int(child.group(1))]
            titles.extend(pdf_strings(item, b"Title")[:1])
            walk(int(child.group(1)))
            child = re.search(rb"/Next\s+" + _REF, item)
    if root:
        walk(int(root.group(1)))
    return titles


def dest_pages(pdf: Path) -> Dict[str, int]:
    """Every named destination of the PDF (an id a link points at) with the
    page it lands on, counted from 1."""
    objs = _objects(pdf.read_bytes())
    catalog = _catalog(objs)
    order: List[int] = []

    def walk(num: int) -> None:
        body = objs[num]
        if re.search(rb"/Type\s*/Pages\b", body):
            kids = re.search(rb"/Kids\s*\[([^\]]*)\]", body)
            for kid in re.findall(_REF, kids.group(1) if kids else b""):
                walk(int(kid))
        else:
            order.append(num)

    root = re.search(rb"/Pages\s+" + _REF, catalog)
    dests = re.search(rb"/Dests\s+" + _REF, catalog)
    if not root:
        raise AssertionError("the PDF names no page tree")
    if not dests:
        # No link points inside the document: a compact print with web links only.
        return {}
    walk(int(root.group(1)))
    page_no = {num: i + 1 for i, num in enumerate(order)}
    pairs = re.findall(rb"/([^\s/\[\]<>()]+)\s*\[\s*" + _REF, objs[int(dests.group(1))])
    return {name.decode("latin-1"): page_no[int(ref)] for name, ref in pairs}


# ---------------------------------------------------------------------------
# The fitting pass: a heading, its words and its picture on one page
# ---------------------------------------------------------------------------

PT_PER_MM = 72 / 25.4
FIT_FLOOR_MM = 36.0      # a picture shrunk below this would not be read; the cluster moves instead
FIT_SHRINK = 0.85        # when an estimate still leaves a picture on the next page, try this much smaller
FIT_PRINTS = 14          # each print settles at least one more page; a long guide needs several
FIGURE_MM, ROW_FIGURE_MM = 70.0, 62.0   # --figure-h and --row-figure-h in the CSS
# The heights in mm of what stands round a picture in a cluster, measured
# on prints: from the heading's destination top to the picture's top is
# 33.2 mm plus a line of words for each line (the same at the top of a page,
# where the destination sits on the page edge); under the picture come its
# caption, if it has one, and its bottom margin, plus a safety margin.
_ABOVE_MM = 33.2
_LINE_MM = 3.4 * 1.45
_CHARS_PER_LINE = 108          # Helvetica at 3.4 mm across the 164 mm text width, measured on a print
_CAPTION_LINE_MM = 2.6 * 1.35
_CAPTION_GAP_MM = 2.0
_CAPTION_CHARS_PER_LINE = 130
_BELOW_MM = 4.0 + 1.5
_CLUSTER = re.compile(r'<div class="cluster(?: keep)?" data-cluster="([^"]+)">(.*?</figure>(?:\s*</div>)?)\s*</div>', re.S)


def figure_boxes(pdf: Path) -> List[Tuple[int, float, float]]:
    """(page, bottom in pt, height in pt) of every picture the PDF draws, in
    drawing order, which is the figures' document order."""
    from pypdf import PdfReader

    reader = PdfReader(str(pdf))
    out: List[Tuple[int, float, float]] = []
    for number, page in enumerate(reader.pages, 1):
        xobjects = page["/Resources"].get("/XObject", {}) if "/Resources" in page else {}

        def before(op, args, cm, tm, _page=number, _x=xobjects):
            if op == b"Do" and str(_x[str(args[0])].get_object().get("/Subtype")) == "/Image":
                out.append((_page, float(cm[5]), float(cm[3])))

        page.extract_text(visitor_operand_before=before)
    return out


def heading_tops(pdf: Path) -> Dict[str, Tuple[int, float]]:
    """Each heading id with the page it lands on and its top, in pt from the
    page's bottom edge, from the PDF's named destinations."""
    from pypdf import PdfReader

    reader = PdfReader(str(pdf))
    out: Dict[str, Tuple[int, float]] = {}
    for name, dest in reader.named_destinations.items():
        top = dest.top
        out[name.lstrip("/")] = (reader.get_destination_page_number(dest) + 1, float(top) if top is not None else PAGE_H_MM * PT_PER_MM)
    return out


def clusters(html_text: str) -> List[Dict]:
    """Each cluster: its heading id, the numbers of the pictures in its first
    figure or figure row, and the height in mm of everything in it that is
    not picture (the heading, the words, the caption, the margins)."""
    out = []
    for m in _CLUSTER.finditer(html_text):
        body = m.group(2)
        fig = re.search(r'data-figure="(\d+)"', body)
        if not fig:
            continue
        after_heading = re.sub(r"<h[23][^>]*>.*?</h[23]>", "", body[:fig.start()], count=1, flags=re.S)
        words = html.unescape(re.sub(r"<[^>]+>", "", after_heading)).strip()
        lines = max(1, -(-len(words) // _CHARS_PER_LINE))
        row = body[:fig.start()].rstrip().endswith('<div class="photo-row">')
        figures = [int(n) for n in re.findall(r'data-figure="(\d+)"', body)] if row else [int(fig.group(1))]
        captions = re.findall(r"<figcaption>(.*?)</figcaption>", body, re.S)
        caption_lines = max([max(1, -(-len(re.sub(r"<[^>]+>", "", c)) // _CAPTION_CHARS_PER_LINE)) for c in captions] or [0])
        caption = _CAPTION_GAP_MM + caption_lines * _CAPTION_LINE_MM if caption_lines else 0.0
        other = _ABOVE_MM + lines * _LINE_MM + caption + _BELOW_MM
        out.append({"id": m.group(1), "figures": figures, "other_mm": other, "natural_mm": ROW_FIGURE_MM if row else FIGURE_MM})
    return out


def fit_pass(pdf: Path, html_text: str, fit: Dict[int, float], move: set) -> bool:
    """Read the print back. On every page where the last cluster's picture
    fell onto the next page, share the room under the page's first cluster
    heading among that page's clusters, so their pictures shrink alike and
    the last one stays with its words; when even the smallest readable
    picture would not fit, that cluster moves whole. Returns True when a
    decision changed, so the document prints again."""
    tops = heading_tops(pdf)
    boxes = figure_boxes(pdf)
    by_page: Dict[int, List[Dict]] = {}
    for c in clusters(html_text):
        if c["id"] in tops and c["figures"][0] < len(boxes):
            by_page.setdefault(tops[c["id"]][0], []).append(c)
    before = (dict(fit), set(move))
    for page, group in sorted(by_page.items()):
        last = group[-1]
        if boxes[last["figures"][0]][0] <= page or last["id"] in move:
            continue
        top = tops[group[0]["id"]][1] / PT_PER_MM
        room = top - PAGE_FOOT_MM - sum(c["other_mm"] for c in group)
        height = room / len(group)
        tried = fit.get(last["figures"][0])
        if tried is not None and height >= tried:
            height = tried * FIT_SHRINK   # the estimate was hopeful: smaller again
        if height >= FIT_FLOOR_MM:
            for c in group:
                for k in c["figures"]:
                    fit[k] = round(min(height, c["natural_mm"]), 1)
        else:
            for k in last["figures"]:
                fit.pop(k, None)
            move.add(last["id"])
        if os.environ.get("PDF_FIT_DEBUG"):
            print(f"  page {page}: top {top:.0f} mm, {len(group)} clusters, other {sum(c['other_mm'] for c in group):.0f} mm, "
                  f"room {room:.0f} mm -> {'move ' + last['id'] if height < FIT_FLOOR_MM else f'{height:.0f} mm each'}")
    return (fit, move) != before


def verify(pdf: Path, html_text: str, pages: Dict[str, int]) -> Dict[str, int]:
    """The checks on the printed PDF; returns its counts."""
    data = pdf.read_bytes()
    objs = _objects(data)
    n_pages = len(re.findall(rb"/Type\s*/Page\b", data))
    for box in re.findall(rb"/MediaBox\s*\[([^\]]*)\]", data):
        x0, y0, x1, y1 = (float(v) for v in box.split())
        if abs((x1 - x0) - PAGE_W_MM * MM_TO_PT) > 0.5 * MM_TO_PT or abs((y1 - y0) - PAGE_H_MM * MM_TO_PT) > 0.5 * MM_TO_PT:
            raise AssertionError(f"a page is {x1 - x0:.1f} x {y1 - y0:.1f} pt, not US Letter")
    want = [html.unescape(re.sub(r"<[^>]+>", "", h)) for h in re.findall(r"<h[1-6][^>]*>(.*?)</h[1-6]>", html_text)]
    titles = outline_titles(pdf)
    # The browser drops the space at the point where a long heading wraps
    # onto a second line of the page, so the two are compared without spaces.
    if [t.replace(" ", "") for t in titles] != [w.replace(" ", "") for w in want]:
        raise AssertionError(f"the bookmarks {titles} are not the headings {want}")
    links = len(re.findall(rb"/Subtype\s*/Link", data))
    if links < html_text.count("<a href="):
        raise AssertionError(f"{links} link annotations for {html_text.count('<a href=')} links")
    found = dest_pages(pdf)
    wrong = {a: (p, found.get(a)) for a, p in pages.items() if found.get(a) != p}
    if wrong:
        raise AssertionError(f"contents page numbers (printed, actual) that are wrong: {wrong}")
    if b"/StructTreeRoot" not in data or not re.search(rb"/Marked\s+true", data):
        raise AssertionError("the PDF is not tagged")
    if LANG not in pdf_strings(data, b"Lang"):
        raise AssertionError(f"the PDF does not name its language as {LANG}")
    if TITLE not in pdf_strings(data, b"Title") or not re.search(rb"/DisplayDocTitle\s+true", data):
        raise AssertionError(f"the PDF does not show its title {TITLE!r}")
    # A <figure> with a <figcaption> prints as Figure{ Figure[Alt], Caption }:
    # the outer Figure groups the picture with its caption and carries no
    # alt of its own, the inner one is the image with its alt text. A figure
    # without a caption (the Visual Assembly Guide's panels) prints as
    # Figure{ Figure[Alt] }. Every Figure must be one of these.
    figures = {num: body for num, body in objs.items() if re.search(rb"/S\s*/Figure\b", body)}
    pictures = {num: pdf_strings(body, b"Alt")[:1] for num, body in figures.items()}
    leaves = {num: alt[0] for num, alt in pictures.items() if alt and alt[0].strip()}
    wrappers = [num for num in figures if num not in leaves]
    for num in wrappers:
        kids = _kids(objs, figures[num])
        if sorted(kids) not in (["Caption", "Figure"], ["Figure"]):
            raise AssertionError(f"a figure in the PDF has no alt text and is not a picture with its caption (children {kids})")
    if sorted(leaves.values()) != sorted(html.unescape(a) for a in re.findall(r'<img [^>]*alt="([^"]*)"', html_text)):
        raise AssertionError("the PDF's alt texts are not the pictures' alt texts")
    if "<table" in html_text and not (b"/Scope /Column" in data and b"/Scope /Row" in data):
        raise AssertionError("the table's column and row headers are not tagged")
    captions_html = html_text.count("<figcaption>")
    captions_pdf = len(re.findall(rb"/S\s*/Caption\b", data))
    if captions_pdf != captions_html:
        raise AssertionError(f"{captions_pdf} caption tags in the PDF for {captions_html} figure captions")
    return {"pages": n_pages, "bookmarks": len(titles), "links": links, "pictures": len(leaves),
            "captions": captions_pdf}


def _kids(objs: Dict[int, bytes], body: bytes) -> List[str]:
    """The structure types of an element's children (the /K array)."""
    m = re.search(rb"/K\s*\[([^\]]*)\]", body) or re.search(rb"/K\s+(\d+\s+\d+\s+R)", body)
    if not m:
        return []
    out = []
    for ref in re.findall(_REF, m.group(1)):
        kid = objs.get(int(ref), b"")
        t = re.search(rb"/S\s*/(\w+)", kid)
        if t:
            out.append(t.group(1).decode("latin-1"))
    return out


# ---------------------------------------------------------------------------
# The record the quick test lane checks
# ---------------------------------------------------------------------------

def input_files() -> List[Path]:
    """What the PDF is printed from: the guide, its pictures and this script."""
    pictures = [(SOURCE.parent / src).resolve() for _alt, src in _IMAGE.findall(printable_markdown())]
    return [SOURCE, *pictures, Path(__file__).resolve()]


def input_digests() -> Dict[str, str]:
    """The SHA-256 of each input file; text with LF line endings on every system."""
    out = {}
    for path in input_files():
        data = path.read_bytes()
        if path.suffix in (".md", ".py"):
            data = data.replace(b"\r\n", b"\n")
        out[path.relative_to(ROOT).as_posix()] = hashlib.sha256(data).hexdigest()
    return out


def build() -> Dict[str, int]:
    md = printable_markdown()
    SCRATCH.mkdir(parents=True, exist_ok=True)
    html_path = SCRATCH / f"{DOCUMENT}.html"
    head, sep, body = md.partition("\n## ")
    # Contents entries need destinations; a compact or poster document has no contents page.
    anchors = [] if COMPACT_DOC or DOCUMENT in COVER_HOLDS_FIRST_SECTION else [anchor(text) for level, text in headings(sep + body) if level in (2, 3)]
    pages: Optional[Dict[str, int]] = None
    fit: Dict[int, float] = {}
    move: set = set()
    for prints in range(1, FIT_PRINTS + 1):
        html_text = document_html(md, pages, fit, move)
        html_path.write_text(html_text, encoding="utf-8")
        print_to_pdf(html_path, OUT_PDF)
        landed = dest_pages(OUT_PDF)
        missing = [a for a in anchors if a not in landed]
        if missing:
            raise AssertionError(f"the PDF has no destination for the contents entries {missing}")
        found = {a: landed[a] for a in anchors}
        refit = fit_pass(OUT_PDF, html_text, fit, move)
        settled = found == pages or COMPACT_DOC or DOCUMENT in COVER_HOLDS_FIRST_SECTION
        pages = found
        if settled and not refit:
            break
    else:
        raise AssertionError(f"the layout still moved after {FIT_PRINTS} prints")
    if fit or move:
        print(f"fitted: {len(fit)} pictures shrunk to their page, {len(move)} sections moved whole")
    counts = verify(OUT_PDF, html_text, pages)
    counts["prints"] = prints
    data = OUT_PDF.read_bytes()
    record = {
        "pdf": OUT_PDF.relative_to(ROOT).as_posix(),
        "pdf_sha256": hashlib.sha256(data).hexdigest(),
        "inputs": input_digests(),
        "pages": counts["pages"],
        "bookmarks": counts["bookmarks"],
        "links": counts["links"],
        "pictures": counts["pictures"],
        "captions": counts["captions"],
        "producer": (pdf_strings(data, b"Producer") or ["unknown"])[0],
    }
    RECORD.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return counts


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--document", choices=list(DOCUMENTS) + ["all"], default="all",
                    help="which document to print (default 'all': every one whose page exists)")
    args = ap.parse_args(argv)
    keys = [k for k in DOCUMENTS if (ROOT / "Documentation" / DOCUMENTS[k]["source"]).exists()] if args.document == "all" else [args.document]
    for key in keys:
        configure(key)
        RECORDS.mkdir(parents=True, exist_ok=True)
        counts = build()
        print(f"{OUT_PDF.relative_to(ROOT).as_posix()}: {counts['pages']} pages, {counts['bookmarks']} bookmarks, "
              f"{counts['links']} links, {counts['pictures']} pictures with alt text, {counts['captions']} caption tags "
              f"({counts['prints']} prints, {OUT_PDF.stat().st_size / 1024:.0f} KB)")
        print(f"{RECORD.relative_to(ROOT).as_posix()} written; HTML in {SCRATCH.relative_to(ROOT).as_posix()}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
