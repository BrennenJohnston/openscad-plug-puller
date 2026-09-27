#!/usr/bin/env python3
"""Draw one diagram per Customizer dial from ``dial_catalog.json``.

For every catalog row the tool is rendered twice with the OpenSCAD CLI: at
its Customizer defaults (plus the row's ``context``) and with the row's dial
moved to its ``after`` value. The top view of each render is extracted with
the outline-sheet helpers (the shadow silhouette with its through-holes plus
the pocket recess for the one-sided puller; the contact-face section for a
two-sided plate; the Z-only dials get a vertical section instead, drawn
with Z up the page), and the symmetric difference of the two views is the
changed geometry of "what this dial moves". Each diagram is an SVG at
1 unit = 1 mm under ``docs/dials/<file>/<name>.svg``. The pair layout (the
default since R3, FD-48) draws three parts at one scale: the BEFORE panel
(the tool at the dial's default, the plug in teal), an arrow with the two
values, and the AFTER panel (the tool after the dial moved, drawn once in
black, with the pieces of its outline that moved overdrawn in red dots),
numbered dots on the moved edges and a key column beside the picture that
names them; no dial name and no legend inside the picture. A feature that
disappeared is drawn from its old outline in red dots and marked removed.
``--layout single`` keeps the previous one-drawing picture for one release
cycle. Rows whose ``view`` is ``none`` get a small SVG saying the dial
changes no shape. Every SVG carries a ``<title>`` / ``<desc>`` pair.

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

import numpy as np
import shapely
import trimesh
from shapely.geometry import LineString, Point, Polygon

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.generate_outline_sheets import (  # noqa: E402
    CLAM_FINGER_WALL,
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
    clamshell_mirror,
    classify_circle,
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
SECTION_VIEWS = ("section-x", "section-y")
VIEWS_BUILT = ("top", "none") + SECTION_VIEWS
VIEW_CHOICES = ("top", "none", "section", "all")

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


COUPON_FRACTION = 0.01  # a body under 1 % of the largest is a warning coupon's letter


def main_bodies(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    """The tool without its warning coupons: every body at least 1 % of the
    largest one (a two-sided plate with no cable strip is two equal halves,
    and both belong in the picture)."""
    parts = mesh.split(only_watertight=False)
    if len(parts) <= 1:
        return mesh
    biggest = max(abs(p.volume) for p in parts)
    keep = [p for p in parts if abs(p.volume) >= COUPON_FRACTION * biggest]
    return trimesh.util.concatenate(keep) if len(keep) > 1 else keep[0]


def _union(polys: Sequence[Polygon]):
    """The union of polygons that may each be slightly invalid (a section
    ring can self-touch at a rounded edge): every input is fixed first, so
    GEOS does not raise a topology exception on the union."""
    fixed = [_fix(p) for p in polys if not p.is_empty]
    return _fix(shapely.union_all(fixed)) if fixed else Polygon()


@dataclass
class Outline:
    """A top view: solid polygons (through-holes as interiors) and the
    recess polygons that are open at the top face."""

    solids: List[Polygon] = field(default_factory=list)
    recess: List[Polygon] = field(default_factory=list)

    @property
    def filled(self):
        solid = _union(self.solids)
        if not self.recess:
            return solid
        return _fix(solid.difference(_union(self.recess)))

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
    mesh = main_bodies(trimesh.load(stl, force="mesh"))
    if file_key == ONE_SIDED:
        return outline_one_sided(mesh, params)
    return outline_two_sided(mesh)


# ---------------------------------------------------------------------------
# Section views (the Z-only dials)
# ---------------------------------------------------------------------------
#
# A vertical cut through the body, drawn with Z up the page. ``axis`` "x" is
# the plane x = at: the page's horizontal axis is the model's Y, mirrored so
# the plate end (largest Y) points LEFT; "y" is the plane y = at: the page's
# horizontal axis is the model's X. The rings come straight from the 3-D
# section (the cut plane is axis-aligned, so dropping the constant
# coordinate is the projection; no reprojection frame involved).


def section_polygons(mesh: trimesh.Trimesh, axis: str, at: float) -> List[Polygon]:
    if axis == "x":
        origin, normal, cols, sign = [at, 0.0, 0.0], [1.0, 0.0, 0.0], (1, 2), -1.0
    elif axis == "y":
        origin, normal, cols, sign = [0.0, at, 0.0], [0.0, 1.0, 0.0], (0, 2), 1.0
    else:
        raise ValueError(f"axis must be 'x' or 'y', not {axis!r}")
    sec = mesh.section(plane_origin=origin, plane_normal=normal)
    if sec is None:
        return []
    rings = []
    for d in sec.discrete:
        r = np.asarray(d)[:, cols].copy()
        r[:, 0] *= sign
        rings.append(r)
    return rings_to_polygons(rings)


def section_view(stl: Path, view: str, at: float) -> Tuple[Outline, Tuple[float, float, float]]:
    """The section polygons of the largest body as an Outline, plus the
    body's (ymin, ymax, zmax) for placing the plug."""
    mesh = main_bodies(trimesh.load(stl, force="mesh"))
    axis = "x" if view == "section-x" else "y"
    polys = section_polygons(mesh, axis, at)
    if not polys:
        raise RuntimeError(f"the plane {axis} = {at} misses the body ({stl.name})")
    (_x0, y0, _z0), (_x1, y1, z1) = mesh.bounds
    return Outline(solids=polys, recess=[]), (float(y0), float(y1), float(z1))


def pocket_floor_z(params: Dict[str, Any]) -> float:
    if params.get("size") == "Custom":
        return float(params["custom_pocket_floor"])
    meas = {k: v for k, v in params.items() if k in fit_formulas.DEFAULT_MEASUREMENTS}
    meas.update(effective_measurements(ONE_SIDED, params))
    return float(fit_formulas.derive(meas)["pocket_floor"])


def section_plug_polygon(file_key: str, params: Dict[str, Any], view: str, at: float,
                         body: Tuple[float, float, float]) -> Optional[Polygon]:
    """The plug in the cut, or None when the plane does not pass through it.

    One-sided, section-x: length (page X, plate end left) by thickness
    (page Y), standing on the pocket floor, thickness at the prong end at
    the plate end. Two-sided, section-y: the plug's width at that station
    by the plate thickness, centred on the channel and on the plate's
    mid-height.
    """
    m = effective_measurements(file_key, params)
    _y0, y1, z1 = body
    length = m["measure_plug_length"]
    if file_key == ONE_SIDED:
        if view != "section-x" or abs(at) > m["measure_plug_width_prong_end"] / 2:
            return None
        floor = pocket_floor_z(params)
        u_plate, u_cord = -y1, -(y1 - length)
        t_prong = m["measure_plug_thickness_prong_end"]
        t_cord = m["measure_plug_thickness_cord_end"]
        return Polygon([(u_plate, floor), (u_cord, floor),
                        (u_cord, floor + t_cord), (u_plate, floor + t_prong)])
    if view != "section-y":
        return None
    y_back = y1 - length
    if not (y_back <= at <= y1 + 2.0):
        return None
    f = min(1.0, max(0.0, (at - y_back) / max(1e-6, length)))
    w = m["measure_plug_width_cord_end"] + f * (m["measure_plug_width_prong_end"] - m["measure_plug_width_cord_end"])
    mid = z1 / 2
    return Polygon([(-w / 2, mid - z1 / 2), (w / 2, mid - z1 / 2), (w / 2, mid + z1 / 2), (-w / 2, mid + z1 / 2)])


