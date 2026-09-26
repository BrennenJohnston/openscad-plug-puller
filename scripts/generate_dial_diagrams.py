#!/usr/bin/env python3
"""Draw one diagram per Customizer dial from ``dial_catalog.json``.

For every catalog row the tool is rendered twice with the OpenSCAD CLI: at
its Customizer defaults (plus the row's ``context``) and with the row's dial
moved to its ``after`` value. The top view of each render is extracted with
the outline-sheet helpers (the shadow silhouette with its through-holes plus
the pocket recess for the one-sided puller; the contact-face section for a
two-sided plate), and the symmetric difference of the two views is the red
dashed trace of "what this dial moves". Each diagram is an SVG at
1 unit = 1 mm under ``docs/dials/<file>/<name>.svg``: the black default
outline, the teal plug, the red trace, the legend line, and a ``<title>`` /
``<desc>`` pair carrying the row's words. Rows whose ``view`` is ``none``
get a small SVG saying the dial changes no shape.

Renders are cached under ``tmp_renders/dial_diagrams/`` (gitignored), keyed
by the parameter set and the SCAD sources, never by STL bytes (identical
renders are not byte-identical).

Usage:
    python scripts/generate_dial_diagrams.py                 # every row
    python scripts/generate_dial_diagrams.py --file one-sided --only size
    python scripts/generate_dial_diagrams.py --views top --force

Exit status 0 only when every selected row produced an SVG.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import logging
import re
import sys
import textwrap
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import shapely
import trimesh
from shapely.geometry import LineString, Polygon

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.generate_outline_sheets import (  # noqa: E402
    DASH_HOLE,
    DASH_POCKET,
    FONT,
    ONE_SIDED,
    PLUG_PRESETS,
    SCAD,
    TWO_SIDED,
    TWO_SIDED_SCAD,
    _fix,
    as_polygons,
    clean_polygon,
    filled_union,
    rings_to_polygons,
    section_rings,
    silhouette,
)
from tests import fit_formulas  # noqa: E402
from tests.openscad_runner import OpenSCADRunner  # noqa: E402

logger = logging.getLogger("dial_diagrams")

CATALOG = PROJECT_ROOT / "dial_catalog.json"
MAPPINGS = {
    ONE_SIDED: PROJECT_ROOT / "parameter_mapping.json",
    TWO_SIDED: PROJECT_ROOT / "parameter_mapping_two_sided.json",
}
SCADS = {ONE_SIDED: SCAD, TWO_SIDED: TWO_SIDED_SCAD}
DEFAULT_OUT = PROJECT_ROOT / "docs" / "dials"
DEFAULT_CACHE = PROJECT_ROOT / "tmp_renders" / "dial_diagrams"
INDEX_NAME = "dial_diagrams_index.json"
CANONICAL_OPENSCAD = Path(r"C:\Program Files\OpenSCAD (Nightly)\openscad.com")

# The words on every diagram (strings pack S-247 and S-248).
LEGEND_LINE = (
    "black = the tool at its defaults; teal = the plug you measured; "
    "red dashed = what this dial moves"
)
NO_SHAPE_SENTENCE = "This dial changes no shape."

# The hidden render-mode dial that isolates the printed body: no see-through
# plug (it is $preview-only anyway) and, for the two-sided file, one plate.
# The print_layout row keeps the file's own layout logic so its two states
# differ.
RENDER_MODE = {ONE_SIDED: ("render_mode", "Body Only"), TWO_SIDED: ("render_mode", "One plate")}
VIEWS_BUILT = ("top", "none")  # C2 adds section-x / section-y
VIEW_CHOICES = ("top", "none", "section", "all")
SECTION_VIEWS = ("section-x", "section-y")

MEASURE_KEYS = (
    "measure_plug_length",
    "measure_plug_width_prong_end",
    "measure_plug_width_cord_end",
    "measure_plug_thickness_prong_end",
    "measure_plug_thickness_cord_end",
    "measure_cord_thickness",
)

# Diff and drawing constants (the planning prototype's values).
MIN_REGION_AREA = 0.4  # mm²
OPEN_CLOSE = 0.02  # mm
POCKET_MIN_AREA = 5.0  # mm²: smaller recess loops are render noise
MARGIN = 6.0  # mm around the outlines
MIN_WIDTH = 64.0  # mm: narrower crops are widened so the words fit
SIMPLIFY = 0.05  # mm
COLOR_OUTLINE = "#000"
COLOR_RECESS = "#333333"
COLOR_PLUG = "#20b2aa"
COLOR_TRACE = "#d81b1b"
DASH_TRACE = "1.2,0.9"
STROKE_OUTER = 0.5
STROKE_INNER = 0.35
STROKE_TRACE = 0.45
FILL_TRACE_OPACITY = 0.10
PLUG_OPACITY = 0.45
TITLE_SIZE = 3.4
LEGEND_SIZE = 2.6
CHAR_W = 0.56  # width of one character as a fraction of the font size


# ---------------------------------------------------------------------------
# Catalog and mappings
# ---------------------------------------------------------------------------


def load_catalog() -> List[Dict[str, Any]]:
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def load_mapping(file_key: str) -> Dict[str, Dict[str, Any]]:
    data = json.loads(MAPPINGS[file_key].read_text(encoding="utf-8"))
    return {row["openscad_name"]: row for row in data["parameters"]}


def mapping_defaults(mapping: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    return {name: row["default"] for name, row in mapping.items()}


def _same_value(a: Any, b: Any) -> bool:
    if isinstance(a, bool) != isinstance(b, bool):
        return False
    return a == b


def parameter_sets(row: Dict[str, Any], defaults: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """The full ``before`` and ``after`` parameter sets of a catalog row."""
    diagram = row["diagram"]
    base = dict(defaults)
    base.update(diagram.get("context") or {})
    after = dict(base)
    after[row["name"]] = diagram["after"]
    return base, after


def defines_for(file_key: str, row_name: str, params: Dict[str, Any], defaults: Dict[str, Any]) -> Dict[str, Any]:
    """Only the keys that differ from the Customizer defaults, plus the
    render mode that isolates the body."""
    defines = {k: v for k, v in params.items() if not _same_value(v, defaults.get(k))}
    mode_key, mode_value = RENDER_MODE[file_key]
    if not (file_key == TWO_SIDED and row_name == "print_layout"):
        defines[mode_key] = mode_value
    return defines


# ---------------------------------------------------------------------------
# Rendering with a cache
# ---------------------------------------------------------------------------


_INCLUDE_RE = re.compile(r"^\s*(?:include|use)\s*<([^>]+)>", re.MULTILINE)


def scad_sources(scad: Path) -> bytes:
    """The SCAD file's bytes plus those of the files it includes."""
    text = scad.read_bytes()
    out = [text]
    for name in _INCLUDE_RE.findall(text.decode("utf-8", errors="replace")):
        inc = scad.parent / name
        if inc.exists():
            out.append(inc.read_bytes())
    return b"\n".join(out)


