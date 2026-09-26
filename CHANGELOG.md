# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Versions below 1.0.0 are public preview releases: the model is complete
and print-tested, but small refinements are expected before the **v1.0
public milestone**.

## [Unreleased]

### Added

- **The dial reference** (`docs/Plug_Puller_Dial_Reference.pdf` and its
  Markdown twin `docs/guides/dial-reference.md`), generated from
  `dial_catalog.json` by `scripts/build_dial_reference.py`: one page per
  Customizer dial of both pullers with a diagram of what the dial moves,
  its sentence, the default, range, step and unit, its caution note, the
  features its trace touches and the warning tags it can trip; the PDF
  has bookmarks and a linked contents page.
- **A diagram for every dial** under `docs/dials/` (118 SVGs, an index
  and a README), drawn by `scripts/generate_dial_diagrams.py` from the
  catalog: the tool at its defaults in black, the plug in teal, a red
  dashed trace on what the dial moves.

### Removed

- `docs/Plug_Puller_Complete_Guide.pdf` (described the retired single-file
  model; replaced by the dial reference and the guides).

## [0.12.0] - 2026-09-24

The two tools move into two files. The **one-sided puller** (the old
flat tool) stays in `src/Plug_Puller_Parametric.scad`; the **two-sided
puller** (the old heavy-duty clamshell) gets its own file,
`src/Plug_Puller_Two_Sided.scad`, with its own Customizer, a cradle for
rounded plugs, and both plates in one download.

### Added

- **`src/Plug_Puller_Two_Sided.scad`**: the two-sided puller in its own
  file, lifted out of the one-sided file without a geometry change
  (proven against the golden fixture). Its Customizer has four steps in
  plain words — Your Plug, Size, Attachment, Print Layout — and an
  `Advanced - Two-Sided Puller` section of 26 `plate_*` dials. Step 1
  takes the plug length (12–85 mm), its width at the prong end and at
  the cord end (`measure_plug_width_prong_end` / `_cord_end`, 5–40 mm:
  the size the two plates close across) and the cord (1.5–12 mm). The
  finger holes follow the shared size table: Ø 17.5 / 21 / 24 mm at
  Small / Medium / Large. Ships with `parameter_mapping_two_sided.json`
  (39 parameters) and `presets/Plug_Puller_Two_Sided.json` (the round
  extension cord and a measured USB-C laptop plug).
- **`dist/Plug_Puller_Two_Sided_SingleFile.scad`**: the two-sided
  puller as one file for web customizers; `scripts/build_flattened.py`
  builds both single files and `--check` verifies both.
- **`src/fit_sizes.scad`**: the Small / Medium / Large size table and
  finger clearance, shared by both files.
- **Both plates in one file**: `print_layout` (Step 4 of the two-sided
  file) is `Both plates` by default, two identical plates side by side,
  or `One plate`. The console says "PRINT LAYOUT: both plates side by
  side - flip one after printing".
- **Rounded or flat sides** (`plug_sides`, two-sided): `Rounded sides`
  (the default) gives each plate a sloped cradle, 2.5 mm per side
  (`plate_cradle_depth`), with 0.5 mm of room where the plates meet
  (`plate_grip_clearance`), so a round plug, a USB-C or charger tip
  centers itself; the teeth follow the slope and the arm tips step in
  to carry it. `Flat sides` keeps the straight toothed edge for a boxy
  plug.
- **See-through plug in the preview** (`show_plug_preview`, both files,
  on by default): a translucent plug built from your numbers sits in
  the pocket or on the plate so you can check the fit; it is never
  exported.
- **New in-model checks**: two-sided WC-12
  `PLUG NARROWER THAN THE CORD CHANNEL - ARMS CANNOT TOUCH IT` and
  WC-13 `CRADLE SHALLOWER THAN ASKED - PLUG NARROW`; one-sided W-20
  `PLUG THICKER THAN 24MM - USE THE TWO-SIDED PULLER FILE`. The
  two-sided file also echoes its derived values (plate length, grip
  gaps, cradle depth, cord channel, finger hole, strap slot, zip
  stations) to the console.
- **`export_card` selector on the measuring stencil** (`Measuring_Stencil.scad`,
  new `[Export]` Customizer tab): `All cards` keeps the normal packed-sheet
  layout, while picking a card ID (P1/P2/P3/R1/C1/F1/F2) renders just that one
  stencil at the origin so it can be uploaded as a standalone model. This is
  what lets the release build ship every card as its own file.
