"""Draw the plug size finder: every plug preset of both tools at 1:1 on one page.

One 210 x 279 mm SVG (``docs/guides/plug-size-finder.svg``; fits A4 and US
Letter, the outline sheets' conventions) that a person prints at 100 % and
lays their plug on. Each preset is drawn as its plug seen lying flat on its
wide side: the body outline from the caliper measurements, the prongs (or
the USB-C metal tip) above it, the cord below it at its true width. The
outlines stand in two groups, the one-sided puller's plugs (2 prongs or a
USB-C tip) and the two-sided puller's (3 prongs), every prong face on one
line, each labelled with the preset to start with. A 50 x 50 mm calibration
square proves the print scale.

The preset numbers come from ``PLUG_PRESETS`` in
``scripts/generate_outline_sheets.py`` (kept in sync with both tool files);
this script adds only the shape between the measured stations (the head,
the strain relief, the prongs), each from the owner's caliper photos.
``tests/test_plug_finder.py`` checks that every outline is as long and as
wide as its preset and that every preset of both dropdowns is on the page.

``finder_text()`` returns the page's text equivalent (a table of every
outline), which the guides print beside the page.

Run from the repo root:

    python scripts/generate_plug_finder.py

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from shapely.geometry import Point, Polygon, box

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.generate_outline_sheets import (  # noqa: E402
    MODEL_VERSION,
    ONE_SIDED,
    PLUG_PRESETS,
    TWO_SIDED,
)

DEFAULT_OUT = PROJECT_ROOT / "docs" / "guides" / "plug-size-finder.svg"

FONT = "Helvetica, Arial, sans-serif"
PAGE_W, PAGE_H = 210.0, 279.0
TEAL = "#20b2aa"
GRAY = "#444444"
PRONG_FILL = "#9a9a9a"
CORD_FILL = "#d0d0d0"

# Where things sit on the page (mm, y down).
Y_FACE = 74.0        # every prong face on this line
CORD_RUN = 24.0      # how much cord is drawn below the plug
LABEL_Y = 160.0      # the first label line under every column
CAL = (12.0, 190.0)  # the calibration square's top-left corner
CAL_SIZE = 50.0

# NEMA 1-15 and 5-15 prongs, seen from the plug's wide side: each flat blade
# is 1.5 mm thick and 15.9 mm long, 12.7 mm apart center to center; the
# ground pin is 4.8 mm across and 18.8 mm long, centered between them. The
# USB-C metal tip is 8.3 mm wide and 6.6 mm long.
BLADE_T, BLADE_L, BLADE_PITCH = 1.5, 15.9, 12.7
PIN_D, PIN_L = 4.8, 18.8
USB_TIP_W, USB_TIP_L = 8.3, 6.6

TOOL_FILES = {
    ONE_SIDED: ("Plug_Puller_One_Sided_SingleFile.scad", "src/Plug_Puller_Parametric.scad"),
    TWO_SIDED: ("Plug_Puller_Two_Sided_SingleFile.scad", "src/Plug_Puller_Two_Sided.scad"),
}
TOOL_WORDS = {ONE_SIDED: "one-sided puller", TWO_SIDED: "two-sided puller"}
GROUP_HEADS = {
    ONE_SIDED: "2 prongs or a USB-C tip: the ONE-SIDED puller",
    TWO_SIDED: "3 prongs: the TWO-SIDED puller",
}


@dataclass(frozen=True)
class Shape:
    """One preset's plug, seen lying on its wide side.

    ``stations`` run from the prong face (0) to the cord end: (distance,
    full width); two stations at one distance make a step. ``prongs`` is
    "2", "3" or "usb-c"; ``cord`` the cord's width as it lies flat;
    ``cord_note`` how the cord reads; ``corner`` the outline's rounding."""

    key: str
    stations: Tuple[Tuple[float, float], ...]
    prongs: str
    cord: float
    cord_note: str
    corner: float = 1.0


