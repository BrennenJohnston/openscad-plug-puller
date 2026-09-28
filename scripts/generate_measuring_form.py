#!/usr/bin/env python3
"""Draw the two measuring form sheets and their text twins.

One 210 × 279 mm SVG per tool under ``docs/guides/<tool>/measuring-form.svg``:
the printed form a person fills in before opening the Customizer. The left
column has one row per Step dial in Customizer order, read from the tool's
parameter mapping (the name, the plain title from ``dial_catalog.json``, the
default and a blank for a number, tick boxes for a dropdown). The right half
is a schematic plug drawn from the tool's defaults at 1.5:1, a knuckle bar and
a strap bar; every row that asks for a number gets a straight leader to a red
dimension line on the feature its catalog ``measure.anchor`` names, the row's
number in a red circle at the line. The page builder is the outline sheets'
``Sheet`` class (its dimension lines and leaders); the halo texts are drawn as
a separate white text underneath so that every SVG rasterizer shows them.

The text twin ``measuring-form.md`` is written from the same data: the rows
as a table, then what the sheet shows, one line per numbered arrow.

The script checks its own drawing: no two leaders cross, and no leader runs
through a drawn shape; it fails loudly otherwise.

Usage:
    python scripts/generate_measuring_form.py            # both tools
    python scripts/generate_measuring_form.py --tool two-sided

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.generate_outline_sheets import PAGE_H, PAGE_W, Sheet, fmt  # noqa: E402

MAPPINGS = {
    "one-sided": PROJECT_ROOT / "parameter_mapping.json",
    "two-sided": PROJECT_ROOT / "parameter_mapping_two_sided.json",
}
CATALOG = PROJECT_ROOT / "dial_catalog.json"
OUT_DIRS = {
    "one-sided": PROJECT_ROOT / "docs" / "guides" / "one-sided",
    "two-sided": PROJECT_ROOT / "docs" / "guides" / "two-sided",
}
TOOL_WORDS = {"one-sided": "one-sided puller", "two-sided": "two-sided puller"}
QUIZ_ANCHORS = {"wall_plate", "plug_sides"}

FONT = "Helvetica, Arial, sans-serif"
MONO = "Consolas, Menlo, monospace"
RED = "#d81b1b"
TEAL = "#20b2aa"
TEAL_OPACITY = 0.45
GRAY = "#555555"

# The left column: rows of 12 mm from y = 34; a dropdown whose boxes need more
# than one line grows by LINE_H per extra line.
COL_X0, COL_X1 = 12.0, 96.0
CONTENT_X = 19.0
ROW_TOP = 34.0
ROW_H = 12.0
LINE_H = 3.2
BOX = 3.0
OPTION_SIZE = 2.4
NAME_SIZE = 3.0
TITLE_SIZE = 2.8
BLANK_LEN = 28.0
LEADER_X = COL_X1 + 2.0

# The right half: the schematic in page millimetres.
SCALE = 1.5
SCH_X0 = 110.0
CIRCLE_D = 3.0
FOOTER_Y = 262.0
HEADER_LINE = "Measure in mm. Fill in the blanks top to bottom, then type them into the Customizer in the same order."
TWIN_INTRO = ("Everything on this sheet is in mm. Fill in the blanks top to bottom, then type the numbers into the "
              "Customizer in the same order. Print the sheet at 100 % and check the 50 mm bar with a ruler.")


def text_width(s: str, size: float, mono: bool = False) -> float:
    """A safe estimate: Helvetica averages half an em per character, Consolas 0.6."""
    return len(s) * size * (0.6 if mono else 0.52)


# ---------------------------------------------------------------------------
# The page builder
# ---------------------------------------------------------------------------


class FormSheet(Sheet):
    """The outline sheets' Sheet with a colour switch for the dimension
    helpers, halo texts drawn as a separate white text underneath (PyMuPDF
    ignores ``paint-order``), circles, rounded rectangles and filled shapes."""

    def __init__(self) -> None:
        super().__init__()
        self.color = "black"
        self.set_model_frame(0.0, PAGE_H)

    def text(self, x: float, y: float, s: str, size: float = 3.2, weight: str = "normal",
             anchor: str = "start", fill: str = "black", halo: bool = False,
             family: str = FONT, attrs: str = "") -> None:
        if not s:
            return
        esc = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        head = (f'<text x="{x:.3f}" y="{y:.3f}" font-family="{family}" font-size="{size:g}" '
                f'font-weight="{weight}" text-anchor="{anchor}"')
        if halo:
            self.parts.append(f'{head} fill="white" stroke="white" stroke-width="0.9" stroke-linejoin="round">{esc}</text>')
        if fill == "black" and self.color != "black":
            fill = self.color
        self.parts.append(f'{head} fill="{fill}"{attrs}>{esc}</text>')

    def line(self, x1: float, y1: float, x2: float, y2: float, w: float = 0.3,
             dash: Optional[str] = None, color: str = "black") -> None:
        if color == "black":
            color = self.color
        super().line(x1, y1, x2, y2, w, dash, color)

    def _arrow(self, x: float, y: float, angle_deg: float) -> None:
        a = math.radians(angle_deg)
        ln, hw = 2.4, 0.75
        bx, by = x - ln * math.cos(a), y - ln * math.sin(a)
        px = (-hw * math.sin(a), hw * math.cos(a))
        p = (f"{x:.3f},{y:.3f} {bx + px[0]:.3f},{by + px[1]:.3f} "
             f"{bx - px[0]:.3f},{by - px[1]:.3f}")
        self.parts.append(f'<polygon points="{p}" fill="{self.color}"/>')

    def circle(self, cx: float, cy: float, d: float, w: float = 0.35, color: str = "black",
               fill: str = "none", opacity: Optional[float] = None) -> None:
        op = f' fill-opacity="{opacity:g}"' if opacity is not None else ""
        self.parts.append(f'<circle cx="{cx:.3f}" cy="{cy:.3f}" r="{d / 2:.3f}" fill="{fill}"{op} '
                          f'stroke="{color}" stroke-width="{w:g}"/>')

    def rrect(self, x: float, y: float, w: float, h: float, r: float, sw: float = 0.35,
              color: str = "black", fill: str = "none", opacity: Optional[float] = None) -> None:
        op = f' fill-opacity="{opacity:g}"' if opacity is not None else ""
        self.parts.append(f'<rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" rx="{r:g}" '
                          f'fill="{fill}"{op} stroke="{color}" stroke-width="{sw:g}"/>')

    def polygon_fill(self, pts: Sequence[Tuple[float, float]], fill: str, opacity: float,
                     sw: float = 0.35, color: str = "black") -> None:
        p = " ".join(f"{x:.3f},{y:.3f}" for x, y in pts)
        self.parts.append(f'<polygon points="{p}" fill="{fill}" fill-opacity="{opacity:g}" '
                          f'stroke="{color}" stroke-width="{sw:g}" stroke-linejoin="round"/>')

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(self.parts + ["</svg>"]) + "\n", encoding="utf-8", newline="\n")

    def open_group(self, tag: str) -> None:
        self.parts.append(tag)

    def close_group(self) -> None:
        self.parts.append("</g>")

    # Dimension helpers in page coordinates (y down); the Sheet's own take
    # model coordinates with y up, mapped by the frame set in __init__.
    def dim_h_page(self, x1: float, x2: float, y_dim: float, y_obj: float) -> None:
        self.dim_h(x1, x2, PAGE_H - y_dim, PAGE_H - y_obj, "")

    def dim_v_page(self, y1: float, y2: float, x_dim: float, x_obj: float) -> None:
        self.dim_v(PAGE_H - y1, PAGE_H - y2, x_dim, x_obj, "")


# ---------------------------------------------------------------------------
# The data
# ---------------------------------------------------------------------------


def load_step_rows(tool: str) -> List[Dict[str, Any]]:
    mapping = json.loads(MAPPINGS[tool].read_text(encoding="utf-8"))
    return [r for r in mapping["parameters"] if r["section"].startswith("Step")]


def load_catalog() -> Dict[Tuple[str, str], Dict[str, Any]]:
    rows = json.loads(CATALOG.read_text(encoding="utf-8"))
    return {(r["file"], r["name"]): r for r in rows}


def default_text(row: Dict[str, Any]) -> str:
    if row["type"] == "enum":
        return str(row["default"])
    if row["type"] == "boolean":
        return "on" if row["default"] else "off"
    return f"{fmt(row['default'])} {row.get('unit') or 'mm'}"


def option_lines(options: Sequence[str]) -> List[List[str]]:
    """Greedy wrap of a dropdown's tick boxes into lines that fit the column."""
    limit = COL_X1 - CONTENT_X
    lines: List[List[str]] = [[]]
    used = 0.0
    for opt in options:
        w = BOX + 1.0 + text_width(opt, OPTION_SIZE) + 3.0
        if lines[-1] and used + w > limit:
            lines.append([])
            used = 0.0
        lines[-1].append(opt)
        used += w
    return lines


