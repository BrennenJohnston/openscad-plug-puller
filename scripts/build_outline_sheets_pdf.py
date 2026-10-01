"""Build the printable outline-sheets PDF for the public repo.

Bundles every SVG in the public repo's ``docs/guides/outline-sheets/`` into
one print-ready PDF (``docs/Plug_Puller_Outline_Sheets.pdf``), preceded by a
styled cover/index page. The sheets are inlined into an HTML
shell whose ``@page`` size equals the SVG page (210 x 279 mm — prints on A4
and US Letter), then printed to PDF with headless Edge/Chrome (Skia PDF,
vector output). Because @page and the SVG share the same mm dimensions the
print scale is exactly 100%, preserving the sheets' 1:1 geometry.

After printing, the script verifies the result: page count, and every page's
MediaBox equal to 210 x 279 mm (within 0.5 mm) so a scaled render cannot ship
silently; then the document title, and a bookmark on every page.

Run from the dev repo root after regenerating the sheets:

    python scripts/generate_outline_sheets.py
    python scripts/build_outline_sheets_pdf.py

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import argparse
import logging
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SHEETS_DIR = PROJECT_ROOT / "docs" / "guides" / "outline-sheets"
DEFAULT_OUT = PROJECT_ROOT / "docs" / "Plug_Puller_Outline_Sheets.pdf"
EDGE_PROFILE = PROJECT_ROOT / "tmp_renders" / "edge_profile"
DOCUMENT_TITLE = "1:1 outline sheets, one-sided and two-sided pullers"

PAGE_W_MM, PAGE_H_MM = 210.0, 279.0
MM_TO_PT = 72.0 / 25.4

# Shared document style for the three PDF builders (this module, plus
# build_dial_reference.py, which already
# import PAGE_W_MM/PAGE_H_MM/print_to_pdf/verify_pdf from here). The accent
# reuses the dial diagrams' own plug teal (generate_dial_diagrams.COLOR_PLUG)
# so the printed guides read as one family with the pictures instead of a
# fourth, invented color. It is decorative only, never text: on white it
# measures 2.6:1, below the 4.5:1 WCAG AA text minimum.
ACCENT = "#20b2aa"
ACCENT_TINT = "#eaf7f6"
RULE_GRAY = "#ccc"
BORDER_GRAY = "#bbb"
TEXT_GRAY = "#444"

logger = logging.getLogger(__name__)

# Sheet order for the PDF: the one-sided puller by plug family (S/M/L), then
# the two-sided puller's plates by plug family. Each key names the sheet
# files outline_<key>_<size>.svg.
SHEET_ORDER = [
    ("flat-2-prong", "Flat 2-prong lamp plug (NEMA 1-15) — one-sided puller"),
    ("standard-3-prong", "Standard 3-prong plug (NEMA 5-15) — one-sided puller"),
    ("wide-2-prong-appliance", "Wide 2-prong appliance plug (NEMA 1-15) — one-sided puller"),
    ("two-sided-plate", "Heavy-duty extension cord (NEMA 5-15) — two-sided puller plate"),
    ("two-sided-plate_usb-c-laptop-tip", "USB-C laptop tip — two-sided puller plate"),
    ("two-sided-plate_flat-2-prong", "Flat 2-prong lamp plug (NEMA 1-15) — two-sided puller plate"),
    ("two-sided-plate_standard-3-prong", "Standard 3-prong plug (NEMA 5-15) — two-sided puller plate"),
]
SIZES = ["small", "medium", "large"]


def find_browser() -> Path:
    env = os.environ.get("CHROMIUM_PATH")
    if env and Path(env).exists():
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
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError(
        "No Chromium-based browser found for PDF printing. "
        "Set CHROMIUM_PATH to msedge.exe or chrome.exe."
    )


def sheet_files() -> List[Path]:
    files: List[Path] = []
    for key, _ in SHEET_ORDER:
        for size in SIZES:
            p = SHEETS_DIR / f"outline_{key}_{size}.svg"
            if not p.exists():
                raise FileNotFoundError(
                    f"Missing sheet {p.name} — run scripts/generate_outline_sheets.py first."
                )
            files.append(p)
    return files


def cover_html() -> str:
    """Cover/index page in the same visual language as the sheets
    (Helvetica, centered bold title, grey hint text, hairline rules)."""
    rows = []
    page = 2
    for key, label in SHEET_ORDER:
        cells = []
        for size in SIZES:
            cells.append(
                f"<td>{size.capitalize()} &nbsp;·&nbsp; p. {page}</td>"
            )
            page += 1
        rows.append(f"<tr><th>{label}</th>{''.join(cells)}</tr>")
    table = "".join(rows)
    return f"""
