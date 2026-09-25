# openscad-plug-puller

[![License: PolyForm Noncommercial 1.0.0](https://img.shields.io/badge/license-PolyForm%20NC%201.0.0-blue.svg)](LICENSE)
[![OpenSCAD](https://img.shields.io/badge/OpenSCAD-2021.01%2B-orange.svg)](https://openscad.org/downloads.html)
[![Version](https://img.shields.io/badge/version-0.10.0-brightgreen.svg)](CHANGELOG.md)
[![CI: STL Validation](https://github.com/BrennenJohnston/openscad-plug-puller/actions/workflows/stl-validation.yml/badge.svg)](https://github.com/BrennenJohnston/openscad-plug-puller/actions/workflows/stl-validation.yml)

Parametric OpenSCAD model of the **Plug Puller** — a handheld assistive
device that helps users grip and remove electrical plugs from wall
outlets. It comes as **two tools**, each in its own file:

- the **one-sided puller**,
  [`src/Plug_Puller_Parametric.scad`](src/Plug_Puller_Parametric.scad):
  a slab with a plug pocket, finger holes, a cord hook, and zip-tie /
  velcro attachment, for lamp plugs, standard 3-prong plugs and other
  plugs thinner than 24 mm;
- the **two-sided puller**,
  [`src/Plug_Puller_Two_Sided.scad`](src/Plug_Puller_Two_Sided.scad):
  two identical serrated plates that zip-tie face to face around a
  thick round plug, a USB-C tip or a charger plug.

Not sure which? Start with the one-sided puller. If your plug measures
24 mm thick or more, it shows a red tag:
`PLUG THICKER THAN 24MM - USE THE TWO-SIDED PULLER FILE`.

A few quick steps drive the one-sided puller:

1. **Your Plug** — pick a `plug_preset` quick-select (US plug families
   measured from reference plugs) *or* type the measurements of your
   plug and outlet: its length plus its width and thickness at the
   **prong end** and at the **cord end** (the pocket, notch, cord hook,
   and the plug side rail are built from them — no protractor needed)
2. **Size** — `Small` / `Medium` (the reference) / `Large`
   (research-grounded ANSUR-II hand pairs), or `Measure my hand` to type
   two hand measurements
3. **Attachment** — `Zip ties`, `Velcro strap` (`Wing` or `Classic slot`
   style with a `strap_width` setting), both (the default), or none
4. **Cord hook** — `hook_hand` picks the J-hook's chirality (`Right` =
   the reference device)

The two-sided puller has four steps of its own: **Your Plug** (a preset,
or four numbers and whether the plug has `Rounded sides` or
`Flat sides`), **Size**, **Attachment** (`Zip ties + Velcro strap` or
`Zip ties`), and **Print Layout** (`Both plates` in one file, the
default, or `One plate`).

`Custom` size unlocks every individual slider of the one-sided puller
for power users (sections marked "(Custom size only)"). Smooth-sided
round plugs are held by its pocket walls plus a zip tie cinched through
the existing zip-tie holes; fat round plugs are gripped between the
two-sided puller's serrated plates.

![The printed two-sided puller in use at a wall outlet — fingers through both holes, pulling the plug straight out](docs/images/clamshell-in-use-outlet.jpg)

> **Version 0.10** — one step from the **v1.0** public milestone. The
> geometry and guides are complete and print-tested, the shipped STLs
> are CI-validated against golden fixtures, and the model is
> customizable in the browser with nothing to install.

> ### 🌐 Customize in your browser — no install
>
> Open a tool in the OpenSCAD Playground:
> **[the one-sided puller](https://ochafik.com/openscad2/#url=https://raw.githubusercontent.com/BrennenJohnston/openscad-plug-puller/main/dist/Plug_Puller_SingleFile.scad)**
> or **[the two-sided puller](https://ochafik.com/openscad2/#url=https://raw.githubusercontent.com/BrennenJohnston/openscad-plug-puller/main/dist/Plug_Puller_Two_Sided_SingleFile.scad)**
> — the full customizer form runs in your web browser, nothing to
> install, works on a phone. The
> **[Web Customizer Guide](docs/guides/web-customizer.md)** walks
> through it step by step.

> ### I'm new — start here
>
> You don't need to know OpenSCAD (or any 3D modeling) to make a Plug
> Puller that fits **your** plug and **your** hand. Measure a few
> things with a ruler, type them into a form, export, print.
>
> **The one page to start from is the
> [Starter Guide](docs/guides/starter-guide.md)** — match your plug
> against the measuring stencil (or measure it), fill in the steps,
> print. Also available as a printable PDF with a built-in 1:1 paper
> stencil sheet:
> [`docs/Plug_Puller_Starter_Guide.pdf`](docs/Plug_Puller_Starter_Guide.pdf).
>
> The deep dives it points into:
>
> 1. **[Measuring Guide](docs/guides/measuring-guide.md)** — the
>    measurements and exactly how to take them (≈ 5 minutes)
> 2. **[Quick Start for Beginners](docs/guides/quick-start-beginner.md)**
>    — install → type numbers → export the print file, every click
>    spelled out — or skip the install with the
>    **[Web Customizer Guide](docs/guides/web-customizer.md)**
> 3. **[Fit Troubleshooting](docs/guides/fit-troubleshooting.md)** —
>    if the print is snug or loose, which one number to nudge
> 4. **[Try Before You Print](docs/guides/print-preview-outlines.md)** —
>    1:1 paper outline sheets for every quick-select combination, plus
>    a printable measuring stencil (plug silhouettes, ruler, cord gauge,
>    finger holes)
>
> Or skip straight to the [ready-to-print STLs](#ready-to-print-stls)
> below.
>
> The Customizer form itself is tiered the same way: the numbered
> **Steps 1–4** are the whole beginner path; the **`Advanced -`**
> sections and the **`(Custom size only)`** sections below them are
> optional power dials.

> ### I'm a power user — start here
>
> The **[Power User Guide](docs/guides/power-user-guide.md)** covers the
> two upper tiers: manual zip/velcro placement along the plug side rail,
> the two-sided puller's plate dials (grip teeth, the cradle, the
> `plate_wall_boost` strength dial), Custom mode's full slider unlock,
> CLI batch export, saved parameter sets, hidden render modes, and the
> console diagnostics. The machine-readable slider matrices are
> [`parameter_mapping.json`](parameter_mapping.json) (one-sided) and
> [`parameter_mapping_two_sided.json`](parameter_mapping_two_sided.json)
> (two-sided); the engineering
> deep-dive is
> [`docs/Plug_Puller_Reference.md`](docs/Plug_Puller_Reference.md).

## Quick start

1. Open the file for your tool in OpenSCAD (v2021.01 or later; recent
   builds with the Manifold backend render fastest):
   [`src/Plug_Puller_Parametric.scad`](src/Plug_Puller_Parametric.scad)
   for the one-sided puller, or
   [`src/Plug_Puller_Two_Sided.scad`](src/Plug_Puller_Two_Sided.scad)
   for the two-sided puller.
2. Open the **Customizer** panel (`View ▸ Hide Customizer` unchecked;
   older builds: `Window ▸ Customizer`).

   **One-sided puller:**
   - **Step 1 - Your Plug**: pick a `plug_preset` (or leave it on
     `Measure my plug` and type your plug measurements — see the
     [Measuring Guide](docs/guides/measuring-guide.md)). Skip both to
     get the reference plug pocket. The preview shows a see-through
     plug built from your numbers.
   - **Step 2 - Size**: keep `Medium` for the reference tool, pick
     `Small` / `Large`, or pick `Measure my hand` and fill in the two
     hand measurements below the dropdown.
   - **Step 3 - Attachment**: `Zip ties + Velcro` (default), `Zip ties`,
     `Velcro strap`, or `None`; `velcro_style` is `Wing` (default) or
     `Classic slot`.
   - **Step 4 - Cord Hook**: `hook_hand` = `Right` (the reference
     device) or `Left`.

   **Two-sided puller:**
   - **Step 1 - Your Plug**: pick the `plug_preset`, or type four
     numbers (the plug's length, its width at the prong end and at the
     cord end, and the cord), then pick `Rounded sides` (a round plug,
     a USB-C or charger tip: the plates get a sloped cradle that
     centers it) or `Flat sides` (a boxy plug: the teeth bite along the
     whole side).
   - **Step 2 - Size**: `Small` / `Medium` / `Large`, or
     `Measure my hand` and your finger width.
   - **Step 3 - Attachment**: `Zip ties + Velcro strap` (default) or
     `Zip ties`. The zip ties are what hold the two plates together.
   - **Step 4 - Print Layout**: `Both plates` (default) puts both
     plates in one file; `One plate` exports a single plate.
3. Press **F6** to render, then `File ▸ Export ▸ STL` to save the
   print file. For the two-sided puller: print both plates, flip one
   over, zip-tie the pair face to face around the plug.

Everything below Step 4 in the Customizer is optional: the `Advanced -`
sections hold placement overrides (one-sided) and plate tuning
(two-sided), and the `(Custom size only)` sections of the one-sided
file only apply when `size = Custom` — see the
[Power User Guide](docs/guides/power-user-guide.md).

Prefer a single file (e.g. for the MakerWorld customizer or offline
sharing)? Use [`dist/Plug_Puller_SingleFile.scad`](dist/Plug_Puller_SingleFile.scad)
(one-sided) or
[`dist/Plug_Puller_Two_Sided_SingleFile.scad`](dist/Plug_Puller_Two_Sided_SingleFile.scad)
(two-sided) — each model flattened into one file.

## Ready-to-print STLs

No OpenSCAD needed — the [`stl/`](stl) folder ships a pre-rendered copy of
every default configuration, named so you can grab yours without opening the
Customizer. [`stl/README.md`](stl/README.md) is a one-line index of the whole
library; the two groups are:

### Plug pullers — [`stl/Plug-Puller/`](stl/Plug-Puller)

Pick your plug family, then your hand size (`Small` / `Medium` / `Large` —
Medium is the reference device, so start there; Small ≈ 5th-percentile female
hand, Large ≈ 95th-percentile male hand).

| Plug family | Files (`_Small` / `_Medium` / `_Large`) | Tool |
| ----------- | --------------------------------------- | ---- |
| Flat 2-prong lamp — NEMA 1-15 | `Plug-Puller_Flat-2-Prong-Lamp-NEMA-1-15_*.stl` | one-sided puller (one part) |
| Standard 3-prong — NEMA 5-15 | `Plug-Puller_Standard-3-Prong-NEMA-5-15_*.stl` | one-sided puller (one part) |
| Heavy-duty extension cord — NEMA 5-15 | `Plug-Puller_Two-Sided_Round-Extension-Cord-NEMA-5-15_*.stl` | two-sided puller (**both plates**): each file holds both plates; flip one after printing, then zip-tie the pair face to face around the plug |

### Measuring stencil — [`stl/Measuring-Stencil/`](stl/Measuring-Stencil)

Thin measuring cards that answer the fit worksheet without a caliper. Print the
full packed set (`..._All-Cards.stl`) or just the one card you need, in either
label mode:

- **Visual** ([`Measuring-Stencil/Visual/`](stl/Measuring-Stencil/Visual)) — debossed printed labels.
- **Tactile** ([`Measuring-Stencil/Tactile/`](stl/Measuring-Stencil/Tactile)) — raised ADA-size characters plus a fold-flat Grade 2 braille title flap on every card (snap off the support fins, fold each flap back until flat — see the [Starter Guide](docs/guides/starter-guide.md#tactile-version-raised-characters--braille)).

| Card | Purpose |
| ---- | ------- |
| `All-Cards` | the full packed set — every card on one plate |
| `P1_Lamp-Plug-Gauge` / `P2_Standard-3-Prong-Gauge` / `P3_Heavy-Duty-Cord-Gauge` | plug-preset silhouettes |
| `R1_Ruler-100mm` | a tactile 100 mm ruler |
| `C1_Cord-Gauge` | open-slot cord gauge that slides onto an installed cord |
| `F1_Finger-Sizing-15-25mm` / `F2_Finger-Sizing-26-32mm` | all 18 finger-sizing holes |

The whole library is regenerated from source by
[`scripts/build_release_stls.py`](scripts/build_release_stls.py).

Not sure which size? Print a **[1:1 paper outline sheet](docs/guides/print-preview-outlines.md)**
of any quick-select combination first and test it against your real
plug and hand — all nine sheets are also bundled as one printable
PDF: [`docs/Plug_Puller_Outline_Sheets.pdf`](docs/Plug_Puller_Outline_Sheets.pdf). For a tool matched to *your* plug and hand, spend five
minutes with the [Measuring Guide](docs/guides/measuring-guide.md) and
the Customizer instead.

## Customize in your browser

No install needed — the OpenSCAD Playground runs the full customizer
form in your web browser (including on a phone):
**[open the one-sided puller](https://ochafik.com/openscad2/#url=https://raw.githubusercontent.com/BrennenJohnston/openscad-plug-puller/main/dist/Plug_Puller_SingleFile.scad)**
or
**[open the two-sided puller](https://ochafik.com/openscad2/#url=https://raw.githubusercontent.com/BrennenJohnston/openscad-plug-puller/main/dist/Plug_Puller_Two_Sided_SingleFile.scad)**.
The **[Web Customizer Guide](docs/guides/web-customizer.md)**
covers it click by click, including the manual load path and phone
usage notes. Each link loads a flattened single-file build:
[`dist/Plug_Puller_SingleFile.scad`](dist/Plug_Puller_SingleFile.scad) or
[`dist/Plug_Puller_Two_Sided_SingleFile.scad`](dist/Plug_Puller_Two_Sided_SingleFile.scad).

## Publishing to MakerWorld

MakerWorld's Parametric Model Maker runs OpenSCAD files directly:

1. Upload the single-file build of each tool,
   [`dist/Plug_Puller_SingleFile.scad`](dist/Plug_Puller_SingleFile.scad)
   (one-sided) and
   [`dist/Plug_Puller_Two_Sided_SingleFile.scad`](dist/Plug_Puller_Two_Sided_SingleFile.scad)
   (two-sided) — the multi-file `src/` tree will not work there because
   `include <>` files are not uploaded alongside it.
2. MakerWorld auto-detects a `.scad` upload and adds the **Customize**
   button to the model page; the parameter form mirrors the OpenSCAD
   Customizer sections (the Step 1–4 beginner path, the `Advanced -`
   power sections, and, in the one-sided file, the "(Custom size only)"
   expert sections).
3. Test the customizer behaviour first via **Creator Portal → Open SCAD
   File** before publishing.

Draft listing text (title, description, print settings, licensing
notes) is prepared in
[`docs/makerworld-listing.md`](docs/makerworld-listing.md), and the user
guide that goes with it is
[`docs/MAKERWORLD_QUICK_START.md`](docs/MAKERWORLD_QUICK_START.md) —
measuring routes, hand sizing, how to read the on-model warning tags, and
the OpenSCAD Playground alternative for people who cannot use MakerWorld's
customizer. Both follow the shared
[Accessible MakerWorld Documentation Standard](https://github.com/BrennenJohnston/accessible-makerworld-doc-standard/blob/main/ACCESSIBLE_MAKERWORLD_DOC_STANDARD.md).

Note the licensing decision recorded in the listing: publishing on
MakerWorld requires granting MakerWorld's platform license terms alongside
this repo's PolyForm NC 1.0.0 — the listing stays unpublished until the
maintainer signs off on that.

## Features

### Both tools

| Feature | Description |
| ------- | ----------- |
| Two tools, two files | The **one-sided puller** (`src/Plug_Puller_Parametric.scad`) and the **two-sided puller** (`src/Plug_Puller_Two_Sided.scad`) share one size table (`src/fit_sizes.scad`); a plug 24 mm thick or more gets a red tag in the one-sided file that points to the two-sided file |
| Measurement-first Customizer | Plug measurements are Step 1 and always active, named for where you take them: the **prong end** and the **cord end**; sizes and attachment are one dropdown each |
| Plug quick-select | `plug_preset` prefills common US plug families, calibrated from reference-plug measurements: the lamp (NEMA 1-15) and standard (NEMA 5-15) plugs in the one-sided file, the round extension cord (NEMA 5-15) in the two-sided file; `Measure my plug` keeps the sliders authoritative |
| See-through plug | The preview draws a translucent plug built from your numbers in the pocket or between the plates (`show_plug_preview`, on by default), so you can check the fit before printing; it is never exported |
| In-model validation | Red warning tag printed flat on the bed next to the part when a check trips (one-sided W-1…W-20; two-sided WC-1…WC-13), including hole-collision checks; messages name the *measurement* to fix; a preview-only green tag confirms your numbers were applied |
| Try-before-you-print previews | [1:1 dimensioned outline sheets](docs/guides/print-preview-outlines.md) for every quick-select combination (cut out, hold against the plug, try the finger holes) plus a printable [measuring stencil](Measuring_Stencil.scad) with plug silhouettes, ruler, cord gauge, and finger holes |

### One-sided puller

| Feature | Description |
| ------- | ----------- |
| Plug side rail | The pocket walls, zip stations, and velcro slot follow one rail down the plug's side; the rail's taper angle is derived from the two Step 1 width stations over the plug length, so one taper moves everything coherently |
| Organic body | A rounded organic silhouette reproduced by a fitted octagon + side rounding; crisp plug end, blob-rounded cord end, wider shoulder ears |
| Dome plug pocket | A two-level pocket: a plug-shaped recess plus a deeper circular seat centered on the top edge; the two floor heights are directly settable in Custom |
| Finger holes | Mirrored pair, Ø 25.4 mm at Medium, quarter-round rim fillets on both faces |
| Cord J-hook | Chiral J-hook cord catch: an offset stem, a catch lip that reaches past the stem, and a tip that drops below Y = 0 so a hooked cord cannot back out (`hook_hand` mirrors left/right) |
| Plug wall notch | Rounded-corner notch that straddles the outlet wall plate; depth follows the wall-plate style dropdown |
| Zip-tie holes | A 2×2 grid of Ø 5.08 mm holes, with a top-face countersink flare on the exposed lower row |
| Wing velcro slots | Default `Wing` style: curved triangular cutouts filling the dead space between finger hole, pocket, side edge, and zip holes, sized to `strap_width`; a `Classic slot` fallback keeps rectangular slots |
| Round-plug retention | Smooth-sided round plugs are held by the pocket walls plus a zip tie cinched through the existing zip-tie hole grid |
| Auto-fit | Every feature is bounds-clamped against the body envelope so measured sizes never self-intersect; in Custom mode every clamp is reported in the console (`(clamped from …)`) with a preview HUD notice |
| Render mode dispatch | The file renders the full tool, body only, isolated cutouts, or a 2D cutout overlay |

### Two-sided puller

| Feature | Description |
| ------- | ----------- |
| Two identical plates | Serrated plates that zip-tie face to face around the plug; `print_layout = Both plates` (the default) puts both side by side in one file — flip one after printing |
| Rounded or flat sides | `plug_sides`: `Rounded sides` gives each plate a sloped cradle (`plate_cradle_depth`, 2.5 mm per side, with `plate_grip_clearance` 0.5 mm where the plates meet) that centers a round plug, a USB-C or charger tip; `Flat sides` keeps the edge straight so the teeth bite along a boxy plug's whole side |
| Serrated grip | Teeth along both arms follow the cradle's slope; `plate_grip_bite` tunes the bite for `Flat sides` and the plug preset |
| Cord channel | A channel between the finger holes carries the cord out of the pair |
| Finger holes | Your finger width plus `plate_finger_fit` (1 mm): Ø 17.5 / 21 / 24 mm at Small / Medium / Large |
| Zip-tie stations and strap slots | Zip-tie holes along both arms, and a velcro strap slot in each arm when the plug is long enough (on a short plug it is left out, with an orange preview note) |
| Plate dials | `Advanced - Two-Sided Puller`: 26 `plate_*` dials, led by `plate_wall_boost`, which thickens every wall at once |

## Sizes

Both files read the same Small / Medium / Large finger widths from
[`src/fit_sizes.scad`](src/fit_sizes.scad). In the one-sided puller,
all non-Custom sizes route through the measurement derivation layer
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

The two-sided puller uses the finger width only: its finger holes are
Ø 17.5 / 21 / 24 mm at Small / Medium / Large, `Measure my hand` asks
for your finger width alone, and there is no `Custom` size.

### Saved Customizer parameter sets

[`presets/Plug_Puller_Parametric.json`](presets/Plug_Puller_Parametric.json)
ships example parameter sets for the one-sided puller (snapshots of
Customizer values):

| Name in JSON | Loads as | Notes |
| ------------ | -------- | ----- |
| `Medium (v6 reference)` | `Medium` | the one-sided reference device, zip ties + wing velcro |
| `Flat 2-prong lamp plug (NEMA 1-15)` | `plug_preset` | 37 mm long, width 25 → 11.2, thickness 18.6 → 8.6 (prong end → cord end), 3.6 mm cord |
| `Standard 3-prong plug (NEMA 5-15)` | `plug_preset` | 46.2 mm long, width 26.6 → 13.4, thickness 18.9 → 15, 7 mm cord |
| `Small hands` / `Large hands` | `Small` / `Large` | ANSUR-II grip scaling |
| `Measure my plug + hand (US vacuum plug)` | `Measure my hand` | straight-sided plug 34 wide × 16 thick at both ends, 38 mm long, 5 mm cord, Decora plate, 22 / 88 mm hand |
| `Left-handed + classic velcro slots` | `Medium` | `hook_hand = Left`, `velcro_style = Classic slot` |

[`presets/Plug_Puller_Two_Sided.json`](presets/Plug_Puller_Two_Sided.json)
ships two for the two-sided puller:

| Name in JSON | Loads as | Notes |
| ------------ | -------- | ----- |
| `Round extension cord - NEMA 5-15` | `plug_preset` | the heavy-duty extension-cord plug, Medium, zip ties + velcro strap |
| `USB-C laptop plug - measured` | `Measure my plug` | 23 mm long, 13 mm wide at both ends, 7 mm cord, `Rounded sides`, zip ties only |

### Auto-fit and `custom_enable_auto_fit`

Auto-fit clamps geometry into safe ranges (always on for the measured
sizes, toggleable in Custom). When enabled, feature placement is
re-derived from the current body envelope. Disable it only when you
specifically need to push features outside the envelope; the
**in-model validation warnings** (red text past the plug end) will tell
you which checks failed.

## Render modes

The hidden `render_mode` parameter controls which subset of geometry is
built. In the one-sided file:

| Mode | What it renders |
| ---- | --------------- |
| `Full` | The tool: pocketed body + cutouts + warnings |
| `Body Only` | Pocketed body + cutouts |
| `Body No Cutouts` | Solid body, no pocket, no holes (debug view) |
| `Only Finger Holes` / `Only T Hook` / `Only Plug Wall Notch` / `Only Zip Tie Holes` / `Only Velcro Strap Holes` | Plain body + a single feature cutout |
| `Cutouts Only 2D` | 2D overlay of every cutout + pocket profile (debug) |

In the two-sided file, `Full` builds what Step 4's `print_layout` picks
(both plates side by side, or one plate) and `One plate` always builds
a single plate.

## Repository layout

```
openscad-plug-puller/
  Measuring_Stencil.scad           # standalone printable measuring stencil
  src/
    Plug_Puller_Parametric.scad    # the one-sided puller — open this in OpenSCAD
    Plug_Puller_Two_Sided.scad     # the two-sided puller — open this in OpenSCAD
    fit_sizes.scad                 # Small / Medium / Large size table, shared by both files
    presets.scad                   # PRESET_MEDIUM reference table + routing (one-sided)
    fit_measured.scad              # measurement -> parameter derivations (one-sided)
  dist/
    Plug_Puller_SingleFile.scad    # one-sided single-file build (MakerWorld / web)
    Plug_Puller_Two_Sided_SingleFile.scad  # two-sided single-file build (MakerWorld / web)
  presets/
    Plug_Puller_Parametric.json    # example saved Customizer parameter sets (one-sided)
    Plug_Puller_Two_Sided.json     # example saved Customizer parameter sets (two-sided)
  stl/                             # ready-to-print library (see stl/README.md)
    Plug-Puller/                   # 9 tools: 6 one-sided + 3 two-sided (both plates per file)
    Measuring-Stencil/             # sizing cards, in Visual/ and Tactile/ label modes
  docs/
    Plug_Puller_Reference.md       # exhaustive engineering reference
    Plug_Puller_Measuring_Template.pdf  # printable 1:1 measuring template
    Plug_Puller_Outline_Sheets.pdf # all nine 1:1 outline sheets as one printable PDF
    guides/                        # beginner guides: quick start, web customizer, measuring, fit troubleshooting
      outline-sheets/              # printable 1:1 outline sheets (one per quick-select combo)
    images/                        # guide photos and model preview renders
  parameter_mapping.json           # one-sided Customizer schema (79 parameters)
  parameter_mapping_two_sided.json # two-sided Customizer schema (39 parameters)
  CHANGELOG.md
  LICENSE                          # PolyForm Noncommercial 1.0.0
```

## 3D printing tips

- **Orientation:** print with `Z = 0` flat on the print bed (the flat
  bottom face) so the plug pocket faces upward. The pocket floors are
  flat terraces — no supports required.
- **Two-sided puller:** print the file as exported — both plates lie
  flat on their outer faces, no supports. After printing, flip one
  plate over so the two plates meet face to face around the plug.
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
| Red tag `PLUG THICKER THAN 24MM - USE THE TWO-SIDED PULLER FILE` | The plug is too thick for the one-sided puller's pocket | Open [`src/Plug_Puller_Two_Sided.scad`](src/Plug_Puller_Two_Sided.scad) and fill in its Step 1: its plug width is the size the two plates close across |
| Orange `STRAP SLOT LEFT OUT - PLUG TOO SHORT FOR ONE` in the two-sided preview | The plug is too short for a velcro strap slot in the arms; the zip ties still hold the plates | Nothing to fix; or pick `Zip ties` in Step 3 |
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
| [`docs/guides/starter-guide.md`](docs/guides/starter-guide.md) | **Start here** — the whole path on one page: match your plug against the stencil cards (or measure it), fill in the Customizer steps, print |
| [`docs/Plug_Puller_Starter_Guide.pdf`](docs/Plug_Puller_Starter_Guide.pdf) | The starter guide as a printable PDF, ending with the 1:1 paper stencil sheet |
| [`docs/guides/stencil-sheet.svg`](docs/guides/stencil-sheet.svg) | The 1:1 paper stencil sheet on its own (A4 / Letter): calibration square, P1–P3 plug silhouettes, mm ruler, finger circles |
| [`docs/guides/quick-start-beginner.md`](docs/guides/quick-start-beginner.md) | Zero-experience walkthrough: install OpenSCAD, type your measurements, export the STL |
| [`docs/guides/web-customizer.md`](docs/guides/web-customizer.md) | The same walkthrough with zero install: customize and export in your web browser (works on a phone) |
| [`docs/guides/measuring-guide.md`](docs/guides/measuring-guide.md) | The plug and hand measurements, how to take each one, printable worksheet |
| [`docs/guides/measuring-template.svg`](docs/guides/measuring-template.svg) | Printable 1:1 sheet (A4 / Letter): calibration square, mm ruler, finger-sizing circles |
| [`docs/Plug_Puller_Measuring_Template.pdf`](docs/Plug_Puller_Measuring_Template.pdf) | The same measuring template as a printable PDF |
| [`docs/guides/print-preview-outlines.md`](docs/guides/print-preview-outlines.md) | Try before you print: 1:1 outline sheets for every quick-select combination + the measuring stencil |
| [`docs/Plug_Puller_Outline_Sheets.pdf`](docs/Plug_Puller_Outline_Sheets.pdf) | All nine 1:1 outline sheets in one printable PDF with a cover index |
| [`docs/guides/fit-troubleshooting.md`](docs/guides/fit-troubleshooting.md) | Symptom → which measurement to nudge → by how much; warning-tag decoder |

### For power users (the Advanced and Custom tiers)

| Document | Description |
| -------- | ----------- |
| [`docs/guides/power-user-guide.md`](docs/guides/power-user-guide.md) | The Advanced sections (rail-based zip/velcro placement, the two-sided puller's plate dials, cradle and strength dial), Custom mode's full unlock, saved parameter sets, CLI batch export, hidden render modes, console diagnostics |
| [`parameter_mapping.json`](parameter_mapping.json) | Machine-readable Customizer schema of the one-sided puller (79 parameters) — every name, type, range, step, and default |
| [`parameter_mapping_two_sided.json`](parameter_mapping_two_sided.json) | The same for the two-sided puller (39 parameters) |

### For contributors and engineers

| Document | Description |
| -------- | ----------- |
| [`docs/Plug_Puller_Reference.md`](docs/Plug_Puller_Reference.md) | Exhaustive reference: both tools, coordinate frames, the plug side rail, the two-sided plate geometry, CSG order, parameter catalog, sizes, derivation layer, render modes, validation warnings |
| [`CHANGELOG.md`](CHANGELOG.md) | Keep-a-Changelog release history |

## Related projects

- [`braille-stl-generator-openscad`](https://github.com/BrennenJohnston/braille-stl-generator-openscad) — sibling parametric OpenSCAD project; the pipeline conventions (presets.scad, in-model warnings) used here were adapted from it.
- [`cad-to-openscad-pipeline`](https://github.com/BrennenJohnston/cad-to-openscad-pipeline) — the general-purpose CAD-to-OpenSCAD methodology and the DXF → polygon conversion tool.

## License

[PolyForm Noncommercial 1.0.0](LICENSE). Personal, hobby, educational,
research, and other noncommercial use is permitted. Contact the
maintainer for commercial use.
