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
1 unit = 1 mm under ``docs/dials/<file>/<name>.svg``. The pair layout
draws three parts at one scale: the BEFORE panel
(the tool at the dial's default, the plug in teal), an arrow with the two
values, and the AFTER panel (the tool after the dial moved, drawn once in
black except the pieces of its outline that moved, which are thick red
dashes instead of black line),
numbered dots on the moved edges and a key column beside the picture that
names them; no dial name and no legend inside the picture. A feature that
disappeared is drawn from its old outline in red dashes and marked removed.
``--layout single`` keeps the previous one-drawing picture for one release
cycle. Rows whose ``view`` is ``none`` get a small SVG saying the dial
changes no shape. Every SVG carries a ``<title>`` / ``<desc>`` pair.

Renders are cached under ``tmp_renders/dial_diagrams/`` (gitignored), keyed
by the parameter set and the SCAD sources, never by STL bytes (identical
renders are not byte-identical).

The two storyboards of ``dial_storyboards.json`` (the four Customizer steps
applied one after another to a real plug, five panels in a 3 + 2 grid) are
drawn by ``--storyboards`` into ``docs/dials/<file>/storyboard.svg`` with
their own index, ``docs/dials/storyboards_index.json``.

Usage:
    python scripts/generate_dial_diagrams.py                 # every row
    python scripts/generate_dial_diagrams.py --file one-sided --only size
    python scripts/generate_dial_diagrams.py --views top --force
    python scripts/generate_dial_diagrams.py --storyboards   # the two storyboards and the README

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

# The picture key (the pages print it once, never the picture).
LEGEND_LINE = (
    "black = the tool; teal = your plug; red dashed = the edges this dial moved; "
    "the numbers match the key beside the picture"
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
    y_prong = y1
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
# edge. A hole or slot whose own outline moved is named on every region
# whose outline encloses part of its change, even a region another part
# owns (``moved_openings``).

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
# How a through-opening is sorted, by the footprints and by the moved-opening check alike
ZIP_MATCH = {ONE_SIDED: 2.0, TWO_SIDED: 1.5}  # mm: a circle this close to the zip-tie hole's diameter is one
FINGER_MATCH = 3.0  # mm: a circle this close to the finger hole's diameter is one
STRAP_MIN_AREA = {ONE_SIDED: 5.0, TWO_SIDED: 20.0}  # mm²: a non-circular opening this big is a strap opening


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


def _wing_name(params: Dict[str, Any]) -> str:
    return "classic slots" if params.get("velcro_style") == "Classic slot" else "wing openings"


def _clamshell(params: Dict[str, Any]) -> Tuple[Dict[str, float], Dict[str, Any]]:
    """The two-sided plug numbers and the clamshell mirror's numbers."""
    m = effective_measurements(TWO_SIDED, params)
    size = params.get("size", "Medium")
    mirror_size = size if size in fit_formulas.FIT_SIZE_TABLE else "Medium"
    return m, clamshell_mirror(mirror_size, {"measurements": m})


def footprints_one_sided(params: Dict[str, Any], outline: Outline,
                         after: Optional[Outline] = None,
                         after_params: Optional[Dict[str, Any]] = None) -> Footprints:
    d = _one_sided_numbers(params)
    d2 = _one_sided_numbers(after_params) if after_params else d
    body = max(outline.solids, key=lambda p: p.area)
    top = body.bounds[3]
    solids = list(outline.solids) + (list(after.solids) if after else [])
    circles = _circles(solids)
    fingers = [c for c in circles if abs(c.d - d["finger_hole_diameter"]) < FINGER_MATCH]
    zips = [c for c in circles if abs(c.d - d["zip_tie_hole_diameter"]) < ZIP_MATCH[ONE_SIDED]]
    wings = _hole_slots(solids, STRAP_MIN_AREA[ONE_SIDED])
    wing_name = _wing_name(params)
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
    m, cm = _clamshell(params)
    solids = list(outline.solids) + (list(after.solids) if after else [])
    x0, y0, x1, y1 = shapely.union_all(solids).bounds
    circles = _circles(solids)
    zip_d = float(params.get("plate_zip_hole_diameter", 4.0))
    fingers = [c for c in circles if abs(c.d - cm["finger_dia"]) < FINGER_MATCH]
    zips = [c for c in circles if abs(c.d - zip_d) < ZIP_MATCH[TWO_SIDED]]
    slots = _hole_slots(solids, STRAP_MIN_AREA[TWO_SIDED])
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


def openings(file_key: str, params: Dict[str, Any], outline: Outline) -> Dict[str, List[Polygon]]:
    """One top view's through-openings by the names the footprints give
    them, each as the exact polygon of its ring, sorted with this state's
    own numbers."""
    found = []
    for poly in outline.solids:
        for ring in poly.interiors:
            coords = np.asarray(ring.coords)
            found.append((Polygon(coords), classify_circle(coords)))
    if file_key == ONE_SIDED:
        d = _one_sided_numbers(params)
        zip_d, finger_d = d["zip_tie_hole_diameter"], d["finger_hole_diameter"]
        names = ("zip-tie holes", "finger holes", _wing_name(params))
    else:
        _m, cm = _clamshell(params)
        zip_d, finger_d = float(params.get("plate_zip_hole_diameter", 4.0)), cm["finger_dia"]
        names = ("zip stations", "finger lobes", "strap slot")
    return {
        names[0]: [p for p, c in found if c and abs(c.d - zip_d) < ZIP_MATCH[file_key]],
        names[1]: [p for p, c in found if c and abs(c.d - finger_d) < FINGER_MATCH],
        names[2]: [p for p, c in found if c is None and p.area > STRAP_MIN_AREA[file_key]],
    }


def moved_openings(file_key: str, before_params: Dict[str, Any], before: Outline,
                   after_params: Dict[str, Any], after: Outline) -> List[Tuple[str, Any]]:
    """Every kind of through-opening whose outline changed between two top
    views, with its change (the symmetric difference of its openings); a
    change under MIN_REGION_AREA is render noise and left out."""
    b = openings(file_key, before_params, before)
    a = openings(file_key, after_params, after)
    moved = []
    for name in sorted(set(b) | set(a)):
        change = _fix(_union(a.get(name, [])).symmetric_difference(_union(b.get(name, []))))
        if not change.is_empty and change.area >= MIN_REGION_AREA:
            moved.append((name, change))
    return moved


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
                     edge_rings: Sequence[LineString] = (),
                     moved: Sequence[Tuple[str, Any]] = ()) -> List[Tuple[Polygon, List[str]]]:
    """Name every changed region, one name list per region in drawing order
    (the most specific footprint first): the specific footprints (holes,
    slots, teeth) covering at least half of it, the broad ones (pocket,
    notch, seat, hook, lobes, channel, arms) covering at least a sixth of
    it, and any footprint the region itself covers at least half of (a
    region that swallows a whole feature); a region that swallows a quarter
    of the body is also the edge's; a region nothing claims takes the
    footprint covering most of it, if a tenth, else the edge. A region that
    lies mostly within EDGE_BAND of one of ``edge_rings`` (the body's outer
    edge before and after), outside every named footprint, is the edge's too.
    In a top view, a region whose outline encloses at least MIN_REGION_AREA
    of a ``moved`` part's change (see ``moved_openings``) is that part's too,
    even when its change merged into another part's region."""
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
        if view == "top" and moved:
            # the region's outline, not its area: a hole that lands in new material is an inner ring of the region
            enclosed = Polygon(region.exterior)
            for name, change in moved:
                if enclosed.intersection(change).area >= MIN_REGION_AREA:
                    hits.add(name)
        if not hits and shares and view == "top":
            # A section probe is a thin box across the whole cut: a feature it
            # merely grazes must not name it, so the tenth-share fallback is
            # for top views only.
            best = max(shares, key=shares.get)
            if shares[best] >= FALLBACK_SHARE:
                hits.add(best)
        names = sorted(hits or {edge}, key=lambda n: (order.index(n) if n in order else len(order), n))
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

    def open_paths(self, coords) -> List[str]:
        """An open line as paths, in pieces where the drawing box cuts it."""
        line = shapely.simplify(LineString(coords), SIMPLIFY, preserve_topology=True)
        clipped = line if self.box.contains(line) else line.intersection(self.box)
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


MIN_KEPT = 0.02  # mm: a shorter leftover of a cut ring is a numeric sliver, not an edge


def _stroke_paths(frame: _Frame, coords, color: str, width: float, dash: Optional[str] = None,
                  cut=None) -> List[str]:
    """A ring as stroked paths; the parts inside ``cut`` (the red-dashed
    edges) are left out, so those edges are drawn once, in red dashes."""
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    ring = LineString(coords)
    if cut is not None and ring.intersects(cut):
        kept = shapely.line_merge(ring.difference(cut))
        paths = [d for g in shapely.get_parts(kept) if isinstance(g, LineString) and g.length >= MIN_KEPT
                 for d in frame.open_paths(g.coords)]
    else:
        paths = frame.ring_paths(coords)
    return [
        f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" '
        f'stroke-linejoin="round" stroke-linecap="round"{dd}/>'
        for d in paths
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
                  width_outer: float, width_inner: float, cut=None) -> List[str]:
    """The outline's rings in black; with ``cut``, without the edges that
    are drawn in red dashes instead."""
    out: List[str] = []
    # The drawn rings are cleaned of render noise (specks and slivers), as
    # the outline sheets do; the diff itself works on the raw geometry.
    for raw in outline.solids:
        poly = clean_polygon(raw)
        if poly is None:
            continue
        out.extend(_stroke_paths(frame, poly.exterior.coords, color, width_outer,
                                 DASH_TRACE if dashed_all else None, cut))
        for ring in poly.interiors:
            out.extend(_stroke_paths(frame, ring.coords, color, width_inner,
                                     DASH_TRACE if dashed_all else DASH_HOLE, cut))
    for raw in outline.recess:
        poly = clean_polygon(raw)
        if poly is None:
            continue
        for ring in [poly.exterior] + list(poly.interiors):
            out.extend(_stroke_paths(frame, ring.coords, color if dashed_all else COLOR_RECESS,
                                     width_inner, DASH_TRACE if dashed_all else DASH_POCKET, cut))
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


def compose_none_svg(note: str, title: str = "", name: str = "", desc: Optional[str] = None) -> str:
    """A 120 x 40 mm card for a dial that changes no shape."""
    width, height = 120.0, 40.0
    body_lines = textwrap.wrap(note or "", width=76)
    desc = desc or f"{NO_SHAPE_SENTENCE} {note}".strip()
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
# The pair picture: before | arrow | after, the moved edges in red
# ---------------------------------------------------------------------------

PAIR_VIEWS = ("top",) + SECTION_VIEWS
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
# A moved edge is drawn in thick red dashes only, with the black outline cut
# away under it, so no edge is drawn twice (the owner, 2026-09-28: "no
# overlap of line styles"; style A, chosen the same day over rimmed dots).
# The dashes differ from the black lines in colour, dash and width at once,
# so they read without colour; long dashes with short gaps are mostly ink,
# calmer to look at than rows of dots. Red measures 5.1:1 on white and 3.3:1
# on the see-through plug, above the 3:1 graphics need, so no rim is drawn.
MARK_W = 0.8  # thicker than the outline (STROKE_OUTER) and the hole lines (STROKE_INNER)
MARK_DASH = "3.5,1.2"  # long dashes, short gaps; the hole lines use DASH_HOLE
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


def _marked(frame: _Frame, line: LineString, color: str = COLOR_TRACE, width: float = MARK_W,
            dash: str = MARK_DASH) -> str:
    """A moved edge in red dashes, clipped to the drawing box (a crop), as
    the outlines are."""
    pieces = [g for g in shapely.get_parts(line.intersection(frame.box)) if isinstance(g, LineString) and not g.is_empty]
    return "".join(
        f'<path d="M {frame._pts(g.coords)}" fill="none" stroke="{color}" stroke-width="{width:g}" '
        f'stroke-linecap="butt" stroke-linejoin="round" stroke-dasharray="{dash}"/>'
        for g in pieces
    )


def _red_marks(plan: PairPlan) -> List[LineString]:
    """Every line a panel draws in red dashes: the moved edges, then the old
    outline of each removed feature."""
    marks = list(plan.arcs) + [LineString(region.exterior.coords)
                               for (region, _names), removed in zip(plan.regions, plan.removed) if removed]
    # Each stretch is drawn once: a mark loses whatever lies within EDGE_TOL
    # of a mark before it (a pocket edge running along a hole edge would
    # otherwise put two rows of dashes on one line).
    kept: List[LineString] = []
    covered = None
    for mark in marks:
        rest = mark if covered is None else mark.difference(covered)
        kept += [g for g in shapely.get_parts(rest) if isinstance(g, LineString) and g.length >= MIN_ARC]
        strip = mark.buffer(EDGE_TOL, cap_style="flat")
        covered = strip if covered is None else covered.union(strip)
    if not kept:
        return []
    # Pieces whose ends meet exactly (a moved stretch across a ring's first
    # point comes as two) are joined, so the dashes run on at an even pitch.
    merged = shapely.line_merge(shapely.multilinestrings(kept))
    return [g for g in shapely.get_parts(merged) if isinstance(g, LineString) and not g.is_empty]


def _marks_cut(marks: Sequence[LineString]):
    """The strip the black outline is cut along: EDGE_TOL on each side of
    every red-dashed line (an edge within EDGE_TOL did not move, so it is the
    same edge), flat at the ends so the black line stops where the dashes
    start. None when nothing is marked."""
    if not marks:
        return None
    return shapely.union_all([m.buffer(EDGE_TOL, cap_style="flat") for m in marks])


def _dim_arrow(x: float, y: float, direction: float, color: str) -> str:
    bx = x - direction * DIM_ARROW * 1.6
    return f'<polygon points="{x:.2f},{y:.2f} {bx:.2f},{y - DIM_ARROW * 0.35:.2f} {bx:.2f},{y + DIM_ARROW * 0.35:.2f}" fill="{color}"/>'


def _dim_arrow_v(x: float, y: float, direction: float, color: str) -> str:
    """A filled arrow head at (x, y) pointing along +y (direction 1, down the page) or -y."""
    by = y - direction * DIM_ARROW * 1.6
    return f'<polygon points="{x:.2f},{y:.2f} {x - DIM_ARROW * 0.35:.2f},{by:.2f} {x + DIM_ARROW * 0.35:.2f},{by:.2f}" fill="{color}"/>'


def _dim_label(x: float, y: float, label: str, anchor: str, color: str) -> List[str]:
    """The label with a white halo drawn as a separate text under it (an SVG
    rasterizer may ignore paint-order)."""
    text = _esc(label)
    return [
        f'<text x="{x:.2f}" y="{y:.2f}" font-family="{FONT}" font-size="{DIM_TEXT}" font-weight="bold" '
        f'text-anchor="{anchor}" fill="white" stroke="white" stroke-width="0.8" stroke-linejoin="round">{text}</text>',
        f'<text x="{x:.2f}" y="{y:.2f}" font-family="{FONT}" font-size="{DIM_TEXT}" font-weight="bold" '
        f'text-anchor="{anchor}" fill="{color}">{text}</text>',
    ]


def draw_dimension(frame: _Frame, dim: Dict[str, Any]) -> List[str]:
    """A dimension callout in the after panel with the outline sheets'
    conventions. Kind "h": extension lines from the object's edge ``y_obj``,
    a line at ``y_dim`` between ``x0`` and ``x1`` with two arrow heads, the
    label above it. Kind "v": the same turned upright (``x_obj``, ``x_dim``,
    ``y0``, ``y1``), the label beside the line on the side with room. Kind
    "dia": a line across the circle (``cx``, ``cy``, ``r``) with the arrow
    heads at its edge, the label above."""
    c = COLOR_TRACE
    out = ['<g class="dimension">']
    kind = dim["kind"]
    if kind == "h":
        (xa, ya), (xb, _yb) = _pt(frame, dim["x0"], dim["y_dim"]), _pt(frame, dim["x1"], dim["y_dim"])
        (_xo, yo) = _pt(frame, dim["x0"], dim["y_obj"])
        over = 1.0 if ya < yo else -1.0
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
        out.extend(_dim_label((xa + xb) / 2, ya - 1.0, dim["label"], "middle", c))
    elif kind == "v":
        (xd, ya) = _pt(frame, dim["x_dim"], max(dim["y0"], dim["y1"]))
        (_x, yb) = _pt(frame, dim["x_dim"], min(dim["y0"], dim["y1"]))
        (xo, _y) = _pt(frame, dim["x_obj"], dim["y0"])
        over = 1.0 if xd < xo else -1.0
        for y in (ya, yb):
            out.append(f'<line x1="{xo:.2f}" y1="{y:.2f}" x2="{xd - over:.2f}" y2="{y:.2f}" stroke="{c}" stroke-width="{DIM_EXT_W}"/>')
        if (yb - ya) < 11.0:
            out.append(f'<line x1="{xd:.2f}" y1="{ya - 5:.2f}" x2="{xd:.2f}" y2="{yb + 5:.2f}" stroke="{c}" stroke-width="{DIM_LINE_W}"/>')
            out.append(_dim_arrow_v(xd, ya, -1.0, c))
            out.append(_dim_arrow_v(xd, yb, 1.0, c))
        else:
            out.append(f'<line x1="{xd:.2f}" y1="{ya:.2f}" x2="{xd:.2f}" y2="{yb:.2f}" stroke="{c}" stroke-width="{DIM_LINE_W}"/>')
            out.append(_dim_arrow_v(xd, ya, 1.0, c))
            out.append(_dim_arrow_v(xd, yb, -1.0, c))
        room_right = (frame.box.bounds[2] - frame.x0) - xd
        if room_right >= CHAR_W * DIM_TEXT * len(dim["label"]) + 2.0:
            out.extend(_dim_label(xd + 1.4, (ya + yb) / 2 + 1.0, dim["label"], "start", c))
        else:
            out.extend(_dim_label(xd - 1.4, (ya + yb) / 2 + 1.0, dim["label"], "end", c))
    else:
        (cx, cy) = _pt(frame, dim["cx"], dim["cy"])
        r = dim["r"]
        out.append(f'<line x1="{cx - r:.2f}" y1="{cy:.2f}" x2="{cx + r:.2f}" y2="{cy:.2f}" stroke="{c}" stroke-width="{DIM_LINE_W}"/>')
        out.append(_dim_arrow(cx - r, cy, -1.0, c))
        out.append(_dim_arrow(cx + r, cy, 1.0, c))
        out.extend(_dim_label(cx, cy - 1.0, dim["label"], "middle", c))
    out.append("</g>")
    return out



# ---------------------------------------------------------------------------
# The dimension callout: one red dimension line at the feature the dial sets
# ---------------------------------------------------------------------------
#
# A catalog row's ``diagram.dimension`` names an anchor; the endpoints are
# read from the AFTER state's outline, plug and numbers (never estimated by
# eye). The label is the dial's value with its unit.

DIM_OFFSET = 4.0  # mm from the object's edge to the dimension line
DIM_LABEL_ROOM = 14.0  # mm of room a vertical dimension's label needs beside its line
DIM_SAME_TOLERANCE = 0.5  # mm: under one slider step, the drawn size reads as the number on the line


def dimension_span(dim: Dict[str, Any]) -> float:
    """The length of the part a callout marks, in model mm: the span of an
    "h" or "v" line, the diameter of a "dia" circle."""
    if dim["kind"] == "h":
        return dim["x1"] - dim["x0"]
    if dim["kind"] == "v":
        return dim["y1"] - dim["y0"]
    return 2 * dim["r"]


def _probe_gap(filled, y: float, near_x: float) -> Optional[Tuple[float, float]]:
    """The gap in ``filled`` along the horizontal line at ``y`` that contains
    or is nearest to ``near_x``: (left edge, right edge)."""
    x0, _y0, x1, _y1 = filled.bounds
    cut = LineString([(x0 - 1.0, y), (x1 + 1.0, y)]).intersection(filled)
    spans = sorted((g.bounds[0], g.bounds[2]) for g in shapely.get_parts(cut) if not g.is_empty)
    gaps = [(a[1], b[0]) for a, b in zip(spans, spans[1:]) if b[0] > a[1]]
    if not gaps:
        return None
    return min(gaps, key=lambda g: 0.0 if g[0] <= near_x <= g[1] else min(abs(g[0] - near_x), abs(g[1] - near_x)))


def _plug_edges(plug: Polygon) -> Tuple[float, float, float, float]:
    x0, y0, x1, y1 = plug.bounds
    return x0, y0, x1, y1


def _label(value: Any, unit: Optional[str]) -> str:
    return f"{_fmt_value(value)} {unit}" if unit else _fmt_value(value)


def anchor_dimension(anchor: str, file_key: str, params: Dict[str, Any], outline: Outline,
                     plug: Optional[Polygon], view: str, at: float, value: Any,
                     unit: Optional[str]) -> Optional[Dict[str, Any]]:
    """The dimension callout for ``anchor`` in model mm, or None when the
    geometry cannot give it: kind "h" {x0, x1, y_obj, y_dim}, kind "v"
    {y0, y1, x_obj, x_dim}, kind "dia" {cx, cy, r}; every kind has "label"."""
    label = _label(value, unit)
    filled = _union(outline.solids)
    bx0, by0, bx1, by1 = filled.bounds
    if anchor in ("plug_width_prong_end", "plug_width_cord_end"):
        if plug is None:
            return None
        pts = list(plug.exterior.coords)[:-1]
        edge_y = max(y for _x, y in pts) if anchor == "plug_width_prong_end" else min(y for _x, y in pts)
        xs = sorted(x for x, y in pts if abs(y - edge_y) < 1e-6)
        if len(xs) < 2:
            return None
        above = anchor == "plug_width_prong_end"
        return {"kind": "h", "x0": xs[0], "x1": xs[-1], "y_obj": edge_y,
                "y_dim": edge_y + (DIM_OFFSET if above else -DIM_OFFSET), "label": label}
    if anchor == "pocket_length":
        if not outline.recess:
            return None
        rx0, ry0, rx1, _ry1 = _union(outline.recess).bounds
        return {"kind": "v", "y0": ry0, "y1": by1, "x_obj": rx1, "x_dim": rx1 + DIM_OFFSET + 1.0, "label": label}
    if anchor in ("plug_thickness_prong_end", "plug_thickness_cord_end"):
        if plug is None or view != "section-x":
            return None
        pts = list(plug.exterior.coords)[:-1]
        floor = min(y for _x, y in pts)
        u_plate, u_cord = min(x for x, _y in pts), max(x for x, _y in pts)
        u_edge = u_plate if anchor == "plug_thickness_prong_end" else u_cord
        top = max(y for x, y in pts if abs(x - u_edge) < 1e-6)
        x_dim = u_edge - DIM_OFFSET if anchor == "plug_thickness_prong_end" else u_edge + DIM_OFFSET
        return {"kind": "v", "y0": floor, "y1": top, "x_obj": u_edge, "x_dim": x_dim, "label": label}
    if anchor == "hook_slot":
        d = _one_sided_numbers(params)
        hook_x = _hook_box(d, params).centroid.x
        gap = _probe_gap(filled, by0 + 3.0, hook_x)  # 1.5 mm up the probe hits the hook's own foot
        if gap is None:
            return None
        return {"kind": "h", "x0": gap[0], "x1": gap[1], "y_obj": by0, "y_dim": by0 - DIM_OFFSET, "label": label}
    if anchor == "finger_hole":
        circles = _circles(outline.solids)
        if not circles:
            return None
        big = max(c.d for c in circles)
        fingers = [c for c in circles if c.d >= big - 3.0]
        c = max(fingers, key=lambda c: c.cx)
        return {"kind": "dia", "cx": c.cx, "cy": c.cy, "r": c.d / 2, "label": label}
    if anchor == "body_width":
        best_y, best_w = by0, 0.0
        y = by0 + 0.5
        while y < by1:
            cut = LineString([(bx0 - 1.0, y), (bx1 + 1.0, y)]).intersection(filled)
            if not cut.is_empty:
                w = cut.bounds[2] - cut.bounds[0]
                if w > best_w:
                    best_y, best_w = y, w
            y += 1.0
        return {"kind": "h", "x0": bx0, "x1": bx1, "y_obj": best_y, "y_dim": by0 - DIM_OFFSET, "label": label}
    if anchor == "plug_length":
        if plug is None:
            return None
        px0, py0, px1, py1 = _plug_edges(plug)
        return {"kind": "v", "y0": py0, "y1": py1, "x_obj": px1, "x_dim": bx1 + DIM_OFFSET, "label": label}
    if anchor in ("gap_tips", "gap_cord_end"):
        m = effective_measurements(file_key, params)
        y = by1 - 2.0 if anchor == "gap_tips" else by1 - m["measure_plug_length"]
        gap = _probe_gap(filled, y, 0.0)
        if gap is None:
            return None
        y_dim = by1 + DIM_OFFSET + 1.0 if anchor == "gap_tips" else y - DIM_OFFSET
        return {"kind": "h", "x0": gap[0], "x1": gap[1], "y_obj": y, "y_dim": y_dim, "label": label}
    if anchor == "channel":
        gap = _probe_gap(filled, by0 + 3.0, 0.0)
        if gap is None:
            return None
        return {"kind": "h", "x0": gap[0], "x1": gap[1], "y_obj": by0, "y_dim": by0 - DIM_OFFSET, "label": label}
    if anchor == "slot_length":
        slots = _hole_slots(outline.solids, 20.0)
        if not slots:
            return None
        s = max(slots, key=lambda q: q.centroid.x)
        sx0, sy0, sx1, sy1 = s.bounds
        return {"kind": "v", "y0": sy0, "y1": sy1, "x_obj": sx1, "x_dim": sx1 + DIM_OFFSET, "label": label}
    return None


def _dimension_extent(dim: Dict[str, Any]) -> Tuple[float, float, float, float]:
    """The model-space box the callout and its label need."""
    if dim["kind"] == "h":
        lo, hi = sorted((dim["y_obj"], dim["y_dim"]))
        return dim["x0"] - 6.0, lo - 1.0, dim["x1"] + 6.0, hi + 5.0
    if dim["kind"] == "v":
        lo, hi = sorted((dim["x_obj"], dim["x_dim"]))
        return lo - DIM_LABEL_ROOM, dim["y0"] - 6.0, hi + DIM_LABEL_ROOM, dim["y1"] + 6.0
    return dim["cx"] - dim["r"] - 2.0, dim["cy"] - 2.0, dim["cx"] + dim["r"] + 2.0, dim["cy"] + 5.0


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
    after plug in teal, the moved edges in red dashes, a removed feature from
    its old outline, an optional dimension callout, the numbered dots), and
    the key column with one leader per entry. ``style`` no longer changes
    the drawing; ``context`` is the card's text, not the picture's.
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
    if dimension and not crop:
        ex0, ey0, ex1, ey1 = _dimension_extent(dimension)
        x0, y0, x1, y1 = min(x0, ex0), min(y0, ey0), max(x1, ex1), max(y1, ey1)
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
    marks = _red_marks(plan)
    svg.extend(_draw_outline(frame, a_out, COLOR_OUTLINE, False, STROKE_OUTER, STROKE_INNER, _marks_cut(marks)))
    svg.extend(_marked(frame, mark) for mark in marks)
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
# The text alternatives: a short alt text and a long description
# ---------------------------------------------------------------------------
#
# The rules are docs/guides/describing-pictures.md (rules 1 to 10). The alt names
# the picture, the two values and what red marks; the long description is the
# overview, the two panels, the numbered list matching the key, and what stayed.