- **`scripts/build_release_stls.py`**: one command renders the entire
  committed ready-to-print library under `stl/` — 9 plug tools (6
  one-sided pullers for the lamp and standard plugs and 3 two-sided
  pullers for the round extension cord, each × Small/Medium/Large) and
  16 measuring-stencil cards (Visual/Tactile full sets plus every
  individual card) — each watertight-checked. `--only plug-puller` /
  `--only stencil` rebuild one group.
- **`stl/README.md`**: an index of the library that maps every file to the
  plug family, hand size, and stencil card it prints.

### Changed

- **Reorganized `stl/` into a self-describing tree** so there is a single,
  unambiguous home for downloads. The old flat, default-plug samples
  (`stl/Plug_Puller_{Small,Medium,Large}.stl`,
  `stl/Measuring_Stencil{,_Tactile}.stl`) are replaced by
  `stl/Plug-Puller/…` and `stl/Measuring-Stencil/{Visual,Tactile}/…`, whose
  filenames name the plug preset, size, and stencil card. README and the
  beginner guides now link the new paths.
- **`tests/test_shipped_stls.py`** guards the whole library by reusing
  `build_release_stls.py`'s job catalog: every shipped STL is checked
  watertight (quick lane) and re-rendered mesh-equivalent to its source
  (render lane), so the downloads can never silently drift from the model.
- **The round extension cord ships as the two-sided puller**:
  `stl/Plug-Puller/Plug-Puller_Two-Sided_Round-Extension-Cord-NEMA-5-15_{Small,Medium,Large}.stl`,
  each file holding both plates (each plate the same as before). Flip
  one after printing, then zip-tie the pair face to face around the
  plug.
- **One-sided Step 1 names**: `measure_plug_width_prong_end` /
  `_cord_end` and `measure_plug_thickness_prong_end` / `_cord_end`
  replace the `…_wall` / `…_cable` names, and the help texts name the
  prong end and the cord end. Saved parameter sets that use the old
  names need the new ones. Slider ranges: width 8–38 mm, thickness
  4–40 mm, cord 1.5–9 mm, length 12–85 mm.
- **One-sided Customizer**: Step 1 comes first (Step 0 is gone), and
  the sections read `Step 4 - Cord Hook`, `Advanced - Zip Tie
  Placement` and `Advanced - Velcro Placement` (no "- Flat Tool"); the
  Step 3, Step 4 and Advanced placement help texts describe the one
  tool.
- **Two-sided strap slot**: with Auto placement a plug too short for a
  velcro slot now gets none, with an orange preview note
  `STRAP SLOT LEFT OUT - PLUG TOO SHORT FOR ONE`, instead of a red tag;
  WC-7 and WC-11 fire only with Manual placement.
- **Two-sided tags name the width**: WC-2
  `PLUG TOO WIDE - ARMS BULGE PAST FINGER LOBES` and WC-9
  `PLUG WIDTH TAPER LOOKS WRONG - RECHECK BOTH ENDS`.
- **`plate_grip_bite`** (was `clam_grip_bite`) applies to `Flat sides`
  and the plug preset only, and WC-3 fires only there.
- **Two-sided finger holes use the true size table**: Large is Ø 24 mm
  (the old file's auto-fit clamp shrank it to 22.66 mm at its default
  plug).
- **Outline sheets**: the sheets say "One-sided puller" and "Two-sided
  puller plate", and the plate sheets are
  `outline_two-sided-plate_{small,medium,large}.svg`: 9 sheets and a
  10-page PDF.
- **README, starter guide, beginner quick start** (and the starter
  guide PDF) describe the two tools, which file to open for each, and
  the two-sided steps.

### Removed

- **Step 0 `tool_style` and the clamshell in the one-sided file**
  (`src/Plug_Puller_Parametric.scad`): its Advanced clamshell section,
  the clamshell checks and the `Clamshell Plate` render mode. The
  two-sided puller lives in `src/Plug_Puller_Two_Sided.scad`.
- **Two-sided attachment choices `Velcro strap` and `None`**: without
  zip ties the two plates cannot be held together.
