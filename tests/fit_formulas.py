"""Pure-Python re-implementation of the measurement derivations.

Single source of truth pairing
------------------------------
This module mirrors ``src/fit_measured.scad`` formula-for-formula and
constant-for-constant. **Any change to one file must be applied to the
other**; the render-lane test
``tests/test_fit_derivations.py::test_echo_matches_python`` enforces the
pairing by rendering the SCAD with ``-o <tmp>.echo`` and comparing every
``fit_derived: <key>=<value>`` line against :func:`derive`.

The quick lane uses :func:`derive` directly for the Medium-parity,
clamp-edge, size-override, and monotonicity checks without invoking
OpenSCAD.

Calibration: all constants are anchored to the v6.0 CAD reference
("Plug Puller 3.1 - B"), measured during development in the historical
dev repo (plug-puller-openscad).
``derive()`` with ``size="Medium"`` and default measurements reproduces
``PRESET_MEDIUM`` exactly.

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import math
from typing import Any, Dict, Mapping, Optional

# ---------------------------------------------------------------------------
# Clearance and design constants (mirror of fit_measured.scad)
# ---------------------------------------------------------------------------

FIT_GRIP_CLEARANCE = 5.4
FIT_FINGER_WEB = 7.6
FIT_SLIDE_CLEARANCE = 0.835
FIT_CORD_CLEARANCE = 0.7625

FIT_T_LENGTH_RATIO = 32 / 15
FIT_T_HOLDER_W_RATIO = 7 / 3
FIT_T_HOLDER_L_RATIO = 16 / 15

FIT_FINGER_HOOK_CLEARANCE = 3.28

# J-hook cord catch (v6)
FIT_HOOK_STEM_OFFSET = 4.48
FIT_HOOK_CATCH_REACH = 4.55
FIT_HOOK_TIP_DROP = 1.98

FIT_WALL_PLATE_DEPTHS = {
    "Standard flat plate": 3.81,
    "Rocker / Decora": 5.3,
    "Oversized / Jumbo": 6.3,
    "No plate / flush": 1.5,
}

FIT_NOTCH_ROUNDING = 2.54
FIT_SEAT_BEYOND_NOTCH = 3.83
FIT_POCKET_WIDTH_CLEARANCE = 6.7
FIT_DOME_DROP = 2.15
FIT_POCKET_FINGER_GAP = 5.5

FIT_RECESS_RATIO_SEAT = 0.15875
FIT_RECESS_RATIO_BODY = 0.127
FIT_MIN_POCKET_FLOOR = 1.5

FIT_BODY_HAND_RATIO = 81.55 / 85
FIT_BODY_CORNER_RATIO = 3 / 81.55
FIT_BODY_TOP_RATIO = 35.75 / 81.55
FIT_BODY_MIDDLE_RATIO = 62.1 / 81.55
FIT_SIDE_CORNER_RATIO = 5.45 / 65.5
FIT_SIDE_ROUNDING_RATIO = 17.05 / 81.55
FIT_THICKNESS_HAND_RATIO = 6.35 / 85

FIT_BODY_TOP_ROUNDING = 2.54
FIT_FINGER_RIM_FILLET = 2.5
FIT_T_GAP_SIDE_ROUNDING = 0
FIT_T_HOLDER_SIDE_ROUNDING = 1.27
FIT_T_TOP_BOTTOM_ROUNDING = 0

# Wing velcro (v6)
FIT_WING_SIDE_INSET = 4.3
FIT_WING_FINGER_WEB = 5.0
FIT_WING_POCKET_WEB = 2.5
FIT_WING_ZIP_WEB = 4.0
FIT_WING_ROUND = 1.5

# Classic slot fallback geometry (the v4/v5 12x7 slot; wings ignore these)
FIT_VELCRO_LENGTH = 12
FIT_VELCRO_WIDTH = 7
FIT_VELCRO_EDGE_OFFSET = 7.02
FIT_VELCRO_POCKET_MARGIN = 6.0

FIT_STRAP_WIDTH = 15

FIT_ZIP_DIAMETER = 5.08
FIT_ZIP_HEIGHT_SPACING = 17.78
FIT_ZIP_WIDTH_SPACING = 17.7
FIT_ZIP_DISTANCE_FROM_NOTCH = 5.1
FIT_ZIP_COUNTERSINK = 0.9

# Minimum wall between the lower zip-row bore and the finger-hole bore
# (D-20 lengthens the body to preserve it; see fit_measured.scad).
FIT_ZIP_FINGER_WEB = 2.5

# Size table: size -> (finger_width, hand_width). ANSUR II 2012 hand breadth
# + Rogers 2008 PIP-joint breadth. Medium is the calibration anchor.
FIT_SIZE_TABLE = {
    "Small": (16.5, 72),
    "Medium": (20, 85),
    "Large": (23, 96),
}

# Default input vector — with size "Medium" this reproduces PRESET_MEDIUM
# exactly (the Medium-parity invariant). The plug is described by two-station
# measurements: width / thickness near the wall (prong face) and near the
# cable end, plus the true body length (wall plate to back face).
DEFAULT_MEASUREMENTS: Dict[str, Any] = {
    "size": "Medium",
    "measure_plug_length": 25.5,
    "measure_plug_width_wall": 25.0,
    "measure_plug_width_cable": 25.0,
    "measure_plug_thickness_wall": 20.0,
    "measure_plug_thickness_cable": 20.0,
    "measure_cord_thickness": 4.0,
    "measure_wall_plate_style": "Standard flat plate",
    "measure_finger_width": 20.0,
    "measure_hand_width": 85.0,
}


def _clamp(v: float, lo: float, hi: float) -> float:
    """Mirror of OpenSCAD's ``_fit_clamp(v, lo, hi) = max(lo, min(v, hi))``."""
    return max(lo, min(v, hi))


