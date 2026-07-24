"""Build the printable outline-sheets PDF for the public repo.

Bundles every SVG in the public repo's ``docs/guides/outline-sheets/`` into
one print-ready PDF (``docs/Plug_Puller_Outline_Sheets.pdf``), preceded by a
styled cover/index page. Uses the same pipeline that produced
``Plug_Puller_Measuring_Template.pdf``: the sheets are inlined into an HTML
shell whose ``@page`` size equals the SVG page (210 x 279 mm — prints on A4
and US Letter), then printed to PDF with headless Edge/Chrome (Skia PDF,
vector output). Because @page and the SVG share the same mm dimensions the
print scale is exactly 100%, preserving the sheets' 1:1 geometry.

After printing, the script verifies the result: page count, and every page's
MediaBox equal to 210 x 279 mm (within 0.5 mm) so a scaled render cannot ship
silently.

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

PAGE_W_MM, PAGE_H_MM = 210.0, 279.0
MM_TO_PT = 72.0 / 25.4

logger = logging.getLogger(__name__)

# Sheet order for the PDF: flat tool by plug family (S/M/L), clamshell last.
SHEET_ORDER = [
    ("flat-2-prong", "Flat 2-prong lamp plug (NEMA 1-15) — flat tool"),
    ("standard-3-prong", "Standard 3-prong plug (NEMA 5-15) — flat tool"),
    ("heavy-duty-round", "Heavy-duty extension cord (NEMA 5-15) — flat tool"),
    ("heavy-duty-clamshell", "Heavy-duty clamshell plate"),
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
        block and export your STL (docs/guides/quick-start-beginner.md).</li>
  </ol>
  <p class="hint">Finger holes feel wrong on every sheet? Print the cards in
  <span class="mono">stl/Measuring-Stencil/</span> — their F1/F2 cards carry all 18
  finger-sizing holes (Ø 15–32 mm) — and measure your finger instead
  (docs/guides/print-preview-outlines.md).</p>
  <p class="footer">openscad-plug-puller · 1:1 outline sheets · works on A4 and US Letter ·
  guide: docs/guides/print-preview-outlines.md</p>
</section>
"""


def build_html(sheets: List[Path]) -> str:
    pages = [cover_html()]
    for svg in sheets:
        content = svg.read_text(encoding="utf-8")
        pages.append(f'<section class="page">{content}</section>')
    body = "\n".join(pages)
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  @page {{ size: {PAGE_W_MM:g}mm {PAGE_H_MM:g}mm; margin: 0; }}
  html, body {{ margin: 0; padding: 0; }}
  .page {{
    width: {PAGE_W_MM:g}mm; height: {PAGE_H_MM:g}mm;
    overflow: hidden; page-break-after: always;
  }}
  .page:last-child {{ page-break-after: auto; }}
  .page svg {{ display: block; }}
  .cover {{
    box-sizing: border-box; padding: 22mm 20mm;
    font-family: Helvetica, Arial, sans-serif; color: black;
  }}
  .cover h1 {{ font-size: 7mm; text-align: center; margin: 0 0 4mm; }}
  .cover .subtitle {{ font-size: 3.4mm; text-align: center; margin: 0 0 8mm; }}
  .cover .warn {{
    border: 0.5mm solid black; padding: 3mm 5mm; margin: 0 0 8mm;
    font-size: 3.2mm;
  }}
  .cover .warn p {{ margin: 1.5mm 0; }}
  .cover h2 {{ font-size: 4.2mm; margin: 8mm 0 3mm; }}
  .cover table.index {{
    border-collapse: collapse; width: 100%; font-size: 3.1mm;
  }}
  .cover table.index th, .cover table.index td {{
    border: 0.2mm solid #888; padding: 1.6mm 2.5mm; text-align: left;
    font-weight: normal;
  }}
  .cover table.index th {{ font-weight: bold; width: 40%; }}
  .cover ol {{ font-size: 3.2mm; margin: 0; padding-left: 6mm; }}
  .cover ol li {{ margin-bottom: 1.6mm; }}
  .cover .hint {{ font-size: 3mm; color: #444; margin-top: 6mm; }}
  .cover .mono {{ font-family: Consolas, monospace; }}
  .cover .footer {{
    position: absolute; left: 0; right: 0; bottom: 8mm;
    text-align: center; font-size: 2.6mm; color: #444;
  }}
</style></head>
<body>{body}</body></html>
"""


def print_to_pdf(html_path: Path, out_pdf: Path) -> None:
    browser = find_browser()
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(browser),
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={out_pdf}",
        html_path.as_uri(),
    ]
    logger.info("Printing with %s", browser.name)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if not out_pdf.exists():
        raise RuntimeError(
            f"PDF printing failed (rc={result.returncode}): {result.stderr[-500:]}"
        )


def verify_pdf(out_pdf: Path, expected_pages: int) -> None:
    data = out_pdf.read_bytes()
    n_pages = data.count(b"/Type /Page") - data.count(b"/Type /Pages")
    if n_pages != expected_pages:
        raise AssertionError(f"Expected {expected_pages} pages, found {n_pages}")
    boxes = set(re.findall(rb"/MediaBox\s*\[([^\]]*)\]", data))
    want_w = PAGE_W_MM * MM_TO_PT
    want_h = PAGE_H_MM * MM_TO_PT
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
        n_pages, PAGE_W_MM, PAGE_H_MM,
    )


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
        print_to_pdf(html_path, args.out)
        if args.keep_html:
            keep = args.out.with_suffix(".html")
            keep.write_text(html, encoding="utf-8")
            logger.info("Kept HTML: %s", keep)

    verify_pdf(args.out, expected_pages=1 + len(sheets))
    logger.info("Wrote %s (%.1f KB)", args.out, args.out.stat().st_size / 1024)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
