// =============================================================================
// fit_sizes.scad — size table and finger clearance shared by both tool files
// =============================================================================
//
// The Small / Medium / Large hand pairs and the finger-hole clearance, kept in
// one small file so the two-sided puller can use them without including the
// one-sided puller's derivation layer.
//
// Include order: every main file includes this file FIRST (before
// fit_measured.scad), because OpenSCAD evaluates top-level assignments in
// source order and the derivations read these constants.
//
// Keep tests/fit_formulas.py (FIT_SIZE_TABLE, FIT_GRIP_CLEARANCE) in sync.
//
// License: PolyForm Noncommercial 1.0.0

/* [Hidden] */

// Finger-hole bore = knuckle width + this. Reference: 1" bore (25.4) for the
// designer's 20 mm finger -> +5.4. Also absorbs FDM hole undersizing.
FIT_GRIP_CLEARANCE = 5.4;

// Size table: hand pair per size (ANSUR II 2012 hand breadth + Rogers 2008
// PIP-joint breadth). Small ~5th %ile female, Medium = calibration anchor
// (~combined 50th %ile), Large ~95th %ile male.
FIT_SIZE_FINGER_S = 16.5;  FIT_SIZE_HAND_S = 72;
FIT_SIZE_FINGER_M = 20;    FIT_SIZE_HAND_M = 85;
FIT_SIZE_FINGER_L = 23;    FIT_SIZE_HAND_L = 96;