# The plug outlines. Each preset's widest station is its prong-end width
# (the heavy-duty plug widens behind its prong face, and the two-sided
# preset takes the widest measurement), its last station its width at the
# cord end; the length is the last station's distance. Between them, the
# shape read off the owner's caliper photos (the lamp's taper and the
# standard plug's body shortened so the sections add up to the measured
# whole length). A plug whose widest point is a corner gets a small
# rounding, so the outline stays within 0.02 mm of its preset.
SHAPES: Dict[str, Shape] = {
    "usb-c-laptop-tip": Shape(
        "usb-c-laptop-tip", ((0.0, 10.25), (17.0, 10.25)), "usb-c", 6.1, "round", corner=1.6),
    "flat-2-prong": Shape(
        "flat-2-prong",
        ((0.0, 20.0), (15.2, 20.0), (15.2, 13.81), (32.5, 11.1)),
        "2", 7.0, "flat, 3.6 thick"),
    "wide-2-prong-appliance": Shape(
        "wide-2-prong-appliance", ((0.0, 34.0), (38.0, 34.0)), "2", 5.0, "round", corner=2.0),
    "standard-3-prong": Shape(
        "standard-3-prong",
        ((0.0, 24.66), (15.6, 23.85), (31.6, 17.1), (31.6, 13.6), (46.1, 13.6)),
        "3", 9.25, "round", corner=0.3),
    "heavy-duty-round": Shape(
        "heavy-duty-round",
        ((0.0, 25.25), (23.0, 26.56), (23.0, 22.0), (28.0, 22.0), (28.0, 24.5), (51.0, 24.5)),
        "3", 8.25, "round", corner=0.3),
}

# Column centers (mm): the one-sided group left, the two-sided group right.
COLUMNS: Dict[str, float] = {
    "usb-c-laptop-tip": 27.0,
    "flat-2-prong": 61.0,
    "wide-2-prong-appliance": 100.0,
    "standard-3-prong": 145.0,
    "heavy-duty-round": 183.0,
}
GROUP_SPANS = {ONE_SIDED: (10.0, 119.0), TWO_SIDED: (128.0, 200.0)}
COLUMN_W = 35.0
LABEL_CHARS = 22


def tool_of(key: str) -> str:
    files = PLUG_PRESETS[key]["files"]
    assert len(files) == 1, f"{key}: a preset belongs to exactly one tool file"
    return files[0]


def preset_numbers(key: str) -> Dict[str, float]:
    plug = PLUG_PRESETS[key]
    return dict(plug["measurements"][tool_of(key)])


def outline(shape: Shape) -> Polygon:
    """The body outline in plug coordinates (x across, y from the prong face
    toward the cord), corners rounded by ``shape.corner``."""
    right = [(w / 2, y) for y, w in shape.stations]
    left = [(-w / 2, y) for y, w in reversed(shape.stations)]
    poly = Polygon(right + left)
    r = shape.corner
    return poly.buffer(-r, join_style="round").buffer(r, join_style="round")


def prong_shapes(shape: Shape) -> List[Polygon]:
    if shape.prongs == "usb-c":
        r = 1.2
        tip = box(-USB_TIP_W / 2, -USB_TIP_L, USB_TIP_W / 2, 0.4)
        return [tip.buffer(-r, join_style="round").buffer(r, join_style="round")]
    blades = [box(x - BLADE_T / 2, -BLADE_L, x + BLADE_T / 2, 0.4) for x in (-BLADE_PITCH / 2, BLADE_PITCH / 2)]
    if shape.prongs == "3":
        tip_y = -PIN_L + PIN_D / 2
        pin = box(-PIN_D / 2, tip_y, PIN_D / 2, 0.4).union(Point(0.0, tip_y).buffer(PIN_D / 2, 32))
        return blades + [pin]
    return blades


def label_lines(key: str) -> List[str]:
    """The preset's dropdown label, wrapped so that " - " stays with the
    word after it."""
    words = PLUG_PRESETS[key]["customizer"].replace(" - ", " - ").split()
    lines: List[str] = []
    for word in words:
        if lines and len(lines[-1]) + 1 + len(word) <= LABEL_CHARS:
            lines[-1] += " " + word
        else:
            lines.append(word)
    return [line.replace(" ", " ") for line in lines]


def fmt(v: float) -> str:
    return f"{v:.2f}".rstrip("0").rstrip(".")


