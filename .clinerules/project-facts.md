# Project Facts — openscad-plug-puller (always active)

Parametric handheld Plug Puller assistive device (current line, v0.11.0).
Working branch: main. The older plug-puller-openscad repo is ARCHIVED — never
copy patterns from it without asking me.

1. Main model: src\Plug_Puller_Parametric.scad. Presets: src\presets.scad.
   Fit calibration: src\fit_measured.scad. Measuring_Stencil.scad prints a
   sizing stencil. dist\ holds the generated single-file release — regenerate,
   never hand-edit.
2. Named checks: powershell -ExecutionPolicy Bypass -File scripts\scad-check.ps1
   (after every .scad edit) and python -m pytest tests/ -v (before commits).
   CI renders with OpenSCAD 2026.01.03 — same as the local canonical binary.
3. Grip dimensions, actuation force, and finger clearances are the
   accessibility features: all are parameters with min/max asserts sized from
   user measurements (the stencil) — never hardcode hand-size assumptions,
   and propose changes with trade-offs for me to decide.