<section class="page cover">
  <h1>Plug Puller — 1:1 Outline Sheets</h1>
  <p class="subtitle">Try the fit on paper before you print the tool. One sheet per
  quick-select combination, all at exact 1:1 scale.</p>
  <div class="warn">
    <p><b>Print this document at 100% scale / “Actual size” — never “fit to page”.</b></p>
    <p>Every sheet carries a 50 × 50 mm calibration square. Measure it with a ruler
    before trusting anything: if it is not exactly 50 × 50 mm, your print was scaled —
    re-print at 100%.</p>
  </div>
  <h2>What's inside</h2>
  <table class="index">{table}</table>
  <h2>How to use a sheet</h2>
  <ol>
    <li>Print the page you need at 100% and check its calibration square.</li>
    <li>Cut along the <b>solid</b> outline. Dashed lines are holes, slots, and the
        plug pocket — poke through the two big finger circles.</li>
    <li>Hold the cutout against your plug on the wall and try the finger holes.</li>
    <li>Happy? Open the Customizer with the settings printed in the sheet's title
        block and export your STL (the tool's quick start).</li>
  </ol>
  <p class="hint">Finger holes feel wrong on every sheet? Print the cards in
  <span class="mono">stl/Measuring-Stencil/</span> — their F1/F2 cards carry all 18
  finger-sizing holes (Ø 15–32 mm) — and measure your finger instead
  (each full guide, under Try it on paper first).</p>
  <p class="footer">openscad-plug-puller · 1:1 outline sheets · works on A4 and US Letter ·
  guide: the full guides, under Try it on paper first</p>
</section>
"""


def sheet_headings(label: str, size: str) -> str:
    """Headings a reader never sees on paper: the PDF's bookmarks and a
    screen reader's page landmarks. A plug's first sheet opens its section;
    each sheet names its hand size."""
    first = f'<h2 class="sheet-heading">{label}</h2>' if size == SIZES[0] else ""
    return f'{first}<h3 class="sheet-heading">{size.capitalize()} hand size</h3>'


def build_html(sheets: List[Path]) -> str:
    pages = [cover_html()]
    names = [(label, size) for _, label in SHEET_ORDER for size in SIZES]
    for svg, (label, size) in zip(sheets, names):
        content = svg.read_text(encoding="utf-8")
        pages.append(f'<section class="page sheet">{sheet_headings(label, size)}{content}</section>')
    body = "\n".join(pages)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>{DOCUMENT_TITLE}</title>
<style>
  @page {{ size: {PAGE_W_MM:g}mm {PAGE_H_MM:g}mm; margin: 0; }}
  html, body {{ margin: 0; padding: 0; }}
  .page {{
    width: {PAGE_W_MM:g}mm; height: {PAGE_H_MM:g}mm;
    overflow: hidden; page-break-after: always;
  }}
  .page:last-child {{ page-break-after: auto; }}
  .page svg {{ display: block; }}
  .sheet {{ position: relative; }}
  /* Painted whole, never clipped: Chromium puts a bookmark where its
     heading is painted (a clipped one falls back to page 1), and the PDF's
     tags carry only the painted letters. */
  .sheet-heading {{
    position: absolute; top: 0; left: 0; margin: 0;
    font-size: 1px; line-height: 1px; white-space: nowrap; color: transparent;
  }}
  .cover {{
    box-sizing: border-box; padding: 24mm 20mm;
    font-family: Helvetica, Arial, sans-serif; color: black;
  }}
  .cover h1 {{ font-size: 7mm; text-align: center; margin: 0 0 3mm; }}
  .cover h1::after {{
    content: ""; display: block; width: 28mm; height: 0.7mm;
    background: {ACCENT}; margin: 3mm auto 0;
  }}
  .cover .subtitle {{ font-size: 3.4mm; text-align: center; margin: 5mm 0 8mm; }}
  .cover .warn {{
    border: 0.5mm solid black; border-left: 1.3mm solid {ACCENT};
    background: {ACCENT_TINT}; padding: 3mm 5mm; margin: 0 0 9mm;
    font-size: 3.2mm;
  }}
  .cover .warn p {{ margin: 1.5mm 0; }}
  .cover h2 {{
    font-size: 4.2mm; margin: 8mm 0 3mm; padding-bottom: 1.3mm;
    border-bottom: 0.3mm solid {RULE_GRAY};
  }}
  .cover table.index {{
    border-collapse: collapse; width: 100%; font-size: 3.1mm; margin-top: 1mm;
  }}
  .cover table.index th, .cover table.index td {{
    border: 0.2mm solid {BORDER_GRAY}; padding: 1.8mm 2.5mm; text-align: left;
    font-weight: normal;
  }}
  .cover table.index th {{
    font-weight: bold; width: 40%; background: {ACCENT_TINT};
    border-bottom: 0.4mm solid {ACCENT};
  }}
  .cover ol {{ font-size: 3.2mm; margin: 0; padding-left: 6mm; }}
  .cover ol li {{ margin-bottom: 2mm; }}
  .cover .hint {{ font-size: 3mm; color: {TEXT_GRAY}; margin-top: 6mm; }}
  .cover .mono {{ font-family: Consolas, monospace; }}
  .cover .footer {{
    position: absolute; left: 0; right: 0; bottom: 8mm;
    text-align: center; font-size: 2.6mm; color: {TEXT_GRAY};
    padding-top: 1.5mm; margin: 0 20mm; border-top: 0.15mm solid {RULE_GRAY};
  }}
</style></head>
<body>{body}</body></html>
"""


def print_to_pdf(
    html_path: Path,
    out_pdf: Path,
    *,
    outline: bool = False,
    user_data_dir: Path | None = None,
) -> None:
    """Print ``html_path`` to ``out_pdf`` with headless Edge/Chrome.

    ``outline=True`` asks the browser for a PDF document outline (bookmarks)
    built from the page's headings. ``user_data_dir`` gives the browser a
    scratch profile: without one, a headless call attaches to a running
    Edge and never returns.
    """
    browser = find_browser()
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(browser),
        "--headless",
        "--disable-gpu",
        "--no-first-run",
        "--disable-extensions",
        "--no-pdf-header-footer",
    ]
    if outline:
        cmd.append("--generate-pdf-document-outline")
    if user_data_dir is not None:
        user_data_dir.mkdir(parents=True, exist_ok=True)
        cmd.append(f"--user-data-dir={user_data_dir}")
    cmd += [f"--print-to-pdf={out_pdf}", html_path.as_uri()]
    before = out_pdf.stat().st_mtime_ns if out_pdf.exists() else None
    logger.info("Printing with %s", browser.name)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if not out_pdf.exists():
        raise RuntimeError(
            f"PDF printing failed (rc={result.returncode}): {result.stderr[-500:]}"
        )
    # The browser exits cleanly when it cannot overwrite a PDF that a
    # viewer holds open, which would leave the old file to be verified.
    if before is not None and out_pdf.stat().st_mtime_ns == before:
        raise RuntimeError(
            f"PDF printing did not replace {out_pdf}; close it if a PDF viewer has it "
            f"open (rc={result.returncode}): {result.stderr[-500:]}"
        )


