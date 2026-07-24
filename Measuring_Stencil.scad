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
//                 slips sideways into the open cord slot, that preset fits —
//                 pick it in Step 1 and skip measuring entirely.
//                   P1 = flat 2-prong lamp plug (NEMA 1-15)
//                   P2 = standard 3-prong plug (NEMA 5-15)
//                   P3 = heavy-duty extension cord (NEMA 5-15)
//   R1            ruler card — raised tactile ticks (1 mm short, 5 mm medium,
//                 10 mm tall), debossed numerals, and touch-countable edge
//                 notches every 10 mm (worksheet measurements 1-5).
//   C1            cord gauge — open-throat U-slots 3-9 mm through the bottom
//                 edge: slide the card sideways onto an installed cord; the
//                 smallest slot that slips over it is the cord diameter
//                 (worksheet measurement 6).
//   F1 / F2       finger sizing — the 18 gauge holes; smallest comfortable
//                 hole minus 5 = your finger width (worksheet measurement 8).
//
// Label modes (ADA 703 naming — by modality, not audience):
//   Visual  = debossed print lettering (ADA 703.5 style, the default).
//   Tactile = raised uppercase characters at ADA 703.2 size (16 mm, 0.8 mm
//             proud) plus a Grade 2 braille title flap on every card
//             (ADA 703.3). Each flap prints leaning back at 75 deg behind
//             the card's top edge — the angle braille prints crispest at —
//             held by break-away support fins. After printing: snap off the
//             fins, then fold the flap AWAY from the card until it lies
//             flat; the braille lands face-up beyond the card's top edge.
//             Fold once, gently — PETG/PP hinges fold more reliably than PLA.
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

/* [Labels] */
// Visual = debossed print lettering (ADA 703.5 style). Tactile = raised ADA 703.2 characters plus Grade 2 braille flaps (ADA 703.3).
label_mode = "Visual"; // [Visual, Tactile]
// Living-hinge thickness joining each braille flap to its card. Tactile mode only. Independent of stencil_thickness. (mm)
hinge_thickness = 0.6; // [0.3:0.1:1.2]

/* [Card IDs] */
// Raised ID text height on every card. Visual mode only - Tactile mode uses the fixed ADA character size. (mm)
id_text_size = 5; // [3:0.5:8]
// How far the ID letters stand proud of the top face, so they read by touch. Visual mode only. (mm)
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

IS_TACTILE = (label_mode == "Tactile");

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

// Cord gauge slot diameters (worksheet measurement 6).
CORD_GAUGE_DIAS = [3, 4, 5, 6, 7, 8, 9];

FONT_BOLD = "Liberation Sans:style=Bold";
FONT      = "Liberation Sans";

_deboss = min(deboss_depth, stencil_thickness - 0.4);

// ── Tactile lettering (ADA 703.2, values from the assistive-forge sign) ─────
ADA_CHAR_HEIGHT = 16;   // ADA 703.2.5: 15.9-50.8 mm
ADA_RAISE       = 0.8;  // ADA 703.2.1: >= 0.8 mm proud

// ── Grade 2 braille flap titles (ADA 703.3, Tactile mode) ───────────────────
// Grade 2 UEB, generated by scripts/generate_braille_labels.mjs — do not
// hand-edit; edit the wording there, re-run it, and paste the output.
// tests/test_braille_labels.py locks this constant to scripts/braille_labels.json.
// P1: "lamp", "2 prong"
// P2: "standard", "3 prong"
// P3: "heavy duty", "cord"
// R1: "ruler 100 mm", "notches 10 mm"
// C1: "cord gauge mm"
// F1: "finger sizing 1 of 2", "width: hole minus 5"
// F2: "finger sizing 2 of 2", "width: hole minus 5"
BRAILLE_LABELS = [
    ["⠇⠁⠍⠏", "⠼⠃⠀⠏⠗⠰⠛"],
    ["⠌⠯⠜⠙", "⠼⠉⠀⠏⠗⠰⠛"],
    ["⠓⠂⠧⠽⠀⠙⠥⠞⠽", "⠉⠕⠗⠙"],
    ["⠗⠥⠇⠻⠀⠼⠁⠚⠚⠀⠍⠍", "⠝⠕⠞⠡⠑⠎⠀⠼⠁⠚⠀⠍⠍"],
    ["⠉⠕⠗⠙⠀⠛⠁⠥⠛⠑⠀⠍⠍"],
    ["⠋⠬⠻⠀⠎⠊⠵⠬⠀⠼⠁⠀⠷⠀⠼⠃", "⠺⠊⠙⠹⠒⠀⠓⠕⠇⠑⠀⠍⠔⠥⠎⠀⠼⠑"],
    ["⠋⠬⠻⠀⠎⠊⠵⠬⠀⠼⠃⠀⠷⠀⠼⠃", "⠺⠊⠙⠹⠒⠀⠓⠕⠇⠑⠀⠍⠔⠥⠎⠀⠼⠑"],
];

