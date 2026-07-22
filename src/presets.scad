// =============================================================================
// presets.scad — Plug Puller v6 preset table and lookup helper
// =============================================================================
//
// This file is `include`d by Plug_Puller_v6_Parametric.scad. It defines:
//
//   - PRESET_MEDIUM       : the calibration reference table. Its values are
//                           the measured dimensions of the authoritative v6.0
//                           CAD reference ("Plug Puller 3.1 - B",
//                           `v6.0/CAD/v6.0.stl`, extracted by
//                           scripts/extract_reference_dims.py +
//                           scripts/analyze_v6*.py). The Medium size IS the
//                           v6 Plug Puller.
//   - preset_lookup(...)  : low-level table lookup; returns undef on miss.
//   - preset_value(p, key, fallback)
//                         : public routing helper used by the main SCAD.
//
// MEDIUM-PARITY INVARIANT
// -----------------------
// With `size = "Medium"` and every `measure_*` input at its default, every
// FIT_MEASURED value equals PRESET_MEDIUM's value exactly, and both equal the
// measured v6 reference geometry. Pinned at three levels: tests/fit_formulas.py
// (pure-Python mirror), the derivation echo parity test, and the mesh-level
// reference-parity test (tests/test_reference_parity.py).
//
// Include-order dependency
// ------------------------
// `preset_value()` references FIT_MEASURED, built by fit_measured.scad. The
// main SCAD must `include <fit_measured.scad>` BEFORE `include <presets.scad>`.
//
// Key-naming convention
// ---------------------
// Keys match the public variable names in the main file. Keep the key set
// identical between PRESET_MEDIUM and FIT_MEASURED (enforced by
// tests/test_preset_routing.py).
//
// License: PolyForm Noncommercial 1.0.0

/* [Hidden] */

// ----------- "Medium" reference table (the v6 Plug Puller) -----------
// Sources: v6.0/reference_dims.json (measured mesh), v6.0/outline_fit.json
// (octagon + rounding fit, silhouette RMS ~0.15 mm), and
// scripts/analyze_v6_features.py (seat/pocket/wing/J-hook).
PRESET_MEDIUM = [
    // -- Body Shape (octagon control points; the rendered outline applies
    //    body_side_rounding below puller_middle_y) --
    ["puller_length",                    65.5],
    ["puller_bottom_width",              81.55],
    ["puller_bottom_corners",            3],
    ["puller_top_width",                 35.75],
    ["puller_middle_width",              62.1],
    ["puller_side_corner",               5.45],
    ["body_thickness",                   6.35],
    ["body_round_bottom_only",           true],

    // -- Plug Pocket (dome style: seat disc + body ellipse) --
    ["pocket_seat_diameter",             30.5],
    ["pocket_width",                     31.7],
    ["pocket_depth",                     25.5],
    ["pocket_dome_drop",                 2.15],
    ["pocket_seat_floor",                3.175],
    ["pocket_floor",                     3.81],
    ["pocket_side_angle",                0],

    // -- Finger Holes --
    ["enable_finger_holes",              true],
    ["finger_hole_diameter",             25.4],
    ["finger_hole_spacing",              33],
    ["finger_hole_y_position",           21.8],

    // -- Hook (J-hook cord catch) --
    ["enable_t_hook",                    true],
    ["t_hook_base_gap",                  4.7625],
    ["t_hook_length",                    10.16],
    ["t_hook_holder_width",              11.1125],
    ["t_hook_holder_length",             5.08],
    ["t_hook_gap_offset",                0],
    ["t_hook_leg_offset",                0],
    ["t_hook_stem_offset",               4.5],
    ["t_hook_catch_reach",               4.55],
    ["t_hook_tip_drop",                  1.98],

    // -- Plug Wall Notch --
    ["enable_plug_wall_notch",           true],
    ["plug_wall_notch_width",            26.67],
    ["plug_wall_notch_height",           3.81],
    ["plug_wall_notch_rounding",         2.54],

    // -- Zip Tie Holes (enable comes from the `attachment` dropdown) --
    ["zip_tie_hole_diameter",            5.08],
    ["zip_tie_height_spacing",           17.78],
    ["zip_tie_width_spacing",            17.7],
    ["zip_tie_distance_from_notch",      5.1],
    ["zip_tie_countersink",              0.9],

    // -- Velcro / Wing Strap (enable/style/width come from Step 3 dropdowns;
    //    the hole_length/width/x/y values size and place the Classic-slot
    //    fallback only — the wing derives its own region) --
    ["velcro_hole_length",               12],
    ["velcro_hole_width",                7],
    ["velcro_hole_x_center",             19.4],
    ["velcro_hole_y_center",             46],
    ["velcro_hole_rotation",             23.5],

    // -- Edge Rounding --
    ["body_side_rounding",               17.05],
    ["body_top_rounding",                2.54],
    ["body_bottom_rounding",             0],
    ["velcro_side_rounding",             0],
    ["velcro_top_bottom_rounding",       0],
    ["finger_hole_rounding",             2.5],
    ["t_hook_holder_side_rounding",      1.27],
    ["t_hook_gap_side_rounding",         0],
    ["t_hook_top_bottom_rounding",       0],
];

// Low-level table lookup. Returns the value for `key` in `preset_list`, or
// `undef` if not found. See the v5 notes on OpenSCAD's search() quirks: we
// wrap the key in a one-element vector and discriminate hit-vs-miss with
// is_num(m[0]) (a hit is the row index; a miss is the empty list []).
function preset_lookup(preset_list, key) =
    let (m = search([key], preset_list))
    is_num(m[0]) ? preset_list[m[0]][1] : undef;

// Public routing helper. `p` is the resolved size name from the main SCAD:
//   "Custom"          -> fallback (the user's `custom_*` slider),
//   "Medium Defaults" -> the static PRESET_MEDIUM table,
//   anything else     -> FIT_MEASURED (Small / Medium / Large / Measure my
//                        hand, all measurement-driven).
function preset_value(p, key, fallback) =
    let (val =
        p == "Custom"          ? undef :
        p == "Medium Defaults" ? preset_lookup(PRESET_MEDIUM, key) :
        preset_lookup(FIT_MEASURED, key))
    val == undef ? fallback : val;
