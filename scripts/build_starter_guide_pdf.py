"""Build the printable Starter Guide PDF.

Produces ``docs/Plug_Puller_Starter_Guide.pdf``: the starter guide
(``docs/guides/starter-guide.md``) condensed onto two typeset pages, followed
by the 1:1 measuring stencil sheet (``docs/guides/stencil-sheet.svg``) as the
final page — so someone without a 3D printer can print one document and have
both the instructions and the paper stencil at exact scale.

Reuses the outline-sheets pipeline (headless Edge/Chrome printing a fixed
210 x 279 mm @page, then MediaBox verification) so the stencil page keeps its
1:1 geometry.

Run from the repo root after regenerating the sheet:

    python scripts/generate_stencil_sheet.py
    python scripts/build_starter_guide_pdf.py

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import argparse
import logging
import tempfile
from pathlib import Path

from build_outline_sheets_pdf import (
    PAGE_H_MM,
    PAGE_W_MM,
    print_to_pdf,
    verify_pdf,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SHEET_SVG = PROJECT_ROOT / "docs" / "guides" / "stencil-sheet.svg"
DEFAULT_OUT = PROJECT_ROOT / "docs" / "Plug_Puller_Starter_Guide.pdf"

logger = logging.getLogger(__name__)


def page_one() -> str:
    return """