// ── Braille flap geometry (wedge-card / braille-sign defaults) ──────────────
// The flap prints as a slab leaning AWAY from the card at FACE_ANGLE, joined
// to the card's top edge by a living hinge and held up by break-away fins.
FACE_ANGLE     = 75;                 // deg from bed (CHI 2024 readability sweet spot)
BRL_DOT_SP     = 2.5;                // dot-to-dot inside a cell
BRL_CELL_SP    = 7.0;                // cell-to-cell
BRL_LINE_SP    = 10.0;               // line-to-line
BRL_BASE_D     = 1.6;                // dot frustum base diameter
BRL_BASE_H     = 0.35;               // dot frustum height
BRL_DOME_D     = 1.4;                // dot dome diameter
BRL_DOME_H     = 0.35;               // dot dome height (total 0.7 <= ADA 0.9)
BRL_DOT_H      = BRL_BASE_H + BRL_DOME_H;
DOT_FACE_EMBED = 0.02;               // sink dots into the face so the union fuses
FLAP_MARGIN    = 4;                  // face border around the braille block
HINGE_LEN      = 2;                  // free hinge length between card and slab
FIN_INTERVAL   = 25;  FIN_OFFSET = 1.0;  FIN_THICK = 1.2;
BRIDGE_N = 4;  BRIDGE_W = 0.5;  BRIDGE_H = 0.5;  BRIDGE_CONTACT = 0.3;
BRIM_W = 2.0;  BRIM_T = 0.2;
// Dot tessellation (wedge-card "Medium" defaults). Deliberately decoupled
// from `quality`: hundreds of 1.5 mm dots at $fn = 64 would multiply the
// facet count (and the exported STL) roughly 40x for no printable gain.
BRL_DOME_FN = 32;   // sphere segments for the dome
BRL_CONE_FN = 40;   // segments for the frustum base

// Dot layout inside a cell: BRL_DOT_POS[i] = [row, col] for braille dot i+1,
// row 0/1/2 = top/middle/bottom, col 0/1 = left/right (braille_sign.scad).
BRL_COL_X   = [-BRL_DOT_SP / 2, +BRL_DOT_SP / 2];
BRL_ROW_Y   = [+BRL_DOT_SP, 0, -BRL_DOT_SP];
BRL_DOT_POS = [[0, 0], [1, 0], [2, 0], [0, 1], [1, 1], [2, 1]];

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

// Mode-derived sizes: Tactile swaps every label to ADA scale and grows the
// bands around them so nothing collides. Visual mode reproduces the original
// layout exactly. Used by BOTH the card modules and the size functions below
// so the sheet packer always sees the true footprint.
_ID_SIZE      = IS_TACTILE ? ADA_CHAR_HEIGHT : id_text_size;
_NUM_SIZE     = IS_TACTILE ? ADA_CHAR_HEIGHT : F_LABEL_SIZE;
_ID_RAISE     = IS_TACTILE ? ADA_RAISE : id_emboss_height;
_C1_GAP       = IS_TACTILE ? 8 : 6;   // slot gap; ADA digits are ~10 mm wide
_P_CAPT_BAND  = IS_TACTILE ? ADA_CHAR_HEIGHT + 2 : P_CAPT_BAND;
_F_TITLE_BAND = IS_TACTILE ? ADA_CHAR_HEIGHT + 6 : F_TITLE_BAND;
_F_LABEL_H    = IS_TACTILE ? ADA_CHAR_HEIGHT + 2 : F_LABEL_H;
// R1 grows so the ADA-size ID clears the raised ticks (which reach y=9.5).
_RULER_H      = IS_TACTILE ? RULER_H + 8 : RULER_H;

