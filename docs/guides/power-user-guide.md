# Power User Guide — The Advanced and Custom Tiers

This guide is for experienced makers, occupational therapists tuning fits
for clients, and engineers who want every dial the model offers. It
assumes you already know the basic flow (open the file for your tool,
fill in Steps 1–4, F6, export) — if not, start with the
[Quick Start for Beginners](quick-start-beginner.md).

The Plug Puller is two tools in two files: the **one-sided puller**,
[`src/Plug_Puller_Parametric.scad`](../../src/Plug_Puller_Parametric.scad),
and the **two-sided puller**,
[`src/Plug_Puller_Two_Sided.scad`](../../src/Plug_Puller_Two_Sided.scad).
Each Customizer is organized in tiers, top to bottom:

| Tier | Sections | Who it's for |
| ---- | -------- | ------------ |
| **Guided steps** | `Step 1` … `Step 4` in both files | Everyone. Measurements + a few dropdowns; the model derives all geometry from these. |
| **Advanced** | One-sided: `Advanced - Zip Tie Placement`, `Advanced - Velcro Placement`, `Advanced - Render Quality`. Two-sided: `Advanced - Two-Sided Puller`, `Advanced - Render Quality` | Power users. Placement overrides and tuning dials that work *with* the measured sizes — no mode switch needed. |
| **Custom** (one-sided only) | `Custom Mode` + every section marked `(Custom size only)` | Experts. Set Step 2's `size = Custom` and the measurements are ignored entirely; ~50 sliders control the raw geometry. |

Everything in the Advanced tier applies immediately, in any size. The
Custom tier is inert until `size = Custom` — if you move one of those
sliders in a measured size, the preview shows an orange
`CUSTOM SLIDERS IGNORED` tag and the console names each ignored slider.

---

## 1. Workflow tools

### Saved parameter sets

The Customizer panel has a preset bar above the sections: **+** saves
your current values as a named set inside a JSON next to the `.scad`
file. Ship-with examples live in
[`presets/Plug_Puller_Parametric.json`](../../presets/Plug_Puller_Parametric.json)
(one-sided) and
[`presets/Plug_Puller_Two_Sided.json`](../../presets/Plug_Puller_Two_Sided.json)
(two-sided). Sets are plain JSON — versionable, diffable, and shareable.

### Command-line batch export

Every parameter can be overridden from the CLI, which makes A/B testing
and batch generation scriptable:

```bash
# Render the two-sided puller (both plates) with a 2 mm strength boost
openscad -o plates.stl --backend Manifold \
  -D 'plug_preset="Heavy-duty extension cord - NEMA 5-15"' \
  -D plate_wall_boost=2 \
  src/Plug_Puller_Two_Sided.scad

# Apply a saved parameter set
openscad -o out.stl -p presets/Plug_Puller_Parametric.json \
  -P "Left-handed + classic velcro slots" \
  src/Plug_Puller_Parametric.scad
```

### The hidden `render_mode` switch

`render_mode` lives under `/* [Hidden] */` (set it via `-D` or by
editing the declaration) and renders geometry subsets — useful for
debugging a single feature or documenting a change. In the one-sided
file:

| Value | Renders |
| ----- | ------- |
| `Full` (default) | The tool + warning tags |
| `Body Only` / `Body No Cutouts` | Body variants |
| `Only Finger Holes` / `Only T Hook` / `Only Plug Wall Notch` / `Only Zip Tie Holes` / `Only Velcro Strap Holes` | Plain body + one cutout |
| `Cutouts Only 2D` | A flat 2D overlay of every cutout + pocket profile |

In the two-sided file, `Full` (default) builds what Step 4's
`print_layout` picks, and `One plate` always builds a single plate (the
golden fixture, most tests and the outline sheets use it).

### Console diagnostics

Every one-sided render echoes a **Final Adapted Dimensions** block:
each derived value, with `(clamped from <your value>)` appended wherever
auto-fit had to adjust an input. Non-Custom sizes also echo one
`fit_derived: <key>=<value>` line per derivation, which is what the CI
parity tests consume.

The two-sided file echoes `=== Two-sided puller derived values (mm) ===`:
the plate length, the grip gap at the prong end and at the cord end, the
cradle depth per side, the cord channel, the finger hole, the strap
slot (or why it was left out) and the zip stations, then the
`PRINT LAYOUT` line.

---

## 2. One-sided puller power dials

### The plug side rail