class Page:
    """A minimal SVG page, 1 user unit = 1 mm."""

    def __init__(self) -> None:
        self.parts: List[str] = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{PAGE_W:g}mm" height="{PAGE_H:g}mm" '
            f'viewBox="0 0 {PAGE_W:g} {PAGE_H:g}">',
            "<title>Plug Puller plug size finder</title>",
            f'<rect x="0" y="0" width="{PAGE_W:g}" height="{PAGE_H:g}" fill="white"/>',
        ]

    def text(self, x: float, y: float, s: str, size: float = 3.2, weight: str = "normal",
             anchor: str = "start", fill: str = "black") -> None:
        s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self.parts.append(f'<text x="{x:.3f}" y="{y:.3f}" font-family="{FONT}" font-size="{size:g}" '
                          f'font-weight="{weight}" text-anchor="{anchor}" fill="{fill}">{s}</text>')

    def line(self, x1: float, y1: float, x2: float, y2: float, w: float = 0.3,
             dash: Optional[str] = None, color: str = "black") -> None:
        dd = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" '
                          f'stroke="{color}" stroke-width="{w:g}"{dd}/>')

    def rect(self, x: float, y: float, w: float, h: float, sw: float = 0.4) -> None:
        self.parts.append(f'<rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" '
                          f'fill="none" stroke="black" stroke-width="{sw:g}"/>')

    def shape(self, poly: Polygon, dx: float, dy: float, fill: str, opacity: float = 1.0,
              sw: float = 0.35, cls: str = "") -> None:
        pts = " ".join(f"{x + dx:.3f},{y + dy:.3f}" for x, y in list(poly.exterior.coords)[:-1])
        c = f' class="{cls}"' if cls else ""
        self.parts.append(f'<polygon{c} points="{pts}" fill="{fill}" fill-opacity="{opacity:g}" '
                          f'stroke="black" stroke-width="{sw:g}" stroke-linejoin="round"/>')

    def raw(self, s: str) -> None:
        self.parts.append(s)

    def svg(self) -> str:
        return "\n".join(self.parts + ["</svg>"]) + "\n"


def draw_cord(page: Page, cx: float, y0: float, width: float) -> None:
    """The cord below the plug, its far end a zigzag break."""
    y1 = y0 + CORD_RUN
    hw = width / 2
    zig = []
    n = 4
    for i in range(n + 1):
        x = cx + hw - i * width / n
        zig.append((x, y1 + (1.2 if i % 2 else 0.0)))
    pts = [(cx - hw, y0), (cx + hw, y0)] + zig
    p = " ".join(f"{x:.3f},{y:.3f}" for x, y in pts)
    page.raw(f'<polygon class="cord" points="{p}" fill="{CORD_FILL}" stroke="black" stroke-width="0.3" '
             f'stroke-linejoin="round"/>')