function sum_list(v, i = 0) = i >= len(v) ? 0 : v[i] + sum_list(v, i + 1);

// ── Braille flap size functions (consumed by the sheet packer too) ──────────
function _flap_lines(i)  = len(BRAILLE_LABELS[i]);
function _flap_face_h(n) = 2 * FLAP_MARGIN + (n - 1) * BRL_LINE_SP + 2 * BRL_DOT_SP;
function _flap_run(n)    = _flap_face_h(n) * cos(FACE_ANGLE);
function _flap_rise(n)   = _flap_face_h(n) * sin(FACE_ANGLE);
// Bed depth the printed flap assembly adds beyond the card's top edge.
function _flap_depth(i)  =
    HINGE_LEN + stencil_thickness + FIN_OFFSET
    + _flap_run(_flap_lines(i)) + BRIM_W;

// ── Card size functions (consumed by the sheet packer) ──────────────────────
function _p_dims(i) = PLUG_PRESET_DIMS[i];
function _p_wmax(i) = max(_p_dims(i)[2], _p_dims(i)[3]);
function _p_tmax(i) = max(_p_dims(i)[4], _p_dims(i)[5]);
function _p_card_w(i) =
    2 * CARD_MARGIN + _p_wmax(i) + P_WEB + _p_tmax(i) + P_WEB + _p_dims(i)[6];
function _p_card_h(i) =
    4 + P_NAME_BAND + _P_CAPT_BAND + _p_dims(i)[1] + 3 + _ID_SIZE + 3;

function _c1_card_w() =
    2 * CARD_MARGIN
    + sum_list(CORD_GAUGE_DIAS)
    + (len(CORD_GAUGE_DIAS) - 1) * _C1_GAP;
function _c1_card_h() =
    CARD_MARGIN + max(CORD_GAUGE_DIAS) + 1.2 + _NUM_SIZE + 2.8
    + _ID_SIZE + 3;

function _f_row_w(row) =
    2 * F_EDGE + (len(row) - 1) * F_HOLE_GAP + sum_list([for (d = row) d]);
function _f_card_w(rows) = max([for (r = rows) _f_row_w(r)]);
// Y of a row's hole centers, measured down from the card top edge.
function _f_row_center_y(rows, i) =
    _F_TITLE_BAND
    + sum_list([for (j = [0 : i]) _F_LABEL_H + rows[j][len(rows[j]) - 1] / 2])
    + sum_list([for (j = [0 : i])
                    j < i ? rows[j][len(rows[j]) - 1] / 2 + F_ROW_GAP : 0]);
function _f_card_h(rows) =
    let (n = len(rows) - 1)
    _f_row_center_y(rows, n) + rows[n][len(rows[n]) - 1] / 2 + F_EDGE;

// Fixed card list: index -> [user-facing id, width, height].
CARD_IDS = [p1_id, p2_id, p3_id, r1_id, c1_id, f1_id, f2_id];
function _card_body_size(i) =
    i <= 2 ? [_p_card_w(i), _p_card_h(i)] :
    i == 3 ? [RULER_LEN, _RULER_H] :
    i == 4 ? [_c1_card_w(), _c1_card_h()] :
    i == 5 ? [_f_card_w(F1_ROWS), _f_card_h(F1_ROWS)] :
             [_f_card_w(F2_ROWS), _f_card_h(F2_ROWS)];
// Full printed footprint: in Tactile mode the braille flap (hinge + leaning
// slab + fins + brim) extends past the card's top edge.
function card_size(i) =
    let (base = _card_body_size(i))
    IS_TACTILE ? [base[0], base[1] + _flap_depth(i)] : base;
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

