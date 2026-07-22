// Plug_Puller.scad — Root entry point.
//
// Open this file in OpenSCAD. It includes the canonical parametric model so
// the Customizer parameters and rendered geometry are identical to opening
// src/Plug_Puller_Parametric.scad directly.
//
// The model unifies two tools behind a single `tool_style` selector: the
// flat tool (rail-based zip/velcro placement, taper-aware pocket) and the
// heavy-duty clamshell (two identical serrated collar plates). It ships plug
// presets calibrated to three reference plugs (2-prong lamp, 2-prong
// standard, 3-prong heavy-duty).

include <src/Plug_Puller_Parametric.scad>