def verify_pdf(
    out_pdf: Path,
    expected_pages: int,
    *,
    page_w_mm: float = PAGE_W_MM,
    page_h_mm: float = PAGE_H_MM,
) -> None:
    """The page count, and every page's box equal to ``page_w_mm`` x
    ``page_h_mm`` (the sheets' own 210 x 279 mm unless given)."""
    data = out_pdf.read_bytes()
    n_pages = data.count(b"/Type /Page") - data.count(b"/Type /Pages")
    if n_pages != expected_pages:
        raise AssertionError(f"Expected {expected_pages} pages, found {n_pages}")
    boxes = set(re.findall(rb"/MediaBox\s*\[([^\]]*)\]", data))
    want_w = page_w_mm * MM_TO_PT
    want_h = page_h_mm * MM_TO_PT
    tol = 0.5 * MM_TO_PT
    for box in boxes:
        vals = [float(v) for v in box.split()]
        w, h = vals[2] - vals[0], vals[3] - vals[1]
        if abs(w - want_w) > tol or abs(h - want_h) > tol:
            raise AssertionError(
                f"Page box {w:.2f}x{h:.2f} pt != {want_w:.2f}x{want_h:.2f} pt "
                "(print scale would be wrong)"
            )
    logger.info(
        "Verified: %d pages, page box %.1f x %.1f mm (1:1 scale preserved).",
        n_pages, page_w_mm, page_h_mm,
    )