def row_height(row: Dict[str, Any]) -> float:
    if row["type"] == "enum":
        return ROW_H + (len(option_lines(row["values"])) - 1) * LINE_H
    return ROW_H


# ---------------------------------------------------------------------------
# The left column
# ---------------------------------------------------------------------------


def draw_row(sh: FormSheet, k: int, y0: float, row: Dict[str, Any], title: str,
             measure: Optional[Dict[str, Any]]) -> Optional[Tuple[float, float]]:
    """Draw one row at its top y0; return the leader's start point for a
    number row with a number anchor, else None."""
    sh.circle(COL_X0 + 3.0, y0 + 4.4, 4.0, 0.35)
    sh.text(COL_X0 + 3.0, y0 + 5.3, str(k), 2.6, "bold", "middle")
    sh.text(CONTENT_X, y0 + 3.6, row["openscad_name"], NAME_SIZE, family=MONO,
            attrs=f' class="dial" data-row="{k}" data-default="{default_text(row)}"')
    sh.text(CONTENT_X, y0 + 6.9, title, TITLE_SIZE)
    if row["type"] == "enum":
        y = y0 + 10.4
        for line in option_lines(row["values"]):
            x = CONTENT_X
            for opt in line:
                is_default = opt == row["default"]
                sh.rect(x, y - 2.7, BOX, BOX, 0.3)
                if is_default:
                    sh.circle(x + BOX / 2, y - 2.7 + BOX / 2, 1.3, 0.1, fill="black")
                sh.text(x + BOX + 1.0, y - 0.35, opt, OPTION_SIZE, "bold" if is_default else "normal")
                x += BOX + 1.0 + text_width(opt, OPTION_SIZE) + 3.0
            y += LINE_H
        return None
    if row["type"] == "boolean":
        y = y0 + 10.4
        sh.rect(CONTENT_X, y - 2.7, BOX, BOX, 0.3)
        if row["default"]:
            sh.circle(CONTENT_X + BOX / 2, y - 2.7 + BOX / 2, 1.3, 0.1, fill="black")
        sh.text(CONTENT_X + BOX + 1.0, y - 0.35, "leave on", OPTION_SIZE, "bold")
        return None
    y = y0 + 10.4
    label = f"default {default_text(row)} →"
    sh.text(CONTENT_X, y, label, TITLE_SIZE)
    x_blank = CONTENT_X + text_width(label, TITLE_SIZE) + 1.5
    sh.line(x_blank, y + 0.4, x_blank + BLANK_LEN, y + 0.4, 0.3)
    sh.text(x_blank + BLANK_LEN + 1.5, y, row.get("unit") or "mm", TITLE_SIZE)
    if measure and measure.get("stencil"):
        sh.text(x_blank + BLANK_LEN + 9.0, y, f"card {measure['stencil']}", 2.4, fill=GRAY)
    if measure and measure["anchor"] not in QUIZ_ANCHORS:
        return (LEADER_X, y - 1.0)
    return None