# ---------------------------------------------------------------------------
# The diff and the plug
# ---------------------------------------------------------------------------


def _regions_of(diff) -> Tuple[List[Polygon], float]:
    """Split a raw difference into the regions worth drawing: closed by
    0.02 mm so a band pinched at a crossing point stays one region (the
    planning prototype's counts), then every part that is thinner than
    0.04 mm everywhere (render noise: an opening would delete it) or under
    0.4 mm² is dropped."""
    # Zero-area parts (degenerate polygons a symmetric difference leaves
    # along shared edges) are dropped first, and the erosion runs part by
    # part: GEOS 3.13 erodes a multipolygon that still carries them to
    # nothing (an 11.4 mm² band vanished once in three renders of the
    # plug-thickness rows before this).
    parts = [p for p in as_polygons(_fix(diff)) if p.area > 1e-6]
    if not parts:
        return [], 0.0
    # The dilated parts are snapped to a 1e-6 mm grid before the union:
    # GEOS raised a non-noded intersection on the countersink row's
    # near-coincident sliver edges without it.
    dilated = _union([shapely.set_precision(p.buffer(OPEN_CLOSE), 1e-6) for p in parts])
    closed = _union([q.buffer(-OPEN_CLOSE) for q in as_polygons(dilated)])
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
# Feature names: which part of the tool a changed region sits on
# ---------------------------------------------------------------------------
#
# Footprints are built in the top view's coordinates from the numbers the
# outline-sheet script uses (the fit formulas, the clamshell mirror, the
# circle classifier) and from the BEFORE outline's own holes. Each changed
# region is named after the first footprint, in the order below (the most
# specific first), that covers at least a quarter of it; failing that, the
# footprint that covers most of it; failing that, the body's or plate's
# edge.

FEATURE_FALLBACK = {ONE_SIDED: "body edge", TWO_SIDED: "plate edge"}
FOOTPRINT_PAD = 1.5  # mm: a moved edge's region lies just outside its old footprint
HOLE_PAD = 1.5  # mm: the holes of both states are in the footprint, so a small pad does
SPECIFIC_SHARE = 0.5  # a hole, slot or tooth band owns a region it covers this much of
BROAD_SHARE = 0.15  # a pocket, notch, lobe, channel or arm owns a region it covers this much of
FALLBACK_SHARE = 0.10  # below this the region is the body's or plate's edge
COVERED_SHARE = 0.5  # a region that covers this much of a footprint's own area names it
WHOLE_BODY_SHARE = 0.25  # a region this big against the body is the edge's too
EDGE_BAND = 1.5  # mm: the strip inside the body's outer edge
EDGE_SHARE = 0.5  # a region lying this much within the strip hugs the edge and is the edge's too
EDGE_CONTACT_SHARE = 0.10  # a region touching this much of the outer edge's length (outside every footprint) is the edge's too
TEETH_DEPTH = 3.0  # mm: the band along the arms' inner edges that the teeth occupy
PROBE_HALF = 0.5  # mm: half the thickness of a section row's probe box


@dataclass
class Footprints:
    """Named regions of the top view. ``specific`` are the holes, slots and
    teeth (padded generously, so a moved hole's region still lands on it);
    ``broad`` are the pocket, notch, seat, hook, lobes, channel and arms,
    each minus the specific cores and the broad ones listed before it."""

    specific: List[Tuple[str, Any]] = field(default_factory=list)
    broad: List[Tuple[str, Any]] = field(default_factory=list)


def _circles(polys: Sequence[Polygon]):
    out = []
    for poly in polys:
        for ring in poly.interiors:
            c = classify_circle(np.asarray(ring.coords))
            if c:
                out.append(c)
    return out


def _disc(c, pad: float = 0.0) -> Polygon:
    return Point(c.cx, c.cy).buffer(c.d / 2 + pad)


def _hole_slots(polys: Sequence[Polygon], min_area: float) -> List[Polygon]:
    out = []
    for poly in polys:
        for ring in poly.interiors:
            coords = np.asarray(ring.coords)
            if classify_circle(coords) is None:
                p = Polygon(coords)
                if p.area > min_area:
                    out.append(p)
    return out


def _assemble(specific_cores: List[Tuple[str, Any, float]], broad: List[Tuple[str, Any]]) -> Footprints:
    """Pad the specific cores by their own pad; pad the broad footprints by
    FOOTPRINT_PAD and make them exclusive of the cores and of each other."""
    fp = Footprints()
    taken = _union([geom for _n, geom, _pad in specific_cores if not geom.is_empty])
    for name, geom, pad in specific_cores:
        if not geom.is_empty:
            fp.specific.append((name, geom.buffer(pad)))
    for name, geom in broad:
        if geom.is_empty:
            continue
        own = _fix(geom.buffer(FOOTPRINT_PAD).difference(taken))
        if not own.is_empty:
            fp.broad.append((name, own))
        taken = _fix(taken.union(geom.buffer(FOOTPRINT_PAD)))
    return fp


def _one_sided_numbers(params: Dict[str, Any]) -> Dict[str, Any]:
    meas = {k: v for k, v in params.items() if k in fit_formulas.DEFAULT_MEASUREMENTS}
    meas.update(effective_measurements(ONE_SIDED, params))
    d = dict(fit_formulas.derive(meas))
    if params.get("size") == "Custom":
        for key in ("pocket_seat_diameter", "plug_wall_notch_width", "plug_wall_notch_height",
                    "t_hook_length", "t_hook_holder_width", "t_hook_catch_reach",
                    "t_hook_tip_drop", "finger_hole_diameter", "zip_tie_hole_diameter"):
            if f"custom_{key}" in params:
                d[key] = float(params[f"custom_{key}"])
    return d


def _hook_box(d: Dict[str, Any], params: Dict[str, Any]) -> Polygon:
    hand = -1.0 if params.get("hook_hand") == "Left" else 1.0
    cl = -d["t_hook_catch_reach"]
    cr = cl + d["t_hook_holder_width"]
    return shapely.box(min(hand * cl, hand * cr), -d["t_hook_tip_drop"] - 1.0,
                       max(hand * cl, hand * cr), d["t_hook_length"])


