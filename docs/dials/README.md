# Dial diagrams

Every dial of the one-sided puller and the two-sided puller has a picture here: the tool at its defaults in black, the plug in teal, and a red dashed trace on the part that dial moves when it goes from its default to a second value.

The pictures are cut from the same OpenSCAD files you print from, at 1 unit = 1 mm; the two values drawn are written under each picture.

black = the tool at its defaults; teal = the plug you measured; red dashed = what this dial moves.

## One-sided puller

### Step 1 - Your Plug

`plug_preset`: Plug preset

![Fills in all six plug numbers from a measured reference plug, so the pocket, the wall notch, the cord hook and the zip-tie and wing positions all take that plug's shape at once.](one-sided/plug_preset.svg)

Before: Measure my plug. After: Standard 3-prong plug - NEMA 5-15. Moves: body edge, pocket, seat, wall notch, wing openings, zip-tie holes.

`measure_plug_length`: Plug length

![Runs the pocket farther toward the finger holes and stretches the whole body to keep the finger holes and zip-tie rows clear of it.](one-sided/measure_plug_length.svg)

Before: 25.5. After: 40. Moves: body edge, seat, wall notch, wing openings, zip-tie holes.

`measure_plug_width_prong_end`: Plug width at the prong end

![Widens or narrows the pocket, its seat and the wall notch at the plug end, and moves the zip-tie holes and wing openings with them.](one-sided/measure_plug_width_prong_end.svg)

Before: 25. After: 32. Moves: seat, wall notch, wing openings, zip-tie holes.

`measure_plug_width_cord_end`: Plug width at the cord end

![Tilts the pocket's side walls to match the plug's taper, and the zip-tie holes and wing openings lean in with them.](one-sided/measure_plug_width_cord_end.svg)

Before: 25. After: 15. Moves: pocket, wing openings.

`measure_plug_thickness_prong_end`: Plug thickness at the prong end

![Deepens or shallows the two pocket floors, the round seat and the plug recess, to suit the fatter of the two thickness numbers.](one-sided/measure_plug_thickness_prong_end.svg)

Before: 20. After: 23.5. Section at x = 0 mm. Moves: pocket, seat.

`measure_plug_thickness_cord_end`: Plug thickness at the cord end

![Deepens or shallows the two pocket floors, the round seat and the plug recess, when this end is the fatter end of the plug.](one-sided/measure_plug_thickness_cord_end.svg)

Before: 20. After: 23.5. Section at x = 0 mm. Moves: pocket, seat.

`measure_cord_thickness`: Cord thickness

![Widens the cord hook's slot and crossbar to fit the cord, and moves the finger holes and the whole body up to make room.](one-sided/measure_cord_thickness.svg)

Before: 4. After: 8. Moves: body edge, finger holes, pocket, wall notch, wing openings, zip-tie holes.

`measure_wall_plate_style`: Outlet cover plate style

![Cuts the wall notch at the plug end deeper or shallower to suit the cover plate, and the zip-tie rows shift down with it.](one-sided/measure_wall_plate_style.svg)

Before: Standard flat plate. After: Oversized / Jumbo. Moves: body edge, pocket, wall notch, wing openings, zip-tie holes.

`show_plug_preview`: Show the see-through plug

![Shows or hides the see-through plug in the preview and changes nothing in the printed tool.](one-sided/show_plug_preview.svg)

This dial changes no shape. Changes no shape: the see-through plug is a preview aid and is never exported.

### Step 2 - Size

`size`: Hand size

![Scales the whole body, both finger holes, the wing openings and the zip-tie grid to the chosen hand size.](one-sided/size.svg)

Before: Medium. After: Large. Moves: body edge, finger holes, pocket, wing openings, zip-tie holes.

`measure_finger_width`: Finger width

![Widens both finger holes, spaces them farther apart and pushes them and the body up to keep the walls printable.](one-sided/measure_finger_width.svg)

Before: 20. After: 26. Context: `size` = Measure my hand. Moves: finger holes, pocket, wall notch, wing openings.

`measure_hand_width`: Hand width

![Widens the whole body outline and thickens the slab in step with the hand.](one-sided/measure_hand_width.svg)

Before: 85. After: 100. Context: `size` = Measure my hand. Moves: wing openings.

### Step 3 - Attachment

`attachment`: Attachment

![Adds or removes the zip-tie holes and the wing or slot openings for the strap.](one-sided/attachment.svg)

Before: Zip ties + Velcro. After: Zip ties. Moves: wing openings.

`velcro_style`: Strap opening style

![Swaps the curved wing openings for a pair of plain rectangular slots that lean along the body's sides.](one-sided/velcro_style.svg)

Before: Wing. After: Classic slot. Moves: wing openings.

`strap_width`: Strap width

![Sets the strap width the wing opening is checked against and changes no shape.](one-sided/strap_width.svg)

This dial changes no shape. Changes no shape: it only sets the width the W-14 check compares the wing opening against.

### Step 4 - Cord Hook

`hook_hand`: Hook side

![Mirrors the cord hook at the cord end so its catch faces the other side, and nothing else moves.](one-sided/hook_hand.svg)

Before: Right. After: Left. Moves: hook.

### Advanced - Zip Tie Placement

`zip_placement`: Zip-tie hole placement

![Switches the zip-tie pairs from the automatic rows to the three position dials, which slide each pair along the plug's side.](one-sided/zip_placement.svg)

Before: Auto. After: Manual. Moves: seat, wall notch, wing openings, zip-tie holes.

`zip_row_count`: Number of zip-tie rows

![Adds or removes a pair of zip-tie holes, and the rows squeeze together when the body has no room for another.](one-sided/zip_row_count.svg)

Before: 2. After: 3. Moves: wing openings, zip-tie holes.

`zip_pos_1`: Zip-tie pair 1 position

![Slides the first pair of zip-tie holes along the plug's side, measured from the plug end.](one-sided/zip_pos_1.svg)

Before: 6. After: 10. Context: `zip_placement` = Manual. Moves: seat, wall notch, zip-tie holes.

`zip_pos_2`: Zip-tie pair 2 position

![Slides the second pair of zip-tie holes along the plug's side, measured from the plug end.](one-sided/zip_pos_2.svg)

Before: 18. After: 26. Context: `zip_placement` = Manual. Moves: wing openings, zip-tie holes.

`zip_pos_3`: Zip-tie pair 3 position

![Slides the third pair of zip-tie holes along the plug's side, measured from the plug end.](one-sided/zip_pos_3.svg)

Before: 30. After: 26. Context: `zip_placement` = Manual, `zip_row_count` = 3. Moves: wing openings, zip-tie holes.

`zip_edge_offset`: Zip-tie hole distance from the pocket wall

![Moves every zip-tie hole farther from or closer to the pocket wall, and the wing openings reshape around them.](one-sided/zip_edge_offset.svg)

Before: 4. After: 8. Moves: wing openings, zip-tie holes.

### Advanced - Velcro Placement

`velcro_placement`: Strap slot placement

![Switches the strap openings to a pair of plain slots that the position dial slides along the plug's side, whatever the opening style.](one-sided/velcro_placement.svg)

Before: Auto. After: Manual. Moves: wing openings.

`velcro_pos`: Strap slot position

![Slides the pair of strap slots along the plug's side, measured from the plug end.](one-sided/velcro_pos.svg)

Before: 12. After: 25. Context: `velcro_style` = Classic slot, `velcro_placement` = Manual. Moves: classic slots.

### Advanced - Render Quality

`quality`: Render quality

![Sets how many flat segments draw each curve and changes no dimension.](one-sided/quality.svg)

This dial changes no shape. Changes no shape: it only sets the number of segments in every circle and arc.

### Custom Mode

`reset_custom_to_medium`: Reset Custom to the Medium reference

![Swaps every Custom slider for the Medium reference values for one render, so the whole tool snaps back to the Medium shape.](one-sided/reset_custom_to_medium.svg)

Before: false. After: true. Context: `size` = Custom. Moves: finger holes, wall notch, wing openings, zip-tie holes.

`custom_enable_auto_fit`: Auto-fit

![Lets the tool clamp any Custom slider that would push a feature past the body or into a neighbor, and changes nothing while every slider is inside its safe range.](one-sided/custom_enable_auto_fit.svg)

This dial changes no shape. Changes no shape at the Custom defaults: it only clamps sliders that leave their safe range, and every clamp is reported in the console.

### Body Shape (Custom size only)

`custom_puller_length`: Body length

![Stretches the whole body from the cord end to the plug end.](one-sided/custom_puller_length.svg)

Before: 63.5. After: 73.5. Context: `size` = Custom. Moves: body edge, pocket, seat, wall notch, zip-tie holes.

`custom_puller_bottom_width`: Body width at the widest point

![Widens the body at its widest point, just above the cord end, before the side rounding is applied.](one-sided/custom_puller_bottom_width.svg)

Before: 77.6. After: 87.6. Context: `size` = Custom. Moves: body edge.

`custom_puller_bottom_corners`: Cord-end corner width

![Widens the flat at the cord end where the two lower corners of the body outline sit.](one-sided/custom_puller_bottom_corners.svg)

Before: 3. After: 13. Context: `size` = Custom. Moves: body edge.

`custom_puller_top_width`: Body width at the plug end

![Widens the plug end of the body, where the wall notch and the pocket seat sit.](one-sided/custom_puller_top_width.svg)

Before: 31.75. After: 41.75. Context: `size` = Custom. Moves: body edge, wing openings.

`custom_puller_middle_width`: Body width at the middle

![Widens the body at the middle control point, bulging or straightening the side edges between the widest point and the plug end.](one-sided/custom_puller_middle_width.svg)

Before: 57.35. After: 67.35. Context: `size` = Custom. Moves: body edge, wing openings.

`custom_puller_side_corner`: Side corner position

![Moves the two widest corners of the body outline up toward the plug end or down toward the cord end.](one-sided/custom_puller_side_corner.svg)

Before: 4.65. After: 14.65. Context: `size` = Custom. Moves: body edge, wing openings.

`custom_body_thickness`: Body thickness

![Thickens the whole slab, so every hole and the pocket get deeper walls.](one-sided/custom_body_thickness.svg)

Before: 6.35. After: 9. Context: `size` = Custom. Section at y = 35 mm. Moves: body edge.

`custom_body_round_bottom_only`: Round the cord half only

![Rounds the whole outline instead of only the cord half, so the plug end loses its crisp corners.](one-sided/custom_body_round_bottom_only.svg)

Before: true. After: false. Context: `size` = Custom. Moves: body edge, hook, seat, wall notch.

### Plug Pocket (Custom size only)

`custom_pocket_seat_diameter`: Pocket seat diameter

![Widens the round seat cut into the plug end of the pocket.](one-sided/custom_pocket_seat_diameter.svg)

Before: 31.75. After: 28. Context: `size` = Custom. Moves: seat.

`custom_pocket_width`: Pocket width

![Widens the plug recess, and the zip-tie holes and wing openings move outward with its wall.](one-sided/custom_pocket_width.svg)

Before: 28.85. After: 34. Context: `size` = Custom. Moves: pocket, seat, wing openings, zip-tie holes.

`custom_pocket_depth`: Pocket depth

![Runs the plug recess farther from the plug end toward the finger holes.](one-sided/custom_pocket_depth.svg)

Before: 24.5. After: 34. Context: `size` = Custom. Moves: pocket, wing openings.

`custom_pocket_dome_drop`: Pocket reference drop

![Changes no shape of the pocket, because the recess outline is built from the plug width at the plug end and the side taper, and this reference point cancels out of it.](one-sided/custom_pocket_dome_drop.svg)

This dial changes no shape. Changes no shape: the recess is a rounded-nose shape whose width at the plug end is the pocket width and whose walls follow the side taper, so this reference point cancels out; measured with straight and with tapered walls.

`custom_pocket_seat_floor`: Pocket seat floor thickness

![Thins or thickens the floor left under the round seat, so the seat is cut deeper or shallower.](one-sided/custom_pocket_seat_floor.svg)

Before: 3.175. After: 1.5. Context: `size` = Custom. Section at x = 0 mm. Moves: seat.

`custom_pocket_floor`: Plug recess floor thickness

![Thins or thickens the floor left under the plug recess, so the recess is cut deeper or shallower.](one-sided/custom_pocket_floor.svg)

Before: 3.81. After: 2. Context: `size` = Custom. Section at x = 0 mm. Moves: pocket, seat.

`custom_pocket_side_angle`: Pocket side taper

![Tilts the pocket's side walls inward toward the cord end, and the zip-tie holes and strap slots lean in along the same line.](one-sided/custom_pocket_side_angle.svg)

Before: 0. After: 10. Context: `size` = Custom. Moves: pocket, wing openings.

### Finger Holes (Custom size only)

`custom_enable_finger_holes`: Finger holes on or off

![Cuts or leaves out both finger holes.](one-sided/custom_enable_finger_holes.svg)

Before: true. After: false. Context: `size` = Custom. Moves: body edge, finger holes.

`custom_finger_hole_diameter`: Finger hole diameter

![Widens both finger holes.](one-sided/custom_finger_hole_diameter.svg)

Before: 25.4. After: 22. Context: `size` = Custom. Moves: finger holes, wing openings.

`custom_finger_hole_spacing`: Finger hole spacing

![Moves the two finger holes farther apart or closer together.](one-sided/custom_finger_hole_spacing.svg)

Before: 33. After: 40. Context: `size` = Custom. Moves: finger holes, wing openings.

`custom_finger_hole_y_position`: Finger hole position

![Slides both finger holes up toward the pocket or down toward the cord hook.](one-sided/custom_finger_hole_y_position.svg)

Before: 19.8. After: 26. Context: `size` = Custom. Moves: finger holes, pocket.

### T Hook (Custom size only)

`custom_enable_t_hook`: Cord hook on or off

![Cuts or leaves out the cord hook at the cord end.](one-sided/custom_enable_t_hook.svg)

Before: true. After: false. Context: `size` = Custom. Moves: hook.

`custom_t_hook_base_gap`: Hook slot width

![Widens the slot the cord slides into at the cord end.](one-sided/custom_t_hook_base_gap.svg)

Before: 4.7625. After: 7. Context: `size` = Custom. Moves: hook.

`custom_t_hook_length`: Hook length

![Runs the cord hook farther into the body from the cord end.](one-sided/custom_t_hook_length.svg)

Before: 10.16. After: 15. Context: `size` = Custom. Moves: finger holes, hook, pocket, wing openings, zip-tie holes.

`custom_t_hook_holder_width`: Hook crossbar width

![Widens the crossbar the cord hooks under at the top of the slot.](one-sided/custom_t_hook_holder_width.svg)

Before: 11.1125. After: 16. Context: `size` = Custom. Moves: finger holes, hook, wing openings, zip-tie holes.

`custom_t_hook_holder_length`: Hook crossbar height

![Makes the crossbar opening taller or shorter along the body.](one-sided/custom_t_hook_holder_length.svg)

Before: 5.08. After: 8. Context: `size` = Custom. Moves: hook.

`custom_t_hook_gap_offset`: Hook slot inset

![Changes no shape of the printed tool, because the J-hook cord catch does not read this dial.](one-sided/custom_t_hook_gap_offset.svg)

This dial changes no shape. Changes no shape: the J-hook cord catch is drawn without this dial; it only appears in the Cutouts Only 2D debug overlay.

`custom_t_hook_leg_offset`: Hook stem side offset

![Moves nothing on the hook itself, and only pushes the finger holes up when the auto-fit keep-out around the hook grows with it.](one-sided/custom_t_hook_leg_offset.svg)

Before: 0. After: 3. Context: `size` = Custom. Moves: finger holes, wing openings, zip-tie holes.

`custom_t_hook_stem_offset`: Hook stem offset

![Shifts the cord slot sideways along the crossbar, making the J of the hook deeper or shallower.](one-sided/custom_t_hook_stem_offset.svg)

Before: 4.5. After: 7. Context: `size` = Custom. Moves: hook.

`custom_t_hook_catch_reach`: Hook catch reach

![Extends the crossbar past the slot on the catch side, lengthening the lip the cord hooks under.](one-sided/custom_t_hook_catch_reach.svg)

Before: 4.55. After: 8. Context: `size` = Custom. Moves: hook.

`custom_t_hook_tip_drop`: Hook tip drop

![Sags the slot's mouth farther below the cord end so a hooked cord cannot back out.](one-sided/custom_t_hook_tip_drop.svg)

This dial changes no shape. Only acts when size is Custom. Changes no shape: the hook slot's mouth already opens through the cord end (the body ends at Y = 0), so sagging the mouth farther below that edge cuts only air; measured at 1.98, 4 and 0.

### Plug Wall Notch (Custom size only)

`custom_enable_plug_wall_notch`: Wall notch on or off

![Cuts or leaves out the notch at the plug end that straddles the outlet's cover plate.](one-sided/custom_enable_plug_wall_notch.svg)

Before: true. After: false. Context: `size` = Custom. Moves: wall notch.

`custom_plug_wall_notch_width`: Wall notch width

![Widens or narrows the notch at the plug end.](one-sided/custom_plug_wall_notch_width.svg)

Before: 26.67. After: 20. Context: `size` = Custom. Moves: wall notch.

`custom_plug_wall_notch_height`: Wall notch depth

![Cuts the notch deeper or shallower into the plug end.](one-sided/custom_plug_wall_notch_height.svg)

Before: 3.81. After: 7. Context: `size` = Custom. Moves: wall notch, wing openings, zip-tie holes.

`custom_plug_wall_notch_rounding`: Wall notch corner rounding

![Rounds or squares the notch's two inner corners.](one-sided/custom_plug_wall_notch_rounding.svg)

Before: 2.54. After: 0. Context: `size` = Custom. Moves: wall notch.

### Zip Tie Holes (Custom size only)

`custom_zip_tie_hole_diameter`: Zip-tie hole diameter

![Widens every zip-tie hole.](one-sided/custom_zip_tie_hole_diameter.svg)

Before: 5.08. After: 7. Context: `size` = Custom. Moves: wing openings, zip-tie holes.

`custom_zip_tie_height_spacing`: Zip-tie row spacing

![Moves the second row of zip-tie holes closer to or farther from the first.](one-sided/custom_zip_tie_height_spacing.svg)

Before: 17.78. After: 12. Context: `size` = Custom. Moves: wing openings, zip-tie holes.

`custom_zip_tie_width_spacing`: Zip-tie column spacing

![Moves no zip-tie hole, because the two columns follow the pocket wall, and only feeds the auto-fit keep-out that can trim the row spacing by a hair.](one-sided/custom_zip_tie_width_spacing.svg)

This dial changes no shape. Changes no shape of its own: the zip-tie columns sit zip_edge_offset inside the pocket wall; this dial only feeds the auto-fit finger keep-out, which trimmed the row spacing by 0.05 mm at the Custom defaults.

`custom_zip_tie_distance_from_notch`: Zip-tie distance from the notch

![Moves the first row of zip-tie holes farther from the wall notch, and the second row follows.](one-sided/custom_zip_tie_distance_from_notch.svg)

Before: 5.1. After: 9. Context: `size` = Custom. Moves: wing openings, zip-tie holes.

`custom_zip_tie_countersink`: Zip-tie countersink

![Flares the top of the zip-tie holes wider so the tie head sits flush.](one-sided/custom_zip_tie_countersink.svg)

Before: 0.9. After: 2.5. Context: `size` = Custom. Section at x = 10.4 mm. Moves: pocket, zip-tie holes.

### Velcro / Wing Strap Holes (Custom size only)

`custom_velcro_hole_length`: Strap slot length

![Lengthens each plain strap slot along its lean.](one-sided/custom_velcro_hole_length.svg)

Before: 12. After: 18. Context: `size` = Custom, `velcro_style` = Classic slot. Moves: classic slots.

`custom_velcro_hole_width`: Strap slot width

![Widens each plain strap slot.](one-sided/custom_velcro_hole_width.svg)

Before: 7. After: 11. Context: `size` = Custom, `velcro_style` = Classic slot. Moves: classic slots.

`custom_velcro_hole_x_center`: Strap slot distance from the centerline

![Moves the two plain strap slots closer to or farther from the centerline.](one-sided/custom_velcro_hole_x_center.svg)

Before: 19.4. After: 14. Context: `size` = Custom, `velcro_style` = Classic slot. Moves: classic slots.

`custom_velcro_hole_y_center`: Strap slot position along the body

![Slides the two plain strap slots toward the cord end or the plug end.](one-sided/custom_velcro_hole_y_center.svg)

Before: 46. After: 38. Context: `size` = Custom, `velcro_style` = Classic slot. Moves: classic slots.

`custom_velcro_hole_rotation`: Strap slot lean

![Leans the two plain strap slots more or less steeply, mirrored on the two sides.](one-sided/custom_velcro_hole_rotation.svg)

Before: 23.5. After: 60. Context: `size` = Custom, `velcro_style` = Classic slot. Moves: classic slots.

### Edge Rounding (Custom size only)

`custom_body_side_rounding`: Body side rounding

![Rounds the body outline's corners more or less, down to the plain octagon at 0.](one-sided/custom_body_side_rounding.svg)

Before: 15.85. After: 5. Context: `size` = Custom. Moves: body edge.

`custom_body_top_rounding`: Top edge rounding

![Rounds or squares the edge where the body's top face meets its sides.](one-sided/custom_body_top_rounding.svg)

Before: 2.54. After: 0. Context: `size` = Custom. Section at y = 35 mm. Moves: body edge.

`custom_body_bottom_rounding`: Bottom edge rounding

![Rounds or squares the edge where the body's bottom face meets its sides.](one-sided/custom_body_bottom_rounding.svg)

Before: 0. After: 2. Context: `size` = Custom. Section at y = 35 mm. Moves: body edge.

`custom_velcro_side_rounding`: Strap slot corner rounding

![Rounds the four corners of each plain strap slot.](one-sided/custom_velcro_side_rounding.svg)

Before: 0. After: 2.5. Context: `size` = Custom, `velcro_style` = Classic slot. Moves: classic slots.

`custom_velcro_top_bottom_rounding`: Strap opening edge rounding

![Flares the top and bottom edges of the strap openings so the strap does not chafe.](one-sided/custom_velcro_top_bottom_rounding.svg)

Before: 0. After: 1.5. Context: `size` = Custom. Section at y = 46 mm. Moves: pocket, wing openings.

`custom_finger_hole_rounding`: Finger hole rim rounding

![Rounds or squares the rims of both finger holes on both faces.](one-sided/custom_finger_hole_rounding.svg)

Before: 2.5. After: 0. Context: `size` = Custom. Section at y = 19.8 mm. Moves: finger holes.

`custom_t_hook_holder_side_rounding`: Hook crossbar corner rounding

![Rounds or squares the top corners of the hook's crossbar.](one-sided/custom_t_hook_holder_side_rounding.svg)

Before: 1.27. After: 0. Context: `size` = Custom. Moves: hook.

`custom_t_hook_gap_side_rounding`: Hook slot corner rounding

![Changes no shape of the printed tool, because the J-hook cord catch draws its own corners.](one-sided/custom_t_hook_gap_side_rounding.svg)

This dial changes no shape. Changes no shape: the J-hook cord catch is drawn without this dial; it only appears in the Cutouts Only 2D debug overlay.

`custom_t_hook_top_bottom_rounding`: Hook edge rounding

![Flares the top and bottom edges of the cord hook's slot and crossbar.](one-sided/custom_t_hook_top_bottom_rounding.svg)

Before: 0. After: 2. Context: `size` = Custom. Section at x = 4.5 mm. Moves: hook.

## Two-sided puller

### Step 1 - Your Plug

`plug_preset`: Plug preset

![Fills in the plug's length, both widths and the cord from the measured heavy-duty cord plug, so the arms, the grip gap, the cord channel and the plate length all take that plug's shape at once.](two-sided/plug_preset.svg)

Before: Measure my plug. After: Heavy-duty extension cord - NEMA 5-15. Moves: arms, finger lobes, plate edge, zip stations.

`measure_plug_length`: Plug length

![Lengthens both arms so the teeth cover the whole plug body, and moves the zip-tie stations and the strap slot with them.](two-sided/measure_plug_length.svg)

Before: 25.5. After: 40. Moves: arms.

`measure_plug_width_prong_end`: Plug width at the prong end

![Opens or closes the gap between the arms at their tips, where the plug's prong end sits.](two-sided/measure_plug_width_prong_end.svg)

Before: 20. After: 28. Moves: arms, cord channel, finger lobes, zip stations.

`measure_plug_width_cord_end`: Plug width at the cord end

![Opens or closes the gap between the arms at the plug's back end, so the arms taper to match the plug.](two-sided/measure_plug_width_cord_end.svg)

Before: 20. After: 12. Moves: arms, teeth, zip stations.

`measure_cord_thickness`: Cord thickness

![Widens the cord channel between the finger holes, and the finger lobes move outward with it.](two-sided/measure_cord_thickness.svg)

Before: 4. After: 9. Moves: arms, cord channel, finger lobes, zip stations.

`plug_sides`: Plug sides

![Removes the sloped cradle from the arms' gripping edges so the teeth bite straight along a flat-sided plug.](two-sided/plug_sides.svg)

Before: Rounded sides. After: Flat sides. Section at y = 45 mm. Moves: arms, teeth.

`show_plug_preview`: Show the see-through plug

![Shows or hides the see-through plug in the preview and changes nothing in the printed plates.](two-sided/show_plug_preview.svg)

This dial changes no shape. Changes no shape: the see-through plug is a preview aid and is never exported.

### Step 2 - Size

`size`: Hand size

![Widens both finger holes and their lobes, so the whole plate grows around them.](two-sided/size.svg)

Before: Medium. After: Large. Moves: arms, finger lobes, zip stations.

`measure_finger_width`: Finger width

![Widens both finger holes and their lobes.](two-sided/measure_finger_width.svg)

Before: 20. After: 26. Context: `size` = Measure my hand. Moves: arms, finger lobes, plate edge, zip stations.

### Step 3 - Attachment

`attachment`: Attachment

![Removes the strap slot from each arm, while the zip-tie stations stay because they hold the plates together.](two-sided/attachment.svg)

Before: Zip ties + Velcro strap. After: Zip ties. Context: `measure_plug_length` = 40. Moves: arms, strap slot, zip stations.

`strap_width`: Strap width

![Sets the strap the arm slot must clear, and when the slot's window between the zip-tie stations is shorter than the strap plus 1.5 mm the slot is left out.](two-sided/strap_width.svg)

Before: 15. After: 25. Context: `measure_plug_length` = 40. Moves: arms, strap slot, zip stations.

### Step 4 - Print Layout

`print_layout`: Print layout

![Puts both identical plates side by side in one file, or just one plate.](two-sided/print_layout.svg)

Before: Both plates. After: One plate. Moves: arms, finger lobes, plate edge, zip stations.

### Advanced - Two-Sided Puller

`plate_wall_boost`: Extra wall on the plate

![Thickens every wall around the finger holes, the cord channel, the zip-tie holes and the strap slot at once, so the plate outline grows and the openings shift to keep their walls.](two-sided/plate_wall_boost.svg)

Before: 0. After: 2. Moves: arms, finger lobes, zip stations.

`plate_thickness`: Plate thickness

![Thickens each plate, so the finished pair is twice as thick.](two-sided/plate_thickness.svg)

Before: 4. After: 6. Section at y = 3 mm. Moves: cord channel, finger lobes, zip stations.

`plate_grip_bite`: Grip bite

![Squeezes the plug harder or softer, because the arms close in by this much per side against the plug's width.](two-sided/plate_grip_bite.svg)

Before: -1. After: -2. Context: `plug_sides` = Flat sides. Section at y = 45 mm. Moves: arms, teeth.

`plate_cradle_depth`: Cradle depth

![Slopes each arm's gripping edge from the mating face down to the outer face, so two plates form a cradle that centers a round plug.](two-sided/plate_cradle_depth.svg)

Before: 2.5. After: 0. Context: `plug_sides` = Rounded sides. Section at y = 45 mm. Moves: arms, teeth.

`plate_grip_clearance`: Grip clearance

![Opens the gap between the arms where the plates meet, so a hard round plug can drop in flat before the cradle holds it.](two-sided/plate_grip_clearance.svg)

Before: 0.5. After: 2. Context: `plug_sides` = Rounded sides. Section at y = 45 mm. Moves: arms, teeth.

`plate_cable_clearance`: Cord channel clearance

![Widens the cord channel between the finger holes beyond the cord's thickness.](two-sided/plate_cable_clearance.svg)

Before: 0.8. After: 3. Moves: arms, cord channel, finger lobes, zip stations.

`plate_finger_fit`: Finger hole fit

![Widens both finger holes beyond your finger width.](two-sided/plate_finger_fit.svg)

Before: 1. After: 4. Moves: arms, finger lobes, zip stations.

`plate_finger_wall`: Finger lobe wall

![Thickens the wall around each finger hole, so the rounded lobes grow.](two-sided/plate_finger_wall.svg)

Before: 5. After: 9. Moves: arms, finger lobes, zip stations.

`plate_finger_inner_wall`: Wall beside the cord channel

![Thickens the wall between the cord channel and each finger hole, pushing the finger holes outward.](two-sided/plate_finger_inner_wall.svg)

Before: 3. After: 6. Moves: arms, finger lobes, zip stations.

`plate_tooth_diameter`: Tooth size

![Cuts bigger or smaller scallops into the arms' gripping edges.](two-sided/plate_tooth_diameter.svg)

Before: 2. After: 4. Moves: teeth.

`plate_tooth_pitch`: Tooth spacing

![Spaces the teeth farther apart or closer together along the gripping edges.](two-sided/plate_tooth_pitch.svg)

Before: 2.8. After: 4.5. Moves: teeth.

`plate_tooth_depth`: Tooth depth

![Cuts each tooth deeper or shallower into the gripping edge.](two-sided/plate_tooth_depth.svg)

Before: 1. After: 0.3. Moves: teeth.

`plate_grip_zone_start`: Toothed zone start

![Moves where the teeth begin, measured back from the arm tips, and the arms lengthen when the zone needs the room.](two-sided/plate_grip_zone_start.svg)

Before: 4. After: 15. Moves: arms, teeth, zip stations.

`plate_grip_zone_length`: Toothed zone length

![Sets how far the teeth run along each arm instead of covering the whole plug body.](two-sided/plate_grip_zone_length.svg)

Before: 0. After: 12. Moves: arms, zip stations.

`plate_tip_flare`: Tip flare

![Opens the gap wider right at the arm tips so the plug head can enter before the teeth bite.](two-sided/plate_tip_flare.svg)

Before: 0.7. After: 3. Moves: arms, cord channel, finger lobes, zip stations.

`plate_arm_tip_width`: Arm tip width

![Widens the rounded tip of each arm, so the arms taper less.](two-sided/plate_arm_tip_width.svg)

Before: 11. After: 16. Moves: arms, zip stations.

`plate_edge_rounding`: Outer edge rounding

![Rounds or squares the outer face's edge all around the plate, while the plug-contact face stays square.](two-sided/plate_edge_rounding.svg)

Before: 1.2. After: 0. Section at y = 3 mm. Moves: finger lobes.

`plate_strip_thickness`: Cable strip thickness

![Thickens or removes the thin strip that bridges the cord channel on the outer face and ties the two arms together.](two-sided/plate_strip_thickness.svg)

Before: 1. After: 0. Section at y = 3 mm. Moves: cord channel.

`plate_zip_hole_diameter`: Zip-tie hole diameter

![Widens the three zip-tie holes in each arm, and the stations shift to keep their walls.](two-sided/plate_zip_hole_diameter.svg)

Before: 4. After: 6. Moves: arms, finger lobes, strap slot, zip stations.

`plate_zip_placement`: Zip-tie station placement

![Switches the three zip-tie stations in each arm from the automatic positions to the three position dials.](two-sided/plate_zip_placement.svg)

Before: Auto. After: Manual. Context: `measure_plug_length` = 40. Moves: arms, strap slot, zip stations.

`plate_zip_pos_1`: Zip-tie station 1 position

![Slides the rear zip-tie station along each arm, measured from the cord end.](two-sided/plate_zip_pos_1.svg)

Before: 4. After: 27. Context: `measure_plug_length` = 40, `plate_zip_placement` = Manual. Moves: finger lobes, zip stations.

`plate_zip_pos_2`: Zip-tie station 2 position

![Slides the middle zip-tie station along each arm, and the strap slot's window moves with it.](two-sided/plate_zip_pos_2.svg)

Before: 32. After: 36. Context: `measure_plug_length` = 40, `plate_zip_placement` = Manual. Moves: strap slot, zip stations.

`plate_zip_pos_3`: Zip-tie station 3 position

![Slides the tip zip-tie station along each arm, and the strap slot's window moves with it.](two-sided/plate_zip_pos_3.svg)

Before: 63. After: 58. Context: `measure_plug_length` = 40, `plate_zip_placement` = Manual. Moves: arms, strap slot, zip stations.

`plate_slot_inner_wall`: Wall between the teeth and the slot

![Thickens the wall between the toothed edge and the strap slot, moving the slot outward.](two-sided/plate_slot_inner_wall.svg)

Before: 2.2. After: 5. Context: `measure_plug_length` = 40. Moves: arms, strap slot, zip stations.

`plate_velcro_slot_width`: Strap slot width

![Widens the strap slot in each arm, and the arm bulges outward to keep its wall.](two-sided/plate_velcro_slot_width.svg)

Before: 9.3. After: 14. Context: `measure_plug_length` = 40. Moves: arms, strap slot, zip stations.

`plate_velcro_slot_length`: Strap slot length

![Lengthens or shortens the strap slot along each arm, within the window between the zip-tie stations.](two-sided/plate_velcro_slot_length.svg)

Before: 28. After: 15. Context: `measure_plug_length` = 40. Moves: arms, strap slot, zip stations.

### Advanced - Render Quality

`quality`: Render quality

![Sets how many flat segments draw each curve and changes no dimension.](two-sided/quality.svg)

This dial changes no shape. Changes no shape: it only sets the number of segments in every circle and arc.