ALT_MAX_CHARS = 150
LONG_MAX_WORDS = 90
TOOL_NAMES = {ONE_SIDED: "the one-sided puller", TWO_SIDED: "the two-sided puller"}
# Where each feature sits, the plug end being the top of the picture (the plan's
# section 4.2, shortened so a five-entry list fits the 90-word rule).
FEATURE_LOCATIONS = {
    ONE_SIDED: {
        "body edge": "the outer outline",
        "pocket": "the plug recess on the centerline",
        "seat": "the round recess at the plug end",
        "wall notch": "the notch in the top edge",
        "wing openings": "the two openings beside the pocket",
        "classic slots": "the two slots beside the pocket",
        "zip-tie holes": "the four small holes beside the pocket",
        "finger holes": "the two large holes in the lower half",
        "hook": "the cord hook slot in the bottom edge",
    },
    TWO_SIDED: {
        "plate edge": "the outer outline",
        "arms": "the two toothed arms in the upper half",
        "teeth": "the serrated inner edges of the arms",
        "finger lobes": "the two rounded lobes in the lower half",
        "cord channel": "the gap between the lobes at the bottom",
        "zip stations": "the three small holes along each arm",
        "strap slot": "the long slot in each arm",
    },
}
LONG_MAX_WORDS_DIMENSION = 110  # a picture with a red dimension line also describes the line
# The sentence on a red dimension line, per anchor: what the line marks, the
# part's short name, its size word, and why the part is drawn larger or
# smaller than the number the line reads (each reason checked against the
# model: the cord clearances, the finger-hole clearance, the body worked out
# from the hand width, the grip clearance or bite; None where the drawing
# has no reason to give).
DIMENSION_WORDS: Dict[str, Tuple[str, str, str, Optional[str], Optional[str]]] = {
    "pocket_length": ("the pocket's length", "the pocket", "long", None, None),
    "plug_width_prong_end": ("the plug's width at the prong end", "the plug", "wide", None, None),
    "plug_width_cord_end": ("the plug's width at the cord end", "the plug", "wide", None, None),
    "plug_thickness_prong_end": ("the plug's thickness at the prong end", "the plug", "thick", None, None),
    "plug_thickness_cord_end": ("the plug's thickness at the cord end", "the plug", "thick", None, None),
    "hook_slot": ("the cord hook slot", "the slot", "wide", "so the cord slips in", None),
    "finger_hole": ("a finger hole", "the hole", "across", "wider than the finger", None),
    "body_width": ("the body at its widest", "the body", "wide",
                   None, "narrower than the hand, as its width is worked out from the hand width"),
    "plug_length": ("the plug's length", "the plug", "long", None, None),
    "gap_tips": ("the gap between the arm tips", "the gap", "wide",
                 "leaving a little room around the plug", "so the arms squeeze the plug"),
    "gap_cord_end": ("the gap between the arms at the cord end", "the gap", "wide",
                     "leaving a little room around the plug", "so the arms squeeze the plug"),
    "channel": ("the cord channel", "the channel", "wide", "so the cord slips in", None),
    "slot_length": ("the strap slot's length", "the slot", "long", None, None),
}


