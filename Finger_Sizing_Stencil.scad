// =============================================================================
// Finger_Sizing_Stencil.scad — printable finger-sizing stencil
// =============================================================================
//
// A thin plate with the 18 finger-sizing circles (Ø15–Ø32 mm) from
// docs/guides/measuring-template.svg as real through-holes — the no-scissors
// alternative to cutting out the paper circles. Find the smallest hole your
// middle finger passes through comfortably; your finger width for the
// Customizer (`measure_finger_width`) is that hole's number minus 5.
//
// Printing: lies flat, no supports. PETG or PLA, 0.2 mm layers. At the
// default 1.2 mm thickness it prints in minutes. The full plate is about
// 157 x 156 mm; set `split_halves = true` for two smaller plates
// (about 157 x 80 and 145 x 96 mm) if your bed is tight.
//
// License: PolyForm Noncommercial 1.0.0

/* [Stencil] */
// Plate thickness. 1.2 mm is stiff enough and prints fast; go thicker if you want a sturdier gauge. (mm)
stencil_thickness = 1.2; // [0.6:0.2:3]
// Print the stencil as two smaller plates (rows Ø15–25 and Ø26–32) instead of one large plate, for beds smaller than ~170 x 160 mm.
split_halves = false;
// Corner rounding of the plate outline. (mm)
corner_radius = 6; // [0:0.5:12]
// How deep the labels are pressed into the top face. Must stay below the plate thickness. (mm)
deboss_depth = 0.6; // [0.2:0.1:1]
// How many segments make up each circle. 64 is print-ready. Higher = smoother but slower.
quality = 64; // [24:8:128]

/* [Hidden] */
eps = 0.01;

// The 18 gauge holes, grouped into rows exactly like the paper template.
ROWS_A = [[15, 16, 17, 18, 19, 20], [21, 22, 23, 24, 25]];
ROWS_B = [[26, 27, 28, 29], [30, 31, 32]];

edge_margin  = 7;    // hole edge -> plate edge
hole_gap     = 7;    // hole edge -> neighbouring hole edge
label_height = 4.5;  // text band above each hole row
row_gap      = 3;    // row bottom -> next label band
title_band   = 16;   // title + rule strip at the top of a plate
label_size   = 4;
title_size   = 5;
rule_size    = 3.2;
FONT_BOLD    = "Liberation Sans:style=Bold";
FONT         = "Liberation Sans";

_deboss = min(deboss_depth, stencil_thickness - 0.4);

function row_width(row) =
    2 * edge_margin
    + (len(row) - 1) * hole_gap
    + sum_list([for (d = row) d]);

function sum_list(v, i = 0) = i >= len(v) ? 0 : v[i] + sum_list(v, i + 1);

function rows_width(rows) = max([for (r = rows) row_width(r)]);

// Y of a row's hole centers, measured down from the plate top edge.
function row_center_y(rows, i) =
    title_band
    + sum_list([for (j = [0 : i]) label_height + rows[j][len(rows[j]) - 1] / 2])
    + sum_list([for (j = [0 : i]) j < i ? rows[j][len(rows[j]) - 1] / 2 + row_gap : 0]);

function plate_height(rows) =
    let (n = len(rows) - 1)
    row_center_y(rows, n) + rows[n][len(rows[n]) - 1] / 2 + edge_margin;

// One stencil plate. rows = list of hole-diameter rows; title/rule strings
// are debossed along the top band ("" = skip).
module stencil_plate(rows, title_str, rule_str) {
    w = rows_width(rows);
    h = plate_height(rows);

    difference() {
        // Plate body with rounded corners.
        linear_extrude(height = stencil_thickness)
            offset(r = corner_radius) offset(delta = -corner_radius)
                square([w, h]);

        // Through-holes, centered rows.
        for (i = [0 : len(rows) - 1]) {
            row = rows[i];
            rw  = row_width(row);
            cy  = plate_height(rows) - row_center_y(rows, i);
            for (k = [0 : len(row) - 1]) {
                d  = row[k];
                cx = (w - rw) / 2 + edge_margin
                     + sum_list([for (m = [0 : k]) m < k ? row[m] + hole_gap : 0])
                     + d / 2;
                translate([cx, cy, -eps])
                    cylinder(d = d, h = stencil_thickness + 2 * eps, $fn = quality);
                // Debossed diameter label above the hole.
                translate([cx, cy + d / 2 + 1.2, stencil_thickness - _deboss])
                    linear_extrude(height = _deboss + eps)
                        text(str(d), size = label_size, font = FONT_BOLD,
                             halign = "center", valign = "baseline");
            }
        }

        // Title with the sizing rule stacked under it in the top band.
        if (title_str != "")
            translate([edge_margin, h - 3 - title_size, stencil_thickness - _deboss])
                linear_extrude(height = _deboss + eps)
                    text(title_str, size = title_size, font = FONT_BOLD,
                         halign = "left", valign = "baseline");
        if (rule_str != "")
            translate([edge_margin, h - 5.5 - title_size - rule_size,
                       stencil_thickness - _deboss])
                linear_extrude(height = _deboss + eps)
                    text(rule_str, size = rule_size, font = FONT,
                         halign = "left", valign = "baseline");
    }
}

RULE_TEXT = "FINGER WIDTH = HOLE No. - 5";

if (split_halves) {
    stencil_plate(ROWS_A, "FINGER SIZING 1/2", RULE_TEXT);
    translate([0, -plate_height(ROWS_B) - 10])
        stencil_plate(ROWS_B, "FINGER SIZING 2/2", RULE_TEXT);
} else {
    stencil_plate(concat(ROWS_A, ROWS_B), "PLUG PULLER FINGER SIZING", RULE_TEXT);
}
