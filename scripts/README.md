# scripts/

Utility scripts used to build and validate the Plug Puller model's committed artifacts. All paths are relative to the repo root; run them from there, e.g. `python scripts/build_flattened.py`.

## Contents

| Script | Purpose |
|--------|---------|
| `build_flattened.py` | Deterministically inline the include tree (`src/fit_measured.scad` + `src/presets.scad`) into `dist/Plug_Puller_SingleFile.scad` for web customizers (MakerWorld PMM, openscad-playground `?src=` loading); `--check` verifies freshness (CI does this on every run). |
| `regenerate_fixtures.py` | Re-render every golden STL under `tests/fixtures/<name>/reference.stl` from its `params.json`, and refresh the matching `metadata.json` with OpenSCAD version + trimesh measurements. Run after any intentional SCAD change so the mesh-comparison tests in `tests/test_render_modes.py` keep validating actual deltas, not stale references. |
| `build_release_stls.py` | Render the committed ready-to-print library under `stl/`: 9 plug tools (3 plug presets × 3 hand sizes, in `stl/Plug-Puller/`) + 16 measuring-stencil cards (Visual/Tactile full sets and individual cards, in `stl/Measuring-Stencil/`). Each output is watertight-checked. Run after any intentional model change and commit the refreshed `stl/`; `tests/test_shipped_stls.py` reuses this script's job catalog to guard the shipped files. Use `--only plug-puller` / `--only stencil` to rebuild one group. |
| `generate_outline_sheets.py` | Generate the try-before-you-print outline sheets (`docs/guides/outline-sheets/`, 12 SVGs): render each quick-select combination (3 plug presets × 3 sizes flat tool + 3 clamshell sizes) via the OpenSCAD CLI, extract the true 1:1 silhouette / through-holes / pocket opening with trimesh + shapely, compute the labeled dimensions from `tests/fit_formulas.py`, and compose A4/Letter SVG sheets with CAD dimension lines and a calibration square. Asserts dimension parity between the mesh, the formulas, and the sheet before writing. Re-run after any geometry or preset change. |
| `build_outline_sheets_pdf.py` | Bundle the 12 outline-sheet SVGs into the printable `docs/Plug_Puller_Outline_Sheets.pdf` (cover/index page + one sheet per page) via headless Edge/Chrome — the same Skia print pipeline as the other PDF guides. The `@page` size equals the SVG page (210 × 279 mm) so the sheets keep their exact 1:1 scale; the script verifies the page count and every page's MediaBox after printing. Run after `generate_outline_sheets.py`. |
| `generate_stencil_sheet.py` | Emit `docs/guides/stencil-sheet.svg`, the 1:1 paper alternative to the 3D-printable `Measuring_Stencil.scad`: one 210 × 279 mm page with the 50 mm calibration square, the P1–P3 plug silhouettes, a 100 mm ruler, and the 18 finger circles. Its `PLUG_PRESET_DIMS` constant is drift-tested against both SCAD files by `tests/test_stencil_data.py`. Re-run after any preset-dimension change. |
| `build_starter_guide_pdf.py` | Build the printable `docs/Plug_Puller_Starter_Guide.pdf`: the starter guide (`docs/guides/starter-guide.md`) condensed onto two typeset pages, plus the stencil sheet SVG as the final page at exact 1:1 scale. Reuses the outline-sheets print/verify pipeline. Run after `generate_stencil_sheet.py`. |

## Prerequisites

- Python 3.11+ with the dev dependencies installed: `pip install -r requirements-dev.txt`
- OpenSCAD 2026.01.03+ nightly (Manifold backend) on `PATH`, or set `OPENSCAD_PATH` — needed by `regenerate_fixtures.py` and `generate_outline_sheets.py`.
- Microsoft Edge or Chrome — needed by `build_outline_sheets_pdf.py` and `build_starter_guide_pdf.py` for headless SVG-to-PDF printing.

## Historical tooling

Earlier development-era scripts (reference-mesh measurement, outline fitting, fidelity reports, DXF conversion helpers) live in the historical dev repo, [`plug-puller-openscad`](https://github.com/BrennenJohnston/plug-puller-openscad). The DXF → OpenSCAD polygon converter is its own package: [`cad-to-openscad-pipeline`](https://github.com/BrennenJohnston/cad-to-openscad-pipeline).