def cache_key(file_key: str, defines: Dict[str, Any]) -> str:
    h = hashlib.sha1()
    h.update(json.dumps(sorted(defines.items()), sort_keys=True).encode("utf-8"))
    h.update(scad_sources(SCADS[file_key]))
    return h.hexdigest()[:16]


def make_runner() -> OpenSCADRunner:
    path = CANONICAL_OPENSCAD if CANONICAL_OPENSCAD.exists() else None
    return OpenSCADRunner(openscad_path=path)


@dataclass
class Renderer:
    cache_dir: Path
    force: bool = False
    runner: Optional[OpenSCADRunner] = None
    renders: int = 0
    hits: int = 0
    seconds: float = 0.0

    def render(self, file_key: str, defines: Dict[str, Any]) -> Tuple[Path, Path, bool]:
        """Return (stl, console log, cache hit)."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        key = cache_key(file_key, defines)
        stl = (self.cache_dir / f"{file_key}-{key}.stl").resolve()
        log = stl.with_suffix(".log")
        if stl.exists() and log.exists() and not self.force:
            self.hits += 1
            return stl, log, True
        if self.runner is None:
            self.runner = make_runner()
            logger.info("OpenSCAD: %s", self.runner.version_string)
        res = self.runner.generate_stl(SCADS[file_key], stl, defines)
        log.write_text(res.stdout + res.stderr, encoding="utf-8")
        self.renders += 1
        self.seconds += res.duration_seconds
        if not res.success or not stl.exists():
            raise RuntimeError(
                f"render failed for {file_key} {defines}:\n{res.stderr[-800:]}"
            )
        return stl, log, False


def warning_tags(log: Path) -> List[str]:
    text = log.read_text(encoding="utf-8", errors="replace")
    return [line.strip() for line in text.splitlines() if "WARNING:" in line]


# ---------------------------------------------------------------------------
# Top views
# ---------------------------------------------------------------------------


def largest_body(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    """Warning coupons export as extra text bodies: keep the biggest body."""
    parts = mesh.split(only_watertight=False)
    if len(parts) <= 1:
        return mesh
    return max(parts, key=lambda p: abs(p.volume))


@dataclass
class Outline:
    """A top view: solid polygons (through-holes as interiors) and the
    recess polygons that are open at the top face."""

    solids: List[Polygon] = field(default_factory=list)
    recess: List[Polygon] = field(default_factory=list)

    @property
    def filled(self):
        solid = _fix(shapely.union_all(self.solids)) if self.solids else Polygon()
        if not self.recess:
            return solid
        return _fix(solid.difference(_fix(shapely.union_all(self.recess))))

    @property
    def bounds(self) -> Tuple[float, float, float, float]:
        geoms = self.solids + self.recess
        return shapely.union_all(geoms).bounds


def effective_measurements(file_key: str, params: Dict[str, Any]) -> Dict[str, float]:
    """The plug numbers the tool builds with: the preset's when one is
    chosen, the Step 1 dials otherwise."""
    preset = params.get("plug_preset", "Measure my plug")
    if preset != "Measure my plug":
        for plug in PLUG_PRESETS.values():
            if plug["customizer"] == preset and file_key in plug["files"]:
                return dict(plug["measurements"])
        raise KeyError(f"no measurements for the preset {preset!r} in {file_key}")
    return {k: params[k] for k in MEASURE_KEYS if k in params}


def pocket_section_z(params: Dict[str, Any]) -> float:
    """Just above the higher pocket floor: the recess exists there and the
    top-edge roundover has barely started."""
    if params.get("size") == "Custom":
        seat = float(params["custom_pocket_seat_floor"])
        floor = float(params["custom_pocket_floor"])
    else:
        meas = {k: v for k, v in params.items() if k in fit_formulas.DEFAULT_MEASUREMENTS}
        meas.update(effective_measurements(ONE_SIDED, params))
        d = fit_formulas.derive(meas)
        seat, floor = d["pocket_seat_floor"], d["pocket_floor"]
    return max(seat, floor) + 0.15


def outline_one_sided(mesh: trimesh.Trimesh, params: Dict[str, Any]) -> Outline:
    body = sorted(as_polygons(silhouette(mesh)), key=lambda p: p.area, reverse=True)[0]
    z = pocket_section_z(params)
    s_filled = filled_union(section_rings(mesh, z))
    recess_geo = _fix(body.difference(s_filled)).buffer(-0.05).buffer(0.05)
    recess = [p for p in as_polygons(recess_geo) if p.area > POCKET_MIN_AREA]
    return Outline(solids=[body], recess=recess)


def outline_two_sided(mesh: trimesh.Trimesh) -> Outline:
    zmax = mesh.bounds[1][2]
    polys = rings_to_polygons(section_rings(mesh, zmax - 0.05))
    return Outline(solids=polys, recess=[])


def top_view(file_key: str, stl: Path, params: Dict[str, Any]) -> Outline:
    mesh = largest_body(trimesh.load(stl, force="mesh"))
    if file_key == ONE_SIDED:
        return outline_one_sided(mesh, params)
    return outline_two_sided(mesh)


# ---------------------------------------------------------------------------
# The diff and the plug
# ---------------------------------------------------------------------------


def _regions_of(diff) -> Tuple[List[Polygon], float]:
    """Split a raw difference into the regions worth drawing: closed by
    0.02 mm so a band pinched at a crossing point stays one region (the
    planning prototype's counts), then every part that is thinner than
    0.04 mm everywhere (render noise: an opening would delete it) or under
    0.4 mm² is dropped."""
    closed = _fix(diff).buffer(OPEN_CLOSE).buffer(-OPEN_CLOSE)
    regions = [
        p for p in as_polygons(closed)
        if p.area >= MIN_REGION_AREA and not p.buffer(-OPEN_CLOSE).is_empty
    ]
    return regions, float(sum(p.area for p in regions))


def changed_regions(before, after) -> Tuple[List[Polygon], float]:
    """The regions where ``after`` differs from ``before`` (two filled
    geometries)."""
    return _regions_of(after.symmetric_difference(before))


def outline_regions(before: Outline, after: Outline) -> Tuple[List[Polygon], float]:
    """The changed regions of two top views: the solids' difference (the
    outer edge and every through-hole, even one that sits inside the
    recess) united with the recess rings' difference."""
    def _union(polys: Sequence[Polygon]):
        return _fix(shapely.union_all(list(polys))) if polys else Polygon()

    solids = _fix(_union(after.solids).symmetric_difference(_union(before.solids)))
    recess = _fix(_union(after.recess).symmetric_difference(_union(before.recess)))
    return _regions_of(solids.union(recess))