def footprints_one_sided(params: Dict[str, Any], outline: Outline,
                         after: Optional[Outline] = None,
                         after_params: Optional[Dict[str, Any]] = None) -> Footprints:
    d = _one_sided_numbers(params)
    d2 = _one_sided_numbers(after_params) if after_params else d
    body = max(outline.solids, key=lambda p: p.area)
    top = body.bounds[3]
    solids = list(outline.solids) + (list(after.solids) if after else [])
    circles = _circles(solids)
    fingers = [c for c in circles if abs(c.d - d["finger_hole_diameter"]) < 3.0]
    zips = [c for c in circles if abs(c.d - d["zip_tie_hole_diameter"]) < 2.0]
    wings = _hole_slots(solids, 5.0)
    wing_name = "classic slots" if params.get("velcro_style") == "Classic slot" else "wing openings"
    notch = _union([shapely.box(-x["plug_wall_notch_width"] / 2, top - x["plug_wall_notch_height"],
                                x["plug_wall_notch_width"] / 2, top + 1.0) for x in (d, d2)])
    seat = Point(0.0, top).buffer(max(d["pocket_seat_diameter"], d2["pocket_seat_diameter"]) / 2)
    hook = _union([_hook_box(d, params), _hook_box(d2, after_params or params)])
    recess = _union(list(outline.recess) + (list(after.recess) if after else []))
    specific = [
        ("zip-tie holes", _union([_disc(c) for c in zips]), HOLE_PAD),
        ("finger holes", _union([_disc(c) for c in fingers]), HOLE_PAD),
        (wing_name, _union(wings), FOOTPRINT_PAD),
    ]
    broad = [("wall notch", notch), ("seat", seat), ("hook", hook), ("pocket", recess)]
    return _assemble(specific, broad)


def footprints_two_sided(params: Dict[str, Any], outline: Outline,
                         after: Optional[Outline] = None,
                         after_params: Optional[Dict[str, Any]] = None) -> Footprints:
    m = effective_measurements(TWO_SIDED, params)
    size = params.get("size", "Medium")
    mirror_size = size if size in fit_formulas.FIT_SIZE_TABLE else "Medium"
    cm = clamshell_mirror(mirror_size, {"measurements": m})
    solids = list(outline.solids) + (list(after.solids) if after else [])
    x0, y0, x1, y1 = shapely.union_all(solids).bounds
    circles = _circles(solids)
    zip_d = float(params.get("plate_zip_hole_diameter", 4.0))
    fingers = [c for c in circles if abs(c.d - cm["finger_dia"]) < 3.0]
    zips = [c for c in circles if abs(c.d - zip_d) < 1.5]
    slots = _hole_slots(solids, 20.0)
    lobes = _union([_disc(c, CLAM_FINGER_WALL) for c in fingers])
    plug = plug_polygon(TWO_SIDED, params, outline)
    teeth = plug.buffer(TEETH_DEPTH).difference(plug).intersection(
        shapely.box(x0 - 1.0, y1 - m["measure_plug_length"], x1 + 1.0, y1 + 3.0))
    channel = shapely.box(-cm["cable_gap"] / 2 - 2.0, y0 - 1.0, cm["cable_gap"] / 2 + 2.0, cm["throat_y0"] + 2.0)
    arms = shapely.box(x0 - 1.0, cm["throat_y0"], x1 + 1.0, y1 + 1.0)
    specific = [
        ("zip stations", _union([_disc(c) for c in zips]), HOLE_PAD),
        ("strap slot", _union(slots), FOOTPRINT_PAD),
        ("teeth", teeth, FOOTPRINT_PAD),
    ]
    broad = [("finger lobes", lobes), ("cord channel", channel), ("arms", arms)]
    return _assemble(specific, broad)


def footprints(file_key: str, params: Dict[str, Any], outline: Outline,
               after: Optional[Outline] = None,
               after_params: Optional[Dict[str, Any]] = None) -> Footprints:
    """The named footprints from the BEFORE outline's numbers; the holes and
    slots of the AFTER outline join them so a hole that appears or moves is
    covered too."""
    if file_key == ONE_SIDED:
        return footprints_one_sided(params, outline, after, after_params)
    return footprints_two_sided(params, outline, after, after_params)


def _section_probe(region: Polygon, view: str, at: float) -> Polygon:
    """A section region mapped back onto the top view: a thin box along the
    cut plane over the region's span."""
    u0, _v0, u1, _v1 = region.bounds
    if view == "section-x":
        return shapely.box(at - PROBE_HALF, -u1, at + PROBE_HALF, -u0)
    return shapely.box(u0, at - PROBE_HALF, u1, at + PROBE_HALF)


def classify_regions(file_key: str, regions: Sequence[Polygon], fp: Footprints,
                     view: str = "top", at: float = 0.0,
                     body_area: float = 0.0,
                     edge_rings: Sequence[LineString] = ()) -> List[Tuple[Polygon, List[str]]]:
    """Name every changed region, one name list per region in drawing order
    (the most specific footprint first): the specific footprints (holes,
    slots, teeth) covering at least half of it, the broad ones (pocket,
    notch, seat, hook, lobes, channel, arms) covering at least a sixth of
    it, and any footprint the region itself covers at least half of (a
    region that swallows a whole feature); a region that swallows a quarter
    of the body is also the edge's; a region nothing claims takes the
    footprint covering most of it, if a tenth, else the edge. A region that
    lies mostly within EDGE_BAND of one of ``edge_rings`` (the body's outer
    edge before and after), outside every named footprint, is the edge's too."""
    named: List[Tuple[Polygon, List[str]]] = []
    edge = FEATURE_FALLBACK[file_key]
    order = [n for n, _g in fp.specific] + [n for n, _g in fp.broad] + [edge]
    edge_strip = edge_lines = None
    edge_length = 0.0
    if edge_rings:
        # the strip along the outer edge, minus every named footprint: a notch, a hook slot or a hole
        # cut into the edge belongs to its own feature, not to the edge
        claimed = _union([g for _n, g in list(fp.specific) + list(fp.broad)])
        edge_strip = _fix(_union([r.buffer(EDGE_BAND) for r in edge_rings]).difference(claimed))
        edge_lines = shapely.union_all(list(edge_rings)).difference(claimed)
        edge_length = sum(r.length for r in edge_rings)
    for region in regions:
        probe = region if view == "top" else _section_probe(region, view, at)
        area = max(probe.area, 1e-9)
        hits = set()
        shares: Dict[str, float] = {}
        for tier, threshold in ((fp.specific, SPECIFIC_SHARE), (fp.broad, BROAD_SHARE)):
            for name, geom in tier:
                inter = probe.intersection(geom).area
                shares[name] = inter / area
                if inter / area >= threshold or inter / max(geom.area, 1e-9) >= COVERED_SHARE:
                    hits.add(name)
        if view == "top" and body_area and region.area >= WHOLE_BODY_SHARE * body_area:
            hits.add(edge)
        if view == "top" and edge_strip is not None and region.area > 0:
            hugs = region.intersection(edge_strip).area / region.area >= EDGE_SHARE
            contact = region.buffer(EDGE_BAND).intersection(edge_lines).length / max(edge_length, 1e-9)
            if hugs or contact >= EDGE_CONTACT_SHARE:
                hits.add(edge)
        if not hits and shares and view == "top":
            # A section probe is a thin box across the whole cut: a feature it
            # merely grazes must not name it, so the tenth-share fallback is
            # for top views only.
            best = max(shares, key=shares.get)
            if shares[best] >= FALLBACK_SHARE:
                hits.add(best)
        names = sorted(hits or {edge}, key=lambda n: order.index(n) if n in order else len(order))
        named.append((region, names))
    return named