# ---------------------------------------------------------------------------
# The schematic
# ---------------------------------------------------------------------------


class Schematic:
    """The right half: the shapes (for the crossing check), the dimension
    lines per anchor with the point where the row's circle sits, and the
    words the twin uses for each arrow."""

    def __init__(self, sh: FormSheet, tool: str, defaults: Dict[str, Any]) -> None:
        self.sh = sh
        self.tool = tool
        self.d = defaults
        self.shapes: List[Tuple[float, float, float, float]] = []
        self.circles: Dict[str, Tuple[float, float]] = {}
        self.tails: Dict[str, Tuple[float, float, float, float]] = {}
        self.words: Dict[str, str] = {}
        self.dims: Dict[str, Any] = {}

    def body(self, x0: float, y0: float, x1: float, y1: float) -> None:
        self.shapes.append((x0, y0, x1, y1))
        self.sh.polygon_fill([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], TEAL, TEAL_OPACITY)

    def draw(self) -> None:
        d, sh = self.d, self.sh
        L = d["measure_plug_length"] * SCALE
        W = d["measure_plug_width_prong_end"] * SCALE
        cord = d["measure_cord_thickness"] * SCALE
        x0, x1 = SCH_X0, SCH_X0 + L
        # The top view, the plug lying with its prong end at the left against the wall plate.
        ty0, ty1 = 46.0, 46.0 + W
        self.body(x0, ty0, x1, ty1)
        cy = (ty0 + ty1) / 2
        self.body(x1, cy - cord / 2, x1 + 8.0, cy + cord / 2)
        sh.line(x0, ty0 - 3.0, x0, ty1 + 1.5, 0.5)
        sh.text(x0 - 1.2, ty1 + 4.6, "wall plate", 2.4, anchor="start", fill=GRAY)
        caption = "top view, widths across the plates" if self.tool == "two-sided" else "top view"
        sh.text((x0 + x1) / 2, ty0 - 8.4, caption, 2.6, "bold", "middle", fill=GRAY)
        self.dims["plug_length"] = ("h", x0, x1, ty0 - 6.0, ty0)
        self.circles["plug_length"] = (x0 - 3.5, ty0 - 6.0)
        self.words["plug_length"] = "the plug's length on the top view, from the wall plate to the plug's back end"
        self.dims["plug_width_prong_end"] = ("v", ty0, ty1, x0 - 5.0, x0)
        self.circles["plug_width_prong_end"] = (x0 - 5.0, ty0)
        self.words["plug_width_prong_end"] = "the plug's width at the prong end, the left edge of the top view"
        wc_x = x1 + 12.0
        self.dims["plug_width_cord_end"] = ("v", ty0, ty1, wc_x, x1)
        self.circles["plug_width_cord_end"] = (wc_x, ty1 + 8.5)
        self.tails["plug_width_cord_end"] = (wc_x, ty1, wc_x, ty1 + 7.0)
        self.words["plug_width_cord_end"] = "the plug's width at the cord end, the right edge of the top view where the cord leaves"
        if "measure_plug_thickness_prong_end" in d:
            # The side view stands with its prong end up, to the right, below the top view.
            T = d["measure_plug_thickness_prong_end"] * SCALE
            sx0, sy0 = 165.0, 104.0
            sx1, sy1 = sx0 + T, sy0 + L
            self.body(sx0, sy0, sx1, sy1)
            sh.line(sx0 - 3.0, sy0, sx1 + 3.0, sy0, 0.5)
            sh.text(sx1 + 3.5, sy0 + 0.8, "wall plate", 2.4, fill=GRAY)
            sh.text((sx0 + sx1) / 2, sy0 - 8.0, "side view", 2.6, "bold", "middle", fill=GRAY)
            self.dims["plug_thickness_prong_end"] = ("h", sx0, sx1, sy0 - 5.0, sy0)
            self.circles["plug_thickness_prong_end"] = (sx0 - 3.2, sy0 - 5.0)
            self.words["plug_thickness_prong_end"] = "the plug's thickness at the prong end, the top of the side view"
            self.dims["plug_thickness_cord_end"] = ("h", sx0, sx1, sy1 + 5.0, sy1)
            self.circles["plug_thickness_cord_end"] = (sx0 - 3.2, sy1 + 5.0)
            self.words["plug_thickness_cord_end"] = "the plug's thickness at the cord end, the bottom of the side view"
            cord_c = (190.0, 158.0)
            bar_y = 174.0
        else:
            cord_c = (190.0, 100.0)
            bar_y = 120.0
        # The cord's end, a circle.
        cx, cyc = cord_c
        sh.circle(cx, cyc, cord, 0.35, fill=TEAL, opacity=TEAL_OPACITY)
        self.shapes.append((cx - cord / 2, cyc - cord / 2, cx + cord / 2, cyc + cord / 2))
        sh.text(cx, cyc - cord / 2 - 2.0, "cord end", 2.4, anchor="middle", fill=GRAY)
        self.dims["cord"] = ("h", cx - cord / 2, cx + cord / 2, cyc + cord / 2 + 3.0, cyc + cord / 2)
        self.circles["cord"] = (cx - cord / 2 - 9.5, cyc + cord / 2 + 3.0)
        self.words["cord"] = "the cord's thickness on the small circle, the cord seen end on"
        # The knuckle bar at 1:1: four knuckles, one 20 mm wide, 85 mm across.
        bx0, bw, kw, bh = SCH_X0, 85.0, 20.0, 22.0
        gap = (bw - 4 * kw) / 3
        for i in range(4):
            kx = bx0 + i * (kw + gap)
            sh.rrect(kx, bar_y, kw, bh, 5.0)
        self.shapes.append((bx0, bar_y, bx0 + bw, bar_y + bh))
        sh.text(bx0 + bw, bar_y - 1.5, "four knuckles, 1:1", 2.4, anchor="end", fill=GRAY)
        self.dims["finger_width"] = ("h", bx0, bx0 + kw, bar_y - 4.0, bar_y)
        self.circles["finger_width"] = (bx0 - 4.0, bar_y - 4.0)
        self.words["finger_width"] = "one knuckle of the knuckle bar, drawn 20 mm wide at 1:1"
        self.dims["hand_width"] = ("h", bx0, bx0 + bw, bar_y + bh + 5.0, bar_y + bh)
        self.circles["hand_width"] = (bx0 - 4.0, bar_y + bh + 5.0)
        self.words["hand_width"] = "the whole knuckle bar, four knuckles 85 mm across at 1:1"
        # The strap bar: a 40 × 15 mm rounded rectangle, its width the vertical way.
        sy = bar_y + bh + 18.0
        sh.rrect(bx0, sy, 40.0, 15.0, 3.0)
        self.shapes.append((bx0, sy, bx0 + 40.0, sy + 15.0))
        sh.text(bx0 + 20.0, sy + 8.4, "strap", 2.4, anchor="middle", fill=GRAY)
        self.dims["strap_width"] = ("v", sy, sy + 15.0, bx0 - 5.0, bx0)
        self.circles["strap_width"] = (bx0 - 5.0, sy)
        self.words["strap_width"] = "the strap bar's width, a 40 by 15 mm bar at 1:1"

    def draw_dimension(self, anchor: str, k: int) -> None:
        sh = self.sh
        kind, a, b, at, obj = self.dims[anchor]
        sh.open_group(f'<g class="dimension" data-row="{k}">')
        sh.color = RED
        if kind == "h":
            sh.dim_h_page(a, b, at, obj)
        else:
            sh.dim_v_page(a, b, at, obj)
        if anchor in self.tails:
            x1, y1, x2, y2 = self.tails[anchor]
            sh.line(x1, y1, x2, y2, 0.25)
        cx, cy = self.circles[anchor]
        sh.circle(cx, cy, CIRCLE_D, 0.35, RED, fill="white")
        sh.text(cx, cy + 0.85, str(k), 2.4, "bold", "middle", fill=RED)
        sh.color = "black"
        sh.close_group()