def plug_polygon(file_key: str, params: Dict[str, Any], outline: Outline) -> Polygon:
    """The plug as the tool places it: a trapezoid from the prong-end width
    at the plate end to the cord-end width over the plug length."""
    m = effective_measurements(file_key, params)
    x0, _y0, x1, y1 = shapely.union_all(outline.solids).bounds
    cx = (x0 + x1) / 2
    length = m["measure_plug_length"]
    w_prong = m["measure_plug_width_prong_end"]
    w_cord = m["measure_plug_width_cord_end"]
    y_prong = y1 + (2.0 if file_key == TWO_SIDED else 0.0)
    y_cord = y1 - length
    return Polygon([
        (cx - w_prong / 2, y_prong),
        (cx + w_prong / 2, y_prong),
        (cx + w_cord / 2, y_cord),
        (cx - w_cord / 2, y_cord),
    ])


# ---------------------------------------------------------------------------
# SVG composition
# ---------------------------------------------------------------------------


def _esc(text: str) -> str:
    return html.escape(str(text), quote=False)


def _fmt_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _fit_size(text: str, width: float, size: float, floor: float = 2.0) -> float:
    need = CHAR_W * size * max(1, len(text))
    if need <= width:
        return size
    return max(floor, width / (CHAR_W * len(text)))


