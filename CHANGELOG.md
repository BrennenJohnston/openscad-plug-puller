# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Versions below 1.0.0 are public preview releases: the model is complete
and print-tested, but small refinements are expected before the **v1.0
public milestone**.

## [Unreleased]

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

[0.9.0]: https://github.com/BrennenJohnston/openscad-plug-puller/releases/tag/v0.9.0
[0.8.0]: https://github.com/BrennenJohnston/openscad-plug-puller/releases/tag/v0.8.0
