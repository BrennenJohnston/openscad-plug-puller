// =============================================================================
// fit_measured.scad — measurement → parameter derivation layer (v6.0)
// =============================================================================
//
// This file is `include`d by Plug_Puller_v6_Parametric.scad, directly ABOVE
// `include <presets.scad>`. Include order matters: OpenSCAD evaluates
// top-level assignments in source order, so
//
//   1. the `measure_*` / `size` / preset Customizer inputs (declared in the
//      main SCAD, above the include lines) must exist before the `_fit_*`
//      derivations here, and
//   2. the `FIT_MEASURED` table built here must exist before `preset_value()`
//      in presets.scad resolves any non-Custom size against it.
//
// What lives here
// ---------------
//   - Clearance / design constants calibrated against the v6.0 CAD reference
//     (`v6.0/CAD/v6.0.stl` = "Plug Puller 3.1 - B", measured by
//     scripts/extract_reference_dims.py + scripts/analyze_v6*.py). The
//     reference is inch-native: 1/4" slab, 1" finger bores, 3/16" cord stem.
//   - The size table (Small / Medium / Large hand pairs, ANSUR-II grounded)
//     and the "Measure my hand" passthrough.
//   - Derivations mapping the always-active plug measurements plus the hand
//     pair to every geometry parameter — including the v6 additions:
//     J-hook cord catch (D-37..D-40), wing velcro (D-41..D-42), zip
//     countersink.
//   - `FIT_MEASURED` — a [key, value] lookup table with exactly the same key
//     set as PRESET_MEDIUM (enforced by tests/test_preset_routing.py).
//   - A machine-parseable `fit_derived:` echo block.
//
// Calibration invariant (MEDIUM PARITY)
// -------------------------------------
// With `size = "Medium"` and every `measure_*` input at its default, every
// FIT_MEASURED value equals PRESET_MEDIUM's value exactly — and both equal
// the measured v6 reference geometry. Pinned at three levels:
// tests/fit_formulas.py (pure-Python mirror), the derivation echo parity
// test, and the mesh-level reference-parity test.
//
// Keep tests/fit_formulas.py in sync with every formula and constant here.
//
// No modules, no geometry — assignments and one echo block only.
//
// License: PolyForm Noncommercial 1.0.0

/* [Hidden] */

// ---------------------------------------------------------------------------
// Clearance and design constants (v6-calibrated)
// ---------------------------------------------------------------------------

// Finger-hole bore = knuckle width + this. Reference: 1" bore (25.4) for the
// designer's 20 mm finger -> +5.4. Also absorbs FDM hole undersizing.
FIT_GRIP_CLEARANCE = 5.4;

// Bridge of material between the two finger holes: spacing 33 - bore 25.4.
FIT_FINGER_WEB = 7.6;

// Sliding fit of the notch over a molded plug, per side: notch 26.67
// (1.05") for the 25 mm reference plug.
FIT_SLIDE_CLEARANCE = 0.835;

// Cord slides into the hook stem with light friction: stem 4.7625 (3/16")
// for the 4 mm reference cord.
FIT_CORD_CLEARANCE = 0.7625;

// T/J-hook family ratios (exact inch fractions of the 3/16" stem):
// length 2/5" (x32/15), crossbar 7/16" (x7/3), crossbar length 1/5" (x16/15).
FIT_T_LENGTH_RATIO   = 32 / 15;
FIT_T_HOLDER_W_RATIO = 7 / 3;
FIT_T_HOLDER_L_RATIO = 16 / 15;

// Radial clearance between the finger-hole rim and the hook crossbar corner.
// v6 places the finger holes ~2 mm higher than v5 (more web behind the wider
// J-hook crossbar): calibrated so finger_hole_y derives to 21.8 at Medium.
FIT_FINGER_HOOK_CLEARANCE = 3.28;

