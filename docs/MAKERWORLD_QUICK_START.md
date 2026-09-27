# MakerWorld Quick Start — Plug Puller

This guide takes you from "I cannot get this plug out of the wall" to a
downloadable, print-ready STL shaped to your plug and your hand, using
[MakerWorld](https://makerworld.com/)'s Parametric Model Maker. The Plug Puller
comes as two tools, each a single file:
[`dist/Plug_Puller_SingleFile.scad`](../dist/Plug_Puller_SingleFile.scad) for
the one-sided puller and
[`dist/Plug_Puller_Two_Sided_SingleFile.scad`](../dist/Plug_Puller_Two_Sided_SingleFile.scad)
for the two-sided puller. Each file is the whole upload for its tool.

Both tools grip a plugged-in plug and give you two large finger holes, so pulling
the plug uses your whole hand instead of a fingertip pinch. They only ever touch
the plug's sides and back — nothing goes between the plug face and the outlet.

You will need a few measurements — six for the one-sided puller, four for the
two-sided puller — or a preset if your plug is a common one. Section 2 covers
both routes.

---

## 1. Which tool you are making

Two tools, each in its own file. Pick the file before you start.

**The one-sided puller** (`Plug_Puller_SingleFile.scad`) is one slab with a
pocket shaped to your plug, two finger holes, a J-hook for the cord, and slots
for zip ties or a velcro strap. You slide it over the plug and pull with your
whole hand. It fits lamp plugs, standard 3-prong plugs, and other plugs thinner
than 24 mm. **Print one.**

**The two-sided puller** (`Plug_Puller_Two_Sided_SingleFile.scad`) is for fat
round extension-cord plugs, USB-C tips, and charger plugs. Two identical plates
with serrated inner arms grip the plug's sides and zip ties cinch them together.
**The download holds both plates side by side**: print it, flip one plate over,
and zip-tie the pair face to face.

If your plug is 24 mm thick or more, the one-sided file shows a red tag,
`PLUG THICKER THAN 24MM - USE THE TWO-SIDED PULLER FILE`. Switch to the
two-sided file. If your plug is borderline and the one-sided puller feels loose,
the two-sided puller is a reasonable choice too.

## 2. Getting your numbers

There are two routes and the preset route is genuinely fine for most people.

### Route A — use a preset

Set `plug_preset` in **Step 1 - Your Plug** to whichever matches:

| `plug_preset` | What it is | File |
|---------------|------------|------|
| `Flat 2-prong lamp plug - NEMA 1-15` | The thin two-blade plug on lamps and small appliances | one-sided, two-sided |
| `Standard 3-prong plug - NEMA 5-15` | The common three-pin plug with a round ground pin | one-sided, two-sided |
| `Wide 2-prong appliance plug - NEMA 1-15` | The wide flat plug on a vacuum or a kitchen appliance | one-sided |
| `Heavy-duty extension cord - NEMA 5-15` | Fat molded plug on a thick orange or brown extension cord | two-sided |
| `USB-C laptop tip` | The metal tip of a USB-C laptop charger cable, held from both sides | two-sided |

That is the whole of Step 1 if a preset fits. Skip to section 3.

### Route B — measure your plug

Set `plug_preset` to `Measure my plug` and type your numbers. All measurements
are in millimeters. **Measure the plug body, not the prongs.**

In the one-sided file, six numbers:

| Parameter | What to measure | Default |
|-----------|-----------------|---------|
| `measure_plug_length` | How far the plug body sticks out from the wall | 25.5 mm |
| `measure_plug_width_prong_end` | Width of the plug body just behind the prongs, the wide way | 25 mm |
| `measure_plug_width_cord_end` | Width at the end where the cord leaves | 25 mm |
| `measure_plug_thickness_prong_end` | Thickness just behind the prongs, the thin way | 20 mm |
| `measure_plug_thickness_cord_end` | Thickness at the cord end | 20 mm |
| `measure_cord_thickness` | Thickness of the cord itself | 4 mm |

Two ends for width and thickness because most plugs taper, and the taper is what
lets the pocket hold the plug rather than slide off it. If your plug does not
taper, enter the same number twice.

Then set `measure_wall_plate_style` to match your outlet cover: `Standard flat
plate`, `Rocker / Decora`, `Oversized / Jumbo`, or `No plate / flush`. This is what
lets the tool straddle the cover plate and sit flat against the wall instead of
rocking on it.

In the two-sided file, four numbers and one choice:

| Parameter | What to measure | Default |
|-----------|-----------------|---------|
| `measure_plug_length` | How far the plug body sticks out; on a laptop or charger, from the device's edge | 25.5 mm |
| `measure_plug_width_prong_end` | The size the two plates close across, just behind the prongs (or the metal tip); on a round plug, the diameter | 20 mm |
| `measure_plug_width_cord_end` | The same direction, where the cord leaves the plug body | 20 mm |
| `measure_cord_thickness` | Thickness of the cord itself | 4 mm |

Then set `plug_sides`: `Rounded sides` (the default) for a round plug, a USB-C
or charger tip — the plates get a sloped cradle that centers the plug and
forgives a small measuring error — or `Flat sides` for a boxy plug, where the
plates stay straight so the teeth bite along the whole side.

**If measuring with a ruler is the hard part,** the source repository has a
printable **measuring stencil**: thin cards with plug-shaped cutouts you match
your plug against, a 100 mm tactile ruler with 10 mm notches, a cord gauge with
slots from 3 to 9 mm, and eighteen finger-sizing holes from 15 to 32 mm. You find
your numbers by fitting shapes rather than reading a scale. There is a tactile
version with raised ADA-size characters and a braille title flap on every card —
the braille is generated at build time in UEB Grade 2 and baked in, so there is no
translation step. See
[`docs/guides/starter-guide.md`](guides/starter-guide.md) in the repository.

The repository also has printable 1:1 outline sheets, so you can hold a paper
version of the finished tool against your plug before spending filament.

### Route C — match a preset by shape, not by name

If you have the printed measuring stencil, hold your plug against the P1, P2, and
P3 silhouette cards. Whichever card your plug fits is the preset to pick in Route
A — P1 and P2 in the one-sided file, P3 in the two-sided file. No numbers needed
at all.

## 3. Sizing it to your hand

`size` in **Step 2 - Size** is `Medium` by default. Small, Medium, and Large are
built from ANSUR II (2012) hand anthropometry spanning roughly the 5th percentile
female to the 95th percentile male, so one of the three fits most people.

If none does, set `size` to `Measure my hand` and two sliders appear:

- `measure_finger_width` (default 20 mm) — the width of your middle finger across
  its widest knuckle. This sets the finger holes.
- `measure_hand_width` (default 85 mm) — the width of your hand across the
  knuckles, thumb excluded. This sets the overall body width. One-sided puller
  only: the two-sided puller asks for the finger width alone.

Measuring for someone else is normal and the repository's measuring guide covers
it. Err on the generous side for the finger holes: a hole slightly too big is
usable and a hole slightly too small is not.

## 4. Using the customizer

1. Go to MakerWorld → **Create** → **Parametric Model Maker** and upload the
   file for your tool: `dist/Plug_Puller_SingleFile.scad` for the one-sided
   puller or `dist/Plug_Puller_Two_Sided_SingleFile.scad` for the two-sided
   puller. Each is the whole tool in one file.

In the one-sided file:

2. **Step 1** — set `plug_preset`, or set it to `Measure my plug` and enter your
   six numbers plus your wall-plate style.
3. **Step 2** — set `size`, or `Measure my hand` and your two numbers.
4. **Step 3** — `attachment` defaults to `Zip ties + Velcro`, which puts both sets
   of holes in. `Zip ties`, `Velcro strap`, and `None` are the alternatives. If you
   pick a velcro option, `velcro_style` is `Wing` (default) or `Classic slot`, and
   `strap_width` defaults to 15 mm — set it to your actual strap width; ONE-WRAP
   comes in 10, 13, 16, 20, and 25 mm.
5. **Step 4** — `hook_hand` is `Right` or `Left`.

In the two-sided file:

2. **Step 1** — set `plug_preset`, or set it to `Measure my plug` and enter your
   four numbers, then `plug_sides`.
3. **Step 2** — set `size`, or `Measure my hand` and your finger width.
4. **Step 3** — `attachment` is `Zip ties + Velcro strap` (the default) or
   `Zip ties`. The zip ties are what hold the two plates together, so both
   choices keep them. `strap_width` sizes the strap slot in each arm.
5. **Step 4** — `print_layout`: keep `Both plates`, and the download holds the
   whole tool.

Then, in either file:

6. **Generate and render, then check the rendered model for red tags.** See
   section 6 — this is the step people skip.
7. Download the STL.

Everything below Step 4 is optional. The advanced sections tune zip-tie and velcro
placement (one-sided), every plate dimension (two-sided), and render quality.
`quality` (in **Advanced - Render Quality**) defaults to 64 circle segments, which
is print-ready; drop it to 32 for a fast test render and put it back before you
export.

**A note on the two-sided puller:** the download holds **both plates**, side by
side, as two separate parts in one file. Most slicers load it as one object with
two parts, which prints fine as it is; use your slicer's split-to-objects command
if you want to move or turn the plates one at a time. After printing, flip one
plate over.

## 5. Printing it

**Print it flat, as modeled** — the one-sided puller pocket up, the two-sided
puller's plates as they lie in the file. No supports.

| Setting | Value | Why |
|---------|-------|-----|
| Orientation | flat face down, pocket up | No overhangs, no supports, and the layers run across the direction of pull |
| Layer height | 0.2 mm, or 0.16 mm | 0.16 gives crisper rim fillets on the 6.35 mm slab |
| Walls | 3–4 | This is a part you pull hard on |
| Infill | 25–35% cubic or gyroid | Same reason |
| Material | **PETG recommended** | Handles repeated flexing and the warmth near an outlet better than PLA. PLA, ABS, and ASA all work |
| Flexible filament | **no** | The tool has to stay rigid to transmit force to the plug |

If layers split at the pocket floor, raise the wall count and the infill. If a
J-hook snaps, reprint in PETG with 4 walls. On the two-sided puller, raise
`plate_wall_boost` or `plate_thickness` if a plate flexes under load.

**Two-sided puller assembly:** flip one plate over, put the pair face to face
around the plug, and thread zip ties through the matching holes. The serrated
inner arms do the gripping; the zip ties hold the two plates together.

**Safety.** The tool grips only the plug body's sides and back face. Nothing goes
between the plug and the outlet and nothing conductive is involved. Inspect the
print for cracks before each use and reprint if damaged. On a round plug with
little for the pocket to grip, a zip tie through the attachment holes adds real
security.

## 6. Reading the tags before you export

This model reports problems as **3D text in the model itself**, not console
messages — which is why it works on MakerWorld, where there is no console. Three
kinds of tag:

**Red `WARNING` tags** name a measurement or a geometry conflict to fix. They are
**part of the exported model**, so if you export with one showing, it prints as an
extra object on your bed. Always clear red tags before you download.

**Preview-only tags never show on MakerWorld,** because MakerWorld renders the
finished STL only. You see them in desktop OpenSCAD and in the OpenSCAD
Playground (section 8):

- **A green tag** (one-sided file) confirms what was applied, in the form
  `Medium: 25x25.5 PLUG, 20MM FINGER`. Read it back against what you typed.
- `CUSTOM SLIDERS IGNORED - SET SIZE = CUSTOM` (orange, one-sided) — you moved a
  `custom_*` slider while `size` is not `Custom`. Either set `size` to `Custom`
  or leave the advanced sliders alone.
- `AUTO-FIT ADJUSTED N VALUES - SEE CONSOLE` (orange, one-sided) — in Custom
  mode, auto-fit clamped some of your values to something buildable.
- `STRAP SLOT LEFT OUT - PLUG TOO SHORT FOR ONE` (orange, two-sided) — the plug
  is too short for a strap slot in the arms, so it was left out; the zip ties
  still hold the plates.

The see-through plug that desktop OpenSCAD draws from your numbers does not show
on MakerWorld either.

## 7. Troubleshooting

The red warning strings are exact. Find yours in the list.

### Measurement out of range

`CHECK PLUG LENGTH MEASUREMENT (MM?)` · `CHECK PLUG WIDTH MEASUREMENTS (MM?)` ·
`CHECK PLUG THICKNESS MEASUREMENTS (MM?)` · `CHECK CORD THICKNESS MEASUREMENT
(MM?)` · `CHECK FINGER WIDTH MEASUREMENT (MM?)` · `CHECK HAND WIDTH MEASUREMENT
(MM?)`

The `(MM?)` is the hint: a number this far out is usually inches typed into a
millimeter field. One inch is 25.4 mm. Re-measure in millimeters, or multiply.

### The measurements contradict each other

- `FINGER TOO BIG FOR HAND WIDTH - RECHECK BOTH` — a finger that wide does not
  belong to a hand that narrow. One of the two is wrong.
- `PLUG WIDTH TAPER TOO STEEP - RECHECK BOTH WIDTHS` (one-sided) and `PLUG WIDTH
  TAPER LOOKS WRONG - RECHECK BOTH ENDS` (two-sided) — the prong end and cord end
  differ by more than a real plug does. You probably measured different features
  at each end.

### The plug does not fit the design

- `PLUG TOO WIDE FOR THIS DESIGN (MAX 38MM)` — beyond what the one-sided puller
  can hold. Try the two-sided puller file.
- `PLUG THICKER THAN 24MM - USE THE TWO-SIDED PULLER FILE` — too thick for the
  one-sided pocket. Open the two-sided file and enter the plug there.
- `PLUG LONGER THAN POCKET LIMIT - POCKET SHORTENED` — informational; the tool
  will grip less of the plug's length than you asked for.
- `PLUG TOO LONG - PLATE OVER 120MM, CHECK PLUG LENGTH` (two-sided) — re-check
  `measure_plug_length`; you may have measured the cord.
- `CORD TOO THICK FOR HOOK SLOT` / `CORD TOO THICK FOR CABLE CHANNEL` — raise
  `measure_cord_thickness` only if it is genuinely that thick; otherwise on the
  two-sided puller raise `plate_cable_clearance`.
- `PLUG NARROWER THAN THE CORD CHANNEL - ARMS CANNOT TOUCH IT` (two-sided) — at
  one end the plug is narrower than the cord channel. Re-measure the plug widths
  and the cord itself, not its strain relief.
- `CRADLE SHALLOWER THAN ASKED - PLUG NARROW` (two-sided, `Rounded sides`) — the
  plug is so narrow next to its cord channel that the cradle was built shallower.
  Use a smaller `plate_cradle_depth`, or measure the cord itself, not its strain
  relief.

### Features are colliding

- `FINGER HOLES HIT PLUG POCKET` / `FINGER HOLES TOO CLOSE - WEAK BRIDGE` /
  `FINGER HOLES OUTSIDE BODY - INCREASE HAND WIDTH` — the hand size and the plug
  size do not leave room for both. Raise `measure_hand_width`, or drop to a
  smaller `size`.
- `ZIP TIE HOLES HIT FINGER HOLES` / `ZIP TIE ROWS OVERLAP EACH OTHER` / `ZIP TIE
  HOLES HIT VELCRO SLOTS` / `ZIP TIE GRID OUTSIDE BODY` / `ZIP TIE GRID BELOW CORD
  END` — set `zip_placement` back to `Auto` and let the model position them.
- `ZIP STATION OFF THE ARM` / `ZIP STATIONS OVERLAP EACH OTHER` / `ZIP STATION
  HITS VELCRO SLOT` (two-sided) — same fix: `plate_zip_placement` back to
  `Auto`.

### The part would not print or would not work

- `SEAT HAS NO RECESS - PLUG WONT NEST` / `POCKET HAS NO RECESS - PLUG WONT NEST` —
  the pocket floor is level with the face, so there is nothing to hold the plug.
- `SEAT FLOOR TOO THIN TO PRINT` / `POCKET FLOOR TOO THIN TO PRINT` — the floor
  under the pocket is thinner than the printer can make. Raise the body thickness.
- `PLATE THINNER THAN 2MM - TOO FLIMSY` (two-sided) — raise `plate_thickness`.
- `NO GRIP BITE - PLUG WONT BE HELD` (two-sided, `Flat sides` or the preset) —
  `plate_grip_bite` must be negative for the arms to actually close on the plug.
  Default is `-1`.
- `STEP 3 DISABLED ZIP HOLES - NOTHING SECURES THE TWO PLATES TOGETHER`
  (two-sided) — the plates need zip ties, and both Step 3 choices keep them, so
  you should not see this. Set `attachment` to `Zip ties` or `Zip ties + Velcro
  strap`.
- `WING OPENING SMALLER THAN STRAP WIDTH` / `WING WEB COLLAPSED - NO ROOM FOR
  STRAP` / `STRAP WIDER THAN ARM SLOT WINDOW - NARROW THE STRAP` — `strap_width`
  is larger than the slot can take. Lower it to your actual strap width.
- `PLUG SEAT OVERHANGS BODY - RECHECK PLUG WIDTH` / `PLUG POCKET OVERHANGS BODY -
  RECHECK PLUG WIDTH` / `PLUG TOO WIDE FOR TOOL END - CHECK PLUG WIDTH` /
  `POCKET WIDER THAN BODY` / `WALL NOTCH WIDER THAN TOP EDGE` — the plug is wide
  relative to the hand size. Go up a `size`, or re-check the width measurements.
- `PLUG TOO WIDE - ARMS BULGE PAST FINGER LOBES` (two-sided) — the plug is wider
  than the arms can wrap while keeping the finger lobes clear.

### The printed tool does not fit, with no warning shown

The model cannot check reality. `docs/guides/fit-troubleshooting.md` in the
repository walks through the fit cases symptom by symptom. The two most common:
the pocket is loose because the taper measurements were taken as if the plug were
square, and the tool rocks against the wall because
`measure_wall_plate_style` does not match the actual cover plate.

## 8. Alternative: OpenSCAD Playground

This project is **not** bundled in [OpenSCAD Assistive
Forge](https://openscad-assistive-forge.pages.dev/), so if the MakerWorld
customizer is difficult with your screen reader, the alternative here is the
**OpenSCAD Playground**, which runs OpenSCAD in your browser. Deep links straight
to the current files — the one-sided puller:

<https://ochafik.com/openscad2/#url=https://raw.githubusercontent.com/BrennenJohnston/openscad-plug-puller/main/dist/Plug_Puller_SingleFile.scad>

and the two-sided puller:

<https://ochafik.com/openscad2/#url=https://raw.githubusercontent.com/BrennenJohnston/openscad-plug-puller/main/dist/Plug_Puller_Two_Sided_SingleFile.scad>

How it compares:

- **No account and no upload.** Your measurements stay on your device; nothing is
  sent anywhere. The first visit downloads the engine, roughly 10 to 20 MB.
- **The same numbered sections.** Open the **Customize** panel and you get Steps
  1 through 4 in the same order as here.
- **The preview shows the tags, not the see-through plug.** Unlike MakerWorld,
  the Playground shows the green and orange preview tags; unlike desktop
  OpenSCAD, it does not draw the see-through plug.
- **It renders slowly.** Browser rendering takes 30 seconds to a few minutes,
  and several minutes on a phone. Drop `quality` to 32 for test renders and put it
  back to 64 before the final export.
- **You must render before exporting.** Exporting without rendering produces a
  tiny or empty STL.
- **If the deep link fails** — a "Failed to fetch" error or a blank editor —
  download the file for your tool from the repository's `dist/` folder and drag it
  into <https://ochafik.com/openscad2/> instead.
- **On a phone,** you will be switching between the editor, the customizer, and
  the preview rather than seeing them at once.
- **No braille translation**, because this model needs none; the plug presets are in the file itself, so they work in the Playground too.

The full Playground walkthrough is in
[`docs/guides/web-customizer.md`](guides/web-customizer.md).

Desktop OpenSCAD is the third route, and the most accessible of the three if you
already use a screen reader: the design is a text file, the Customizer panel is
native, and the console messages are readable — including the auto-fit detail that
neither MakerWorld nor the Playground shows you well. See
[`docs/guides/starter-guide.md`](guides/starter-guide.md).

This project is a reasonable future candidate for the Forge, which would add
screen-reader-first parameter UI, presets, and offline use. It is not there today.

## 9. Resources

- [Measuring guide](guides/measuring-guide.md) — every measurement with photos,
  a worksheet, and worked examples
- [Starter guide](guides/starter-guide.md) — the measuring stencil, the two
  measurement paths, and the desktop workflow
- [Fit troubleshooting](guides/fit-troubleshooting.md) — symptom-by-symptom fit
  fixes and the full warning decode
- [Web customizer guide](guides/web-customizer.md) — the OpenSCAD Playground
  walkthrough
- [This project on GitHub](https://github.com/BrennenJohnston/openscad-plug-puller)
- [Smith-Kettlewell *3D Printing for Blind & Low Vision Makers*](https://www.ski.org/technical-file/3d-printing-for-bvi-makers/)
  — printer and slicer guidance for the part of the workflow this model cannot
  cover. Relevant here because slicer accessibility is a real barrier:
  [Ballarin, Stangl, Oswal, Whiting, DIS 2025](https://doi.org/10.1145/3715668.3736342)
  measured that much of Cura's, PrusaSlicer's, and Bambu Studio's interfaces is
  invisible to the accessibility APIs screen readers use, which is why the print
  settings in section 5 are written out as text rather than shown as a screenshot.