// Mode-aware short label (IDs, numerals, W/T captions — 1-2 characters).
// Visual: debossed at the given size (call from the SUBTRACT side of the
// card's difference()). Tactile: raised uppercase ADA 703.2 character
// (call from the card's union()). Card modules route each labels() helper
// to the right side based on IS_TACTILE.
module card_label(t, size, font = FONT_BOLD, halign = "left") {
    if (IS_TACTILE)
        translate([0, 0, stencil_thickness - eps])
            linear_extrude(height = ADA_RAISE + eps)
                text(t, size = ADA_CHAR_HEIGHT, font = FONT_BOLD,
                     halign = halign, valign = "baseline");
    else
        deboss_text(t, size, font, halign);
}

// Raised, touch-readable card ID (union on the top face).
module raised_id(t) {
    translate([0, 0, stencil_thickness - eps])
        linear_extrude(height = _ID_RAISE + eps)
            text(t, size = _ID_SIZE, font = FONT_BOLD,
                 halign = "left", valign = "baseline");
}

// Rounded-corner plug silhouette: isoceles trapezoid, `base` wide at the
// bottom (wall end), `top` wide at the top (cord end), `h` tall.
module plug_trap_2d(base, top, h) {
    offset(r = 1) offset(delta = -1)
        polygon([[-base / 2, 0], [base / 2, 0], [top / 2, h], [-top / 2, h]]);
}

// ── Braille flap (Tactile mode) ──────────────────────────────────────────────
// Each card grows a braille title flap past its TOP edge (y = h): a thin
// living hinge, then a slab leaning AWAY from the card at FACE_ANGLE with
// the braille dots on the CARD-FACING surface, and break-away support fins
// behind it (wedge-card technique: fins + snap-off bridges + bed brim).
//
// Side view (YZ plane; card lies flat to the left, +y = away from the card):
//
//              top of flap       dots on the face toward the card;
//                 /|  |\         fins + brims behind (+y), on the bed
//              ● / |  | \
//             ● /  |  |  \  <- fin (snap-off bridges, 0.3 mm contact)
//            ● /   |  |___\_____ bed
//   card ===[hinge]/_____________
//   y=0 .. h    ^ HINGE_LEN x hinge_thickness strip
//
// Post-print: snap the fins off, then fold the flap AWAY from the card
// (like a door falling backward) until it lies flat — the braille face
// lands facing UP, extending the card past its top edge.

// Unicode braille char (U+2800-U+28FF) -> 6-bit dot array
// (ported from braille_sign.scad).
function get_dot_pattern(char) =
    let (code = ord(char))
    (code >= 10240 && code <= 10495)
        ? let (pattern = code - 10240)
          [
              (pattern % 2) >= 1 ? 1 : 0,
              floor(pattern / 2)  % 2 >= 1 ? 1 : 0,
              floor(pattern / 4)  % 2 >= 1 ? 1 : 0,
              floor(pattern / 8)  % 2 >= 1 ? 1 : 0,
              floor(pattern / 16) % 2 >= 1 ? 1 : 0,
              floor(pattern / 32) % 2 >= 1 ? 1 : 0
          ]
        : [0, 0, 0, 0, 0, 0];

// ADA-profile dot: frustum base + spherical dome, built centered so the
// caller seats it with +BRL_DOT_H/2 (ported from the wedge card).
module braille_dot_centered() {
    _dome_r   = BRL_DOME_D / 2;
    _R_sphere = (_dome_r * _dome_r + BRL_DOME_H * BRL_DOME_H) / (2 * BRL_DOME_H);
    _center_z = BRL_BASE_H + BRL_DOME_H - _R_sphere;
    _fuse     = 0.02;   // base extends into the dome so the union fuses
    translate([0, 0, -BRL_DOT_H / 2]) {
        translate([0, 0, (BRL_BASE_H + _fuse) / 2])
            cylinder(h = BRL_BASE_H + _fuse,
                     r1 = BRL_BASE_D / 2, r2 = BRL_DOME_D / 2,
                     center = true, $fn = BRL_CONE_FN);
        intersection() {
            translate([0, 0, _center_z]) sphere(r = _R_sphere, $fn = BRL_DOME_FN);
            translate([0, 0, BRL_BASE_H + _R_sphere])
                cube([_R_sphere * 4, _R_sphere * 4, _R_sphere * 2],
                     center = true);
        }
    }
}