def describe_dimension(dim: Dict[str, Any], value: Any) -> str:
    """One sentence on a picture's red dimension line: what it marks and the
    label it reads, which is the number you type; when the part is drawn at
    another size (by DIM_SAME_TOLERANCE or more), that size and why."""
    part, noun, word, larger, smaller = DIMENSION_WORDS.get(
        dim["at"], ("the measured part", "the part", "long", None, None))
    text = f"The red line marks {part} and reads {dim['label']}, the number you type"
    drawn = dim.get("drawn")
    if drawn is not None and isinstance(value, (int, float)) and not isinstance(value, bool):
        if abs(drawn - float(value)) >= DIM_SAME_TOLERANCE:
            reason = larger if drawn > float(value) else smaller
            text += f"; {noun} is drawn {_fmt_value(drawn)} mm {word}" + (f", {reason}" if reason else "")
    return text + "."


def _join_names(names: Sequence[str], one_article: bool = False) -> str:
    """The names joined with "the" before each, or with ``one_article``
    before the first only."""
    items = [f"the {n}" if not one_article or i == 0 else n for i, n in enumerate(names)]
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


def _values_words(before: Any, after: Any, unit: Optional[str]) -> str:
    text = f"{_fmt_value(before)} to {_fmt_value(after)}"
    if unit and not isinstance(after, str):
        text += f" {unit}"
    return text