- **`Plug-Puller_Heavy-Duty-Cord-NEMA-5-15_Clamshell-Plate_{Small,Medium,Large}.stl`**,
  replaced by the two-sided files above.
- **The one-sided saved set "Heavy-duty round cord (NEMA 5-15)"**; the
  two-sided presets file has the round extension cord.
- **The `clamshell_plate` golden fixture**; the `two_sided_plate`
  fixture covers the plate.
- **The three one-sided outline sheets for the extension-cord plug**:
  that plug's sheets are the three two-sided plate sheets.
- **`dist/Plug_Puller_SingleFile.json`**: a stray file of Customizer
  sets saved in 0.8.0 that named settings which no longer exist.

## [0.11.0] - 2026-07-23

Makes the measuring stencil work one-handed on an installed cord (the
gauges open through the card edge) and fully non-visual: a Tactile
label mode with raised ADA-size characters and a fold-flat Grade 2
braille title flap on every card.

### Added

- **Tactile label mode** (`label_mode = Tactile`, new `[Labels]`
  Customizer tab with a `Visual (default)` / `Tactile (raised +
  braille)` preset pair in `Measuring_Stencil.json`, pre-rendered
  `stl/Measuring_Stencil_Tactile.stl`): every debossed label becomes a
  raised uppercase character at ADA 703.2 size (16 mm nominal, 0.8 mm
  proud), and every card grows a **Grade 2 braille title flap**
  (ADA 703.3) past its top edge. The flap prints leaning back at 75° —
  the CHI 2024 sweet spot where braille dots print crispest — joined
  to the card by a living hinge (`hinge_thickness`, the only other new
  parameter) and held by break-away support fins with snap-off bridges
  and a bed brim (the braille-wedge-card technique). Post-print: snap
  the fins off and fold each flap away from the card until flat — the
  braille lands face-up beyond the card's top edge. Tactile R1 drops
  the numerals (an ADA digit cannot fit the 10 mm tick pitch) and C1's
  slot pitch widens so the ADA digits stay separated; the sheet packer
  accounts for every flap's printed footprint.
- **Braille translation pipeline**
  (`scripts/generate_braille_labels.mjs` + committed
  `scripts/braille_labels.json`): card titles pre-translated to UEB
  Grade 2 Unicode braille with Liblouis
  (`unicode.dis,en-ueb-g2.ctb`), hardcoded into the SCAD as
  `BRAILLE_LABELS` — no user-facing braille settings.
  `tests/test_braille_labels.py` drift-locks the SCAD copy against the
  generator output, validates every codepoint is Unicode braille, and
  asserts every line fits its card's width.
- **Shipped-STL coverage**: `stl/Measuring_Stencil_Tactile.stl` joins
  the watertight/winding guards, and the stencil render-parity test is
  parametrized over both label modes (the Tactile case doubles as the
  render smoke test for the new geometry).

### Changed

- **C1 cord gauge is now open-throat** (both label modes): the Ø 3–9 mm
  through-holes became U-slots opening through the card's bottom edge,
  so the card slides sideways onto an *installed* cord — no free cord
  end needed. Usage is now "the smallest slot that slips over the cord
  is the cord thickness".
- **P1–P3 cord holes opened the same way**: each plug card's round
  cord hole gained a channel through the bottom edge (the numeric cord
  caption moved just left of the channel in Visual mode).
- **README, starter guide, measuring guide, and outlines guide**
  updated for the open-slot gauge usage, the two label-mode presets
  (ADA 703 naming: modes named by modality, Visual/Tactile), the
  Tactile post-print fold steps, and a hinge material note (PETG/PP
  folds more reliably than PLA; fold once, gently).

## [0.10.0] - 2026-07-23

Makes Step 3 shape both tools, replaces the finger stencil with a full
measuring kit (match your plug by touch or measure it), and adds a
single starter guide — with a printable PDF that carries its own 1:1
paper stencil — as the one page to start from.

### Added

