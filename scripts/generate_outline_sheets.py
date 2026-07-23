"""Generate the 1:1 dimensioned outline sheets for the public repo.

For every quick-select combination (3 ``plug_preset`` families x 3 sizes for
the flat tool, plus the heavy-duty clamshell plate at all 3 sizes — the plate
geometry follows the Size selection, so it gets its own 3 sheets), this
script:

1. Renders the v7 SCAD via the OpenSCAD CLI (``render_mode="Body Only"`` /
   ``"Clamshell Plate"`` with the preset + size ``-D`` overrides) — the same
   pattern as ``regenerate_fixtures.py``. No model changes needed.
2. Extracts the 2D geometry with trimesh + shapely:
   - flat tool: the true silhouette + through-hole bores from the projected
     shadow (union of the projected triangles), and the blind plug-pocket
     opening as the difference between the shadow and a near-top-face
     cross-section;
   - clamshell: a near-contact-face cross-section (the outer-face edge
     roundover and the cable strip live on the other face).
3. Computes the labeled dimension values from ``tests/fit_formulas.py`` (the
   pure-Python mirror of ``fit_measured.scad``) and cross-checks them against
   the rendered mesh (print-scale + dimension-parity asserts).
4. Composes each sheet as a 210 x 279 mm SVG (fits A4 and US Letter, same
   conventions as ``docs/guides/measuring-template.svg``): the outline at
   exact 1:1 scale with interior cutouts dashed, CAD-style dimension lines,
   a 50 x 50 mm calibration square, a title block with the matching
   Customizer settings, and a how-to strip.

Run from the repo root:

    python scripts/generate_outline_sheets.py
    python scripts/generate_outline_sheets.py --only standard-3-prong_medium
    python scripts/generate_outline_sheets.py --skip-render   # reuse STLs

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import argparse
import datetime as _dt
import logging
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import shapely
import trimesh
from shapely.geometry import MultiPolygon, Polygon

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tests import fit_formulas  # noqa: E402
from tests.openscad_runner import OpenSCADRunner  # noqa: E402

logger = logging.getLogger(__name__)

SCAD = PROJECT_ROOT / "src" / "Plug_Puller_Parametric.scad"
STL_DIR = PROJECT_ROOT / "tmp_renders" / "outline_sheets"
DEFAULT_OUT = PROJECT_ROOT / "docs" / "guides" / "outline-sheets"

MODEL_VERSION = "0.8"

# ---------------------------------------------------------------------------
# The quick-select matrix
# ---------------------------------------------------------------------------

SIZES = ["Small", "Medium", "Large"]

# Station measurements each plug_preset prefills (mirrors the `_eff_plug_*`
# quick-select table in the v7 SCAD — keep in sync).
PLUG_PRESETS: Dict[str, Dict] = {
    "flat-2-prong": {
        "customizer": "Flat 2-prong lamp plug - NEMA 1-15",
        "label": "Flat 2-prong lamp plug (NEMA 1-15)",
        "short": "Flat 2-prong lamp plug",
        "measurements": {
            "measure_plug_length": 37.0,
            "measure_plug_width_wall": 25.0,
            "measure_plug_width_cable": 11.2,
            "measure_plug_thickness_wall": 18.6,
            "measure_plug_thickness_cable": 8.6,
            "measure_cord_thickness": 3.6,
        },
    },
    "standard-3-prong": {
        "customizer": "Standard 3-prong plug - NEMA 5-15",
        "label": "Standard 3-prong plug (NEMA 5-15)",
        "short": "Standard 3-prong plug",
        "measurements": {
            "measure_plug_length": 46.2,
            "measure_plug_width_wall": 26.6,
            "measure_plug_width_cable": 13.4,
            "measure_plug_thickness_wall": 18.9,
            "measure_plug_thickness_cable": 15.0,
            "measure_cord_thickness": 7.0,
        },
    },
    "heavy-duty-round": {
        "customizer": "Heavy-duty extension cord - NEMA 5-15",
        "label": "Heavy-duty extension cord (NEMA 5-15)",
        "short": "Heavy-duty extension cord",
        "measurements": {
            "measure_plug_length": 43.8,
            "measure_plug_width_wall": 25.8,
            "measure_plug_width_cable": 21.9,
            "measure_plug_thickness_wall": 27.0,
            "measure_plug_thickness_cable": 27.0,
            "measure_cord_thickness": 8.2,
        },
    },
}

# Clamshell defaults mirrored from the v7 Customizer block (used for the
# pure-Python clamshell dimension mirror below).
CLAM_FINGER_FIT = 1.0
CLAM_CABLE_CLEARANCE = 0.8
CLAM_FINGER_WALL = 5.0
CLAM_FINGER_INNER_WALL = 3.0
CLAM_PLATE_THICKNESS = 4.0
CLAM_ZIP_HOLE_DIAMETER = 4.0
CLAM_VELCRO_SLOT = (9.3, 28.0)  # width x length
CLAM_GRIP_ZONE_START = 4.0
CLAM_GRIP_BITE = -1.0


def clamshell_mirror(size: str, plug: Dict) -> Dict[str, float]:
    """Pure-Python mirror of the clamshell envelope derivations (see the
    'CLAMSHELL DERIVED VALUES' block in the v7 SCAD)."""
    m = plug["measurements"]
    finger_width = fit_formulas.FIT_SIZE_TABLE[size][0]
    finger_dia = finger_width + CLAM_FINGER_FIT
    cable_gap = max(2.0, m["measure_cord_thickness"] + CLAM_CABLE_CLEARANCE)
    cable_hw = cable_gap / 2
    lobe_r = finger_dia / 2 + CLAM_FINGER_WALL
    finger_y = lobe_r
    finger_x = cable_hw + CLAM_FINGER_INNER_WALL + finger_dia / 2
    outer_x = finger_x + finger_dia / 2 + CLAM_FINGER_WALL
    throat_y0 = finger_y + finger_dia / 2 + 2
    y_back_min = throat_y0 + 2
    plug_len = m["measure_plug_length"]
    length = max(
        y_back_min + CLAM_GRIP_ZONE_START + 12,
        plug_len + 11,
        y_back_min + plug_len,
    )
    return {
        "finger_dia": finger_dia,
        "finger_x": finger_x,
        "finger_y": finger_y,
        "cable_gap": cable_gap,
        "throat_y0": throat_y0,
        "width": 2 * outer_x,
        "length": length,
        "plate_thickness": CLAM_PLATE_THICKNESS,
    }


# ---------------------------------------------------------------------------
# Geometry extraction
# ---------------------------------------------------------------------------


def _fix(geom):
    return geom if geom.is_valid else shapely.make_valid(geom)


def as_polygons(geom) -> List[Polygon]:
    if geom.is_empty:
        return []
    if isinstance(geom, Polygon):
        return [geom]
    if isinstance(geom, MultiPolygon):
        return list(geom.geoms)
    return [g for g in getattr(geom, "geoms", []) if isinstance(g, Polygon)]


def silhouette(mesh: trimesh.Trimesh) -> MultiPolygon:
    """True downward shadow: union of the XY-projected triangles.

    Exterior = the widest footprint; interior rings = regions void at every
    Z, i.e. every through-hole at its narrowest (true) bore.
    """
    tris = mesh.triangles[:, :, :2]
    polys = shapely.polygons(tris)
    polys = polys[shapely.area(polys) > 1e-9]
    merged = _fix(shapely.union_all(polys, grid_size=1e-6))
    merged = shapely.simplify(merged, 0.01, preserve_topology=True)
    return MultiPolygon(as_polygons(merged))


def section_rings(mesh: trimesh.Trimesh, z: float) -> List[np.ndarray]:
    """Closed 2D rings of the horizontal cross-section at height ``z``
    (model XY coordinates, Z dropped — no reprojection frame involved)."""
    sec = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if sec is None:
        return []
    return [np.asarray(d)[:, :2] for d in sec.discrete]


def _dedupe_rings(rings: Sequence[np.ndarray]) -> List[np.ndarray]:
    """Drop duplicate section rings (trimesh can emit each loop twice when
    the cut plane grazes coincident geometry)."""
    seen = set()
    out = []
    for r in rings:
        p = Polygon(r)
        if p.area <= 1e-6:
            continue
        c = p.centroid
        key = (round(p.area, 3), round(c.x, 2), round(c.y, 2))
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def rings_to_polygons(rings: Sequence[np.ndarray]) -> List[Polygon]:
    """Assemble rings into shell polygons with holes (even-odd nesting)."""
    ring_polys = [Polygon(r) for r in _dedupe_rings(rings) if len(r) >= 3]
    n = len(ring_polys)
    # Full-polygon containment (a representative point is not enough: a
    # solid shell's point can land inside one of its own hole rings).
    depth = [0] * n
    for i in range(n):
        for j in range(n):
            if i != j and ring_polys[j].contains(ring_polys[i]):
                depth[i] += 1
    shells = [i for i in range(n) if depth[i] % 2 == 0]
    holes = [i for i in range(n) if depth[i] % 2 == 1]
    out = []
    for si in shells:
        my_holes = [
            ring_polys[hi].exterior.coords
            for hi in holes
            if depth[hi] == depth[si] + 1
            and ring_polys[si].contains(ring_polys[hi])
        ]
        out.append(Polygon(ring_polys[si].exterior.coords, my_holes))
    return out


def filled_union(rings: Sequence[np.ndarray]):
    """Union of every ring filled solid (holes swallowed)."""
    polys = [Polygon(r) for r in rings if len(r) >= 3]
    polys = [_fix(p) for p in polys if p.area > 1e-6]
    return _fix(shapely.union_all(polys))


@dataclass
class Circle:
    cx: float
    cy: float
    d: float


def classify_circle(ring: np.ndarray) -> Optional[Circle]:
    pts = np.asarray(ring)
    c = pts.mean(axis=0)
    r = np.linalg.norm(pts - c, axis=1)
    if r.mean() < 0.5:
        return None
    # 4% tolerance: simplify() nibbles small bores (a Ø4 zip hole sits at
    # ~2.2% radial scatter after the 0.01 mm simplification).
    if r.std() / r.mean() < 0.04:
        return Circle(float(c[0]), float(c[1]), float(2 * r.mean()))
    return None


# ---------------------------------------------------------------------------
# SVG composer
# ---------------------------------------------------------------------------

FONT = "Helvetica, Arial, sans-serif"
PAGE_W, PAGE_H = 210.0, 279.0
DASH_HOLE = "1.6,1.1"
DASH_POCKET = "2.4,1.4"


def fmt(v: float) -> str:
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return s if s else "0"


class Sheet:
    """Minimal SVG builder. All coordinates are millimetres; the drawing
    transform is a pure translation + Y flip, so 1 SVG user unit == 1 mm ==
    1 model mm (asserted in :meth:`set_model_frame`)."""

    def __init__(self) -> None:
        self.parts: List[str] = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{PAGE_W:g}mm" '
            f'height="{PAGE_H:g}mm" viewBox="0 0 {PAGE_W:g} {PAGE_H:g}">',
            f'<rect x="0" y="0" width="{PAGE_W:g}" height="{PAGE_H:g}" fill="white"/>',
        ]
        self._ox = 0.0
        self._oy = 0.0

    # -- model frame -------------------------------------------------------
    def set_model_frame(self, ox: float, oy: float) -> None:
        """Model (x, y) maps to sheet (ox + x, oy - y)."""
        self._ox, self._oy = ox, oy
        ax, ay = self.pt(10.0, 20.0)
        bx, by = self.pt(-3.5, 4.25)
        assert abs((ax - bx) - 13.5) < 1e-9 and abs((by - ay) - 15.75) < 1e-9, (
            "sheet transform is not a rigid 1:1 mapping"
        )

    def pt(self, x: float, y: float) -> Tuple[float, float]:
        return self._ox + x, self._oy - y

    # -- primitives ---------------------------------------------------------
    def text(
        self,
        x: float,
        y: float,
        s: str,
        size: float = 3.2,
        weight: str = "normal",
        anchor: str = "start",
        fill: str = "black",
        halo: bool = False,
    ) -> None:
        s = (
            s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        )
        extra = (
            ' paint-order="stroke" stroke="white" stroke-width="0.9"' if halo else ""
        )
        self.parts.append(
            f'<text x="{x:.3f}" y="{y:.3f}" font-family="{FONT}" '
            f'font-size="{size:g}" font-weight="{weight}" text-anchor="{anchor}" '
            f'fill="{fill}"{extra}>{s}</text>'
        )

    def line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        w: float = 0.3,
        dash: Optional[str] = None,
        color: str = "black",
    ) -> None:
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(
            f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" '
            f'stroke="{color}" stroke-width="{w:g}"{d}/>'
        )

    def rect(
        self, x: float, y: float, w: float, h: float, sw: float = 0.4
    ) -> None:
        self.parts.append(
            f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" '
            f'fill="none" stroke="black" stroke-width="{sw:g}"/>'
        )

    def ring_path(
        self,
        coords: Sequence[Tuple[float, float]],
        w: float,
        dash: Optional[str] = None,
        color: str = "black",
    ) -> None:
        pts = [self.pt(x, y) for x, y in coords]
        d = "M " + " L ".join(f"{x:.3f} {y:.3f}" for x, y in pts) + " Z"
        dd = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w:g}" '
            f'stroke-linejoin="round"{dd}/>'
        )

    def polygon_outline(
        self, poly: Polygon, w: float, dash: Optional[str] = None,
        color: str = "black",
    ) -> None:
        self.ring_path(list(poly.exterior.coords), w, dash, color)
        for interior in poly.interiors:
            self.ring_path(list(interior.coords), w, dash, color)

    def cross(self, mx: float, my: float, r: float = 1.4) -> None:
        x, y = self.pt(mx, my)
        self.line(x - r, y, x + r, y, 0.2)
        self.line(x, y - r, x, y + r, 0.2)

    # -- CAD dimension helpers (sheet coordinates) ---------------------------
    def _arrow(self, x: float, y: float, angle_deg: float) -> None:
        a = math.radians(angle_deg)
        ln, hw = 2.4, 0.75
        bx, by = x - ln * math.cos(a), y - ln * math.sin(a)
        px = (-hw * math.sin(a), hw * math.cos(a))
        p = (
            f"{x:.3f},{y:.3f} {bx + px[0]:.3f},{by + px[1]:.3f} "
            f"{bx - px[0]:.3f},{by - px[1]:.3f}"
        )
        self.parts.append(f'<polygon points="{p}" fill="black"/>')

    def dim_h(
        self,
        mx1: float,
        mx2: float,
        my_dim: float,
        my_obj: float,
        label: str,
        text_size: float = 3.0,
        label_above: bool = True,
    ) -> None:
        """Horizontal dimension in model coords: between x = mx1..mx2, the
        dimension line at model y = my_dim, extension lines starting at the
        object edge y = my_obj."""
        (x1, yd) = self.pt(min(mx1, mx2), my_dim)
        (x2, _) = self.pt(max(mx1, mx2), my_dim)
        (_, yo) = self.pt(0, my_obj)
        over = 1.0 if yd < yo else -1.0
        for x in (x1, x2):
            self.line(x, yo, x, yd - over, 0.18)
        narrow = (x2 - x1) < 11.0
        if narrow:
            self.line(x1 - 5, yd, x2 + 5, yd, 0.25)
            self._arrow(x1, yd, 0)
            self._arrow(x2, yd, 180)
            tx, anchor = x2 + 5.8, "start"
        else:
            self.line(x1, yd, x2, yd, 0.25)
            self._arrow(x1, yd, 180)
            self._arrow(x2, yd, 0)
            tx, anchor = (x1 + x2) / 2, "middle"
        ty = yd - 1.1 if label_above else yd + text_size + 0.9
        self.text(tx, ty, label, text_size, "bold", anchor, halo=True)

    def dim_v(
        self,
        my1: float,
        my2: float,
        mx_dim: float,
        mx_obj: float,
        label: str,
        text_size: float = 3.0,
        label_side: str = "left",
    ) -> None:
        (xd, y1) = self.pt(mx_dim, max(my1, my2))
        (_, y2) = self.pt(mx_dim, min(my1, my2))
        (xo, _) = self.pt(mx_obj, 0)
        over = 1.0 if xd < xo else -1.0
        for y in (y1, y2):
            self.line(xo, y, xd - over, y, 0.18)
        narrow = (y2 - y1) < 11.0
        if narrow:
            self.line(xd, y1 - 5, xd, y2 + 5, 0.25)
            self._arrow(xd, y1, 90)
            self._arrow(xd, y2, 270)
        else:
            self.line(xd, y1, xd, y2, 0.25)
            self._arrow(xd, y1, 270)
            self._arrow(xd, y2, 90)
        ym = (y1 + y2) / 2 + 1.0
        if label_side == "left":
            self.text(xd - 1.4, ym, label, text_size, "bold", "end", halo=True)
        else:
            self.text(xd + 1.4, ym, label, text_size, "bold", "start", halo=True)

    def leader(
        self,
        mx: float,
        my: float,
        angle_deg: float,
        length: float,
        label: str,
        text_size: float = 3.0,
    ) -> None:
        """Leader arrow pointing at model point (mx, my)."""
        x, y = self.pt(mx, my)
        a = math.radians(angle_deg)  # sheet-frame angle, y down
        x2, y2 = x + length * math.cos(a), y + length * math.sin(a)
        self.line(x, y, x2, y2, 0.25)
        self._arrow(x, y, angle_deg + 180)
        shelf = 6.0 if math.cos(a) >= 0 else -6.0
        self.line(x2, y2, x2 + shelf, y2, 0.25)
        anchor = "start" if shelf > 0 else "end"
        self.text(x2 + shelf + (0.8 if shelf > 0 else -0.8), y2 - 0.9,
                  label, text_size, "bold", anchor, halo=True)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(self.parts + ["</svg>"]) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Shared sheet chrome (header, calibration square, title block, how-to strip)
# ---------------------------------------------------------------------------


@dataclass
class SheetInfo:
    filename: str
    title: str
    combo_lines: List[str]
    settings_lines: List[str]
    keydim_lines: List[str]
    howto_lines: List[str]
    footprint: Tuple[float, float]  # printed outline W x H (mm), for the block


def draw_chrome(sh: Sheet, info: SheetInfo) -> None:
    sh.text(PAGE_W / 2, 12, f"Plug Puller — {info.title}", 5.0, "bold", "middle")
    sh.text(
        PAGE_W / 2,
        17.5,
        "1:1 outline sheet — print at 100% scale / “Actual size”, never “fit to page”. "
        "Check the calibration square before trusting anything.",
        2.8,
        anchor="middle",
    )
    # Calibration square
    sh.rect(14, 22, 50, 50)
    sh.text(39, 45.5, "CALIBRATION", 3.4, "bold", "middle")
    sh.text(39, 50.5, "50 × 50 mm", 3.4, anchor="middle")
    sh.text(39, 56.5, "Measure me with a ruler.", 2.6, anchor="middle", fill="#444444")
    sh.text(39, 60.5, "Not 50 mm? Re-print at 100%.", 2.6, anchor="middle", fill="#444444")
    # Title block
    sh.rect(70, 22, 126, 50, 0.3)
    y = 27.0
    for i, ln in enumerate(info.combo_lines):
        sh.text(73, y, ln, 3.4 if i == 0 else 2.8, "bold" if i == 0 else "normal")
        y += 4.6 if i == 0 else 3.8
    y += 0.8
    for ln in info.settings_lines:
        sh.text(73, y, ln, 2.6, fill="#333333")
        y += 3.4
    y = 27.0
    sh.text(133, y, "Key dimensions", 2.8, "bold")
    y += 4.0
    for ln in info.keydim_lines:
        sh.text(133, y, ln, 2.6)
        y += 3.5
    # How-to strip
    sh.line(14, 248, 196, 248, 0.2, color="#888888")
    sh.text(14, 252.5, "How to use this sheet", 3.2, "bold")
    y = 256.5
    for ln in info.howto_lines:
        sh.text(14, y, ln, 2.7)
        y += 3.6
    sh.text(
        PAGE_W / 2,
        275.5,
        f"openscad-plug-puller v{MODEL_VERSION} · {info.filename} · scale 1:1 · "
        "guide: docs/guides/print-preview-outlines.md",
        2.4,
        anchor="middle",
        fill="#444444",
    )


DRAW_TOP = 78.0  # top of the drawing area
DRAW_BOTTOM = 245.0


def drawing_frame(sh: Sheet, extent_y: float, top_margin: float) -> None:
    """Center the model horizontally at page center and place model y-max at
    DRAW_TOP + top_margin (top_margin = room reserved for top-side dims)."""
    avail = DRAW_BOTTOM - DRAW_TOP
    used = extent_y + top_margin + 12.0
    pad = max(0.0, (avail - used) / 2)
    sh.set_model_frame(PAGE_W / 2, DRAW_TOP + pad + top_margin + extent_y)


# ---------------------------------------------------------------------------
# Flat-tool sheet
# ---------------------------------------------------------------------------


@dataclass
class Check:
    name: str
    expected: float
    actual: float
    tol: float

    @property
    def ok(self) -> bool:
        return abs(self.expected - self.actual) <= self.tol


def build_flat_sheet(
    stl: Path, preset_key: str, size: str, out: Path
) -> List[Check]:
    plug = PLUG_PRESETS[preset_key]
    d = fit_formulas.derive({**plug["measurements"], "size": size})
    mesh = trimesh.load(stl, force="mesh")
    (xmin, ymin, zmin), (xmax, ymax, zmax) = mesh.bounds

    shadow = silhouette(mesh)
    exts = sorted(as_polygons(shadow), key=lambda p: p.area, reverse=True)
    body = exts[0]
    # Through-hole bores.
    circles: List[Circle] = []
    slots: List[np.ndarray] = []
    for interior in body.interiors:
        ring = np.asarray(interior.coords)
        c = classify_circle(ring)
        if c:
            circles.append(c)
        else:
            slots.append(ring)
    fingers = sorted(
        [c for c in circles if abs(c.d - d["finger_hole_diameter"]) < 3.0],
        key=lambda c: c.cx,
    )
    zips = sorted(
        [c for c in circles if abs(c.d - d["zip_tie_hole_diameter"]) < 2.0],
        key=lambda c: (round(c.cy, 1), c.cx),
    )

    # Blind pocket opening: the pocket recesses exist above the pocket
    # floors, so difference the filled cross-section just above the higher
    # floor against the full footprint. (A near-top-face section won't do:
    # the top-edge ball roundover already pulls the outer wall inward
    # there.) The tiny erode/dilate scrubs the hairline band where the
    # roundover has just started at this height.
    z_pocket = max(d["pocket_seat_floor"], d["pocket_floor"]) + 0.15
    s_filled = filled_union(section_rings(mesh, z_pocket))
    # body (not just its exterior) so the through-holes, already drawn from
    # the shadow's interior rings, don't reappear as "pockets".
    pocket_geo = _fix(body.difference(s_filled)).buffer(-0.05).buffer(0.05)
    pockets = [
        shapely.simplify(p, 0.01, preserve_topology=True)
        for p in as_polygons(pocket_geo)
        if p.area > 5.0
    ]

    # ---- parity checks ----------------------------------------------------
    checks = [
        Check("puller_length vs mesh", d["puller_length"], ymax - ymin, 0.15),
        Check("body_thickness vs mesh", d["body_thickness"], zmax - zmin, 0.15),
    ]
    if len(fingers) == 2:
        for c in fingers:
            checks.append(
                Check("finger bore Ø", d["finger_hole_diameter"], c.d, 0.25)
            )
        checks.append(
            Check(
                "finger spacing",
                d["finger_hole_spacing"],
                fingers[1].cx - fingers[0].cx,
                0.25,
            )
        )
        checks.append(
            Check(
                "finger_hole_y",
                d["finger_hole_y_position"],
                (fingers[0].cy + fingers[1].cy) / 2,
                0.25,
            )
        )
    else:
        checks.append(Check("finger holes found", 2, len(fingers), 0))
    if len(zips) == 4:
        checks.append(
            Check(
                "zip row spacing",
                d["zip_tie_height_spacing"],
                abs(zips[0].cy - zips[2].cy),
                0.25,
            )
        )
        for c in zips:
            checks.append(Check("zip bore Ø", d["zip_tie_hole_diameter"], c.d, 0.2))
    if pockets:
        pk_min_y = min(p.bounds[1] for p in pockets)
        checks.append(
            Check(
                "pocket depth vs mesh",
                d["pocket_depth"],
                (ymax - pk_min_y),
                0.6,
            )
        )

    # ---- compose ----------------------------------------------------------
    L = ymax - ymin
    W = xmax - xmin
    sh = Sheet()
    size_word = size.lower()
    info = SheetInfo(
        filename=out.name,
        title=f"{plug['label']} · {size}",
        combo_lines=[
            f"{plug['short']}",
            f"Flat tool · {size} hand size",
            f"Printed footprint ≈ {fmt(W)} × {fmt(L)} mm",
        ],
        settings_lines=[
            "Customizer settings for this exact tool:",
            "  tool_style = Flat tool",
            "  plug_preset =",
            f"      {plug['customizer']}",
            f"  size = {size}",
            "  (everything else at its default)",
        ],
        keydim_lines=[
            f"Body thickness: {fmt(d['body_thickness'])} mm (this sheet is 2D)",
            f"Finger holes: Ø{fmt(d['finger_hole_diameter'])}, "
            f"{fmt(d['finger_hole_spacing'])} apart",
            f"Pocket: {fmt(d['pocket_width'])} wide × {fmt(d['pocket_depth'])} deep",
            f"Wall notch: {fmt(d['plug_wall_notch_width'])} wide × "
            f"{fmt(d['plug_wall_notch_height'])} deep",
            f"Zip holes: 4 × Ø{fmt(d['zip_tie_hole_diameter'])}, rows "
            f"{fmt(d['zip_tie_height_spacing'])} apart",
            f"J-hook cord gap: {fmt(d['t_hook_base_gap'])} mm",
        ],
        howto_lines=[
            "1. Print at 100% and measure the calibration square — it must be exactly 50 × 50 mm.",
            "2. Cut along the SOLID outline. Dashed lines are holes and the plug pocket — poke through the two big finger circles.",
            "3. Hold the cutout on your plug at the wall: the plug fits the dashed pocket, the top notch straddles the wall plate.",
            f"4. Try the finger holes ({size_word} size). Wrong size? Try a neighbouring sheet, or print stl/Finger_Sizing_Stencil.stl.",
            "5. Happy? Open the Customizer with the title-block settings and export your STL (docs/guides/quick-start-beginner.md).",
        ],
        footprint=(W, L),
    )
    draw_chrome(sh, info)
    top_margin = 16.0  # room for the notch + pocket-width dims above the tool
    drawing_frame(sh, L, top_margin)

    # Outline: exterior solid, everything interior dashed.
    sh.ring_path(list(body.exterior.coords), 0.5)
    for interior in body.interiors:
        sh.ring_path(list(interior.coords), 0.35, DASH_HOLE)
    for p in pockets:
        sh.polygon_outline(p, 0.35, DASH_POCKET, color="#333333")
    for c in fingers + zips:
        sh.cross(c.cx, c.cy)

    # Dimensions.
    sh.dim_v(0, L, xmin - 9, xmin, f"{fmt(L)}")
    sh.dim_h(xmin, xmax, -8, 0, f"{fmt(W)}", label_above=False)
    sh.dim_h(
        -d["plug_wall_notch_width"] / 2,
        d["plug_wall_notch_width"] / 2,
        L + 6,
        L,
        f"notch {fmt(d['plug_wall_notch_width'])}",
    )
    sh.dim_h(
        -d["pocket_width"] / 2,
        d["pocket_width"] / 2,
        L + 12.5,
        L,
        f"pocket {fmt(d['pocket_width'])}",
    )
    sh.dim_v(
        L - d["pocket_depth"],
        L,
        xmax + 8,
        xmax,
        f"pocket depth {fmt(d['pocket_depth'])}",
        label_side="right",
    )
    if len(fingers) == 2:
        sh.dim_h(
            fingers[0].cx,
            fingers[1].cx,
            fingers[0].cy,
            fingers[0].cy,
            f"{fmt(d['finger_hole_spacing'])}",
        )
        c = fingers[1]
        sh.leader(
            c.cx + c.d / 2 * math.cos(math.radians(-40)),
            c.cy + c.d / 2 * math.sin(math.radians(-40)),
            40,
            9,
            f"Ø{fmt(d['finger_hole_diameter'])} (2×)",
        )
    if len(zips) == 4:
        top_pair = zips[2:] if zips[2].cy > zips[0].cy else zips[:2]
        bot_pair = zips[:2] if zips[2].cy > zips[0].cy else zips[2:]
        sh.dim_h(
            top_pair[0].cx,
            top_pair[1].cx,
            (top_pair[0].cy + bot_pair[0].cy) / 2,
            top_pair[0].cy,
            f"{fmt(top_pair[1].cx - top_pair[0].cx)}",
            2.6,
        )
        col = [top_pair[0], bot_pair[0]]
        sh.dim_v(
            col[1].cy,
            col[0].cy,
            col[0].cx - 10,
            col[0].cx,
            f"{fmt(abs(col[0].cy - col[1].cy))}",
            2.6,
            label_side="left",
        )
        z = min(zips, key=lambda c: (c.cy, c.cx))
        sh.leader(
            z.cx - z.d / 2 * math.cos(math.radians(45)),
            z.cy - z.d / 2 * math.sin(math.radians(45)),
            135,
            8,
            f"Ø{fmt(d['zip_tie_hole_diameter'])} (4×)",
            2.6,
        )
    sh.save(out)
    return checks


# ---------------------------------------------------------------------------
# Clamshell sheet
# ---------------------------------------------------------------------------


def build_clamshell_sheet(stl: Path, size: str, out: Path) -> List[Check]:
    plug = PLUG_PRESETS["heavy-duty-round"]
    cm = clamshell_mirror(size, plug)
    mesh = trimesh.load(stl, force="mesh")
    (xmin, ymin, zmin), (xmax, ymax, zmax) = mesh.bounds

    # Contact-face section: outer-face edge roundover + cable strip live at
    # the other face, so this is the true plate profile.
    rings = section_rings(mesh, zmax - 0.05)
    polys = rings_to_polygons(rings)
    polys = [shapely.simplify(p, 0.01, preserve_topology=True) for p in polys]
    circles = []
    for p in polys:
        for interior in p.interiors:
            c = classify_circle(np.asarray(interior.coords))
            if c:
                circles.append(c)
    fingers = sorted(
        [c for c in circles if abs(c.d - cm["finger_dia"]) < 3.0], key=lambda c: c.cx
    )
    zips = [c for c in circles if abs(c.d - CLAM_ZIP_HOLE_DIAMETER) < 1.5]

    checks = [
        Check("plate width vs mirror", cm["width"], xmax - xmin, 0.2),
        Check("plate length vs mirror", cm["length"], ymax - ymin, 0.2),
        Check("plate thickness", cm["plate_thickness"], zmax - zmin, 0.1),
        Check("finger holes found", 2, len(fingers), 0),
        Check("zip holes found", 6, len(zips), 0),
    ]
    for c in fingers:
        checks.append(Check("clam finger bore Ø", cm["finger_dia"], c.d, 0.25))

    L = ymax - ymin
    W = xmax - xmin
    sh = Sheet()
    info = SheetInfo(
        filename=out.name,
        title=f"Heavy-duty clamshell plate · {size}",
        combo_lines=[
            "Heavy-duty clamshell plate",
            f"{plug['short']}",
            f"{size} hand size · the tool is TWO plates",
            f"Printed footprint ≈ {fmt(W)} × {fmt(L)} mm (one plate)",
        ],
        settings_lines=[
            "Customizer settings for this exact plate:",
            "  tool_style = Heavy-duty clamshell",
            "  plug_preset =",
            f"      {plug['customizer']}",
            f"  size = {size}",
            "  (everything else at its default)",
        ],
        keydim_lines=[
            f"Plate thickness: {fmt(cm['plate_thickness'])} mm each (×2 plates)",
            f"Finger holes: 2 × Ø{fmt(cm['finger_dia'])}",
            f"Cord channel: {fmt(cm['cable_gap'])} mm wide",
            f"Zip holes: 6 × Ø{fmt(CLAM_ZIP_HOLE_DIAMETER)}",
            f"Velcro slots: {fmt(CLAM_VELCRO_SLOT[0])} × {fmt(CLAM_VELCRO_SLOT[1])}",
            "Serrated V-edges grip the plug",
        ],
        howto_lines=[
            "1. Print at 100% and measure the calibration square — it must be exactly 50 × 50 mm.",
            "2. Cut along the SOLID outline (both arms). Dashed lines are holes and slots.",
            "3. Lay the cutout over your plug: the plug body sits between the serrated V-edges, the cord in the bottom channel.",
            "4. The real tool is TWO of these plates zip-tied face to face around the plug — this sheet previews one.",
            "5. Happy? Open the Customizer with the title-block settings and export your STL (docs/guides/quick-start-beginner.md).",
        ],
        footprint=(W, L),
    )
    draw_chrome(sh, info)
    drawing_frame(sh, L, 8.0)

    for p in polys:
        sh.ring_path(list(p.exterior.coords), 0.5)
        for interior in p.interiors:
            sh.ring_path(list(interior.coords), 0.35, DASH_HOLE)
    for c in circles:
        sh.cross(c.cx, c.cy)
    # Cable strip (outer face) as a light dashed rectangle.
    hw = cm["cable_gap"] / 2 + 1.5
    strip = [(-hw, 0), (hw, 0), (hw, cm["throat_y0"]), (-hw, cm["throat_y0"])]
    sh.ring_path(strip, 0.25, DASH_POCKET, color="#888888")
    (tsx, tsy) = sh.pt(0, cm["throat_y0"] + 1.5)
    sh.text(tsx, tsy, "cable strip (outer face)", 2.2, anchor="middle",
            fill="#888888", halo=True)

    sh.dim_v(0, L, xmin - 9, xmin, f"{fmt(L)}")
    sh.dim_h(xmin, xmax, -8, 0, f"{fmt(W)}", label_above=False)
    sh.dim_h(
        -cm["cable_gap"] / 2,
        cm["cable_gap"] / 2,
        -3.5,
        0,
        f"cord {fmt(cm['cable_gap'])}",
        2.6,
        label_above=False,
    )
    if fingers:
        c = fingers[-1]
        sh.leader(
            c.cx + c.d / 2 * math.cos(math.radians(-45)),
            c.cy + c.d / 2 * math.sin(math.radians(-45)),
            45,
            9,
            f"Ø{fmt(cm['finger_dia'])} (2×)",
        )
    sh.save(out)
    return checks


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


@dataclass
class Job:
    slug: str
    kind: str  # "flat" | "clamshell"
    preset_key: str
    size: str
    params: Dict = field(default_factory=dict)

    @property
    def stl(self) -> Path:
        return STL_DIR / f"{self.slug}.stl"

    def svg_name(self) -> str:
        return f"outline_{self.slug}.svg"


def all_jobs() -> List[Job]:
    jobs: List[Job] = []
    for key, plug in PLUG_PRESETS.items():
        for size in SIZES:
            jobs.append(
                Job(
                    slug=f"{key}_{size.lower()}",
                    kind="flat",
                    preset_key=key,
                    size=size,
                    params={
                        "render_mode": "Body Only",
                        "plug_preset": plug["customizer"],
                        "size": size,
                    },
                )
            )
    for size in SIZES:
        jobs.append(
            Job(
                slug=f"heavy-duty-clamshell_{size.lower()}",
                kind="clamshell",
                preset_key="heavy-duty-round",
                size=size,
                params={
                    "render_mode": "Clamshell Plate",
                    "plug_preset": PLUG_PRESETS["heavy-duty-round"]["customizer"],
                    "size": size,
                },
            )
        )
    return jobs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT,
                        help="Output directory for the SVG sheets.")
    parser.add_argument("--only", nargs="+", help="Limit to these job slugs.")
    parser.add_argument("--skip-render", action="store_true",
                        help="Reuse STLs already in tmp_renders/outline_sheets.")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    jobs = all_jobs()
    if args.only:
        wanted = set(args.only)
        jobs = [j for j in jobs if j.slug in wanted]
        missing = wanted - {j.slug for j in jobs}
        if missing:
            logger.error("Unknown jobs: %s", sorted(missing))
            return 2

    if not args.skip_render:
        runner = OpenSCADRunner()
        logger.info("OpenSCAD: %s", runner.version_string)
        for job in jobs:
            res = runner.generate_stl(SCAD, job.stl, job.params)
            if not res.success:
                logger.error("Render failed for %s: %s", job.slug, res.stderr[-400:])
                return 1

    failures: List[str] = []
    for job in jobs:
        out = args.out / job.svg_name()
        if job.kind == "flat":
            checks = build_flat_sheet(job.stl, job.preset_key, job.size, out)
        else:
            checks = build_clamshell_sheet(job.stl, job.size, out)
        bad = [c for c in checks if not c.ok]
        status = "OK " if not bad else "FAIL"
        logger.info("%s %s -> %s (%d checks)", status, job.slug, out.name, len(checks))
        for c in checks:
            level = logging.DEBUG if c.ok else logging.ERROR
            logger.log(
                level,
                "    %-24s expected %-9s actual %-9s tol %s",
                c.name, fmt(c.expected), fmt(round(c.actual, 3)), c.tol,
            )
        if bad:
            failures.append(job.slug)

    if failures:
        logger.error("Dimension-parity failures: %s", failures)
        return 1
    logger.info(
        "All %d sheets written to %s (generated %s).",
        len(jobs), args.out, _dt.date.today().isoformat(),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
