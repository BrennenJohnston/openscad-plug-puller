# MakerWorld Quick Start — Plug Puller

This page goes with the MakerWorld listing. It covers what is particular to
MakerWorld: which file to upload, how its customizer differs from the
desktop program, and where the full instructions are.

The Plug Puller comes as two tools, each a single file that is the whole
upload for its tool:

- the **one-sided puller**,
  [`dist/Plug_Puller_SingleFile.scad`](../dist/Plug_Puller_SingleFile.scad):
  one slab with a pocket shaped to your plug, two finger holes and a cord
  hook, for lamp plugs, standard 3-prong plugs and other plugs thinner than
  24 mm. Print one.
- the **two-sided puller**,
  [`dist/Plug_Puller_Two_Sided_SingleFile.scad`](../dist/Plug_Puller_Two_Sided_SingleFile.scad):
  two identical serrated plates that zip-tie around a thick round
  extension-cord plug, a USB-C tip or a charger plug. The download holds
  both plates: print it, flip one plate over, and zip-tie the pair face to
  face.

If your plug is 24 mm thick or more, the one-sided file shows a red tag,
`PLUG THICKER THAN 24MM - USE THE TWO-SIDED PULLER FILE`: switch to the
two-sided file.

Each tool has a **quick start** (get the file, measure, the four Customizer
steps, print, assemble, use) and a **full guide** (every dial with a
picture, fit troubleshooting, every warning, the advanced dials), each as a
page and as a printable PDF whose last pages are the measuring form and the
paper measuring stencil at true size:

| Tool | Quick start | Full guide |
| ---- | ----------- | ---------- |
| One-sided puller | [page](guides/one-sided/quick-start.md), [PDF](Plug_Puller_One_Sided_Quick_Start.pdf) | [page](guides/one-sided/full-guide.md), [PDF](Plug_Puller_One_Sided_Full_Guide.pdf) |
| Two-sided puller | [page](guides/two-sided/quick-start.md), [PDF](Plug_Puller_Two_Sided_Quick_Start.pdf) | [page](guides/two-sided/full-guide.md), [PDF](Plug_Puller_Two_Sided_Full_Guide.pdf) |

---

## Using the MakerWorld customizer

1. Go to MakerWorld, then **Create**, then **Parametric Model Maker**, and
   upload the file for your tool.
2. Work the form top to bottom: **Step 1 - Your Plug** (a preset, or
   `Measure my plug` and your numbers in mm), **Step 2 - Size**, **Step 3 -
   Attachment**, then Step 4. The quick start explains every field, with a
   picture of what it changes. Everything below Step 4 is optional.
3. Generate and render, then look at the rendered model for **red text**
   beside the part. It names a measurement to fix, and it is part of the
   model: exported with it, it prints as an extra object on your bed. Clear
   every red tag before you download.
4. Download the STL and print it with the settings in the quick start:
   flat on the bed as modeled, no supports, 0.2 mm layers, 3 to 4 walls, 25
   to 35 percent infill, PETG.

## What MakerWorld's preview does not show

MakerWorld renders the finished model only. The red warning tags show,
because they are part of the model. These do not:

- the see-through plug that the desktop program draws from your numbers;
- the green tag that confirms which numbers were applied (one-sided);
- the orange notes about ignored Custom dials, auto-fit adjustments
  (one-sided) and a strap slot left out for a short plug (two-sided).

If you want to see them, open the same file in the desktop program or in
the browser, as the quick start's "Get the file" section describes.

## Other ways to customize

- **The OpenSCAD Playground**, in your browser, no account and no upload:
  [the one-sided puller](https://ochafik.com/openscad2/#url=https://raw.githubusercontent.com/BrennenJohnston/openscad-plug-puller/main/dist/Plug_Puller_SingleFile.scad)
  or
  [the two-sided puller](https://ochafik.com/openscad2/#url=https://raw.githubusercontent.com/BrennenJohnston/openscad-plug-puller/main/dist/Plug_Puller_Two_Sided_SingleFile.scad).
  It shows the green and orange notes but not the see-through plug, and it
  renders slowly. The full guide's "Working in the browser" section has the
  details.
- **Desktop OpenSCAD**, the most accessible of the three with a screen
  reader: the design is a text file, the Customizer panel is native, and
  the console messages are readable, including the auto-fit detail that
  neither MakerWorld nor the Playground shows well.
- This project is not bundled in
  [OpenSCAD Assistive Forge](https://openscad-assistive-forge.pages.dev/).
  It is a reasonable future candidate, which would add a screen-reader-first
  parameter form, presets and offline use; it is not there today.

## Resources

- [This project on GitHub](https://github.com/BrennenJohnston/openscad-plug-puller)
- [Smith-Kettlewell *3D Printing for Blind & Low Vision Makers*](https://www.ski.org/technical-file/3d-printing-for-bvi-makers/):
  printer and slicer guidance for the part of the workflow this model
  cannot cover. Slicer accessibility is a real barrier:
  [Ballarin, Stangl, Oswal, Whiting, DIS 2025](https://doi.org/10.1145/3715668.3736342)
  measured that much of Cura's, PrusaSlicer's and Bambu Studio's interfaces
  is invisible to the accessibility APIs screen readers use, which is why
  the print settings in the guides are written out as text rather than
  shown as a screenshot.
