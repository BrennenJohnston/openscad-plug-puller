# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Versions below 1.0.0 are public preview releases: the model is complete
and print-tested, but small refinements are expected before the **v1.0
public milestone**.

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

[0.8.0]: https://github.com/BrennenJohnston/openscad-plug-puller/releases/tag/v0.8.0