class _Frame:
    """Model millimetres to SVG user units: x shifted, y flipped so the
    plate end (largest y) sits at the top of the picture. Everything drawn
    is clipped to the drawing box in model space first, so no renderer has
    to honour an SVG clip path."""

    def __init__(self, x0: float, y0: float, x1: float, y1: float, top: float) -> None:
        self.x0, self.y1, self.top = x0, y1, top
        self.box = shapely.box(x0, y0, x1, y1)

    def _pts(self, coords: Iterable[Tuple[float, float]]) -> str:
        return " L ".join(f"{x - self.x0:.2f} {self.top + (self.y1 - y):.2f}" for x, y in coords)

    def ring_paths(self, coords) -> List[str]:
        """A closed ring as one closed path, or as open pieces where the
        drawing box cuts it."""
        line = shapely.simplify(LineString(coords), SIMPLIFY, preserve_topology=True)
        if self.box.contains(line):
            return ["M " + self._pts(line.coords) + " Z"]
        clipped = line.intersection(self.box)
        pieces = [g for g in getattr(clipped, "geoms", [clipped]) if isinstance(g, LineString) and not g.is_empty]
        return ["M " + self._pts(g.coords) for g in pieces]

    def polygon_path(self, poly: Polygon) -> str:
        """A polygon with its holes (even-odd), clipped to the drawing box."""
        clipped = shapely.simplify(poly.intersection(self.box), SIMPLIFY, preserve_topology=True)
        parts = []
        for p in as_polygons(clipped):
            parts.append("M " + self._pts(p.exterior.coords) + " Z")
            parts.extend("M " + self._pts(i.coords) + " Z" for i in p.interiors)
        return " ".join(parts)