One concept powers the one-sided puller's Advanced tier: a 2D **rail** that
runs down the plug's side, starting at the pocket edge on the plug face
and sloping by the plug's side-taper angle. The angle is **derived from
the two Step 1 width stations** over the plug length (in Custom mode
`custom_pocket_side_angle` sets it directly), so its sign encodes the
taper direction: a plug that is wider at the cord end gives a negative
angle and the pocket walls widen toward the cord. The pocket walls, the
zip-tie stations, and the manual velcro slots all hang off this rail, so
their positions are measured in **mm along the plug's side, from the
plug face toward the cord** — the taper moves everything coherently.

### Zip-tie placement (`Advanced - Zip Tie Placement`)

- `zip_placement = Auto` spaces `zip_row_count` (1–3) hole pairs along
  the rail and automatically compresses the spacing rather than letting
  a row punch into the finger holes.
- `Manual` places each pair with `zip_pos_1/2/3` (mm along the rail).
  Manual placements are *not* collision-protected — the red warning tags
  (`ZIP TIE HOLES HIT FINGER HOLES`, `…OVERLAP EACH OTHER`,
  `…HIT VELCRO SLOTS`) fire if you overlap something.
- `zip_edge_offset` slides the whole column toward/away from the pocket
  wall.

### Velcro placement (`Advanced - Velcro Placement`)

