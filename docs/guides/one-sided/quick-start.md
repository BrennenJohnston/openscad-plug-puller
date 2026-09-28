# Quick start, one-sided puller

The four Customizer steps of the one-sided puller, dial by dial: what each dial moves, in a picture and a sentence, with the numbers the Customizer allows.

Model version 0.12.0. The printable packet is `docs/Plug_Puller_One_Sided_Guide.pdf`; its parts are [the quick start](quick-start.md), [the dial guide](dial-guide.md), [the measuring guide](measuring-guide.md) and [the measuring form](measuring-form.md). The dial names are written exactly as the Customizer shows them.

## Which tool this is

This packet is for the one-sided puller, src/Plug_Puller_Parametric.scad: the tool for a wall plug up to 24 mm thick, a pocket around the plug's back and sides with two finger holes below it, pulled with one hand. Measure your plug's thickness first. Thicker than 24 mm, or a plug you want held from both sides such as a USB-C tip or a round extension-cord plug, is the two-sided puller's job, and that tool has its own packet.

The Customizer's four steps are your plug, your size, the attachment and the hook's side. The quick start below shows each step's dials, the dial guide every dial of the file, the measuring guide how to take each number, and the measuring form is the sheet you fill in first.

If red text appears beside the part in the preview, read it: it names the measurement to fix, and the part will not fit until it is gone.

In every picture: black = the tool; teal = your plug; red dotted = the edges this dial moved; the numbers match the key beside the picture.

![The one-sided puller, the four Customizer steps on a US vacuum plug, five stages left to right.](../../dials/one-sided/storyboard.svg)

Five stages of the one-sided puller, left to right, the top row first, the plug end at the top; red dots mark the edges each step moved. 1, the defaults: the tool as the file opens, with a 25 mm wide plug in teal. 2, Step 1 - Your Plug: plug length, plug width at the prong end, plug width at the cord end, and 4 more; red on the body edge, the finger holes, the seat, the wall notch and the wing openings. 3, Step 2 - Size: hand size, finger width, hand width; red on the body edge, the finger holes, the pocket, the wall notch, the wing openings and the zip-tie holes. 4, Step 3 - Attachment: attachment; the wing openings removed, drawn in red from the old outline. 5, Step 4 - Cord Hook: hook side; red on the hook.

- Step 1: type your plug's numbers
- Step 2: pick your hand size
- Step 3: pick how it attaches
- Step 4: pick the hook's side

## Step 1 - Your Plug

### `plug_preset`

Plug preset