// Extrude a YZ-plane profile across X: local x->global y, y->z, z->x.
module flap_yz_prism(profile, x0, wx) {
    translate([x0, 0, 0])
        rotate([90, 0, 90])
            linear_extrude(height = wx)
                polygon(profile);
}

// Dots for the given braille lines in the face-local frame: x across the
// card (shared with card x), y up the slope (0 = face bottom edge at the
// hinge), z = outward face normal. Line 0 sits at the TOP of the face.
// CRITICAL — no mirror: a fold about the x-parallel hinge preserves x, so
// cells laid out in +x order read left-to-right both as printed (viewed
// from the card side) and after folding flat (viewed from above).
module flap_face_dots(lines, w) {
    face_h = _flap_face_h(len(lines));
    for (line = [0 : len(lines) - 1]) {
        cells = len(lines[line]);
        v     = face_h - FLAP_MARGIN - line * BRL_LINE_SP;  // row centre
        x0    = w / 2 - (cells - 1) * BRL_CELL_SP / 2;      // first cell centre
        for (col = [0 : cells - 1]) {
            dots = get_dot_pattern(lines[line][col]);
            for (d = [0 : 5])
                if (dots[d] == 1)
                    translate([x0 + col * BRL_CELL_SP + BRL_COL_X[BRL_DOT_POS[d][1]],
                               v + BRL_ROW_Y[BRL_DOT_POS[d][0]],
                               BRL_DOT_H / 2 - DOT_FACE_EMBED])
                        braille_dot_centered();
        }
    }
}

// Fin X centres across the flap width: both outer edges (inset half a fin
// so nothing overhangs the card footprint) plus every FIN_INTERVAL.
function flap_fin_xs(w) =
    let (x_first = FIN_THICK / 2,
         x_last  = w - FIN_THICK / 2,
         n       = max(1, floor((x_last - x_first) / FIN_INTERVAL)))
    concat([x_first],
           [for (k = [1 : n])
               let (x = x_first + k * FIN_INTERVAL)
               if (x < x_last - 1e-3) x],
           [x_last]);

// Y of the slab's BACK (away-from-card) face at height z.
function _flap_back_y(y0, run, rise, z) = y0 + stencil_thickness + run * z / rise;

// One right-triangle fin prism: vertical spine on the far side, hypotenuse
// hugging the slab's back face at FIN_OFFSET. Lives entirely at
// y > y0 + stencil_thickness, so it can never touch the card or hinge.
module flap_fin(x, y0, run, rise) {
    yb = y0 + stencil_thickness + FIN_OFFSET;
    flap_yz_prism([[yb, 0], [yb + run, 0], [yb + run, rise]],
                  x - FIN_THICK / 2, FIN_THICK);
}

// Bed brim under one fin, clamped so it never touches the slab foot and
// never overhangs the card footprint in x.
module flap_fin_brim(x, y0, run, w) {
    yb   = y0 + stencil_thickness + FIN_OFFSET;
    y_lo = max(yb - BRIM_W, y0 + stencil_thickness + 0.05);
    y_hi = yb + run + BRIM_W;
    x_lo = max(x - FIN_THICK / 2 - BRIM_W, 0);
    x_hi = min(x + FIN_THICK / 2 + BRIM_W, w);
    translate([x_lo, y_lo, 0])
        cube([x_hi - x_lo, y_hi - y_lo, BRIM_T]);
}

