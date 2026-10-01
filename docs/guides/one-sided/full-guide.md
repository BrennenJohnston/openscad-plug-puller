# Full guide, one-sided puller

Everything about the one-sided puller: getting the file, measuring, every dial with a picture, printing, assembly, use and care, what to do when a print does not fit, every warning, and how the advanced dials work.

Model version 0.13.0. [The printable full guide](../../Plug_Puller_One_Sided_Full_Guide.pdf) has the same text, with the measuring form and the paper stencil sheets at true size as its last pages. The other document for this tool is [the quick start](quick-start.md). Each dial is headed by its plain name, with the name the Customizer shows on the line under it.

## Which tool this is

This guide is for the one-sided puller, src/Plug_Puller_Parametric.scad: the tool for a wall plug up to 24 mm thick, a pocket around the plug's back and sides with two finger holes below it, pulled with one hand. Measure your plug's thickness first. Thicker than 24 mm, or a plug you want held from both sides such as a USB-C tip or a round extension-cord plug, is the two-sided puller's job, and that tool has its own guide.

The Customizer's four steps are your plug, your size, the attachment and the hook's side. This full guide covers getting the file, measuring your plug and your hand or matching a card, every dial with a picture, printing, assembly, use and care, what to do when a print does not fit, every warning, and how the advanced dials work.

If red text appears beside the part in the preview, read it: it names the measurement to fix, and the part will not fit until it is gone.

In every picture: black = the tool; teal = your plug; red dashed = the edges this dial moved; the numbers match the key beside the picture.

![The one-sided puller, the four Customizer steps on a US vacuum plug, five stages left to right.](../../dials/one-sided/storyboard.svg)

Five stages of the one-sided puller, left to right, the top row first, the plug end at the top; arrows numbered 1 to 4 show the steps, and red dashes mark the edges each step moved. Start, the defaults: the tool as the file opens, with a 25 mm wide plug in teal. Step 1 - Your Plug: plug length, plug width at both ends, plug thickness at both ends, cord thickness, outlet cover plate style; red on the body edge, finger holes, seat, wall notch, wing openings and zip-tie holes. Step 2 - Size: hand size, finger width, hand width; red on the body edge, finger holes, pocket, wall notch, wing openings and zip-tie holes. Step 3 - Attachment: attachment; the wing openings removed, drawn in red from the old outline. Step 4 - Cord Hook: hook side; red on the hook.

- Step 1: type your plug's numbers
- Step 2: pick your hand size
- Step 3: pick how it attaches
- Step 4: pick the hook's side

## Get the file

The one-sided puller is the file `src/Plug_Puller_Parametric.scad`. There are two ways to open it and fill in its form: in your web browser with nothing to install, or in the free OpenSCAD program on your computer. Both show the same form, called the Customizer.

### In your browser

The OpenSCAD Assistive Forge is a version of OpenSCAD that runs in your browser, on a computer or a phone, built for keyboard and screen reader use. Nothing is uploaded: your numbers stay on your device.

