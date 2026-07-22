# openscad-plug-puller

[![License: PolyForm Noncommercial 1.0.0](https://img.shields.io/badge/license-PolyForm%20NC%201.0.0-blue.svg)](LICENSE)
[![OpenSCAD](https://img.shields.io/badge/OpenSCAD-2021.01%2B-orange.svg)](https://openscad.org/downloads.html)
[![Version](https://img.shields.io/badge/version-0.8.0-brightgreen.svg)](CHANGELOG.md)

Parametric OpenSCAD model of the **Plug Puller** — a handheld assistive
device that helps users grip and remove electrical plugs from wall
outlets. One model builds **two tools**, chosen with a Step 0
`tool_style` selector: a **flat tool** (a slab with a plug pocket,
finger holes, a cord hook, and zip-tie / velcro attachment) and a
**heavy-duty clamshell** (a pair of identical serrated collar plates
that zip-tie around a fat extension-cord plug). A few quick steps drive
the whole model:

0. **Tool style** — `Auto from plug` (clamshell for thick plugs, else the
   flat tool), or force `Flat tool` / `Heavy-duty clamshell`
1. **Your Plug** — pick a `plug_preset` quick-select (top-3 US plug
   families, measured from reference plugs) *or* type the measurements
   of your plug and outlet: its length plus width and thickness **near
   the wall** and **near the cord** (the pocket, notch, cord hook, and
   the plug side rail are built from them — no protractor needed)
2. **Size** — `Small` / `Medium` (the reference) / `Large`
   (research-grounded ANSUR-II hand pairs), or `Measure my hand` to type
   two hand measurements
3. **Attachment** — `Zip ties`, `Velcro strap` (`Wing` or `Classic slot`
   style with a `strap_width` setting), both (the default), or none
4. **Cord hook** — `hook_hand` picks the J-hook's chirality (`Right` =
   the reference device)

`Custom` size unlocks every individual slider for power users (sections
marked "(Custom size only)"). Smooth-sided round plugs are held by the
pocket walls plus a zip tie cinched through the existing zip-tie holes;
fat round plugs are gripped between two serrated clamshell plates.

> **Version 0.8** — this is the first public release, approaching a
> **v1.0** public milestone. The geometry and guides are complete and
> print-tested; expect small refinements before 1.0.

> ### I'm new — start here
>
> You don't need to know OpenSCAD (or any 3D modeling) to make a Plug
> Puller that fits **your** plug and **your** hand. Measure a few
> things with a ruler, type them into a form, export, print:
>
> 1. **[Measuring Guide](docs/guides/measuring-guide.md)** — the
>    measurements and exactly how to take them (≈ 5 minutes)
> 2. **[Quick Start for Beginners](docs/guides/quick-start-beginner.md)**
>    — install → type numbers → export the print file, every click
>    spelled out
> 3. **[Fit Troubleshooting](docs/guides/fit-troubleshooting.md)** —
>    if the print is snug or loose, which one number to nudge
>
> Or skip straight to the [ready-to-print STLs](#ready-to-print-stls)
> below.
>
> The Customizer form itself is tiered the same way: the numbered
> **Steps 0–4** are the whole beginner path; the **`Advanced -`**
> sections and the **`(Custom size only)`** sections below them are
> optional power dials.

> ### I'm a power user — start here
>
> The **[Power User Guide](docs/guides/power-user-guide.md)** covers the
> two upper tiers: manual zip/velcro placement along the plug side rail,
> heavy-duty clamshell tuning (grip teeth, `clam_wall_boost` strength
> dial), Custom mode's full slider unlock, CLI batch export, saved
> parameter sets, hidden render modes, and the console diagnostics. The
> machine-readable slider matrix is
> [`parameter_mapping.json`](parameter_mapping.json); the engineering
> deep-dive is
> [`docs/Plug_Puller_Reference.md`](docs/Plug_Puller_Reference.md).

## Quick start

1. Open [`Plug_Puller.scad`](Plug_Puller.scad) at the repo root in
   OpenSCAD (v2021.01 or later; recent builds with the Manifold backend
   render fastest). It is a thin wrapper around the source in
   [`src/`](src).
2. Open the **Customizer** panel (`View ▸ Hide Customizer` unchecked;
   older builds: `Window ▸ Customizer`).
   - **Step 0 - Tool Style**: `Auto from plug` (default) picks the
     clamshell for thick plugs and the flat tool otherwise; or force
     `Flat tool` / `Heavy-duty clamshell`.
   - **Step 1 - Your Plug**: pick a `plug_preset` (or leave it on
     `Measure my plug` and type your plug measurements — see the
     [Measuring Guide](docs/guides/measuring-guide.md)). Skip both to
     get the reference plug pocket.
   - **Step 2 - Size**: keep `Medium` for the flat-tool reference, pick
     `Small` / `Large`, or pick `Measure my hand` and fill in the two
     hand measurements below the dropdown.
   - **Step 3 - Attachment**: `Zip ties + Velcro` (default), `Zip ties`,
     `Velcro strap`, or `None`; `velcro_style` is `Wing` (default) or
     `Classic slot`.
   - **Step 4 - Cord Hook**: `hook_hand` = `Right` (the reference
     device) or `Left`.
3. Press **F6** to render, then `File ▸ Export ▸ STL` to save the
   print file. (The heavy-duty clamshell is a single plate — print it
   twice and flip one copy over, then zip-tie the pair face to face
   around the plug.)

Everything below Step 4 in the Customizer is optional: the `Advanced -`
sections hold placement overrides and clamshell tuning, and the
`(Custom size only)` sections only apply when `size = Custom` — see the
[Power User Guide](docs/guides/power-user-guide.md).

For direct access to the source (e.g. when working on the model
itself), open [`src/Plug_Puller_Parametric.scad`](src/Plug_Puller_Parametric.scad).
For web customizers that require a single file, use the flattened build
[`dist/Plug_Puller_SingleFile.scad`](dist/Plug_Puller_SingleFile.scad).

## Ready-to-print STLs

No OpenSCAD needed — three pre-rendered flat tools with default
settings live in [`stl/`](stl):

| File | Size | Fits |
| ---- | ---- | ---- |
| [`stl/Plug_Puller_Small.stl`](stl/Plug_Puller_Small.stl) | Small | ≈ 5th-percentile female hand |
| [`stl/Plug_Puller_Medium.stl`](stl/Plug_Puller_Medium.stl) | Medium | the reference size — start here |
| [`stl/Plug_Puller_Large.stl`](stl/Plug_Puller_Large.stl) | Large | ≈ 95th-percentile male hand |

For a tool matched to *your* plug and hand, spend five minutes with the
[Measuring Guide](docs/guides/measuring-guide.md) and the Customizer
instead.

## Publishing to MakerWorld

MakerWorld's Parametric Model Maker runs OpenSCAD files directly:

1. Upload [`dist/Plug_Puller_SingleFile.scad`](dist/Plug_Puller_SingleFile.scad)
   (the single-file build — the multi-file `src/` tree will not work
   there because `include <>` files are not uploaded alongside it).
2. MakerWorld auto-detects the `.scad` upload and adds the **Customize**
   button to the model page; the parameter form mirrors the OpenSCAD
   Customizer sections (the Step 0–4 beginner path, the `Advanced -`
   power sections, and the "(Custom size only)" expert sections).
3. Test the customizer behaviour first via **Creator Portal → Open SCAD
   File** before publishing.

## Features

| Feature | Description |
| ------- | ----------- |
| Two tools, one model | Step 0 `tool_style` picks the **flat tool** or the **heavy-duty clamshell**; `Auto from plug` chooses the clamshell for thick plugs (effective thickness ≥ 24 mm) and the flat tool otherwise |
| Heavy-duty clamshell | A pair of identical serrated collar plates that zip-tie around a fat extension-cord plug |
| Plug side rail | The flat-tool pocket walls, zip stations, and velcro slot follow one rail down the plug's side; the rail's taper angle is derived from the two Step 1 width stations over the plug length, so one taper moves everything coherently |
| Plug quick-select | `plug_preset` prefills three common US plug families (Flat NEMA 1-15, Standard NEMA 5-15, Heavy-duty round NEMA 5-15), calibrated from reference-plug measurements; `Measure my plug` keeps the sliders authoritative |
| Measurement-first Customizer | Plug measurements are Step 1 and always active; sizes and attachment are one dropdown each |
| Organic body | A rounded organic silhouette reproduced by a fitted octagon + side rounding; crisp plug end, blob-rounded cord end, wider shoulder ears |
| Dome plug pocket | A two-level pocket: a plug-shaped recess plus a deeper circular seat centered on the top edge; the two floor heights are directly settable in Custom |
| Finger holes | Mirrored pair, Ø 25.4 mm at Medium, quarter-round rim fillets on both faces |
| Cord J-hook | Chiral J-hook cord catch: an offset stem, a catch lip that reaches past the stem, and a tip that drops below Y = 0 so a hooked cord cannot back out (`hook_hand` mirrors left/right) |
| Plug wall notch | Rounded-corner notch that straddles the outlet wall plate; depth follows the wall-plate style dropdown |
| Zip-tie holes | A 2×2 grid of Ø 5.08 mm holes, with a top-face countersink flare on the exposed lower row |
| Wing velcro slots | Default `Wing` style: curved triangular cutouts filling the dead space between finger hole, pocket, side edge, and zip holes, sized to `strap_width`; a `Classic slot` fallback keeps rectangular slots |
| Round-plug retention | Smooth-sided round plugs are held by the pocket walls plus a zip tie cinched through the existing zip-tie hole grid |
| Auto-fit | Every feature is bounds-clamped against the body envelope so measured sizes never self-intersect; in Custom mode every clamp is reported in the console (`(clamped from …)`) with a preview HUD notice |
| In-model validation | Red warning tag printed flat on the bed next to the part when a check trips (flat tool W-1…W-19; clamshell WC-1…WC-9), including hole-collision checks; messages name the *measurement* to fix; a preview-only green tag confirms your numbers were applied |
| Render mode dispatch | Single SCAD renders the full model, the clamshell plate, body only, isolated cutouts, or a 2D cutout overlay |

## Sizes

All non-Custom sizes route through the measurement derivation layer
([`src/fit_measured.scad`](src/fit_measured.scad)): the plug
measurements (or a `plug_preset`) drive the pocket / notch / J-hook, and
the size picks the hand pair that drives the grip and body envelope. The
hand pairs are research-grounded (ANSUR II 2012 hand breadth + Rogers 2008
PIP-joint breadth): Small ≈ 5th %ile female, Large ≈ 95th %ile male.

| Size | Hand pair (finger / hand) | Body | Notes |
| ---- | ------------------------- | ---- | ----- |
| `Small` | 16.5 / 72 mm | ≈ 60 × 65 × 5.4 mm | scaled-down grip |
| `Medium` | 20 / 85 mm | 81.55 × 65.5 × 6.35 mm (octagon) | **= the reference device** |
| `Large` | 23 / 96 mm | ≈ 78 × 66 × 7.2 mm | scaled-up grip |
| `Measure my hand` | your two measurements | derived | defaults reproduce Medium exactly |
| `Custom` | — | sliders | measurements ignored; every slider unlocked |

### Saved Customizer parameter sets

[`presets/Plug_Puller_Parametric.json`](presets/Plug_Puller_Parametric.json)
ships example parameter sets (snapshots of Customizer values):

| Name in JSON | Loads as | Notes |
| ------------ | -------- | ----- |
| `Medium (v6 reference)` | `Medium` | the flat-tool reference device, zip ties + wing velcro |
| `Flat 2-prong lamp plug (NEMA 1-15)` | `plug_preset` | 37 mm long, width 25 → 11.2, thickness 18.6 → 8.6 (wall → cord), 3.6 mm cord |
| `Standard 3-prong plug (NEMA 5-15)` | `plug_preset` | 46.2 mm long, width 26.6 → 13.4, thickness 18.9 → 15, 7 mm cord |
| `Heavy-duty round cord (NEMA 5-15)` | `plug_preset` | 43.8 mm long, 27 mm thick at both ends (→ clamshell), 8.2 mm cord |
| `Small hands` / `Large hands` | `Small` / `Large` | ANSUR-II grip scaling |
| `Measure my plug + hand (US vacuum plug)` | `Measure my hand` | straight-sided plug 34 wide × 16 thick at both stations, 38 mm long, 5 mm cord, Decora plate, 22 / 88 mm hand |
| `Left-handed + classic velcro slots` | `Medium` | `hook_hand = Left`, `velcro_style = Classic slot` |

### Auto-fit and `custom_enable_auto_fit`

Auto-fit clamps geometry into safe ranges (always on for the measured
sizes, toggleable in Custom). When enabled, feature placement is
re-derived from the current body envelope. Disable it only when you
specifically need to push features outside the envelope; the
**in-model validation warnings** (red text past the plug end) will tell
you which checks failed.

## Render modes

The hidden `render_mode` parameter controls which subset of geometry is built:

| Mode | What it renders |
| ---- | --------------- |
| `Full` | The resolved tool — flat tool (pocketed body + cutouts + warnings) or the clamshell plate |
| `Clamshell Plate` | The heavy-duty plate (print two copies, flip one) |
| `Body Only` | Pocketed body + cutouts |
| `Body No Cutouts` | Solid body, no pocket, no holes (debug view) |
| `Only Finger Holes` / `Only T Hook` / `Only Plug Wall Notch` / `Only Zip Tie Holes` / `Only Velcro Strap Holes` | Plain body + a single feature cutout |
| `Cutouts Only 2D` | 2D overlay of every cutout + pocket profile (debug) |

## Repository layout

```
openscad-plug-puller/
  Plug_Puller.scad                 # root entry point — open this in OpenSCAD
  src/
    Plug_Puller_Parametric.scad    # flat tool + heavy-duty clamshell
    presets.scad                   # PRESET_MEDIUM reference table + routing
    fit_measured.scad              # measurement -> parameter derivations
  dist/
    Plug_Puller_SingleFile.scad    # flattened single-file build (MakerWorld / web)
  presets/
    Plug_Puller_Parametric.json    # example saved Customizer parameter sets
  stl/                             # ready-to-print Small / Medium / Large samples
  docs/
    Plug_Puller_Reference.md       # exhaustive engineering reference
    Plug_Puller_Complete_Guide.pdf # printable complete guide
    Plug_Puller_Measuring_Template.pdf  # printable 1:1 measuring template
    guides/                        # beginner guides: quick start, measuring, fit troubleshooting
  parameter_mapping.json           # full Customizer schema (103 parameters)
  CHANGELOG.md
  LICENSE                          # PolyForm Noncommercial 1.0.0
```

## 3D printing tips

- **Orientation:** print with `Z = 0` flat on the print bed (the flat
  bottom face) so the plug pocket faces upward. The pocket floors are
  flat terraces — no supports required.
- **Layer height:** 0.2 mm gives a clean finish on the pocket walls;
  0.16 mm sharpens the rim fillets on the 6.35 mm slab.
- **Infill:** 25–35 % cubic or gyroid is plenty for hand strength. The
  pull cord, not the slab, takes most of the load.
- **Walls / perimeters:** 3–4 walls. The zip-tie holes and optional
  velcro slots cut close to the pocket, so thin walls make those
  regions fragile.
- **Material:** PETG is the recommended default — it tolerates the
  cord-tension fatigue cycle better than PLA and resists outlet heat
  near a misbehaving plug. ABS / ASA work too. Avoid soft TPU; the
  device needs to stay rigid for the hook to grip the cord.
- **Quality slider:** the default `quality = 64` is already
  print-ready. Drop to `32` for fast previews; push to `96` or `128`
  only if you specifically need crisp curvature on a very large export.

## Troubleshooting

| Symptom | Likely cause | Where to look |
| ------- | ------------ | ------------- |
| Red warning tag lies flat on the bed past the end of the model | One of the in-model validation checks tripped | The tag text names the failed check; every warning is also echoed to the console. In the measured sizes the message names the *measurement* to fix — see the [Fit Troubleshooting Guide](docs/guides/fit-troubleshooting.md) |
| Green `MEDIUM: …` (or `MEASURED: …`) tag in the preview | Not a problem — preview-only confirmation that your measurements were applied. Never appears in the exported STL | — |
| Orange `CUSTOM SLIDERS IGNORED - SET SIZE = CUSTOM` tag in the preview | A `custom_*` slider was moved while a non-Custom size is active — those sliders only apply when `size = Custom`. The console lists each ignored slider by name | The `size` dropdown (Step 2) |
| Typed measurements but the model doesn't change | `size` is set to `Custom` — measurements are ignored there. Pick any other size | The `size` dropdown (Step 2) |
| Sliders ignored | The measured sizes override the custom sliders via the derivation layer (the preview shows the orange HUD tag). Switch `size` to `Custom` | [`src/presets.scad`](src/presets.scad) |
| Smooth round plug slips out of the pocket | Round cord ends have no shoulders for the notch to catch | Thread a zip tie down one zip-tie hole, around the plug barrel, and back up the opposite hole, then cinch it — the 2×2 grid doubles as a clamp anchor |
| Hand sliders do nothing | `measure_finger_width` / `measure_hand_width` apply only when `size = Measure my hand` | Step 2 of the Customizer |
| Customizer never shows a slider you expected | Either the parameter lives under `/* [Hidden] */` (e.g. `render_mode`), or you are not in `Custom` size | [`parameter_mapping.json`](parameter_mapping.json) lists every user-facing parameter |

## Documentation index

Organized by audience — start in the row that matches you.

### For beginners (measure, type, print)

| Document | Description |
| -------- | ----------- |
| [`docs/guides/quick-start-beginner.md`](docs/guides/quick-start-beginner.md) | Zero-experience walkthrough: install OpenSCAD, type your measurements, export the STL |
| [`docs/guides/measuring-guide.md`](docs/guides/measuring-guide.md) | The plug and hand measurements, how to take each one, printable worksheet |
| [`docs/guides/measuring-template.svg`](docs/guides/measuring-template.svg) | Printable 1:1 sheet (A4 / Letter): calibration square, mm ruler, finger-sizing circles |
| [`docs/Plug_Puller_Measuring_Template.pdf`](docs/Plug_Puller_Measuring_Template.pdf) | The same measuring template as a printable PDF |
| [`docs/guides/fit-troubleshooting.md`](docs/guides/fit-troubleshooting.md) | Symptom → which measurement to nudge → by how much; warning-tag decoder |
| [`docs/Plug_Puller_Complete_Guide.pdf`](docs/Plug_Puller_Complete_Guide.pdf) | The complete guide as a single printable PDF |

### For power users (the Advanced and Custom tiers)

| Document | Description |
| -------- | ----------- |
| [`docs/guides/power-user-guide.md`](docs/guides/power-user-guide.md) | The Advanced sections (rail-based zip/velcro placement, clamshell tuning and strength dials), Custom mode's full unlock, saved parameter sets, CLI batch export, hidden render modes, console diagnostics |
| [`parameter_mapping.json`](parameter_mapping.json) | Machine-readable Customizer schema (103 parameters) — every name, type, range, step, and default |

### For contributors and engineers

| Document | Description |
| -------- | ----------- |
| [`docs/Plug_Puller_Reference.md`](docs/Plug_Puller_Reference.md) | Exhaustive reference: both tools, coordinate frames, the plug side rail, clamshell geometry, CSG order, parameter catalog, sizes, derivation layer, render modes, validation warnings |
| [`CHANGELOG.md`](CHANGELOG.md) | Keep-a-Changelog release history |

## Related projects

- [`braille-stl-generator-openscad`](https://github.com/BrennenJohnston/braille-stl-generator-openscad) — sibling parametric OpenSCAD project; the pipeline conventions (presets.scad, in-model warnings) used here were adapted from it.
- [`cad-to-openscad-pipeline`](https://github.com/BrennenJohnston/cad-to-openscad-pipeline) — the general-purpose CAD-to-OpenSCAD methodology and the DXF → polygon conversion tool.

## License

[PolyForm Noncommercial 1.0.0](LICENSE). Personal, hobby, educational,
research, and other noncommercial use is permitted. Contact the
maintainer for commercial use.