// BRIDGE_N snap-off prongs climbing the FIN_OFFSET gap: each merges
// BRIDGE_CONTACT into the slab's back face and runs eps PAST the fin's
// vertical spine so it always overlaps the fin solid — an exactly-coplanar
// bridge end face would export as a non-watertight T-junction
// (wedge-card bridges() math).
module flap_bridges(x, y0, run, rise) {
    top_clear = 0.1;  // keep the top bridge below the slab/fin top plane
    z_lo = min(max(BRIDGE_H, 2),
               max(rise - BRIDGE_H / 2 - top_clear, BRIDGE_H / 2));
    z_hi = max(z_lo, rise - BRIDGE_H / 2 - top_clear);
    y_far = y0 + stencil_thickness + FIN_OFFSET + run + eps;
    for (k = [0 : BRIDGE_N - 1]) {
        z_k = (BRIDGE_N == 1) ? (z_lo + z_hi) / 2
                              : z_lo + (z_hi - z_lo) * k / (BRIDGE_N - 1);
        y_near = _flap_back_y(y0, run, rise, z_k) - BRIDGE_CONTACT;
        translate([x - BRIDGE_W / 2, y_near, z_k - BRIDGE_H / 2])
            cube([BRIDGE_W, y_far - y_near, BRIDGE_H]);
    }
}

// Whole flap assembly for card index i (card is w x h, at the origin).
// Call from inside the card's union() when IS_TACTILE.
module braille_flap(i, w, h) {
    lines = BRAILLE_LABELS[i];
    n     = len(lines);
    run   = _flap_run(n);
    rise  = _flap_rise(n);
    t     = stencil_thickness;
    y0    = h + HINGE_LEN;   // slab bottom-front edge

    // Living hinge: 0.5 mm overlap into both the card and the slab, inset
    // 0.5 mm clear of the corner arcs (an end face exactly tangent to the
    // arc start would export as a non-watertight tangency).
    translate([corner_radius + 0.5, h - 0.5, 0])
        cube([w - 2 * corner_radius - 1.0, HINGE_LEN + 1.0, hinge_thickness]);

    // Leaning slab: sheared parallelogram, full card width.
    flap_yz_prism([[y0, 0], [y0 + t, 0], [y0 + t + run, rise], [y0 + run, rise]],
                  0, w);

    // Braille dots on the card-facing surface. rotate([FACE_ANGLE,0,0])
    // maps local +z to the face's outward normal (0, -sin75, cos75).
    translate([0, y0, 0])
        rotate([FACE_ANGLE, 0, 0])
            flap_face_dots(lines, w);

    // Break-away support structure behind the slab.
    for (x = flap_fin_xs(w)) {
        flap_fin(x, y0, run, rise);
        flap_fin_brim(x, y0, run, w);
        flap_bridges(x, y0, run, rise);
    }
}

// ── P1 / P2 / P3: plug preset silhouette cards ───────────────────────────────
// Two through-cutouts side by side — the width view (W) and the thickness
// view (T) — plus an open cord slot. Hold the plug in/behind a cutout: if
// it fills the opening, this preset fits (no ruler needed). The cord slot
// opens through the bottom edge so the card slips sideways over an
// installed cord instead of needing a free cord end.
module plug_card_labels(i) {
    x_w = CARD_MARGIN + _p_wmax(i) / 2;
    x_t = CARD_MARGIN + _p_wmax(i) + P_WEB + _p_tmax(i) / 2;
    translate([x_w, 4 + P_NAME_BAND]) card_label("W", 4, halign = "center");
    translate([x_t, 4 + P_NAME_BAND]) card_label("T", 4, halign = "center");
}

module plug_card(i) {
    d      = _p_dims(i);
    w      = _p_card_w(i);
    h      = _p_card_h(i);
    y_sil  = 4 + P_NAME_BAND + _P_CAPT_BAND;     // silhouette bottom edge
    x_w    = CARD_MARGIN + _p_wmax(i) / 2;
    x_t    = CARD_MARGIN + _p_wmax(i) + P_WEB + _p_tmax(i) / 2;
    x_c    = CARD_MARGIN + _p_wmax(i) + P_WEB + _p_tmax(i) + P_WEB + d[6] / 2;