![Plug preset: before and after, Measure my plug to Standard 3-prong plug - NEMA 5-15; red marks 6 parts, named below.](../../dials/one-sided/plug_preset.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults, a 25 mm wide plug in teal. Right: plug preset set to Standard 3-prong plug - NEMA 5-15. Marked in red: 1, the zip-tie holes, the wing openings, the wall notch, the seat, the pocket and the body edge.

Fills in all six plug numbers from a measured reference plug, so the pocket, the wall notch, the cord hook and the zip-tie and wing positions all take that plug's shape at once.

Default Measure my plug · 5 options

Options: Measure my plug, Flat 2-prong lamp plug - NEMA 1-15, Standard 3-prong plug - NEMA 5-15, Heavy-duty extension cord - NEMA 5-15, Wide 2-prong appliance plug - NEMA 1-15.

Before: Measure my plug. After: Standard 3-prong plug - NEMA 5-15.

Moves: body edge, pocket, seat, wall notch, wing openings, zip-tie holes.

### `measure_plug_length`

Plug length

![Plug length: before and after, 25.5 to 40 mm; red marks the body edge, the seat, the wall notch, the wing openings and the zip-tie holes.](../../dials/one-sided/measure_plug_length.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults, a 25 mm wide plug in teal. Right: plug length at 40 mm. Marked in red: 1, the zip-tie holes: the four small holes beside the pocket. 2, the zip-tie holes and the wing openings. 3, the wall notch, the seat and the body edge.

Runs the pocket farther toward the finger holes and stretches the whole body to keep the finger holes and zip-tie rows clear of it.

Default 25.5 · Range 12 to 85 · Step size 0.5 · Unit mm

Before: 25.5. After: 40.

Moves: body edge, seat, wall notch, wing openings, zip-tie holes.

### `measure_plug_width_prong_end`

Plug width at the prong end

![Plug width at the prong end: before and after, 25 to 32 mm; red marks 5 parts, named below.](../../dials/one-sided/measure_plug_width_prong_end.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults, a 25 mm wide plug in teal. Right: plug width at the prong end at 32 mm. Marked in red: 1, the zip-tie holes: the four small holes beside the pocket. 2, the wing openings: the two openings beside the pocket. 3, the wall notch, the seat and the body edge: the notch in the top edge; the round recess at the plug end; the outer outline.

Widens or narrows the pocket, its seat and the wall notch at the plug end, and moves the zip-tie holes and wing openings with them.

Default 25 · Range 8 to 38 · Step size 0.5 · Unit mm

Before: 25. After: 32.

Moves: body edge, seat, wall notch, wing openings, zip-tie holes.

### `measure_plug_width_cord_end`

Plug width at the cord end

![Plug width at the cord end: before and after, 25 to 15 mm; red marks the pocket and the wing openings.](../../dials/one-sided/measure_plug_width_cord_end.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults, a 25 mm wide plug in teal. Right: plug width at the cord end at 15 mm: tilts the pocket's side walls to match the plug's taper, and the zip-tie holes and wing openings lean in with them. Marked in red: 1, the wing openings and the pocket: the two openings beside the pocket; the plug recess on the centerline.

Tilts the pocket's side walls to match the plug's taper, and the zip-tie holes and wing openings lean in with them.

Default 25 · Range 8 to 38 · Step size 0.5 · Unit mm

Before: 25. After: 15.

Moves: pocket, wing openings.

### `measure_plug_thickness_prong_end`

Plug thickness at the prong end

![Plug thickness at the prong end: before and after, 20 to 23.5 mm; red marks the pocket and the seat.](../../dials/one-sided/measure_plug_thickness_prong_end.svg)

Two vertical slices of the one-sided puller at x = 0 mm, before left and after right, the top face up. Left: the defaults, the plug in teal in the cut. Right: plug thickness at the prong end at 23.5 mm: deepens or shallows the two pocket floors, the round seat and the plug recess, to suit the fatter of the two thickness numbers. Marked in red: 1, the seat and the pocket: the round recess at the plug end; the plug recess on the centerline.

Deepens or shallows the two pocket floors, the round seat and the plug recess, to suit the fatter of the two thickness numbers.

Default 20 · Range 4 to 40 · Step size 0.5 · Unit mm

Before: 20. After: 23.5. Section at x = 0 mm.

The fatter of the two thickness numbers sets the floors, so lowering one alone changes nothing; 24 mm or more sends you to the two-sided puller.

Moves: pocket, seat.

### `measure_plug_thickness_cord_end`

Plug thickness at the cord end

![Plug thickness at the cord end: before and after, 20 to 23.5 mm; red marks the pocket and the seat.](../../dials/one-sided/measure_plug_thickness_cord_end.svg)

Two vertical slices of the one-sided puller at x = 0 mm, before left and after right, the top face up. Left: the defaults, the plug in teal in the cut. Right: plug thickness at the cord end at 23.5 mm: deepens or shallows the two pocket floors, the round seat and the plug recess, when this end is the fatter end of the plug. Marked in red: 1, the seat and the pocket: the round recess at the plug end; the plug recess on the centerline.

Deepens or shallows the two pocket floors, the round seat and the plug recess, when this end is the fatter end of the plug.

Default 20 · Range 4 to 40 · Step size 0.5 · Unit mm

Before: 20. After: 23.5. Section at x = 0 mm.

The fatter of the two thickness numbers sets the floors, so lowering one alone changes nothing; 24 mm or more sends you to the two-sided puller.

Moves: pocket, seat.

### `measure_cord_thickness`

Cord thickness

![Cord thickness: before and after, 4 to 8 mm; red marks 6 parts, named below.](../../dials/one-sided/measure_cord_thickness.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults, a 25 mm wide plug in teal. Right: cord thickness at 8 mm. Marked in red: 1, the zip-tie holes, the finger holes, the wing openings, the wall notch, the pocket and the body edge.

Widens the cord hook's slot and crossbar to fit the cord, and moves the finger holes and the whole body up to make room.

Default 4 · Range 1.5 to 9 · Step size 0.5 · Unit mm

Before: 4. After: 8.

Moves: body edge, finger holes, pocket, wall notch, wing openings, zip-tie holes.

### `measure_wall_plate_style`

Outlet cover plate style

![Outlet cover plate style: before and after, Standard flat plate to Oversized / Jumbo; red marks 5 parts, named below.](../../dials/one-sided/measure_wall_plate_style.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults, a 25 mm wide plug in teal. Right: outlet cover plate style set to Oversized / Jumbo. Marked in red: 1, the wall notch and the body edge: the notch in the top edge; the outer outline. 2, the zip-tie holes: the four small holes beside the pocket. 3, the pocket: the plug recess on the centerline. 4, the wing openings: the two openings beside the pocket.

Cuts the wall notch at the plug end deeper or shallower to suit the cover plate, and the zip-tie rows shift down with it.

Default Standard flat plate · 4 options

Options: Standard flat plate, Rocker / Decora, Oversized / Jumbo, No plate / flush.

Before: Standard flat plate. After: Oversized / Jumbo.

Moves: body edge, pocket, wall notch, wing openings, zip-tie holes.

### `show_plug_preview`

Show the see-through plug

![Show the see-through plug: changes no shape.](../../dials/one-sided/show_plug_preview.svg)

This dial changes no shape: the see-through plug is a preview aid and is never exported.

Shows or hides the see-through plug in the preview and changes nothing in the printed tool.

Default true · true / false

## Step 2 - Size

### `size`

Hand size

![Hand size: before and after, Medium to Large; red marks the body edge, the finger holes, the pocket, the wing openings and the zip-tie holes.](../../dials/one-sided/size.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults, a 25 mm wide plug in teal. Right: hand size set to Large. Marked in red: 1, the zip-tie holes: the four small holes beside the pocket. 2, the pocket: the plug recess on the centerline. 3, the wing openings: the two openings beside the pocket. 4, the finger holes: the two large holes in the lower half. 5, the body edge: the outer outline.

Scales the whole body, both finger holes, the wing openings and the zip-tie grid to the chosen hand size.

Default Medium · 5 options

Options: Small, Medium, Large, Measure my hand, Custom.

Before: Medium. After: Large.

Moves: body edge, finger holes, pocket, wing openings, zip-tie holes.

### `measure_finger_width`

Finger width

![Finger width: before and after, 20 to 26 mm; red marks the body edge, the finger holes, the pocket, the wall notch and the wing openings.](../../dials/one-sided/measure_finger_width.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Measure my hand, a 25 mm wide plug in teal. Right: finger width at 26 mm. Marked in red: 1, the pocket: the plug recess on the centerline. 2, the wing openings: the two openings beside the pocket. 3, the finger holes: the two large holes in the lower half. 4, the wall notch and the body edge.

Widens both finger holes, spaces them farther apart and pushes them and the body up to keep the walls printable.

Default 20 · Range 14 to 32 · Step size 0.5 · Unit mm

Before: 20. After: 26. Context: `size` = Measure my hand.

Only acts when size is Measure my hand.

Moves: body edge, finger holes, pocket, wall notch, wing openings.

### `measure_hand_width`

Hand width

![Hand width: before and after, 85 to 100 mm; red marks the body edge.](../../dials/one-sided/measure_hand_width.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Measure my hand, a 25 mm wide plug in teal. Right: hand width at 100 mm: widens the whole body outline and thickens the slab in step with the hand. Marked in red: 1, the body edge: the outer outline. Everything else follows the outline.

Widens the whole body outline and thickens the slab in step with the hand.

Default 85 · Range 60 to 110 · Step size 1 · Unit mm

Before: 85. After: 100. Context: `size` = Measure my hand.

Only acts when size is Measure my hand.

Moves: body edge.

## Step 3 - Attachment

### `attachment`

Attachment

![Attachment: before and after, Zip ties + Velcro to Zip ties; red marks the wing openings.](../../dials/one-sided/attachment.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults, a 25 mm wide plug in teal. Right: attachment set to Zip ties: adds or removes the zip-tie holes and the wing or slot openings for the strap. Marked in red: 1, the wing openings: the two openings beside the pocket, removed. The body edge, the pocket, the seat and the wall notch stay where they were.

Adds or removes the zip-tie holes and the wing or slot openings for the strap.

Default Zip ties + Velcro · 4 options

Options: Zip ties, Velcro strap, Zip ties + Velcro, None.

Before: Zip ties + Velcro. After: Zip ties.

Moves: wing openings.

### `velcro_style`

Strap opening style

![Strap opening style: before and after, Wing to Classic slot; red marks the wing openings.](../../dials/one-sided/velcro_style.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults, a 25 mm wide plug in teal. Right: strap opening style set to Classic slot: swaps the curved wing openings for a pair of plain rectangular slots that lean along the body's sides. Marked in red: 1, the wing openings: the two openings beside the pocket. The body edge, the pocket, the seat and the wall notch stay where they were.

Swaps the curved wing openings for a pair of plain rectangular slots that lean along the body's sides.

Default Wing · 2 options

Options: Wing, Classic slot.

Before: Wing. After: Classic slot.

Moves: wing openings.

Can trip: `WING OPENING SMALLER THAN STRAP WIDTH`.

### `strap_width`

Strap width

![Strap width: changes no shape.](../../dials/one-sided/strap_width.svg)

This dial changes no shape: it only sets the width the W-14 check compares the wing opening against.

Sets the strap width the wing opening is checked against and changes no shape.

Default 15 · Range 10 to 25 · Step size 1 · Unit mm

Can trip: `WING OPENING SMALLER THAN STRAP WIDTH`; `WING WEB COLLAPSED - NO ROOM FOR STRAP`.

## Step 4 - Cord Hook

### `hook_hand`

Hook side

![Hook side: before and after, Right to Left; red marks the hook.](../../dials/one-sided/hook_hand.svg)

Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults, a 25 mm wide plug in teal. Right: hook side set to Left: mirrors the cord hook at the cord end so its catch faces the other side, and nothing else moves. Marked in red: 1, the hook: the cord hook slot in the bottom edge. The body edge, the pocket, the seat and the wall notch stay where they were.

Mirrors the cord hook at the cord end so its catch faces the other side, and nothing else moves.

Default Right · 2 options

Options: Right, Left.

Before: Right. After: Left.

Moves: hook.
