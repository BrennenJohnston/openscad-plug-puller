#!/usr/bin/env python3
"""The MakerWorld listing as a Word document to copy and paste from.

MakerWorld's upload form has separate fields (title, summary, description,
tags, print profiles), and its description editor takes pasted text and
uploaded pictures. The listing is written once, as Markdown, in
``Documentation/Plug_Puller_MakerWorld_Listing.md``, where the
docs gate checks it; this script turns that page into
``Documentation/Plug_Puller_MakerWorld_Listing.docx`` with
each field under its own heading, the pictures placed where they go in the
description, and under each picture the file to upload, so the owner can
work down the document and the form side by side.

Markdown handled: ``#``/``##``/``###`` headings, paragraphs, ``-`` and ``1.``
lists, pipe tables, pictures alone on a line (the alt text is noted under the
picture, with the file to upload), ``**bold**``
and ``*italic*`` runs, and links, which print as their text followed by the
address in brackets, since a pasted link keeps only its text.

Usage:
    python scripts/makerworld_listing_docx.py

Local lane: needs python-docx and Pillow. License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Mm, Pt, RGBColor
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "Documentation" / "Plug_Puller_MakerWorld_Listing.md"
OUT = ROOT / "Documentation" / "Plug_Puller_MakerWorld_Listing.docx"
PICTURE_W_MM = 150
_IMAGE = re.compile(r"^!\[([^\]]*)\]\(([^)\s]+)\)$")
_RUN = re.compile(r"(\*\*[^*]+\*\*|\*[^*]+\*|\[[^\]]+\]\([^)\s]+\)|<https?://[^>]+>|`[^`]+`)")
_ROW = re.compile(r"^\|.*\|$")
_SEP = re.compile(r"^\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?$")
MUTED = RGBColor(0x55, 0x55, 0x55)


def add_runs(paragraph, text: str) -> None:
    """Bold, italic, code and links as Word runs."""
    for piece in _RUN.split(text):
        if not piece:
            continue
        if piece.startswith("**") and piece.endswith("**"):
            paragraph.add_run(piece[2:-2]).bold = True
        elif piece.startswith("*") and piece.endswith("*"):
            paragraph.add_run(piece[1:-1]).italic = True
        elif piece.startswith("`") and piece.endswith("`"):
            run = paragraph.add_run(piece[1:-1])
            run.font.name = "Consolas"
        elif piece.startswith("<http"):
            paragraph.add_run(piece[1:-1])
        elif piece.startswith("[") and (m := re.match(r"\[([^\]]+)\]\(([^)\s]+)\)", piece)):
            paragraph.add_run(f"{m.group(1)} ({m.group(2)})")
        else:
            paragraph.add_run(piece)


def _fit(src: Path, max_w_mm: float, max_h_mm: float) -> float:
    """The width in mm that keeps the picture inside the box."""
    with Image.open(src) as im:
        w_mm = max_w_mm
        if w_mm * im.height / im.width > max_h_mm:
            w_mm = max_h_mm * im.width / im.height
    return w_mm


def _notes(container, src: Path, alt: str) -> None:
    """The two small lines under a picture: the file to upload, and the alt text to paste."""
    for text in (f"Upload: {src.relative_to(ROOT).as_posix()}", f"Alt text for the picture: {alt}"):
        p = container.add_paragraph()
        r = p.add_run(text)
        r.font.size = Pt(8)
        r.font.color.rgb = MUTED


def add_picture(doc, src: Path, alt: str, caption: Optional[str]) -> None:
    doc.add_picture(str(src), width=Mm(_fit(src, min(PICTURE_W_MM, 160), 120)))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    if caption:
        cap = doc.add_paragraph()
        add_runs(cap, caption)
        cap.runs[0].italic = True if cap.runs else None
    _notes(doc, src, alt)


def add_picture_row(doc, pictures: Sequence[Tuple[Path, str]]) -> None:
    """Pictures that follow each other in the page stand side by side on one
    line (the owner's layout for the Using it section, 2026-10-06), each
    with its upload note and alt text under it."""
    table = doc.add_table(rows=1, cols=len(pictures))
    width = (160 - 4 * (len(pictures) - 1)) / len(pictures)
    for cell, (src, alt) in zip(table.rows[0].cells, pictures):
        cell.paragraphs[0].add_run().add_picture(str(src), width=Mm(_fit(src, width, 120)))
        _notes(cell, src, alt)


def add_table(doc, rows: Sequence[str]) -> None:
    cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows if not _SEP.match(r)]
    table = doc.add_table(rows=len(cells), cols=len(cells[0]))
    table.style = "Light Grid Accent 1"
    for i, row in enumerate(cells):
        for j, text in enumerate(row):
            p = table.cell(i, j).paragraphs[0]
            add_runs(p, text)
            if i == 0:
                for run in p.runs:
                    run.bold = True


def build(md: str) -> Document:
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)
    lines = md.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith("<!--"):
            while i < len(lines) and "-->" not in lines[i]:
                i += 1
            i += 1
            continue
        m = re.match(r"^(#{1,3}) (.+)$", line)
        if m:
            doc.add_heading(m.group(2).strip(), level=len(m.group(1)))
            i += 1
            continue
        m = _IMAGE.match(line.strip())
        if m:
            # Pictures that follow each other, blank lines between, share one row.
            run: List[Tuple[Path, str]] = []
            while i < len(lines) and (m := _IMAGE.match(lines[i].strip())):
                run.append(((SOURCE.parent / m.group(2)).resolve(), m.group(1)))
                i += 1
                while i < len(lines) and not lines[i].strip():
                    i += 1
            if len(run) == 1:
                # The paragraph after a picture is ordinary prose here, not a caption.
                add_picture(doc, run[0][0], run[0][1], None)
            else:
                add_picture_row(doc, run)
            continue
        if _ROW.match(line.strip()):
            rows: List[str] = []
            while i < len(lines) and _ROW.match(lines[i].strip()):
                rows.append(lines[i])
                i += 1
            add_table(doc, rows)
            continue
        if line.startswith("- "):
            while i < len(lines) and lines[i].startswith("- "):
                add_runs(doc.add_paragraph(style="List Bullet"), lines[i][2:])
                i += 1
            continue
        if re.match(r"^\d+\. ", line):
            while i < len(lines) and re.match(r"^\d+\. ", lines[i]):
                add_runs(doc.add_paragraph(style="List Number"), re.sub(r"^\d+\. ", "", lines[i]))
                i += 1
            continue
        if line.startswith("> "):
            p = doc.add_paragraph(style="Intense Quote")
            add_runs(p, line[2:])
            i += 1
            continue
        # A paragraph runs to the next blank line.
        para: List[str] = []
        while i < len(lines) and lines[i].strip() and not lines[i].startswith(("#", "- ", "|", "> ", "!")) and not re.match(r"^\d+\. ", lines[i]):
            para.append(lines[i].strip())
            i += 1
        add_runs(doc.add_paragraph(), " ".join(para))
    return doc


def main(argv: Optional[Sequence[str]] = None) -> int:
    doc = build(SOURCE.read_text(encoding="utf-8"))
    doc.save(str(OUT))
    print(f"{OUT.relative_to(ROOT).as_posix()} {OUT.stat().st_size // 1024} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