def build_page() -> Page:
    page = Page()
    page.text(PAGE_W / 2, 13.0, "Plug Puller — Plug size finder", 6.0, "bold", "middle")
    page.text(PAGE_W / 2, 19.5, "Lay your plug flat on the outlines, prongs up. "
              "The closest outline names the preset to start with.", 3.2, anchor="middle")
    page.text(PAGE_W / 2, 24.5, "Print at 100 % (“Actual size”), never “fit to page”, "
              "and check the 50 mm square first.", 2.8, "bold", "middle")

    # The two groups: a bracket line, the rule, the file to open.
    for tool, (x0, x1) in GROUP_SPANS.items():
        page.line(x0, 32.0, x1, 32.0, 0.6)
        page.line(x0, 32.0, x0, 35.0, 0.6)
        page.line(x1, 32.0, x1, 35.0, 0.6)
        page.text((x0 + x1) / 2, 30.0, GROUP_HEADS[tool], 3.4, "bold", "middle")
        upload, desktop = TOOL_FILES[tool]
        page.text((x0 + x1) / 2, 39.0, f"Open {upload}", 2.6, anchor="middle", fill=GRAY)
        page.text((x0 + x1) / 2, 42.6, f"(desktop: {desktop})", 2.6, anchor="middle", fill=GRAY)

    # The prong-face line across every column.
    page.line(8.0, Y_FACE, 202.0, Y_FACE, 0.3, "2,1.2", GRAY)
    page.text(8.0, Y_FACE - 1.2, "prong face", 2.4, fill=GRAY)

    for key, shape in SHAPES.items():
        cx = COLUMNS[key]
        body = outline(shape)
        length = shape.stations[-1][0]
        for prong in prong_shapes(shape):
            page.shape(prong, cx, Y_FACE, PRONG_FILL, 1.0, 0.25, "prong")
        draw_cord(page, cx, Y_FACE + length - 0.2, shape.cord)
        page.shape(body, cx, Y_FACE, TEAL, 0.35, 0.4, f"plug plug-{key}")
        nums = preset_numbers(key)
        y = LABEL_Y
        for line in label_lines(key):
            page.text(cx, y, line, 3.0, "bold", "middle")
            y += 3.9
        y += 0.6
        page.text(cx, y, f"{fmt(nums['measure_plug_length'])} long, "
                  f"{fmt(nums['measure_plug_width_prong_end'])} wide", 2.6, anchor="middle")
        y += 3.4
        page.text(cx, y, f"cord {fmt(shape.cord)} ({shape.cord_note})", 2.6, anchor="middle")
        y += 3.4
        page.text(cx, y, TOOL_WORDS[tool_of(key)], 2.6, anchor="middle", fill=GRAY)

    # The calibration square and the how-to.
    x, y = CAL
    page.rect(x, y, CAL_SIZE, CAL_SIZE, 0.5)
    page.text(x + CAL_SIZE / 2, y + 22.0, "CALIBRATION", 3.4, "bold", "middle")
    page.text(x + CAL_SIZE / 2, y + 27.0, "50 × 50 mm", 3.4, anchor="middle")
    page.text(x + CAL_SIZE / 2, y + 33.0, "Not 50 mm? Re-print", 2.6, anchor="middle", fill=GRAY)
    page.text(x + CAL_SIZE / 2, y + 36.5, "at 100 %.", 2.6, anchor="middle", fill=GRAY)
    steps = [
        "1. Measure the square with a ruler: it must be 50 × 50 mm.",
        "2. Count your plug's prongs. 2 prongs or a USB-C tip: the left",
        "    group. 3 prongs: the right group.",
        "3. Lay the plug on its wide side, prongs up, the prong face on the",
        "    dashed line. Slide it from outline to outline in its group.",
        "4. The closest outline names the preset: open that tool's file",
        "    and pick the preset in Step 1.",
        "5. Between two outlines, or none close? Fill in the measuring",
        "    form and type your own numbers instead.",
    ]
    ty = y + 4.0
    page.text(72.0, ty, "How to use this page", 3.6, "bold")
    ty += 6.0
    for s in steps:
        page.text(72.0, ty, s, 3.0)
        ty += 4.6
    page.text(PAGE_W / 2, 274.5, f"openscad-plug-puller v{MODEL_VERSION} · plug size finder · scale 1:1 · "
              "works on A4 and US Letter", 2.4, anchor="middle", fill=GRAY)
    return page


def finder_rows() -> List[Dict[str, str]]:
    """One row per outline, in page order, for the text equivalent."""
    rows = []
    for key, shape in SHAPES.items():
        nums = preset_numbers(key)
        rows.append({
            "preset": PLUG_PRESETS[key]["customizer"],
            "tool": TOOL_WORDS[tool_of(key)],
            "prongs": {"2": "2", "3": "3", "usb-c": "USB-C metal tip"}[shape.prongs],
            "length": fmt(nums["measure_plug_length"]),
            "prong_end": fmt(nums["measure_plug_width_prong_end"]),
            "cord_end": fmt(nums["measure_plug_width_cord_end"]),
            "cord": f"{fmt(shape.cord)} ({shape.cord_note})",
        })
    return rows


def finder_text() -> str:
    """The page as text: what it shows, then a table of every outline."""
    out = [
        "The page shows five plugs at true size, each lying on its wide side with its prongs up and every prong "
        "face on one dashed line, the cord drawn below each at its true width. The left group, under \"2 prongs "
        "or a USB-C tip: the ONE-SIDED puller\", holds the one-sided puller's presets; the right group, under "
        "\"3 prongs: the TWO-SIDED puller\", the two-sided puller's. Each outline is labelled with the preset to "
        "pick. A 50 by 50 mm calibration square sits at the bottom left, the five steps below beside it.",
        "",
        "| Preset to pick | Tool file | Prongs | Length (mm) | Width at the prong end (mm) | "
        "Width at the cord end (mm) | Cord (mm) |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in finder_rows():
        out.append(f"| {r['preset']} | {r['tool']} | {r['prongs']} | {r['length']} | {r['prong_end']} | "
                   f"{r['cord_end']} | {r['cord']} |")
    return "\n".join(out)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(build_page().svg(), encoding="utf-8", newline="\n")
    print(f"Wrote {args.out} ({len(SHAPES)} plug outlines at 1:1)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