- **Measuring stencil** (`Measuring_Stencil.scad`, pre-rendered
  `stl/Measuring_Stencil.stl`): the finger-sizing stencil grown into a
  full measuring kit of thin cards, each with a raised two-letter ID
  readable by touch — P1/P2/P3 plug silhouette cards (width + thickness
  cutouts and a cord hole per Step 1 preset: hold your plug in the
  opening, no ruler needed), R1 tactile ruler (raised mm ticks,
  debossed numerals, edge notches every 10 mm), C1 cord gauge
  (Ø 3–9 mm holes), and F1/F2 finger cards (the 18 labeled holes,
  Ø 15–25 / Ø 26–32). Customizer `bed_width` / `bed_depth` /
  `part_index` split the cards onto print sheets automatically for
  small printers (console echoes the sheet map; oversize cards are
  reported and isolated). Preset dimensions are drift-tested against
  the main model by `tests/test_stencil_data.py`.
- **Starter guide** (`docs/guides/starter-guide.md`): the single
  entry-point walkthrough — Path A "match a preset with the stencil
  cards" / Path B "measure with R1/C1/F1/F2", the stencil card legend,
  the Customizer steps, and a per-step map of which tool each step
  shapes. Ships as a printable PDF
  (`docs/Plug_Puller_Starter_Guide.pdf`, built by
  `scripts/build_starter_guide_pdf.py`) whose last page is a 1:1 paper
  stencil sheet (`docs/guides/stencil-sheet.svg`, generated by
  `scripts/generate_stencil_sheet.py`) — calibration square, P1–P3
  silhouettes, 100 mm ruler, and finger circles for people without a
  3D printer.
- **Clamshell Step 3 wiring**: the Step 3 Attachment dropdown now
  shapes the heavy-duty clamshell too — `Zip ties` / `None` remove the
  velcro strap slots, `Velcro strap` / `None` remove the zip stations,
  and `strap_width` widens the arm slots (up to the arm window). Two
  new in-model warnings: WC-10 (zip stations disabled by Step 3 — the
  zip ties are what hold the two plates together) and WC-11 (strap
  wider than the arm slot window). Covered by a new render test
  (`tests/test_clamshell_attachment.py`).

### Changed

- **Customizer copy**: every step tab now says which tool it shapes —
  Step 4 renamed to "Cord Hook - Flat Tool", `velcro_style` labeled
  flat-tool-only, `strap_width` documented for both tools, and the
  console echoes the resolved tool plus which settings it ignores.
- **README / guides** repointed at the new starter guide as the
  primary path; all finger-stencil references updated to the
  measuring stencil.

### Removed

- **Root wrapper `Plug_Puller.scad`**: open
  `src/Plug_Puller_Parametric.scad` directly (the wrapper confused
  "which file do I open?" and broke Customizer dropdowns in some
  builds when opened from the root).
- **`Finger_Sizing_Stencil.scad`** and `stl/Finger_Sizing_Stencil.stl`
  — superseded by the measuring stencil (its F1/F2 cards carry the
  same 18 holes).

## [0.9.0] - 2026-07-23

One step from the **v1.0 public milestone**: the release that makes the
public repo self-validating (tests + CI), zero-install customizable
(browser path), and illustrated (guide photos).

### Added

- **Engineering pipeline** ported from the development repo: the full
  pytest suite (7 golden STL fixtures rendered from `src/` with
  OpenSCAD 2026.01.03 + Manifold, mesh comparison via trimesh,
  Customizer hygiene / preset routing / fit-derivation / parameter
  schema / flattened-build parity tests), the `stl-validation.yml`
  GitHub Actions workflow (lint → quick tests → full render validation
  → fixture integrity), and the build scripts
  (`scripts/build_flattened.py`, `scripts/generate_outline_sheets.py`,
  `scripts/build_outline_sheets_pdf.py`,
  `scripts/regenerate_fixtures.py`). Fixtures are plain committed STLs
  — no Git LFS needed to clone or run CI.
- **Mesh-health guards**: `tests/test_shipped_stls.py` pins every
  shipped STL as watertight/winding-consistent and keeps the Small /
  Medium / Large downloads mesh-equivalent to their golden fixtures;
  `tests/test_preset_renders.py` renders every saved parameter set and
  fails on any `WARNING:`/`undefined` console output or non-watertight
  mesh. Audit confirmed all shipped meshes healthy and all presets
  warning-free.
- **Zero-install web customizer path**: `docs/guides/web-customizer.md`
  walks through customizing in the browser via the OpenSCAD Playground
  (loading `dist/Plug_Puller_SingleFile.scad` from the repo), with a
  manual load fallback and phone usage notes; the README links it
  prominently ("Customize in your browser — no install").
