# Power User Guide — The Advanced and Custom Tiers

This guide is for experienced makers, occupational therapists tuning fits
for clients, and engineers who want every dial the model offers. It
assumes you already know the basic flow (open the file, fill in Steps
0–4, F6, export) — if not, start with the
[Quick Start for Beginners](quick-start-beginner.md).

The Customizer is organized in **three tiers**, top to bottom:

| Tier | Sections | Who it's for |
| ---- | -------- | ------------ |
| **Guided steps** | `Step 0` … `Step 4` | Everyone. Measurements + four dropdowns; the model derives all geometry from these. |
| **Advanced** | `Advanced - Zip Tie Placement - Flat Tool`, `Advanced - Velcro Placement - Flat Tool`, `Advanced - Heavy Duty Clamshell`, `Advanced - Render Quality` | Power users. Placement overrides and tuning dials that work *with* the measured sizes — no mode switch needed. |
| **Custom** | `Custom Mode` + every section marked `(Custom size only)` | Experts. Set Step 2's `size = Custom` and the measurements are ignored entirely; ~50 sliders control the raw geometry. |

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
[`presets/Plug_Puller_Parametric.json`](../../presets/Plug_Puller_Parametric.json).
Sets are plain JSON — versionable, diffable, and shareable.

### Command-line batch export

Every parameter can be overridden from the CLI, which makes A/B testing
and batch generation scriptable:

```bash
# Render the heavy-duty clamshell plate with a 2 mm strength boost
openscad -o plate.stl --backend Manifold \
  -D 'plug_preset="Heavy-duty extension cord - NEMA 5-15"' \
  -D 'render_mode="Clamshell Plate"' \
  -D clam_wall_boost=2 \
  src/Plug_Puller_Parametric.scad

# Apply a saved parameter set
openscad -o out.stl -p presets/Plug_Puller_Parametric.json \
  -P "Left-handed + classic velcro slots" \
  src/Plug_Puller_Parametric.scad
```

### The hidden `render_mode` switch

`render_mode` lives under `/* [Hidden] */` (set it via `-D` or by
editing the declaration) and renders geometry subsets — useful for
debugging a single feature or documenting a change:

| Value | Renders |
| ----- | ------- |
| `Full` (default) | The resolved tool + warning tags |
| `Clamshell Plate` | The heavy-duty plate regardless of `tool_style` |
| `Body Only` / `Body No Cutouts` | Flat-tool body variants |
| `Only Finger Holes` / `Only T Hook` / `Only Plug Wall Notch` / `Only Zip Tie Holes` / `Only Velcro Strap Holes` | Flat body + one cutout |
| `Cutouts Only 2D` | A flat 2D overlay of every cutout + pocket profile |

### Console diagnostics

Every render echoes a **Final Adapted Dimensions** block: each derived
value, with `(clamped from <your value>)` appended wherever auto-fit had
to adjust an input. Non-Custom sizes also echo one
`fit_derived: <key>=<value>` line per derivation, which is what the CI
parity tests consume.

---

## 2. Flat tool power dials

### The plug side rail

One concept powers the flat tool's Advanced tier: a 2D **rail** that
runs down the plug's side, starting at the pocket edge on the plug face
and sloping by the plug's side-taper angle. The angle is **derived from
the two Step 1 width stations** over the plug length (in Custom mode
`custom_pocket_side_angle` sets it directly), so its sign encodes the
taper direction: a plug that is wider at the cable end gives a negative
angle and the pocket walls widen toward the cord. The pocket walls, the
zip-tie stations, and the manual velcro slots all hang off this rail, so
their positions are measured in **mm along the plug's side, from the
plug face toward the cord** — the taper moves everything coherently.

### Zip-tie placement (`Advanced - Zip Tie Placement - Flat Tool`)

- `zip_placement = Auto` spaces `zip_row_count` (1–3) hole pairs along
  the rail and automatically compresses the spacing rather than letting
  a row punch into the finger holes.
- `Manual` places each pair with `zip_pos_1/2/3` (mm along the rail).
  Manual placements are *not* collision-protected — the red warning tags
  (`ZIP TIE HOLES HIT FINGER HOLES`, `…OVERLAP EACH OTHER`,
  `…HIT VELCRO SLOTS`) fire if you overlap something.