# ---------------------------------------------------------------------------
# Geometry checks
# ---------------------------------------------------------------------------


def _orient(px: float, py: float, qx: float, qy: float, rx: float, ry: float) -> int:
    v = (qx - px) * (ry - py) - (qy - py) * (rx - px)
    return 0 if abs(v) < 1e-9 else (1 if v > 0 else -1)


def segments_cross(a: Tuple[float, float, float, float], b: Tuple[float, float, float, float]) -> bool:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    o1 = _orient(ax1, ay1, ax2, ay2, bx1, by1)
    o2 = _orient(ax1, ay1, ax2, ay2, bx2, by2)
    o3 = _orient(bx1, by1, bx2, by2, ax1, ay1)
    o4 = _orient(bx1, by1, bx2, by2, ax2, ay2)
    return o1 != o2 and o3 != o4


def segment_hits_box(seg: Tuple[float, float, float, float], box: Tuple[float, float, float, float]) -> bool:
    x0, y0, x1, y1 = box
    sx1, sy1, sx2, sy2 = seg
    if x0 < sx1 < x1 and y0 < sy1 < y1 or x0 < sx2 < x1 and y0 < sy2 < y1:
        return True
    edges = [(x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)]
    return any(segments_cross(seg, e) for e in edges)


# ---------------------------------------------------------------------------
# One sheet
# ---------------------------------------------------------------------------


