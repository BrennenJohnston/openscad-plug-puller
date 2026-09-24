# Plug Puller — Complete Object Reference

> **Covers**: two tools in two files — the one-sided puller and the
> two-sided puller
> **Files**: `src/Plug_Puller_Parametric.scad`, the one-sided puller
> (`include`s `src/fit_sizes.scad`, `src/fit_measured.scad`, then
> `src/presets.scad` — order matters, see [Section 8.4](#84-include-order));
> `src/Plug_Puller_Two_Sided.scad`, the two-sided puller (`include`s
> `src/fit_sizes.scad`)
> **Entry points**: open either file in OpenSCAD; the single-file builds
> are `dist/Plug_Puller_SingleFile.scad` and
> `dist/Plug_Puller_Two_Sided_SingleFile.scad`
> **One-sided heritage**: `v6.0/CAD/v6.0.stl` ("Plug Puller 3.1 - B")
> **Two-sided reference**: `plug references/3 Prong Heavy Ideal Sample/…Plug_Bottom.stl`
> **Last Updated**: 2026-09-24
> **Purpose**: Authoritative reference for the geometry of both tools,
> parameters, sizes, the measurement derivation layer, CSG construction,
> render modes, in-model validation warnings, and the parity story.
> Intended for AI models and human engineers modifying, debugging, or
> extending the design.

For the parameter min/max/step/type schemas and the validator, see
[`parameter_mapping.json`](../parameter_mapping.json) (79 rows, one-sided)
and [`parameter_mapping_two_sided.json`](../parameter_mapping_two_sided.json)
(39 rows, two-sided).

---

## 1. Object purpose and physical context

The Plug Puller is a handheld assistive device that helps users grip and
remove electrical plugs from wall outlets. It comes as **two tools, each in
its own file**:

- **One-sided puller** (`src/Plug_Puller_Parametric.scad`) — the single
  flat printed piece carried over and reworked from v6: finger holes, a
  chiral cord J-hook, a plug wall notch, a dome plug pocket, a zip-tie
  grid, and wing/classic velcro slots. The pocket walls and the zip/velcro
  placement follow a **plug side rail** (Section 5.2) so a single taper
  dial slides them along the plug's side.
- **Two-sided puller** (`src/Plug_Puller_Two_Sided.scad`) — a pair of
  identical serrated plates that sandwich a plug and zip-tie together face
  to face, with the cord exiting a narrow channel and the user pulling from
  finger lobes at the cord end (Section 6). With `Rounded sides` the plates
  carry a sloped cradle; the file prints both plates side by side.

The files are independent. A plug 24 mm thick or more gets W-20 in the
one-sided file (`PLUG THICKER THAN 24MM - USE THE TWO-SIDED PULLER FILE`);
the tool still builds.

## 2. The references and the Medium size

**The Medium one-sided puller descends from the v6 CAD reference** but no
longer clones it at the mesh level: the pocket is re-derived as a
taper-aware rounded trapezoid and the zip/velcro features hang off the
plug rail, so the placement grid moves intentionally. The parity story is
now:

1. **Self-consistency** — with `size = Medium`, `plug_preset = "Measure my
   plug"`, and default measurements, every `FIT_MEASURED` value equals
   `PRESET_MEDIUM` exactly (Section 4.2).
2. **Golden-fixture parity** — `tests/test_render_modes.py` renders each
   fixture and asserts mesh parity with the committed `reference.stl`.
3. **Two-sided parity** — `tests/test_two_sided_parity.py` asserts that the
   two-sided file's plate at the heavy-duty preset is the same object as the
   `two_sided_plate` golden fixture (volume, area and bounds to 6 decimals)
   and prints the finger-bore table (17.5 / 21.0 / 24.0 mm at Small /
   Medium / Large); `tests/test_clamshell_parity.py` asserts loose
   envelope + feature-inventory + grip-gap parity against the idealized
   heavy-duty plate.

The v6-CAD feature-by-feature parity suite (`test_reference_parity.py`)
was **retired**: the pocket and rail placement are re-parametrised on
purpose.

### 2.1 Plug presets (two-station, re-measured)

`plug_preset` prefills the effective plug measurements (`_eff_*`) from
two-station measurements of the three reference plugs
(`scripts/measure_plug_references.py`: length = the molded body only, the
prong-end station just behind the prongs, the cord-end station at the cord
end of the gripped body — the heavy-duty plug's narrower strain-relief
boot is skipped); the manual sliders are ignored unless
`plug_preset = "Measure my plug"`. In the one-sided file:

| Preset | length | width prong end/cord end | thickness prong end/cord end | cord |
|--------|--------|--------------------------|------------------------------|------|
| Flat 2-prong lamp plug - NEMA 1-15 | 37.0 | 25.0 / 11.2 | 18.6 / 8.6 | 3.6 |
| Standard 3-prong plug - NEMA 5-15 | 46.2 | 26.6 / 13.4 | 18.9 / 15.0 | 7.0 |
| Heavy-duty extension cord - NEMA 5-15 | 43.8 | 25.8 / 21.9 | **27.0** / 27.0 | 8.2 |

The heavy-duty preset's 27 mm thickness (`_eff_plug_thickness` = the
fatter end) trips W-20 in the one-sided file. The two-sided file offers only
that preset: length 43.8, width 27.0 / 27.0 (the size the plates close
across: the one-sided file's thickness pair), cord 8.2, always built with
`Flat sides` and the bite (the preset's tested grip).

## 3. Coordinate systems

### 3.1 One-sided puller

| Axis | Direction | Zero | Positive |
|------|-----------|------|----------|
| **X** | Horizontal | Midline | Right |
| **Y** | Along body length | Cord / hook end | Toward plug end |
| **Z** | Slab thickness | Print bed | Away from bed |

Symmetric about X = 0 except the chiral J-hook.

### 3.2 Two-sided plate (local frame)

| Axis | Direction | Zero | Positive |
|------|-----------|------|----------|
| **X** | Across the plate | Midline (mirrored arms) | Right |
| **Y** | Along the arms | Cord end | Toward the plug/arm tip |
| **Z** | Plate thickness | Outer face (the print bed) | Mating face at Z = `plate_thickness`, where the two plates meet |

## 4. Customizer architecture

File order = UI order. The one-sided file has three audience tiers: the
numbered Steps (beginner path), the `Advanced -` sections (power users),
and the `(Custom size only)` sections (experts, active only in
`size = Custom`). The two-sided file has the Steps and the Advanced
sections.

One-sided puller (`src/Plug_Puller_Parametric.scad`):

```
── Beginner tier ──────────────────────────────────────────────────────
/* [Step 1 - Your Plug] */     plug_preset, measure_plug_length [12:85],
                               measure_plug_width_prong_end/_cord_end [8:38],
                               measure_plug_thickness_prong_end/_cord_end [4:40],
                               measure_cord_thickness [1.5:9],
                               measure_wall_plate_style, show_plug_preview
/* [Step 2 - Size] */          size = Small | Medium | Large |
                               Measure my hand | Custom + hand sliders
/* [Step 3 - Attachment] */    attachment, velcro_style, strap_width
/* [Step 4 - Cord Hook] */     hook_hand
── Advanced tier ──────────────────────────────────────────────────────
/* [Advanced - Zip Tie Placement] */  zip_placement dials
/* [Advanced - Velcro Placement] */   velcro_placement dials
/* [Advanced - Render Quality] */     quality
/* [Hidden] */                 render_mode, eps, _pp_active (routing)
── Custom / expert tier ───────────────────────────────────────────────
/* [Custom Mode] + [Body Shape (Custom size only)] etc. */ custom_* sliders
```

Two-sided puller (`src/Plug_Puller_Two_Sided.scad`):

```
/* [Step 1 - Your Plug] */     plug_preset = Measure my plug |
                               Heavy-duty extension cord - NEMA 5-15,
                               measure_plug_length [12:85],
                               measure_plug_width_prong_end/_cord_end [5:40],
                               measure_cord_thickness [1.5:12],
                               plug_sides = Rounded sides | Flat sides,
                               show_plug_preview
/* [Step 2 - Size] */          size = Small | Medium | Large | Measure my hand,
                               measure_finger_width
/* [Step 3 - Attachment] */    attachment = Zip ties + Velcro strap | Zip ties,
                               strap_width
/* [Step 4 - Print Layout] */  print_layout = Both plates | One plate
/* [Advanced - Two-Sided Puller] */ 26 plate_* dials (plate_wall_boost leads)
/* [Advanced - Render Quality] */   quality
/* [Hidden] */                 render_mode = Full | One plate, eps
```

The beginner-facing walkthrough is `docs/guides/quick-start-beginner.md`;
the Advanced/Custom tiers are documented for users in
`docs/guides/power-user-guide.md`.

### 4.1 Routing

One-sided file:

```
plug_preset != "Measure my plug"  ->  prefills _eff_* ; sliders ignored.
_eff_plug_thickness >= 24         ->  W-20 tag (the tool still builds).
size != "Custom"  ->  FIT_MEASURED table (fit_measured.scad)
size == "Custom"  ->  custom_* sliders (measurements ignored)
Custom + reset_custom_to_medium -> "Medium Defaults" -> PRESET_MEDIUM
```

Two-sided file:

```
plug_preset == the heavy-duty preset -> _eff_* = 43.8 / 27.0 / 27.0 / 8.2,
                                        _sides_eff = "Flat sides"
plug_preset == "Measure my plug"     -> the sliders; _sides_eff = plug_sides
_attach_zip = true ; _attach_velcro = (attachment == "Zip ties + Velcro strap")
finger bore = finger width (size table or measure_finger_width)
              + FIT_GRIP_CLEARANCE, clamped 15-40;
plate finger hole = finger width + plate_finger_fit
```

`preset_value(p, key, fallback)` returns `PRESET_MEDIUM[key]` for "Medium
Defaults", `fallback` for "Custom", and `FIT_MEASURED[key]` otherwise.

### 4.2 MEDIUM-PARITY INVARIANT

In the one-sided file, with `size = "Medium"`, `plug_preset = "Measure my
plug"`, default measurements (equal prong-end and cord-end values, so the
derived side angle is 0),
every `FIT_MEASURED` value equals `PRESET_MEDIUM` exactly. Pinned by:

1. `tests/test_fit_derivations.py::TestMediumParity` — Python formulas at
   defaults equal the parsed `PRESET_MEDIUM` table.
2. The echo parity test — OpenSCAD's derived values match the Python
   mirror (`tests/fit_formulas.py`).
3. `test_measured_parity_against_medium_fixture` — the "Measure my hand"
   default render is mesh-identical to the `medium` fixture.

**Any change that breaks parity is a bug** unless `PRESET_MEDIUM`,
`fit_measured.scad`, and `tests/fit_formulas.py` change together.

## 5. One-sided puller geometry

### 5.1 Body

`body_octagon_2d()` is an 8-vertex control polygon; `body_outline_2d()`
applies `body_side_rounding` as a morphological opening (bottom-only in
the Medium mode). `plug_puller_body_3d()` extrudes to `body_thickness`
(6.35) with a top-fillet ball roundover. Unchanged from v6.

### 5.2 Plug side rail

`pocket_side_angle` (D-43) defines a rail down the plug's side. The angle
is **derived** from the two Step 1 widths over the plug length —
`atan(((width at the prong end − width at the cord end)/2) / length)`,
clamped to [−15, 25] — so its sign encodes which end of the plug is wider
(negative = wider at the cord end; the pocket walls then widen toward the
cord):

```openscad
function rail_x(t)     = pocket_width / 2 - t * tan(pocket_side_angle);
function rail_point(t) = [rail_x(t), puller_length - t];        // t mm from plug face
function rail_feature_center(t, d) =                            // d mm along outward normal
    [rail_x(t) + d*cos(pocket_side_angle), puller_length - t - d*sin(pocket_side_angle)];
```

- **Pocket walls** follow the rail: `pocket_recess_footprint_2d()` is a
  rounded-nose trapezoid (`_pocket_hw_top` → `_pocket_hw_nose`). At angle 0
  it collapses to the v6-style rounded-nose rectangle of width
  `pocket_width` (Medium parity).
- **Zip stations** (`_zip_centers`): `Auto` reproduces v6-like rows a fixed
  run behind the plug face stepping toward the cord; `Manual` uses
  `zip_pos_1/2/3` (mm along the rail). Each hole sits `zip_edge_offset`
  inward of the pocket wall so the outer side stays clear for the velcro
  wing.
- **Velcro slot** slides along the rail in `Manual` mode
  (`velcro_pos`); `Auto`/Wing keeps the v6 placement.

### 5.3 Dome plug pocket

Two partial-depth recesses cut from the top face: the taper-aware
plug-recess footprint (Section 5.2) and a seat circle centered on the top
edge. Floor parameters are the material left under each recess.

### 5.4 Feature cutouts

Finger holes, J-hook (chiral, `hook_hand`), wall notch, zip-tie holes
(rail-placed, exposed row countersunk), and wing/classic velcro — see the
v6 reference for the unchanged geometry details; only the zip and velcro
*placement* (rail-based) and the pocket *footprint* (taper-aware) changed.

### 5.5 See-through plug (preview only)

`plug_body_1s_3d()` hulls a rounded slice of the prong-end width at the
plug end (Y = `puller_length`) with one of the cord-end width a plug
length back, standing on `pocket_floor`, `_eff_plug_thickness` tall.
`plug_preview_1s()` draws it as `%color("SkyBlue", 0.35)` when
`show_plug_preview` is on (the default). The `%` modifier keeps it out of
every render and export.

## 6. Two-sided puller geometry

Local frame per Section 3.2. Calibrated to the idealized plate
(66.6 × 73.7 × 4.5 mm; see `scripts/measure_clamshell_ideal.py`); the
`plate_*` defaults carry the field-tested "New Heavy Duty Clam T3" grip
profile (2 mm teeth on a 2.8 mm pitch biting 1 mm deep, bite −1, tip
flare 0.7, 11 mm arm tips, 4 mm plate; the serration span is auto = the
full plug body span, `plate_grip_zone_length` overrides). The inner edge
follows the plug's own **two-width profile**: the plug body spans
`[_clam_y_back, _clam_length]` with its prong end at the arm tips. Derived
values (`CLAMSHELL DERIVED VALUES` block; the internal `_clam_*` names
predate the file):

| Value | Formula (≈ HD) | Notes |
|-------|----------------|-------|
| `_clam_finger_dia` | finger width + `plate_finger_fit` (≈21.0) | tracks Size: 17.5 / 21.0 / 24.0 |
| `_clam_cable_gap` | `max(2, _eff_cord_thickness + plate_cable_clearance)` (≈9) | cord channel |
| `_grip_term` | `plate_grip_clearance / 2` with `Rounded sides`, else `plate_grip_bite` | per side, at the mating face |
| `_clam_hw_wall` / `_clam_hw_cable` | `width at the prong end / 2 + _grip_term` (≈12.5) / same at the cord end | half-gaps at the two ends; floored 1 mm outside the cable channel |
| `_cradle_eff` | `Rounded sides`: `max(0, min(plate_cradle_depth, plate_thickness, min(hw_wall, hw_cable) − cable_hw))`; else 0 | the cradle's step-in per side (Section 6.1) |
| `_clam_finger_wall_eff` | `plate_finger_wall + plate_wall_boost` | outer wall around each finger bore |
| `_clam_inner_wall_eff` | `plate_finger_inner_wall + plate_wall_boost` | channel-to-finger web |
| `_clam_slot_in_wall` | `plate_slot_inner_wall + plate_wall_boost + tooth depth` | tooth-ROOT-to-slot wall (teeth scallop into the edge the slot sits behind) |
| `_clam_slot_out_wall` | `2.2 + plate_wall_boost` | slot-to-outer-edge wall |
| `_clam_lobe_r` | bore radius + `_clam_finger_wall_eff` (≈15.5) | goggle lobe, tangent to Y = 0 |
| `_clam_outer_x` | finger lobe + wall (≈33.5) | plate half-width |
| `_clam_length` | `max(manual grip-zone floor, plug_length + 11, _clam_y_back_min + plug_length)` (≈73.8) | arms always cover the full plug |
| `_clam_throat_y0` / `_clam_y_back` | ≈28.0 / `_clam_length − plug_length` (≥ throat + 2, ≈30.0) | channel end → throat ramp → plug back end |
| `_clam_grip_len_eff` / `_clam_grip_y0` | auto: the plug body span / its start | serration span (0 = auto) |
| `_clam_tip_hw` | `_clam_hw_wall + plate_tip_flare/2` (≈12.9) | flared mouth at the tips |
| `_clam_tip_cx/cy/r` | `_clam_tip_hw − _cradle_eff + tip_r` / `_clam_length − tip_r` / `plate_arm_tip_width/2` | rounded arm tip, stepped in by the cradle |
| `_clam_mid_*` | circle concentric with the slot's top cap + `_clam_slot_out_wall` | mid-arm bulge carrying the slot |
| `_clam_half_width` | `max(_clam_outer_x, tip circle, slot bulge)` | the pair's spacing (Section 6.2) |

**`plate_wall_boost` (the strength dial)** adds its value to *every* wall
listed above plus the zip-station webs (rear 2.6/keep 1.6, in-web 2.6,
out-web 2.0, slot-to-zip 2.0), so a single slider densifies the whole
plate: the outline grows outward, the openings shift or shrink, and the
Auto placement keeps every web printable at any boost.
**`plate_slot_inner_wall`** is the user-facing dial for the wall between
the serrated gripping edge and the velcro slot — measured from the
deepest tooth bite, so enlarging the teeth never silently thins it.

`_clam_inner_x(y)` is the piecewise V profile: cable channel to
`_clam_throat_y0`, a throat ramp up to the plug's back end
(`_clam_y_back`), then `_clam_plug_hw(y)` — the plug's own width
interpolated between the two ends plus `_grip_term` — with the tip flare
added from the serration-zone start. The throat position therefore
derives from where the plug actually ends. `_clam_outer_x_at(y)` is the
conservative chord bound of the arm's tapered outer edge, used to cap
hole placement. Zip stations (`_clam_zip_pts`): rear beside the cable
channel (finger-web capped), mid just past the plug's back end, tip
centered in the arm tip. The velcro slot spans the window *between* the
mid and tip stations (2 mm web each) so Auto placement can never
collide. Step 3: zip ties are always on (`_attach_zip = true`;
`_clam_zip_on = plate_zip_hole_diameter > 0`), and the slot requires
`_attach_velcro` as well as a printable slot width; its length is floored
at `strap_width_eff + 1.5` so the strap always threads through. In `Auto`
placement a window shorter than `max(6, strap_width_eff + 1.5)` leaves the
slot out (`_clam_slot_left_out`, with the orange preview note `STRAP SLOT
LEFT OUT - PLUG TOO SHORT FOR ONE`); `Manual` placement keeps it, and
WC-7 / WC-11 flag collisions. Modules:

- `clamshell_v_gap_2d(c = 0)` — the V gap polygon, its plug-zone edge
  stepped in by `c`.
- `clamshell_half_outline_2d()` — one arm; 2D hull of the goggle lobe,
  mid-arm bulge, and rounded tip circle, minus the inner V gap at the outer
  face (narrowed by the cradle); the knee and cord-end corners rounded by
  an opening.
- `clamshell_outline_2d()` — both arms (the full plate footprint).
- `clamshell_serrations_2d(c = 0)` — gripper teeth scalloped into the
  inner edge over the serration zone (auto = the full plug body span;
  teeth ride `_clam_inner_x() − c` so they follow the plug's taper and the
  cradle's slope).
- `clamshell_slot_2d()` — a stadium (velcro / material-reduction slot).
- `two_sided_gap_cutter_3d()` — the cradle cutter (Section 6.1).
- `clamshell_plate_3d()` — extruded outline with an outer-face perimeter
  roundover (`plate_edge_rounding`) + the outer-face cable strip, minus
  rim-filleted finger holes, six zip stations, velcro slots, and the gap
  cutter when `_cradle_eff > 0` (otherwise straight through-cut
  serrations).
- `plug_preview_2s()` — the see-through plug (preview only).
- `two_sided_pair()` — both plates side by side (Section 6.2).

### 6.1 The cradle (`Rounded sides`)

The stacked pair forms a diamond-shaped channel: the gap between the arms
is widest at the mating face (Z = `plate_thickness`) and narrowest at the
outer face (Z = 0), so a round or oval plug rests on four sloped faces and
centers itself. As built:

| # | Feature | As built |
|---|---------|----------|
| 1 | Mating-face gap | half-gap = width/2 + `plate_grip_clearance`/2 per side (default clearance 0.5 mm in total); `Flat sides` and the preset use `+ plate_grip_bite` (−1) instead |
| 2 | Ramped gap cutter | `two_sided_gap_cutter_3d()`: n = `max(6, floor(quality/6))` slices (10 at quality 64); slice i cuts `clamshell_v_gap_2d(c)` (limited to Y past the throat) and `clamshell_serrations_2d(c)` with c = `_cradle_eff × (1 − z_mid/t)`, so the teeth ride the slope; the cable channel and strip are left alone |
| 3 | Arm tips | `_clam_tip_cx` steps in by `_cradle_eff`, so the slope runs to the tips |
| 4 | Depth guard | `_cradle_eff ≤ min(plate_cradle_depth, plate_thickness, min(hw_wall, hw_cable) − cable_hw)`: the outer-face gap may come down to the cord channel's width but never below it |
| 5 | WC-13 | `CRADLE SHALLOWER THAN ASKED - PLUG NARROW` when `_cradle_eff < plate_cradle_depth − 0.01` |
| 6 | See-through plug | `plug_preview_2s()`: a `%` hull of two slices on the mating face, the cord-end width at `_clam_y_back` and the prong-end width at `_clam_length + 2`; an ellipse (`Rounded sides`) or rounded rectangle (`Flat sides`) 0.55 × the width tall; drawn on the pair's left plate |

Defaults: `plate_cradle_depth` 2.5 mm per side [0:0.25:3.5] (the gap
narrows by 5 mm from the mating face to the outer face; about 32° from
vertical at a 4 mm plate) and `plate_grip_clearance` 0.5 mm [0:0.1:2].
The derived-values echo prints `cradle depth per side = …`.

### 6.2 The pair

`two_sided_pair()` places two identical plates at
X = ±(`_clam_half_width` + 4), outer face down, 8 mm apart at their widest
points. `print_layout = Both plates` (the default) exports the pair;
`One plate` exports a single plate. The tool is the two plates: after
printing, flip one over and zip-tie them face to face around the plug.

## 7. CSG order

```
One-sided puller: plug_puller_complete()
└─ difference(body_pocketed, [j_hook, finger_holes, wall_notch, zip_holes, velcro])

Two-sided puller: clamshell_plate_3d()  (× 2 in two_sided_pair())
└─ difference(union(two arms, cable strip),
              [finger holes, zip stations, velcro slots,
               gap cutter (Rounded sides) | serration through-cuts])
```

Boolean epsilon convention: subtractive extrusions extend `eps = 0.01`
beyond the faces they cut.

## 8. Derivation layer (`fit_measured.scad`)

One-sided file only. Inputs: the Step 1 two-station measurements (or the
`plug_preset` prefill via `_eff_*`) + the hand pair from `size` (the
Small / Medium / Large pairs come from `src/fit_sizes.scad`). **D-43**
(`pocket_side_angle` = the derived-and-clamped plug side angle, 0 at
Medium's equal stations). Notch/pocket/seat widths (D-12/D-15/D-16) read
the prong-end station; **D-19** caps the pocket depth at the real budget
left inside the 120 mm body ceiling (`120 − (gap + finger_y + bore/2)`,
≈80 at Medium) so the pocket runs the full plug length instead of half
the body. The two-sided file derives its plate from its own `_eff_*` and
the shared size table; it includes neither `fit_measured.scad` nor
`presets.scad`.

Values snap to 0.05 mm / 0.5°. `tests/fit_formulas.py` mirrors this file
formula-for-formula — **keep them in lock-step**.

### 8.4 Include order

One-sided file:

```openscad
// 1. Customizer block (plug_preset / measure_* / size / …)
include <fit_sizes.scad>      // 2. the Small / Medium / Large table + FIT_GRIP_CLEARANCE
include <fit_measured.scad>   // 3. derives _fit_* and builds FIT_MEASURED
include <presets.scad>        // 4. preset_value() references FIT_MEASURED
// 5. routing block, auto-fit, geometry
```

A static test in `tests/test_preset_routing.py` pins the order. The
two-sided file includes only `fit_sizes.scad`, after its Customizer block.
`scripts/build_flattened.py` inlines the same includes, in the same order,
into each single-file build.

### 8.5 Diagnostics

For every non-Custom size the one-sided file echoes one
`fit_derived: <key>=<value>` line per derived key;
`tests/test_fit_derivations.py` consumes this to assert SCAD ↔ Python
parity. The two-sided file echoes `TOOL: Two-sided puller`, a
`=== Two-sided puller derived values (mm) ===` block (plate length, grip
gap at the prong end and at the cord end, cradle depth per side, cord
channel, finger hole, strap slot or why it was left out, zip stations) and,
with `Both plates`, `PRINT LAYOUT: both plates side by side - flip one after
printing`.

## 9. Render modes

One-sided file:

| Mode | Geometry |
|------|----------|
| `Full` | the tool + warnings (+ the see-through plug in preview) |
| `Body Only` / `Body No Cutouts` | body variants |
| `Only <Feature>` | plain body + one cutout |
| `Cutouts Only 2D` | red 2D overlay of the cutouts + pocket |

Two-sided file:

| Mode | Geometry |
|------|----------|
| `Full` | `print_layout`: `Both plates` → `two_sided_pair()`, `One plate` → one plate; + warnings and the see-through plug |
| `One plate` | one plate + warnings (the golden fixture, most tests and the outline sheets use it) |

## 10. In-model validation warnings

Fail-loudly system: a red bed-level tag past the part end + a console echo;
the part itself is never altered.

- **One-sided puller** — W-1…W-20 (measurement plausibility, finger holes,
  pocket floors, wall notch, cord hook, rail zip grid, wing, plug
  thickness) reading `_eff_*`. W-4 fires only when the pocket was actually
  truncated at the 120 mm body ceiling (`PLUG LONGER THAN POCKET LIMIT -
  POCKET SHORTENED`); W-19 fires when the two width stations describe a
  taper steeper than the rail's [−15, 25] clamp window. W-16…W-18 are
  hole-collision checks: zip vs finger bores, zip rows vs each other, zip
  vs classic velcro slots. In `Auto` placement the zip rows also *derive*
  around the finger keep-out (`_zip_t_max`), compressing the row spacing
  instead of punching into the bores; the warnings then only fire for
  Manual placements. W-20 (`PLUG THICKER THAN 24MM - USE THE TWO-SIDED
  PULLER FILE`) fires in the measured sizes when `_eff_plug_thickness`
  is 24 mm or more.
- **Two-sided puller** — WC-1…WC-13: `CORD TOO THICK FOR CABLE CHANNEL`,
  `PLUG TOO WIDE - ARMS BULGE PAST FINGER LOBES`, `NO GRIP BITE - PLUG
  WONT BE HELD` (WC-3: `Flat sides` or the preset only), `PLATE THINNER
  THAN 2MM - TOO FLIMSY`, `ZIP STATION OFF THE ARM`, `ZIP STATIONS OVERLAP
  EACH OTHER`, `ZIP STATION HITS VELCRO SLOT` (WC-7: Manual placement
  only), `PLUG TOO LONG - PLATE OVER 120MM, CHECK PLUG LENGTH` (the derived
  arm run outgrew a printable plate), `PLUG WIDTH TAPER LOOKS WRONG -
  RECHECK BOTH ENDS` (the ends more than ~20° apart per side), `STEP 3
  DISABLED ZIP HOLES - NOTHING SECURES THE TWO PLATES TOGETHER` (WC-10:
  unreachable from Step 3, which always keeps the zip ties), `STRAP WIDER
  THAN ARM SLOT WINDOW - NARROW THE STRAP` (WC-11: Manual placement only),
  `PLUG NARROWER THAN THE CORD CHANNEL - ARMS CANNOT TOUCH IT` (WC-12: the
  channel floor, not the plug, set a station's gap and the plug is narrower
  than it), and `CRADLE SHALLOWER THAN ASKED - PLUG NARROW` (WC-13, Section
  6.1).

Preview only (`$preview`-gated or `%`, never exported): the see-through
plug in both files; in the one-sided file the green `MEDIUM: …` /
`MEASURED: …` confirmation tag and the orange `CUSTOM SLIDERS IGNORED -
SET SIZE = CUSTOM` and `AUTO-FIT ADJUSTED <n> VALUES - SEE CONSOLE`
notices; in the two-sided file the orange `STRAP SLOT LEFT OUT - PLUG TOO
SHORT FOR ONE` note. MakerWorld renders the final STL only, so none of
these show there; the OpenSCAD Playground shows the tags but not the
see-through plug.

## 11. Source data authority

1. `src/Plug_Puller_Parametric.scad` — the one-sided puller's geometry,
   render dispatch, validation predicates, auto-fit clamps.
2. `src/Plug_Puller_Two_Sided.scad` — the two-sided puller's geometry,
   derived values, cradle, pair layout, render dispatch and validation
   predicates.
3. `src/fit_sizes.scad` — the Small / Medium / Large size table and
   finger clearance, shared by both files.
4. `src/presets.scad` — the PRESET_MEDIUM reference table (one-sided).
5. `src/fit_measured.scad` — derivation formulas (one-sided; mirrored by
   `tests/fit_formulas.py`).
6. `parameter_mapping.json` (79 parameters) and
   `parameter_mapping_two_sided.json` (39 parameters) — the Customizer
   schemas.
7. `plug references/3 Prong Heavy Ideal Sample/…Plug_Bottom.stl` — the
   two-sided plate's calibration target.
8. This document — narrative reference. When it disagrees with the files
   above, the files win.

## 12. Implementation notes

### 12.1 Adding a one-sided cutout

Author `new_feature_2d/3d()`, call it in `plug_puller_cutouts_3d()` behind
an `enable_*` toggle, add the Customizer rows + `preset_value` routing +
`PRESET_MEDIUM` + `FIT_MEASURED` rows + the mirrored `fit_formulas.py`
formula, regenerate `parameter_mapping.json`, and add a `_vw_*` predicate
if it can leave the envelope.

### 12.2 Tuning the two-sided puller

Adjust the `plate_*` Customizer knobs or the `CLAMSHELL DERIVED VALUES`
block in `src/Plug_Puller_Two_Sided.scad`. For a stronger print, raise
`plate_wall_boost` (thickens every wall around the inner openings at once)
and/or `plate_thickness`; for the tooth-to-slot boundary specifically,
raise `plate_slot_inner_wall`; for the cradle, `plate_cradle_depth` and
`plate_grip_clearance`. Re-run `scripts/measure_clamshell_ideal.py`
against the reference plate to re-check calibration, then
`tests/test_two_sided_parity.py`, `tests/test_clamshell_parity.py` and
`tests/test_two_sided_cradle.py`.

### 12.3 Print orientation

- One-sided puller: flat bottom face on the bed, pocket up, no supports.
- Two-sided puller: both plates lie flat on their outer faces as exported;
  flip one after printing and zip-tie the pair face to face.

### 12.4 Safety rule

The tool touches only the plug's sides and back — never between the plug
face and the wall. A zip tie through the holes provides form closure; a
compliant liner raises friction on smooth round cords.