def feature_names(named: Sequence[Tuple[Polygon, Sequence[str]]]) -> List[str]:
    """The sorted, distinct feature names of a row (the index's ``features``)."""
    return sorted({n for _region, names in named for n in names})


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
        bx0, by0, bx1, by1 = shapely.union_all([before, after] + ([plug] if plug is not None else [])).bounds
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
# The pair picture (R3, FD-48): before | arrow | after, the moved edges in red
# ---------------------------------------------------------------------------

PAIR_VIEWS = ("top",)  # B2 brings the section views into the same layout
# Rows drawn as ONE panel of their default state with no marks: a layout switch
# moves everything, so "what moved" says nothing (the two-sided print layout
# puts both plates side by side; its picture is what you print).
SINGLE_PANEL_ROWS = {(TWO_SIDED, "print_layout")}
PAIR_GAP = 10.0  # mm between the panels; the arrow lives here
KEY_W = 34.0  # mm, the key column beside the after panel
KEY_PAD = 3.0
KEY_LINE = 4.0  # mm between key entries
KEY_SUBLINE = 3.1  # mm between the wrapped lines of one entry
KEY_SIZE = 2.6
KEY_WRAP_MM = KEY_W - KEY_PAD - 1.0
ARROW_W = 0.6
ARROW_HEAD = 2.5
VALUES_SIZE = 2.8
STRIP_LINE = 3.4  # mm per values line when the values go under the panels
CALLOUT_D = 2.6  # mm, the numbered dot
CALLOUT_STROKE = 0.35
CALLOUT_TEXT = 2.2
LEADER_W = 0.3
LEADER_MIN_MM2 = 2.0  # a region smaller than this never carries the number's leader
EDGE_TOL = 0.2  # mm: an after edge within this of a before edge did not move (render jitter is under 0.1)
MIN_ARC = 0.6  # mm: shorter moved pieces are noise
ARC_TOUCH = 0.5  # mm: an arc this close to a region bounds it
REMOVED_MIN_MM2 = 5.0  # a region with no moved edge is a removed feature only from this size
REMOVED_SUFFIX = " (removed)"
DOTS_PER_NUMBER = 6  # a number shared by more regions than this shows its dot on the leadered region only
DOT_W = 0.6  # the red dotted stroke; round caps make 0.6 mm dots at a 1.1 mm pitch
DOT_DASH = "0.01,1.1"
DIM_HEADROOM = 7.0  # mm added to the panel box on a dimension callout's side
DIM_EXT_W = 0.25
DIM_LINE_W = 0.3
DIM_ARROW = 1.5
DIM_TEXT = 2.6


def _as_outline(geom) -> Outline:
    return geom if isinstance(geom, Outline) else _outline_from_filled(geom)


def _drawn_rings(outline: Outline) -> List[List[Tuple[float, float]]]:
    """The rings _draw_outline() draws (cleaned), as coordinate lists."""
    rings: List[List[Tuple[float, float]]] = []
    for raw in list(outline.solids) + list(outline.recess):
        poly = clean_polygon(raw)
        if poly is None:
            continue
        rings.append(list(poly.exterior.coords))
        rings.extend(list(i.coords) for i in poly.interiors)
    return rings


def moved_arcs(after_out: Outline, before_out: Outline) -> List[LineString]:
    """The pieces of the after outline's rings farther than EDGE_TOL from every
    ring of the before outline: the edges the dial moved."""
    before = [LineString(r) for r in _drawn_rings(before_out)]
    guard = shapely.union_all(before).buffer(EDGE_TOL) if before else None
    arcs: List[LineString] = []
    for coords in _drawn_rings(after_out):
        line = LineString(coords)
        moved = line.difference(guard) if guard is not None else line
        for g in shapely.get_parts(moved):
            if isinstance(g, LineString) and g.length >= MIN_ARC:
                arcs.append(g)
    return arcs


def _arc_owner(arc: LineString, regions: Sequence[Polygon]) -> Optional[int]:
    """The region the arc bounds: the one nearest to the arc's quarter points,
    if all three lie within ARC_TOUCH of it."""
    probes = [arc.interpolate(f, normalized=True) for f in (0.25, 0.5, 0.75)]
    best, best_d = None, None
    for i, region in enumerate(regions):
        d = max(region.distance(pt) for pt in probes)
        if d <= ARC_TOUCH and (best_d is None or d < best_d):
            best, best_d = i, d
    return best


def wrap_key(line: str) -> List[str]:
    words = line.split(" ")
    out: List[str] = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if cur and CHAR_W * KEY_SIZE * len(trial) > KEY_WRAP_MM:
            out.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        out.append(cur)
    return out


@dataclass
class PairPlan:
    """What the pair picture marks: the regions that get a dot (specks with no
    moved edge dropped), their arcs, the numbering and the key."""

    regions: List[Tuple[Polygon, List[str]]] = field(default_factory=list)
    arcs: List[LineString] = field(default_factory=list)
    region_arcs: List[List[LineString]] = field(default_factory=list)
    removed: List[bool] = field(default_factory=list)
    number_of: List[int] = field(default_factory=list)
    key_lines: List[str] = field(default_factory=list)
    dots: List[Point] = field(default_factory=list)

    @property
    def key_rows(self) -> List[List[Any]]:
        """The key as index data: ``[number, names, removed]`` per entry."""
        rows: Dict[int, List[Any]] = {}
        for (region, names), n, rm in zip(self.regions, self.number_of, self.removed):
            row = rows.setdefault(n, [n, list(names), True])
            row[2] = row[2] and rm
        return [rows[n] for n in sorted(rows)]


def _dot_point(arcs: Sequence[LineString]) -> Point:
    """The arc vertex nearest the key column: the greatest x, then the highest y."""
    best = None
    for a in arcs:
        for x, y in a.coords:
            if best is None or (x, y) > best:
                best = (x, y)
    return Point(best)