`velcro_placement = Manual` slides a pair of classic slots along the
rail with `velcro_pos`. The `Wing` style ignores manual placement (its
opening is derived from the body's dead space); switch
`velcro_style = Classic slot` in Step 3 to use it.

---

## 3. Two-sided puller tuning (`Advanced - Two-Sided Puller`)

The two-sided puller derives its core dimensions from its Step 1
measurements: the arm's gripping edge follows the plug's own
**two-width profile** (the prong-end width at the arm tips, the
cord-end width at the plug's back end, interpolated in between), the
arm length grows so the arms always cover the full plug length, the
throat — where the V closes down to the cord channel — sits just below
the plug's back end, the cord channel comes from the cord thickness,
and the finger holes from the Step 2 size. The `plate_*` dials tune
that result. The defaults carry the field-tested **T3 grip profile**
(2 mm teeth, 2.8 mm pitch, 1 mm bite, grip bite −1) with the serration
span on auto.

Step 3's `attachment` offers `Zip ties + Velcro strap` (default) and
`Zip ties`: the 3 zip-tie stations per arm are always there, because
the ties are what cinch the two plates together, and the strap slot in
each arm comes with the velcro choice (`plate_zip_hole_diameter` and
`plate_velcro_slot_width` stay the sizing dials — 0 still disables the
feature). `strap_width` floors the arm slot's length so the strap
always threads through. In `Auto` placement a plug too short for a slot
gets none, with the orange preview note
`STRAP SLOT LEFT OUT - PLUG TOO SHORT FOR ONE`.

### Rounded or flat sides: the cradle

Step 1's `plug_sides` picks how the arms meet the plug. `Rounded sides`
(the default) builds a sloped **cradle**: the gap between the arms is
narrower at each plate's outer face than where the plates meet, by
`plate_cradle_depth` per side (2.5 mm by default, so the gap narrows by
5 mm), and `plate_grip_clearance` (0.5 mm) is the total extra room where
the plates meet, so a hard plug drops in flat and the cradle does the
holding. Stacked face to face, the two plates form a diamond-shaped
channel that centers a round plug, a USB-C or charger tip. The teeth
follow the slope, and the arm tips step in to carry it.

The cradle never makes the outer-face gap narrower than the cord
channel. When a narrow plug would need that, the file builds a
shallower cradle and shows `CRADLE SHALLOWER THAN ASKED - PLUG NARROW`;
a smaller `plate_cradle_depth`, or measuring the cord itself rather
than its strain relief, clears it.

`Flat sides` keeps the straight toothed edge, and there
`plate_grip_bite` sets the squeeze. `plate_cradle_depth` and
`plate_grip_clearance` apply to Rounded sides only; `plate_grip_bite`
applies to Flat sides and the plug preset only (the preset carries its
own tested grip and ignores `plug_sides`).

### Print layout and the pair

Step 4's `print_layout` is `Both plates` by default: the two identical
plates side by side in one file, spaced by the plate's widest point
plus 4 mm, so one export prints the whole tool. `One plate` exports a
single plate. Either way, flip one plate over after printing and
zip-tie the pair face to face around the plug.

### Strength recipes

| Goal | Dial(s) |
| ---- | ------- |
| **Denser, stronger plate all around** | `plate_wall_boost` — adds N mm to *every* wall around the inner openings at once (finger walls, cord-channel web, both velcro-slot walls, zip webs). The outline grows and the holes re-place themselves; Auto placement keeps every web intact at any boost. |
| Stiffer sandwich | `plate_thickness` (each plate; the stack is 2×) |
| Beef up only the tooth-to-slot boundary | `plate_slot_inner_wall` — measured from the **deepest tooth bite**, so bigger teeth never silently thin it |
| Less plastic / lighter | `plate_velcro_slot_width/length` (the slots double as material reduction), `plate_strip_thickness = 0` |

### Grip tuning

| Goal | Dial(s) |
| ---- | ------- |
| Steeper or gentler cradle (Rounded sides) | `plate_cradle_depth` (per side; 0 = straight edge) |
| More or less room where the plates meet (Rounded sides) | `plate_grip_clearance` (total, not per side) |
| Squeeze harder / looser (Flat sides and the preset) | `plate_grip_bite` (negative = interference squeeze; applied per side on top of the plug's own width profile) |
| Teeth that bite soft plug bodies | `plate_tooth_diameter`, `plate_tooth_pitch`, `plate_tooth_depth` |
| Where the teeth sit | `plate_grip_zone_start` / `plate_grip_zone_length` (measured back from the arm tips; length 0 = auto — the teeth cover the full plug body span) |
| Easier plug entry | `plate_tip_flare` (opens the V at the tips) |
| Cord slides freely | `plate_cable_clearance` |
| Finger security | `plate_finger_fit` (hole = finger width + this) |

Manual zip placement (`plate_zip_placement = Manual` +
`plate_zip_pos_1/2/3`) trades the collision guarantees for full control;
the `WC-*` warning tags call out stations that fall off the arm, overlap
each other, or break into the velcro slot.

---

## 4. Custom mode — the full unlock

In the one-sided file, set **Step 2 `size = Custom`** and the
measurement/derivation layer switches off: every slider in the
`(Custom size only)` sections drives the one-sided puller's geometry
directly (body octagon, pocket, finger holes, J-hook, notch, zip grid,
velcro, edge rounding). The two-sided file has no Custom size.

- **`reset_custom_to_medium`** — render once with this on to snap the
  output back to the Medium reference geometry (a known-good baseline),
  then turn it off and diverge.
- **`custom_enable_auto_fit`** — on (default), every slider is clamped
  so features stay inside the body with printable webs; each clamp is
  echoed as `(clamped from …)` and the preview shows an
  `AUTO-FIT ADJUSTED N VALUES` notice. Off = raw values, no protection;
  the warning tags become your only guard rail.
- The Step 3/4 dropdowns (attachment, velcro style, strap width, hook
  hand) remain authoritative even in Custom.

The full slider matrix — names, types, ranges, steps, defaults — is the
machine-readable schema
[`parameter_mapping.json`](../../parameter_mapping.json)
(79 parameters) and, for the two-sided file,
[`parameter_mapping_two_sided.json`](../../parameter_mapping_two_sided.json)
(39 parameters), both CI-validated against the SCAD.

---

## 5. Guard rails and how to read them

The model never silently "fixes" your input past what auto-fit reports.
Anything genuinely wrong prints a **red warning tag** flat on the bed
next to the part (so an exported file physically shows its own defect)
and echoes the same message to the console. The
[Fit Troubleshooting guide](fit-troubleshooting.md) decodes every tag —
one-sided tags `W-1…W-20`, two-sided tags `WC-1…WC-13`.

Preview-only (never exported): the see-through plug in both files, the
green `MEDIUM: …` / `MEASURED: …` confirmation tag and the orange HUD
notices for ignored custom sliders and auto-fit clamps in the one-sided
file, and the orange `STRAP SLOT LEFT OUT - PLUG TOO SHORT FOR ONE`
note in the two-sided file.

---

## 6. Going deeper

| Resource | What's in it |
| -------- | ------------ |
| [`docs/Plug_Puller_Reference.md`](../../docs/Plug_Puller_Reference.md) | The engineering reference: coordinate frames, the rail math, the two-sided plate's derived values, CSG order, derivation layer, parity invariants |
| [`parameter_mapping.json`](../../parameter_mapping.json) / [`parameter_mapping_two_sided.json`](../../parameter_mapping_two_sided.json) | Machine-readable Customizer schemas, one per file (source of truth for the validator) |

License: PolyForm Noncommercial 1.0.0