// --- J-hook cord catch (v6) --------------------------------------------------
// The v6 reference replaces v5's symmetric T-hook with a chiral J-hook: the
// stem opening is offset toward one side, the crossbar extends past it on the
// catch side, and the stem tip sags below Y = 0 so a hooked cord cannot back
// out. Measured on v6.0.stl (right-hand device).
FIT_HOOK_STEM_OFFSET = 4.48;  // stem center X, offset from crossbar center
FIT_HOOK_CATCH_REACH = 4.55;  // crossbar left (catch) half-extent past center
FIT_HOOK_TIP_DROP    = 1.98;  // stem extends this far below Y = 0

// Wall-plate style -> notch depth. Reference: 0.15" (3.81) standard plate.
FIT_WALL_PLATE_DEPTH_STANDARD  = 3.81;
FIT_WALL_PLATE_DEPTH_DECORA    = 5.3;
FIT_WALL_PLATE_DEPTH_OVERSIZED = 6.3;
FIT_WALL_PLATE_DEPTH_NONE      = 1.5;

// Notch bottom-corner rounding: 2.54 = 0.1".
FIT_NOTCH_ROUNDING = 2.54;

// Dome pocket: seat disc diameter = notch width + this. v6 seat measures
// 30.5 = 26.67 + 3.83 (the seat no longer reaches the top corners; the wider
// body leaves ~2.6 mm shoulder ears per side).
FIT_SEAT_BEYOND_NOTCH = 3.83;

// Dome pocket: ellipse width = plug width + this. v6 widens the plug-body
// recess to 31.7 for a 25 mm reference plug (freer drop-in on the wider body).
FIT_POCKET_WIDTH_CLEARANCE = 6.7;

// Dome pocket: ellipse center sits this far below the top edge.
FIT_DOME_DROP = 2.15;

// Gap between the finger-hole top rim and the pocket's inner end. v6: 5.5
// (the finger holes sit closer to the pocket than v5's 6.5).
FIT_POCKET_FINGER_GAP = 5.5;

// Seat recess = this x plug thickness: 0.15875 x 20 = 3.175 (1/8").
FIT_RECESS_RATIO_SEAT = 0.15875;
// Pocket-body recess = this x plug thickness: 0.127 x 20 = 2.54 (1/10").
FIT_RECESS_RATIO_BODY = 0.127;
// Thinnest printable pocket floor at 0.2 mm layers.
FIT_MIN_POCKET_FLOOR = 1.5;

// Body envelope ratios — the v6 reference's own proportions (octagon control
// values are PRE-ROUNDING; body_side_rounding turns them into the organic
// outline; see scripts/fit_body_outline_v6.py, silhouette RMS ~0.15 mm).
FIT_BODY_HAND_RATIO     = 81.55 / 85;   // octagon bottom_width / hand width
FIT_BODY_CORNER_RATIO   = 3 / 81.55;    // bottom_corners / bottom_width
FIT_BODY_TOP_RATIO      = 35.75 / 81.55; // top_width / bottom_width
FIT_BODY_MIDDLE_RATIO   = 62.1 / 81.55; // middle_width / bottom_width
FIT_SIDE_CORNER_RATIO   = 5.45 / 65.5;  // side_corner / length
FIT_SIDE_ROUNDING_RATIO = 17.05 / 81.55; // side_rounding / bottom_width
FIT_THICKNESS_HAND_RATIO = 6.35 / 85;   // slab thickness / hand width

// Body top-face roundover: 2.54 = 0.1".
FIT_BODY_TOP_ROUNDING = 2.54;
// Finger-hole rim fillet.
FIT_FINGER_RIM_FILLET = 2.5;

// Hook edge rounding set (stem walls sharp; crossbar corners 1.27 = 0.05").
FIT_T_GAP_SIDE_ROUNDING    = 0;
FIT_T_HOLDER_SIDE_ROUNDING = 1.27;
FIT_T_TOP_BOTTOM_ROUNDING  = 0;

