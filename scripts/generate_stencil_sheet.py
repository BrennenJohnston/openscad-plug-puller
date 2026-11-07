"""Generate the 1:1 paper measuring-stencil sheet.

The paper alternative to the 3D-printable ``Measuring_Stencil.scad``'s
ruler and finger cards: one 210 x 279 mm SVG page (fits A4 and US Letter,
the outline sheets' conventions), printed at true size as one of the last
pages of each tool's quick start and full guide PDFs. It carries:

* the 50 x 50 mm calibration square,
* a 100 mm ruler (R1),
* the 18 finger-sizing circles (F1 / F2).

The paper stand-in for the P plug cards is the plug size finder page
(``scripts/generate_plug_finder.py``), which shows every preset of both
tools at 1:1 on one page.

Run from the repo root:

    python scripts/generate_stencil_sheet.py

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = PROJECT_ROOT / "docs" / "guides" / "stencil-sheet.svg"

logger = logging.getLogger(__name__)

FONT = "Helvetica, Arial, sans-serif"
PAGE_W, PAGE_H = 210.0, 279.0
DASH_CUT = "1.6,1.1"

# Finger circles in the same groups as the 3D stencil's F1 / F2 cards
# (F1 = Ø15-25, F2 = Ø26-32).
FINGER_ROWS = [
    ("F1", [15, 16, 17, 18, 19, 20]),
    ("F1", [21, 22, 23, 24, 25]),
    ("F2", [26, 27, 28, 29]),
    ("F2", [30, 31, 32]),
]


class Svg:
    """Minimal SVG builder — 1 user unit == 1 mm (same as the templates)."""

    def __init__(self) -> None:
        self.parts: List[str] = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{PAGE_W:g}mm" '
            f'height="{PAGE_H:g}mm" viewBox="0 0 {PAGE_W:g} {PAGE_H:g}">',
            f'<rect x="0" y="0" width="{PAGE_W:g}" height="{PAGE_H:g}" fill="white"/>',
        ]

    def text(
        self,
        x: float,
        y: float,
        s: str,
        size: float = 3.2,
        weight: str = "normal",
        anchor: str = "start",
        fill: str = "black",
    ) -> None:
        s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self.parts.append(
            f'<text x="{x:.3f}" y="{y:.3f}" font-family="{FONT}" '
            f'font-size="{size:g}" font-weight="{weight}" '
            f'text-anchor="{anchor}" fill="{fill}">{s}</text>'
        )

    def line(
        self, x1: float, y1: float, x2: float, y2: float, w: float = 0.3
    ) -> None:
        self.parts.append(
            f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" '
            f'stroke="black" stroke-width="{w:g}"/>'
        )

    def rect(self, x: float, y: float, w: float, h: float, sw: float = 0.4) -> None:
        self.parts.append(
            f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" '
            f'fill="none" stroke="black" stroke-width="{sw:g}"/>'
        )

    def circle(
        self, cx: float, cy: float, d: float, w: float = 0.35,
        dash: Optional[str] = None,
    ) -> None:
        dd = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(
            f'<circle cx="{cx:.3f}" cy="{cy:.3f}" r="{d / 2:.3f}" fill="none" '
            f'stroke="black" stroke-width="{w:g}"{dd}/>'
        )

    def polygon(
        self, pts: List[tuple], w: float = 0.4, dash: Optional[str] = None
    ) -> None:
        p = " ".join(f"{x:.3f},{y:.3f}" for x, y in pts)
        dd = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(
            f'<polygon points="{p}" fill="none" stroke="black" '
            f'stroke-width="{w:g}" stroke-linejoin="round"{dd}/>'
        )

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(self.parts + ["</svg>"]) + "\n", encoding="utf-8")


def draw_header(svg: Svg) -> None:
    svg.text(PAGE_W / 2, 14, "Plug Puller — Measuring Stencil Sheet", 5.5,
             "bold", "middle")
    svg.text(
        PAGE_W / 2, 19.5,
        "Print at 100% scale / “Actual size” — never “fit to page”. "
        "Check the calibration square before trusting anything on this sheet.",
        2.8, anchor="middle",
    )
    # Calibration square (the outline sheets' convention).
    svg.rect(14, 26, 50, 50)
    svg.text(39, 49.5, "CALIBRATION", 3.4, "bold", "middle")
    svg.text(39, 54.5, "50 × 50 mm", 3.4, anchor="middle")
    svg.text(72, 32, "1. Measure this square with a ruler.", 3.0)
    svg.text(72, 36.5, "It must be exactly 50 × 50 mm — if not, your", 3.0)
    svg.text(72, 41, "print was scaled: re-print at 100%.", 3.0)
    svg.text(72, 47.5, "Plug outlines: the plug size finder page", 2.8,
             fill="#444444")
    svg.text(72, 52, "Works on A4 and US Letter paper.", 2.8, fill="#444444")


def draw_ruler(svg: Svg, x0: float, y0: float, length: float = 100.0) -> None:
    """R1 — a horizontal mm ruler with the baseline at y0."""
    svg.text(x0, y0 - 5.5, "R1 — ruler (mm): plug length, widths, thicknesses, hand width",
             3.0, "bold")
    svg.line(x0, y0, x0 + length, y0, 0.4)
    for mm in range(0, int(length) + 1):
        tick = 6.0 if mm % 10 == 0 else 4.5 if mm % 5 == 0 else 3.0
        w = 0.3 if mm % 5 == 0 else 0.2
        svg.line(x0 + mm, y0, x0 + mm, y0 + tick, w)
        if mm % 10 == 0:
            svg.text(x0 + mm, y0 + 9.5, str(mm), 2.6, anchor="middle")


def draw_finger_circles(svg: Svg, y_header: float, row_centers: List[float]) -> None:
    svg.text(
        14, y_header,
        "2. F1 / F2 — finger circles: smallest circle your middle finger "
        "passes through, minus 5 = finger width.",
        3.0, "bold",
    )
    for (label, dias), cy in zip(FINGER_ROWS, row_centers):
        total = sum(dias) + 5.0 * (len(dias) - 1)
        x = (PAGE_W - total) / 2
        for d in dias:
            cx = x + d / 2
            svg.circle(cx, cy, d, 0.35, DASH_CUT)
            svg.text(cx, cy + 1.1, str(d), 2.8, "bold", "middle")
            x += d + 5.0
        row_max = max(dias)
        svg.text(14, cy + 1.1, label, 3.4, "bold", fill="#444444")
        assert cy + row_max / 2 < PAGE_H - 6, "finger row overflows the page"


def build_sheet() -> Svg:
    """The page: the header, the ruler and the finger circles."""
    svg = Svg()
    draw_header(svg)
    # Ruler in the header row, right of the calibration square.
    draw_ruler(svg, x0=76, y0=64)
    # Finger circles: rows sized so the largest circle of each row clears
    # the next row and the footer.
    draw_finger_circles(svg, y_header=90, row_centers=[106, 136, 172, 212])
    svg.text(
        PAGE_W / 2, 274.5,
        "openscad-plug-puller · measuring stencil sheet · scale 1:1 · "
        "prefer plastic? print stl/Measuring-Stencil/",
        2.4, anchor="middle", fill="#444444",
    )
    return svg


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    build_sheet().save(args.out)
    logger.info("Wrote %s (the calibration square, the ruler and the finger circles)", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
