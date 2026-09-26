# Plug Puller Dial Reference

Every dial of the one-sided puller and the two-sided puller on its own page: what it moves, in a picture and a sentence, with the numbers the Customizer allows.

Model version 0.12.0. The printable twin is `docs/Plug_Puller_Dial_Reference.pdf` (one dial per page, with bookmarks and a linked contents page). The dial names are written exactly as the Customizer shows them.

In every picture: black = the tool at its defaults; teal = the plug you measured; red dashed = what this dial moves.

## One-sided puller

### Step 1 - Your Plug

#### `plug_preset`

Plug preset

![Fills in all six plug numbers from a measured reference plug, so the pocket, the wall notch, the cord hook and the zip-tie and wing positions all take that plug's shape at once.](../dials/one-sided/plug_preset.svg)

Fills in all six plug numbers from a measured reference plug, so the pocket, the wall notch, the cord hook and the zip-tie and wing positions all take that plug's shape at once.

| Default | Range | Step | Unit |
|---|---|---|---|
| Measure my plug | 5 options | — | — |

Options: Measure my plug, Flat 2-prong lamp plug - NEMA 1-15, Standard 3-prong plug - NEMA 5-15, Heavy-duty extension cord - NEMA 5-15, Wide 2-prong appliance plug - NEMA 1-15.

Before: Measure my plug. After: Standard 3-prong plug - NEMA 5-15.

Moves: body edge, pocket, seat, wall notch, wing openings, zip-tie holes.

#### `measure_plug_length`

Plug length

![Runs the pocket farther toward the finger holes and stretches the whole body to keep the finger holes and zip-tie rows clear of it.](../dials/one-sided/measure_plug_length.svg)

Runs the pocket farther toward the finger holes and stretches the whole body to keep the finger holes and zip-tie rows clear of it.

| Default | Range | Step | Unit |
|---|---|---|---|
| 25.5 | 12 to 85 | 0.5 | mm |

Before: 25.5. After: 40.

Moves: body edge, seat, wall notch, wing openings, zip-tie holes.

#### `measure_plug_width_prong_end`

Plug width at the prong end

![Widens or narrows the pocket, its seat and the wall notch at the plug end, and moves the zip-tie holes and wing openings with them.](../dials/one-sided/measure_plug_width_prong_end.svg)

Widens or narrows the pocket, its seat and the wall notch at the plug end, and moves the zip-tie holes and wing openings with them.

| Default | Range | Step | Unit |
|---|---|---|---|
| 25 | 8 to 38 | 0.5 | mm |

Before: 25. After: 32.

Moves: seat, wall notch, wing openings, zip-tie holes.

#### `measure_plug_width_cord_end`

Plug width at the cord end

![Tilts the pocket's side walls to match the plug's taper, and the zip-tie holes and wing openings lean in with them.](../dials/one-sided/measure_plug_width_cord_end.svg)

Tilts the pocket's side walls to match the plug's taper, and the zip-tie holes and wing openings lean in with them.

| Default | Range | Step | Unit |
|---|---|---|---|
| 25 | 8 to 38 | 0.5 | mm |

Before: 25. After: 15.

Moves: pocket, wing openings.

#### `measure_plug_thickness_prong_end`

Plug thickness at the prong end

![Deepens or shallows the two pocket floors, the round seat and the plug recess, to suit the fatter of the two thickness numbers.](../dials/one-sided/measure_plug_thickness_prong_end.svg)

Deepens or shallows the two pocket floors, the round seat and the plug recess, to suit the fatter of the two thickness numbers.

| Default | Range | Step | Unit |
|---|---|---|---|
| 20 | 4 to 40 | 0.5 | mm |

Before: 20. After: 23.5. Section at x = 0 mm.

The fatter of the two thickness numbers sets the floors, so lowering one alone changes nothing; 24 mm or more sends you to the two-sided puller.

Moves: pocket, seat.

#### `measure_plug_thickness_cord_end`

Plug thickness at the cord end

![Deepens or shallows the two pocket floors, the round seat and the plug recess, when this end is the fatter end of the plug.](../dials/one-sided/measure_plug_thickness_cord_end.svg)

Deepens or shallows the two pocket floors, the round seat and the plug recess, when this end is the fatter end of the plug.

| Default | Range | Step | Unit |
|---|---|---|---|
| 20 | 4 to 40 | 0.5 | mm |

Before: 20. After: 23.5. Section at x = 0 mm.

The fatter of the two thickness numbers sets the floors, so lowering one alone changes nothing; 24 mm or more sends you to the two-sided puller.

Moves: pocket, seat.

#### `measure_cord_thickness`

Cord thickness

![Widens the cord hook's slot and crossbar to fit the cord, and moves the finger holes and the whole body up to make room.](../dials/one-sided/measure_cord_thickness.svg)

Widens the cord hook's slot and crossbar to fit the cord, and moves the finger holes and the whole body up to make room.

| Default | Range | Step | Unit |
|---|---|---|---|
| 4 | 1.5 to 9 | 0.5 | mm |

Before: 4. After: 8.

Moves: body edge, finger holes, pocket, wall notch, wing openings, zip-tie holes.

#### `measure_wall_plate_style`

Outlet cover plate style

![Cuts the wall notch at the plug end deeper or shallower to suit the cover plate, and the zip-tie rows shift down with it.](../dials/one-sided/measure_wall_plate_style.svg)

Cuts the wall notch at the plug end deeper or shallower to suit the cover plate, and the zip-tie rows shift down with it.

| Default | Range | Step | Unit |
|---|---|---|---|
| Standard flat plate | 4 options | — | — |

Options: Standard flat plate, Rocker / Decora, Oversized / Jumbo, No plate / flush.

Before: Standard flat plate. After: Oversized / Jumbo.

Moves: body edge, pocket, wall notch, wing openings, zip-tie holes.

#### `show_plug_preview`

Show the see-through plug

![Shows or hides the see-through plug in the preview and changes nothing in the printed tool.](../dials/one-sided/show_plug_preview.svg)

Shows or hides the see-through plug in the preview and changes nothing in the printed tool.

| Default | Range | Step | Unit |
|---|---|---|---|
| true | true / false | — | — |

This dial changes no shape. Changes no shape: the see-through plug is a preview aid and is never exported.

### Step 2 - Size

#### `size`

Hand size

![Scales the whole body, both finger holes, the wing openings and the zip-tie grid to the chosen hand size.](../dials/one-sided/size.svg)

Scales the whole body, both finger holes, the wing openings and the zip-tie grid to the chosen hand size.

| Default | Range | Step | Unit |
|---|---|---|---|
| Medium | 5 options | — | — |

Options: Small, Medium, Large, Measure my hand, Custom.

Before: Medium. After: Large.

Moves: body edge, finger holes, pocket, wing openings, zip-tie holes.

#### `measure_finger_width`

Finger width

![Widens both finger holes, spaces them farther apart and pushes them and the body up to keep the walls printable.](../dials/one-sided/measure_finger_width.svg)

Widens both finger holes, spaces them farther apart and pushes them and the body up to keep the walls printable.

| Default | Range | Step | Unit |
|---|---|---|---|
| 20 | 14 to 32 | 0.5 | mm |

Before: 20. After: 26. Context: `size` = Measure my hand.

Only acts when size is Measure my hand.

Moves: finger holes, pocket, wall notch, wing openings.

#### `measure_hand_width`

Hand width

![Widens the whole body outline and thickens the slab in step with the hand.](../dials/one-sided/measure_hand_width.svg)

Widens the whole body outline and thickens the slab in step with the hand.

| Default | Range | Step | Unit |
|---|---|---|---|
| 85 | 60 to 110 | 1 | mm |

Before: 85. After: 100. Context: `size` = Measure my hand.

Only acts when size is Measure my hand.

Moves: wing openings.

### Step 3 - Attachment

#### `attachment`

Attachment

![Adds or removes the zip-tie holes and the wing or slot openings for the strap.](../dials/one-sided/attachment.svg)

Adds or removes the zip-tie holes and the wing or slot openings for the strap.

| Default | Range | Step | Unit |
|---|---|---|---|
| Zip ties + Velcro | 4 options | — | — |

Options: Zip ties, Velcro strap, Zip ties + Velcro, None.

Before: Zip ties + Velcro. After: Zip ties.

Moves: wing openings.

#### `velcro_style`

Strap opening style

![Swaps the curved wing openings for a pair of plain rectangular slots that lean along the body's sides.](../dials/one-sided/velcro_style.svg)

Swaps the curved wing openings for a pair of plain rectangular slots that lean along the body's sides.

| Default | Range | Step | Unit |
|---|---|---|---|
| Wing | 2 options | — | — |

Options: Wing, Classic slot.

Before: Wing. After: Classic slot.

Moves: wing openings.

Can trip: `WING OPENING SMALLER THAN STRAP WIDTH`.

#### `strap_width`

Strap width

![Sets the strap width the wing opening is checked against and changes no shape.](../dials/one-sided/strap_width.svg)

Sets the strap width the wing opening is checked against and changes no shape.

| Default | Range | Step | Unit |
|---|---|---|---|
| 15 | 10 to 25 | 1 | mm |

This dial changes no shape. Changes no shape: it only sets the width the W-14 check compares the wing opening against.

Can trip: `WING OPENING SMALLER THAN STRAP WIDTH`; `WING WEB COLLAPSED - NO ROOM FOR STRAP`.

### Step 4 - Cord Hook

#### `hook_hand`

Hook side

![Mirrors the cord hook at the cord end so its catch faces the other side, and nothing else moves.](../dials/one-sided/hook_hand.svg)

Mirrors the cord hook at the cord end so its catch faces the other side, and nothing else moves.

| Default | Range | Step | Unit |
|---|---|---|---|
| Right | 2 options | — | — |

Options: Right, Left.

Before: Right. After: Left.

Moves: hook.

### Advanced - Zip Tie Placement

#### `zip_placement`

Zip-tie hole placement

![Switches the zip-tie pairs from the automatic rows to the three position dials, which slide each pair along the plug's side.](../dials/one-sided/zip_placement.svg)

Switches the zip-tie pairs from the automatic rows to the three position dials, which slide each pair along the plug's side.

| Default | Range | Step | Unit |
|---|---|---|---|
| Auto | 2 options | — | — |

Options: Auto, Manual.

Before: Auto. After: Manual.

Moves: seat, wall notch, wing openings, zip-tie holes.

#### `zip_row_count`

Number of zip-tie rows

![Adds or removes a pair of zip-tie holes, and the rows squeeze together when the body has no room for another.](../dials/one-sided/zip_row_count.svg)

Adds or removes a pair of zip-tie holes, and the rows squeeze together when the body has no room for another.

| Default | Range | Step | Unit |
|---|---|---|---|
| 2 | 1 to 3 | 1 | — |

Before: 2. After: 3.

Moves: wing openings, zip-tie holes.

#### `zip_pos_1`

Zip-tie pair 1 position

![Slides the first pair of zip-tie holes along the plug's side, measured from the plug end.](../dials/one-sided/zip_pos_1.svg)

Slides the first pair of zip-tie holes along the plug's side, measured from the plug end.

| Default | Range | Step | Unit |
|---|---|---|---|
| 6 | 0 to 55 | 0.5 | mm |

Before: 6. After: 10. Context: `zip_placement` = Manual.

Only acts when zip_placement is Manual.

Moves: seat, wall notch, zip-tie holes.

Can trip: `ZIP TIE HOLES HIT FINGER HOLES`; `ZIP TIE ROWS OVERLAP EACH OTHER`; `ZIP TIE HOLES HIT VELCRO SLOTS`.

#### `zip_pos_2`

Zip-tie pair 2 position

![Slides the second pair of zip-tie holes along the plug's side, measured from the plug end.](../dials/one-sided/zip_pos_2.svg)

Slides the second pair of zip-tie holes along the plug's side, measured from the plug end.

| Default | Range | Step | Unit |
|---|---|---|---|
| 18 | 0 to 55 | 0.5 | mm |

Before: 18. After: 26. Context: `zip_placement` = Manual.

Only acts when zip_placement is Manual.

Moves: wing openings, zip-tie holes.

Can trip: `ZIP TIE HOLES HIT FINGER HOLES`; `ZIP TIE ROWS OVERLAP EACH OTHER`; `ZIP TIE HOLES HIT VELCRO SLOTS`.

#### `zip_pos_3`

Zip-tie pair 3 position

![Slides the third pair of zip-tie holes along the plug's side, measured from the plug end.](../dials/one-sided/zip_pos_3.svg)

Slides the third pair of zip-tie holes along the plug's side, measured from the plug end.

| Default | Range | Step | Unit |
|---|---|---|---|
| 30 | 0 to 55 | 0.5 | mm |

Before: 30. After: 26. Context: `zip_placement` = Manual, `zip_row_count` = 3.

Only acts when zip_placement is Manual and zip_row_count is 3.

Moves: wing openings, zip-tie holes.

Can trip: `ZIP TIE HOLES HIT FINGER HOLES`; `ZIP TIE ROWS OVERLAP EACH OTHER`; `ZIP TIE HOLES HIT VELCRO SLOTS`.

#### `zip_edge_offset`

Zip-tie hole distance from the pocket wall

![Moves every zip-tie hole farther from or closer to the pocket wall, and the wing openings reshape around them.](../dials/one-sided/zip_edge_offset.svg)

Moves every zip-tie hole farther from or closer to the pocket wall, and the wing openings reshape around them.

| Default | Range | Step | Unit |
|---|---|---|---|
| 4 | 2.5 to 12 | 0.25 | mm |

Before: 4. After: 8.

Moves: wing openings, zip-tie holes.

### Advanced - Velcro Placement

#### `velcro_placement`

Strap slot placement

![Switches the strap openings to a pair of plain slots that the position dial slides along the plug's side, whatever the opening style.](../dials/one-sided/velcro_placement.svg)

Switches the strap openings to a pair of plain slots that the position dial slides along the plug's side, whatever the opening style.

| Default | Range | Step | Unit |
|---|---|---|---|
| Auto | 2 options | — | — |

Options: Auto, Manual.

Before: Auto. After: Manual.

Moves: wing openings.

#### `velcro_pos`

Strap slot position

![Slides the pair of strap slots along the plug's side, measured from the plug end.](../dials/one-sided/velcro_pos.svg)

Slides the pair of strap slots along the plug's side, measured from the plug end.

| Default | Range | Step | Unit |
|---|---|---|---|
| 12 | 0 to 55 | 0.5 | mm |

Before: 12. After: 25. Context: `velcro_style` = Classic slot, `velcro_placement` = Manual.

Only acts when velcro_placement is Manual.

Moves: classic slots.

Can trip: `ZIP TIE HOLES HIT VELCRO SLOTS`.

### Advanced - Render Quality

#### `quality`

Render quality

![Sets how many flat segments draw each curve and changes no dimension.](../dials/one-sided/quality.svg)

Sets how many flat segments draw each curve and changes no dimension.

| Default | Range | Step | Unit |
|---|---|---|---|
| 64 | 24 to 128 | 8 | segments |

This dial changes no shape. Changes no shape: it only sets the number of segments in every circle and arc.

### Custom Mode

#### `reset_custom_to_medium`

Reset Custom to the Medium reference

![Swaps every Custom slider for the Medium reference values for one render, so the whole tool snaps back to the Medium shape.](../dials/one-sided/reset_custom_to_medium.svg)

Swaps every Custom slider for the Medium reference values for one render, so the whole tool snaps back to the Medium shape.

| Default | Range | Step | Unit |
|---|---|---|---|
| false | true / false | — | — |

Before: false. After: true. Context: `size` = Custom.

Only acts when size is Custom.

Moves: finger holes, wall notch, wing openings, zip-tie holes.

#### `custom_enable_auto_fit`

Auto-fit

![Lets the tool clamp any Custom slider that would push a feature past the body or into a neighbor, and changes nothing while every slider is inside its safe range.](../dials/one-sided/custom_enable_auto_fit.svg)

Lets the tool clamp any Custom slider that would push a feature past the body or into a neighbor, and changes nothing while every slider is inside its safe range.

| Default | Range | Step | Unit |
|---|---|---|---|
| true | true / false | — | — |

This dial changes no shape. Changes no shape at the Custom defaults: it only clamps sliders that leave their safe range, and every clamp is reported in the console.

Can trip: `ZIP TIE HOLES HIT FINGER HOLES`; `FINGER HOLES OUTSIDE BODY`; `POCKET SEAT WIDER THAN TOP EDGE`; `POCKET WIDER THAN BODY`; `WALL NOTCH WIDER THAN TOP EDGE`.

### Body Shape (Custom size only)

#### `custom_puller_length`

Body length

![Stretches the whole body from the cord end to the plug end.](../dials/one-sided/custom_puller_length.svg)

Stretches the whole body from the cord end to the plug end.

| Default | Range | Step | Unit |
|---|---|---|---|
| 63.5 | 50 to 120 | 0.5 | mm |

Before: 63.5. After: 73.5. Context: `size` = Custom.

Only acts when size is Custom.

Moves: body edge, pocket, seat, wall notch, zip-tie holes.

#### `custom_puller_bottom_width`

Body width at the widest point

![Widens the body at its widest point, just above the cord end, before the side rounding is applied.](../dials/one-sided/custom_puller_bottom_width.svg)

Widens the body at its widest point, just above the cord end, before the side rounding is applied.

| Default | Range | Step | Unit |
|---|---|---|---|
| 77.6 | 50 to 120 | 0.05 | mm |

Before: 77.6. After: 87.6. Context: `size` = Custom.

Only acts when size is Custom.

Moves: body edge.

#### `custom_puller_bottom_corners`

Cord-end corner width

![Widens the flat at the cord end where the two lower corners of the body outline sit.](../dials/one-sided/custom_puller_bottom_corners.svg)

Widens the flat at the cord end where the two lower corners of the body outline sit.

| Default | Range | Step | Unit |
|---|---|---|---|
| 3 | 3 to 80 | 0.25 | mm |

Before: 3. After: 13. Context: `size` = Custom.

Only acts when size is Custom.

Moves: body edge.

#### `custom_puller_top_width`

Body width at the plug end

![Widens the plug end of the body, where the wall notch and the pocket seat sit.](../dials/one-sided/custom_puller_top_width.svg)

Widens the plug end of the body, where the wall notch and the pocket seat sit.

| Default | Range | Step | Unit |
|---|---|---|---|
| 31.75 | 25 to 80 | 0.25 | mm |

Before: 31.75. After: 41.75. Context: `size` = Custom.

Only acts when size is Custom.

Moves: body edge, wing openings.

#### `custom_puller_middle_width`

Body width at the middle

![Widens the body at the middle control point, bulging or straightening the side edges between the widest point and the plug end.](../dials/one-sided/custom_puller_middle_width.svg)

Widens the body at the middle control point, bulging or straightening the side edges between the widest point and the plug end.

| Default | Range | Step | Unit |
|---|---|---|---|
| 57.35 | 25 to 120 | 0.05 | mm |

Before: 57.35. After: 67.35. Context: `size` = Custom.

Only acts when size is Custom.

Moves: body edge, wing openings.

#### `custom_puller_side_corner`

Side corner position

![Moves the two widest corners of the body outline up toward the plug end or down toward the cord end.](../dials/one-sided/custom_puller_side_corner.svg)

Moves the two widest corners of the body outline up toward the plug end or down toward the cord end.

| Default | Range | Step | Unit |
|---|---|---|---|
| 4.65 | 3 to 35 | 0.05 | mm |

Before: 4.65. After: 14.65. Context: `size` = Custom.

Only acts when size is Custom.

Moves: body edge, wing openings.

#### `custom_body_thickness`

Body thickness

![Thickens the whole slab, so every hole and the pocket get deeper walls.](../dials/one-sided/custom_body_thickness.svg)

Thickens the whole slab, so every hole and the pocket get deeper walls.

| Default | Range | Step | Unit |
|---|---|---|---|
| 6.35 | 4 to 15 | 0.05 | mm |

Before: 6.35. After: 9. Context: `size` = Custom. Section at y = 35 mm.

Only acts when size is Custom.

Moves: body edge.

#### `custom_body_round_bottom_only`

Round the cord half only

![Rounds the whole outline instead of only the cord half, so the plug end loses its crisp corners.](../dials/one-sided/custom_body_round_bottom_only.svg)

Rounds the whole outline instead of only the cord half, so the plug end loses its crisp corners.

| Default | Range | Step | Unit |
|---|---|---|---|
| true | true / false | — | — |

Before: true. After: false. Context: `size` = Custom.

Only acts when size is Custom.

Moves: body edge, hook, seat, wall notch.

### Plug Pocket (Custom size only)

#### `custom_pocket_seat_diameter`

Pocket seat diameter

![Widens the round seat cut into the plug end of the pocket.](../dials/one-sided/custom_pocket_seat_diameter.svg)

Widens the round seat cut into the plug end of the pocket.

| Default | Range | Step | Unit |
|---|---|---|---|
| 31.75 | 10 to 45 | 0.05 | mm |

Before: 31.75. After: 28. Context: `size` = Custom.

Only acts when size is Custom.

Moves: seat.

#### `custom_pocket_width`

Pocket width

![Widens the plug recess, and the zip-tie holes and wing openings move outward with its wall.](../dials/one-sided/custom_pocket_width.svg)

Widens the plug recess, and the zip-tie holes and wing openings move outward with its wall.

| Default | Range | Step | Unit |
|---|---|---|---|
| 28.85 | 10 to 45 | 0.05 | mm |

Before: 28.85. After: 34. Context: `size` = Custom.

Only acts when size is Custom.

Moves: pocket, seat, wing openings, zip-tie holes.

#### `custom_pocket_depth`

Pocket depth

![Runs the plug recess farther from the plug end toward the finger holes.](../dials/one-sided/custom_pocket_depth.svg)

Runs the plug recess farther from the plug end toward the finger holes.

| Default | Range | Step | Unit |
|---|---|---|---|
| 24.5 | 5 to 60 | 0.5 | mm |

Before: 24.5. After: 34. Context: `size` = Custom.

Only acts when size is Custom.

Moves: pocket, wing openings.

#### `custom_pocket_dome_drop`

Pocket reference drop

![Changes no shape of the pocket, because the recess outline is built from the plug width at the plug end and the side taper, and this reference point cancels out of it.](../dials/one-sided/custom_pocket_dome_drop.svg)

Changes no shape of the pocket, because the recess outline is built from the plug width at the plug end and the side taper, and this reference point cancels out of it.

| Default | Range | Step | Unit |
|---|---|---|---|
| 2.15 | 0 to 8 | 0.05 | mm |

This dial changes no shape. Changes no shape: the recess is a rounded-nose shape whose width at the plug end is the pocket width and whose walls follow the side taper, so this reference point cancels out; measured with straight and with tapered walls.

#### `custom_pocket_seat_floor`

Pocket seat floor thickness

![Thins or thickens the floor left under the round seat, so the seat is cut deeper or shallower.](../dials/one-sided/custom_pocket_seat_floor.svg)

Thins or thickens the floor left under the round seat, so the seat is cut deeper or shallower.

| Default | Range | Step | Unit |
|---|---|---|---|
| 3.175 | 0 to 8 | 0.025 | mm |

Before: 3.175. After: 1.5. Context: `size` = Custom. Section at x = 0 mm.

Only acts when size is Custom.

Moves: seat.

#### `custom_pocket_floor`

Plug recess floor thickness

![Thins or thickens the floor left under the plug recess, so the recess is cut deeper or shallower.](../dials/one-sided/custom_pocket_floor.svg)

Thins or thickens the floor left under the plug recess, so the recess is cut deeper or shallower.

| Default | Range | Step | Unit |
|---|---|---|---|
| 3.81 | 0 to 12 | 0.025 | mm |

Before: 3.81. After: 2. Context: `size` = Custom. Section at x = 0 mm.

Only acts when size is Custom.

Moves: pocket, seat.

#### `custom_pocket_side_angle`

Pocket side taper

![Tilts the pocket's side walls inward toward the cord end, and the zip-tie holes and strap slots lean in along the same line.](../dials/one-sided/custom_pocket_side_angle.svg)

Tilts the pocket's side walls inward toward the cord end, and the zip-tie holes and strap slots lean in along the same line.

| Default | Range | Step | Unit |
|---|---|---|---|
| 0 | -15 to 25 | 0.5 | mm |

Before: 0. After: 10. Context: `size` = Custom.

Only acts when size is Custom.

Moves: pocket, wing openings.

### Finger Holes (Custom size only)

#### `custom_enable_finger_holes`

Finger holes on or off

![Cuts or leaves out both finger holes.](../dials/one-sided/custom_enable_finger_holes.svg)

Cuts or leaves out both finger holes.

| Default | Range | Step | Unit |
|---|---|---|---|
| true | true / false | — | — |

Before: true. After: false. Context: `size` = Custom.

Only acts when size is Custom.

Moves: body edge, finger holes.

#### `custom_finger_hole_diameter`

Finger hole diameter

![Widens both finger holes.](../dials/one-sided/custom_finger_hole_diameter.svg)

Widens both finger holes.

| Default | Range | Step | Unit |
|---|---|---|---|
| 25.4 | 15 to 40 | 0.1 | mm |

Before: 25.4. After: 22. Context: `size` = Custom.

Only acts when size is Custom.

Moves: finger holes, wing openings.

#### `custom_finger_hole_spacing`

Finger hole spacing

![Moves the two finger holes farther apart or closer together.](../dials/one-sided/custom_finger_hole_spacing.svg)

Moves the two finger holes farther apart or closer together.

| Default | Range | Step | Unit |
|---|---|---|---|
| 33 | 20 to 50 | 0.5 | mm |

Before: 33. After: 40. Context: `size` = Custom.

Only acts when size is Custom.

Moves: finger holes, wing openings.

#### `custom_finger_hole_y_position`

Finger hole position

![Slides both finger holes up toward the pocket or down toward the cord hook.](../dials/one-sided/custom_finger_hole_y_position.svg)

Slides both finger holes up toward the pocket or down toward the cord hook.

| Default | Range | Step | Unit |
|---|---|---|---|
| 19.8 | 10 to 50 | 0.1 | mm |

Before: 19.8. After: 26. Context: `size` = Custom.

Only acts when size is Custom.

Moves: finger holes, pocket.

### T Hook (Custom size only)

#### `custom_enable_t_hook`

Cord hook on or off

![Cuts or leaves out the cord hook at the cord end.](../dials/one-sided/custom_enable_t_hook.svg)

Cuts or leaves out the cord hook at the cord end.

| Default | Range | Step | Unit |
|---|---|---|---|
| true | true / false | — | — |

Before: true. After: false. Context: `size` = Custom.

Only acts when size is Custom.

Moves: hook.

#### `custom_t_hook_base_gap`

Hook slot width

![Widens the slot the cord slides into at the cord end.](../dials/one-sided/custom_t_hook_base_gap.svg)

Widens the slot the cord slides into at the cord end.

| Default | Range | Step | Unit |
|---|---|---|---|
| 4.7625 | 3 to 10 | 0.05 | mm |

Before: 4.7625. After: 7. Context: `size` = Custom.

Only acts when size is Custom.

Moves: hook.

#### `custom_t_hook_length`

Hook length

![Runs the cord hook farther into the body from the cord end.](../dials/one-sided/custom_t_hook_length.svg)

Runs the cord hook farther into the body from the cord end.

| Default | Range | Step | Unit |
|---|---|---|---|
| 10.16 | 6 to 20 | 0.05 | mm |

Before: 10.16. After: 15. Context: `size` = Custom.

Only acts when size is Custom.

Moves: finger holes, hook, pocket, wing openings, zip-tie holes.

#### `custom_t_hook_holder_width`

Hook crossbar width

![Widens the crossbar the cord hooks under at the top of the slot.](../dials/one-sided/custom_t_hook_holder_width.svg)

Widens the crossbar the cord hooks under at the top of the slot.

| Default | Range | Step | Unit |
|---|---|---|---|
| 11.1125 | 8 to 25 | 0.05 | mm |

Before: 11.1125. After: 16. Context: `size` = Custom.

Only acts when size is Custom.

Moves: finger holes, hook, wing openings, zip-tie holes.

#### `custom_t_hook_holder_length`

Hook crossbar height

![Makes the crossbar opening taller or shorter along the body.](../dials/one-sided/custom_t_hook_holder_length.svg)

Makes the crossbar opening taller or shorter along the body.

| Default | Range | Step | Unit |
|---|---|---|---|
| 5.08 | 2 to 15 | 0.05 | mm |

Before: 5.08. After: 8. Context: `size` = Custom.

Only acts when size is Custom.

Moves: hook.

#### `custom_t_hook_gap_offset`

Hook slot inset

![Changes no shape of the printed tool, because the J-hook cord catch does not read this dial.](../dials/one-sided/custom_t_hook_gap_offset.svg)

Changes no shape of the printed tool, because the J-hook cord catch does not read this dial.

| Default | Range | Step | Unit |
|---|---|---|---|
| 0 | 0 to 8 | 0.5 | mm |

This dial changes no shape. Changes no shape: the J-hook cord catch is drawn without this dial; it only appears in the Cutouts Only 2D debug overlay.

#### `custom_t_hook_leg_offset`

Hook stem side offset

![Moves nothing on the hook itself, and only pushes the finger holes up when the auto-fit keep-out around the hook grows with it.](../dials/one-sided/custom_t_hook_leg_offset.svg)

Moves nothing on the hook itself, and only pushes the finger holes up when the auto-fit keep-out around the hook grows with it.

| Default | Range | Step | Unit |
|---|---|---|---|
| 0 | -5 to 5 | 0.5 | mm |

Before: 0. After: 3. Context: `size` = Custom.

Only acts when size is Custom; the J-hook cord catch is drawn without this dial, and only the auto-fit clamp on the finger holes reads it.

Moves: finger holes, wing openings, zip-tie holes.

#### `custom_t_hook_stem_offset`

Hook stem offset

![Shifts the cord slot sideways along the crossbar, making the J of the hook deeper or shallower.](../dials/one-sided/custom_t_hook_stem_offset.svg)

Shifts the cord slot sideways along the crossbar, making the J of the hook deeper or shallower.

| Default | Range | Step | Unit |
|---|---|---|---|
| 4.5 | 0 to 8 | 0.05 | mm |

Before: 4.5. After: 7. Context: `size` = Custom.

Only acts when size is Custom.

Moves: hook.

#### `custom_t_hook_catch_reach`

Hook catch reach

![Extends the crossbar past the slot on the catch side, lengthening the lip the cord hooks under.](../dials/one-sided/custom_t_hook_catch_reach.svg)

Extends the crossbar past the slot on the catch side, lengthening the lip the cord hooks under.

| Default | Range | Step | Unit |
|---|---|---|---|
| 4.55 | 0 to 10 | 0.05 | mm |

Before: 4.55. After: 8. Context: `size` = Custom.

Only acts when size is Custom.

Moves: hook.

#### `custom_t_hook_tip_drop`

Hook tip drop

![Sags the slot's mouth farther below the cord end so a hooked cord cannot back out.](../dials/one-sided/custom_t_hook_tip_drop.svg)

Sags the slot's mouth farther below the cord end so a hooked cord cannot back out.

| Default | Range | Step | Unit |
|---|---|---|---|
| 1.98 | 0 to 5 | 0.05 | mm |

This dial changes no shape. Only acts when size is Custom. Changes no shape: the hook slot's mouth already opens through the cord end (the body ends at Y = 0), so sagging the mouth farther below that edge cuts only air; measured at 1.98, 4 and 0.

### Plug Wall Notch (Custom size only)

#### `custom_enable_plug_wall_notch`

Wall notch on or off

![Cuts or leaves out the notch at the plug end that straddles the outlet's cover plate.](../dials/one-sided/custom_enable_plug_wall_notch.svg)

Cuts or leaves out the notch at the plug end that straddles the outlet's cover plate.

| Default | Range | Step | Unit |
|---|---|---|---|
| true | true / false | — | — |

Before: true. After: false. Context: `size` = Custom.

Only acts when size is Custom.

Moves: wall notch.

#### `custom_plug_wall_notch_width`

Wall notch width

![Widens or narrows the notch at the plug end.](../dials/one-sided/custom_plug_wall_notch_width.svg)

Widens or narrows the notch at the plug end.

| Default | Range | Step | Unit |
|---|---|---|---|
| 26.67 | 5 to 40 | 0.01 | mm |

Before: 26.67. After: 20. Context: `size` = Custom.

Only acts when size is Custom.

Moves: wall notch.

#### `custom_plug_wall_notch_height`

Wall notch depth

![Cuts the notch deeper or shallower into the plug end.](../dials/one-sided/custom_plug_wall_notch_height.svg)

Cuts the notch deeper or shallower into the plug end.

| Default | Range | Step | Unit |
|---|---|---|---|
| 3.81 | 0 to 10 | 0.05 | mm |

Before: 3.81. After: 7. Context: `size` = Custom.

Only acts when size is Custom.

Moves: wall notch, wing openings, zip-tie holes.

#### `custom_plug_wall_notch_rounding`

Wall notch corner rounding

![Rounds or squares the notch's two inner corners.](../dials/one-sided/custom_plug_wall_notch_rounding.svg)

Rounds or squares the notch's two inner corners.

| Default | Range | Step | Unit |
|---|---|---|---|
| 2.54 | 0 to 5 | 0.01 | mm |

Before: 2.54. After: 0. Context: `size` = Custom.

Only acts when size is Custom.

Moves: wall notch.

### Zip Tie Holes (Custom size only)

#### `custom_zip_tie_hole_diameter`

Zip-tie hole diameter

![Widens every zip-tie hole.](../dials/one-sided/custom_zip_tie_hole_diameter.svg)

Widens every zip-tie hole.

| Default | Range | Step | Unit |
|---|---|---|---|
| 5.08 | 2 to 8 | 0.02 | mm |

Before: 5.08. After: 7. Context: `size` = Custom.

Only acts when size is Custom.

Moves: wing openings, zip-tie holes.

#### `custom_zip_tie_height_spacing`

Zip-tie row spacing

![Moves the second row of zip-tie holes closer to or farther from the first.](../dials/one-sided/custom_zip_tie_height_spacing.svg)

Moves the second row of zip-tie holes closer to or farther from the first.

| Default | Range | Step | Unit |
|---|---|---|---|
| 17.78 | 5 to 30 | 0.02 | mm |

Before: 17.78. After: 12. Context: `size` = Custom.

Only acts when size is Custom.

Moves: wing openings, zip-tie holes.

#### `custom_zip_tie_width_spacing`

Zip-tie column spacing

![Moves no zip-tie hole, because the two columns follow the pocket wall, and only feeds the auto-fit keep-out that can trim the row spacing by a hair.](../dials/one-sided/custom_zip_tie_width_spacing.svg)

Moves no zip-tie hole, because the two columns follow the pocket wall, and only feeds the auto-fit keep-out that can trim the row spacing by a hair.

| Default | Range | Step | Unit |
|---|---|---|---|
| 17.7 | 10 to 50 | 0.02 | mm |

This dial changes no shape. Changes no shape of its own: the zip-tie columns sit zip_edge_offset inside the pocket wall; this dial only feeds the auto-fit finger keep-out, which trimmed the row spacing by 0.05 mm at the Custom defaults.

#### `custom_zip_tie_distance_from_notch`

Zip-tie distance from the notch

![Moves the first row of zip-tie holes farther from the wall notch, and the second row follows.](../dials/one-sided/custom_zip_tie_distance_from_notch.svg)

Moves the first row of zip-tie holes farther from the wall notch, and the second row follows.

| Default | Range | Step | Unit |
|---|---|---|---|
| 5.1 | 1 to 15 | 0.05 | mm |

Before: 5.1. After: 9. Context: `size` = Custom.

Only acts when size is Custom.

Moves: wing openings, zip-tie holes.

#### `custom_zip_tie_countersink`

Zip-tie countersink

![Flares the top of the zip-tie holes wider so the tie head sits flush.](../dials/one-sided/custom_zip_tie_countersink.svg)

Flares the top of the zip-tie holes wider so the tie head sits flush.

| Default | Range | Step | Unit |
|---|---|---|---|
| 0.9 | 0 to 3 | 0.05 | mm |

Before: 0.9. After: 2.5. Context: `size` = Custom. Section at x = 10.4 mm.

Only acts when size is Custom.

Moves: pocket, zip-tie holes.

### Velcro / Wing Strap Holes (Custom size only)

#### `custom_velcro_hole_length`

Strap slot length

![Lengthens each plain strap slot along its lean.](../dials/one-sided/custom_velcro_hole_length.svg)

Lengthens each plain strap slot along its lean.

| Default | Range | Step | Unit |
|---|---|---|---|
| 12 | 6 to 20 | 0.5 | mm |

Before: 12. After: 18. Context: `size` = Custom, `velcro_style` = Classic slot.

Only acts when size is Custom and velcro_style is Classic slot.

Moves: classic slots.

#### `custom_velcro_hole_width`

Strap slot width

![Widens each plain strap slot.](../dials/one-sided/custom_velcro_hole_width.svg)

Widens each plain strap slot.

| Default | Range | Step | Unit |
|---|---|---|---|
| 7 | 3 to 14 | 0.5 | mm |

Before: 7. After: 11. Context: `size` = Custom, `velcro_style` = Classic slot.

Only acts when size is Custom and velcro_style is Classic slot.

Moves: classic slots.

#### `custom_velcro_hole_x_center`

Strap slot distance from the centerline

![Moves the two plain strap slots closer to or farther from the centerline.](../dials/one-sided/custom_velcro_hole_x_center.svg)

Moves the two plain strap slots closer to or farther from the centerline.

| Default | Range | Step | Unit |
|---|---|---|---|
| 19.4 | 5 to 35 | 0.05 | mm |

Before: 19.4. After: 14. Context: `size` = Custom, `velcro_style` = Classic slot.

Only acts when size is Custom and velcro_style is Classic slot.

Moves: classic slots.

#### `custom_velcro_hole_y_center`

Strap slot position along the body

![Slides the two plain strap slots toward the cord end or the plug end.](../dials/one-sided/custom_velcro_hole_y_center.svg)

Slides the two plain strap slots toward the cord end or the plug end.

| Default | Range | Step | Unit |
|---|---|---|---|
| 46 | 30 to 80 | 0.5 | mm |

Before: 46. After: 38. Context: `size` = Custom, `velcro_style` = Classic slot.

Only acts when size is Custom and velcro_style is Classic slot.

Moves: classic slots.

#### `custom_velcro_hole_rotation`

Strap slot lean

![Leans the two plain strap slots more or less steeply, mirrored on the two sides.](../dials/one-sided/custom_velcro_hole_rotation.svg)

Leans the two plain strap slots more or less steeply, mirrored on the two sides.

| Default | Range | Step | Unit |
|---|---|---|---|
| 23.5 | 0 to 180 | 0.5 | deg |

Before: 23.5. After: 60. Context: `size` = Custom, `velcro_style` = Classic slot.

Only acts when size is Custom and velcro_style is Classic slot.

Moves: classic slots.

### Edge Rounding (Custom size only)

#### `custom_body_side_rounding`

Body side rounding

![Rounds the body outline's corners more or less, down to the plain octagon at 0.](../dials/one-sided/custom_body_side_rounding.svg)

Rounds the body outline's corners more or less, down to the plain octagon at 0.

| Default | Range | Step | Unit |
|---|---|---|---|
| 15.85 | 0 to 30 | 0.05 | mm |

Before: 15.85. After: 5. Context: `size` = Custom.

Only acts when size is Custom.

Moves: body edge.

#### `custom_body_top_rounding`

Top edge rounding

![Rounds or squares the edge where the body's top face meets its sides.](../dials/one-sided/custom_body_top_rounding.svg)

Rounds or squares the edge where the body's top face meets its sides.

| Default | Range | Step | Unit |
|---|---|---|---|
| 2.54 | 0 to 5 | 0.01 | mm |

Before: 2.54. After: 0. Context: `size` = Custom. Section at y = 35 mm.

Only acts when size is Custom.

Moves: body edge.

#### `custom_body_bottom_rounding`

Bottom edge rounding

![Rounds or squares the edge where the body's bottom face meets its sides.](../dials/one-sided/custom_body_bottom_rounding.svg)

Rounds or squares the edge where the body's bottom face meets its sides.

| Default | Range | Step | Unit |
|---|---|---|---|
| 0 | 0 to 5 | 0.1 | mm |

Before: 0. After: 2. Context: `size` = Custom. Section at y = 35 mm.

Only acts when size is Custom.

Moves: body edge.

#### `custom_velcro_side_rounding`

Strap slot corner rounding

![Rounds the four corners of each plain strap slot.](../dials/one-sided/custom_velcro_side_rounding.svg)

Rounds the four corners of each plain strap slot.

| Default | Range | Step | Unit |
|---|---|---|---|
| 0 | 0 to 3 | 0.5 | mm |

Before: 0. After: 2.5. Context: `size` = Custom, `velcro_style` = Classic slot.

Only acts when size is Custom and velcro_style is Classic slot.

Moves: classic slots.

#### `custom_velcro_top_bottom_rounding`

Strap opening edge rounding

![Flares the top and bottom edges of the strap openings so the strap does not chafe.](../dials/one-sided/custom_velcro_top_bottom_rounding.svg)

Flares the top and bottom edges of the strap openings so the strap does not chafe.

| Default | Range | Step | Unit |
|---|---|---|---|
| 0 | 0 to 3 | 0.1 | mm |

Before: 0. After: 1.5. Context: `size` = Custom. Section at y = 46 mm.

Only acts when size is Custom.

Moves: pocket, wing openings.

#### `custom_finger_hole_rounding`

Finger hole rim rounding

![Rounds or squares the rims of both finger holes on both faces.](../dials/one-sided/custom_finger_hole_rounding.svg)

Rounds or squares the rims of both finger holes on both faces.

| Default | Range | Step | Unit |
|---|---|---|---|
| 2.5 | 0 to 5 | 0.1 | mm |

Before: 2.5. After: 0. Context: `size` = Custom. Section at y = 19.8 mm.

Only acts when size is Custom.

Moves: finger holes.

#### `custom_t_hook_holder_side_rounding`

Hook crossbar corner rounding

![Rounds or squares the top corners of the hook's crossbar.](../dials/one-sided/custom_t_hook_holder_side_rounding.svg)

Rounds or squares the top corners of the hook's crossbar.

| Default | Range | Step | Unit |
|---|---|---|---|
| 1.27 | 0 to 3 | 0.01 | mm |

Before: 1.27. After: 0. Context: `size` = Custom.

Only acts when size is Custom.

Moves: hook.

#### `custom_t_hook_gap_side_rounding`

Hook slot corner rounding

![Changes no shape of the printed tool, because the J-hook cord catch draws its own corners.](../dials/one-sided/custom_t_hook_gap_side_rounding.svg)

Changes no shape of the printed tool, because the J-hook cord catch draws its own corners.

| Default | Range | Step | Unit |
|---|---|---|---|
| 0 | 0 to 3 | 0.1 | mm |

This dial changes no shape. Changes no shape: the J-hook cord catch is drawn without this dial; it only appears in the Cutouts Only 2D debug overlay.

#### `custom_t_hook_top_bottom_rounding`

Hook edge rounding

![Flares the top and bottom edges of the cord hook's slot and crossbar.](../dials/one-sided/custom_t_hook_top_bottom_rounding.svg)

Flares the top and bottom edges of the cord hook's slot and crossbar.

| Default | Range | Step | Unit |
|---|---|---|---|
| 0 | 0 to 3 | 0.1 | mm |

Before: 0. After: 2. Context: `size` = Custom. Section at x = 4.5 mm.

Only acts when size is Custom.

Moves: hook.

## Two-sided puller

### Step 1 - Your Plug

#### `plug_preset`

Plug preset

![Fills in the plug's length, both widths and the cord from the measured heavy-duty cord plug, so the arms, the grip gap, the cord channel and the plate length all take that plug's shape at once.](../dials/two-sided/plug_preset.svg)

Fills in the plug's length, both widths and the cord from the measured heavy-duty cord plug, so the arms, the grip gap, the cord channel and the plate length all take that plug's shape at once.

| Default | Range | Step | Unit |
|---|---|---|---|
| Measure my plug | 5 options | — | — |

Options: Measure my plug, Heavy-duty extension cord - NEMA 5-15, USB-C laptop tip, Flat 2-prong lamp plug - NEMA 1-15, Standard 3-prong plug - NEMA 5-15.

Before: Measure my plug. After: Heavy-duty extension cord - NEMA 5-15.

Moves: arms, finger lobes, plate edge, zip stations.

#### `measure_plug_length`

Plug length

![Lengthens both arms so the teeth cover the whole plug body, and moves the zip-tie stations and the strap slot with them.](../dials/two-sided/measure_plug_length.svg)

Lengthens both arms so the teeth cover the whole plug body, and moves the zip-tie stations and the strap slot with them.

| Default | Range | Step | Unit |
|---|---|---|---|
| 25.5 | 12 to 85 | 0.5 | mm |

Before: 25.5. After: 40.

Moves: arms.

#### `measure_plug_width_prong_end`

Plug width at the prong end

![Opens or closes the gap between the arms at their tips, where the plug's prong end sits.](../dials/two-sided/measure_plug_width_prong_end.svg)

Opens or closes the gap between the arms at their tips, where the plug's prong end sits.

| Default | Range | Step | Unit |
|---|---|---|---|
| 20 | 5 to 40 | 0.5 | mm |

Before: 20. After: 28.

Moves: arms, cord channel, finger lobes, zip stations.

#### `measure_plug_width_cord_end`

Plug width at the cord end

![Opens or closes the gap between the arms at the plug's back end, so the arms taper to match the plug.](../dials/two-sided/measure_plug_width_cord_end.svg)

Opens or closes the gap between the arms at the plug's back end, so the arms taper to match the plug.

| Default | Range | Step | Unit |
|---|---|---|---|
| 20 | 5 to 40 | 0.5 | mm |

Before: 20. After: 12.

Moves: arms, teeth, zip stations.

#### `measure_cord_thickness`

Cord thickness

![Widens the cord channel between the finger holes, and the finger lobes move outward with it.](../dials/two-sided/measure_cord_thickness.svg)

Widens the cord channel between the finger holes, and the finger lobes move outward with it.

| Default | Range | Step | Unit |
|---|---|---|---|
| 4 | 1.5 to 12 | 0.5 | mm |

Before: 4. After: 9.

Moves: arms, cord channel, finger lobes, zip stations.

#### `plug_sides`

Plug sides

![Removes the sloped cradle from the arms' gripping edges so the teeth bite straight along a flat-sided plug.](../dials/two-sided/plug_sides.svg)

Removes the sloped cradle from the arms' gripping edges so the teeth bite straight along a flat-sided plug.

| Default | Range | Step | Unit |
|---|---|---|---|
| Rounded sides | 2 options | — | — |

Options: Rounded sides, Flat sides.

Before: Rounded sides. After: Flat sides. Section at y = 45 mm.

Moves: arms, teeth.

#### `show_plug_preview`

Show the see-through plug

![Shows or hides the see-through plug in the preview and changes nothing in the printed plates.](../dials/two-sided/show_plug_preview.svg)

Shows or hides the see-through plug in the preview and changes nothing in the printed plates.

| Default | Range | Step | Unit |
|---|---|---|---|
| true | true / false | — | — |

This dial changes no shape. Changes no shape: the see-through plug is a preview aid and is never exported.

### Step 2 - Size

#### `size`

Hand size

![Widens both finger holes and their lobes, so the whole plate grows around them.](../dials/two-sided/size.svg)

Widens both finger holes and their lobes, so the whole plate grows around them.

| Default | Range | Step | Unit |
|---|---|---|---|
| Medium | 4 options | — | — |

Options: Small, Medium, Large, Measure my hand.

Before: Medium. After: Large.

Moves: arms, finger lobes, zip stations.

#### `measure_finger_width`

Finger width

![Widens both finger holes and their lobes.](../dials/two-sided/measure_finger_width.svg)

Widens both finger holes and their lobes.

| Default | Range | Step | Unit |
|---|---|---|---|
| 20 | 14 to 32 | 0.5 | mm |

Before: 20. After: 26. Context: `size` = Measure my hand.

Only acts when size is Measure my hand.

Moves: arms, finger lobes, plate edge, zip stations.

### Step 3 - Attachment

#### `attachment`

Attachment

![Removes the strap slot from each arm, while the zip-tie stations stay because they hold the plates together.](../dials/two-sided/attachment.svg)

Removes the strap slot from each arm, while the zip-tie stations stay because they hold the plates together.

| Default | Range | Step | Unit |
|---|---|---|---|
| Zip ties + Velcro strap | 2 options | — | — |

Options: Zip ties + Velcro strap, Zip ties.

Before: Zip ties + Velcro strap. After: Zip ties. Context: `measure_plug_length` = 40.

Drawn on a 40 mm plug: on the default 25.5 mm plug the arms are too short for a strap slot.

Moves: arms, strap slot, zip stations.

#### `strap_width`

Strap width

![Sets the strap the arm slot must clear, and when the slot's window between the zip-tie stations is shorter than the strap plus 1.5 mm the slot is left out.](../dials/two-sided/strap_width.svg)

Sets the strap the arm slot must clear, and when the slot's window between the zip-tie stations is shorter than the strap plus 1.5 mm the slot is left out.

| Default | Range | Step | Unit |
|---|---|---|---|
| 15 | 10 to 25 | 1 | mm |

Before: 15. After: 25. Context: `measure_plug_length` = 40.

Drawn on a 40 mm plug: on the default 25.5 mm plug the arms are too short for a strap slot.

Moves: arms, strap slot, zip stations.

Can trip: `STRAP WIDER THAN ARM SLOT WINDOW - NARROW THE STRAP`.

### Step 4 - Print Layout

#### `print_layout`

Print layout

![Puts both identical plates side by side in one file, or just one plate.](../dials/two-sided/print_layout.svg)

Puts both identical plates side by side in one file, or just one plate.

| Default | Range | Step | Unit |
|---|---|---|---|
| Both plates | 2 options | — | — |

Options: Both plates, One plate.

Before: Both plates. After: One plate.

Moves: arms, finger lobes, plate edge, zip stations.

### Advanced - Two-Sided Puller

#### `plate_wall_boost`

Extra wall on the plate

![Thickens every wall around the finger holes, the cord channel, the zip-tie holes and the strap slot at once, so the plate outline grows and the openings shift to keep their walls.](../dials/two-sided/plate_wall_boost.svg)

Thickens every wall around the finger holes, the cord channel, the zip-tie holes and the strap slot at once, so the plate outline grows and the openings shift to keep their walls.

| Default | Range | Step | Unit |
|---|---|---|---|
| 0 | 0 to 5 | 0.25 | mm |

Before: 0. After: 2.

Moves: arms, finger lobes, zip stations.

#### `plate_thickness`

Plate thickness

![Thickens each plate, so the finished pair is twice as thick.](../dials/two-sided/plate_thickness.svg)

Thickens each plate, so the finished pair is twice as thick.

| Default | Range | Step | Unit |
|---|---|---|---|
| 4 | 2 to 8 | 0.25 | mm |

Before: 4. After: 6. Section at y = 3 mm.

Moves: cord channel, finger lobes, zip stations.

Can trip: `PLATE THINNER THAN 2MM - TOO FLIMSY`.

#### `plate_grip_bite`

Grip bite

![Squeezes the plug harder or softer, because the arms close in by this much per side against the plug's width.](../dials/two-sided/plate_grip_bite.svg)

Squeezes the plug harder or softer, because the arms close in by this much per side against the plug's width.

| Default | Range | Step | Unit |
|---|---|---|---|
| -1 | -2 to 2 | 0.1 | mm |

Before: -1. After: -2. Context: `plug_sides` = Flat sides. Section at y = 45 mm.

Only acts when plug_sides is Flat sides or a plug preset is chosen.

Moves: arms, teeth.

Can trip: `NO GRIP BITE - PLUG WONT BE HELD`.

#### `plate_cradle_depth`

Cradle depth

![Slopes each arm's gripping edge from the mating face down to the outer face, so two plates form a cradle that centers a round plug.](../dials/two-sided/plate_cradle_depth.svg)

Slopes each arm's gripping edge from the mating face down to the outer face, so two plates form a cradle that centers a round plug.

| Default | Range | Step | Unit |
|---|---|---|---|
| 2.5 | 0 to 3.5 | 0.25 | mm |

Before: 2.5. After: 0. Context: `plug_sides` = Rounded sides. Section at y = 45 mm.

Only acts when plug_sides is Rounded sides.

Moves: arms, teeth.

Can trip: `CRADLE SHALLOWER THAN ASKED - PLUG NARROW`.

#### `plate_grip_clearance`

Grip clearance

![Opens the gap between the arms where the plates meet, so a hard round plug can drop in flat before the cradle holds it.](../dials/two-sided/plate_grip_clearance.svg)

Opens the gap between the arms where the plates meet, so a hard round plug can drop in flat before the cradle holds it.

| Default | Range | Step | Unit |
|---|---|---|---|
| 0.5 | 0 to 2 | 0.1 | mm |

Before: 0.5. After: 2. Context: `plug_sides` = Rounded sides. Section at y = 45 mm.

Only acts when plug_sides is Rounded sides.

Moves: arms, teeth.

#### `plate_cable_clearance`

Cord channel clearance

![Widens the cord channel between the finger holes beyond the cord's thickness.](../dials/two-sided/plate_cable_clearance.svg)

Widens the cord channel between the finger holes beyond the cord's thickness.

| Default | Range | Step | Unit |
|---|---|---|---|
| 0.8 | 0 to 5 | 0.1 | mm |

Before: 0.8. After: 3.

Moves: arms, cord channel, finger lobes, zip stations.

Can trip: `CORD TOO THICK FOR CABLE CHANNEL`; `PLUG NARROWER THAN THE CORD CHANNEL - ARMS CANNOT TOUCH IT`.

#### `plate_finger_fit`

Finger hole fit

![Widens both finger holes beyond your finger width.](../dials/two-sided/plate_finger_fit.svg)

Widens both finger holes beyond your finger width.

| Default | Range | Step | Unit |
|---|---|---|---|
| 1 | 0 to 8 | 0.25 | mm |

Before: 1. After: 4.

Moves: arms, finger lobes, zip stations.

#### `plate_finger_wall`

Finger lobe wall

![Thickens the wall around each finger hole, so the rounded lobes grow.](../dials/two-sided/plate_finger_wall.svg)

Thickens the wall around each finger hole, so the rounded lobes grow.

| Default | Range | Step | Unit |
|---|---|---|---|
| 5 | 3 to 12 | 0.25 | mm |

Before: 5. After: 9.

Moves: arms, finger lobes, zip stations.

#### `plate_finger_inner_wall`

Wall beside the cord channel

![Thickens the wall between the cord channel and each finger hole, pushing the finger holes outward.](../dials/two-sided/plate_finger_inner_wall.svg)

Thickens the wall between the cord channel and each finger hole, pushing the finger holes outward.

| Default | Range | Step | Unit |
|---|---|---|---|
| 3 | 1 to 8 | 0.25 | mm |

Before: 3. After: 6.

Moves: arms, finger lobes, zip stations.

#### `plate_tooth_diameter`

Tooth size

![Cuts bigger or smaller scallops into the arms' gripping edges.](../dials/two-sided/plate_tooth_diameter.svg)

Cuts bigger or smaller scallops into the arms' gripping edges.

| Default | Range | Step | Unit |
|---|---|---|---|
| 2 | 0 to 4 | 0.1 | mm |

Before: 2. After: 4.

Moves: teeth.

#### `plate_tooth_pitch`

Tooth spacing

![Spaces the teeth farther apart or closer together along the gripping edges.](../dials/two-sided/plate_tooth_pitch.svg)

Spaces the teeth farther apart or closer together along the gripping edges.

| Default | Range | Step | Unit |
|---|---|---|---|
| 2.8 | 0.5 to 5 | 0.1 | mm |

Before: 2.8. After: 4.5.

Moves: teeth.

#### `plate_tooth_depth`

Tooth depth

![Cuts each tooth deeper or shallower into the gripping edge.](../dials/two-sided/plate_tooth_depth.svg)

Cuts each tooth deeper or shallower into the gripping edge.

| Default | Range | Step | Unit |
|---|---|---|---|
| 1 | 0 to 1.5 | 0.05 | mm |

Before: 1. After: 0.3.

Moves: teeth.

#### `plate_grip_zone_start`

Toothed zone start

![Moves where the teeth begin, measured back from the arm tips, and the arms lengthen when the zone needs the room.](../dials/two-sided/plate_grip_zone_start.svg)

Moves where the teeth begin, measured back from the arm tips, and the arms lengthen when the zone needs the room.

| Default | Range | Step | Unit |
|---|---|---|---|
| 4 | 0 to 25 | 0.5 | mm |

Before: 4. After: 15.

Moves: arms, teeth, zip stations.

#### `plate_grip_zone_length`

Toothed zone length

![Sets how far the teeth run along each arm instead of covering the whole plug body.](../dials/two-sided/plate_grip_zone_length.svg)

Sets how far the teeth run along each arm instead of covering the whole plug body.

| Default | Range | Step | Unit |
|---|---|---|---|
| 0 | 0 to 60 | 1 | mm |

Before: 0. After: 12.

Moves: arms, zip stations.

#### `plate_tip_flare`

Tip flare

![Opens the gap wider right at the arm tips so the plug head can enter before the teeth bite.](../dials/two-sided/plate_tip_flare.svg)

Opens the gap wider right at the arm tips so the plug head can enter before the teeth bite.

| Default | Range | Step | Unit |
|---|---|---|---|
| 0.7 | 0 to 4 | 0.1 | mm |

Before: 0.7. After: 3.

Moves: arms, cord channel, finger lobes, zip stations.

#### `plate_arm_tip_width`

Arm tip width

![Widens the rounded tip of each arm, so the arms taper less.](../dials/two-sided/plate_arm_tip_width.svg)

Widens the rounded tip of each arm, so the arms taper less.

| Default | Range | Step | Unit |
|---|---|---|---|
| 11 | 5 to 16 | 0.5 | mm |

Before: 11. After: 16.

Moves: arms, zip stations.

#### `plate_edge_rounding`

Outer edge rounding

![Rounds or squares the outer face's edge all around the plate, while the plug-contact face stays square.](../dials/two-sided/plate_edge_rounding.svg)

Rounds or squares the outer face's edge all around the plate, while the plug-contact face stays square.

| Default | Range | Step | Unit |
|---|---|---|---|
| 1.2 | 0 to 2 | 0.1 | mm |

Before: 1.2. After: 0. Section at y = 3 mm.

Moves: finger lobes.

#### `plate_strip_thickness`

Cable strip thickness

![Thickens or removes the thin strip that bridges the cord channel on the outer face and ties the two arms together.](../dials/two-sided/plate_strip_thickness.svg)

Thickens or removes the thin strip that bridges the cord channel on the outer face and ties the two arms together.

| Default | Range | Step | Unit |
|---|---|---|---|
| 1 | 0 to 4 | 0.25 | mm |

Before: 1. After: 0. Section at y = 3 mm.

Moves: cord channel.

#### `plate_zip_hole_diameter`

Zip-tie hole diameter

![Widens the three zip-tie holes in each arm, and the stations shift to keep their walls.](../dials/two-sided/plate_zip_hole_diameter.svg)

Widens the three zip-tie holes in each arm, and the stations shift to keep their walls.

| Default | Range | Step | Unit |
|---|---|---|---|
| 4 | 0 to 8 | 0.1 | mm |

Before: 4. After: 6.

Moves: arms, finger lobes, strap slot, zip stations.

#### `plate_zip_placement`

Zip-tie station placement

![Switches the three zip-tie stations in each arm from the automatic positions to the three position dials.](../dials/two-sided/plate_zip_placement.svg)

Switches the three zip-tie stations in each arm from the automatic positions to the three position dials.

| Default | Range | Step | Unit |
|---|---|---|---|
| Auto | 2 options | — | — |

Options: Auto, Manual.

Before: Auto. After: Manual. Context: `measure_plug_length` = 40.

Drawn on a 40 mm plug so the default manual positions sit on the arm.

Moves: arms, strap slot, zip stations.

#### `plate_zip_pos_1`

Zip-tie station 1 position

![Slides the rear zip-tie station along each arm, measured from the cord end.](../dials/two-sided/plate_zip_pos_1.svg)

Slides the rear zip-tie station along each arm, measured from the cord end.

| Default | Range | Step | Unit |
|---|---|---|---|
| 4 | 0 to 80 | 0.5 | mm |

Before: 4. After: 27. Context: `measure_plug_length` = 40, `plate_zip_placement` = Manual.

Only acts when plate_zip_placement is Manual; drawn on a 40 mm plug so every station sits on the arm.

Moves: finger lobes, zip stations.

Can trip: `ZIP STATION OFF THE ARM`; `ZIP STATIONS OVERLAP EACH OTHER`; `STRAP WIDER THAN ARM SLOT WINDOW - NARROW THE STRAP`.

#### `plate_zip_pos_2`

Zip-tie station 2 position

![Slides the middle zip-tie station along each arm, and the strap slot's window moves with it.](../dials/two-sided/plate_zip_pos_2.svg)

Slides the middle zip-tie station along each arm, and the strap slot's window moves with it.

| Default | Range | Step | Unit |
|---|---|---|---|
| 32 | 0 to 80 | 0.5 | mm |

Before: 32. After: 36. Context: `measure_plug_length` = 40, `plate_zip_placement` = Manual.

Only acts when plate_zip_placement is Manual; drawn on a 40 mm plug so every station sits on the arm.

Moves: strap slot, zip stations.

Can trip: `ZIP STATION OFF THE ARM`; `ZIP STATIONS OVERLAP EACH OTHER`; `ZIP STATION HITS VELCRO SLOT`; `STRAP WIDER THAN ARM SLOT WINDOW - NARROW THE STRAP`.

#### `plate_zip_pos_3`

Zip-tie station 3 position

![Slides the tip zip-tie station along each arm, and the strap slot's window moves with it.](../dials/two-sided/plate_zip_pos_3.svg)

Slides the tip zip-tie station along each arm, and the strap slot's window moves with it.

| Default | Range | Step | Unit |
|---|---|---|---|
| 63 | 0 to 80 | 0.5 | mm |

Before: 63. After: 58. Context: `measure_plug_length` = 40, `plate_zip_placement` = Manual.

Only acts when plate_zip_placement is Manual; drawn on a 40 mm plug so every station sits on the arm.

Moves: arms, strap slot, zip stations.

Can trip: `ZIP STATION OFF THE ARM`; `ZIP STATIONS OVERLAP EACH OTHER`; `ZIP STATION HITS VELCRO SLOT`; `STRAP WIDER THAN ARM SLOT WINDOW - NARROW THE STRAP`.

#### `plate_slot_inner_wall`

Wall between the teeth and the slot

![Thickens the wall between the toothed edge and the strap slot, moving the slot outward.](../dials/two-sided/plate_slot_inner_wall.svg)

Thickens the wall between the toothed edge and the strap slot, moving the slot outward.

| Default | Range | Step | Unit |
|---|---|---|---|
| 2.2 | 1 to 8 | 0.1 | mm |

Before: 2.2. After: 5. Context: `measure_plug_length` = 40.

Drawn on a 40 mm plug: on the default 25.5 mm plug the arms are too short for a strap slot.

Moves: arms, strap slot, zip stations.

#### `plate_velcro_slot_width`

Strap slot width

![Widens the strap slot in each arm, and the arm bulges outward to keep its wall.](../dials/two-sided/plate_velcro_slot_width.svg)

Widens the strap slot in each arm, and the arm bulges outward to keep its wall.

| Default | Range | Step | Unit |
|---|---|---|---|
| 9.3 | 0 to 20 | 0.25 | mm |

Before: 9.3. After: 14. Context: `measure_plug_length` = 40.

Drawn on a 40 mm plug: on the default 25.5 mm plug the arms are too short for a strap slot.

Moves: arms, strap slot, zip stations.

#### `plate_velcro_slot_length`

Strap slot length

![Lengthens or shortens the strap slot along each arm, within the window between the zip-tie stations.](../dials/two-sided/plate_velcro_slot_length.svg)

Lengthens or shortens the strap slot along each arm, within the window between the zip-tie stations.

| Default | Range | Step | Unit |
|---|---|---|---|
| 28 | 5 to 60 | 1 | mm |

Before: 28. After: 15. Context: `measure_plug_length` = 40.

Drawn on a 40 mm plug: on the default 25.5 mm plug the arms are too short for a strap slot.

Moves: arms, strap slot, zip stations.

Can trip: `STRAP WIDER THAN ARM SLOT WINDOW - NARROW THE STRAP`.

### Advanced - Render Quality

#### `quality`

Render quality

![Sets how many flat segments draw each curve and changes no dimension.](../dials/two-sided/quality.svg)

Sets how many flat segments draw each curve and changes no dimension.

| Default | Range | Step | Unit |
|---|---|---|---|
| 64 | 24 to 128 | 8 | segments |

This dial changes no shape. Changes no shape: it only sets the number of segments in every circle and arc.
