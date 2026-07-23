// =============================================================================
// Measuring_Stencil.scad — printable measuring stencil (supersedes the old
// Finger_Sizing_Stencil.scad)
// =============================================================================
//
// A set of thin measuring cards that answer the Plug Puller worksheet without
// a caliper. Each card carries a raised 2-character ID you can read by touch;
// the legend lives in docs/guides/starter-guide.md:
//
//   P1 / P2 / P3  plug preset cards — hold your plug in the cutouts; if it
//                 fills the W (width) and T (thickness) openings and the cord
//                 passes the round hole, that preset fits — pick it in Step 1
//                 and skip measuring entirely.
//                   P1 = flat 2-prong lamp plug (NEMA 1-15)
//                   P2 = standard 3-prong plug (NEMA 5-15)
//                   P3 = heavy-duty extension cord (NEMA 5-15)
//   R1            ruler card — raised tactile ticks (1 mm short, 5 mm medium,
//                 10 mm tall), debossed numerals, and touch-countable edge
//                 notches every 10 mm (worksheet measurements 1-5).
//   C1            cord gauge — through-holes 3-9 mm (worksheet measurement 6).
//   F1 / F2       finger sizing — the 18 gauge holes; smallest comfortable
//                 hole minus 5 = your finger width (worksheet measurement 8).
//
// Printing: all cards lie flat, no supports. PETG or PLA, 0.2 mm layers. At
// the default 1.2 mm thickness the full set prints fast. Small printer? Set
// `bed_width` / `bed_depth` to your bed and the cards pack themselves onto
// numbered sheets — render `part_index` = 1, 2, ... to export one sheet at a
// time (0 previews every sheet at once).
//
// License: PolyForm Noncommercial 1.0.0

/* [Stencil] */
// Plate thickness of every card. 1.2 mm is stiff enough and prints fast; go thicker for a sturdier gauge. (mm)
stencil_thickness = 1.2; // [0.6:0.2:3]
// Corner rounding of each card outline. (mm)
corner_radius = 3; // [0:0.5:8]
// How deep the labels are pressed into the top face. Must stay below the plate thickness. (mm)
deboss_depth = 0.6; // [0.2:0.1:1]
// How many segments make up each circle. 64 is print-ready. Higher = smoother but slower.
quality = 64; // [24:8:128]

/* [Card IDs] */
// Raised ID text height on every card. (mm)
id_text_size = 5; // [3:0.5:8]
// How far the ID letters stand proud of the top face, so they read by touch. (mm)
id_emboss_height = 0.8; // [0.5:0.1:1]
// ID embossed on the lamp plug card - max 2 characters
p1_id = "P1";
// ID embossed on the standard 3-prong plug card - max 2 characters
p2_id = "P2";
// ID embossed on the heavy-duty plug card - max 2 characters
p3_id = "P3";
// ID embossed on the ruler card - max 2 characters
r1_id = "R1";
// ID embossed on the cord gauge card - max 2 characters
c1_id = "C1";
// ID embossed on the first finger-sizing card - max 2 characters
f1_id = "F1";
// ID embossed on the second finger-sizing card - max 2 characters
f2_id = "F2";

/* [Print Bed] */
// Usable width of your print bed. Cards are packed onto sheets no bigger than this. (mm)
bed_width = 200; // [80:5:400]
// Usable depth of your print bed. (mm)
bed_depth = 200; // [80:5:400]
// Which sheet to render. 0 = preview every sheet at once, separated by 15 mm; 1-9 = render only that sheet for export.
part_index = 0; // [0:1:9]

/* [Hidden] */
eps = 0.01;

// ── Preset plug dimensions ──────────────────────────────────────────────────
// [id, length, width wall, width cable, thickness wall, thickness cable, cord]
// Copied from the `_eff_*` preset ternaries in src/Plug_Puller_Parametric.scad
// (lamp, standard 3-prong, heavy-duty — the Step 1 dropdown order).
// tests/test_stencil_data.py asserts these numbers match the main SCAD and
// scripts/generate_stencil_sheet.py — keep all three in lock-step.
PLUG_PRESET_DIMS = [
    ["P1", 37.0, 25.0, 11.2, 18.6, 8.6, 3.6],
    ["P2", 46.2, 26.6, 13.4, 18.9, 15.0, 7.0],
    ["P3", 43.8, 25.8, 21.9, 27.0, 27.0, 8.2],
];
PLUG_PRESET_NAMES = [
    "LAMP 2-PRONG NEMA 1-15",
    "STANDARD 3-PRONG NEMA 5-15",
    "HEAVY-DUTY CORD NEMA 5-15",
];

