# Plug Puller 0.8 — Complete Object Reference

> **Version**: 0.8 (unified two-tool model: rail flat tool + heavy-duty clamshell)
> **File**: `src/Plug_Puller_Parametric.scad` (`include`s
> `src/fit_measured.scad` then `src/presets.scad` — order matters,
> see [Section 8.4](#84-include-order))
> **Root entry point**: `Plug_Puller.scad` (thin wrapper)
> **Flat-tool heritage**: `v6.0/CAD/v6.0.stl` ("Plug Puller 3.1 - B")
> **Clamshell reference**: `plug references/3 Prong Heavy Ideal Sample/…Plug_Bottom.stl`
> **Last Updated**: 2026-07-12
> **Purpose**: Authoritative reference for the 0.8 geometry (both tools),
> parameters, sizes, the measurement derivation layer, CSG construction,
> render modes, in-model validation warnings, and the parity story.
> Intended for AI models and human engineers modifying, debugging, or
> extending the design.

For the parameter min/max/step/type schema and validator, see
[`parameter_mapping.json`](../parameter_mapping.json) (103 rows).

---

## 1. Object purpose and physical context

The Plug Puller is a handheld assistive device that helps users grip and
remove electrical plugs from wall outlets. **The model unifies two tools** behind
the Step 0 `tool_style` selector:

- **Flat tool** — the single flat printed piece carried over and reworked
  from v6: finger holes, a chiral cord J-hook, a plug wall notch, a dome
  plug pocket, a zip-tie grid, and wing/classic velcro slots. New in 0.8,
  the pocket walls and the zip/velcro placement follow a **plug side rail**
  (Section 5.2) so a single taper dial slides them along the plug's side.
- **Heavy-duty clamshell** — a pair of identical serrated collar plates
  that sandwich a fat extension-cord plug and zip-tie together, with the
  cord exiting a narrow channel and the user pulling from finger lobes at
  the cord end (Section 6).

`Auto from plug` builds the clamshell for thick plugs and the flat tool
otherwise; an explicit `tool_style` choice always wins.

## 2. The references and the Medium size

**The Medium flat tool descends from the v6 CAD reference** but 0.8 no
longer clones it at the mesh level: the pocket is re-derived as a
taper-aware rounded trapezoid and the zip/velcro features hang off the
plug rail, so the placement grid moves intentionally. The parity story is
now:

1. **Self-consistency** — with `size = Medium`, `plug_preset = "Measure my
   plug"`, and default measurements, every `FIT_MEASURED` value equals
   `PRESET_MEDIUM` exactly (Section 4.2).
2. **Golden-fixture parity** — `tests/test_render_modes.py` renders each
   fixture and asserts mesh parity with the committed `reference.stl`.
3. **Clamshell parity** — `tests/test_clamshell_parity.py` asserts loose
   envelope + feature-inventory + grip-gap parity against the idealized
   heavy-duty plate.

The v6-CAD feature-by-feature parity suite (`test_reference_parity.py`)
was **retired**: 0.8 re-parametrises the pocket and rail placement on
purpose.

### 2.1 Plug presets (two-station, re-measured)

`plug_preset` prefills the effective plug measurements (`_eff_*`) from
two-station measurements of the three reference plugs
(`scripts/measure_plug_references.py`: length = the molded body only,
wall station just behind the prong face, cable station at the cord end
of the gripped body — the heavy-duty plug's narrower strain-relief boot
is skipped); the manual sliders are ignored unless
`plug_preset = "Measure my plug"`:

| Preset | length | width wall/cable | thickness wall/cable | cord |
|--------|--------|------------------|----------------------|------|
| Flat 2-prong lamp plug - NEMA 1-15 | 37.0 | 25.0 / 11.2 | 18.6 / 8.6 | 3.6 |
| Standard 3-prong plug - NEMA 5-15 | 46.2 | 26.6 / 13.4 | 18.9 / 15.0 | 7.0 |
| Heavy-duty extension cord - NEMA 5-15 | 43.8 | 25.8 / 21.9 | **27.0** / 27.0 | 8.2 |

The heavy-duty preset's 27 mm thickness trips `Auto` into the clamshell
(`_eff_plug_thickness` = the fatter station).

## 3. Coordinate systems

### 3.1 Flat tool

| Axis | Direction | Zero | Positive |
|------|-----------|------|----------|
| **X** | Horizontal | Midline | Right |
| **Y** | Along body length | Cord / hook end | Toward plug end |
| **Z** | Slab thickness | Print bed | Away from bed |

Symmetric about X = 0 except the chiral J-hook.

### 3.2 Clamshell plate (local frame)

| Axis | Direction | Zero | Positive |
|------|-----------|------|----------|
| **X** | Across the plate | Midline (mirrored arms) | Right |
| **Y** | Along the arms | Cord end | Toward the plug/arm tip |
| **Z** | Plate thickness | Outer face | Plug-contact face |

## 4. Customizer architecture (0.8)

File order = UI order, organized in three audience tiers: the numbered
Steps (beginner path), the `Advanced -` sections (power users), and the
`(Custom size only)` sections (experts, active only in `size = Custom`).

```
── Beginner tier ──────────────────────────────────────────────────────
/* [Step 0 - Tool Style] */    tool_style = Auto from plug | Flat tool |
                               Heavy-duty clamshell
/* [Step 1 - Your Plug] */     plug_preset, measure_plug_length,
                               measure_plug_width_wall/_cable,
                               measure_plug_thickness_wall/_cable,
                               measure_cord_thickness, measure_wall_plate_style
/* [Step 2 - Size] */          size = Small | Medium | Large |
                               Measure my hand | Custom + hand sliders
/* [Step 3 - Attachment] */    attachment, velcro_style, strap_width
/* [Step 4 - Cord Hook] */     hook_hand
── Advanced tier ──────────────────────────────────────────────────────
/* [Advanced - Zip Tie Placement - Flat Tool] */  zip_placement dials
/* [Advanced - Velcro Placement - Flat Tool] */   velcro_placement dials
/* [Advanced - Heavy Duty Clamshell] */           clam_* tuning knobs
                                                  (clam_wall_boost leads)
/* [Advanced - Render Quality] */                 quality
/* [Hidden] */                 render_mode, eps, _pp_active (routing)
── Custom / expert tier ───────────────────────────────────────────────
/* [Custom Mode] + [Body Shape (Custom size only)] etc. */ custom_* sliders
```

The beginner-facing walkthrough is `docs/guides/quick-start-beginner.md`;
the Advanced/Custom tiers are documented for users in
`docs/guides/power-user-guide.md`.

### 4.1 Routing

```
tool_style == "Auto from plug"  ->  clamshell if _eff_plug_thickness >= 24,
                                    else flat tool. Explicit choice wins.
plug_preset != "Measure my plug"  ->  prefills _eff_* ; sliders ignored.
size != "Custom"  ->  FIT_MEASURED table (fit_measured.scad)
size == "Custom"  ->  custom_* sliders (measurements ignored)
Custom + reset_custom_to_medium -> "Medium Defaults" -> PRESET_MEDIUM
```

`preset_value(p, key, fallback)` returns `PRESET_MEDIUM[key]` for "Medium
Defaults", `fallback` for "Custom", and `FIT_MEASURED[key]` otherwise.

### 4.2 MEDIUM-PARITY INVARIANT

With `size = "Medium"`, `plug_preset = "Measure my plug"`, default
measurements (equal wall/cable stations, so the derived side angle is 0),
every `FIT_MEASURED` value equals `PRESET_MEDIUM` exactly. Pinned by:

1. `tests/test_fit_derivations.py::TestMediumParity` — Python formulas at
   defaults equal the parsed `PRESET_MEDIUM` table.
2. The echo parity test — OpenSCAD's derived values match the Python
   mirror (`tests/fit_formulas.py`).
3. `test_measured_parity_against_medium_fixture` — the "Measure my hand"
   default render is mesh-identical to the `medium` fixture.

**Any change that breaks parity is a bug** unless `PRESET_MEDIUM`,
`fit_measured.scad`, and `tests/fit_formulas.py` change together.

## 5. Flat-tool geometry

### 5.1 Body

`body_octagon_2d()` is an 8-vertex control polygon; `body_outline_2d()`
applies `body_side_rounding` as a morphological opening (bottom-only in
the Medium mode). `plug_puller_body_3d()` extrudes to `body_thickness`
(6.35) with a top-fillet ball roundover. Unchanged from v6.

### 5.2 Plug side rail (new in 0.8)

`pocket_side_angle` (D-43) defines a rail down the plug's side. The angle
is **derived** from the two Step 1 width stations over the plug length —
`atan(((width_wall − width_cable)/2) / length)`, clamped to [−15, 25] —
so its sign encodes which end of the plug is wider (negative = wider at
the cable end; the pocket walls then widen toward the cord):

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
v6 reference for the unchanged geometry details; 0.8 only changes zip and
velcro *placement* (rail-based) and the pocket *footprint* (taper-aware).

## 6. Clamshell geometry

Local frame per Section 3.2. Calibrated to the idealized plate
(66.6 × 73.7 × 4.5 mm; see `scripts/measure_clamshell_ideal.py`); the
`clam_*` defaults carry the field-tested "New Heavy Duty Clam T3" grip
profile (2 mm teeth on a 2.8 mm pitch biting 1 mm deep, bite −1, tip
flare 0.7, 11 mm arm tips, 4 mm plate; the serration span is auto =
the full plug body span, `clam_grip_zone_length` overrides). The inner
edge follows the plug's own **two-station thickness profile**: the plug
body spans `[_clam_y_back, _clam_length]` with its wall face at the arm
tips. Derived values (`CLAMSHELL DERIVED VALUES` block):

| Value | Formula (≈ HD) | Notes |
|-------|----------------|-------|
| `_clam_finger_dia` | `finger_hole_diameter - FIT_GRIP_CLEARANCE + clam_finger_fit` (≈21.0) | tracks Size |
| `_clam_cable_gap` | `_eff_cord_thickness + clam_cable_clearance` (≈9) | cord channel |
| `_clam_hw_wall` / `_clam_hw_cable` | `_eff_plug_thickness_wall/2 + clam_grip_bite` (≈12.5) / same for the cable station | plug-profile half-gaps at the two stations; floored 1 mm outside the cable channel |
| `_clam_finger_wall_eff` | `clam_finger_wall + clam_wall_boost` | outer wall around each finger bore |
| `_clam_inner_wall_eff` | `clam_finger_inner_wall + clam_wall_boost` | channel-to-finger web |
| `_clam_slot_in_wall` | `clam_slot_inner_wall + clam_wall_boost + tooth depth` | tooth-ROOT-to-slot wall (teeth scallop into the edge the slot sits behind) |
| `_clam_slot_out_wall` | `2.2 + clam_wall_boost` | slot-to-outer-edge wall |
| `_clam_lobe_r` | bore radius + `_clam_finger_wall_eff` (≈15.5) | goggle lobe, tangent to Y = 0 |
| `_clam_outer_x` | finger lobe + wall (≈33.5) | plate half-width |
| `_clam_length` | `max(manual grip-zone floor, plug_length + 11, _clam_y_back_min + plug_length)` (≈73.8) | arms always cover the full plug |
| `_clam_throat_y0` / `_clam_y_back` | ≈28.0 / `_clam_length − plug_length` (≥ throat + 2, ≈30.0) | channel end → throat ramp → plug back end |
| `_clam_grip_len_eff` / `_clam_grip_y0` | auto: the plug body span / its start | serration span (0 = auto) |
| `_clam_tip_hw` | `_clam_hw_wall + clam_tip_flare/2` (≈12.9) | flared mouth at the tips |
| `_clam_tip_cx/cy/r` | tip circle hugging the flared inner edge | rounded arm tip (`clam_arm_tip_width`) |
| `_clam_mid_*` | circle concentric with the slot's top cap + `_clam_slot_out_wall` | mid-arm bulge carrying the slot |

**`clam_wall_boost` (the strength dial)** adds its value to *every* wall
listed above plus the zip-station webs (rear 2.6/keep 1.6, in-web 2.6,
out-web 2.0, slot-to-zip 2.0), so a single slider densifies the whole
plate: the outline grows outward, the openings shift or shrink, and the
Auto placement keeps every web printable at any boost.
**`clam_slot_inner_wall`** is the user-facing dial for the wall between
the serrated gripping edge and the velcro slot — measured from the
deepest tooth bite, so enlarging the teeth never silently thins it.

`_clam_inner_x(y)` is the piecewise V profile: cable channel to
`_clam_throat_y0`, a throat ramp up to the plug's back end
(`_clam_y_back`), then `_clam_plug_hw(y)` — the plug's own thickness
interpolated between the two stations plus the bite — with the tip flare
added from the serration-zone start. The throat position therefore
derives from where the plug actually ends. `_clam_outer_x_at(y)` is the
conservative chord bound of the arm's tapered outer edge, used to cap
hole placement. Zip stations (`_clam_zip_pts`): rear beside the cable
channel (finger-web capped), mid just past the plug's back end, tip
centered in the arm tip. The velcro slot spans the window *between* the
mid and tip stations (2 mm web each) so Auto placement can never
collide. Modules:

- `clamshell_half_outline_2d()` — one arm; 2D hull of the goggle lobe,
  mid-arm bulge, and rounded tip circle, minus the inner V gap; the knee
  and cord-end corners rounded by an opening.
- `clamshell_outline_2d()` — both arms (the full plate footprint).
- `clamshell_serrations_2d()` — gripper teeth scalloped into the inner
  edge over the serration zone (auto = the full plug body span; teeth
  ride `_clam_inner_x()` so they follow the plug's taper).
- `clamshell_slot_2d()` — a stadium (velcro / material-reduction slot).
- `clamshell_plate_3d()` — extruded outline with an outer-face perimeter
  roundover (`clam_edge_rounding`) + the outer-face cable strip, minus
  rim-filleted finger holes, six zip stations, velcro slots, and
  serrations.

The tool is TWO printed copies of this one plate: print it twice, flip one
over, and zip-tie them face to face around the plug. (There is no doubled
render output — the old `clamshell_layout` / `Clamshell Pair` mode was
removed.)

## 7. CSG order

```
Flat tool: plug_puller_complete()
└─ difference(body_pocketed, [j_hook, finger_holes, wall_notch, zip_holes, velcro])

Clamshell: clamshell_plate_3d()
└─ difference(union(two arms, cable strip),
              [finger holes, zip stations, velcro slots, serrations])
```

Boolean epsilon convention: subtractive extrusions extend `eps = 0.01`
beyond the faces they cut.

## 8. Derivation layer (`fit_measured.scad`)

Inputs: the Step 1 two-station measurements (or the `plug_preset` prefill
via `_eff_*`) + the hand pair from `size`. 0.8 adds **D-43**
(`pocket_side_angle` = the derived-and-clamped plug side angle, 0 at
Medium's equal stations). Notch/pocket/seat widths (D-12/D-15/D-16) read
the WALL station; **D-19** caps the pocket depth at the real budget left
inside the 120 mm body ceiling (`120 − (gap + finger_y + bore/2)`, ≈80 at
Medium) so the pocket runs the full plug length instead of half the body.
Clamshell dimensions are derived directly from `_eff_*` in the main file
(no new routed preset keys), so `PRESET_MEDIUM` / `FIT_MEASURED` gain
only `pocket_side_angle`.

Values snap to 0.05 mm / 0.5°. `tests/fit_formulas.py` mirrors this file
formula-for-formula — **keep them in lock-step**.

### 8.4 Include order

```openscad
// 1. Customizer block (tool_style / plug_preset / measure_* / size / …)
include <fit_measured.scad>   // 2. derives _fit_* and builds FIT_MEASURED
include <presets.scad>        // 3. preset_value() references FIT_MEASURED
// 4. routing block, auto-fit, geometry (flat tool + clamshell)
```

A static test in `tests/test_preset_routing.py` pins the order.

### 8.5 Diagnostics

For every non-Custom size the file echoes one `fit_derived: <key>=<value>`
line per derived key; `tests/test_fit_derivations.py` consumes this to
assert SCAD ↔ Python parity.

## 9. Render modes

| Mode | Geometry |
|------|----------|
| `Full` | clamshell plate if `tool_style` resolves to it, else flat tool + warnings |
| `Clamshell Plate` | the clamshell plate + clamshell warnings |
| `Body Only` / `Body No Cutouts` | flat-tool body variants |
| `Only <Feature>` | flat body + one cutout |
| `Cutouts Only 2D` | red 2D overlay of the flat-tool cutouts + pocket |

## 10. In-model validation warnings

Fail-loudly system: a red bed-level tag past the part end + a console echo;
the part itself is never altered.

- **Flat tool** — W-1…W-19 (measurement plausibility, finger holes, pocket
  floors, wall notch, cord hook, rail zip grid, wing) reading `_eff_*`.
  W-4 now fires only when the pocket was actually truncated at the 120 mm
  body ceiling (`PLUG LONGER THAN POCKET LIMIT`); W-19 fires when the two
  width stations describe a taper steeper than the rail's [−15, 25] clamp
  window. W-16…W-18 are hole-collision checks: zip vs finger bores, zip
  rows vs each other, zip vs classic velcro slots. In `Auto` placement the
  zip rows also *derive* around the finger keep-out (`_zip_t_max`),
  compressing the row spacing instead of punching into the bores; the
  warnings then only fire for Manual placements.
- **Clamshell** — WC-1…WC-9: `CORD TOO THICK FOR CABLE CHANNEL`, `PLUG TOO
  THICK - ARMS BULGE PAST FINGER LOBES`, `NO GRIP BITE - PLUG WONT BE
  HELD`, `PLATE THINNER THAN 2MM - TOO FLIMSY`, `ZIP STATION OFF THE ARM`,
  `ZIP STATIONS OVERLAP EACH OTHER`, `ZIP STATION HITS VELCRO SLOT`,
  `PLUG TOO LONG - PLATE OVER 120MM` (the derived arm run outgrew a
  printable plate), `PLUG THICKNESS TAPER LOOKS WRONG` (stations more
  than ~20° apart per side).

## 11. Source data authority

1. `src/Plug_Puller_Parametric.scad` — feature geometry (both
   tools), render dispatch, validation predicates, auto-fit clamps,
   clamshell derived values.
2. `src/presets.scad` — the PRESET_MEDIUM reference table.
3. `src/fit_measured.scad` — derivation formulas (mirrored by
   `tests/fit_formulas.py`).
4. `parameter_mapping.json` — Customizer schema (103 parameters).
5. `plug references/3 Prong Heavy Ideal Sample/…Plug_Bottom.stl` — the
   clamshell calibration target.
6. This document — narrative reference. When it disagrees with the files
   above, the files win.

## 12. Implementation notes

### 12.1 Adding a flat-tool cutout

Author `new_feature_2d/3d()`, call it in `plug_puller_cutouts_3d()` behind
an `enable_*` toggle, add the Customizer rows + `preset_value` routing +
`PRESET_MEDIUM` + `FIT_MEASURED` rows + the mirrored `fit_formulas.py`
formula, regenerate `parameter_mapping.json`, and add a `_vw_*` predicate
if it can leave the envelope.

### 12.2 Tuning the clamshell

Adjust the `clam_*` Customizer knobs or the `CLAMSHELL DERIVED VALUES`
block. For a stronger print, raise `clam_wall_boost` (thickens every wall
around the inner openings at once) and/or `clam_plate_thickness`; for the
tooth-to-slot boundary specifically, raise `clam_slot_inner_wall`. Re-run
`scripts/measure_clamshell_ideal.py` against the reference plate to
re-check calibration, then `tests/test_clamshell_parity.py`.

### 12.3 Print orientation

- Flat tool: flat bottom face on the bed, pocket up, no supports.
- Clamshell: plates lie flat, print two, flip one, zip-tie face to face.

### 12.4 Safety rule

The tool touches only the plug's sides and back — never between the plug
face and the wall. A zip tie through the holes provides form closure; a
compliant liner raises friction on smooth round cords.