// --- Wing velcro slots (v6) --------------------------------------------------
// The v6 reference replaces v5's 12x7 rectangular slots with curved
// triangular "wing" cutouts that fill the dead space between the finger hole,
// pocket ellipse, side edge, and zip holes (measured: ~10.6 x 14.9 mm, area
// 72.5 mm^2, centroid +/-19.7 / 43.2). The wing region is built from 2D
// offsets of those neighbours; these are the web (keep-out) widths.
FIT_WING_SIDE_INSET  = 4.3;  // inset from the raw body side edge
FIT_WING_FINGER_WEB  = 5.0;  // keep-out ring outside the finger circle
FIT_WING_POCKET_WEB  = 2.5;  // web outside the pocket ellipse footprint
FIT_WING_ZIP_WEB     = 4.0;  // keep-out around each zip hole
FIT_WING_ROUND       = 1.5;  // corner rounding of the wing region

// Classic slot fallback geometry (velcro_style = "Classic slot"): the v4/v5
// 12x7 rectangular slot with its v5 placement margins. The wing style
// derives its own region and ignores these.
FIT_VELCRO_LENGTH = 12;
FIT_VELCRO_WIDTH = 7;
FIT_VELCRO_EDGE_OFFSET = 7.02;
FIT_VELCRO_POCKET_MARGIN = 6.0;  // slot center Y above the pocket end

// ONE-WRAP strap default (widths available: 10/13/16/20/25).
FIT_STRAP_WIDTH = 15;

// Zip-tie constants (measured: 0.2" holes, 0.7" row spacing). v6 adds a
// top-face countersink flare on the exposed (lower-row) holes.
FIT_ZIP_DIAMETER = 5.08;
FIT_ZIP_HEIGHT_SPACING = 17.78;
FIT_ZIP_WIDTH_SPACING = 17.7;
FIT_ZIP_DISTANCE_FROM_NOTCH = 5.1;
FIT_ZIP_COUNTERSINK = 0.9;  // Ø5.1 -> ~Ø6.9 flare at the top face

// Minimum wall between the lower zip-row bore and the finger-hole bore. The
// zip grid hangs from the top edge while the finger holes anchor near the
// cord end, so shallow plugs (short bodies) can pull the grid down into the
// finger holes; D-20 lengthens the body to preserve this web instead.
// Chosen below the Small-size default web (2.87) so every shipped size is
// unchanged at default measurements.
FIT_ZIP_FINGER_WEB = 2.5;

// Size table: hand pair per size (ANSUR II 2012 hand breadth + Rogers 2008
// PIP-joint breadth). Small ~5th %ile female, Medium = calibration anchor
// (~combined 50th %ile), Large ~95th %ile male.
FIT_SIZE_FINGER_S = 16.5;  FIT_SIZE_HAND_S = 72;
FIT_SIZE_FINGER_M = 20;    FIT_SIZE_HAND_M = 85;
FIT_SIZE_FINGER_L = 23;    FIT_SIZE_HAND_L = 96;

function _fit_clamp(v, lo, hi) = max(lo, min(v, hi));
function _fit_round05(v) = floor(v * 20 + 0.5) / 20;
function _fit_round_half(v) = floor(v * 2 + 0.5) / 2;

// ---------------------------------------------------------------------------
// D-1 / D-2 — Size → hand pair
// ---------------------------------------------------------------------------
_fit_finger_width = size == "Small"  ? FIT_SIZE_FINGER_S :
                    size == "Medium" ? FIT_SIZE_FINGER_M :
                    size == "Large"  ? FIT_SIZE_FINGER_L :
                    measure_finger_width;
_fit_hand_width   = size == "Small"  ? FIT_SIZE_HAND_S :
                    size == "Medium" ? FIT_SIZE_HAND_M :
                    size == "Large"  ? FIT_SIZE_HAND_L :
                    measure_hand_width;

