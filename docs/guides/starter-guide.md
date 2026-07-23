# Starter Guide — From "That Plug Is Stuck" to a Printed Tool

This is the one page to start from. It walks the whole path: figure out
your plug (two ways — match it or measure it), fill in the Customizer
steps, and print. Everything else in `docs/guides/` is a deep dive you
can open when this page points at it.

**What you need:** the plug you want to pull (in its outlet), and
either the printed **measuring stencil** or a ruler with mm markings.

> **No 3D printer handy yet?** There is a **paper version of the
> stencil**: print [`stencil-sheet.svg`](stencil-sheet.svg) at 100 %
> scale ("actual size", never "fit to page") and check its 50 × 50 mm
> calibration square. The same sheet ships inside the printable
> **[Starter Guide PDF](../Plug_Puller_Starter_Guide.pdf)** — this
> whole page plus the 1:1 stencil sheet in one document.

---

## The measuring stencil — card legend

Print [`stl/Measuring_Stencil.stl`](../../stl/Measuring_Stencil.stl)
(1.2 mm cards, no supports, any rigid filament). Each card has a
raised two-letter ID you can find by touch:

- **P1** — plug silhouette card: **flat 2-prong lamp plug** (NEMA 1-15)
- **P2** — plug silhouette card: **standard 3-prong plug** (NEMA 5-15)
- **P3** — plug silhouette card: **heavy-duty extension cord** (NEMA 5-15)
- **R1** — **ruler**: raised mm ticks, numerals every 10 mm, and edge
  notches every 10 mm you can count by touch
- **C1** — **cord gauge**: through-holes Ø 3–9 mm
- **F1 / F2** — **finger sizing**: the 18 labeled finger holes
  (Ø 15–25 on F1, Ø 26–32 on F2)

Each P card has three openings: **W** (the plug's width outline),
**T** (its thickness outline), and a round cord hole. The card is a
"does my plug match this preset?" test — no numbers involved.

### Printing the stencil on a small bed

The cards pack onto print sheets automatically. Open
[`Measuring_Stencil.scad`](../../Measuring_Stencil.scad) in OpenSCAD,
set **`bed_width`** and **`bed_depth`** to your printer's bed, and the
console lists which cards land on which sheet. Render with
**`part_index` = 1**, export the STL, print it, then repeat with
`part_index = 2`, and so on. (`part_index = 0` previews all sheets at
once — don't print that one.) A card larger than your bed is reported
in the console and placed alone on its own sheet.

---

## Path A — match a preset (fastest, no numbers)

1. Take the **P1**, **P2**, and **P3** cards to your plug.
2. Hold each card's **W** cutout over the plug (looking at its wide
   side), then the **T** cutout (looking at its thin side). Try the
   cord in the round hole.
3. **If the plug fills one card's openings** — snug, no big gaps —
   that preset is your plug:
   - P1 → Step 1 `plug_preset` = `Flat 2-prong lamp plug - NEMA 1-15`
   - P2 → Step 1 `plug_preset` = `Standard 3-prong plug - NEMA 5-15`
   - P3 → Step 1 `plug_preset` = `Heavy-duty extension cord - NEMA 5-15`
4. Skip to [Fill in the steps](#fill-in-the-customizer-steps) below.

No card fits? Your plug is between presets — take Path B; the measured
tool will fit better than any preset anyway.

## Path B — measure (about 5 minutes)

Work through the worksheet from the
[Measuring Guide](measuring-guide.md); the numbers below are the
worksheet's own numbering. Which card answers which number:

| Worksheet # | What | Stencil card |
| ----------- | ---- | ------------ |
| 1 | Plug length | **R1** — wall plate to the plug's back face |
| 2–3 | Plug width near the wall / near the cord | **R1** — hold the notched edge against the plug body |
| 4–5 | Plug thickness near the wall / near the cord | **R1** — same, across the thin direction |
| 6 | Cord thickness | **C1** — smallest hole the cord slides through |
| 7 | Wall plate style | your eyes — it's a picture quiz, see the [Measuring Guide](measuring-guide.md#7-wall-plate-style-a-picture-quiz-not-a-measurement) |
| 8 | Finger knuckle width | **F1 / F2** — smallest comfortable hole, **minus 5** |
| 9 | Hand width | **R1** — across the four knuckles, flat hand |

(8 and 9 are only needed if you pick `Measure my hand` in Step 2 —
the built-in Small / Medium / Large cover most hands.)

---

## Fill in the Customizer steps

Open [`src/Plug_Puller_Parametric.scad`](../../src/Plug_Puller_Parametric.scad)
in OpenSCAD and show the Customizer panel (`View ▸ Hide Customizer`
unchecked). Every click is spelled out in the
[Quick Start](quick-start-beginner.md); the short version:

- **Step 0 — Tool Style:** leave on `Auto from plug`. Thick round
  plugs (like P3) get the **heavy-duty clamshell**, everything else
  the **flat tool**.
- **Step 1 — Your Plug:** the preset from Path A, or your Path B
  numbers with `plug_preset` = `Measure my plug`.
- **Step 2 — Size:** `Medium` fits most adults; or `Measure my hand`
  with worksheet numbers 8–9.
- **Step 3 — Attachment:** how the tool attaches to the plug. Keep the
  default `Zip ties + Velcro` unless you know you want less.
- **Step 4 — Cord Hook:** `Right` or `Left` (flat tool only).

Press **F6** to render and `File ▸ Export ▸ STL` to save. The
clamshell is one plate — print it **twice**, flip one copy, zip-tie
the pair face to face around the plug.

### Which steps shape which tool

Each Customizer step says which tool it shapes; settings for the other
tool are simply ignored (the console tells you which ones). The map:

| Step | Flat tool | Heavy-duty clamshell |
| ---- | --------- | -------------------- |
| 0 — Tool style | picks it | picks it |
| 1 — Your plug | pocket, notch, hook slot | arm gap, arm length, cord channel |
| 2 — Size | finger holes, body size | finger bores |
| 3 — Attachment | zip-hole grid, velcro wings | zip stations, arm strap slots |
| 4 — Cord hook | J-hook direction | *ignored — no cord hook* |

On the clamshell, the Step 3 **zip ties are what hold the two plates
together** — leave them on unless you have another plan (the model
warns you if you turn them off).

---

## If the print doesn't fit

One symptom, one number to nudge:
**[Fit Troubleshooting](fit-troubleshooting.md)**. Want to sanity-check
before printing the real tool? Print a paper
**[1:1 outline sheet](print-preview-outlines.md)** of your combination
first.