def _lower_first(text: str) -> str:
    return text[:1].lower() + text[1:] if text else text


def describe_alt(row: Dict[str, Any], unit: Optional[str], entry: Dict[str, Any]) -> str:
    """The short alt text (at most ALT_MAX_CHARS): the title, the kind of
    picture, the two values, and the parts red marks (or their count when
    the names do not fit)."""
    title = row["title"]
    d = row["diagram"]
    if d["view"] == "none":
        return f"{title}: changes no shape."
    values = _values_words(d["before"], d["after"], unit)
    if (row["file"], row["name"]) in SINGLE_PANEL_ROWS:
        return f"{title}: one view, {values}; the layout with both plates, nothing marked."
    features = list(entry.get("features") or [])
    alt = f"{title}: before and after, {values}; red marks {_join_names(features)}."
    if len(alt) > ALT_MAX_CHARS:
        alt = f"{title}: before and after, {values}; red marks {len(features)} parts, named below."
    return alt


def describe_long(row: Dict[str, Any], unit: Optional[str], entry: Dict[str, Any],
                  plug_width: Optional[float] = None, titles: Optional[Dict[str, str]] = None) -> str:
    """The long description (at most LONG_MAX_WORDS, or
    LONG_MAX_WORDS_DIMENSION with a red dimension line): an overview
    sentence, the left panel, the right panel, the red dimension line when
    the picture has one, the numbered list that matches the key, and what
    stayed. When the whole runs long, the closing sentence goes first, then
    the changes sentence, then the locations of the entries that carry
    several names, then every location; the dimension sentence, like the
    numbered list, is never dropped."""
    file_key = row["file"]
    d = row["diagram"]
    view = d["view"]
    title = row["title"]
    tool = TOOL_NAMES[file_key]
    titles = titles or {}
    if view == "none":
        note = (row.get("note") or "").strip()
        if note.lower().startswith("changes no shape:"):
            return f"{NO_SHAPE_SENTENCE[:-1]}: {note.split(':', 1)[1].strip()}"
        return f"{NO_SHAPE_SENTENCE} {note}".strip()
    if (file_key, row["name"]) in SINGLE_PANEL_ROWS:
        return (f"One top view of {tool} with both plates side by side, the plug end at the top: "
                f"what the file prints at {_fmt_value(d['before'])}. At {_fmt_value(d['after'])} it prints "
                f"one plate. Nothing is marked in red: this dial changes the layout, not the plate.")
    if view == "top":
        subject = "one plate of the two-sided puller" if file_key == TWO_SIDED else "the one-sided puller"
        overview = f"Two top views of {subject}, before left and after right, the plug end at the top."
    else:
        axis = "x" if view == "section-x" else "y"
        overview = (f"Two vertical slices of {tool} at {axis} = {_fmt_value(d.get('at') or 0)} mm, "
                    "before left and after right, the top face up.")
    ctx = d.get("context") or {}
    ctx_words = (" with " + " and ".join(f"{_lower_first(titles.get(k, k))} set to {_fmt_value(v)}" for k, v in ctx.items())) if ctx else ""
    if view == "top" and plug_width is not None:
        left = f"Left: the defaults{ctx_words}, a {_fmt_value(plug_width)} mm wide plug in teal."
    else:
        left = f"Left: the defaults{ctx_words}, the plug in teal in the cut."
    if isinstance(d["after"], (str, bool)):
        after_words = f"set to {_fmt_value(d['after'])}"
    else:
        after_words = "at " + _fmt_value(d["after"]) + (f" {unit}" if unit else "")
    right_short = f"Right: {_lower_first(title)} {after_words}."
    right_full = f"Right: {_lower_first(title)} {after_words}: {_lower_first(row['changes'])}"
    dim = entry.get("dimension")
    dimension = describe_dimension(dim, d["after"]) if dim else ""
    max_words = LONG_MAX_WORDS_DIMENSION if dim else LONG_MAX_WORDS
    locations = FEATURE_LOCATIONS[file_key]
    callouts = entry.get("callouts") or []

    def marked(with_locations: str) -> str:
        """``with_locations``: "all", "single" (entries with one name only) or "none"."""
        if not callouts:
            return "Nothing is marked in red."
        items = []
        for n, names, removed in callouts:
            state = ", removed" if removed else ""
            if with_locations == "all" or (with_locations == "single" and len(names) == 1):
                where = "; ".join(locations.get(nm, nm) for nm in names)
                items.append(f"{n}, {_join_names(names)}: {where}{state}.")
            else:
                items.append(f"{n}, {_join_names(names)}{state}.")
        return "Marked in red: " + " ".join(items)

    named = {nm for _n, names, _r in callouts for nm in names}
    unnamed = [f for f in locations if f not in named][:4]
    if FEATURE_FALLBACK[file_key] in named:
        closing = "Everything else follows the outline."
    elif unnamed:
        stayed = _join_names(unnamed)
        closing = f"{stayed[:1].upper()}{stayed[1:]} stay where they were."
    else:
        closing = ""
    text = ""
    for parts in ([overview, left, right_full, dimension, marked("all"), closing],
                  [overview, left, right_full, dimension, marked("all")],
                  [overview, left, right_short, dimension, marked("all")],
                  [overview, left, right_short, dimension, marked("single")],
                  [overview, left, right_short, dimension, marked("none")]):
        text = " ".join(part for part in parts if part)
        if len(text.split()) <= max_words:
            return text
    return text


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