// ---------------------------------------------------------------------------
// D-3 … D-8 — Hook family (whole family scales off the cord)
// ---------------------------------------------------------------------------
_fit_t_hook_base_gap      = _fit_clamp(_eff_cord_thickness + FIT_CORD_CLEARANCE, 3, 10); // D-3
_fit_t_hook_length        = _fit_clamp(FIT_T_LENGTH_RATIO   * _fit_t_hook_base_gap, 6, 20); // D-4
_fit_t_hook_holder_width  = _fit_clamp(FIT_T_HOLDER_W_RATIO * _fit_t_hook_base_gap, 8, 25); // D-5
_fit_t_hook_holder_length = _fit_clamp(FIT_T_HOLDER_L_RATIO * _fit_t_hook_base_gap, 2, 15); // D-6
_fit_t_hook_gap_offset    = 0;                                                              // D-7 (const)
_fit_t_hook_leg_offset    = 0;                                                              // D-8 (const)

// ---------------------------------------------------------------------------
// D-9 … D-11 — Finger holes
// ---------------------------------------------------------------------------
_fit_finger_hole_diameter = _fit_clamp(_fit_finger_width + FIT_GRIP_CLEARANCE, 15, 40);     // D-9
_fit_finger_hole_spacing  = _fit_clamp(_fit_finger_hole_diameter + FIT_FINGER_WEB, 20, 50); // D-10
_fit_finger_dx = max(0, _fit_finger_hole_spacing / 2 - _fit_t_hook_holder_width / 2);
_fit_finger_reach = _fit_finger_hole_diameter / 2 + FIT_FINGER_HOOK_CLEARANCE;
_fit_finger_hole_y_position = _fit_round05(
    max(_fit_finger_hole_diameter / 2 + 2,
        _fit_t_hook_length
            + sqrt(max(0, _fit_finger_reach * _fit_finger_reach
                          - _fit_finger_dx * _fit_finger_dx))));

// ---------------------------------------------------------------------------
// D-12 … D-14 — Plug wall notch
// ---------------------------------------------------------------------------
// Notch (and pocket/seat below) size from the WALL-station width — the end
// of the plug that meets the wall is the end the notch must straddle.
_fit_plug_wall_notch_width = _fit_clamp(
    _eff_plug_width_wall + 2 * FIT_SLIDE_CLEARANCE, 5, 40);                              // D-12
_fit_plug_wall_notch_height =                                                               // D-13
    _eff_wall_plate_style == "Rocker / Decora"    ? FIT_WALL_PLATE_DEPTH_DECORA    :
    _eff_wall_plate_style == "Oversized / Jumbo"  ? FIT_WALL_PLATE_DEPTH_OVERSIZED :
    _eff_wall_plate_style == "No plate / flush"   ? FIT_WALL_PLATE_DEPTH_NONE      :
    FIT_WALL_PLATE_DEPTH_STANDARD;
_fit_plug_wall_notch_rounding = min(FIT_NOTCH_ROUNDING,                                     // D-14
    _fit_plug_wall_notch_height, _fit_plug_wall_notch_width / 4);

// ---------------------------------------------------------------------------
// D-15 … D-18 — Dome pocket (seat disc + plug-body ellipse)
// ---------------------------------------------------------------------------
_fit_pocket_seat_diameter = _fit_clamp(
    _fit_plug_wall_notch_width + FIT_SEAT_BEYOND_NOTCH, 10, 45);                            // D-15
_fit_pocket_width = _fit_clamp(
    _eff_plug_width_wall + FIT_POCKET_WIDTH_CLEARANCE, 10, 45);                          // D-16
_fit_pocket_dome_drop = min(FIT_DOME_DROP, 0.25 * _eff_plug_length);                     // D-17
// D-43 — Plug side taper (also the plug side rail angle). The angle is
// DERIVED from the two Step 1 width stations over the plug length (in the
// main SCAD), so its sign encodes which end of the plug is wider: positive
// narrows toward the cord, negative widens toward it. Clamped to the rail
// math's safe window. 0 at Medium defaults (equal stations — parity).
_fit_pocket_side_angle = _fit_clamp(_eff_plug_side_angle, -15, 25);                      // D-43