// The 18 finger gauge holes, grouped into rows exactly like the paper
// template (docs/guides/measuring-template.svg).
F1_ROWS = [[15, 16, 17, 18, 19, 20], [21, 22, 23, 24, 25]];
F2_ROWS = [[26, 27, 28, 29], [30, 31, 32]];
FINGER_RULE_TEXT = "FINGER WIDTH = HOLE No. - 5";

// Cord gauge hole diameters (worksheet measurement 6).
CORD_GAUGE_DIAS = [3, 4, 5, 6, 7, 8, 9];

FONT_BOLD = "Liberation Sans:style=Bold";
FONT      = "Liberation Sans";

_deboss = min(deboss_depth, stencil_thickness - 0.4);

// ── Shared layout constants ─────────────────────────────────────────────────
CARD_GAP     = 5;    // card-to-card gap on a sheet
CARD_MARGIN  = 6;    // cutout edge -> card edge
P_WEB        = 8;    // web between the two plug silhouettes
P_NAME_BAND  = 6;    // preset name strip along a plug card's bottom
P_CAPT_BAND  = 6;    // W / T caption strip under the silhouettes
RULER_LEN    = 100;
RULER_H      = 22;
// Finger-card bands (inherited from the proven finger stencil layout).
F_EDGE       = 7;    // hole edge -> card edge
F_HOLE_GAP   = 7;    // hole edge -> neighbouring hole edge
F_LABEL_H    = 4.5;  // text band above each hole row
F_ROW_GAP    = 3;    // row bottom -> next label band
F_TITLE_BAND = 16;   // ID + title + rule strip at the top
F_LABEL_SIZE = 4;
F_TITLE_SIZE = 5;
F_RULE_SIZE  = 3.2;

function sum_list(v, i = 0) = i >= len(v) ? 0 : v[i] + sum_list(v, i + 1);

// ── Card size functions (consumed by the sheet packer) ──────────────────────
function _p_dims(i) = PLUG_PRESET_DIMS[i];
function _p_wmax(i) = max(_p_dims(i)[2], _p_dims(i)[3]);
function _p_tmax(i) = max(_p_dims(i)[4], _p_dims(i)[5]);
function _p_card_w(i) =
    2 * CARD_MARGIN + _p_wmax(i) + P_WEB + _p_tmax(i) + P_WEB + _p_dims(i)[6];
function _p_card_h(i) =
    4 + P_NAME_BAND + P_CAPT_BAND + _p_dims(i)[1] + 3 + id_text_size + 3;

function _c1_card_w() =
    2 * CARD_MARGIN
    + sum_list(CORD_GAUGE_DIAS)
    + (len(CORD_GAUGE_DIAS) - 1) * 6;
function _c1_card_h() =
    CARD_MARGIN + max(CORD_GAUGE_DIAS) + 1.2 + F_LABEL_SIZE + 2.8
    + id_text_size + 3;

function _f_row_w(row) =
    2 * F_EDGE + (len(row) - 1) * F_HOLE_GAP + sum_list([for (d = row) d]);
function _f_card_w(rows) = max([for (r = rows) _f_row_w(r)]);
// Y of a row's hole centers, measured down from the card top edge.
function _f_row_center_y(rows, i) =
    F_TITLE_BAND
    + sum_list([for (j = [0 : i]) F_LABEL_H + rows[j][len(rows[j]) - 1] / 2])
    + sum_list([for (j = [0 : i])
                    j < i ? rows[j][len(rows[j]) - 1] / 2 + F_ROW_GAP : 0]);
function _f_card_h(rows) =
    let (n = len(rows) - 1)
    _f_row_center_y(rows, n) + rows[n][len(rows[n]) - 1] / 2 + F_EDGE;