def build_none(row: Dict[str, Any], out_dir: Path, unit: Optional[str] = None) -> Dict[str, Any]:
    entry = index_row(row, 0, 0.0, [], ["none"])
    entry["alt"] = describe_alt(row, unit, entry)
    entry["long_description"] = describe_long(row, unit, entry)
    svg = compose_none_svg(note=row.get("note") or "", title=row["title"], name=row["name"],
                           desc=entry["long_description"])
    path = out_dir / svg_relpath(row)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")
    return entry


def build_diff(row: Dict[str, Any], renderer: Renderer, defaults: Dict[str, Any], out_dir: Path,
               layout: str = "pair", unit: Optional[str] = None,
               titles: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
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
    bodies = []
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
            bodies.append(body)
    b_out, a_out = outlines
    context = dict(d.get("context") or {})
    if view == "top":
        plug = plug_polygon(file_key, after_params, a_out)
        before_plug = plug_polygon(file_key, base, b_out)
    else:
        plug = section_plug_polygon(file_key, after_params, view, at, bodies[1])
        before_plug = section_plug_polygon(file_key, base, view, at, bodies[0])
        context[view] = at  # the cut plane, shown with the context
    dimension = None
    if d.get("dimension"):
        dimension = anchor_dimension(d["dimension"]["at"], file_key, after_params, a_out, plug, view, at,
                                     d["after"], unit)
        if dimension is None:
            logger.warning("%s %s: the anchor %s gave no dimension callout", file_key, row["name"], d["dimension"]["at"])
    dim_entry = ({"kind": dimension["kind"], "at": d["dimension"]["at"], "label": dimension["label"],
                  "drawn": round(dimension_span(dimension), 1)}
                 if dimension else None)
    regions, area = outline_regions(b_out, a_out)
    if view == "top":
        feats = footprints(file_key, base, b_out, a_out, after_params)
    else:
        feats = footprints(file_key, base, top_view(file_key, stls[0], base),
                           top_view(file_key, stls[1], after_params), after_params)
    body_area = sum(p.area for p in b_out.solids) if view == "top" else 0.0
    edge_rings = ([LineString(max(o.solids, key=lambda q: q.area).exterior.coords) for o in (b_out, a_out) if o.solids]
                  if view == "top" else [])
    moved = moved_openings(file_key, base, b_out, after_params, a_out) if view == "top" else []
    named = classify_regions(file_key, regions, feats, view, at, body_area, edge_rings, moved) if regions else []
    features = feature_names(named)
    callouts: List[List[Any]] = []
    alt = long_description = None
    if layout == "pair" and view in PAIR_VIEWS:
        crop = d.get("crop")
        single = (file_key, row["name"]) in SINGLE_PANEL_ROWS
        plan = plan_callouts(b_out, a_out, named, shapely.box(*(float(v) for v in crop)) if crop else None)
        callouts = [] if single else plan.key_rows
        draft = index_row(row, len(regions), area, tags, features, named, callouts)
        draft["dimension"] = dim_entry
        plug_width = effective_measurements(file_key, base)["measure_plug_width_prong_end"] if view == "top" else None
        alt = describe_alt(row, unit, draft)
        long_description = describe_long(row, unit, draft, plug_width, titles)
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
            dimension=dimension,
            desc=long_description,
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
    entry = index_row(row, len(regions), area, tags, features, named, callouts)
    entry["dimension"] = dim_entry
    entry["alt"] = alt if alt is not None else describe_alt(row, unit, entry)
    entry["long_description"] = (long_description if long_description is not None
                                 else describe_long(row, unit, entry, None, titles))
    return entry


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
    catalog = load_catalog()  # the whole catalog: a context dial's title is needed even when its row is not rebuilt
    titles = {key: {r["name"]: r["title"] for r in catalog if r["file"] == key} for key in SCADS}
    produced: List[Dict[str, Any]] = []
    for row in rows:
        view = row["diagram"]["view"]
        t0 = time.time()
        if view == "none":
            entry = build_none(row, out_dir, (mappings[row["file"]].get(row["name"]) or {}).get("unit"))
        elif view == "top" or view in SECTION_VIEWS:
            r0, h0 = renderer.renders, renderer.hits
            unit = (mappings[row["file"]].get(row["name"]) or {}).get("unit")
            entry = build_diff(row, renderer, defaults[row["file"]], out_dir, layout=layout, unit=unit,
                               titles=titles[row["file"]])
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
# The storyboards: the four Customizer steps on one plug, five panels
# ---------------------------------------------------------------------------

STORYBOARDS = PROJECT_ROOT / "dial_storyboards.json"
STORYBOARD_INDEX_NAME = "storyboards_index.json"
SB_PANEL_W = 48.0  # mm, the widest ordinary panel; the others share its scale
SB_GAP = 13.0  # mm between panels, the numbered arrow lives here
SB_STUB = 6.0  # mm, the wrap arrow's stubs at the end of row 1 and the start of row 2
SB_CIRCLE = 3.2  # mm, the step number's circle
SB_CAPTION = 2.4  # mm, the step names under the rows
SB_LONG_MAX_WORDS = 150
LAYOUT_STEP = "Step 4 - Print Layout"  # the two-sided file's last step: both plates in Full mode, nothing marked


def load_storyboards() -> List[Dict[str, Any]]:
    return json.loads(STORYBOARDS.read_text(encoding="utf-8"))


def storyboard_stages(board: Dict[str, Any], renderer: Renderer, defaults: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Render the five cumulative states through the cache and diff each
    against the previous one; the layout step (both plates) is drawn as it
    prints, with no marks."""
    file_key = board["file"]
    params = dict(defaults)
    prev: Optional[Dict[str, Any]] = None
    stages: List[Dict[str, Any]] = []
    for stage in board["stages"]:
        params = dict(params)
        params.update(stage["set"])
        layout = stage["step"] == LAYOUT_STEP
        if layout:
            defines = {k: v for k, v in params.items() if not _same_value(v, defaults.get(k))}
            defines["render_mode"] = "Full"
        else:
            defines = defines_for(file_key, "storyboard", params, defaults)
        stl, log, _hit = renderer.render(file_key, defines)
        outline = top_view(file_key, stl, params)
        plug = None if layout else plug_polygon(file_key, params, outline)
        named: List[Tuple[Polygon, List[str]]] = []
        area = 0.0
        plan = PairPlan()
        if prev is not None and not layout:
            regions, area = outline_regions(prev["outline"], outline)
            if regions:
                fp = footprints(file_key, prev["params"], prev["outline"], outline, params)
                body_area = sum(q.area for q in prev["outline"].solids)
                edge_rings = [LineString(max(o.solids, key=lambda q: q.area).exterior.coords)
                              for o in (prev["outline"], outline) if o.solids]
                moved = moved_openings(file_key, prev["params"], prev["outline"], params, outline)
                named = classify_regions(file_key, regions, fp, "top", 0.0, body_area, edge_rings, moved)
            plan = plan_callouts(prev["outline"], outline, named)
        stages.append({"step": stage["step"], "set": stage["set"], "params": params, "outline": outline,
                       "plug": plug, "named": named, "area": area, "plan": plan,
                       "tags": warning_tags(log), "layout": layout})
        prev = stages[-1]
    return stages


def compose_storyboard_svg(board: Dict[str, Any], stages: Sequence[Dict[str, Any]], desc: str) -> str:
    """The 3 + 2 grid: five panels at one scale (the layout panel may be
    wider), each drawn like an after panel against the previous stage, the
    numbered arrows between them, the step names under the rows, the wrap
    from panel 3 to panel 4 as two stubs in one arrow group."""
    panels = []
    for k, st in enumerate(stages):
        geoms = list(st["outline"].solids) + list(st["outline"].recess) + ([st["plug"]] if st["plug"] is not None else [])
        if k > 0 and not st["layout"]:
            pv = stages[k - 1]
            geoms += list(pv["outline"].solids) + list(pv["outline"].recess) + ([pv["plug"]] if pv["plug"] is not None else [])
        bx0, by0, bx1, by1 = shapely.union_all(geoms).bounds
        x0, y0, x1, y1 = bx0 - MARGIN, by0 - MARGIN, bx1 + MARGIN, by1 + MARGIN
        panels.append({"frame": _Frame(x0, y0, x1, y1, 0.0), "W": x1 - x0, "H": y1 - y0})
    s = SB_PANEL_W / max(pn["W"] for pn, st in zip(panels, stages) if not st["layout"])
    for pn in panels:
        pn["s"], pn["w_page"], pn["h_page"] = s, pn["W"] * s, pn["H"] * s
    row_h1 = max(pn["h_page"] for pn in panels[:3])
    row_h2 = max(pn["h_page"] for pn in panels[3:])
    cap_h = 1.5 + SB_CAPTION + 1.0
    cells = [SB_PANEL_W] * 3
    total_w = SB_STUB + 1.0 + sum(cells) + 2 * SB_GAP + 0.5 + SB_STUB + 1.0
    total_h = 2.0 + row_h1 + cap_h + 4.0 + row_h2 + cap_h + 1.0
    origins: Dict[int, Tuple[float, float]] = {}
    y_row1 = 2.0
    y_row2 = 2.0 + row_h1 + cap_h + 4.0
    for k in range(3):
        origins[k] = (SB_STUB + 1.0 + k * (SB_PANEL_W + SB_GAP), y_row1 + (row_h1 - panels[k]["h_page"]) / 2)
    for k in (3, 4):
        origins[k] = (SB_STUB + 1.0 + (k - 3) * (SB_PANEL_W + SB_GAP), y_row2 + (row_h2 - panels[k]["h_page"]) / 2)
    svg: List[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_w:.2f}mm" height="{total_h:.2f}mm" '
        f'viewBox="0 0 {total_w:.2f} {total_h:.2f}" role="img">',
        f'<title>{_esc(board["title"])}</title>',
        f'<desc>{_esc(desc)}</desc>',
        f'<rect width="{total_w:.2f}" height="{total_h:.2f}" fill="white"/>',
    ]
    for k, (st, pn) in enumerate(zip(stages, panels)):
        ox, oy = origins[k]
        if not st["layout"]:
            ox += (SB_PANEL_W - pn["w_page"]) / 2
        fr = pn["frame"]
        svg.append(f'<g class="panel" id="stage{k}" transform="translate({ox:.2f} {oy:.2f}) scale({pn["s"]:.4f})">')
        if st["plug"] is not None:
            svg.append(_filled_polygon(fr, st["plug"], COLOR_PLUG, PLUG_OPACITY))
        marks = _red_marks(st["plan"])
        svg.extend(_draw_outline(fr, st["outline"], COLOR_OUTLINE, False, STROKE_OUTER, STROKE_INNER, _marks_cut(marks)))
        svg.extend(_marked(fr, mark) for mark in marks)
        svg.append("</g>")

    def arrow(xa: float, xb: float, y: float, step: int, caption_y: float, caption: Optional[str],
              anchor: str = "middle") -> List[str]:
        cx = (xa + xb) / 2
        out = [_svg_arrow_h(xa, xb, y),
               f'<circle cx="{cx:.2f}" cy="{y - 4.2:.2f}" r="{SB_CIRCLE / 2}" fill="white" stroke="#000" stroke-width="0.35"/>',
               _text(cx, y - 4.2 + 1.0, str(step), 2.6, bold=True)]
        if caption:
            tx = cx if anchor == "middle" else xa
            out.append(_text(tx, caption_y, caption, SB_CAPTION, anchor=anchor, fill="#333333"))
        return out

    steps = [st["step"] for st in stages[1:]]
    mid1, mid2 = y_row1 + row_h1 / 2, y_row2 + row_h2 / 2
    cap1, cap2 = y_row1 + row_h1 + 1.5 + SB_CAPTION, y_row2 + row_h2 + 1.5 + SB_CAPTION
    for k in (0, 1):
        xa = origins[k][0] + SB_PANEL_W + 1.0
        svg.append('<g class="arrow">')
        svg.extend(arrow(xa, xa + SB_GAP - 2.0, mid1, k + 1, cap1, steps[k]))
        svg.append("</g>")
    svg.append('<g class="arrow">')
    xa = origins[2][0] + SB_PANEL_W + 0.5
    svg.extend(arrow(xa, xa + SB_STUB, mid1, 3, cap1, None))
    svg.extend(arrow(0.5, 0.5 + SB_STUB, mid2, 3, cap2, steps[2], anchor="start"))
    svg.append("</g>")
    xa = origins[3][0] + SB_PANEL_W + 1.0
    svg.append('<g class="arrow">')
    svg.extend(arrow(xa, xa + SB_GAP - 2.0, mid2, 4, cap2, steps[3]))
    svg.append("</g>")
    svg.append("</svg>")
    return "\n".join(x for x in svg if x) + "\n"


def _stage_dials(stage_set: Dict[str, Any], titles: Dict[str, str], units: Dict[str, Optional[str]],
                 with_values: bool) -> List[str]:
    """The dials a storyboard stage sets, by name, with their values when
    ``with_values``; a pair named "... at the prong end" and "... at the cord
    end" is named once ("plug width at both ends")."""
    items = []
    for dial, value in stage_set.items():
        unit = units.get(dial)
        shown = f"{_fmt_value(value)} {unit}" if unit and not isinstance(value, (str, bool)) else _fmt_value(value)
        items.append((_lower_first(titles.get(dial, dial)), shown))
    names = [name for name, _shown in items]
    parts: List[str] = []
    done: set = set()
    for i, (name, shown) in enumerate(items):
        if i in done:
            continue
        stem, _sep, end = name.partition(" at the ")
        other = {"prong end": f"{stem} at the cord end", "cord end": f"{stem} at the prong end"}.get(end)
        j = names.index(other) if other in names else None
        if j is None or j in done:
            parts.append(f"{name} {shown}" if with_values else name)
            continue
        done.add(j)
        prong, cord = (shown, items[j][1]) if end == "prong end" else (items[j][1], shown)
        if not with_values:
            parts.append(f"{stem} at both ends")
        elif prong == cord:
            parts.append(f"{stem} at both ends {prong}")
        else:
            parts.append(f"{stem} {prong} at the prong end and {cord} at the cord end")
    return parts


def describe_storyboard(board: Dict[str, Any], stages: Sequence[Dict[str, Any]], titles: Dict[str, str],
                        units: Dict[str, Optional[str]], defaults: Dict[str, Any]) -> Tuple[str, str]:
    """The storyboard's alt text and long description, at most
    SB_LONG_MAX_WORDS: an overview, then one line per stage named as the
    picture names it, Start for the defaults and each step by its own name
    (the picture numbers its four arrows 1 to 4, one per step). Every dial a
    step sets is named, with its value when the whole fits; when the names
    alone still run long, each list of parts takes a single "the"."""
    file_key = board["file"]
    tool = TOOL_NAMES[file_key]
    alt = f"{tool[0].upper()}{tool[1:]}, the four Customizer steps on a {board['plug_label']}, five stages left to right."
    plug_w = _fmt_value(effective_measurements(file_key, defaults)["measure_plug_width_prong_end"])
    overview = (f"Five stages of {tool}, left to right, the top row first, the plug end at the top; "
                "arrows numbered 1 to 4 show the steps, and red dashes mark the edges each step moved.")

    def stage_line(k: int, st: Dict[str, Any], with_values: bool, one_article: bool) -> str:
        if k == 0:
            return f"Start, the defaults: the tool as the file opens, with a {plug_w} mm wide plug in teal."
        if st["layout"]:
            return f"{st['step']}: both plates side by side in one file, what you print; nothing marked."
        parts = _stage_dials(st["set"], titles, units, with_values)
        plan = st["plan"]
        gone = feature_names([rn for rn, rm in zip(plan.regions, plan.removed) if rm])
        feats = [f for f in feature_names(st["named"]) if f not in gone]
        if feats or gone:
            red = f"; red on {_join_names(feats, one_article)}" if feats else ""
            if gone:
                red += f"; {_join_names(gone, one_article)} removed, drawn in red from the old outline"
        elif file_key == TWO_SIDED and st["step"].startswith("Step 3"):
            red = "; no strap slot on a plug this short, so nothing moved"
        else:
            red = "; nothing moved"
        return f"{st['step']}: {', '.join(parts)}{red}."

    for with_values, one_article in ((True, False), (False, False), (False, True)):
        lines = [stage_line(k, st, with_values, one_article) for k, st in enumerate(stages)]
        text = overview + " " + " ".join(lines)
        if len(text.split()) <= SB_LONG_MAX_WORDS:
            return alt, text
    return alt, text


def build_storyboards(out_dir: Path, renderer: Renderer, catalog: Sequence[Dict[str, Any]]) -> Path:
    """Draw both storyboards under ``out_dir`` and write their index."""
    mappings = {key: load_mapping(key) for key in SCADS}
    defaults = {key: mapping_defaults(m) for key, m in mappings.items()}
    entries = []
    for board in load_storyboards():
        file_key = board["file"]
        t0 = time.time()
        stages = storyboard_stages(board, renderer, defaults[file_key])
        titles = {r["name"]: r["title"] for r in catalog if r["file"] == file_key}
        units = {name: row.get("unit") for name, row in mappings[file_key].items()}
        alt, long_description = describe_storyboard(board, stages, titles, units, defaults[file_key])
        svg = compose_storyboard_svg(board, stages, long_description)
        rel = f"{file_key}/storyboard.svg"
        path = out_dir / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(svg, encoding="utf-8")
        tags = sorted({tag for st in stages for tag in st["tags"]})
        entries.append({"file": file_key, "name": "storyboard", "key": board["key"], "title": board["title"],
                        "svg": rel, "stages": [len(st["plan"].regions) for st in stages], "tags": tags,
                        "alt": alt, "long_description": long_description})
        logger.info("storyboard %s: stages %s, %.1f s%s", board["key"], entries[-1]["stages"], time.time() - t0,
                    f", tags {tags}" if tags else "")
    index_path = out_dir / STORYBOARD_INDEX_NAME
    index_path.write_text(json.dumps(entries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return index_path


def load_storyboard_index(out_dir: Path) -> List[Dict[str, Any]]:
    path = out_dir / STORYBOARD_INDEX_NAME
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


# ---------------------------------------------------------------------------
# docs/dials/README.md: every diagram inline with its words
# ---------------------------------------------------------------------------

README_NAME = "README.md"
README_TITLE = "Dial diagrams"
README_INTRO = (
    "Every dial of the one-sided puller and the two-sided puller has a picture here: "
    "the tool at the dial's default on the left with the plug in teal, an arrow with the "
    "two values, and the tool after the dial moved on the right, drawn once in black with "
    "the edges that moved in red dashes; the numbered dots on those edges match the key "
    "beside the picture.",
    "The pictures are cut from the same OpenSCAD files you print from, at 1 unit = 1 mm. "
    "Under each picture: the long form of its text alternative, then the two values and "
    "the parts that moved.",
)
README_FILE_HEADINGS = {ONE_SIDED: "One-sided puller", TWO_SIDED: "Two-sided puller"}


def _readme_entry(row: Dict[str, Any], entry: Dict[str, Any]) -> List[str]:
    d = row["diagram"]
    lines = [f"`{row['name']}`: {row['title']}", "", f"![{entry['alt']}]({svg_relpath(row)})", "",
             entry["long_description"], ""]
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
                 index_rows: Sequence[Dict[str, Any]],
                 storyboards: Sequence[Dict[str, Any]] = ()) -> Path:
    """The Markdown index: H1, the intro and the legend, H2 per file, the
    storyboard section when one exists, H3 per Customizer section in mapping
    order, one entry per dial."""
    index = {(e["file"], e["name"]): e for e in index_rows}
    boards = {e["file"]: e for e in storyboards}
    lines = [f"# {README_TITLE}", "", README_INTRO[0], "", README_INTRO[1], "", LEGEND_LINE + ".", ""]
    count = 0
    for file_key in (ONE_SIDED, TWO_SIDED):
        lines += [f"## {README_FILE_HEADINGS[file_key]}", ""]
        board = boards.get(file_key)
        if board:
            lines += ["### The four steps", "", f"![{board['alt']}]({board['svg']})", "", board["long_description"], ""]
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
    parser.add_argument("--storyboards", action="store_true", help="draw the two storyboards of dial_storyboards.json and rewrite the README (no catalog rows built)")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    catalog = load_catalog()
    if args.readme or args.storyboards:
        index_path = args.out / INDEX_NAME
        if not index_path.exists():
            logger.error("no index at %s; build the rows first", index_path)
            return 1
        if args.storyboards:
            renderer = Renderer(cache_dir=args.cache, force=args.force)
            build_storyboards(args.out, renderer, catalog)
            logger.info("storyboards: %d renders (%.1f s in OpenSCAD), %d cache hits", renderer.renders, renderer.seconds, renderer.hits)
        write_readme(args.out, catalog, json.loads(index_path.read_text(encoding="utf-8")), load_storyboard_index(args.out))
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
        write_readme(args.out, catalog, index_rows, load_storyboard_index(args.out))
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
