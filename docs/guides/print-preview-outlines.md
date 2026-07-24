# Try Before You Print — 1:1 Outline Sheets and the Measuring Stencil

Not sure which quick-select combination to print? You can test the fit
**on paper first**. This folder of printable sheets and one thin
3D-printable stencil set let you check a tool against your real plug,
your real wall plate, and your real fingers before you spend hours
printing the actual tool.

Two things live here:

1. **[Outline sheets](outline-sheets/)** — one printable page per
   quick-select combination. Each page shows that tool's exact
   silhouette at **1:1 scale** with CAD-style dimensions: cut it out,
   hold it against your plug, and try the finger holes. All twelve
   sheets are also bundled into one printable PDF with a cover index:
   **[`docs/Plug_Puller_Outline_Sheets.pdf`](../Plug_Puller_Outline_Sheets.pdf)**.
2. **[`Measuring_Stencil.stl`](../../stl/Measuring_Stencil.stl)** — a
   printable set of thin measuring cards: plug-preset silhouettes
   (P1/P2/P3), a tactile mm ruler (R1), a cord gauge (C1), and the 18
   finger-sizing holes (F1/F2). The no-scissors, no-caliper way to
   answer the whole measuring worksheet — see the
   [Starter Guide](starter-guide.md) for the card legend.

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
   [measuring stencil](#the-measuring-stencil) below.
4. Found your combination? Open the Customizer, set the values from the
   sheet's title block, and follow the
   [Quick Start](quick-start-beginner.md) to export and print the real
   tool.

> These sheets cover the **quick-select presets only**. If your plug or
> hand is between sizes, use the [Measuring Guide](measuring-guide.md)
> instead — the measured tool will fit better than any preset.

---

## The measuring stencil

[`Measuring_Stencil.stl`](../../stl/Measuring_Stencil.stl)
(source: [`Measuring_Stencil.scad`](../../Measuring_Stencil.scad)
at the repo root) is a set of 1.2 mm measuring cards, each with a
raised 2-character ID you can read by touch:

| ID | Card | Worksheet numbers it answers |
| -- | ---- | ---------------------------- |
| **P1 / P2 / P3** | Plug preset silhouettes (lamp / standard 3-prong / heavy-duty). Hold your plug in the **W** (width) and **T** (thickness) cutouts — if it fills them and the cord slips sideways into the open cord slot, that preset fits: pick it in Step 1 and skip measuring | all of 1–6, by preset match |
| **R1** | Tactile mm ruler — raised ticks, edge notches every 10 mm | 1–5 |
| **C1** | Cord gauge — open slots Ø 3–9 mm through the bottom edge; slides onto an installed cord from the side | 6 |
| **F1 / F2** | The 18 finger-sizing circles (Ø 15–32 mm) from the [measuring template](measuring-template.svg) as real through-holes | 8 |

The finger rule is debossed on the F cards:

> **finger width = hole number − 5** (your middle finger passes Ø 26
> comfortably → enter `measure_finger_width = 21`).

It replaces cutting out the template's paper circles, and it is
reusable — handy for occupational therapists or anyone sizing tools
for several people.

A **Tactile** version
([`stl/Measuring_Stencil_Tactile.stl`](../../stl/Measuring_Stencil_Tactile.stl),
or the `label_mode = Tactile` Customizer preset) swaps the debossed
lettering for raised ADA-size characters and adds a fold-flat
**Grade 2 braille title flap** to every card — see the
[Starter Guide](starter-guide.md#tactile-version-raised-characters--braille)
for the post-print fold steps.

### Print settings

- **Footprint:** the cards pack onto sheets automatically. On a
  200 × 200 mm bed the set is two sheets. Smaller bed? Open the `.scad`
  in OpenSCAD, set **`bed_width` / `bed_depth`** to your bed, and
  render **`part_index`** = 1, 2, … to export one sheet at a time
  (`part_index = 0` previews every sheet; the console lists which
  cards land on which sheet).
- **Material:** PETG or PLA — anything rigid.
- **Layer height:** 0.2 mm (the cards are 6 layers).
- **Supports:** none. **Infill:** any (the cards are solid at this
  thickness). **Walls:** 2 is plenty.
- The labels are debossed 0.6 mm into the top face and the card IDs
  are raised 0.8 mm — both print cleanly with no bridging.

### Using it

Start with the plug cards: if your plug fills a P card's cutouts, pick
that preset in Step 1 — done. Otherwise measure with R1 (lengths and
widths), C1 (cord), and the worksheet in the
[Measuring Guide](measuring-guide.md). For your finger, find the
**smallest hole your middle finger passes through comfortably** (down
to the middle knuckle, no forcing) on F1/F2, subtract 5 from that
hole's number, and enter the result as `measure_finger_width` in the
Customizer (Step 2, size = `Measure my hand`).
