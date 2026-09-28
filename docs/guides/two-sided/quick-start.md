# Quick start, two-sided puller

The four Customizer steps of the two-sided puller, dial by dial: what each dial moves, in a picture and a sentence, with the numbers the Customizer allows.

Model version 0.13.0. The printable packet is `docs/Plug_Puller_Two_Sided_Guide.pdf`; its parts are [the quick start](quick-start.md), [the dial guide](dial-guide.md), [the measuring guide](measuring-guide.md) and [the measuring form](measuring-form.md). The dial names are written exactly as the Customizer shows them.

## Which tool this is

This packet is for the two-sided puller, src/Plug_Puller_Two_Sided.scad: two serrated plates that zip-tie around the plug and close across it, for a plug 24 mm thick or more and for a plug held from both sides, a USB-C tip or a round extension-cord plug. A thinner wall plug is the one-sided puller's job, and that tool has its own packet.

The Customizer's four steps are your plug, your size, the attachment and the print layout. The quick start below shows each step's dials, the dial guide every dial of the file, the measuring guide how to take each number, and the measuring form is the sheet you fill in first.

If red text appears beside the part in the preview, read it: it names the measurement to fix, and the part will not fit until it is gone.

In every picture: black = the tool; teal = your plug; red dotted = the edges this dial moved; the numbers match the key beside the picture.

![The two-sided puller, the four Customizer steps on a USB-C laptop plug, five stages left to right.](../../dials/two-sided/storyboard.svg)

Five stages of the two-sided puller, left to right, the top row first, the plug end at the top; red dots mark the edges each step moved. 1, the defaults: the tool as the file opens, with a 20 mm wide plug in teal. 2, Step 1 - Your Plug: plug length 23 mm, plug width at the prong end 13 mm, plug width at the cord end 13 mm, cord thickness 7 mm, plug sides Rounded sides; red on the arms, the finger lobes and the zip stations. 3, Step 2 - Size: hand size Large; red on the arms, the finger lobes and the zip stations. 4, Step 3 - Attachment: attachment Zip ties; no strap slot on a plug this short, so nothing moved. 5, Step 4 - Print Layout: both plates side by side in one file, what you print; nothing marked.

- Step 1: type your plug's numbers and pick Rounded sides or Flat sides
- Step 2: pick your hand size
- Step 3: pick how it attaches; a plug this short gets no strap slot
- Step 4: both plates in one file

## Step 1 - Your Plug

### `plug_preset`

Plug preset

![Plug preset: before and after, Measure my plug to Heavy-duty extension cord - NEMA 5-15; red marks 4 parts, named below.](../../dials/two-sided/plug_preset.svg)

Two top views of one plate of the two-sided puller, before left and after right, the plug end at the top. Left: the defaults, a 20 mm wide plug in teal. Right: plug preset set to Heavy-duty extension cord - NEMA 5-15. Marked in red: 1, the finger lobes, the arms and the plate edge. 2, the finger lobes: the two rounded lobes in the lower half. 3, the zip stations: the three small holes along each arm.

Fills in the plug's length, both widths and the cord from the measured heavy-duty cord plug, so the arms, the grip gap, the cord channel and the plate length all take that plug's shape at once.

Default Measure my plug · 5 options

Options: Measure my plug, Heavy-duty extension cord - NEMA 5-15, USB-C laptop tip, Flat 2-prong lamp plug - NEMA 1-15, Standard 3-prong plug - NEMA 5-15.

Before: Measure my plug. After: Heavy-duty extension cord - NEMA 5-15.

Moves: arms, finger lobes, plate edge, zip stations.

### `measure_plug_length`

Plug length

![Plug length: before and after, 25.5 to 40 mm; red marks the arms.](../../dials/two-sided/measure_plug_length.svg)

Two top views of one plate of the two-sided puller, before left and after right, the plug end at the top. Left: the defaults, a 20 mm wide plug in teal. Right: plug length at 40 mm: lengthens both arms so the teeth cover the whole plug body, and moves the zip-tie stations and the strap slot with them. Marked in red: 1, the arms: the two toothed arms in the upper half. The plate edge, the teeth, the finger lobes and the cord channel stay where they were.