// Fixed card list: index -> [user-facing id, width, height].
CARD_IDS = [p1_id, p2_id, p3_id, r1_id, c1_id, f1_id, f2_id];
function card_size(i) =
    i <= 2 ? [_p_card_w(i), _p_card_h(i)] :
    i == 3 ? [RULER_LEN, RULER_H] :
    i == 4 ? [_c1_card_w(), _c1_card_h()] :
    i == 5 ? [_f_card_w(F1_ROWS), _f_card_h(F1_ROWS)] :
             [_f_card_w(F2_ROWS), _f_card_h(F2_ROWS)];
N_CARDS = len(CARD_IDS);

// ── Shared building blocks ───────────────────────────────────────────────────
module card_blank(w, h) {
    r = min(corner_radius, w / 4, h / 4);
    linear_extrude(height = stencil_thickness)
        offset(r = r) offset(delta = -r)
            square([w, h]);
}

// Debossed text (subtract inside a difference()).
module deboss_text(t, size, font = FONT_BOLD, halign = "left") {
    translate([0, 0, stencil_thickness - _deboss])
        linear_extrude(height = _deboss + eps)
            text(t, size = size, font = font,
                 halign = halign, valign = "baseline");
}

// Raised, touch-readable card ID (union on the top face).
module raised_id(t) {
    translate([0, 0, stencil_thickness - eps])
        linear_extrude(height = id_emboss_height + eps)
            text(t, size = id_text_size, font = FONT_BOLD,
                 halign = "left", valign = "baseline");
}

// Rounded-corner plug silhouette: isoceles trapezoid, `base` wide at the
// bottom (wall end), `top` wide at the top (cord end), `h` tall.
module plug_trap_2d(base, top, h) {
    offset(r = 1) offset(delta = -1)
        polygon([[-base / 2, 0], [base / 2, 0], [top / 2, h], [-top / 2, h]]);
}

// ── P1 / P2 / P3: plug preset silhouette cards ───────────────────────────────
// Two through-cutouts side by side — the width view (W) and the thickness
// view (T) — plus a cord-diameter hole. Hold the plug in/behind a cutout: if
// it fills the opening, this preset fits (no ruler needed).
module plug_card(i) {
    d      = _p_dims(i);
    w      = _p_card_w(i);
    h      = _p_card_h(i);
    y_sil  = 4 + P_NAME_BAND + P_CAPT_BAND;     // silhouette bottom edge
    x_w    = CARD_MARGIN + _p_wmax(i) / 2;
    x_t    = CARD_MARGIN + _p_wmax(i) + P_WEB + _p_tmax(i) / 2;
    x_c    = CARD_MARGIN + _p_wmax(i) + P_WEB + _p_tmax(i) + P_WEB + d[6] / 2;

    difference() {
        union() {
            card_blank(w, h);
            translate([CARD_MARGIN, h - 3 - id_text_size])
                raised_id(CARD_IDS[i]);
        }
        // Width view: width_wall at the base, width_cable at the top.
        translate([x_w, y_sil, -eps])
            linear_extrude(height = stencil_thickness + 2 * eps)
                plug_trap_2d(d[2], d[3], d[1]);
        // Thickness view: the two thickness stations.
        translate([x_t, y_sil, -eps])
            linear_extrude(height = stencil_thickness + 2 * eps)
                plug_trap_2d(d[4], d[5], d[1]);
        // Cord hole, bottom-aligned with the silhouettes.
        translate([x_c, y_sil + d[6] / 2, -eps])
            cylinder(d = d[6], h = stencil_thickness + 2 * eps, $fn = quality);
        // Captions under the three openings.
        translate([x_w, 4 + P_NAME_BAND]) deboss_text("W", 4, halign = "center");
        translate([x_t, 4 + P_NAME_BAND]) deboss_text("T", 4, halign = "center");
        translate([x_c, 4 + P_NAME_BAND])
            deboss_text(str(d[6]), 3.2, halign = "center");
        // Preset name along the bottom.
        translate([CARD_MARGIN, 4])
            deboss_text(PLUG_PRESET_NAMES[i], 3.2, font = FONT);
    }
}