// ---------------------------------------------------------------------------
// D-19 / D-20 — Pocket depth and body length (two-pass)
// ---------------------------------------------------------------------------
// The pocket runs the FULL plug length whenever the 120 mm body ceiling
// allows: the only cap is the real budget left after the cord-end features
// (finger holes + the pocket/finger gap) claim their run. At Medium
// defaults the budget is ~80 mm, so a 60-85 mm plug still gets a
// full-length pocket (the old rule capped it at half the body).
_fit_pocket_depth_max = 120 - (FIT_POCKET_FINGER_GAP                                     // D-19a (internal)
    + _fit_finger_hole_y_position + _fit_finger_hole_diameter / 2);
_fit_pocket_depth = _fit_clamp(_eff_plug_length, 12, _fit_pocket_depth_max);             // D-19b
// Zip-grid floor: the body must also be long enough that the lower zip row
// keeps a FIT_ZIP_FINGER_WEB wall from the nearest finger bore. dy_req is the
// vertical center distance that yields that wall given the fixed lateral
// offset between the zip column and the finger-hole center.
_fit_zip_finger_dx = abs(_fit_finger_hole_spacing / 2 - FIT_ZIP_WIDTH_SPACING / 2);
_fit_zip_finger_rr = _fit_finger_hole_diameter / 2 + FIT_ZIP_DIAMETER / 2
    + FIT_ZIP_FINGER_WEB;
_fit_zip_dy_req = sqrt(max(0,
    _fit_zip_finger_rr * _fit_zip_finger_rr
        - _fit_zip_finger_dx * _fit_zip_finger_dx));
_fit_length_for_zip = _fit_finger_hole_y_position + _fit_zip_dy_req                      // D-20a (internal)
    + FIT_ZIP_HEIGHT_SPACING + FIT_ZIP_DISTANCE_FROM_NOTCH
    + _fit_plug_wall_notch_height;
_fit_puller_length = _fit_clamp(                                                            // D-20
    max(_fit_pocket_depth + FIT_POCKET_FINGER_GAP
            + _fit_finger_hole_y_position + _fit_finger_hole_diameter / 2,
        _fit_length_for_zip),
    55, 120);

// ---------------------------------------------------------------------------
// D-21 — Slab thickness
// ---------------------------------------------------------------------------
_fit_body_thickness = _fit_round05(
    _fit_clamp(FIT_THICKNESS_HAND_RATIO * _fit_hand_width, 5, 9));                          // D-21

// ---------------------------------------------------------------------------
// D-22 / D-23 — Pocket floor heights (seat + body recesses)
// ---------------------------------------------------------------------------
_fit_seat_floor = _fit_body_thickness                                                       // D-22
    - _fit_clamp(FIT_RECESS_RATIO_SEAT * _eff_plug_thickness,
                 2, _fit_body_thickness - FIT_MIN_POCKET_FLOOR);
_fit_body_floor = _fit_body_thickness                                                       // D-23
    - _fit_clamp(FIT_RECESS_RATIO_BODY * _eff_plug_thickness,
                 1, _fit_body_thickness - FIT_MIN_POCKET_FLOOR);

// ---------------------------------------------------------------------------
// D-28 … D-33 — Body envelope (octagon control points, pre-rounding)
// ---------------------------------------------------------------------------
_fit_puller_bottom_width = _fit_round05(
    _fit_clamp(FIT_BODY_HAND_RATIO * _fit_hand_width, 50, 120));                            // D-28
_fit_puller_top_width = _fit_round05(_fit_clamp(                                            // D-29
    max(FIT_BODY_TOP_RATIO * _fit_puller_bottom_width,
        _fit_pocket_seat_diameter),
    25, 80));
_fit_puller_bottom_corners = _fit_round05(
    _fit_clamp(FIT_BODY_CORNER_RATIO * _fit_puller_bottom_width, 3, 80));                   // D-30
_fit_puller_middle_width = _fit_round05(_fit_clamp(                                         // D-31
    max(FIT_BODY_MIDDLE_RATIO * _fit_puller_bottom_width,
        _fit_puller_top_width + 4),
    25, 120));