- **MakerWorld listing draft** (`docs/makerworld-listing.md`): full
  Parametric Model Maker listing text and publish checklist, gated
  behind an explicit maintainer licensing decision (MakerWorld
  platform grant alongside PolyForm NC 1.0.0, or stay
  playground-only).
- **Guide photos and preview renders** (`docs/images/`): real photos of
  the printed heavy-duty clamshell (plates, zip-tie assembly,
  assembled, in use at an outlet) embedded in the quick-start and
  measuring guides plus a README hero shot, and fresh OpenSCAD preview
  renders (Medium flat tool with the green confirmation tag, clamshell
  plate).
- **Try-before-you-print outline sheets**
  (`docs/guides/outline-sheets/`, 12 SVGs): a printable 1:1
  dimensioned silhouette of every quick-select combination — the three
  `plug_preset` families × Small / Medium / Large for the flat tool,
  plus the heavy-duty clamshell plate at all three sizes. Each sheet
  has CAD-style dimension lines, a 50 × 50 mm calibration square, the
  matching Customizer settings in the title block, and a how-to strip.
  Guide: `docs/guides/print-preview-outlines.md`. All twelve sheets are
  also bundled as one printable PDF with a cover index
  (`docs/Plug_Puller_Outline_Sheets.pdf`), page size 210 × 279 mm so it
  prints 1:1 on both A4 and US Letter.
- **Finger-sizing stencil** (`Finger_Sizing_Stencil.scad` at the repo
  root, pre-rendered `stl/Finger_Sizing_Stencil.stl`): a thin
  parametric plate with the measuring template's 18 finger-sizing
  circles (Ø 15–32 mm) as labeled through-holes — the no-scissors way
  to find `measure_finger_width`. A `split_halves` option splits it
  into two smaller plates for tight beds.
- README, measuring guide, and quick-start cross-links to the new
  sheets and stencil.

## [0.8.0] - 2026-07-22

First public release.

### Added

- Unified two-tool parametric model behind a Step 0 `tool_style`
  selector:
  - **Flat tool** — a slab with a taper-aware two-level plug pocket
    whose side walls follow a parametric plug side rail, rail-placed
    zip-tie holes and velcro slots, mirrored finger holes, a chiral
    J-hook cord catch, and a plug wall notch.
  - **Heavy-duty clamshell** — two identical serrated collar plates
    that zip-tie face to face around a thick extension-cord plug.
  - `Auto from plug` picks the right tool from the plug measurements.
- Measurement-first Customizer: numbered Steps 0–4 for beginners,
  `Advanced -` sections for power users, `(Custom size only)` sections
  for experts.
- `plug_preset` quick-select calibrated to three reference plugs
  (2-prong lamp NEMA 1-15, standard 3-prong NEMA 5-15, heavy-duty
  round NEMA 5-15) plus `Measure my plug` manual entry.
- Sizes `Small` / `Medium` / `Large` grounded in ANSUR-II hand
  anthropometry, plus `Measure my hand` and full `Custom` unlock.
- Auto-fit bounds clamping and in-model validation warnings (flat tool
  W-1…W-19, clamshell WC-1…WC-9) printed as red tags next to the part.
- Flattened single-file build (`dist/Plug_Puller_SingleFile.scad`) for
  MakerWorld Parametric Model Maker and other web customizers.
- Example saved parameter sets (`presets/Plug_Puller_Parametric.json`)
  and a machine-readable parameter schema (`parameter_mapping.json`,
  103 parameters).
- Beginner guides (quick start, measuring guide with printable 1:1
  template, fit troubleshooting), a power-user guide, printable PDF
  guides, and a full engineering reference
  (`docs/Plug_Puller_Reference.md`).
- Ready-to-print Small / Medium / Large sample STLs in `stl/`.

[0.12.0]: https://github.com/BrennenJohnston/openscad-plug-puller/releases/tag/v0.12.0
[0.11.0]: https://github.com/BrennenJohnston/openscad-plug-puller/releases/tag/v0.11.0
[0.10.0]: https://github.com/BrennenJohnston/openscad-plug-puller/releases/tag/v0.10.0
[0.9.0]: https://github.com/BrennenJohnston/openscad-plug-puller/releases/tag/v0.9.0
[0.8.0]: https://github.com/BrennenJohnston/openscad-plug-puller/releases/tag/v0.8.0