def _round05(v: float) -> float:
    """Mirror of ``_fit_round05``: snap to 0.05 mm (floor(v*20 + 0.5)/20)."""
    return math.floor(v * 20 + 0.5) / 20


def _round_half(v: float) -> float:
    """Mirror of ``_fit_round_half``: snap to 0.5 (floor(v*2 + 0.5)/2)."""
    return math.floor(v * 2 + 0.5) / 2


def _openscad_round(v: float) -> float:
    """OpenSCAD ``round()`` rounds half away from zero (Python rounds half to
    even), so mirror the SCAD behaviour explicitly."""
    return math.floor(v + 0.5) if v >= 0 else math.ceil(v - 0.5)


def derive(measurements: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    """Compute every FIT_MEASURED value from an input vector.

    ``measurements`` may override any subset of :data:`DEFAULT_MEASUREMENTS`
    (including ``size``); missing keys take their defaults. Returns a dict
    with exactly the same key set as ``PRESET_MEDIUM`` in
    ``src/presets.scad``.
    """
    m = dict(DEFAULT_MEASUREMENTS)
    if measurements:
        unknown = set(measurements) - set(DEFAULT_MEASUREMENTS)
        if unknown:
            raise KeyError(f"Unknown measurement inputs: {sorted(unknown)}")
        m.update(measurements)

    size = m["size"]

    # D-1 / D-2 — size -> hand pair ("Measure my hand" honors the sliders)
    finger_width, hand_width = FIT_SIZE_TABLE.get(
        size, (m["measure_finger_width"], m["measure_hand_width"])
    )

    # D-3 … D-8 — hook family
    t_gap = _clamp(m["measure_cord_thickness"] + FIT_CORD_CLEARANCE, 3, 10)
    t_length = _clamp(FIT_T_LENGTH_RATIO * t_gap, 6, 20)
    t_holder_w = _clamp(FIT_T_HOLDER_W_RATIO * t_gap, 8, 25)
    t_holder_l = _clamp(FIT_T_HOLDER_L_RATIO * t_gap, 2, 15)

    # D-9 … D-11 — finger holes
    finger_d = _clamp(finger_width + FIT_GRIP_CLEARANCE, 15, 40)
    finger_spacing = _clamp(finger_d + FIT_FINGER_WEB, 20, 50)
    finger_dx = max(0.0, finger_spacing / 2 - t_holder_w / 2)
    finger_reach = finger_d / 2 + FIT_FINGER_HOOK_CLEARANCE
    finger_y = _round05(
        max(
            finger_d / 2 + 2,
            t_length
            + math.sqrt(max(0.0, finger_reach**2 - finger_dx**2)),
        )
    )

    # D-12 … D-14 — plug wall notch (from the WALL-station width — the end
    # of the plug that meets the wall is the end the notch must straddle)
    notch_w = _clamp(
        m["measure_plug_width_wall"] + 2 * FIT_SLIDE_CLEARANCE, 5, 40
    )
    notch_h = FIT_WALL_PLATE_DEPTHS.get(
        m["measure_wall_plate_style"], FIT_WALL_PLATE_DEPTHS["Standard flat plate"]
    )
    notch_r = min(FIT_NOTCH_ROUNDING, notch_h, notch_w / 4)

    # D-15 … D-18 — dome pocket
    seat_d = _clamp(notch_w + FIT_SEAT_BEYOND_NOTCH, 10, 45)
    pocket_w = _clamp(
        m["measure_plug_width_wall"] + FIT_POCKET_WIDTH_CLEARANCE, 10, 45
    )
    dome_drop = min(FIT_DOME_DROP, 0.25 * m["measure_plug_length"])
    # D-43 — plug side taper (= the plug side rail angle), DERIVED from the
    # two width stations over the plug length (sign encodes which end is
    # wider), clamped to the rail window. Mirrors _eff_plug_side_angle in
    # the main SCAD.
    side_angle = math.degrees(
        math.atan(
            ((m["measure_plug_width_wall"] - m["measure_plug_width_cable"]) / 2)
            / max(1.0, m["measure_plug_length"])
        )
    )
    pocket_side_angle = _clamp(side_angle, -15, 25)

    # D-19 / D-20 — pocket depth and body length. The pocket runs the FULL
    # plug length whenever the 120 mm body ceiling allows; the only cap is
    # the depth budget left after the cord-end features claim their run.
    pocket_depth_max = 120 - (FIT_POCKET_FINGER_GAP + finger_y + finger_d / 2)
    pocket_depth = _clamp(m["measure_plug_length"], 12, pocket_depth_max)
    # Zip-grid floor: keep a FIT_ZIP_FINGER_WEB wall between the lower zip
    # row and the nearest finger bore (mirrors D-20a in fit_measured.scad).
    zip_finger_dx = abs(finger_spacing / 2 - FIT_ZIP_WIDTH_SPACING / 2)
    zip_finger_rr = finger_d / 2 + FIT_ZIP_DIAMETER / 2 + FIT_ZIP_FINGER_WEB
    zip_dy_req = math.sqrt(max(0.0, zip_finger_rr**2 - zip_finger_dx**2))
    length_for_zip = (
        finger_y + zip_dy_req + FIT_ZIP_HEIGHT_SPACING
        + FIT_ZIP_DISTANCE_FROM_NOTCH + notch_h
    )
    puller_length = _clamp(
        max(
            pocket_depth + FIT_POCKET_FINGER_GAP + finger_y + finger_d / 2,
            length_for_zip,
        ),
        55, 120,
    )

    # D-21 — slab thickness
    thickness = _round05(_clamp(FIT_THICKNESS_HAND_RATIO * hand_width, 5, 9))

    # D-22 / D-23 — pocket floor heights (overall plug thickness = the
    # fatter of the two stations; mirrors _eff_plug_thickness)
    plug_thickness = max(
        m["measure_plug_thickness_wall"], m["measure_plug_thickness_cable"]
    )
    seat_floor = thickness - _clamp(
        FIT_RECESS_RATIO_SEAT * plug_thickness,
        2,
        thickness - FIT_MIN_POCKET_FLOOR,
    )
    body_floor = thickness - _clamp(
        FIT_RECESS_RATIO_BODY * plug_thickness,
        1,
        thickness - FIT_MIN_POCKET_FLOOR,
    )

    # D-28 … D-33 — body envelope (octagon control points, pre-rounding)
    bottom_width = _round05(_clamp(FIT_BODY_HAND_RATIO * hand_width, 50, 120))
    top_width = _round05(
        _clamp(max(FIT_BODY_TOP_RATIO * bottom_width, seat_d), 25, 80)
    )
    bottom_corners = _round05(
        _clamp(FIT_BODY_CORNER_RATIO * bottom_width, 3, 80)
    )
    middle_width = _round05(
        _clamp(max(FIT_BODY_MIDDLE_RATIO * bottom_width, top_width + 4), 25, 120)
    )
    side_corner = _round05(_clamp(FIT_SIDE_CORNER_RATIO * puller_length, 3, 35))
    side_rounding = _round05(
        _clamp(FIT_SIDE_ROUNDING_RATIO * bottom_width, 0, 30)
    )

    # D-34 … D-36 — velcro / wing placement
    middle_y = (side_corner + puller_length) / 2

    def hw_at(y: float) -> float:
        if y <= side_corner:
            return (
                bottom_corners / 2
                + (bottom_width / 2 - bottom_corners / 2) * y / side_corner
            )
        if y <= middle_y:
            return bottom_width / 2 + (middle_width / 2 - bottom_width / 2) * (
                y - side_corner
            ) / (middle_y - side_corner)
        return middle_width / 2 + (top_width / 2 - middle_width / 2) * (
            y - middle_y
        ) / (puller_length - middle_y)

    velcro_y = _round05(puller_length - pocket_depth + FIT_VELCRO_POCKET_MARGIN)
    side_edge_angle = math.degrees(
        math.atan2(puller_length - middle_y, top_width / 2 - middle_width / 2)
    )
    velcro_rot = _round_half(side_edge_angle - 90)
    velcro_x = _round05(hw_at(velcro_y) - FIT_VELCRO_EDGE_OFFSET)

    # D-37 … D-40 — J-hook cord catch. Offsets scale off the (measured-Medium)
    # base gap / crossbar so the catch stays proportional across cord sizes.
    hook_stem_offset = _round05(FIT_HOOK_STEM_OFFSET * t_gap / 4.7625)
    hook_catch_reach = _round05(FIT_HOOK_CATCH_REACH * t_holder_w / 11.1125)
    hook_tip_drop = FIT_HOOK_TIP_DROP
    zip_countersink = FIT_ZIP_COUNTERSINK

    return {
        # -- Body Shape --
        "puller_length": puller_length,
        "puller_bottom_width": bottom_width,
        "puller_bottom_corners": bottom_corners,
        "puller_top_width": top_width,
        "puller_middle_width": middle_width,
        "puller_side_corner": side_corner,
        "body_thickness": thickness,
        "body_round_bottom_only": True,
        # -- Plug Pocket --
        "pocket_seat_diameter": seat_d,
        "pocket_width": pocket_w,
        "pocket_depth": pocket_depth,
        "pocket_dome_drop": dome_drop,
        "pocket_seat_floor": seat_floor,
        "pocket_floor": body_floor,
        "pocket_side_angle": pocket_side_angle,
        # -- Finger Holes --
        "enable_finger_holes": True,
        "finger_hole_diameter": finger_d,
        "finger_hole_spacing": finger_spacing,
        "finger_hole_y_position": finger_y,
        # -- Hook (J-hook cord catch) --
        "enable_t_hook": True,
        "t_hook_base_gap": t_gap,
        "t_hook_length": t_length,
        "t_hook_holder_width": t_holder_w,
        "t_hook_holder_length": t_holder_l,
        "t_hook_gap_offset": 0,
        "t_hook_leg_offset": 0,
        "t_hook_stem_offset": hook_stem_offset,
        "t_hook_catch_reach": hook_catch_reach,
        "t_hook_tip_drop": hook_tip_drop,
        # -- Plug Wall Notch --
        "enable_plug_wall_notch": True,
        "plug_wall_notch_width": notch_w,
        "plug_wall_notch_height": notch_h,
        "plug_wall_notch_rounding": notch_r,
        # -- Zip Tie Holes (enable comes from the `attachment` dropdown) --
        "zip_tie_hole_diameter": FIT_ZIP_DIAMETER,
        "zip_tie_height_spacing": FIT_ZIP_HEIGHT_SPACING,
        "zip_tie_width_spacing": FIT_ZIP_WIDTH_SPACING,
        "zip_tie_distance_from_notch": FIT_ZIP_DISTANCE_FROM_NOTCH,
        "zip_tie_countersink": zip_countersink,
        # -- Velcro / Wing Strap (enable/style/width come from Step 3) --
        "velcro_hole_length": FIT_VELCRO_LENGTH,
        "velcro_hole_width": FIT_VELCRO_WIDTH,
        "velcro_hole_x_center": velcro_x,
        "velcro_hole_y_center": velcro_y,
        "velcro_hole_rotation": velcro_rot,
        # -- Edge Rounding --
        "body_side_rounding": side_rounding,
        "body_top_rounding": FIT_BODY_TOP_ROUNDING,
        "body_bottom_rounding": 0,
        "velcro_side_rounding": 0,
        "velcro_top_bottom_rounding": 0,
        "finger_hole_rounding": FIT_FINGER_RIM_FILLET,
        "t_hook_holder_side_rounding": FIT_T_HOLDER_SIDE_ROUNDING,
        "t_hook_gap_side_rounding": FIT_T_GAP_SIDE_ROUNDING,
        "t_hook_top_bottom_rounding": FIT_T_TOP_BOTTOM_ROUNDING,
    }