def _stroke_paths(frame: _Frame, coords, color: str, width: float, dash: Optional[str] = None) -> List[str]:
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    return [
        f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" '
        f'stroke-linejoin="round" stroke-linecap="round"{dd}/>'
        for d in frame.ring_paths(coords)
    ]


def _filled_polygon(frame: _Frame, poly: Polygon, color: str, opacity: float,
                    stroke: Optional[str] = None, width: float = 0.0,
                    dash: Optional[str] = None) -> str:
    d = frame.polygon_path(poly)
    if not d:
        return ""
    st = (f' stroke="{stroke}" stroke-width="{width}" stroke-linejoin="round"'
          + (f' stroke-dasharray="{dash}"' if dash else "")) if stroke else ' stroke="none"'
    return (f'<path d="{d}" fill="{color}" fill-rule="evenodd" '
            f'fill-opacity="{opacity}"{st}/>')


def _outline_from_filled(geom) -> Outline:
    return Outline(solids=list(as_polygons(geom)), recess=[])


def _draw_outline(frame: _Frame, outline: Outline, color: str, dashed_all: bool,
                  width_outer: float, width_inner: float) -> List[str]:
    out: List[str] = []
    # The drawn rings are cleaned of render noise (specks and slivers), as
    # the outline sheets do; the diff itself works on the raw geometry.
    for raw in outline.solids:
        poly = clean_polygon(raw)
        if poly is None:
            continue
        out.extend(_stroke_paths(frame, poly.exterior.coords, color, width_outer,
                                 DASH_TRACE if dashed_all else None))
        for ring in poly.interiors:
            out.extend(_stroke_paths(frame, ring.coords, color, width_inner,
                                     DASH_TRACE if dashed_all else DASH_HOLE))
    for raw in outline.recess:
        poly = clean_polygon(raw)
        if poly is None:
            continue
        for ring in [poly.exterior] + list(poly.interiors):
            out.extend(_stroke_paths(frame, ring.coords, color if dashed_all else COLOR_RECESS,
                                     width_inner, DASH_TRACE if dashed_all else DASH_POCKET))
    return out


def _text(x: float, y: float, text: str, size: float, anchor: str = "middle",
          bold: bool = False, fill: str = "#000") -> str:
    fw = ' font-weight="bold"' if bold else ""
    return (f'<text x="{x:.2f}" y="{y:.2f}" font-family="{FONT}" font-size="{size:.2f}"'
            f'{fw} text-anchor="{anchor}" fill="{fill}">{_esc(text)}</text>')