<section class="page guide">
  <h1>Plug Puller — Starter Guide</h1>
  <p class="subtitle">From “that plug is stuck” to a printed tool: figure out
  your plug (match it or measure it), fill in the Customizer steps, print.</p>

  <div class="warn">
    <p><b>The last page of this PDF is a 1:1 measuring stencil sheet.</b>
    Print this document at 100% scale / “Actual size” — never “fit to page” —
    and check the 50 × 50 mm calibration square on that page before
    trusting it.</p>
  </div>

  <h2>What you need</h2>
  <p>The plug you want to pull (in its outlet), and either the printed
  <b>measuring stencil</b> (<span class="mono">stl/Measuring_Stencil.stl</span>,
  1.2 mm cards, no supports) or the paper stencil sheet at the back of this
  document.</p>

  <h2>The stencil cards — legend</h2>
  <p>Each 3D-printed card has a raised two-letter ID you can find by touch:</p>
  <table class="index">
    <tr><th>P1</th><td>plug silhouette: <b>flat 2-prong lamp plug</b> (NEMA 1-15)</td></tr>
    <tr><th>P2</th><td>plug silhouette: <b>standard 3-prong plug</b> (NEMA 5-15)</td></tr>
    <tr><th>P3</th><td>plug silhouette: <b>heavy-duty extension cord</b> (NEMA 5-15)</td></tr>
    <tr><th>R1</th><td><b>ruler</b> — raised mm ticks, numerals every 10 mm, tactile edge notches</td></tr>
    <tr><th>C1</th><td><b>cord gauge</b> — through-holes Ø 3–9 mm</td></tr>
    <tr><th>F1 / F2</th><td><b>finger sizing</b> — 18 labeled holes (Ø 15–25 on F1, Ø 26–32 on F2)</td></tr>
  </table>
  <p>Each P card has three openings: <b>W</b> (the plug's width outline),
  <b>T</b> (its thickness outline), and a round cord hole. It is a “does my
  plug match this preset?” test — no numbers involved.</p>

  <h2>Path A — match a preset (fastest, no numbers)</h2>
  <ol>
    <li>Take the <b>P1</b>, <b>P2</b>, and <b>P3</b> cards to your plug.</li>
    <li>Hold each card's <b>W</b> cutout over the plug (wide side), then the
        <b>T</b> cutout (thin side). Try the cord in the round hole.</li>
    <li>If the plug fills one card's openings — snug, no big gaps — that
        preset is your plug. Pick it in Step 1:
      <ul>
        <li>P1 → <span class="mono">Flat 2-prong lamp plug - NEMA 1-15</span></li>
        <li>P2 → <span class="mono">Standard 3-prong plug - NEMA 5-15</span></li>
        <li>P3 → <span class="mono">Heavy-duty extension cord - NEMA 5-15</span></li>
      </ul></li>
    <li>Skip ahead to “Fill in the Customizer steps” on the next page.</li>
  </ol>
  <p>No card fits? Your plug is between presets — take Path B; the measured
  tool will fit better than any preset anyway.</p>

  <h2>Path B — measure (about 5 minutes)</h2>
  <p>Work the worksheet in <span class="mono">docs/guides/measuring-guide.md</span>;
  the numbers below are the worksheet's own numbering.</p>
  <table class="index">
    <tr><th>1</th><td>Plug length — <b>R1</b>, wall plate to the plug's back face</td></tr>
    <tr><th>2–3</th><td>Plug width near wall / near cord — <b>R1</b> notched edge against the plug body</td></tr>
    <tr><th>4–5</th><td>Plug thickness near wall / near cord — <b>R1</b>, across the thin direction</td></tr>
    <tr><th>6</th><td>Cord thickness — <b>C1</b>, smallest hole the cord slides through</td></tr>
    <tr><th>7</th><td>Wall plate style — a picture quiz, see the measuring guide</td></tr>
    <tr><th>8</th><td>Finger knuckle width — <b>F1 / F2</b>, smallest comfortable hole, <b>minus 5</b></td></tr>
    <tr><th>9</th><td>Hand width — <b>R1</b>, across the four knuckles, flat hand</td></tr>
  </table>
  <p class="hint">8 and 9 are only needed if you pick “Measure my hand” in
  Step 2 — the built-in Small / Medium / Large cover most hands.</p>
  <p class="footer">openscad-plug-puller · starter guide · page 1 of 3</p>
</section>
"""


def page_two() -> str:
    return """
<section class="page guide">
  <h2>Fill in the Customizer steps</h2>
  <p>Open <span class="mono">src/Plug_Puller_Parametric.scad</span> in OpenSCAD
  and show the Customizer panel (uncheck <i>View ▸ Hide Customizer</i>). Every
  click is spelled out in <span class="mono">docs/guides/quick-start-beginner.md</span>;
  the short version:</p>
  <table class="index">
    <tr><th>Step 0 — Tool Style</th><td>leave on <span class="mono">Auto from plug</span>.
        Thick round plugs (like P3) get the heavy-duty clamshell, everything
        else the flat tool.</td></tr>
    <tr><th>Step 1 — Your Plug</th><td>the preset from Path A, or your Path B numbers
        with <span class="mono">plug_preset = Measure my plug</span>.</td></tr>
    <tr><th>Step 2 — Size</th><td><span class="mono">Medium</span> fits most adults; or
        <span class="mono">Measure my hand</span> with worksheet numbers 8–9.</td></tr>
    <tr><th>Step 3 — Attachment</th><td>how the tool attaches to the plug. Keep the default
        <span class="mono">Zip ties + Velcro</span> unless you know you want less.</td></tr>
    <tr><th>Step 4 — Cord Hook</th><td><span class="mono">Right</span> or
        <span class="mono">Left</span> (flat tool only).</td></tr>
  </table>
  <p>Press <b>F6</b> to render, then <i>File ▸ Export ▸ STL</i>. The clamshell
  is one plate — print it <b>twice</b>, flip one copy, zip-tie the pair face
  to face around the plug.</p>

  <h2>Which steps shape which tool</h2>
  <p>Each step says which tool it shapes; settings for the other tool are
  simply ignored (the console tells you which ones).</p>
  <table class="index three">
    <tr class="head"><th>Step</th><td><b>Flat tool</b></td><td><b>Heavy-duty clamshell</b></td></tr>
    <tr><th>0 — Tool style</th><td>picks it</td><td>picks it</td></tr>
    <tr><th>1 — Your plug</th><td>pocket, notch, hook slot</td><td>arm gap, arm length, cord channel</td></tr>
    <tr><th>2 — Size</th><td>finger holes, body size</td><td>finger bores</td></tr>
    <tr><th>3 — Attachment</th><td>zip-hole grid, velcro wings</td><td>zip stations, arm strap slots</td></tr>
    <tr><th>4 — Cord hook</th><td>J-hook direction</td><td><i>ignored — no cord hook</i></td></tr>
  </table>
  <p>On the clamshell, the Step 3 <b>zip ties are what hold the two plates
  together</b> — leave them on unless you have another plan (the model warns
  you if you turn them off).</p>

  <h2>Printing the 3D stencil on a small bed</h2>
  <p>The cards pack onto print sheets automatically. Open
  <span class="mono">Measuring_Stencil.scad</span>, set
  <span class="mono">bed_width</span> and <span class="mono">bed_depth</span> to
  your printer's bed, and the console lists which cards land on which sheet.
  Render with <span class="mono">part_index = 1</span>, export and print, then
  repeat with <span class="mono">part_index = 2</span>, and so on.
  (<span class="mono">part_index = 0</span> previews all sheets at once —
  don't print that one.)</p>

  <h2>If the print doesn't fit</h2>
  <p>One symptom, one number to nudge:
  <span class="mono">docs/guides/fit-troubleshooting.md</span>. Want to
  sanity-check before printing the real tool? Print a paper 1:1 outline sheet
  of your combination first
  (<span class="mono">docs/guides/print-preview-outlines.md</span>).</p>

  <div class="warn">
    <p><b>Next page: the 1:1 measuring stencil sheet.</b> Cut along the dashed
    lines. Measure the calibration square before trusting anything — it must
    be exactly 50 × 50 mm.</p>
  </div>
  <p class="footer">openscad-plug-puller · starter guide · page 2 of 3</p>
</section>
"""


def build_html() -> str:
    sheet = SHEET_SVG.read_text(encoding="utf-8")
    body = "\n".join(
        [page_one(), page_two(), f'<section class="page">{sheet}</section>']
    )
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
  .guide {{
    box-sizing: border-box; padding: 16mm 18mm; position: relative;
    font-family: Helvetica, Arial, sans-serif; color: black;
    font-size: 3.1mm; line-height: 1.45;
  }}
  .guide h1 {{ font-size: 6.4mm; text-align: center; margin: 0 0 2.5mm; }}
  .guide .subtitle {{ font-size: 3.3mm; text-align: center; margin: 0 0 5mm; }}
  .guide h2 {{ font-size: 4mm; margin: 4.5mm 0 1.8mm; }}
  .guide p {{ margin: 1.5mm 0; }}
  .guide .warn {{
    border: 0.5mm solid black; padding: 2mm 4mm; margin: 3mm 0;
  }}
  .guide table.index {{
    border-collapse: collapse; width: 100%; margin: 1.5mm 0;
  }}
  .guide table.index th, .guide table.index td {{
    border: 0.2mm solid #888; padding: 1.2mm 2.2mm; text-align: left;
    vertical-align: top; font-weight: normal;
  }}
  .guide table.index th {{ font-weight: bold; white-space: nowrap; }}
  .guide table.three th {{ width: 26%; }}
  .guide ol, .guide ul {{ margin: 1mm 0; padding-left: 6mm; }}
  .guide li {{ margin-bottom: 1mm; }}
  .guide .mono {{ font-family: Consolas, monospace; font-size: 0.95em; }}
  .guide .hint {{ color: #444; }}
  .guide .footer {{
    position: absolute; left: 0; right: 0; bottom: 7mm;
    text-align: center; font-size: 2.6mm; color: #444; margin: 0;
  }}
</style></head>
<body>{body}</body></html>
"""


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

    if not SHEET_SVG.exists():
        raise FileNotFoundError(
            f"Missing {SHEET_SVG} — run scripts/generate_stencil_sheet.py first."
        )
    html = build_html()
    with tempfile.TemporaryDirectory() as tmp:
        html_path = Path(tmp) / "starter_guide.html"
        html_path.write_text(html, encoding="utf-8")
        print_to_pdf(html_path, args.out)
        if args.keep_html:
            keep = args.out.with_suffix(".html")
            keep.write_text(html, encoding="utf-8")
            logger.info("Kept HTML: %s", keep)

    verify_pdf(args.out, expected_pages=3)
    logger.info("Wrote %s (%.1f KB)", args.out, args.out.stat().st_size / 1024)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