- `zip_edge_offset` slides the whole column toward/away from the pocket
  wall.

### Velcro placement (`Advanced - Velcro Placement - Flat Tool`)

`velcro_placement = Manual` slides a pair of classic slots along the
rail with `velcro_pos`. The `Wing` style ignores manual placement (its
opening is derived from the body's dead space); switch
`velcro_style = Classic slot` in Step 3 to use it.

---

## 3. Heavy-duty clamshell tuning (`Advanced - Heavy Duty Clamshell`)

The clamshell derives its core dimensions from the Step 1 measurements:
the arm's gripping edge follows the plug's own **two-station thickness
profile** (thickness near the wall at the arm tips, thickness near the
cord at the plug's back end, interpolated in between), the arm length
grows so the arms always cover the full plug length, the throat — where
the V closes down to the cord channel — sits just below the plug's back
end, the cord channel comes from the cord thickness, and the finger
bores from the Step 2 hand. The `clam_*` dials tune that result. The
defaults carry the field-tested **T3 grip profile** (2 mm teeth, 2.8 mm
pitch, 1 mm bite, grip bite −1) with the serration span on auto.

### Strength recipes

| Goal | Dial(s) |
| ---- | ------- |
| **Denser, stronger plate all around** | `clam_wall_boost` — adds N mm to *every* wall around the inner openings at once (finger walls, cord-channel web, both velcro-slot walls, zip webs). The outline grows and the holes re-place themselves; Auto placement keeps every web intact at any boost. |
| Stiffer sandwich | `clam_plate_thickness` (each half; the stack is 2×) |
| Beef up only the tooth-to-slot boundary | `clam_slot_inner_wall` — measured from the **deepest tooth bite**, so bigger teeth never silently thin it |
| Less plastic / lighter | `clam_velcro_slot_width/length` (the slots double as material reduction), `clam_strip_thickness = 0` |

### Grip tuning

| Goal | Dial(s) |
| ---- | ------- |
| Squeeze harder / looser | `clam_grip_bite` (negative = interference squeeze; applied per side on top of the plug's own thickness profile) |
| Teeth that bite soft plug bodies | `clam_tooth_diameter`, `clam_tooth_pitch`, `clam_tooth_depth` |
| Where the teeth sit | `clam_grip_zone_start` / `clam_grip_zone_length` (measured back from the arm tips; length 0 = auto — the teeth cover the full plug body span) |
| Easier plug entry | `clam_tip_flare` (opens the V at the tips) |
| Cord slides freely | `clam_cable_clearance` |
| Finger security | `clam_finger_fit` (bore = finger width + this) |

Manual zip placement (`clam_zip_placement = Manual` +
`clam_zip_pos_1/2/3`) trades the collision guarantees for full control;
the `WC-*` warning tags call out stations that fall off the arm, overlap
each other, or break into the velcro slot.

---

## 4. Custom mode — the full unlock

Set **Step 2 `size = Custom`** and the measurement/derivation layer
switches off: every slider in the `(Custom size only)` sections drives
the flat-tool geometry directly (body octagon, pocket, finger holes,
J-hook, notch, zip grid, velcro, edge rounding).

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
(103 parameters, CI-validated against the SCAD).

---

## 5. Guard rails and how to read them

The model never silently "fixes" your input past what auto-fit reports.
Anything genuinely wrong prints a **red warning tag** flat on the bed
next to the part (so an exported file physically shows its own defect)
and echoes the same message to the console. The
[Fit Troubleshooting guide](fit-troubleshooting.md) decodes every tag —
flat-tool tags `W-1…W-19`, clamshell tags `WC-1…WC-9`.

Preview-only (never exported): the green `MEDIUM: …` / `MEASURED: …`
confirmation tag, and the orange HUD notices for ignored custom sliders
and auto-fit clamps.

---

## 6. Going deeper

| Resource | What's in it |
| -------- | ------------ |
| [`docs/Plug_Puller_Reference.md`](../../docs/Plug_Puller_Reference.md) | The engineering reference: coordinate frames, the rail math, clamshell derived values, CSG order, derivation layer, parity invariants |
| [`parameter_mapping.json`](../../parameter_mapping.json) | Machine-readable Customizer schema (source of truth for the validator) |

License: PolyForm Noncommercial 1.0.0