def compose_svg(
    before,
    after,
    plug: Optional[Polygon],
    title: str,
    changes: str,
    name: str,
    before_value: Any,
    after_value: Any,
    context: Dict[str, Any],
    style: str,
    crop: Optional[Sequence[float]],
    before_outline: Optional[Outline] = None,
    after_outline: Optional[Outline] = None,
    regions: Optional[List[Polygon]] = None,
) -> str:
    """The diagram as SVG text (1 unit = 1 mm).

    ``before`` and ``after`` are the filled top-view geometries the picture
    is framed on; the outlines drawn are ``before_outline`` /
    ``after_outline`` when given (solids with their through-holes, plus the
    recess), else the filled geometries themselves. ``regions`` are the
    changed regions to trace; when omitted they are the difference of the
    two filled geometries.
    """
    b_out = before_outline or _outline_from_filled(before)
    a_out = after_outline or _outline_from_filled(after)
    if regions is None:
        regions, _area = changed_regions(before, after)

    if crop:
        x0, y0, x1, y1 = (float(v) for v in crop)
    else:
        bx0, by0, bx1, by1 = shapely.union_all([before, after]).bounds
        x0, y0, x1, y1 = bx0 - MARGIN, by0 - MARGIN, bx1 + MARGIN, by1 + MARGIN
    if x1 - x0 < MIN_WIDTH:
        pad = (MIN_WIDTH - (x1 - x0)) / 2
        x0, x1 = x0 - pad, x1 + pad
    width = x1 - x0

    ctx = ", ".join(f"{k}: {_fmt_value(v)}" for k, v in (context or {}).items())
    title_lines: List[Tuple[str, bool]] = [
        (name, True),
        (f"{_fmt_value(before_value)} \u2192 {_fmt_value(after_value)}", False),
    ]
    if ctx:
        title_lines.append((f"({ctx})", False))
    title_sizes = [_fit_size(t, width - 4, TITLE_SIZE) for t, _ in title_lines]
    top = 2.0 + sum(s * 1.25 for s in title_sizes)

    legend_size = _fit_size(LEGEND_LINE, width - 4, LEGEND_SIZE, floor=LEGEND_SIZE)
    if CHAR_W * legend_size * len(LEGEND_LINE) <= width - 4:
        legend_lines = [LEGEND_LINE]
    else:
        legend_lines = LEGEND_LINE.split("; ")
        legend_lines = [ln + ";" for ln in legend_lines[:-1]] + legend_lines[-1:]
    legend_h = 1.5 + len(legend_lines) * legend_size * 1.3
    height = top + (y1 - y0) + legend_h

    frame = _Frame(x0, y0, x1, y1, top)
    desc = f"{changes} Before: {_fmt_value(before_value)}. After: {_fmt_value(after_value)}."
    svg: List[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.2f}mm" height="{height:.2f}mm" '
        f'viewBox="0 0 {width:.2f} {height:.2f}" role="img">',
        f'<title>{_esc(title)}</title>',
        f'<desc>{_esc(desc)}</desc>',
        f'<rect width="{width:.2f}" height="{height:.2f}" fill="white"/>',
    ]
    y = 2.0
    for (text, bold), size in zip(title_lines, title_sizes):
        y += size
        svg.append(_text(width / 2, y, text, size, bold=bold))
        y += size * 0.25
    if plug is not None:
        svg.append(_filled_polygon(frame, plug, COLOR_PLUG, PLUG_OPACITY))
    svg.extend(_draw_outline(frame, b_out, COLOR_OUTLINE, False, STROKE_OUTER, STROKE_INNER))
    if style == "trace":
        svg.extend(_draw_outline(frame, a_out, COLOR_TRACE, True, STROKE_TRACE, STROKE_TRACE))
    else:
        for region in regions:
            svg.append(_filled_polygon(frame, region, COLOR_TRACE, FILL_TRACE_OPACITY,
                                       stroke=COLOR_TRACE, width=STROKE_TRACE, dash=DASH_TRACE))
    svg = [line for line in svg if line]
    y = top + (y1 - y0) + 1.0
    for line in legend_lines:
        y += legend_size
        svg.append(_text(width / 2, y, line, legend_size, fill="#444444"))
        y += legend_size * 0.3
    svg.append("</svg>")
    return "\n".join(svg) + "\n"