_OBJ = re.compile(rb"(\d+)\s+\d+\s+obj(.*?)endobj", re.S)
_REF = re.compile(rb"(\d+)\s+\d+\s+R")
_STRING = rb"(<[0-9A-Fa-f\s]*>|\((?:\\.|[^\\)])*\))"


def pdf_string(raw: bytes) -> str:
    """A PDF string token: UTF-16 hex with its byte-order mark, or a
    literal with backslash escapes."""
    if raw.startswith(b"<"):
        data = bytes.fromhex(re.sub(rb"\s", b"", raw[1:-1]).decode("ascii"))
        return data[2:].decode("utf-16-be") if data.startswith(b"\xfe\xff") else data.decode("latin-1")
    return re.sub(rb"\\(.)", rb"\1", raw[1:-1]).decode("latin-1")


def bookmark_pages(pdf: Path) -> List[int]:
    """The page each bookmark lands on, counted from 1 in the page tree's
    order; 0 for a bookmark without a page."""
    objs = {int(m.group(1)): m.group(2) for m in _OBJ.finditer(pdf.read_bytes())}
    catalog = next(body for body in objs.values() if re.search(rb"/Type\s*/Catalog\b", body))

    def leaves(num: int) -> List[int]:
        kids = re.search(rb"/Kids\s*\[([^\]]*)\]", objs[num])
        if kids is None:
            return [num]
        return [leaf for kid in _REF.findall(kids.group(1)) for leaf in leaves(int(kid))]

    root = re.search(rb"/Pages\s+(\d+)\s+\d+\s+R", catalog)
    order = {num: i + 1 for i, num in enumerate(leaves(int(root.group(1))))}
    pages = []
    for body in objs.values():
        if b"/Title" in body and b"/Parent" in body:
            dest = re.search(rb"/Dest\s*\[\s*(\d+)\s+\d+\s+R", body)
            pages.append(order.get(int(dest.group(1)), 0) if dest else 0)
    return pages


def verify_title_and_bookmarks(out_pdf: Path, html_text: str, n_pages: int) -> None:
    """The document title, one bookmark per heading, and a bookmark on every
    page, so a title or a bookmark lost by the browser cannot ship."""
    titles = {pdf_string(m.group(1)) for m in re.finditer(rb"/Title\s*" + _STRING, out_pdf.read_bytes())}
    if DOCUMENT_TITLE not in titles:
        raise AssertionError(f"The PDF's title is not {DOCUMENT_TITLE!r}")
    pages = bookmark_pages(out_pdf)
    want = len(re.findall(r"<h[1-6][ >]", html_text))
    if len(pages) != want:
        raise AssertionError(f"Expected {want} bookmarks (the HTML's headings), found {len(pages)}")
    missing = sorted(set(range(1, n_pages + 1)) - set(pages))
    if missing:
        raise AssertionError(f"No bookmark lands on pages {missing}")
    logger.info("Verified: the title, and %d bookmarks reaching all %d pages.", len(pages), n_pages)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--keep-html", action="store_true",
                        help="Keep the intermediate HTML next to the PDF.")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    sheets = sheet_files()
    html = build_html(sheets)
    with tempfile.TemporaryDirectory() as tmp:
        html_path = Path(tmp) / "outline_sheets.html"
        html_path.write_text(html, encoding="utf-8")
        print_to_pdf(html_path, args.out, outline=True, user_data_dir=EDGE_PROFILE)
        if args.keep_html:
            keep = args.out.with_suffix(".html")
            keep.write_text(html, encoding="utf-8")
            logger.info("Kept HTML: %s", keep)

    verify_pdf(args.out, expected_pages=1 + len(sheets))
    verify_title_and_bookmarks(args.out, html, n_pages=1 + len(sheets))
    logger.info("Wrote %s (%.1f KB)", args.out, args.out.stat().st_size / 1024)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