Lengthens both arms so the teeth cover the whole plug body, and moves the zip-tie stations and the strap slot with them.

Default 25.5 · Range 12 to 85 · Step size 0.5 · Unit mm

Before: 25.5. After: 40.

Moves: arms.

### `measure_plug_width_prong_end`

Plug width at the prong end

![Plug width at the prong end: before and after, 20 to 28 mm; red marks the arms, the cord channel, the finger lobes and the zip stations.](../../dials/two-sided/measure_plug_width_prong_end.svg)

Two top views of one plate of the two-sided puller, before left and after right, the plug end at the top. Left: the defaults, a 20 mm wide plug in teal. Right: plug width at the prong end at 28 mm. Marked in red: 1, the arms: the two toothed arms in the upper half. 2, the zip stations: the three small holes along each arm. 3, the finger lobes and the cord channel: the two rounded lobes in the lower half; the gap between the lobes at the bottom.

Opens or closes the gap between the arms at their tips, where the plug's prong end sits.

Default 20 · Range 5 to 40 · Step size 0.5 · Unit mm

Before: 20. After: 28.

Moves: arms, cord channel, finger lobes, zip stations.

### `measure_plug_width_cord_end`

Plug width at the cord end

![Plug width at the cord end: before and after, 20 to 12 mm; red marks the arms, the teeth and the zip stations.](../../dials/two-sided/measure_plug_width_cord_end.svg)

Two top views of one plate of the two-sided puller, before left and after right, the plug end at the top. Left: the defaults, a 20 mm wide plug in teal. Right: plug width at the cord end at 12 mm. Marked in red: 1, the zip stations: the three small holes along each arm. 2, the teeth and the arms: the serrated inner edges of the arms; the two toothed arms in the upper half.

Opens or closes the gap between the arms at the plug's back end, so the arms taper to match the plug.

Default 20 · Range 5 to 40 · Step size 0.5 · Unit mm

Before: 20. After: 12.

Moves: arms, teeth, zip stations.

### `measure_cord_thickness`

Cord thickness

![Cord thickness: before and after, 4 to 9 mm; red marks the arms, the cord channel, the finger lobes and the zip stations.](../../dials/two-sided/measure_cord_thickness.svg)

Two top views of one plate of the two-sided puller, before left and after right, the plug end at the top. Left: the defaults, a 20 mm wide plug in teal. Right: cord thickness at 9 mm. Marked in red: 1, the finger lobes and the cord channel. 2, the finger lobes: the two rounded lobes in the lower half. 3, the finger lobes and the arms. 4, the zip stations: the three small holes along each arm.

Widens the cord channel between the finger holes, and the finger lobes move outward with it.

Default 4 · Range 1.5 to 12 · Step size 0.5 · Unit mm

Before: 4. After: 9.

Moves: arms, cord channel, finger lobes, zip stations.

### `plug_sides`

Plug sides

![Plug sides: before and after, Rounded sides to Flat sides; red marks the arms and the teeth.](../../dials/two-sided/plug_sides.svg)

Two vertical slices of the two-sided puller at y = 45 mm, before left and after right, the top face up. Left: the defaults, the plug in teal in the cut. Right: plug sides set to Flat sides. Marked in red: 1, the teeth and the arms: the serrated inner edges of the arms; the two toothed arms in the upper half. 2, the arms: the two toothed arms in the upper half.

Removes the sloped cradle from the arms' gripping edges so the teeth bite straight along a flat-sided plug.

Default Rounded sides · 2 options

Options: Rounded sides, Flat sides.

Before: Rounded sides. After: Flat sides. Section at y = 45 mm.

Moves: arms, teeth.

### `show_plug_preview`

Show the see-through plug

![Show the see-through plug: changes no shape.](../../dials/two-sided/show_plug_preview.svg)

This dial changes no shape: the see-through plug is a preview aid and is never exported.

Shows or hides the see-through plug in the preview and changes nothing in the printed plates.

Default true · true / false

## Step 2 - Size

### `size`

Hand size

![Hand size: before and after, Medium to Large; red marks the arms, the finger lobes and the zip stations.](../../dials/two-sided/size.svg)