// ── R1: tactile ruler card ───────────────────────────────────────────────────
// 100 x 22 mm strip. Raised ticks (short = 1 mm, medium = 5 mm, tall =
// 10 mm), debossed numerals every 10 mm, and 2 x 2 mm notches cut into the
// bottom edge every 10 mm so the marks can be counted by touch and the edge
// used as a physical ruler against a plug.
module ruler_card() {
    w = RULER_LEN;
    h = RULER_H;
    difference() {
        union() {
            card_blank(w, h);
            // Raised ticks, clipped to the card footprint so the edge ticks
            // at 0 and 100 mm never overhang.
            intersection() {
                for (x = [0 : 1 : RULER_LEN]) {
                    tick_l = (x % 10 == 0) ? 7 : (x % 5 == 0) ? 5 : 3;
                    translate([x - 0.3, 2.5, stencil_thickness - eps])
                        cube([0.6, tick_l, 0.6 + eps]);
                }
                translate([0, 0, stencil_thickness - eps])
                    linear_extrude(height = 2)
                        square([w, h]);
            }
            translate([2, h - 3 - id_text_size]) raised_id(r1_id);
        }
        // Touch-countable notches every 10 mm along the bottom edge.
        for (x = [10 : 10 : RULER_LEN - 10])
            translate([x - 1, -eps, -eps])
                cube([2, 2 + eps, stencil_thickness + 2 * eps]);
        // Debossed numerals every 10 mm (10-90; the ends are the card edges).
        for (x = [10 : 10 : RULER_LEN - 10])
            translate([x, 11.5]) deboss_text(str(x), 3, halign = "center");
        translate([2 + id_text_size * 2 + 4, h - 3 - id_text_size])
            deboss_text("MM", 5);
    }
}

// ── C1: cord gauge card ──────────────────────────────────────────────────────
// Through-holes 3-9 mm: the smallest hole the cord slides through is the
// cord thickness (worksheet measurement 6).
module cord_card() {
    w  = _c1_card_w();
    h  = _c1_card_h();
    cy = CARD_MARGIN + max(CORD_GAUGE_DIAS) / 2;
    difference() {
        union() {
            card_blank(w, h);
            translate([CARD_MARGIN, h - 3 - id_text_size]) raised_id(c1_id);
        }
        for (k = [0 : len(CORD_GAUGE_DIAS) - 1]) {
            d  = CORD_GAUGE_DIAS[k];
            cx = CARD_MARGIN
                 + sum_list([for (m = [0 : k]) m < k ? CORD_GAUGE_DIAS[m] + 6 : 0])
                 + d / 2;
            translate([cx, cy, -eps])
                cylinder(d = d, h = stencil_thickness + 2 * eps, $fn = quality);
            translate([cx, cy + max(CORD_GAUGE_DIAS) / 2 + 1.2])
                deboss_text(str(d), F_LABEL_SIZE, halign = "center");
        }
        translate([CARD_MARGIN + id_text_size * 2 + 6, h - 3 - id_text_size])
            deboss_text("CORD GAUGE MM", 4, font = FONT);
    }
}

// ── F1 / F2: finger sizing cards ─────────────────────────────────────────────
// The 18 gauge holes of the original finger stencil, split into two cards.
// Smallest comfortable hole minus 5 = measure_finger_width.
module finger_card(rows, id_str, title_str) {
    w = _f_card_w(rows);
    h = _f_card_h(rows);
    difference() {
        union() {
            card_blank(w, h);
            translate([F_EDGE, h - 3 - id_text_size]) raised_id(id_str);
        }
        for (i = [0 : len(rows) - 1]) {
            row = rows[i];
            rw  = _f_row_w(row);
            cy  = h - _f_row_center_y(rows, i);
            for (k = [0 : len(row) - 1]) {
                d  = row[k];
                cx = (w - rw) / 2 + F_EDGE
                     + sum_list([for (m = [0 : k]) m < k ? row[m] + F_HOLE_GAP : 0])
                     + d / 2;
                translate([cx, cy, -eps])
                    cylinder(d = d, h = stencil_thickness + 2 * eps,
                             $fn = quality);
                translate([cx, cy + d / 2 + 1.2])
                    deboss_text(str(d), F_LABEL_SIZE, halign = "center");
            }
        }
        translate([F_EDGE + id_text_size * 2 + 6, h - 3 - F_TITLE_SIZE])
            deboss_text(title_str, F_TITLE_SIZE);
        translate([F_EDGE, h - 5.5 - F_TITLE_SIZE - F_RULE_SIZE])
            deboss_text(FINGER_RULE_TEXT, F_RULE_SIZE, font = FONT);
    }
}