def first_sentence(how: str) -> str:
    return how.split(". ")[0].rstrip(".") + "."


def cell_text(row: Dict[str, Any], title: str, measure: Optional[Dict[str, Any]]) -> str:
    if measure is None:
        return f"{title}: pick one" if row["type"] == "enum" else f"{title}: leave on"
    if measure["anchor"] == "wall_plate":
        return "Look at the outlet cover plate and pick the closest match."
    sentence = first_sentence(measure["how"])
    words = sentence.split()
    if len(words) > 22:
        sentence = " ".join(words[:20]) + "."
    return sentence


def build_sheet(tool: str, catalog: Dict[Tuple[str, str], Dict[str, Any]]) -> Tuple[FormSheet, str, Dict[str, Any]]:
    rows = load_step_rows(tool)
    defaults = {r["openscad_name"]: r["default"] for r in rows}
    words = TOOL_WORDS[tool]
    sh = FormSheet()
    # Header
    sh.text(PAGE_W / 2, 12.0, f"Plug Puller — Measuring form, {words}", 5.0, "bold", "middle")
    sh.text(PAGE_W / 2, 18.0, HEADER_LINE, 2.8, anchor="middle")
    sh.text(146.0, 24.6, "Print at 100 %", 2.8, "bold", "end")
    sh.line(150.0, 23.8, 200.0, 23.8, 0.35)
    sh.line(150.0, 22.0, 150.0, 25.6, 0.35)
    sh.line(200.0, 22.0, 200.0, 25.6, 0.35)
    sh.text(175.0, 21.6, "50 mm", 2.6, anchor="middle")
    # The schematic first, so the dimension lines exist before the leaders.
    schematic = Schematic(sh, tool, defaults)
    schematic.draw()
    # The rows
    starts: Dict[int, Tuple[float, float]] = {}
    anchors: Dict[int, str] = {}
    y = ROW_TOP
    table: List[Dict[str, Any]] = []
    for k, row in enumerate(rows, start=1):
        cat = catalog[(tool, row["openscad_name"])]
        measure = cat["measure"]
        start = draw_row(sh, k, y, row, cat["title"], measure)
        if start is not None:
            starts[k] = start
            anchors[k] = measure["anchor"]
        table.append({"k": k, "row": row, "title": cat["title"], "measure": measure})
        y += row_height(row)
    rows_bottom = y
    assert rows_bottom < FOOTER_Y - 6.0, f"{tool}: the rows run to {rows_bottom:.1f} mm, past the footer"
    # The dimension lines and the leaders
    leaders: Dict[int, Tuple[float, float, float, float]] = {}
    for k, anchor in anchors.items():
        schematic.draw_dimension(anchor, k)
        (x1, y1), (cx, cy) = starts[k], schematic.circles[anchor]
        dx, dy = cx - x1, cy - y1
        n = math.hypot(dx, dy)
        x2, y2 = cx - dx / n * (CIRCLE_D / 2 + 0.3), cy - dy / n * (CIRCLE_D / 2 + 0.3)
        sh.open_group(f'<g class="leader" data-row="{k}">')
        sh.line(x1, y1, x2, y2, 0.35)
        sh.close_group()
        leaders[k] = (x1, y1, x2, y2)
    keys = sorted(leaders)
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            assert not segments_cross(leaders[a], leaders[b]), f"{tool}: leaders {a} and {b} cross"
    for k, seg in leaders.items():
        for box in schematic.shapes:
            assert not segment_hits_box(seg, box), f"{tool}: leader {k} runs through a drawn shape {box}"
    # Footer
    sh.text(PAGE_W / 2, FOOTER_Y, f"openscad-plug-puller · measuring form · {words} · fill in, then type in order",
            2.4, anchor="middle", fill=GRAY)
    twin = build_twin(tool, table, anchors, schematic)
    summary = {"rows": len(rows), "rows_bottom": round(rows_bottom, 1), "leaders": len(leaders),
               "circles": {k: schematic.circles[a] for k, a in anchors.items()}}
    return sh, twin, summary