Two top views of one plate of the two-sided puller, before left and after right, the plug end at the top. Left: the defaults, a 20 mm wide plug in teal. Right: hand size set to Large. Marked in red: 1, the zip stations: the three small holes along each arm. 2, the finger lobes and the arms: the two rounded lobes in the lower half; the two toothed arms in the upper half. 3, the finger lobes: the two rounded lobes in the lower half.

Widens both finger holes and their lobes, so the whole plate grows around them.

Default Medium · 4 options

Options: Small, Medium, Large, Measure my hand.

Before: Medium. After: Large.

Moves: arms, finger lobes, zip stations.

### `measure_finger_width`

Finger width

![Finger width: before and after, 20 to 26 mm; red marks the arms, the finger lobes, the plate edge and the zip stations.](../../dials/two-sided/measure_finger_width.svg)

Two top views of one plate of the two-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Measure my hand, a 20 mm wide plug in teal. Right: finger width at 26 mm. Marked in red: 1, the zip stations: the three small holes along each arm. 2, the finger lobes, the arms and the plate edge: the two rounded lobes in the lower half; the two toothed arms in the upper half; the outer outline.

Widens both finger holes and their lobes.

Default 20 · Range 14 to 32 · Step size 0.5 · Unit mm

Before: 20. After: 26. Context: `size` = Measure my hand.

Only acts when size is Measure my hand.

Moves: arms, finger lobes, plate edge, zip stations.

## Step 3 - Attachment

### `attachment`

Attachment

![Attachment: before and after, Zip ties + Velcro strap to Zip ties; red marks the arms, the strap slot and the zip stations.](../../dials/two-sided/attachment.svg)

Two top views of one plate of the two-sided puller, before left and after right, the plug end at the top. Left: the defaults with plug length set to 40, a 20 mm wide plug in teal. Right: attachment set to Zip ties. Marked in red: 1, the zip stations: the three small holes along each arm. 2, the strap slot and the arms: the long slot in each arm; the two toothed arms in the upper half.

Removes the strap slot from each arm, while the zip-tie stations stay because they hold the plates together.

Default Zip ties + Velcro strap · 2 options

Options: Zip ties + Velcro strap, Zip ties.

Before: Zip ties + Velcro strap. After: Zip ties. Context: `measure_plug_length` = 40.

Drawn on a 40 mm plug: on the default 25.5 mm plug the arms are too short for a strap slot.

Moves: arms, strap slot, zip stations.

### `strap_width`

Strap width

![Strap width: before and after, 15 to 25 mm; red marks the arms, the strap slot and the zip stations.](../../dials/two-sided/strap_width.svg)

Two top views of one plate of the two-sided puller, before left and after right, the plug end at the top. Left: the defaults with plug length set to 40, a 20 mm wide plug in teal. Right: strap width at 25 mm. Marked in red: 1, the zip stations: the three small holes along each arm. 2, the strap slot and the arms: the long slot in each arm; the two toothed arms in the upper half.

Sets the strap the arm slot must clear, and when the slot's window between the zip-tie stations is shorter than the strap plus 1.5 mm the slot is left out.

Default 15 · Range 10 to 25 · Step size 1 · Unit mm

Before: 15. After: 25. Context: `measure_plug_length` = 40.

Drawn on a 40 mm plug: on the default 25.5 mm plug the arms are too short for a strap slot. At 25 mm the slot leaves too, because the plug is too short for one, so the after picture has no slot and no dimension line.

Moves: arms, strap slot, zip stations.

Can trip: `STRAP WIDER THAN ARM SLOT WINDOW - NARROW THE STRAP`.

## Step 4 - Print Layout

### `print_layout`

Print layout

![Print layout: one view, Both plates to One plate; the layout with both plates, nothing marked.](../../dials/two-sided/print_layout.svg)

One top view of the two-sided puller with both plates side by side, the plug end at the top: what the file prints at Both plates. At One plate it prints one plate. Nothing is marked in red: this dial changes the layout, not the plate.

Puts both identical plates side by side in one file, or just one plate.

Default Both plates · 2 options

Options: Both plates, One plate.

Before: Both plates. After: One plate.

Moves: arms, finger lobes, plate edge, zip stations.