_fit_puller_side_corner = _fit_round05(
    _fit_clamp(FIT_SIDE_CORNER_RATIO * _fit_puller_length, 3, 35));                         // D-32
_fit_body_side_rounding = _fit_round05(
    _fit_clamp(FIT_SIDE_ROUNDING_RATIO * _fit_puller_bottom_width, 0, 30));                 // D-33

// ---------------------------------------------------------------------------
// D-34 … D-36 — Velcro / wing placement (optional attachment)
// ---------------------------------------------------------------------------
_fit_middle_y = (_fit_puller_side_corner + _fit_puller_length) / 2;
function _fit_hw_at(y) =
    (y <= _fit_puller_side_corner)
        ? _fit_puller_bottom_corners / 2
          + (_fit_puller_bottom_width / 2 - _fit_puller_bottom_corners / 2)
            * y / _fit_puller_side_corner
        : (y <= _fit_middle_y)
            ? _fit_puller_bottom_width / 2
              + (_fit_puller_middle_width / 2 - _fit_puller_bottom_width / 2)
                * (y - _fit_puller_side_corner)
                / (_fit_middle_y - _fit_puller_side_corner)
            : _fit_puller_middle_width / 2
              + (_fit_puller_top_width / 2 - _fit_puller_middle_width / 2)
                * (y - _fit_middle_y)
                / (_fit_puller_length - _fit_middle_y);

_fit_velcro_hole_y_center = _fit_round05(                                                   // D-34
    _fit_puller_length - _fit_pocket_depth + FIT_VELCRO_POCKET_MARGIN);
_fit_side_edge_angle = atan2(
    _fit_puller_length - _fit_middle_y,
    _fit_puller_top_width / 2 - _fit_puller_middle_width / 2);
_fit_velcro_hole_rotation = _fit_round_half(_fit_side_edge_angle - 90);                     // D-35
_fit_velcro_hole_x_center = _fit_round05(
    _fit_hw_at(_fit_velcro_hole_y_center) - FIT_VELCRO_EDGE_OFFSET);                        // D-36

// ---------------------------------------------------------------------------
// D-37 … D-40 — J-hook cord catch (v6)
// ---------------------------------------------------------------------------
// The stem offset and catch reach scale with the crossbar so the catch stays
// proportional across cord sizes; the tip drop is a fixed sag.
_fit_hook_stem_offset = _fit_round05(                                                       // D-37
    FIT_HOOK_STEM_OFFSET * _fit_t_hook_base_gap / 4.7625);
_fit_hook_catch_reach = _fit_round05(                                                       // D-38
    FIT_HOOK_CATCH_REACH * _fit_t_hook_holder_width / 11.1125);
_fit_hook_tip_drop = FIT_HOOK_TIP_DROP;                                                     // D-39
_fit_zip_countersink = FIT_ZIP_COUNTERSINK;                                                 // D-40 (const)

// ---------------------------------------------------------------------------
// D-41 … D-42 — Wing velcro / strap width (v6)
// ---------------------------------------------------------------------------
_fit_strap_width = FIT_STRAP_WIDTH;                                                         // D-41
_fit_velcro_hole_length = FIT_VELCRO_LENGTH;                                                // D-42a (const)
_fit_velcro_hole_width  = FIT_VELCRO_WIDTH;                                                 // D-42b (const)