def build_twin(tool: str, table: List[Dict[str, Any]], anchors: Dict[int, str], schematic: Schematic) -> str:
    words = TOOL_WORDS[tool]
    out = [f"# Measuring form, {words}", "", TWIN_INTRO, "",
           "The printable sheet is [measuring-form.svg](measuring-form.svg); this page is its text twin.", "",
           "| # | Customizer name | What you measure | Default | Yours |", "|---|---|---|---|---|"]
    for t in table:
        out.append(f"| {t['k']} | `{t['row']['openscad_name']}` | {cell_text(t['row'], t['title'], t['measure'])} | "
                   f"{default_text(t['row'])} | ________ |")
    out += ["", "## What the sheet shows", "",
            f"The left column is the numbered list above, one row per dial in the Customizer's Step order, each with the "
            f"dial's name, its plain title and either a blank after the default or a tick box per choice with the default "
            f"marked. The right half is a schematic plug in teal drawn from the {words}'s defaults at 1.5 to 1, "
            + ("a top view with the prong end at the left against a wall plate line, a side view standing with its prong end up, "
               if tool == "one-sided" else "a top view with the prong end at the left against a wall plate line, ")
            + "the cord's end as a small circle, a bar of four knuckles at 1:1 and a strap bar at 1:1. A straight black arrow "
              "runs from each measured row's blank to a red dimension line on the schematic, the row's number in a red circle "
              "at the line:", ""]
    for k in sorted(anchors):
        out.append(f"- Arrow {k} points to {schematic.words[anchors[k]]}.")
    out.append("")
    for t in table:
        row = t["row"]
        if row["type"] == "enum":
            opts = ", ".join(str(v) for v in row["values"])
            out.append(f"- Row {t['k']}, {t['title'].lower()}: {len(row['values'])} boxes, {row['default']} marked as the default; "
                       f"the choices are {opts}.")
        elif row["type"] == "boolean":
            out.append(f"- Row {t['k']}, {t['title'].lower()}: one box marked, leave on.")
        elif t["measure"] is not None and t["measure"]["anchor"] in QUIZ_ANCHORS:
            out.append(f"- Row {t['k']}, {t['title'].lower()}: no arrow; the boxes carry the choice.")
    out += ["", "Type them into the Customizer in this order.", "",
            f"How each number is measured, with its typical range and an example: [the {words}'s measuring guide](measuring-guide.md).", ""]
    return "\n".join(out)


def write_sheet(tool: str, catalog: Dict[Tuple[str, str], Dict[str, Any]], out_dir: Path) -> Dict[str, Any]:
    sh, twin, summary = build_sheet(tool, catalog)
    out_dir.mkdir(parents=True, exist_ok=True)
    sh.save(out_dir / "measuring-form.svg")
    (out_dir / "measuring-form.md").write_text(twin, encoding="utf-8", newline="\n")
    return summary


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Draw the measuring form sheets and their text twins.")
    parser.add_argument("--tool", choices=sorted(OUT_DIRS), help="one tool (default: both)")
    args = parser.parse_args(argv)
    catalog = load_catalog()
    for tool in ([args.tool] if args.tool else sorted(OUT_DIRS)):
        summary = write_sheet(tool, catalog, OUT_DIRS[tool])
        print(f"{tool}: {summary['rows']} rows to y = {summary['rows_bottom']} mm, {summary['leaders']} leaders, "
              f"no crossings; {OUT_DIRS[tool] / 'measuring-form.svg'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