def plan_callouts(before_out: Outline, after_out: Outline,
                  regions_named: Sequence[Tuple[Polygon, Sequence[str]]],
                  box: Optional[Polygon] = None) -> PairPlan:
    """``box`` is the panel's drawing box in model mm (a crop): a region whose
    marks all lie outside it is not numbered, so its leader cannot land on the
    neighbouring panel."""
    arcs = moved_arcs(after_out, before_out)
    all_regions = [r for r, _n in regions_named]
    owner = [_arc_owner(a, all_regions) for a in arcs]
    arcs_of = {i: [a for a, o in zip(arcs, owner) if o == i] for i in range(len(all_regions))}
    plan = PairPlan(arcs=arcs)
    for i, (region, names) in enumerate(regions_named):
        ra = arcs_of[i]
        if not ra and region.area < REMOVED_MIN_MM2:
            continue
        dot = _dot_point(ra) if ra else region.representative_point()
        if box is not None:
            marks = shapely.union_all(ra) if ra else region.exterior
            if not marks.intersects(box):
                continue
            if not box.contains(dot):
                inside = marks.intersection(box)
                dot = inside.representative_point() if not inside.is_empty else dot
        plan.regions.append((region, list(names)))
        plan.region_arcs.append(ra)
        plan.removed.append(not ra)
        plan.dots.append(dot)
    groups: Dict[Tuple[str, ...], List[int]] = {}
    for i, (_region, names) in enumerate(plan.regions):
        groups.setdefault(tuple(names), []).append(i)
    ordered = sorted(groups.items(), key=lambda kv: -max(plan.dots[i].y for i in kv[1]))
    plan.number_of = [0] * len(plan.regions)
    for n, (names, idxs) in enumerate(ordered, start=1):
        for i in idxs:
            plan.number_of[i] = n
        suffix = REMOVED_SUFFIX if all(plan.removed[i] for i in idxs) else ""
        plan.key_lines.append(f"{n} {' / '.join(names)}{suffix}")
    return plan


def _values_lines(before_value: Any, after_value: Any, unit: Optional[str],
                  section: Optional[Tuple[str, float]]) -> List[str]:
    if isinstance(before_value, str) or isinstance(after_value, str):
        lines = [f"{_fmt_value(before_value)}", f"\u2192 {_fmt_value(after_value)}"]
    else:
        lines = [f"{_fmt_value(before_value)} \u2192 {_fmt_value(after_value)}" + (f" {unit}" if unit else "")]
    if section:
        axis = "x" if section[0] == "section-x" else "y"
        lines.append(f"section at {axis} = {_fmt_value(section[1])} mm")
    return lines


def _svg_arrow_h(x0: float, x1: float, y: float) -> str:
    hx = x1 - ARROW_HEAD
    return (f'<line x1="{x0:.2f}" y1="{y:.2f}" x2="{hx:.2f}" y2="{y:.2f}" stroke="#000" stroke-width="{ARROW_W}"/>'
            f'<polygon points="{x1:.2f},{y:.2f} {hx:.2f},{y - ARROW_HEAD * 0.45:.2f} {hx:.2f},{y + ARROW_HEAD * 0.45:.2f}" fill="#000"/>')


def _pt(frame: _Frame, x: float, y: float) -> Tuple[float, float]:
    return x - frame.x0, frame.top + (frame.y1 - y)


def _dotted(frame: _Frame, line: LineString, color: str = COLOR_TRACE, width: float = DOT_W,
            dash: str = DOT_DASH) -> str:
    """A dotted line clipped to the drawing box (a crop), as the outlines are."""
    pieces = [g for g in shapely.get_parts(line.intersection(frame.box)) if isinstance(g, LineString) and not g.is_empty]
    return "".join(
        f'<path d="M {frame._pts(g.coords)}" fill="none" stroke="{color}" stroke-width="{width}" '
        f'stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="{dash}"/>'
        for g in pieces
    )


def _dim_arrow(x: float, y: float, direction: float, color: str) -> str:
    bx = x - direction * DIM_ARROW * 1.6
    return f'<polygon points="{x:.2f},{y:.2f} {bx:.2f},{y - DIM_ARROW * 0.35:.2f} {bx:.2f},{y + DIM_ARROW * 0.35:.2f}" fill="{color}"/>'


def draw_dimension(frame: _Frame, dim: Dict[str, Any]) -> List[str]:
    """A horizontal dimension callout in the after panel, the outline sheets'
    conventions: extension lines from the object's edge (``y_obj``), a line at
    ``y_dim`` between ``x0`` and ``x1`` with two arrow heads, the ``label``
    above it. The white halo is a separate text under the red one (an SVG
    rasterizer may ignore paint-order)."""
    c = COLOR_TRACE
    (xa, ya), (xb, _yb) = _pt(frame, dim["x0"], dim["y_dim"]), _pt(frame, dim["x1"], dim["y_dim"])
    (_xo, yo) = _pt(frame, dim["x0"], dim["y_obj"])
    over = 1.0 if ya < yo else -1.0
    out = ['<g class="dimension">']
    for x in (xa, xb):
        out.append(f'<line x1="{x:.2f}" y1="{yo:.2f}" x2="{x:.2f}" y2="{ya - over:.2f}" stroke="{c}" stroke-width="{DIM_EXT_W}"/>')
    if (xb - xa) < 11.0:
        out.append(f'<line x1="{xa - 5:.2f}" y1="{ya:.2f}" x2="{xb + 5:.2f}" y2="{ya:.2f}" stroke="{c}" stroke-width="{DIM_LINE_W}"/>')
        out.append(_dim_arrow(xa, ya, -1.0, c))
        out.append(_dim_arrow(xb, ya, 1.0, c))
    else:
        out.append(f'<line x1="{xa:.2f}" y1="{ya:.2f}" x2="{xb:.2f}" y2="{ya:.2f}" stroke="{c}" stroke-width="{DIM_LINE_W}"/>')
        out.append(_dim_arrow(xa, ya, 1.0, c))
        out.append(_dim_arrow(xb, ya, -1.0, c))
    tx, ty = (xa + xb) / 2, ya - 1.0
    label = _esc(dim["label"])
    out.append(f'<text x="{tx:.2f}" y="{ty:.2f}" font-family="{FONT}" font-size="{DIM_TEXT}" font-weight="bold" '
               f'text-anchor="middle" fill="white" stroke="white" stroke-width="0.8" stroke-linejoin="round">{label}</text>')
    out.append(f'<text x="{tx:.2f}" y="{ty:.2f}" font-family="{FONT}" font-size="{DIM_TEXT}" font-weight="bold" '
               f'text-anchor="middle" fill="{c}">{label}</text>')
    out.append("</g>")
    return out