    difference() {
        union() {
            card_blank(w, h);
            translate([CARD_MARGIN, h - 3 - _ID_SIZE])
                raised_id(CARD_IDS[i]);
            if (IS_TACTILE) {
                plug_card_labels(i);
                braille_flap(i, w, h);
            }
        }
        // Width view: width_wall at the base, width_cable at the top.
        translate([x_w, y_sil, -eps])
            linear_extrude(height = stencil_thickness + 2 * eps)
                plug_trap_2d(d[2], d[3], d[1]);
        // Thickness view: the two thickness stations.
        translate([x_t, y_sil, -eps])
            linear_extrude(height = stencil_thickness + 2 * eps)
                plug_trap_2d(d[4], d[5], d[1]);
        // Cord slot, bottom-aligned with the silhouettes and open through
        // the bottom edge (slide sideways onto an installed cord).
        translate([x_c, y_sil + d[6] / 2, -eps])
            cylinder(d = d[6], h = stencil_thickness + 2 * eps, $fn = quality);
        // Channel x-range (x_c +/- d[6]/2) starts at >= 65 mm on every
        // preset while the debossed name ends by ~61 mm — verified clear.
        translate([x_c - d[6] / 2, -eps, -eps])
            cube([d[6], y_sil + d[6] / 2 + eps, stencil_thickness + 2 * eps]);
        if (!IS_TACTILE) {
            // Captions under the openings (debossed in Visual mode).
            plug_card_labels(i);
            // Cord diameter caption, kept left of the open channel.
            translate([x_c - d[6] / 2 - 1.5, 4 + P_NAME_BAND])
                deboss_text(str(d[6]), 3.2, halign = "right");
            // Preset name along the bottom.
            translate([CARD_MARGIN, 4])
                deboss_text(PLUG_PRESET_NAMES[i], 3.2, font = FONT);
        }
    }
}

// ── R1: tactile ruler card ───────────────────────────────────────────────────
// 100 mm strip. Raised ticks (short = 1 mm, medium = 5 mm, tall = 10 mm),
// debossed numerals (Visual mode), and 2 x 2 mm notches cut into the bottom
// edge every 10 mm so the marks can be counted by touch and the edge used
// as a physical ruler against a plug. Tactile mode drops the numerals (an
// ADA-size digit cannot fit the 10 mm pitch) — the braille flap carries the
// description instead — and grows the card for the ADA-size ID.
module ruler_card() {
    w = RULER_LEN;
    h = _RULER_H;
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
            translate([2, h - 3 - _ID_SIZE]) raised_id(r1_id);
            if (IS_TACTILE) braille_flap(3, w, h);
        }
        // Touch-countable notches every 10 mm along the bottom edge.
        for (x = [10 : 10 : RULER_LEN - 10])
            translate([x - 1, -eps, -eps])
                cube([2, 2 + eps, stencil_thickness + 2 * eps]);
        if (!IS_TACTILE) {
            // Debossed numerals every 10 mm (10-90; the ends are the card edges).
            for (x = [10 : 10 : RULER_LEN - 10])
                translate([x, 11.5]) deboss_text(str(x), 3, halign = "center");
            translate([2 + id_text_size * 2 + 4, h - 3 - id_text_size])
                deboss_text("MM", 5);
        }
    }
}

// ── C1: cord gauge card ──────────────────────────────────────────────────────
// Open-throat U-slots 3-9 mm through the card's BOTTOM edge: slide the card
// sideways over an installed cord; the smallest slot that slips over it is
// the cord diameter (worksheet measurement 6). No free cord end needed.
module cord_card_labels() {
    cy = CARD_MARGIN + max(CORD_GAUGE_DIAS) / 2;
    for (k = [0 : len(CORD_GAUGE_DIAS) - 1]) {
        d  = CORD_GAUGE_DIAS[k];
        cx = CARD_MARGIN
             + sum_list([for (m = [0 : k]) m < k ? CORD_GAUGE_DIAS[m] + _C1_GAP : 0])
             + d / 2;
        translate([cx, cy + max(CORD_GAUGE_DIAS) / 2 + 1.2])
            card_label(str(d), F_LABEL_SIZE, halign = "center");
    }
}