// ---------------------------------------------------------------------------
// FIT_MEASURED lookup table
// ---------------------------------------------------------------------------
// Same key set as PRESET_MEDIUM (enforced by the key-parity test).
FIT_MEASURED = [
    // -- Body Shape --
    ["puller_length",                    _fit_puller_length],
    ["puller_bottom_width",              _fit_puller_bottom_width],
    ["puller_bottom_corners",            _fit_puller_bottom_corners],
    ["puller_top_width",                 _fit_puller_top_width],
    ["puller_middle_width",              _fit_puller_middle_width],
    ["puller_side_corner",               _fit_puller_side_corner],
    ["body_thickness",                   _fit_body_thickness],
    ["body_round_bottom_only",           true],

    // -- Plug Pocket (dome) --
    ["pocket_seat_diameter",             _fit_pocket_seat_diameter],
    ["pocket_width",                     _fit_pocket_width],
    ["pocket_depth",                     _fit_pocket_depth],
    ["pocket_dome_drop",                 _fit_pocket_dome_drop],
    ["pocket_seat_floor",                _fit_seat_floor],
    ["pocket_floor",                     _fit_body_floor],
    ["pocket_side_angle",                _fit_pocket_side_angle],

    // -- Finger Holes --
    ["enable_finger_holes",              true],
    ["finger_hole_diameter",             _fit_finger_hole_diameter],
    ["finger_hole_spacing",              _fit_finger_hole_spacing],
    ["finger_hole_y_position",           _fit_finger_hole_y_position],

    // -- Hook (J-hook cord catch) --
    ["enable_t_hook",                    true],
    ["t_hook_base_gap",                  _fit_t_hook_base_gap],
    ["t_hook_length",                    _fit_t_hook_length],
    ["t_hook_holder_width",              _fit_t_hook_holder_width],
    ["t_hook_holder_length",             _fit_t_hook_holder_length],
    ["t_hook_gap_offset",                _fit_t_hook_gap_offset],
    ["t_hook_leg_offset",                _fit_t_hook_leg_offset],
    ["t_hook_stem_offset",               _fit_hook_stem_offset],
    ["t_hook_catch_reach",               _fit_hook_catch_reach],
    ["t_hook_tip_drop",                  _fit_hook_tip_drop],

    // -- Plug Wall Notch --
    ["enable_plug_wall_notch",           true],
    ["plug_wall_notch_width",            _fit_plug_wall_notch_width],
    ["plug_wall_notch_height",           _fit_plug_wall_notch_height],
    ["plug_wall_notch_rounding",         _fit_plug_wall_notch_rounding],

    // -- Zip Tie Holes (enable comes from the `attachment` dropdown) --
    ["zip_tie_hole_diameter",            FIT_ZIP_DIAMETER],
    ["zip_tie_height_spacing",           FIT_ZIP_HEIGHT_SPACING],
    ["zip_tie_width_spacing",            FIT_ZIP_WIDTH_SPACING],
    ["zip_tie_distance_from_notch",      FIT_ZIP_DISTANCE_FROM_NOTCH],
    ["zip_tie_countersink",              _fit_zip_countersink],

    // -- Velcro / Wing Strap (enable/style/width come from Step 3 dropdowns) --
    ["velcro_hole_length",               _fit_velcro_hole_length],
    ["velcro_hole_width",                _fit_velcro_hole_width],
    ["velcro_hole_x_center",             _fit_velcro_hole_x_center],
    ["velcro_hole_y_center",             _fit_velcro_hole_y_center],
    ["velcro_hole_rotation",             _fit_velcro_hole_rotation],

    // -- Edge Rounding --
    ["body_side_rounding",               _fit_body_side_rounding],
    ["body_top_rounding",                FIT_BODY_TOP_ROUNDING],
    ["body_bottom_rounding",             0],
    ["velcro_side_rounding",             0],
    ["velcro_top_bottom_rounding",       0],
    ["finger_hole_rounding",             FIT_FINGER_RIM_FILLET],
    ["t_hook_holder_side_rounding",      FIT_T_HOLDER_SIDE_ROUNDING],
    ["t_hook_gap_side_rounding",         FIT_T_GAP_SIDE_ROUNDING],
    ["t_hook_top_bottom_rounding",       FIT_T_TOP_BOTTOM_ROUNDING],
];

// ---------------------------------------------------------------------------
// Diagnostics — machine-parseable derivation echo
// ---------------------------------------------------------------------------
if (size != "Custom") {
    echo(str("=== Derived values for size '", size, "' (mm) ==="));
    for (row = FIT_MEASURED)
        echo(str("fit_derived: ", row[0], "=", row[1]));
}