def _compose_single_panel(outline: Outline, plug: Optional[Polygon], title: str, changes: str,
                          before_value: Any, after_value: Any, unit: Optional[str],
                          desc: Optional[str]) -> str:
    """One panel of the row's default state in black with the plug, the two
    values in a strip under it, no marks and no key (SINGLE_PANEL_ROWS)."""
    geoms = outline.solids + outline.recess + ([plug] if plug is not None else [])
    bx0, by0, bx1, by1 = shapely.union_all(geoms).bounds
    x0, y0, x1, y1 = bx0 - MARGIN, by0 - MARGIN, bx1 + MARGIN, by1 + MARGIN
    width, height = x1 - x0, y1 - y0
    lines = _values_lines(before_value, after_value, unit, None)
    strip_h = 1.5 + len(lines) * STRIP_LINE
    row_h = height + strip_h
    frame = _Frame(x0, y0, x1, y1, 0.0)
    text = desc or f"{changes} Before: {_fmt_value(before_value)}. After: {_fmt_value(after_value)}."
    svg: List[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.2f}mm" height="{row_h:.2f}mm" '
        f'viewBox="0 0 {width:.2f} {row_h:.2f}" role="img">',
        f'<title>{_esc(title)}</title>',
        f'<desc>{_esc(text)}</desc>',
        f'<rect width="{width:.2f}" height="{row_h:.2f}" fill="white"/>',
        '<g class="panel" id="single">',
    ]
    if plug is not None:
        svg.append(_filled_polygon(frame, plug, COLOR_PLUG, PLUG_OPACITY))
    svg.extend(_draw_outline(frame, outline, COLOR_OUTLINE, False, STROKE_OUTER, STROKE_INNER))
    svg.append("</g>")
    svg.append('<g class="arrow">')
    ty = height + 1.5 + VALUES_SIZE
    for line in lines:
        svg.append(_text(width / 2, ty, line, VALUES_SIZE))
        ty += STRIP_LINE
    svg.append("</g>")
    svg.append("</svg>")
    return "\n".join(s for s in svg if s) + "\n"


def compose_pair_svg(
    before_outline,
    after_outline,
    before_plug: Optional[Polygon],
    after_plug: Optional[Polygon],
    title: str,
    changes: str,
    name: str,
    before_value: Any,
    after_value: Any,
    unit: Optional[str],
    context: Dict[str, Any],
    style: str,
    crop: Optional[Sequence[float]],
    regions_named: Sequence[Tuple[Polygon, Sequence[str]]],
    dimension: Optional[Dict[str, Any]] = None,
    desc: Optional[str] = None,
    section: Optional[Tuple[str, float]] = None,
    plan: Optional[PairPlan] = None,
    single_panel: bool = False,
) -> str:
    """The pair picture as SVG text (1 unit = 1 mm): the BEFORE panel (the
    outline in black, the before plug in teal), a 10 mm gap with the arrow
    and the two values, the AFTER panel (the after outline in black, the
    after plug in teal, the moved edges in red dots, a removed feature from
    its old outline, an optional dimension callout, the numbered dots), and
    the key column with one leader per entry. ``style`` no longer changes
    the drawing (FD-48); ``context`` is the card's text, not the picture's.
    """
    del style, context
    b_out, a_out = _as_outline(before_outline), _as_outline(after_outline)
    if single_panel:
        return _compose_single_panel(b_out, before_plug, title, changes, before_value, after_value, unit, desc)
    if crop:
        x0, y0, x1, y1 = (float(v) for v in crop)
    else:
        geoms = b_out.solids + b_out.recess + a_out.solids + a_out.recess
        geoms += [g for g in (before_plug, after_plug) if g is not None]
        bx0, by0, bx1, by1 = shapely.union_all(geoms).bounds
        x0, y0, x1, y1 = bx0 - MARGIN, by0 - MARGIN, bx1 + MARGIN, by1 + MARGIN
    if dimension:
        if dimension.get("side", "above") == "above":
            y1 += DIM_HEADROOM
        else:
            y0 -= DIM_HEADROOM
    width, height = x1 - x0, y1 - y0
    plan = plan or plan_callouts(b_out, a_out, regions_named, shapely.box(x0, y0, x1, y1) if crop else None)

    key_entries = [wrap_key(line) for line in plan.key_lines]
    key_h = 2.0 + sum(KEY_LINE + (len(e) - 1) * KEY_SUBLINE for e in key_entries) + 1.0
    lines = _values_lines(before_value, after_value, unit, section)
    widest = max(CHAR_W * VALUES_SIZE * len(t) for t in lines)
    # a crop has no margin around the drawing, so only the gap itself may hold the values
    under_arrow = widest <= PAIR_GAP - 1.0 + (0.0 if crop else 2 * MARGIN - 1.0)
    strip_h = 0.0 if under_arrow else 1.5 + len(lines) * STRIP_LINE
    row_w = 2 * width + PAIR_GAP + KEY_W
    row_h = max(height, key_h) + strip_h

    frame = _Frame(x0, y0, x1, y1, 0.0)
    ax = width + PAIR_GAP
    text = desc or f"{changes} Before: {_fmt_value(before_value)}. After: {_fmt_value(after_value)}."
    svg: List[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{row_w:.2f}mm" height="{row_h:.2f}mm" '
        f'viewBox="0 0 {row_w:.2f} {row_h:.2f}" role="img">',
        f'<title>{_esc(title)}</title>',
        f'<desc>{_esc(text)}</desc>',
        f'<rect width="{row_w:.2f}" height="{row_h:.2f}" fill="white"/>',
        '<g class="panel" id="before">',
    ]
    if before_plug is not None:
        svg.append(_filled_polygon(frame, before_plug, COLOR_PLUG, PLUG_OPACITY))
    svg.extend(_draw_outline(frame, b_out, COLOR_OUTLINE, False, STROKE_OUTER, STROKE_INNER))
    svg.append("</g>")
    svg.append('<g class="arrow">')
    mid = height / 2
    svg.append(_svg_arrow_h(width + 1.5, width + PAIR_GAP - 1.5, mid))
    ty = mid + 3.0 + VALUES_SIZE if under_arrow else max(height, key_h) + 1.5 + VALUES_SIZE
    for line in lines:
        svg.append(_text(width + PAIR_GAP / 2, ty, line, VALUES_SIZE))
        ty += STRIP_LINE
    svg.append("</g>")
    svg.append(f'<g class="panel" id="after" transform="translate({ax:.2f} 0)">')
    if after_plug is not None:
        svg.append(_filled_polygon(frame, after_plug, COLOR_PLUG, PLUG_OPACITY))
    svg.extend(_draw_outline(frame, a_out, COLOR_OUTLINE, False, STROKE_OUTER, STROKE_INNER))
    for arc in plan.arcs:
        svg.append(_dotted(frame, arc))
    for (region, _names), removed in zip(plan.regions, plan.removed):
        if removed:
            svg.append(_dotted(frame, LineString(region.exterior.coords)))
    if dimension:
        svg.extend(draw_dimension(frame, dimension))
    dots_row: List[Tuple[int, float, float]] = []
    for dot, n in zip(plan.dots, plan.number_of):
        px, py = _pt(frame, dot.x, dot.y)
        dots_row.append((n, px + ax, py))
    dot_svg: Dict[int, str] = {}
    for i, (n, rx, ry) in enumerate(dots_row):
        px, py = rx - ax, ry
        dot_svg[i] = (f'<circle cx="{px:.2f}" cy="{py:.2f}" r="{CALLOUT_D / 2}" fill="white" stroke="{COLOR_TRACE}" stroke-width="{CALLOUT_STROKE}"/>'
                      + _text(px, py + CALLOUT_TEXT * 0.36, str(n), CALLOUT_TEXT, fill=COLOR_TRACE))
    crowded = {n for n in set(plan.number_of) if plan.number_of.count(n) > DOTS_PER_NUMBER}
    after_close = len(svg)  # the dots are inserted here, before the after panel closes
    svg.append("</g>")
    key_x = 2 * width + PAIR_GAP + KEY_PAD
    svg.append('<g class="key">')
    key_y: List[float] = []
    y = 2.0 + KEY_SIZE
    for entry in key_entries:
        key_y.append(y)
        for j, line in enumerate(entry):
            svg.append(_text(key_x + (3.0 if j else 0.0), y, line, KEY_SIZE, anchor="start"))
            y += KEY_SUBLINE
        y += KEY_LINE - KEY_SUBLINE
    svg.append("</g>")
    # One leader per key entry, from the dot whose straight leader crosses the fewest drawn lines
    # (then the fewest plug edges, then the dot nearest the key); a speck never carries it.
    rings_row = [LineString([(x - x0 + ax, (y1 - y)) for x, y in r]) for r in _drawn_rings(a_out)]
    plug_row = (Polygon([(x - x0 + ax, (y1 - y)) for x, y in after_plug.exterior.coords])
                if after_plug is not None else None)
    leaders: List[str] = []
    shown: set = set()
    for n in range(1, len(plan.key_lines) + 1):
        idxs = [i for i, m in enumerate(plan.number_of) if m == n]
        biggest = max(plan.regions[i][0].area for i in idxs)
        big = [i for i in idxs if plan.regions[i][0].area >= max(LEADER_MIN_MM2, 0.1 * biggest)] or idxs
        ex, ey = key_x - 1.0, key_y[n - 1] - KEY_SIZE * 0.35
        best = None
        for i in big:
            _m, cx, cy = dots_row[i]
            dx, dy = ex - cx, ey - cy
            dist = (dx * dx + dy * dy) ** 0.5 or 1.0
            sx, sy = cx + dx / dist * (CALLOUT_D / 2), cy + dy / dist * (CALLOUT_D / 2)
            leader = LineString([(sx, sy), (ex, ey)])
            crossings = sum(len([g for g in shapely.get_parts(leader.intersection(r)) if not g.is_empty]) for r in rings_row)
            plug_x = (len([g for g in shapely.get_parts(leader.intersection(plug_row.exterior)) if not g.is_empty])
                      if plug_row is not None else 0)
            score = (crossings, plug_x, -cx)
            if best is None or score < best[0]:
                best = (score, sx, sy, i)
        _score, sx, sy, i_best = best
        leaders.append(f'<line x1="{sx:.2f}" y1="{sy:.2f}" x2="{ex:.2f}" y2="{ey:.2f}" stroke="{COLOR_TRACE}" stroke-width="{LEADER_W}"/>')
        shown.add(i_best)
        if n not in crowded:
            shown.update(idxs)
    svg[after_close:after_close] = [dot_svg[i] for i in sorted(shown)]
    svg.append('<g class="leaders">')
    svg.extend(leaders)
    svg.append("</g>")
    svg.append("</svg>")
    return "\n".join(s for s in svg if s) + "\n"


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def svg_relpath(row: Dict[str, Any]) -> str:
    return f"{row['file']}/{row['name']}.svg"