module cord_card() {
    w  = _c1_card_w();
    h  = _c1_card_h();
    cy = CARD_MARGIN + max(CORD_GAUGE_DIAS) / 2;
    difference() {
        union() {
            card_blank(w, h);
            translate([CARD_MARGIN, h - 3 - _ID_SIZE]) raised_id(c1_id);
            if (IS_TACTILE) {
                cord_card_labels();
                braille_flap(4, w, h);
            }
        }
        for (k = [0 : len(CORD_GAUGE_DIAS) - 1]) {
            d  = CORD_GAUGE_DIAS[k];
            cx = CARD_MARGIN
                 + sum_list([for (m = [0 : k]) m < k ? CORD_GAUGE_DIAS[m] + _C1_GAP : 0])
                 + d / 2;
            // U-slot: the gauge circle plus a channel of width d opening
            // through the bottom edge (~10.5 mm deep; >= 6 mm teeth between).
            translate([cx, cy, -eps])
                cylinder(d = d, h = stencil_thickness + 2 * eps, $fn = quality);
            translate([cx - d / 2, -eps, -eps])
                cube([d, cy + eps, stencil_thickness + 2 * eps]);
        }
        if (!IS_TACTILE) {
            cord_card_labels();
            translate([CARD_MARGIN + id_text_size * 2 + 6, h - 3 - id_text_size])
                deboss_text("CORD GAUGE MM", 4, font = FONT);
        }
    }
}

// ── F1 / F2: finger sizing cards ─────────────────────────────────────────────
// The 18 gauge holes of the original finger stencil, split into two cards.
// Smallest comfortable hole minus 5 = measure_finger_width.
module finger_card_labels(rows, w, h) {
    for (i = [0 : len(rows) - 1]) {
        row = rows[i];
        rw  = _f_row_w(row);
        cy  = h - _f_row_center_y(rows, i);
        for (k = [0 : len(row) - 1]) {
            d  = row[k];
            cx = (w - rw) / 2 + F_EDGE
                 + sum_list([for (m = [0 : k]) m < k ? row[m] + F_HOLE_GAP : 0])
                 + d / 2;
            translate([cx, cy + d / 2 + 1.2])
                card_label(str(d), F_LABEL_SIZE, halign = "center");
        }
    }
}

module finger_card(rows, idx, id_str, title_str) {
    w = _f_card_w(rows);
    h = _f_card_h(rows);
    difference() {
        union() {
            card_blank(w, h);
            translate([F_EDGE, h - 3 - _ID_SIZE]) raised_id(id_str);
            if (IS_TACTILE) {
                finger_card_labels(rows, w, h);
                braille_flap(idx, w, h);
            }
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
            }
        }
        if (!IS_TACTILE) {
            finger_card_labels(rows, w, h);
            translate([F_EDGE + id_text_size * 2 + 6, h - 3 - F_TITLE_SIZE])
                deboss_text(title_str, F_TITLE_SIZE);
            translate([F_EDGE, h - 5.5 - F_TITLE_SIZE - F_RULE_SIZE])
                deboss_text(FINGER_RULE_TEXT, F_RULE_SIZE, font = FONT);
        }
    }
}

// One card by fixed-list index.
module card(i) {
    if (i <= 2)      plug_card(i);
    else if (i == 3) ruler_card();
    else if (i == 4) cord_card();
    else if (i == 5) finger_card(F1_ROWS, 5, f1_id, "FINGER SIZING 1/2");
    else             finger_card(F2_ROWS, 6, f2_id, "FINGER SIZING 2/2");
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

echo(str("STENCIL: ", N_CARDS, " cards (", label_mode, " labels) packed onto ",
         N_SHEETS, " sheet(s) for a ", bed_width, " x ", bed_depth, " mm bed"));
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

// Braille width guard: every flap line must fit its card. Fix by shortening
// the wording in scripts/generate_braille_labels.mjs and regenerating.
if (IS_TACTILE)
    for (i = [0 : N_CARDS - 1])
        for (line = BRAILLE_LABELS[i])
            if (len(line) * BRL_CELL_SP + 2 * FLAP_MARGIN > card_size(i)[0])
                echo(str("WARNING: BRAILLE LINE ON CARD ", CARD_IDS[i],
                         " IS ", len(line), " CELLS (",
                         len(line) * BRL_CELL_SP + 2 * FLAP_MARGIN,
                         " MM) AND EXCEEDS THE ", card_size(i)[0],
                         " MM CARD WIDTH - SHORTEN THE SOURCE STRING"));

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