1. Open [the one-sided puller in the Assistive Forge](https://openscad-assistive-forge.pages.dev/?manifest=https://raw.githubusercontent.com/BrennenJohnston/openscad-assistive-forge/example-manifest/plug-puller/forge-manifest-one-sided.json). On a first visit Forge asks which interface you want: choose **Assistive Forge**, then **Download & Continue**, and it downloads its engine once.
2. Forge offers to keep a copy of the project in your browser. Choose **Save My Copy**: the tool is then listed on Forge's main page whenever you come back, no link needed.
3. The form shows the four steps' dials first. The rest sit behind one button, **Show all parameters**.

If the link cannot load, Forge says why and offers **Try again**. You can also download the whole tool as one file, [`dist/Plug_Puller_SingleFile.scad`](../../../dist/Plug_Puller_SingleFile.scad), and open it from Forge's main page, under Open or start a project.

### On your computer

OpenSCAD is the free program that turns your numbers into a printable file. You use one panel of it and never touch the code.

1. Download OpenSCAD from <https://openscad.org/downloads.html>: the **Development Snapshot** for your system. This project is tested with the snapshot of 2026-01-03; any recent snapshot works. The regular release works too, only slower.
2. Get the project: on its GitHub page press the green **Code** button, then **Download ZIP**, and unzip it anywhere. Or download only [`dist/Plug_Puller_SingleFile.scad`](../../../dist/Plug_Puller_SingleFile.scad), the whole tool in one file.
3. Open `src/Plug_Puller_Parametric.scad` (or the single file) in OpenSCAD: double-click it, or use **File ▸ Open**. A wall of code appears in an editor pane. Ignore it; you will not touch it.
4. Show the Customizer, the form you type into: in the **View** menu, make sure **Hide Customizer** is unchecked. In older versions it is **Window ▸ Customizer**.

The form's sections read top to bottom in the order you decide things: **Step 1 - Your Plug**, **Step 2 - Size**, **Step 3 - Attachment**, then **Step 4 - Cord Hook**. Everything below Step 4 is optional.

### Working in the browser

Forge and the desktop program show the same form and make the same tool. What differs:

- Forge draws the tool as it will print, with any red warning text beside it. It does not draw the see-through plug, or the green and orange notes of the desktop program's preview.
- A render takes longer in the browser than on the desktop, and longest on a phone. Forge says **Preview ready** under the picture when it is done.
- On a phone the screen is tight. The parameter search finds any dial by its name, and searching also brings back the dials behind **Show all parameters**.
- Forge can be installed as an app that works offline: use your browser's install button at the right end of the address bar.
- To send your numbers to someone, or to keep them, use Forge's **Copy Link**: the link carries the values you changed, and opening it puts them back.

| Problem | What to do |
| ------- | ---------- |
| "The shared project could not be opened" | Forge names the reason. Press **Try again**; if it keeps failing, download the single file and open it from Forge's main page. |
| A dial you want is not on the form | Press **Show all parameters**. The four steps' dials are shown first; the rest sit behind that button. |
| Red text beside the tool in the preview | A measurement cannot work, and the text names it. Fix it before you export: the red text is part of the model. |

## Measure your plug and your hand

Everything here is in mm: a US plug is about 25 mm wide, so a 1 on your paper means you measured in inches. You need a caliper or a ruler with mm marks, the plug in its outlet, and your own hand only if you pick Measure my hand. Print the measuring form at 100 % and fill it in as you go: the sections below are the form's rows, in the same order, and the card names (R1, C1, F1 / F2) are the cards of the printed measuring stencil, described under Match a card instead of measuring.

### Plug length

Customizer name: `measure_plug_length`. Row 2 of the measuring form.

With the plug in the outlet, ruler from the wall plate face to the plug's back face. On a laptop or charger plug, measure from the device's edge.

Typical: 20 to 50 mm. Example: 38 mm.

With the stencil: card R1.

### Plug width at the prong end

Customizer name: `measure_plug_width_prong_end`. Row 3 of the measuring form.

Caliper straight across the plastic body just behind the prongs, the wide way, parallel to the wall. Measure the body, not the metal prongs; if the head flares, take the widest part of that first stretch.

Typical: 20 to 38 mm. Example: 34 mm.

With the stencil: card R1.

### Plug width at the cord end

Customizer name: `measure_plug_width_cord_end`. Row 4 of the measuring form.

The same wide direction, but where the cord leaves the plug body. Skip any soft rubber strain relief and measure the last part of the hard body you would grip.

Typical: 10 to 35 mm. Example: 13 mm.

With the stencil: card R1.

### Plug thickness at the prong end

Customizer name: `measure_plug_thickness_prong_end`. Row 5 of the measuring form.

Caliper across the plug body's thin direction, usually top to bottom on a flat plug, just behind the prongs. A plug 24 mm thick or more needs the two-sided puller, so measure carefully.

Typical: 12 to 30 mm. Example: 16 mm.

With the stencil: card R1.

### Plug thickness at the cord end

Customizer name: `measure_plug_thickness_cord_end`. Row 6 of the measuring form.

The same thin direction, where the cord leaves the plug body, skipping the soft strain relief. On a round extension-cord plug this can be as fat as the prong end.

Typical: 8 to 30 mm. Example: 9 mm.

With the stencil: card R1.

### Cord thickness

Customizer name: `measure_cord_thickness`. Row 7 of the measuring form.

Caliper across the cord just behind the plug, on its thin side: flat cord the narrow way, round cord the diameter. With the stencil, the smallest C1 slot that slips over the cord is this number.

Typical: 3 to 7 mm. Example: 5 mm.

With the stencil: card C1.

### Outlet cover plate style

Customizer name: `measure_wall_plate_style`. Row 8 of the measuring form.

Look at the outlet cover plate: two small oval openings is Standard flat plate; one big rectangle per outlet is Rocker / Decora; a bigger, thicker plate is Oversized / Jumbo; no plate or a flush outlet is No plate / flush.

The choices: Standard flat plate, Rocker / Decora, Oversized / Jumbo, No plate / flush.

### Finger width

Customizer name: `measure_finger_width`. Row 11 of the measuring form.

Caliper across the widest knuckle of your middle finger, the finger that goes into the pull hole. With the stencil, find the smallest F1 or F2 hole your finger passes through comfortably and subtract 5 from its number.

Typical: 16 to 24 mm. Example: 22 mm.

With the stencil: card F1 / F2.

No caliper? Take a ring that fits that finger snugly, measure the ring's inner diameter in mm and add 1.5 mm.

### Hand width

Customizer name: `measure_hand_width`. Row 12 of the measuring form.

Caliper or ruler straight across the four knuckles of your flat hand, fingers together, no thumb. Measure at the widest point.

Typical: 70 to 100 mm. Example: 88 mm.

With the stencil: card R1.

### Strap width

Customizer name: `strap_width`. Row 15 of the measuring form.

Read the width on the strap's packaging. ONE-WRAP comes in 10, 13, 16, 20 and 25 mm.

Typical: 10 to 25 mm. Example: 15 mm.

Sanity check: each plug width is a two-digit number, roughly 12 to 45, and the prong-end width is usually the bigger one; the finger width is roughly 14 to 32. A number like 1.3 is inches: measure again with the mm side.

When you measure for someone else, a relative or a client, measure their hand for the finger and hand rows and their outlet and plug for the plug rows. Doubtful between two values? Round up: a slightly roomy fit works, a tight one does not.

### The measuring form

The form is the sheet [measuring-form.svg](measuring-form.svg); the paper stencil sheets are [stencil-sheet.svg](../stencil-sheet.svg) and [stencil-sheet-2.svg](../stencil-sheet-2.svg). Print the form at 100 % (actual size, never fit to page) and check its 50 mm bar with a ruler before you trust it. Fill in the blanks top to bottom as you measure, then type the numbers into the Customizer in the same order.

| # | Customizer name | What you measure | Default | Yours |
|---|---|---|---|---|
| 1 | `plug_preset` | Plug preset: pick one | Measure my plug | ________ |
| 2 | `measure_plug_length` | With the plug in the outlet, ruler from the wall plate face to the plug's back face. | 25.5 mm | ________ |
| 3 | `measure_plug_width_prong_end` | Caliper straight across the plastic body just behind the prongs, the wide way, parallel to the wall. | 25 mm | ________ |
| 4 | `measure_plug_width_cord_end` | The same wide direction, but where the cord leaves the plug body. | 25 mm | ________ |
| 5 | `measure_plug_thickness_prong_end` | Caliper across the plug body's thin direction, usually top to bottom on a flat plug, just behind the prongs. | 20 mm | ________ |
| 6 | `measure_plug_thickness_cord_end` | The same thin direction, where the cord leaves the plug body, skipping the soft strain relief. | 20 mm | ________ |
| 7 | `measure_cord_thickness` | Caliper across the cord just behind the plug, on its thin side: flat cord the narrow way, round cord the diameter. | 4 mm | ________ |
| 8 | `measure_wall_plate_style` | Look at the outlet cover plate and pick the closest match. | Standard flat plate | ________ |
| 9 | `show_plug_preview` | Show the see-through plug: leave on | on | ________ |
| 10 | `size` | Hand size: pick one | Medium | ________ |
| 11 | `measure_finger_width` | Caliper across the widest knuckle of your middle finger, the finger that goes into the pull hole. | 20 mm | ________ |
| 12 | `measure_hand_width` | Caliper or ruler straight across the four knuckles of your flat hand, fingers together, no thumb. | 85 mm | ________ |
| 13 | `attachment` | Attachment: pick one | Zip ties + Velcro | ________ |
| 14 | `velcro_style` | Strap opening style: pick one | Wing | ________ |
| 15 | `strap_width` | Read the width on the strap's packaging. | 15 mm | ________ |
| 16 | `hook_hand` | Hook side: pick one | Right | ________ |

**What the sheet shows.** The left column is the numbered list above, one row per dial in the Customizer's Step order, each with the dial's name, its plain title and either a blank after the default or a tick box per choice with the default marked. The right half is a schematic plug in teal drawn from the one-sided puller's defaults at 1.5 to 1, a top view with the prong end at the left against a wall plate line, a side view standing with its prong end up, the cord's end as a small circle, a bar of four knuckles at 1:1 and a strap bar at 1:1. A straight black arrow runs from each measured row's blank to a red dimension line on the schematic, the row's number in a red circle at the line:

- Arrow 2 points to the plug's length on the top view, from the wall plate to the plug's back end.
- Arrow 3 points to the plug's width at the prong end, the left edge of the top view.
- Arrow 4 points to the plug's width at the cord end, the right edge of the top view where the cord leaves.
- Arrow 5 points to the plug's thickness at the prong end, the top of the side view.
- Arrow 6 points to the plug's thickness at the cord end, the bottom of the side view.
- Arrow 7 points to the cord's thickness on the small circle, the cord seen end on.
- Arrow 11 points to one knuckle of the knuckle bar, drawn 20 mm wide at 1:1.
- Arrow 12 points to the whole knuckle bar, four knuckles 85 mm across at 1:1.
- Arrow 15 points to the strap bar's width, a 40 by 15 mm bar at 1:1.

- Row 1, plug preset: 5 boxes, Measure my plug marked as the default; the choices are Measure my plug, Flat 2-prong lamp plug - NEMA 1-15, Standard 3-prong plug - NEMA 5-15, Heavy-duty extension cord - NEMA 5-15, Wide 2-prong appliance plug - NEMA 1-15.
- Row 8, outlet cover plate style: 4 boxes, Standard flat plate marked as the default; the choices are Standard flat plate, Rocker / Decora, Oversized / Jumbo, No plate / flush.
- Row 9, show the see-through plug: one box marked, leave on.
- Row 10, hand size: 5 boxes, Medium marked as the default; the choices are Small, Medium, Large, Measure my hand, Custom.
- Row 13, attachment: 4 boxes, Zip ties + Velcro marked as the default; the choices are Zip ties, Velcro strap, Zip ties + Velcro, None.
- Row 14, strap opening style: 2 boxes, Wing marked as the default; the choices are Wing, Classic slot.
- Row 16, hook side: 2 boxes, Right marked as the default; the choices are Right, Left.

Type them into the Customizer in this order.

### Match a card instead of measuring

The measuring stencil is a set of thin printed cards. Each has a two-letter name raised on its face, so you can find it by touch. Hold your plug in the plug cards: if it fills one card's openings, snug with no big gaps, that card names the preset to pick in Step 1, and you type no numbers at all.

| Card | What it is | What it answers |
| ---- | ---------- | --------------- |
| P1 | The flat 2-prong lamp plug (NEMA 1-15) | the preset `Flat 2-prong lamp plug - NEMA 1-15` |
| P2 | The standard 3-prong plug (NEMA 5-15) | the preset `Standard 3-prong plug - NEMA 5-15` |
| P3 | The heavy-duty extension cord plug (NEMA 5-15) | the two-sided puller's preset `Heavy-duty extension cord - NEMA 5-15` |
| P4 | The wide 2-prong appliance plug (NEMA 1-15) | the one-sided puller's preset `Wide 2-prong appliance plug - NEMA 1-15` |
| R1 | A ruler: raised mm ticks, numbers every 10 mm, and a notch every 10 mm you can count by touch | the plug's length, widths and thicknesses |
| C1 | A cord gauge: open slots 3 to 9 mm wide along one edge, slid onto the cord from the side | the cord thickness: the smallest slot that slips over the cord |
| F1, F2 | Finger holes 15 to 25 mm across (F1) and 26 to 32 mm (F2) | your finger width: the smallest hole your middle finger passes through comfortably, minus 5 |

Each P card has three openings: W for the plug's width, T for its thickness, and an open slot that slides onto the cord. If no card fits, your plug is between presets: measure it instead. The measured tool fits better than any preset.

**Printing the cards.** Print [`stl/Measuring-Stencil/Visual/Measuring-Stencil_Visual_All-Cards.stl`](../../../stl/Measuring-Stencil/Visual/Measuring-Stencil_Visual_All-Cards.stl): 1.2 mm thick cards, no supports, any rigid filament, packed onto sheets for a 200 by 200 mm bed. The tactile version, [`stl/Measuring-Stencil/Tactile/`](../../../stl/Measuring-Stencil/Tactile), prints every label as a raised character at ADA size and adds a Grade 2 braille title flap to every card.
Or print one card at a time from [`stl/Measuring-Stencil/`](../../../stl/Measuring-Stencil). For a smaller bed, open [`Measuring_Stencil.scad`](../../../Measuring_Stencil.scad) in OpenSCAD, set `bed_width` and `bed_depth` to your bed, and export `part_index` 1, then 2, and so on, one sheet at a time. `part_index` 0 previews every sheet at once; do not print that one.

**Folding the tactile flaps.** The tactile version is also `label_mode` set to Tactile in the file. Each flap prints leaning back, held by thin fins. Snap the fins off, then fold the flap away from the card until it lies flat, so the braille lands face up beyond the card's edge. Fold once, gently; a PETG or PP hinge folds more reliably than PLA.

**No 3D printer yet?** The last pages of the printed quick start and full guide are paper versions of the cards at true size: the plug outlines, a 100 mm ruler and the finger circles. Print them at 100 % (actual size, never fit to page) and check the 50 by 50 mm square with a ruler before you trust them. On their own they are [`stencil-sheet.svg`](../stencil-sheet.svg) and [`stencil-sheet-2.svg`](../stencil-sheet-2.svg).

### Try it on paper first

Every preset at every size has a printable sheet with the tool's exact outline at true size, its dimensions in mm, a 50 by 50 mm square to check the print scale, and the Customizer settings that make it. Print one at 100 % (actual size, never fit to page) and measure the square with a ruler: it must be exactly 50 by 50 mm, or the print was scaled. Cut out the outline along the solid line and poke through the two finger circles. Hold it against your plug on the wall: the plug should fit inside the dashed pocket outline, and the notch at the top edge should straddle the outlet cover. Try the finger holes; if they feel wrong, try the next size's sheet.

| Plug preset | Small | Medium | Large |
| ----------- | ----- | ------ | ----- |
| Flat 2-prong lamp plug (NEMA 1-15) | [sheet](../outline-sheets/outline_flat-2-prong_small.svg) | [sheet](../outline-sheets/outline_flat-2-prong_medium.svg) | [sheet](../outline-sheets/outline_flat-2-prong_large.svg) |
| Standard 3-prong plug (NEMA 5-15) | [sheet](../outline-sheets/outline_standard-3-prong_small.svg) | [sheet](../outline-sheets/outline_standard-3-prong_medium.svg) | [sheet](../outline-sheets/outline_standard-3-prong_large.svg) |
| Wide 2-prong appliance plug (NEMA 1-15) | [sheet](../outline-sheets/outline_wide-2-prong-appliance_small.svg) | [sheet](../outline-sheets/outline_wide-2-prong-appliance_medium.svg) | [sheet](../outline-sheets/outline_wide-2-prong-appliance_large.svg) |

Every sheet, for both tools, is also in one printable PDF with an index: [`docs/Plug_Puller_Outline_Sheets.pdf`](../../Plug_Puller_Outline_Sheets.pdf). The sheets cover the presets only; a plug or a hand between sizes is better served by measuring.

## Step 1 - Your Plug

Pick a plug preset, or leave it on Measure my plug and type your plug's numbers.

### Plug preset

Customizer name: `plug_preset`

Fills in all six plug numbers from a measured reference plug, so the pocket, the wall notch, the cord hook and the zip-tie and wing positions all take that plug's shape at once.

![Plug preset: before and after, Measure my plug to Standard 3-prong plug - NEMA 5-15; red marks 7 parts, named below.](../../dials/one-sided/plug_preset.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults, a 25 mm wide plug in teal. Right: plug preset set to Standard 3-prong plug - NEMA 5-15. Marked in red: 1, the zip-tie holes, the finger holes, the wing openings, the wall notch, the seat, the pocket and the body edge.

- Default: Measure my plug
- Choices: Measure my plug, Flat 2-prong lamp plug - NEMA 1-15, Standard 3-prong plug - NEMA 5-15, Heavy-duty extension cord - NEMA 5-15, Wide 2-prong appliance plug - NEMA 1-15
- Moves: body edge, finger holes, pocket, seat, wall notch, wing openings, zip-tie holes

### Plug length

Customizer name: `measure_plug_length`

Runs the pocket farther toward the finger holes and stretches the whole body to keep the finger holes and zip-tie rows clear of it.

![Plug length: before and after, 25.5 to 40 mm; red marks the body edge, the seat, the wall notch, the wing openings and the zip-tie holes.](../../dials/one-sided/measure_plug_length.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults, a 25 mm wide plug in teal. Right: plug length at 40 mm. The red line marks the pocket's length and reads 40 mm, the number you type. Marked in red: 1, the zip-tie holes: the four small holes beside the pocket. 2, the zip-tie holes and the wing openings. 3, the zip-tie holes, the wing openings, the wall notch, the seat and the body edge.

- Default: 25.5 mm
- Range: 12 to 85 mm, in steps of 0.5 mm
- Moves: body edge, seat, wall notch, wing openings, zip-tie holes

### Plug width at the prong end

Customizer name: `measure_plug_width_prong_end`

Widens or narrows the pocket, its seat and the wall notch at the plug end, and moves the zip-tie holes and wing openings with them.

![Plug width at the prong end: before and after, 25 to 32 mm; red marks 5 parts, named below.](../../dials/one-sided/measure_plug_width_prong_end.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults, a 25 mm wide plug in teal. Right: plug width at the prong end at 32 mm. The red line marks the plug's width at the prong end and reads 32 mm, the number you type. Marked in red: 1, the zip-tie holes: the four small holes beside the pocket. 2, the wing openings: the two openings beside the pocket. 3, the wall notch, the seat and the body edge: the notch in the top edge; the round recess at the plug end; the outer outline.

- Default: 25 mm
- Range: 8 to 38 mm, in steps of 0.5 mm
- Moves: body edge, seat, wall notch, wing openings, zip-tie holes

### Plug width at the cord end

Customizer name: `measure_plug_width_cord_end`

Tilts the pocket's side walls to match the plug's taper, and the zip-tie holes and wing openings lean in with them.

![Plug width at the cord end: before and after, 25 to 15 mm; red marks the pocket, the wing openings and the zip-tie holes.](../../dials/one-sided/measure_plug_width_cord_end.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults, a 25 mm wide plug in teal. Right: plug width at the cord end at 15 mm. The red line marks the plug's width at the cord end and reads 15 mm, the number you type. Marked in red: 1, the zip-tie holes, the wing openings and the pocket: the four small holes beside the pocket; the two openings beside the pocket; the plug recess on the centerline.

- Default: 25 mm
- Range: 8 to 38 mm, in steps of 0.5 mm
- Moves: pocket, wing openings, zip-tie holes

### Plug thickness at the prong end

Customizer name: `measure_plug_thickness_prong_end`

Deepens or shallows the two pocket floors, the round seat and the plug recess, to suit the fatter of the two thickness numbers.

![Plug thickness at the prong end: before and after, 20 to 23.5 mm; red marks the pocket and the seat.](../../dials/one-sided/measure_plug_thickness_prong_end.svg)

Two vertical slices of the one-sided puller at x = 0 mm, before left and after right, the top face up. Left: the defaults, the plug in teal in the cut. Right: plug thickness at the prong end at 23.5 mm. The red line marks the plug's thickness at the prong end and reads 23.5 mm, the number you type. Marked in red: 1, the seat and the pocket: the round recess at the plug end; the plug recess on the centerline.

- Default: 20 mm
- Range: 4 to 40 mm, in steps of 0.5 mm
- Moves: pocket, seat

Note: The fatter of the two thickness numbers sets the floors, so lowering one alone changes nothing; 24 mm or more sends you to the two-sided puller.

### Plug thickness at the cord end

Customizer name: `measure_plug_thickness_cord_end`

Deepens or shallows the two pocket floors, the round seat and the plug recess, when this end is the fatter end of the plug.

![Plug thickness at the cord end: before and after, 20 to 23.5 mm; red marks the pocket and the seat.](../../dials/one-sided/measure_plug_thickness_cord_end.svg)

Two vertical slices of the one-sided puller at x = 0 mm, before left and after right, the top face up. Left: the defaults, the plug in teal in the cut. Right: plug thickness at the cord end at 23.5 mm. The red line marks the plug's thickness at the cord end and reads 23.5 mm, the number you type. Marked in red: 1, the seat and the pocket: the round recess at the plug end; the plug recess on the centerline.

- Default: 20 mm
- Range: 4 to 40 mm, in steps of 0.5 mm
- Moves: pocket, seat

Note: The fatter of the two thickness numbers sets the floors, so lowering one alone changes nothing; 24 mm or more sends you to the two-sided puller.

### Cord thickness

Customizer name: `measure_cord_thickness`

Widens the cord hook's slot and crossbar to fit the cord, and moves the finger holes and the whole body up to make room.

![Cord thickness: before and after, 4 to 8 mm; red marks 6 parts, named below.](../../dials/one-sided/measure_cord_thickness.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults, a 25 mm wide plug in teal. Right: cord thickness at 8 mm. The red line marks the cord hook slot and reads 8 mm, the number you type; the slot is drawn 8.8 mm wide, so the cord slips in. Marked in red: 1, the zip-tie holes, the finger holes, the wing openings, the wall notch, the pocket and the body edge.

- Default: 4 mm
- Range: 1.5 to 9 mm, in steps of 0.5 mm
- Moves: body edge, finger holes, pocket, wall notch, wing openings, zip-tie holes

### Outlet cover plate style

Customizer name: `measure_wall_plate_style`

Cuts the wall notch at the plug end deeper or shallower to suit the cover plate, and the zip-tie rows shift down with it.

![Outlet cover plate style: before and after, Standard flat plate to Oversized / Jumbo; red marks 5 parts, named below.](../../dials/one-sided/measure_wall_plate_style.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults, a 25 mm wide plug in teal. Right: outlet cover plate style set to Oversized / Jumbo. Marked in red: 1, the wall notch and the body edge: the notch in the top edge; the outer outline. 2, the zip-tie holes: the four small holes beside the pocket. 3, the pocket: the plug recess on the centerline. 4, the wing openings: the two openings beside the pocket.

- Default: Standard flat plate
- Choices: Standard flat plate, Rocker / Decora, Oversized / Jumbo, No plate / flush
- Moves: body edge, pocket, wall notch, wing openings, zip-tie holes

### Show the see-through plug

Customizer name: `show_plug_preview`

Shows or hides the see-through plug in the preview and changes nothing in the printed tool.

No picture. Changes no shape: the see-through plug is a preview aid and is never exported.

- Default: On
- Choices: On or off (a check box)

## Step 2 - Size

Pick your hand size, or pick Measure my hand and type your hand's numbers.

### Hand size

Customizer name: `size`

Scales the whole body, both finger holes, the wing openings and the zip-tie grid to the chosen hand size.

![Hand size: before and after, Medium to Large; red marks the body edge, the finger holes, the pocket, the wing openings and the zip-tie holes.](../../dials/one-sided/size.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults, a 25 mm wide plug in teal. Right: hand size set to Large. Marked in red: 1, the zip-tie holes: the four small holes beside the pocket. 2, the pocket: the plug recess on the centerline. 3, the wing openings: the two openings beside the pocket. 4, the finger holes: the two large holes in the lower half. 5, the body edge: the outer outline.

- Default: Medium
- Choices: Small, Medium, Large, Measure my hand, Custom
- Moves: body edge, finger holes, pocket, wing openings, zip-tie holes

### Finger width

Customizer name: `measure_finger_width`

Widens both finger holes, spaces them farther apart and pushes them and the body up to keep the walls printable.

![Finger width: before and after, 20 to 26 mm; red marks 6 parts, named below.](../../dials/one-sided/measure_finger_width.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Measure my hand, a 25 mm wide plug in teal. Right: finger width at 26 mm. The red line marks a finger hole and reads 26 mm, the number you type; the hole is drawn 27.9 mm across, wider than the finger. Marked in red: 1, the zip-tie holes and the pocket. 2, the wing openings. 3, the finger holes. 4, the zip-tie holes, the wall notch and the body edge.

- Default: 20 mm
- Range: 14 to 32 mm, in steps of 0.5 mm
- Moves: body edge, finger holes, pocket, wall notch, wing openings, zip-tie holes

Note: Only acts when size is Measure my hand.

### Hand width

Customizer name: `measure_hand_width`

Widens the whole body outline and thickens the slab in step with the hand.

![Hand width: before and after, 85 to 100 mm; red marks the body edge and the wing openings.](../../dials/one-sided/measure_hand_width.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Measure my hand, a 25 mm wide plug in teal. Right: hand width at 100 mm. The red line marks the body at its widest and reads 100 mm, the number you type; the body is drawn 80.3 mm wide, narrower than the hand, as its width is worked out from the hand width. Marked in red: 1, the wing openings and the body edge: the two openings beside the pocket; the outer outline.

- Default: 85 mm
- Range: 60 to 110 mm, in steps of 1 mm
- Moves: body edge, wing openings

Note: Only acts when size is Measure my hand.

## Step 3 - Attachment

Pick how the tool attaches.

### Attachment

Customizer name: `attachment`

Adds or removes the zip-tie holes and the wing or slot openings for the strap.

![Attachment: before and after, Zip ties + Velcro to Zip ties; red marks the wing openings.](../../dials/one-sided/attachment.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults, a 25 mm wide plug in teal. Right: attachment set to Zip ties. Marked in red: 1, the wing openings: the two openings beside the pocket, removed. The body edge, the pocket, the seat and the wall notch stay where they were.

- Default: Zip ties + Velcro
- Choices: Zip ties, Velcro strap, Zip ties + Velcro, None
- Moves: wing openings

### Strap opening style

Customizer name: `velcro_style`

Swaps the curved wing openings for a pair of plain rectangular slots that lean along the body's sides.

![Strap opening style: before and after, Wing to Classic slot; red marks the classic slots and the wing openings.](../../dials/one-sided/velcro_style.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults, a 25 mm wide plug in teal. Right: strap opening style set to Classic slot. Marked in red: 1, the wing openings and the classic slots: the two openings beside the pocket; the two slots beside the pocket.

- Default: Wing
- Choices: Wing, Classic slot
- Moves: classic slots, wing openings
- Red warnings: WING OPENING SMALLER THAN STRAP WIDTH

### Strap width

Customizer name: `strap_width`

Sets the strap width the wing opening is checked against and changes no shape.

No picture. Changes no shape: it only sets the width the W-14 check compares the wing opening against.

- Default: 15 mm
- Range: 10 to 25 mm, in steps of 1 mm
- Red warnings: WING OPENING SMALLER THAN STRAP WIDTH; WING WEB COLLAPSED - NO ROOM FOR STRAP

## Step 4 - Cord Hook

Pick the hook's side.

### Hook side

Customizer name: `hook_hand`

Mirrors the cord hook at the cord end so its catch faces the other side, and nothing else moves.

![Hook side: before and after, Right to Left; red marks the hook.](../../dials/one-sided/hook_hand.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults, a 25 mm wide plug in teal. Right: hook side set to Left. Marked in red: 1, the hook: the cord hook slot in the bottom edge. The body edge, the pocket, the seat and the wall notch stay where they were.

- Default: Right
- Choices: Right, Left
- Moves: hook

## The optional dials

Everything below Step 4 in the Customizer is optional. These dials apply in every hand size, except the sections marked (Custom size only), which do nothing until Step 2's hand size is Custom. The sections follow in the Customizer's order; how they work together is explained after the troubleshooting sections.

- **Advanced - Zip Tie Placement**, 6 dials: Zip-tie hole placement, Number of zip-tie rows, Zip-tie pair 1 position, Zip-tie pair 2 position, Zip-tie pair 3 position, Zip-tie hole distance from the pocket wall.
- **Advanced - Velcro Placement**, 2 dials: Strap slot placement, Strap slot position.
- **Advanced - Render Quality**, 1 dial: Render quality.
- **Custom Mode**, 2 dials: Reset Custom to the Medium reference, Auto-fit.
- **Body Shape (Custom size only)**, 8 dials: Body length, Body width at the widest point, Cord-end corner width, Body width at the plug end, Body width at the middle, Side corner position, Body thickness, Round the cord half only.
- **Plug Pocket (Custom size only)**, 7 dials: Pocket seat diameter, Pocket width, Pocket depth, Pocket reference drop, Pocket seat floor thickness, Plug recess floor thickness, Pocket side taper.
- **Finger Holes (Custom size only)**, 4 dials: Finger holes on or off, Finger hole diameter, Finger hole spacing, Finger hole position.
- **T Hook (Custom size only)**, 10 dials: Cord hook on or off, Hook slot width, Hook length, Hook crossbar width, Hook crossbar height, Hook slot inset, Hook stem side offset, Hook stem offset, Hook catch reach, Hook tip drop.
- **Plug Wall Notch (Custom size only)**, 4 dials: Wall notch on or off, Wall notch width, Wall notch depth, Wall notch corner rounding.
- **Zip Tie Holes (Custom size only)**, 5 dials: Zip-tie hole diameter, Zip-tie row spacing, Zip-tie column spacing, Zip-tie distance from the notch, Zip-tie countersink.
- **Velcro / Wing Strap Holes (Custom size only)**, 5 dials: Strap slot length, Strap slot width, Strap slot distance from the centerline, Strap slot position along the body, Strap slot lean.
- **Edge Rounding (Custom size only)**, 9 dials: Body side rounding, Top edge rounding, Bottom edge rounding, Strap slot corner rounding, Strap opening edge rounding, Finger hole rim rounding, Hook crossbar corner rounding, Hook slot corner rounding, Hook edge rounding.

## Advanced - Zip Tie Placement

### Zip-tie hole placement

Customizer name: `zip_placement`

Switches the zip-tie pairs from the automatic rows to the three position dials, which slide each pair along the plug's side.

![Zip-tie hole placement: before and after, Auto to Manual; red marks the seat, the wall notch, the wing openings and the zip-tie holes.](../../dials/one-sided/zip_placement.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults, a 25 mm wide plug in teal. Right: zip-tie hole placement set to Manual. Marked in red: 1, the zip-tie holes, the wall notch and the seat: the four small holes beside the pocket; the notch in the top edge; the round recess at the plug end. 2, the wing openings: the two openings beside the pocket. 3, the zip-tie holes: the four small holes beside the pocket.

- Default: Auto
- Choices: Auto, Manual
- Moves: seat, wall notch, wing openings, zip-tie holes

### Number of zip-tie rows

Customizer name: `zip_row_count`

Adds or removes a pair of zip-tie holes, and the rows squeeze together when the body has no room for another.

![Number of zip-tie rows: before and after, 2 to 3; red marks the wing openings and the zip-tie holes.](../../dials/one-sided/zip_row_count.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults, a 25 mm wide plug in teal. Right: number of zip-tie rows at 3. Marked in red: 1, the wing openings: the two openings beside the pocket. 2, the zip-tie holes: the four small holes beside the pocket.

- Default: 2
- Range: 1 to 3, in steps of 1
- Moves: wing openings, zip-tie holes

### Zip-tie pair 1 position

Customizer name: `zip_pos_1`

Slides the first pair of zip-tie holes along the plug's side, measured from the plug end.

![Zip-tie pair 1 position: before and after, 6 to 10 mm; red marks the seat, the wall notch and the zip-tie holes.](../../dials/one-sided/zip_pos_1.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with zip-tie hole placement set to Manual, a 25 mm wide plug in teal. Right: zip-tie pair 1 position at 10 mm. Marked in red: 1, the zip-tie holes, the wall notch and the seat: the four small holes beside the pocket; the notch in the top edge; the round recess at the plug end.

- Default: 6 mm
- Range: 0 to 55 mm, in steps of 0.5 mm
- Moves: seat, wall notch, zip-tie holes
- Red warnings: ZIP TIE HOLES HIT FINGER HOLES; ZIP TIE ROWS OVERLAP EACH OTHER; ZIP TIE HOLES HIT VELCRO SLOTS

Note: Only acts when zip_placement is Manual.

### Zip-tie pair 2 position

Customizer name: `zip_pos_2`

Slides the second pair of zip-tie holes along the plug's side, measured from the plug end.

![Zip-tie pair 2 position: before and after, 18 to 26 mm; red marks the wing openings and the zip-tie holes.](../../dials/one-sided/zip_pos_2.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with zip-tie hole placement set to Manual, a 25 mm wide plug in teal. Right: zip-tie pair 2 position at 26 mm. Marked in red: 1, the zip-tie holes: the four small holes beside the pocket. 2, the wing openings: the two openings beside the pocket.

- Default: 18 mm
- Range: 0 to 55 mm, in steps of 0.5 mm
- Moves: wing openings, zip-tie holes
- Red warnings: ZIP TIE HOLES HIT FINGER HOLES; ZIP TIE ROWS OVERLAP EACH OTHER; ZIP TIE HOLES HIT VELCRO SLOTS

Note: Only acts when zip_placement is Manual.

### Zip-tie pair 3 position

Customizer name: `zip_pos_3`

Slides the third pair of zip-tie holes along the plug's side, measured from the plug end.

![Zip-tie pair 3 position: before and after, 30 to 26 mm; red marks the wing openings and the zip-tie holes.](../../dials/one-sided/zip_pos_3.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with zip-tie hole placement set to Manual and number of zip-tie rows set to 3, a 25 mm wide plug in teal. Right: zip-tie pair 3 position at 26 mm. Marked in red: 1, the wing openings: the two openings beside the pocket. 2, the zip-tie holes and the wing openings: the four small holes beside the pocket; the two openings beside the pocket.

- Default: 30 mm
- Range: 0 to 55 mm, in steps of 0.5 mm
- Moves: wing openings, zip-tie holes
- Red warnings: ZIP TIE HOLES HIT FINGER HOLES; ZIP TIE ROWS OVERLAP EACH OTHER; ZIP TIE HOLES HIT VELCRO SLOTS

Note: Only acts when zip_placement is Manual and zip_row_count is 3.

### Zip-tie hole distance from the pocket wall

Customizer name: `zip_edge_offset`

Moves every zip-tie hole farther from or closer to the pocket wall, and the wing openings reshape around them.

![Zip-tie hole distance from the pocket wall: before and after, 4 to 8 mm; red marks the wing openings and the zip-tie holes.](../../dials/one-sided/zip_edge_offset.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults, a 25 mm wide plug in teal. Right: zip-tie hole distance from the pocket wall at 8 mm. Marked in red: 1, the zip-tie holes: the four small holes beside the pocket. 2, the wing openings: the two openings beside the pocket.

- Default: 4 mm
- Range: 2.5 to 12 mm, in steps of 0.25 mm
- Moves: wing openings, zip-tie holes

## Advanced - Velcro Placement

### Strap slot placement

Customizer name: `velcro_placement`

Switches the strap openings to a pair of plain slots that the position dial slides along the plug's side, whatever the opening style.

![Strap slot placement: before and after, Auto to Manual; red marks the wing openings.](../../dials/one-sided/velcro_placement.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults, a 25 mm wide plug in teal. Right: strap slot placement set to Manual. Marked in red: 1, the wing openings: the two openings beside the pocket. The body edge, the pocket, the seat and the wall notch stay where they were.

- Default: Auto
- Choices: Auto, Manual
- Moves: wing openings

### Strap slot position

Customizer name: `velcro_pos`

Slides the pair of strap slots along the plug's side, measured from the plug end.

![Strap slot position: before and after, 12 to 25 mm; red marks the classic slots.](../../dials/one-sided/velcro_pos.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with strap opening style set to Classic slot and strap slot placement set to Manual, a 25 mm wide plug in teal. Right: strap slot position at 25 mm. Marked in red: 1, the classic slots: the two slots beside the pocket.

- Default: 12 mm
- Range: 0 to 55 mm, in steps of 0.5 mm
- Moves: classic slots
- Red warnings: ZIP TIE HOLES HIT VELCRO SLOTS

Note: Only acts when velcro_placement is Manual.

## Advanced - Render Quality

### Render quality

Customizer name: `quality`

Sets how many flat segments draw each curve and changes no dimension.

No picture. Changes no shape: it only sets the number of segments in every circle and arc.

- Default: 64 segments
- Range: 24 to 128 segments, in steps of 8 segments

## Custom Mode

### Reset Custom to the Medium reference

Customizer name: `reset_custom_to_medium`

Swaps every Custom slider for the Medium reference values for one render, so the whole tool snaps back to the Medium shape.

![Reset Custom to the Medium reference: before and after, false to true; red marks 4 parts, named below.](../../dials/one-sided/reset_custom_to_medium.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom, a 25 mm wide plug in teal. Right: reset Custom to the Medium reference set to true. Marked in red: 1, the zip-tie holes: the four small holes beside the pocket. 2, the wing openings: the two openings beside the pocket. 3, the finger holes: the two large holes in the lower half. 4, the zip-tie holes and the body edge.

- Default: Off
- Choices: On or off (a check box)
- Moves: body edge, finger holes, wing openings, zip-tie holes

Note: Only acts when size is Custom.

### Auto-fit

Customizer name: `custom_enable_auto_fit`

Lets the tool clamp any Custom slider that would push a feature past the body or into a neighbor, and changes nothing while every slider is inside its safe range.

No picture. Changes no shape at the Custom defaults: it only clamps sliders that leave their safe range, and every clamp is reported in the console.

- Default: On
- Choices: On or off (a check box)
- Red warnings: ZIP TIE HOLES HIT FINGER HOLES; FINGER HOLES OUTSIDE BODY; POCKET SEAT WIDER THAN TOP EDGE; POCKET WIDER THAN BODY; WALL NOTCH WIDER THAN TOP EDGE

## Body Shape (Custom size only)

### Body length

Customizer name: `custom_puller_length`

Stretches the whole body from the cord end to the plug end.

![Body length: before and after, 63.5 to 73.5 mm; red marks 6 parts, named below.](../../dials/one-sided/custom_puller_length.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom, a 25 mm wide plug in teal. Right: body length at 73.5 mm. Marked in red: 1, the zip-tie holes, the wing openings, the wall notch, the seat, the pocket and the body edge.

- Default: 63.5 mm
- Range: 50 to 120 mm, in steps of 0.5 mm
- Moves: body edge, pocket, seat, wall notch, wing openings, zip-tie holes

Note: Only acts when size is Custom.

### Body width at the widest point

Customizer name: `custom_puller_bottom_width`

Widens the body at its widest point, just above the cord end, before the side rounding is applied.

![Body width at the widest point: before and after, 77.6 to 87.6 mm; red marks the body edge.](../../dials/one-sided/custom_puller_bottom_width.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom, a 25 mm wide plug in teal. Right: body width at the widest point at 87.6 mm. Marked in red: 1, the body edge: the outer outline. Everything else follows the outline.

- Default: 77.6 mm
- Range: 50 to 120 mm, in steps of 0.05 mm
- Moves: body edge

Note: Only acts when size is Custom.

### Cord-end corner width

Customizer name: `custom_puller_bottom_corners`

Widens the flat at the cord end where the two lower corners of the body outline sit.

![Cord-end corner width: before and after, 3 to 13 mm; red marks the body edge.](../../dials/one-sided/custom_puller_bottom_corners.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom, a 25 mm wide plug in teal. Right: cord-end corner width at 13 mm. Marked in red: 1, the body edge: the outer outline. Everything else follows the outline.

- Default: 3 mm
- Range: 3 to 80 mm, in steps of 0.25 mm
- Moves: body edge

Note: Only acts when size is Custom.

### Body width at the plug end

Customizer name: `custom_puller_top_width`

Widens the plug end of the body, where the wall notch and the pocket seat sit.

![Body width at the plug end: before and after, 31.75 to 41.75 mm; red marks the body edge and the wing openings.](../../dials/one-sided/custom_puller_top_width.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom, a 25 mm wide plug in teal. Right: body width at the plug end at 41.75 mm. Marked in red: 1, the body edge: the outer outline. 2, the wing openings: the two openings beside the pocket. Everything else follows the outline.

- Default: 31.75 mm
- Range: 25 to 80 mm, in steps of 0.25 mm
- Moves: body edge, wing openings

Note: Only acts when size is Custom.

### Body width at the middle

Customizer name: `custom_puller_middle_width`

Widens the body at the middle control point, bulging or straightening the side edges between the widest point and the plug end.

![Body width at the middle: before and after, 57.35 to 67.35 mm; red marks the body edge and the wing openings.](../../dials/one-sided/custom_puller_middle_width.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom, a 25 mm wide plug in teal. Right: body width at the middle at 67.35 mm. Marked in red: 1, the body edge: the outer outline. 2, the wing openings: the two openings beside the pocket. Everything else follows the outline.

- Default: 57.35 mm
- Range: 25 to 120 mm, in steps of 0.05 mm
- Moves: body edge, wing openings

Note: Only acts when size is Custom.

### Side corner position

Customizer name: `custom_puller_side_corner`

Moves the two widest corners of the body outline up toward the plug end or down toward the cord end.

![Side corner position: before and after, 4.65 to 14.65 mm; red marks the body edge and the wing openings.](../../dials/one-sided/custom_puller_side_corner.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom, a 25 mm wide plug in teal. Right: side corner position at 14.65 mm. Marked in red: 1, the wing openings: the two openings beside the pocket. 2, the body edge: the outer outline. Everything else follows the outline.

- Default: 4.65 mm
- Range: 3 to 35 mm, in steps of 0.05 mm
- Moves: body edge, wing openings

Note: Only acts when size is Custom.

### Body thickness

Customizer name: `custom_body_thickness`

Thickens the whole slab, so every hole and the pocket get deeper walls.

![Body thickness: before and after, 6.35 to 9 mm; red marks the body edge.](../../dials/one-sided/custom_body_thickness.svg)

Two vertical slices of the one-sided puller at y = 35 mm, before left and after right, the top face up. Left: the defaults with hand size set to Custom, the plug in teal in the cut. Right: body thickness at 9 mm. Marked in red: 1, the body edge: the outer outline. Everything else follows the outline.

- Default: 6.35 mm
- Range: 4 to 15 mm, in steps of 0.05 mm
- Moves: body edge

Note: Only acts when size is Custom.

### Round the cord half only

Customizer name: `custom_body_round_bottom_only`

Rounds the whole outline instead of only the cord half, so the plug end loses its crisp corners.

![Round the cord half only: before and after, true to false; red marks the body edge, the hook, the seat and the wall notch.](../../dials/one-sided/custom_body_round_bottom_only.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom, a 25 mm wide plug in teal. Right: round the cord half only set to false. Marked in red: 1, the wall notch and the seat: the notch in the top edge; the round recess at the plug end.

- Default: On
- Choices: On or off (a check box)
- Moves: body edge, hook, seat, wall notch

Note: Only acts when size is Custom.

## Plug Pocket (Custom size only)

### Pocket seat diameter

Customizer name: `custom_pocket_seat_diameter`

Widens the round seat cut into the plug end of the pocket.

![Pocket seat diameter: before and after, 31.75 to 28 mm; red marks the seat.](../../dials/one-sided/custom_pocket_seat_diameter.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom, a 25 mm wide plug in teal. Right: pocket seat diameter at 28 mm. Marked in red: 1, the seat: the round recess at the plug end. The body edge, the pocket, the wall notch and the wing openings stay where they were.

- Default: 31.75 mm
- Range: 10 to 45 mm, in steps of 0.05 mm
- Moves: seat

Note: Only acts when size is Custom.

### Pocket width

Customizer name: `custom_pocket_width`

Widens the plug recess, and the zip-tie holes and wing openings move outward with its wall.

![Pocket width: before and after, 28.85 to 34 mm; red marks the pocket, the seat, the wing openings and the zip-tie holes.](../../dials/one-sided/custom_pocket_width.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom, a 25 mm wide plug in teal. Right: pocket width at 34 mm. Marked in red: 1, the seat and the pocket: the round recess at the plug end; the plug recess on the centerline. 2, the zip-tie holes: the four small holes beside the pocket. 3, the wing openings: the two openings beside the pocket.

- Default: 28.85 mm
- Range: 10 to 45 mm, in steps of 0.05 mm
- Moves: pocket, seat, wing openings, zip-tie holes

Note: Only acts when size is Custom.

### Pocket depth

Customizer name: `custom_pocket_depth`

Runs the plug recess farther from the plug end toward the finger holes.

![Pocket depth: before and after, 24.5 to 34 mm; red marks the pocket and the wing openings.](../../dials/one-sided/custom_pocket_depth.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom, a 25 mm wide plug in teal. Right: pocket depth at 34 mm. Marked in red: 1, the pocket: the plug recess on the centerline. 2, the wing openings: the two openings beside the pocket.

- Default: 24.5 mm
- Range: 5 to 60 mm, in steps of 0.5 mm
- Moves: pocket, wing openings

Note: Only acts when size is Custom.

### Pocket reference drop

Customizer name: `custom_pocket_dome_drop`

Changes no shape of the pocket, because the recess outline is built from the plug width at the plug end and the side taper, and this reference point cancels out of it.

No picture. Changes no shape: the recess is a rounded-nose shape whose width at the plug end is the pocket width and whose walls follow the side taper, so this reference point cancels out; measured with straight and with tapered walls.

- Default: 2.15 mm
- Range: 0 to 8 mm, in steps of 0.05 mm

### Pocket seat floor thickness

Customizer name: `custom_pocket_seat_floor`

Thins or thickens the floor left under the round seat, so the seat is cut deeper or shallower.

![Pocket seat floor thickness: before and after, 3.175 to 1.5 mm; red marks the seat.](../../dials/one-sided/custom_pocket_seat_floor.svg)

Two vertical slices of the one-sided puller at x = 0 mm, before left and after right, the top face up. Left: the defaults with hand size set to Custom, the plug in teal in the cut. Right: pocket seat floor thickness at 1.5 mm. Marked in red: 1, the seat: the round recess at the plug end.

- Default: 3.175 mm
- Range: 0 to 8 mm, in steps of 0.025 mm
- Moves: seat

Note: Only acts when size is Custom.

### Plug recess floor thickness

Customizer name: `custom_pocket_floor`

Thins or thickens the floor left under the plug recess, so the recess is cut deeper or shallower.

![Plug recess floor thickness: before and after, 3.81 to 2 mm; red marks the pocket and the seat.](../../dials/one-sided/custom_pocket_floor.svg)

Two vertical slices of the one-sided puller at x = 0 mm, before left and after right, the top face up. Left: the defaults with hand size set to Custom, the plug in teal in the cut. Right: plug recess floor thickness at 2 mm. Marked in red: 1, the seat and the pocket: the round recess at the plug end; the plug recess on the centerline.

- Default: 3.81 mm
- Range: 0 to 12 mm, in steps of 0.025 mm
- Moves: pocket, seat

Note: Only acts when size is Custom.

### Pocket side taper

Customizer name: `custom_pocket_side_angle`

Tilts the pocket's side walls inward toward the cord end, and the zip-tie holes and strap slots lean in along the same line.

![Pocket side taper: before and after, 0 to 10 mm; red marks the pocket, the wing openings and the zip-tie holes.](../../dials/one-sided/custom_pocket_side_angle.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom, a 25 mm wide plug in teal. Right: pocket side taper at 10 mm. Marked in red: 1, the zip-tie holes, the wing openings and the pocket: the four small holes beside the pocket; the two openings beside the pocket; the plug recess on the centerline.

- Default: 0 mm
- Range: -15 to 25 mm, in steps of 0.5 mm
- Moves: pocket, wing openings, zip-tie holes

Note: Only acts when size is Custom.

## Finger Holes (Custom size only)

### Finger holes on or off

Customizer name: `custom_enable_finger_holes`

Cuts or leaves out both finger holes.

![Finger holes on or off: before and after, true to false; red marks the body edge and the finger holes.](../../dials/one-sided/custom_enable_finger_holes.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom, a 25 mm wide plug in teal. Right: finger holes on or off set to false. Marked in red: 1, the finger holes and the body edge: the two large holes in the lower half; the outer outline, removed. Everything else follows the outline.

- Default: On
- Choices: On or off (a check box)
- Moves: body edge, finger holes

Note: Only acts when size is Custom.

### Finger hole diameter

Customizer name: `custom_finger_hole_diameter`

Widens both finger holes.

![Finger hole diameter: before and after, 25.4 to 22 mm; red marks the finger holes and the wing openings.](../../dials/one-sided/custom_finger_hole_diameter.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom, a 25 mm wide plug in teal. Right: finger hole diameter at 22 mm. Marked in red: 1, the wing openings: the two openings beside the pocket. 2, the finger holes: the two large holes in the lower half. The body edge, the pocket, the seat and the wall notch stay where they were.

- Default: 25.4 mm
- Range: 15 to 40 mm, in steps of 0.1 mm
- Moves: finger holes, wing openings

Note: Only acts when size is Custom.

### Finger hole spacing

Customizer name: `custom_finger_hole_spacing`

Moves the two finger holes farther apart or closer together.

![Finger hole spacing: before and after, 33 to 40 mm; red marks the finger holes and the wing openings.](../../dials/one-sided/custom_finger_hole_spacing.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom, a 25 mm wide plug in teal. Right: finger hole spacing at 40 mm. Marked in red: 1, the wing openings: the two openings beside the pocket. 2, the finger holes: the two large holes in the lower half.

- Default: 33 mm
- Range: 20 to 50 mm, in steps of 0.5 mm
- Moves: finger holes, wing openings

Note: Only acts when size is Custom.

### Finger hole position

Customizer name: `custom_finger_hole_y_position`

Slides both finger holes up toward the pocket or down toward the cord hook.

![Finger hole position: before and after, 19.8 to 26 mm; red marks the finger holes, the pocket, the wing openings and the zip-tie holes.](../../dials/one-sided/custom_finger_hole_y_position.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom, a 25 mm wide plug in teal. Right: finger hole position at 26 mm. Marked in red: 1, the zip-tie holes and the pocket. 2, the zip-tie holes, the finger holes and the wing openings.

- Default: 19.8 mm
- Range: 10 to 50 mm, in steps of 0.1 mm
- Moves: finger holes, pocket, wing openings, zip-tie holes

Note: Only acts when size is Custom.

## T Hook (Custom size only)

### Cord hook on or off

Customizer name: `custom_enable_t_hook`

Cuts or leaves out the cord hook at the cord end.

![Cord hook on or off: before and after, true to false; red marks the hook.](../../dials/one-sided/custom_enable_t_hook.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom, a 25 mm wide plug in teal. Right: cord hook on or off set to false. Marked in red: 1, the hook: the cord hook slot in the bottom edge. The body edge, the pocket, the seat and the wall notch stay where they were.

- Default: On
- Choices: On or off (a check box)
- Moves: hook

Note: Only acts when size is Custom.

### Hook slot width

Customizer name: `custom_t_hook_base_gap`

Widens the slot the cord slides into at the cord end.

![Hook slot width: before and after, 4.7625 to 7 mm; red marks the hook.](../../dials/one-sided/custom_t_hook_base_gap.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom, a 25 mm wide plug in teal. Right: hook slot width at 7 mm. Marked in red: 1, the hook: the cord hook slot in the bottom edge. The body edge, the pocket, the seat and the wall notch stay where they were.

- Default: 4.7625 mm
- Range: 3 to 10 mm, in steps of 0.05 mm
- Moves: hook

Note: Only acts when size is Custom.

### Hook length

Customizer name: `custom_t_hook_length`

Runs the cord hook farther into the body from the cord end.

![Hook length: before and after, 10.16 to 15 mm; red marks the finger holes, the hook, the pocket, the wing openings and the zip-tie holes.](../../dials/one-sided/custom_t_hook_length.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom, a 25 mm wide plug in teal. Right: hook length at 15 mm. Marked in red: 1, the finger holes: the two large holes in the lower half. 2, the finger holes and the hook: the two large holes in the lower half; the cord hook slot in the bottom edge.

- Default: 10.16 mm
- Range: 6 to 20 mm, in steps of 0.05 mm
- Moves: finger holes, hook, pocket, wing openings, zip-tie holes

Note: Only acts when size is Custom.

### Hook crossbar width

Customizer name: `custom_t_hook_holder_width`

Widens the crossbar the cord hooks under at the top of the slot.

![Hook crossbar width: before and after, 11.1125 to 16 mm; red marks the finger holes, the hook, the wing openings and the zip-tie holes.](../../dials/one-sided/custom_t_hook_holder_width.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom, a 25 mm wide plug in teal. Right: hook crossbar width at 16 mm. Marked in red: 1, the finger holes and the hook: the two large holes in the lower half; the cord hook slot in the bottom edge. 2, the finger holes: the two large holes in the lower half.

- Default: 11.1125 mm
- Range: 8 to 25 mm, in steps of 0.05 mm
- Moves: finger holes, hook, wing openings, zip-tie holes

Note: Only acts when size is Custom.

### Hook crossbar height

Customizer name: `custom_t_hook_holder_length`

Makes the crossbar opening taller or shorter along the body.

![Hook crossbar height: before and after, 5.08 to 8 mm; red marks the hook.](../../dials/one-sided/custom_t_hook_holder_length.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom, a 25 mm wide plug in teal. Right: hook crossbar height at 8 mm. Marked in red: 1, the hook: the cord hook slot in the bottom edge. The body edge, the pocket, the seat and the wall notch stay where they were.

- Default: 5.08 mm
- Range: 2 to 15 mm, in steps of 0.05 mm
- Moves: hook

Note: Only acts when size is Custom.

### Hook slot inset

Customizer name: `custom_t_hook_gap_offset`

Changes no shape of the printed tool, because the J-hook cord catch does not read this dial.

No picture. Changes no shape: the J-hook cord catch is drawn without this dial; it only appears in the Cutouts Only 2D debug overlay.

- Default: 0 mm
- Range: 0 to 8 mm, in steps of 0.5 mm

### Hook stem side offset

Customizer name: `custom_t_hook_leg_offset`

Moves nothing on the hook itself, and only pushes the finger holes up when the auto-fit keep-out around the hook grows with it.

![Hook stem side offset: before and after, 0 to 3 mm; red marks the finger holes, the wing openings and the zip-tie holes.](../../dials/one-sided/custom_t_hook_leg_offset.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom, a 25 mm wide plug in teal. Right: hook stem side offset at 3 mm. Marked in red: 1, the wing openings: the two openings beside the pocket. 2, the zip-tie holes: the four small holes beside the pocket. 3, the finger holes: the two large holes in the lower half.

- Default: 0 mm
- Range: -5 to 5 mm, in steps of 0.5 mm
- Moves: finger holes, wing openings, zip-tie holes

Note: Only acts when size is Custom; the J-hook cord catch is drawn without this dial, and only the auto-fit clamp on the finger holes reads it.

### Hook stem offset

Customizer name: `custom_t_hook_stem_offset`

Shifts the cord slot sideways along the crossbar, making the J of the hook deeper or shallower.

![Hook stem offset: before and after, 4.5 to 7 mm; red marks the hook.](../../dials/one-sided/custom_t_hook_stem_offset.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom, a 25 mm wide plug in teal. Right: hook stem offset at 7 mm. Marked in red: 1, the hook: the cord hook slot in the bottom edge. The body edge, the pocket, the seat and the wall notch stay where they were.

- Default: 4.5 mm
- Range: 0 to 8 mm, in steps of 0.05 mm
- Moves: hook

Note: Only acts when size is Custom.

### Hook catch reach

Customizer name: `custom_t_hook_catch_reach`

Extends the crossbar past the slot on the catch side, lengthening the lip the cord hooks under.

![Hook catch reach: before and after, 4.55 to 8 mm; red marks the hook.](../../dials/one-sided/custom_t_hook_catch_reach.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom, a 25 mm wide plug in teal. Right: hook catch reach at 8 mm. Marked in red: 1, the hook: the cord hook slot in the bottom edge. The body edge, the pocket, the seat and the wall notch stay where they were.

- Default: 4.55 mm
- Range: 0 to 10 mm, in steps of 0.05 mm
- Moves: hook

Note: Only acts when size is Custom.

### Hook tip drop

Customizer name: `custom_t_hook_tip_drop`

Changes no shape of the printed tool, because the hook slot's mouth already opens through the cord end.

No picture. Only acts when size is Custom. Changes no shape: the hook slot's mouth already opens through the cord end (the body ends at Y = 0), so sagging the mouth farther below that edge cuts only air; measured at 1.98, 4 and 0.

- Default: 1.98 mm
- Range: 0 to 5 mm, in steps of 0.05 mm

## Plug Wall Notch (Custom size only)

### Wall notch on or off

Customizer name: `custom_enable_plug_wall_notch`

Cuts or leaves out the notch at the plug end that straddles the outlet's cover plate.

![Wall notch on or off: before and after, true to false; red marks the wall notch.](../../dials/one-sided/custom_enable_plug_wall_notch.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom, a 25 mm wide plug in teal. Right: wall notch on or off set to false. Marked in red: 1, the wall notch: the notch in the top edge. The body edge, the pocket, the seat and the wing openings stay where they were.

- Default: On
- Choices: On or off (a check box)
- Moves: wall notch

Note: Only acts when size is Custom.

### Wall notch width

Customizer name: `custom_plug_wall_notch_width`

Widens or narrows the notch at the plug end.

![Wall notch width: before and after, 26.67 to 20 mm; red marks the wall notch.](../../dials/one-sided/custom_plug_wall_notch_width.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom, a 25 mm wide plug in teal. Right: wall notch width at 20 mm. Marked in red: 1, the wall notch: the notch in the top edge. The body edge, the pocket, the seat and the wing openings stay where they were.

- Default: 26.67 mm
- Range: 5 to 40 mm, in steps of 0.01 mm
- Moves: wall notch

Note: Only acts when size is Custom.

### Wall notch depth

Customizer name: `custom_plug_wall_notch_height`

Cuts the notch deeper or shallower into the plug end.

![Wall notch depth: before and after, 3.81 to 7 mm; red marks the wall notch, the wing openings and the zip-tie holes.](../../dials/one-sided/custom_plug_wall_notch_height.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom, a 25 mm wide plug in teal. Right: wall notch depth at 7 mm. Marked in red: 1, the zip-tie holes and the wall notch: the four small holes beside the pocket; the notch in the top edge. The body edge, the pocket, the seat and the wing openings stay where they were.

- Default: 3.81 mm
- Range: 0 to 10 mm, in steps of 0.05 mm
- Moves: wall notch, wing openings, zip-tie holes

Note: Only acts when size is Custom.

### Wall notch corner rounding

Customizer name: `custom_plug_wall_notch_rounding`

Rounds or squares the notch's two inner corners.

![Wall notch corner rounding: before and after, 2.54 to 0 mm; red marks the wall notch.](../../dials/one-sided/custom_plug_wall_notch_rounding.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom, a 25 mm wide plug in teal. Right: wall notch corner rounding at 0 mm. Marked in red: 1, the wall notch: the notch in the top edge. The body edge, the pocket, the seat and the wing openings stay where they were.

- Default: 2.54 mm
- Range: 0 to 5 mm, in steps of 0.01 mm
- Moves: wall notch

Note: Only acts when size is Custom.

## Zip Tie Holes (Custom size only)

### Zip-tie hole diameter

Customizer name: `custom_zip_tie_hole_diameter`

Widens every zip-tie hole.

![Zip-tie hole diameter: before and after, 5.08 to 7 mm; red marks the wing openings and the zip-tie holes.](../../dials/one-sided/custom_zip_tie_hole_diameter.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom, a 25 mm wide plug in teal. Right: zip-tie hole diameter at 7 mm. Marked in red: 1, the zip-tie holes: the four small holes beside the pocket. 2, the wing openings: the two openings beside the pocket. The body edge, the pocket, the seat and the wall notch stay where they were.

- Default: 5.08 mm
- Range: 2 to 8 mm, in steps of 0.02 mm
- Moves: wing openings, zip-tie holes

Note: Only acts when size is Custom.

### Zip-tie row spacing

Customizer name: `custom_zip_tie_height_spacing`

Moves the second row of zip-tie holes closer to or farther from the first.

![Zip-tie row spacing: before and after, 17.78 to 12 mm; red marks the wing openings and the zip-tie holes.](../../dials/one-sided/custom_zip_tie_height_spacing.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom, a 25 mm wide plug in teal. Right: zip-tie row spacing at 12 mm. Marked in red: 1, the wing openings: the two openings beside the pocket. 2, the zip-tie holes: the four small holes beside the pocket.

- Default: 17.78 mm
- Range: 5 to 30 mm, in steps of 0.02 mm
- Moves: wing openings, zip-tie holes

Note: Only acts when size is Custom.

### Zip-tie column spacing

Customizer name: `custom_zip_tie_width_spacing`

Moves no zip-tie hole, because the two columns follow the pocket wall, and only feeds the auto-fit keep-out that can trim the row spacing by a hair.

No picture. Changes no shape of its own: the zip-tie columns sit zip_edge_offset inside the pocket wall; this dial only feeds the auto-fit finger keep-out, which trimmed the row spacing by 0.05 mm at the Custom defaults.

- Default: 17.7 mm
- Range: 10 to 50 mm, in steps of 0.02 mm

### Zip-tie distance from the notch

Customizer name: `custom_zip_tie_distance_from_notch`

Moves the first row of zip-tie holes farther from the wall notch, and the second row follows.

![Zip-tie distance from the notch: before and after, 5.1 to 9 mm; red marks the wing openings and the zip-tie holes.](../../dials/one-sided/custom_zip_tie_distance_from_notch.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom, a 25 mm wide plug in teal. Right: zip-tie distance from the notch at 9 mm. Marked in red: 1, the zip-tie holes: the four small holes beside the pocket. 2, the wing openings: the two openings beside the pocket.

- Default: 5.1 mm
- Range: 1 to 15 mm, in steps of 0.05 mm
- Moves: wing openings, zip-tie holes

Note: Only acts when size is Custom.

### Zip-tie countersink

Customizer name: `custom_zip_tie_countersink`

Flares the top of the zip-tie holes wider so the tie head sits flush.

![Zip-tie countersink: before and after, 0.9 to 2.5 mm; red marks the pocket and the zip-tie holes.](../../dials/one-sided/custom_zip_tie_countersink.svg)

Two vertical slices of the one-sided puller at x = 10.4 mm, before left and after right, the top face up. Left: the defaults with hand size set to Custom, the plug in teal in the cut. Right: zip-tie countersink at 2.5 mm. Marked in red: 1, the zip-tie holes: the four small holes beside the pocket. 2, the zip-tie holes and the pocket: the four small holes beside the pocket; the plug recess on the centerline.

- Default: 0.9 mm
- Range: 0 to 3 mm, in steps of 0.05 mm
- Moves: pocket, zip-tie holes

Note: Only acts when size is Custom.

## Velcro / Wing Strap Holes (Custom size only)

### Strap slot length

Customizer name: `custom_velcro_hole_length`

Lengthens each plain strap slot along its lean.

![Strap slot length: before and after, 12 to 18 mm; red marks the classic slots.](../../dials/one-sided/custom_velcro_hole_length.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom and strap opening style set to Classic slot, a 25 mm wide plug in teal. Right: strap slot length at 18 mm. Marked in red: 1, the classic slots: the two slots beside the pocket. The body edge, the pocket, the seat and the wall notch stay where they were.

- Default: 12 mm
- Range: 6 to 20 mm, in steps of 0.5 mm
- Moves: classic slots

Note: Only acts when size is Custom and velcro_style is Classic slot, or when velcro_placement is Manual.

### Strap slot width

Customizer name: `custom_velcro_hole_width`

Widens each plain strap slot.

![Strap slot width: before and after, 7 to 11 mm; red marks the classic slots.](../../dials/one-sided/custom_velcro_hole_width.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom and strap opening style set to Classic slot, a 25 mm wide plug in teal. Right: strap slot width at 11 mm. Marked in red: 1, the classic slots: the two slots beside the pocket. The body edge, the pocket, the seat and the wall notch stay where they were.

- Default: 7 mm
- Range: 3 to 14 mm, in steps of 0.5 mm
- Moves: classic slots

Note: Only acts when size is Custom and velcro_style is Classic slot, or when velcro_placement is Manual.

### Strap slot distance from the centerline

Customizer name: `custom_velcro_hole_x_center`

Moves the two plain strap slots closer to or farther from the centerline.

![Strap slot distance from the centerline: before and after, 19.4 to 14 mm; red marks the classic slots.](../../dials/one-sided/custom_velcro_hole_x_center.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom and strap opening style set to Classic slot, a 25 mm wide plug in teal. Right: strap slot distance from the centerline at 14 mm. Marked in red: 1, the classic slots: the two slots beside the pocket.

- Default: 19.4 mm
- Range: 5 to 35 mm, in steps of 0.05 mm
- Moves: classic slots

Note: Only acts when size is Custom and velcro_style is Classic slot, or when velcro_placement is Manual.

### Strap slot position along the body

Customizer name: `custom_velcro_hole_y_center`

Slides the two plain strap slots toward the cord end or the plug end.

![Strap slot position along the body: before and after, 46 to 38 mm; red marks the classic slots.](../../dials/one-sided/custom_velcro_hole_y_center.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom and strap opening style set to Classic slot, a 25 mm wide plug in teal. Right: strap slot position along the body at 38 mm. Marked in red: 1, the classic slots: the two slots beside the pocket.

- Default: 46 mm
- Range: 30 to 80 mm, in steps of 0.5 mm
- Moves: classic slots

Note: Only acts when size is Custom, velcro_style is Classic slot and velcro_placement is Auto.

### Strap slot lean

Customizer name: `custom_velcro_hole_rotation`

Leans the two plain strap slots more or less steeply, mirrored on the two sides.

![Strap slot lean: before and after, 23.5 to 60 deg; red marks the classic slots.](../../dials/one-sided/custom_velcro_hole_rotation.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom and strap opening style set to Classic slot, a 25 mm wide plug in teal. Right: strap slot lean at 60 deg. Marked in red: 1, the classic slots: the two slots beside the pocket.

- Default: 23.5 degrees
- Range: 0 to 180 degrees, in steps of 0.5 degrees
- Moves: classic slots

Note: Only acts when size is Custom and velcro_style is Classic slot, or when velcro_placement is Manual.

## Edge Rounding (Custom size only)

### Body side rounding

Customizer name: `custom_body_side_rounding`

Rounds the body outline's corners more or less, down to the plain octagon at 0.

![Body side rounding: before and after, 15.85 to 5 mm; red marks the body edge.](../../dials/one-sided/custom_body_side_rounding.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom, a 25 mm wide plug in teal. Right: body side rounding at 5 mm. Marked in red: 1, the body edge: the outer outline. Everything else follows the outline.

- Default: 15.85 mm
- Range: 0 to 30 mm, in steps of 0.05 mm
- Moves: body edge

Note: Only acts when size is Custom.

### Top edge rounding

Customizer name: `custom_body_top_rounding`

Rounds or squares the edge where the body's top face meets its sides.

![Top edge rounding: before and after, 2.54 to 0 mm; red marks the body edge.](../../dials/one-sided/custom_body_top_rounding.svg)

Two vertical slices of the one-sided puller at y = 35 mm, before left and after right, the top face up. Left: the defaults with hand size set to Custom, the plug in teal in the cut. Right: top edge rounding at 0 mm. Marked in red: 1, the body edge: the outer outline. Everything else follows the outline.

- Default: 2.54 mm
- Range: 0 to 5 mm, in steps of 0.01 mm
- Moves: body edge

Note: Only acts when size is Custom.

### Bottom edge rounding

Customizer name: `custom_body_bottom_rounding`

Rounds or squares the edge where the body's bottom face meets its sides.

![Bottom edge rounding: before and after, 0 to 2 mm; red marks the body edge.](../../dials/one-sided/custom_body_bottom_rounding.svg)

Two vertical slices of the one-sided puller at y = 35 mm, before left and after right, the top face up. Left: the defaults with hand size set to Custom, the plug in teal in the cut. Right: bottom edge rounding at 2 mm. Marked in red: 1, the body edge: the outer outline. Everything else follows the outline.

- Default: 0 mm
- Range: 0 to 5 mm, in steps of 0.1 mm
- Moves: body edge

Note: Only acts when size is Custom.

### Strap slot corner rounding

Customizer name: `custom_velcro_side_rounding`

Rounds the four corners of each plain strap slot.

![Strap slot corner rounding: before and after, 0 to 2.5 mm; red marks the classic slots.](../../dials/one-sided/custom_velcro_side_rounding.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom and strap opening style set to Classic slot, a 25 mm wide plug in teal. Right: strap slot corner rounding at 2.5 mm. Marked in red: 1, the classic slots: the two slots beside the pocket. The body edge, the pocket, the seat and the wall notch stay where they were.

- Default: 0 mm
- Range: 0 to 3 mm, in steps of 0.5 mm
- Moves: classic slots

Note: Only acts when size is Custom and velcro_style is Classic slot, or when velcro_placement is Manual.

### Strap opening edge rounding

Customizer name: `custom_velcro_top_bottom_rounding`

Flares the top and bottom edges of the strap openings so the strap does not chafe.

![Strap opening edge rounding: before and after, 0 to 1.5 mm; red marks the pocket and the wing openings.](../../dials/one-sided/custom_velcro_top_bottom_rounding.svg)

Two vertical slices of the one-sided puller at y = 46 mm, before left and after right, the top face up. Left: the defaults with hand size set to Custom, the plug in teal in the cut. Right: strap opening edge rounding at 1.5 mm. Marked in red: 1, the wing openings: the two openings beside the pocket. 2, the wing openings and the pocket: the two openings beside the pocket; the plug recess on the centerline.

- Default: 0 mm
- Range: 0 to 3 mm, in steps of 0.1 mm
- Moves: pocket, wing openings

Note: Only acts when size is Custom.

### Finger hole rim rounding

Customizer name: `custom_finger_hole_rounding`

Rounds or squares the rims of both finger holes on both faces.

![Finger hole rim rounding: before and after, 2.5 to 0 mm; red marks the finger holes.](../../dials/one-sided/custom_finger_hole_rounding.svg)

Two vertical slices of the one-sided puller at y = 19.8 mm, before left and after right, the top face up. Left: the defaults with hand size set to Custom, the plug in teal in the cut. Right: finger hole rim rounding at 0 mm. Marked in red: 1, the finger holes: the two large holes in the lower half. The body edge, the pocket, the seat and the wall notch stay where they were.

- Default: 2.5 mm
- Range: 0 to 5 mm, in steps of 0.1 mm
- Moves: finger holes

Note: Only acts when size is Custom.

### Hook crossbar corner rounding

Customizer name: `custom_t_hook_holder_side_rounding`

Rounds or squares the top corners of the hook's crossbar.

![Hook crossbar corner rounding: before and after, 1.27 to 0 mm; red marks the hook.](../../dials/one-sided/custom_t_hook_holder_side_rounding.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom, a 25 mm wide plug in teal. Right: hook crossbar corner rounding at 0 mm. Marked in red: 1, the hook: the cord hook slot in the bottom edge. The body edge, the pocket, the seat and the wall notch stay where they were.

- Default: 1.27 mm
- Range: 0 to 3 mm, in steps of 0.01 mm
- Moves: hook

Note: Only acts when size is Custom.

### Hook slot corner rounding

Customizer name: `custom_t_hook_gap_side_rounding`

Changes no shape of the printed tool, because the J-hook cord catch draws its own corners.

No picture. Changes no shape: the J-hook cord catch is drawn without this dial; it only appears in the Cutouts Only 2D debug overlay.

- Default: 0 mm
- Range: 0 to 3 mm, in steps of 0.1 mm

### Hook edge rounding

Customizer name: `custom_t_hook_top_bottom_rounding`

Flares the top and bottom edges of the cord hook's slot and crossbar.

![Hook edge rounding: before and after, 0 to 2 mm; red marks the hook.](../../dials/one-sided/custom_t_hook_top_bottom_rounding.svg)

Two vertical slices of the one-sided puller at x = 4.5 mm, before left and after right, the top face up. Left: the defaults with hand size set to Custom, the plug in teal in the cut. Right: hook edge rounding at 2 mm. Marked in red: 1, the hook: the cord hook slot in the bottom edge. The body edge, the pocket, the seat and the wall notch stay where they were.

- Default: 0 mm
- Range: 0 to 3 mm, in steps of 0.1 mm
- Moves: hook

Note: Only acts when size is Custom.

## Render, export and print

1. On the computer, press **F6** (or **Design ▸ Render**) and wait for the progress bar to finish; a render takes from a few seconds to a minute. In Forge, the preview draws on its own: wait for **Preview ready** under the picture.
2. Look for red text beside the part. If there is any, read it: it names the measurement to fix, and the part will not fit until it is gone.
3. Save the file: on the computer, **File ▸ Export ▸ Export as STL**; in Forge, **Export STL**. If you export without rendering, OpenSCAD asks you to render first: press F6 and export again. The quick preview (F5) looks complete but cannot be exported.

Load the STL into your slicer with these settings:

| Setting | Value |
| ------- | ----- |
| Orientation | flat face down on the bed, the plug pocket facing up. No supports. |
| Layer height | 0.2 mm |
| Walls | 3 to 4: you pull hard on this part |
| Infill | 25 to 35 percent |
| Material | PETG. PLA, ABS and ASA work too. Never a flexible filament: the tool has to stay stiff. |

The picture shows nine one-sided pullers printed this way, in three sizes, all flat on the bed.

![Nine one-sided pullers in three sizes printed flat on the printer bed, the pocket side up, no supports.](../../images/print-bed-nine-tools.jpg)

### What to buy

Nothing to solder and almost nothing to buy: filament, zip ties, and a strap if you want one. For the one-sided puller you need two zip ties up to 4.8 mm wide (about 200 mm long), or one hook-and-loop strap 10 to 25 mm wide. The filament each tool uses, and the strap widths that fit, are in the [bill of materials](../bom.md).

## Assemble

The tool goes onto the plug while the plug is in the outlet. You need two zip ties, or a strap; the sizes are in the [bill of materials](../bom.md).

1. Seat the tool on the plugged-in plug: the plug sits in the pocket, and the notch at the plug end straddles the outlet cover.
2. Press the cord into the hook at the cord end so it cannot slip out.
3. Push the first zip tie down through one of the zip-tie holes beside the pocket.
4. Pass the tie around the plug body and up through the hole on the other side of the pocket.
5. Pull the tie tight and cut off the tail.
6. Fit the second zip tie through the other pair of holes the same way.
7. Instead of the ties, or as well: thread the strap through the two wing openings and around the plug, and close it. The picture shows a strap holding the tool on a three-prong plug.

   ![The one-sided puller at Medium size held on a black three-prong plug by a strap through its wing openings, on the printer bed beside a printed hand model for scale.](../../images/one-sided-3-prong-plug-medium.jpg)

The tool can stay on the plug between uses. The pictures below show the finished one-sided puller strapped to a lamp plug at Small, Medium and Large, next to a printed hand for scale.

![The one-sided puller at Small size strapped to a black two-prong lamp plug, on the printer bed beside a printed hand model for scale.](../../images/one-sided-lamp-plug-small.jpg)

![The one-sided puller at Medium size strapped to a black two-prong lamp plug, beside a printed hand model for scale.](../../images/one-sided-lamp-plug-medium.jpg)

![The one-sided puller at Large size strapped to a black two-prong lamp plug, beside a printed hand model for scale.](../../images/one-sided-lamp-plug-large.jpg)

## Use it

The plug puller is for anyone who cannot grip a plug and pull it out of an outlet: arthritis, low grip strength, tremor, a small hand, one hand. Two finger holes take the pull, so your whole hand does the work instead of a fingertip pinch. The tool touches only the plug's sides and back, never the outlet.

1. Seat the tool on the plug while the plug is in the outlet: the plug in the pocket, the notch at the plug end over the outlet cover.
2. Press the cord into the hook at the cord end.
3. Put two fingers through the holes.
4. Pull straight back, away from the wall.

The tool can stay strapped to the plug between uses.

### Safety

- Nothing goes between the plug face and the outlet cover: the tool grips only the plug's sides and back.
- Pull straight out. Never lever the tool sideways or up and down.
- Do not use the tool on a damaged cord, a cracked plug, or a plug that is warm to the touch.
- Keep your fingers away from the prongs as the plug comes out.
- The tool has no conductive parts, but it is still plastic near electricity: if it cracks, stop using it.

### Care

- Before each use, look at the finger holes and the places the zip ties or the strap pass through for cracks. A cracked tool is replaced, not repaired.
- Replace a zip tie that has loosened.
- Wash with soap and warm water. No solvents: they attack PETG and PLA.
- Keep it out of direct sun and off heaters; the plastic softens when hot.

## If the print does not fit

Printed your tool and something is not quite right? Find your symptom below. Every fix names one measurement to change and by how much. Change it in the Customizer, render and export again, and reprint. You never need to touch anything below the four Steps.

> Nudge in small steps, 0.5 to 2 mm. Looser always beats tighter: a slightly roomy tool still works, a tight one does not.

| # | Symptom | Change this | By how much |
| --- | ------- | ----------- | ----------- |
| 1 | The plug body rubs the sides of the notch, or will not slide in | Plug width at the prong end | +1 mm |
| 2 | The plug falls out of the notch or rattles side to side | Plug width at the prong end | −0.5 mm |
| 3 | The plug will not seat down into the pocket | Plug length | +2 mm |
| 4 | The plug seats, but the tool overhangs the plug by a lot | Plug length | −2 mm |
| 5 | The plug sits proud of the pocket, or the tool rocks on top of it | Plug thickness, at the end that measured fatter | +2 mm |
| 6 | The pocket walls pinch the plug's cord end, or gape at it | Plug width at the cord end | +1 mm if it pinches, −1 mm if it gapes |
| 7 | The hook will not take the cord, or the cord has to be forced in | Cord thickness | +0.5 mm |
| 8 | The cord slips out of the hook while pulling | Cord thickness | −0.5 mm |
| 9 | The tool will not sit flat against the wall; the outlet cover pushes it away | Outlet cover plate style | the next bigger style: Standard flat plate, then Rocker / Decora, then Oversized / Jumbo |
| 10 | Fingers pinch in the holes, or a knuckle drags on the rim | Hand size up one step, or Measure my hand with the finger width | +1 mm |
| 11 | Fingers swim in the holes and the pull feels sloppy | Hand size down one step, or Measure my hand with the finger width | −1 mm |
| 12 | The tool's edges dig into your palm, or it feels too wide | Hand size down one step, or Measure my hand with the hand width | −5 mm |
| 13 | The tool feels too small in the hand; fingers crowd the edges | Hand size up one step, or Measure my hand with the hand width | +5 mm |
| 14 | The tool is too wide for a cramped outlet corner | Hand size down one step: the body follows the hand size | |
| 15 | The strap keeps sliding off the plug | Attachment: Zip ties + Velcro, and use both | |
| 16 | A smooth round plug still slips out of the zip-tie hold | Thread a zip tie down one zip-tie hole, around the plug body, up the opposite hole, and cinch it | |
| 17 | The hook is on the wrong side for your hand | Step 4: Hook side, Left or Right | |
| 18 | The strap will not thread through the wing opening | Step 3: a smaller Strap width, or a narrower strap; the wing is sized to it | |

### Red warning tags

If the preview shows red text, or a red text tag printed next to your part, the file found a problem before you wasted a full print. That is on purpose: a bad file fails loudly instead of silently. Read the tag, fix that measurement, and export again.

| The tag says | What it means | What to do |
| ------------ | ------------- | ---------- |
| `CHECK PLUG LENGTH MEASUREMENT (MM?)`, and the same for `PLUG WIDTH`, `PLUG THICKNESS`, `CORD THICKNESS`, `FINGER WIDTH`, `HAND WIDTH` | That number is outside any plausible mm value: usually inches typed into a mm field (1.25 instead of 32) | Measure again with the mm side of the ruler and type it again |
| `FINGER TOO BIG FOR HAND WIDTH - RECHECK BOTH` | Finger holes that wide cannot fit inside a body sized for that hand width | Measure both the finger width and the hand width again; one of them is off |
| `PLUG TOO WIDE FOR THIS DESIGN (MAX 38MM)` | The plug, at the prong end, is wider than the tool's end can open | The one-sided puller tops out near 38 mm of plug width; a plug that wide needs the two-sided puller |
| `PLUG THICKER THAN 24MM - USE THE TWO-SIDED PULLER FILE` | The plug is 24 mm thick or more at one end: too thick for this tool's pocket | Open the two-sided puller and fill in its Step 1; or measure the thickness again at both ends |
| `PLUG LONGER THAN POCKET LIMIT - POCKET SHORTENED` | The plug is longer than the pocket can be inside the 120 mm body, so the pocket stops short | Check the plug length; if it is real, print and try it |
| `PLUG WIDTH TAPER TOO STEEP - RECHECK BOTH WIDTHS` | The two widths describe a taper steeper than the pocket walls can follow | Measure the plug width at the prong end and at the cord end again; one of them is probably off |
| `CORD TOO THICK FOR HOOK SLOT` | The hook slot cannot open wide enough for that cord | Measure the cord's thin side again; a cord past about 9 mm does not fit the hook |
| `FINGER HOLES HIT PLUG POCKET` | Your finger and plug numbers make the holes collide with the plug pocket | Reduce the finger width slightly, or check the plug length again |
| `FINGER HOLES TOO CLOSE - WEAK BRIDGE` | The strip of plastic between the two holes is too thin to be strong | Reduce the finger width by 1 mm |
| `FINGER HOLES OUTSIDE BODY - INCREASE HAND WIDTH` | The holes for your fingers do not fit inside a body sized for your hand width | Increase the hand width, or measure both again |
| `PLUG TOO WIDE FOR TOOL END - CHECK PLUG WIDTH` | The notch came out wider than the tool's end itself | Measure the plug width again; it is probably too large |
| `PLUG SEAT OVERHANGS BODY - RECHECK PLUG WIDTH`, `PLUG POCKET OVERHANGS BODY - RECHECK PLUG WIDTH` | The plug pocket is wider than the tool body at that spot | Measure the plug width again, or go up a hand size so the body grows |
| `WING OPENING SMALLER THAN STRAP WIDTH` | The wing opening is too narrow to pass the strap you set | Lower the strap width (Step 3), or switch the strap opening style to Classic slot |
| `WING WEB COLLAPSED - NO ROOM FOR STRAP` | Features crowded the wing until no opening was left | Go up a hand size (a bigger body), or lower the strap width |
| `ZIP TIE HOLES HIT FINGER HOLES` | A zip-tie row landed too close to a finger hole; Auto placement avoids this, Manual positions or auto-fit off can cause it | Move that zip-tie pair position, or turn Auto placement back on |
| `ZIP TIE ROWS OVERLAP EACH OTHER` | Two manual zip-tie rows landed on top of each other | Spread the zip-tie pair positions at least one hole diameter apart |
| `ZIP TIE HOLES HIT VELCRO SLOTS` | A zip-tie row broke into a classic strap slot | Move the zip-tie pair or the strap slot position apart |
| `SEAT HAS NO RECESS - PLUG WONT NEST`, `POCKET HAS NO RECESS - PLUG WONT NEST` | An internal geometry check; with measured numbers it should not happen | Measure every number again, following Measure your plug and your hand; if it persists, open an issue with your numbers |
| `SEAT FLOOR TOO THIN TO PRINT`, `POCKET FLOOR TOO THIN TO PRINT` | The same internal check, on the pocket floors | As above |
| `ZIP TIE GRID BELOW CORD END`, `ZIP TIE GRID OUTSIDE BODY`, anything else | The same internal check, on the zip-tie grid | As above |
| `FINGER HOLES OUTSIDE BODY`, `POCKET SEAT WIDER THAN TOP EDGE`, `POCKET WIDER THAN BODY`, `WALL NOTCH WIDER THAN TOP EDGE` | Custom size only: the Custom-mode wording of the checks above | Adjust that feature's Custom dials, or turn Auto-fit back on |

### Notes that show in the preview only

These never reach the exported file.

| The note says | What it means | What to do |
| ------------- | ------------- | ---------- |
| A green `Medium: …` or `MEASURED: …` tag | Not a warning: it confirms that your size and numbers were applied | Nothing |
| Orange `CUSTOM SLIDERS IGNORED - SET SIZE = CUSTOM` | A Custom dial was moved while a measured size is active; the console names each one | Set Step 2's hand size to Custom if you meant it, or leave the dial alone |
| Orange `AUTO-FIT ADJUSTED <n> VALUES - SEE CONSOLE` | Custom size with Auto-fit on: that many dials were clamped to keep the part printable | Read the console's `(clamped from …)` lines |

### Printing problems

| Symptom | Cause | Fix |
| ------- | ----- | --- |
| The slicer complains about floating or disconnected parts | You exported with a red warning tag showing; the tag is a separate object | Fix the named measurement first |
| Layers split at the pocket floor or around a hole | Under-extrusion, or too few walls | 3 to 4 walls and 25 percent infill or more |
| The tool snapped while pulling | A brittle material, or walls too thin | Reprint in PETG with 4 walls |

## Advanced settings

Everything below Step 4 in the Customizer is optional. The **Advanced** sections hold placement dials that work with your measured sizes and apply in every hand size. The sections marked **(Custom size only)** are for experts: they do nothing until Step 2's hand size is Custom, and then they replace the measurements entirely. Every one of these dials is described, with a picture, earlier in this guide.

### The plug side rail

One idea powers the one-sided puller's advanced dials: a line that runs down the plug's side, starting at the pocket edge on the plug face and sloping by the plug's taper. The taper comes from the two widths in Step 1 over the plug length (in Custom size, the pocket side taper dial sets it directly): a plug that is wider at the cord end gives a negative angle, and the pocket walls widen toward the cord. The pocket walls, the zip-tie holes and the manual strap slots all hang off this line, so their positions are measured in mm along the plug's side, from the plug face toward the cord, and the taper moves them together.

### Zip-tie placement

- Zip-tie hole placement on Auto spaces the number of zip-tie rows you choose (1 to 3) along the rail, and moves them closer together rather than letting a row punch into the finger holes.
- Manual places each pair with its own position dial, in mm along the rail. Manual positions are not protected from collisions: the red tags `ZIP TIE HOLES HIT FINGER HOLES`, `ZIP TIE ROWS OVERLAP EACH OTHER` and `ZIP TIE HOLES HIT VELCRO SLOTS` fire if you overlap something.
- The zip-tie hole distance from the pocket wall slides the whole column toward or away from the pocket.

### Strap slot placement

Strap slot placement on Manual slides a pair of classic slots along the rail with the strap slot position dial. The Wing style ignores manual placement, because its opening comes from the body's spare space; switch the strap opening style to Classic slot in Step 3 to use it.

### Custom size

Set Step 2's hand size to **Custom** and the measurements switch off: every dial in the **(Custom size only)** sections drives the geometry directly, the body shape, the pocket, the finger holes, the cord hook, the notch, the zip-tie grid, the strap openings and the edge rounding. The Step 3 and Step 4 choices still apply.

- **Reset Custom to the Medium reference**: render once with this on to snap everything back to the Medium reference shape, a known-good starting point, then turn it off and change what you want.
- **Auto-fit**, on by default, clamps every dial so that features stay inside the body with printable walls; each clamp is written to the console as `(clamped from …)` and the preview shows the note `AUTO-FIT ADJUSTED N VALUES`. Off, the dials are taken as typed and the red warning tags are your only guard rail.

The full list of dials with their ranges, steps and defaults is the machine-readable file [`parameter_mapping.json`](../../../parameter_mapping.json), checked against the model by the project's tests.

### Guard rails

The model never silently changes your input beyond what Auto-fit reports. Anything truly wrong prints a red warning tag flat on the bed beside the part, so an exported file shows its own defect, and writes the same message to the console. The see-through plug, the green confirmation tag and the orange notes appear in the preview only and are never exported.

### Saved settings

The Customizer panel has a preset bar above the sections: the **+** button saves your current values as a named set inside a JSON file next to the `.scad` file. The sets that ship with the project are in [`presets/Plug_Puller_Parametric.json`](../../../presets/Plug_Puller_Parametric.json). They are plain text: easy to keep, compare and share.

### The command line

Every dial can be set from the command line, which makes batches and A/B tests scriptable:

```bash
# A left-handed hook and the standard 3-prong preset
openscad -o puller.stl --backend Manifold \
  -D 'plug_preset="Standard 3-prong plug - NEMA 5-15"' -D 'hook_hand="Left"' \
  src/Plug_Puller_Parametric.scad

# A saved set of settings
openscad -o puller.stl -p presets/Plug_Puller_Parametric.json \
  -P "Left-handed + classic velcro slots" src/Plug_Puller_Parametric.scad
```

## Going deeper

- The two-sided puller has its own quick start and full guide, in the folder beside this one.
- [The design rationale](../design-rationale.md): why each default is what it is, with its number and its source.
- [The engineering reference](../../Plug_Puller_Reference.md): both tools' geometry, coordinate frames, the derivation layer, render modes, the console messages and every validation check.
- [The dial pictures](../../dials/README.md): every picture in this guide with its text alternative, and [how the pictures are described](../describing-pictures.md).
- [The bill of materials](../bom.md): zip ties, the strap, filament per tool.