def compose_none_svg(note: str, title: str = "", name: str = "") -> str:
    """A 120 x 40 mm card for a dial that changes no shape."""
    width, height = 120.0, 40.0
    body_lines = textwrap.wrap(note or "", width=76)
    desc = f"{NO_SHAPE_SENTENCE} {note}".strip()
    svg = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}mm" height="{height:.0f}mm" '
        f'viewBox="0 0 {width:.0f} {height:.0f}" role="img">',
        f'<title>{_esc(title or name)}</title>',
        f'<desc>{_esc(desc)}</desc>',
        f'<rect width="{width:.0f}" height="{height:.0f}" fill="white"/>',
        f'<rect x="0.5" y="0.5" width="{width - 1:.0f}" height="{height - 1:.0f}" fill="none" '
        f'stroke="#999999" stroke-width="0.4" stroke-dasharray="{DASH_HOLE}"/>',
    ]
    y = 8.0
    if name:
        svg.append(_text(width / 2, y, name, TITLE_SIZE, bold=True))
        y += 6.0
    svg.append(_text(width / 2, y, NO_SHAPE_SENTENCE, 3.2))
    y += 5.5
    for line in body_lines:
        svg.append(_text(width / 2, y, line, LEGEND_SIZE, fill="#444444"))
        y += 3.6
    svg.append("</svg>")
    return "\n".join(svg) + "\n"


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def svg_relpath(row: Dict[str, Any]) -> str:
    return f"{row['file']}/{row['name']}.svg"


def index_row(row: Dict[str, Any], regions: int, area: float, tags: List[str]) -> Dict[str, Any]:
    d = row["diagram"]
    return {
        "file": row["file"],
        "name": row["name"],
        "view": d["view"],
        "style": d["style"],
        "before": d["before"],
        "after": d["after"],
        "context": d.get("context") or {},
        "plug": d.get("plug", "default"),
        "regions": regions,
        "changed_area_mm2": round(area, 1),
        "tags": tags,
        "svg": svg_relpath(row),
    }


def build_none(row: Dict[str, Any], out_dir: Path) -> Dict[str, Any]:
    svg = compose_none_svg(note=row.get("note") or "", title=row["title"], name=row["name"])
    path = out_dir / svg_relpath(row)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")
    return index_row(row, 0, 0.0, [])


def build_top(row: Dict[str, Any], renderer: Renderer, defaults: Dict[str, Any], out_dir: Path) -> Dict[str, Any]:
    file_key = row["file"]
    d = row["diagram"]
    base, after_params = parameter_sets(row, defaults)
    tags: List[str] = []
    outlines = []
    for params in (base, after_params):
        defines = defines_for(file_key, row["name"], params, defaults)
        stl, log, _hit = renderer.render(file_key, defines)
        tags.extend(t for t in warning_tags(log) if t not in tags)
        outlines.append(top_view(file_key, stl, params))
    b_out, a_out = outlines
    plug = plug_polygon(file_key, after_params, a_out)
    before_filled, after_filled = b_out.filled, a_out.filled
    regions, area = outline_regions(b_out, a_out)
    svg = compose_svg(
        before=before_filled,
        after=after_filled,
        plug=plug,
        title=row["title"],
        changes=row["changes"],
        name=row["name"],
        before_value=d["before"],
        after_value=d["after"],
        context=d.get("context") or {},
        style=d["style"],
        crop=d.get("crop"),
        before_outline=b_out,
        after_outline=a_out,
        regions=regions,
    )
    path = out_dir / svg_relpath(row)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")
    return index_row(row, len(regions), area, tags)


def run_rows(
    rows: Sequence[Dict[str, Any]],
    out_dir: Path,
    cache_dir: Path,
    force: bool = False,
    renderer: Optional[Renderer] = None,
) -> List[Dict[str, Any]]:
    """Build the diagrams of ``rows`` under ``out_dir``; return their index
    rows (rows whose view is not built yet are skipped with a log line)."""
    out_dir = Path(out_dir)
    renderer = renderer or Renderer(cache_dir=Path(cache_dir), force=force)
    defaults = {key: mapping_defaults(load_mapping(key)) for key in SCADS}
    produced: List[Dict[str, Any]] = []
    for row in rows:
        view = row["diagram"]["view"]
        t0 = time.time()
        if view == "none":
            entry = build_none(row, out_dir)
        elif view == "top":
            r0, h0 = renderer.renders, renderer.hits
            entry = build_top(row, renderer, defaults[row["file"]], out_dir)
            logger.info(
                "%s %s: %d region(s), %.1f mm2, %d render(s), %d cache hit(s), %.1f s%s",
                row["file"], row["name"], entry["regions"], entry["changed_area_mm2"],
                renderer.renders - r0, renderer.hits - h0, time.time() - t0,
                f", tags {entry['tags']}" if entry["tags"] else "",
            )
        else:
            logger.warning("%s %s: view %s is not built yet (C2); skipped", row["file"], row["name"], view)
            continue
        produced.append(entry)
    return produced