// One card by fixed-list index.
module card(i) {
    if (i <= 2)      plug_card(i);
    else if (i == 3) ruler_card();
    else if (i == 4) cord_card();
    else if (i == 5) finger_card(F1_ROWS, f1_id, "FINGER SIZING 1/2");
    else             finger_card(F2_ROWS, f2_id, "FINGER SIZING 2/2");
}

// ── Sheet packing ────────────────────────────────────────────────────────────
// Deterministic shelf packing of the fixed card list: place left-to-right in
// a row until bed_width would overflow, start a new row until bed_depth
// overflows, then start a new sheet. A card bigger than the bed itself gets
// its own sheet regardless (with a console warning).
// Returns a list of [card index, sheet, x, y].
function _pack(i = 0, sheet = 0, x = 0, y = 0, rowh = 0) =
    i >= N_CARDS ? [] :
    let (w = card_size(i)[0], h = card_size(i)[1],
         oversize = (w > bed_width || h > bed_depth))
    oversize
        ? let (s = (x > 0 || y > 0) ? sheet + 1 : sheet)
          concat([[i, s, 0, 0]], _pack(i + 1, s + 1, 0, 0, 0))
        : let (wrap = (x > 0 && x + w > bed_width),
               nx   = wrap ? 0 : x,
               ny   = wrap ? y + rowh + CARD_GAP : y,
               nrh  = wrap ? 0 : rowh,
               over = (ny > 0 && ny + h > bed_depth),
               fs   = over ? sheet + 1 : sheet,
               fx   = over ? 0 : nx,
               fy   = over ? 0 : ny)
          concat([[i, fs, fx, fy]],
                 _pack(i + 1, fs, fx + w + CARD_GAP, fy,
                       max(over ? 0 : nrh, h)));

PLACEMENTS = _pack();
N_SHEETS   = max([for (p = PLACEMENTS) p[1]]) + 1;

function _join(v, i = 0) =
    i >= len(v) ? "" :
    i == len(v) - 1 ? v[i] : str(v[i], ", ", _join(v, i + 1));

echo(str("STENCIL: ", N_CARDS, " cards packed onto ", N_SHEETS,
         " sheet(s) for a ", bed_width, " x ", bed_depth, " mm bed"));
for (s = [0 : N_SHEETS - 1])
    echo(str("SHEET ", s + 1, ": ",
             _join([for (p = PLACEMENTS) if (p[1] == s) CARD_IDS[p[0]]])));
for (p = PLACEMENTS)
    if (card_size(p[0])[0] > bed_width || card_size(p[0])[1] > bed_depth)
        echo(str("WARNING: CARD ", CARD_IDS[p[0]], " IS ",
                 card_size(p[0])[0], " x ", card_size(p[0])[1],
                 " MM AND EXCEEDS THE BED - PRINTED ALONE ON SHEET ",
                 p[1] + 1));
if (part_index > N_SHEETS)
    echo(str("WARNING: PART_INDEX ", part_index, " IS EMPTY - ONLY ",
             N_SHEETS, " SHEET(S) FOR THIS BED"));

// ── Render ───────────────────────────────────────────────────────────────────
// part_index = 0: every sheet at once, each sheet offset along Y by the bed
// depth + 15 mm. part_index = N: only sheet N, at the origin, for export.
for (p = PLACEMENTS) {
    if (part_index == 0 || p[1] == part_index - 1) {
        sheet_dy = (part_index == 0) ? p[1] * (bed_depth + 15) : 0;
        translate([p[2], p[3] + sheet_dy, 0])
            card(p[0]);
    }
}