def index_row(row: Dict[str, Any], regions: int, area: float, tags: List[str],
              features: Sequence[str],
              regions_named: Sequence[Tuple[Polygon, Sequence[str]]] = (),
              callouts: Sequence[Sequence[Any]] = ()) -> Dict[str, Any]:
    """One index entry: ``regions_named`` is ``[area_mm2, [names]]`` per
    changed region in drawing order; ``callouts`` is the key of the pair
    picture, ``[number, [names], removed]`` per entry."""
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
        "features": list(features),
        "regions_named": [[round(region.area, 1), list(names)] for region, names in regions_named],
        "callouts": [list(c) for c in callouts],
    }


def build_none(row: Dict[str, Any], out_dir: Path) -> Dict[str, Any]:
    svg = compose_none_svg(note=row.get("note") or "", title=row["title"], name=row["name"])
    path = out_dir / svg_relpath(row)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")
    return index_row(row, 0, 0.0, [], ["none"])


def build_diff(row: Dict[str, Any], renderer: Renderer, defaults: Dict[str, Any], out_dir: Path,
               layout: str = "pair", unit: Optional[str] = None) -> Dict[str, Any]:
    """A top-view or section diagram: two renders, two views, the diff; the
    pair picture for the views in PAIR_VIEWS (``layout`` "pair"), else the
    single drawing."""
    file_key = row["file"]
    d = row["diagram"]
    view = d["view"]
    at = float(d.get("at") or 0.0)
    base, after_params = parameter_sets(row, defaults)
    tags: List[str] = []
    outlines = []
    stls: List[Path] = []
    body = None
    for params in (base, after_params):
        defines = defines_for(file_key, row["name"], params, defaults)
        stl, log, _hit = renderer.render(file_key, defines)
        stls.append(stl)
        tags.extend(t for t in warning_tags(log) if t not in tags)
        if view == "top":
            outlines.append(top_view(file_key, stl, params))
        else:
            outline, body = section_view(stl, view, at)
            outlines.append(outline)
    b_out, a_out = outlines
    context = dict(d.get("context") or {})
    if view == "top":
        plug = plug_polygon(file_key, after_params, a_out)
        before_plug = plug_polygon(file_key, base, b_out)
    else:
        plug = section_plug_polygon(file_key, after_params, view, at, body)
        before_plug = None
        context[view] = at  # the cut plane, shown with the context
    regions, area = outline_regions(b_out, a_out)
    if view == "top":
        feats = footprints(file_key, base, b_out, a_out, after_params)
    else:
        feats = footprints(file_key, base, top_view(file_key, stls[0], base),
                           top_view(file_key, stls[1], after_params), after_params)
    body_area = sum(p.area for p in b_out.solids) if view == "top" else 0.0
    edge_rings = ([LineString(max(o.solids, key=lambda q: q.area).exterior.coords) for o in (b_out, a_out) if o.solids]
                  if view == "top" else [])
    named = classify_regions(file_key, regions, feats, view, at, body_area, edge_rings) if regions else []
    features = feature_names(named)
    callouts: List[List[Any]] = []
    if layout == "pair" and view in PAIR_VIEWS:
        crop = d.get("crop")
        single = (file_key, row["name"]) in SINGLE_PANEL_ROWS
        plan = plan_callouts(b_out, a_out, named, shapely.box(*(float(v) for v in crop)) if crop else None)
        callouts = [] if single else plan.key_rows
        svg = compose_pair_svg(
            before_outline=b_out,
            after_outline=a_out,
            before_plug=before_plug,
            after_plug=plug,
            title=row["title"],
            changes=row["changes"],
            name=row["name"],
            before_value=d["before"],
            after_value=d["after"],
            unit=unit,
            context=context,
            style=d["style"],
            crop=d.get("crop"),
            regions_named=named,
            section=(view, at) if view in SECTION_VIEWS else None,
            plan=plan,
            single_panel=single,
        )
    else:
        svg = compose_svg(
            before=b_out.filled,
            after=a_out.filled,
            plug=plug,
            title=row["title"],
            changes=row["changes"],
            name=row["name"],
            before_value=d["before"],
            after_value=d["after"],
            context=context,
            style=d["style"],
            crop=d.get("crop"),
            before_outline=b_out,
            after_outline=a_out,
            regions=regions,
        )
    path = out_dir / svg_relpath(row)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")
    return index_row(row, len(regions), area, tags, features, named, callouts)