def write_index(out_dir: Path, produced: Sequence[Dict[str, Any]], catalog: Sequence[Dict[str, Any]]) -> Path:
    """Merge the produced rows into the index, in catalog order; rows not
    rebuilt keep their entries (including C3's ``features``)."""
    path = out_dir / INDEX_NAME
    existing: Dict[Tuple[str, str], Dict[str, Any]] = {}
    if path.exists():
        for entry in json.loads(path.read_text(encoding="utf-8")):
            existing[(entry["file"], entry["name"])] = entry
    for entry in produced:
        key = (entry["file"], entry["name"])
        old = existing.get(key, {})
        merged = dict(old)
        merged.update(entry)
        existing[key] = merged
    order = {(r["file"], r["name"]): i for i, r in enumerate(catalog)}
    rows = sorted(existing.values(), key=lambda e: order.get((e["file"], e["name"]), len(order)))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def select_rows(catalog: Sequence[Dict[str, Any]], files: Sequence[str], only: Sequence[str], views: str) -> List[Dict[str, Any]]:
    if views == "all":
        wanted = set(VIEWS_BUILT)
    elif views == "section":
        wanted = set(SECTION_VIEWS)
    else:
        wanted = {views}
    rows = [r for r in catalog if r["file"] in files and r["diagram"]["view"] in wanted]
    if only:
        rows = [r for r in rows if r["name"] in set(only)]
    return rows


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--file", choices=[ONE_SIDED, TWO_SIDED], help="one tool file (default: both)")
    parser.add_argument("--only", action="append", default=[], metavar="NAME", help="one dial name (repeatable)")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="output folder (default: docs/dials)")
    parser.add_argument("--cache", type=Path, default=DEFAULT_CACHE, help="render cache (default: tmp_renders/dial_diagrams)")
    parser.add_argument("--force", action="store_true", help="re-render even when the cache has the STL")
    parser.add_argument("--views", choices=VIEW_CHOICES, default="all", help="which catalog views to build (default: every view this script supports)")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    catalog = load_catalog()
    files = [args.file] if args.file else [ONE_SIDED, TWO_SIDED]
    rows = select_rows(catalog, files, args.only, args.views)
    if not rows:
        logger.error("no catalog rows match the selection")
        return 1
    t0 = time.time()
    renderer = Renderer(cache_dir=args.cache, force=args.force)
    produced = run_rows(rows, out_dir=args.out, cache_dir=args.cache, force=args.force, renderer=renderer)
    index_path = write_index(args.out, produced, catalog)
    empty = [f"{e['file']}/{e['name']}" for e in produced if e["view"] == "top" and e["regions"] == 0]
    missing = [f"{r['file']}/{r['name']}" for r in rows
               if (r["file"], r["name"]) not in {(e["file"], e["name"]) for e in produced}]
    if empty:
        logger.warning("empty diff (no changed region): %s", ", ".join(empty))
    if missing:
        logger.warning("no SVG produced for: %s", ", ".join(missing))
    logger.info(
        "Summary: %d rows selected, %d SVGs written, %d renders (%.1f s in OpenSCAD), "
        "%d cache hits, %d empty diffs, %.1f s total; index %s",
        len(rows), len(produced), renderer.renders, renderer.seconds, renderer.hits,
        len(empty), time.time() - t0, index_path,
    )
    return 0 if len(produced) == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
