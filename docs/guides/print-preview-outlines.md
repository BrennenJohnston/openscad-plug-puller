# Try Before You Print — 1:1 Outline Sheets and the Finger-Sizing Stencil

Not sure which quick-select combination to print? You can test the fit
**on paper first**. This folder of printable sheets and one thin
3D-printable stencil let you check a tool against your real plug, your
real wall plate, and your real fingers before you spend hours printing
the actual tool.

Two things live here:

1. **[Outline sheets](outline-sheets/)** — one printable page per
   quick-select combination. Each page shows that tool's exact
   silhouette at **1:1 scale** with CAD-style dimensions: cut it out,
   hold it against your plug, and try the finger holes. All twelve
   sheets are also bundled into one printable PDF with a cover index:
   **[`docs/Plug_Puller_Outline_Sheets.pdf`](../Plug_Puller_Outline_Sheets.pdf)**.
2. **[`Finger_Sizing_Stencil.stl`](../../stl/Finger_Sizing_Stencil.stl)** —
   a thin printable plate with all 18 finger-sizing circles from the
   measuring template as real through-holes. The no-scissors way to find
   your `measure_finger_width`.

---

## The outline sheets

Every quick-select combination in the Customizer has a sheet — the
three `plug_preset` plug families × the three hand sizes for the flat
tool, plus the heavy-duty clamshell plate at the three hand sizes (the
plate's finger holes follow the Size selection too):

| Plug preset | Small | Medium | Large |
| ----------- | ----- | ------ | ----- |
| Flat 2-prong lamp plug (NEMA 1-15) | [sheet](outline-sheets/outline_flat-2-prong_small.svg) | [sheet](outline-sheets/outline_flat-2-prong_medium.svg) | [sheet](outline-sheets/outline_flat-2-prong_large.svg) |
| Standard 3-prong plug (NEMA 5-15) | [sheet](outline-sheets/outline_standard-3-prong_small.svg) | [sheet](outline-sheets/outline_standard-3-prong_medium.svg) | [sheet](outline-sheets/outline_standard-3-prong_large.svg) |
| Heavy-duty extension cord (NEMA 5-15), flat tool | [sheet](outline-sheets/outline_heavy-duty-round_small.svg) | [sheet](outline-sheets/outline_heavy-duty-round_medium.svg) | [sheet](outline-sheets/outline_heavy-duty-round_large.svg) |
| Heavy-duty clamshell plate | [sheet](outline-sheets/outline_heavy-duty-clamshell_small.svg) | [sheet](outline-sheets/outline_heavy-duty-clamshell_medium.svg) | [sheet](outline-sheets/outline_heavy-duty-clamshell_large.svg) |

Prefer one file? **[`docs/Plug_Puller_Outline_Sheets.pdf`](../Plug_Puller_Outline_Sheets.pdf)**
bundles all twelve sheets behind a cover page with a page index — open
it, print just the page you need (at 100 %), done.

Each sheet fits both **A4 and US Letter** paper and contains:

- the tool outline at **exact 1:1 scale** — solid line = the outer
  edge, dashed lines = holes and the plug pocket,
- CAD-style dimension lines with mm values,
- a **50 × 50 mm calibration square**,
- a title block naming the combination and the exact **Customizer
  settings** that reproduce it,
- a short how-to strip at the bottom.

### Printing at 100 %

The whole point of these sheets is true scale, so the print dialog
matters:

1. Print at **100 % / "Actual size"** — never "fit to page", "shrink to
   fit", or any scale other than 100 %.
2. **Measure the calibration square** with a ruler. It must be exactly
   **50 × 50 mm**. If it is not, your print was scaled — fix the dialog
   and re-print before trusting anything on the sheet.

### Testing the fit

1. **Cut out the silhouette** along the solid outline. Poke through the
   two big finger circles (dashed).
2. **Hold it against your plug** on the wall: the plug should fit
   inside the dashed pocket outline, and the notch at the top edge
   should straddle the wall plate. On the clamshell sheets, the plug
   body sits between the two serrated V-edges with the cord in the
   bottom channel.
3. **Try the finger holes.** If they feel wrong, try the neighbouring
   size's sheet — or skip the scissors and print the
   [finger-sizing stencil](#the-finger-sizing-stencil) below.
4. Found your combination? Open the Customizer, set the values from the
   sheet's title block, and follow the
   [Quick Start](quick-start-beginner.md) to export and print the real
   tool.

> These sheets cover the **quick-select presets only**. If your plug or
> hand is between sizes, use the [Measuring Guide](measuring-guide.md)
> instead — the measured tool will fit better than any preset.

---

## The finger-sizing stencil

[`Finger_Sizing_Stencil.stl`](../../stl/Finger_Sizing_Stencil.stl)
(source: [`Finger_Sizing_Stencil.scad`](../../Finger_Sizing_Stencil.scad)
at the repo root) is a 1.2 mm plate with the 18 sizing circles
(Ø 15–32 mm) from the
[measuring template](measuring-template.svg) as real through-holes,
each labeled with its diameter, plus the sizing rule debossed on the
plate:

> **finger width = hole number − 5** (your middle finger passes Ø 26
> comfortably → enter `measure_finger_width = 21`).

It replaces cutting out the template's paper circles, and it is
reusable — handy for occupational therapists or anyone sizing tools
for several people.

### Print settings

- **Footprint:** ≈ 157 × 156 mm. Bed smaller than that? Open the
  `.scad` in OpenSCAD and set **`split_halves = true`** in the
  Customizer to get two half-plates (≈ 157 × 80 and 145 × 96 mm), then
  render (F6) and export your own STL.
- **Material:** PETG or PLA — anything rigid.
- **Layer height:** 0.2 mm (the plate is 6 layers).
- **Supports:** none. **Infill:** any (the plate is solid at this
  thickness). **Walls:** 2 is plenty.
- The labels are debossed 0.6 mm into the top face — they print
  cleanly with no bridging.

### Using it

Find the **smallest hole your middle finger passes through
comfortably** (down to the middle knuckle, no forcing). Subtract 5 from
that hole's number and enter the result as `measure_finger_width` in
the Customizer (Step 2, size = `Measure my hand`).