def run_rows(
    rows: Sequence[Dict[str, Any]],
    out_dir: Path,
    cache_dir: Path,
    force: bool = False,
    renderer: Optional[Renderer] = None,
    layout: str = "pair",
) -> List[Dict[str, Any]]:
    """Build the diagrams of ``rows`` under ``out_dir``; return their index
    rows (rows with a view this script does not build are skipped with a log line)."""
    out_dir = Path(out_dir)
    renderer = renderer or Renderer(cache_dir=Path(cache_dir), force=force)
    mappings = {key: load_mapping(key) for key in SCADS}
    defaults = {key: mapping_defaults(m) for key, m in mappings.items()}
    produced: List[Dict[str, Any]] = []
    for row in rows:
        view = row["diagram"]["view"]
        t0 = time.time()
        if view == "none":
            entry = build_none(row, out_dir)
        elif view == "top" or view in SECTION_VIEWS:
            r0, h0 = renderer.renders, renderer.hits
            unit = (mappings[row["file"]].get(row["name"]) or {}).get("unit")
            entry = build_diff(row, renderer, defaults[row["file"]], out_dir, layout=layout, unit=unit)
            logger.info(
                "%s %s: %d region(s), %.1f mm2, %d render(s), %d cache hit(s), %.1f s%s",
                row["file"], row["name"], entry["regions"], entry["changed_area_mm2"],
                renderer.renders - r0, renderer.hits - h0, time.time() - t0,
                f", tags {entry['tags']}" if entry["tags"] else "",
            )
        else:
            logger.warning("%s %s: view %s is not one this script builds; skipped", row["file"], row["name"], view)
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


# ---------------------------------------------------------------------------
# docs/dials/README.md: every diagram inline with its words
# ---------------------------------------------------------------------------

README_NAME = "README.md"
README_TITLE = "Dial diagrams"
README_INTRO = (
    "Every dial of the one-sided puller and the two-sided puller has a picture here: "
    "the tool at its defaults in black, the plug in teal, and a red dashed trace on the "
    "part that dial moves when it goes from its default to a second value.",
    "The pictures are cut from the same OpenSCAD files you print from, at 1 unit = 1 mm; "
    "the two values drawn are written under each picture.",
)
README_FILE_HEADINGS = {ONE_SIDED: "One-sided puller", TWO_SIDED: "Two-sided puller"}


def _readme_entry(row: Dict[str, Any], entry: Dict[str, Any]) -> List[str]:
    d = row["diagram"]
    lines = [f"`{row['name']}`: {row['title']}", "", f"![{row['changes']}]({svg_relpath(row)})", ""]
    if d["view"] == "none":
        lines.append(f"{NO_SHAPE_SENTENCE} {row.get('note') or ''}".strip())
    else:
        parts = [f"Before: {_fmt_value(d['before'])}. After: {_fmt_value(d['after'])}."]
        ctx = d.get("context") or {}
        if ctx:
            parts.append("Context: " + ", ".join(f"`{k}` = {_fmt_value(v)}" for k, v in ctx.items()) + ".")
        if d["view"] in SECTION_VIEWS:
            axis = "x" if d["view"] == "section-x" else "y"
            parts.append(f"Section at {axis} = {_fmt_value(d.get('at') or 0)} mm.")
        parts.append("Moves: " + ", ".join(entry.get("features") or []) + ".")
        lines.append(" ".join(parts))
    lines.append("")
    return lines


def write_readme(out_dir: Path, catalog: Sequence[Dict[str, Any]],
                 index_rows: Sequence[Dict[str, Any]]) -> Path:
    """The Markdown index: H1, the intro and the legend, H2 per file, H3 per
    Customizer section in mapping order, one entry per dial."""
    index = {(e["file"], e["name"]): e for e in index_rows}
    lines = [f"# {README_TITLE}", "", README_INTRO[0], "", README_INTRO[1], "", LEGEND_LINE + ".", ""]
    count = 0
    for file_key in (ONE_SIDED, TWO_SIDED):
        lines += [f"## {README_FILE_HEADINGS[file_key]}", ""]
        sections: List[str] = []
        for mrow in load_mapping(file_key).values():
            if mrow["section"] not in sections:
                sections.append(mrow["section"])
        for section in sections:
            rows = [r for r in catalog if r["file"] == file_key and r["section"] == section]
            if not rows:
                continue
            lines += [f"### {section}", ""]
            for row in rows:
                entry = index.get((row["file"], row["name"]))
                if entry is None:
                    raise RuntimeError(f"{row['file']}/{row['name']} has no index row; build it first")
                lines += _readme_entry(row, entry)
                count += 1
    path = out_dir / README_NAME
    path.write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8")
    logger.info("README: %d entries -> %s", count, path)
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
    parser.add_argument("--readme", action="store_true", help="only rewrite docs/dials/README.md from the index on disk (no rows built)")
    parser.add_argument("--layout", choices=("pair", "single"), default="pair", help="the pair picture (default) or the previous one-drawing picture")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    catalog = load_catalog()
    if args.readme:
        index_path = args.out / INDEX_NAME
        if not index_path.exists():
            logger.error("no index at %s; build the rows first", index_path)
            return 1
        write_readme(args.out, catalog, json.loads(index_path.read_text(encoding="utf-8")))
        return 0
    files = [args.file] if args.file else [ONE_SIDED, TWO_SIDED]
    rows = select_rows(catalog, files, args.only, args.views)
    if not rows:
        logger.error("no catalog rows match the selection")
        return 1
    t0 = time.time()
    renderer = Renderer(cache_dir=args.cache, force=args.force)
    produced = run_rows(rows, out_dir=args.out, cache_dir=args.cache, force=args.force, renderer=renderer, layout=args.layout)
    index_path = write_index(args.out, produced, catalog)
    index_rows = json.loads(index_path.read_text(encoding="utf-8"))
    if len(index_rows) == len(catalog):
        write_readme(args.out, catalog, index_rows)
    else:
        logger.warning("README not written: the index has %d of %d catalog rows", len(index_rows), len(catalog))
    empty = [f"{e['file']}/{e['name']}" for e in produced if e["view"] != "none" and e["regions"] == 0]
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
