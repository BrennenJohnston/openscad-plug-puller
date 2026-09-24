# Fit Troubleshooting — One Measurement, One Nudge, One Reprint

Printed your Plug Puller and something isn't quite right? Find your
symptom below. Every fix names **one measurement** to change and **by
how much**. Change it in the Customizer form, re-export (F6, then
`File ▸ Export ▸ Export as STL…`), and reprint. You never need to
touch anything below the three Step groups at the top of the form.

> **Rule of thumb:** nudge in small steps (0.5–2 mm). Looser always
> beats tighter — a slightly roomy tool still works, a tight one
> doesn't.

## Physical fit problems

These are the one-sided puller's symptoms. The two-sided puller's fit
dials (`plate_grip_clearance`, `plate_cradle_depth`, `plate_grip_bite`,
`plate_cable_clearance`, `plate_finger_fit`) are in the
[Power User Guide](power-user-guide.md).

| # | Symptom | Change this | By how much |
| - | ------- | ----------- | ----------- |
| 1 | Plug body rubs the sides of the end notch / won't slide in | **Plug width at the prong end** | **+1 mm** |
| 2 | Plug falls out of the notch or rattles side to side | **Plug width at the prong end** | **−0.5 mm** |
| 3 | Plug won't seat down into the pocket | **Plug length** | **+2 mm** |
| 4 | Plug seats, but the tool overhangs the plug by a lot (pocket much longer than the plug) | **Plug length** | **−2 mm** |
| 5 | Plug sits proud of the pocket / tool rocks on top of the plug | **Plug thickness** (the end that measured fatter) | **+2 mm** |
| 5b | Pocket walls pinch the plug's cord end (or gape at it) | **Plug width at the cord end** | **+1 mm** (pinches) / **−1 mm** (gapes) |
| 6 | Hook won't take the cord / cord has to be forced in | **Cord thickness** | **+0.5 mm** |
| 7 | Cord slips out of the hook while pulling | **Cord thickness** | **−0.5 mm** |
| 8 | Tool won't sit flat against the wall — the outlet cover pushes it away | **Wall plate style** | Pick the next bigger style (Standard flat plate → Rocker / Decora → Oversized / Jumbo) |
| 9 | Fingers pinch in the holes / knuckle drags on the rim | **Size** up one step — or switch to **Measure my hand** and add **+1 mm** finger knuckle width |
| 10 | Fingers swim in the holes and the pull feels sloppy | **Size** down one step — or Measure my hand with **−1 mm** finger width |
| 11 | Tool edges dig into your palm / tool feels too wide | **Size** down — or Measure my hand with **−5 mm** hand width |
| 12 | Tool feels too small in the hand / fingers crowd the edges | **Size** up — or Measure my hand with **+5 mm** hand width |
| 13 | Tool too wide for a cramped outlet corner (hits trim or another plug) | **Size** down one step (the body tracks the hand size) |
| 14 | Strap keeps sliding off the plug | **Attachment** → `Zip ties + Velcro` and use both |
| 15 | Smooth round plug still slips out of the zip-tie hold | Thread a zip tie down one zip-tie hole, around the plug barrel, and back up the opposite hole, then cinch it — the 2×2 hole grid doubles as a clamp anchor |
| 16 | Hook is on the wrong side for your hand | **Step 4** → `hook_hand` = **Left** (or **Right**) |
| 17 | Strap won't thread through the wing opening | **Step 3** → lower `strap_width`, or use a narrower strap (the wing is sized to it) |

## Red warning tags

If the preview shows red text — or a red text tag **printed next to
your part** — the model detected a problem before you wasted a full
print. That's deliberate: a bad file fails loudly instead of silently.
Read the tag, fix that measurement, re-export.

### One-sided puller tags

| Tag says | What it means | What to do |
| -------- | ------------- | ---------- |
| `CHECK PLUG LENGTH MEASUREMENT (MM?)` / `CHECK PLUG WIDTH MEASUREMENTS (MM?)` / `CHECK PLUG THICKNESS MEASUREMENTS (MM?)` / `CHECK CORD THICKNESS MEASUREMENT (MM?)` / `CHECK FINGER WIDTH MEASUREMENT (MM?)` / `CHECK HAND WIDTH MEASUREMENT (MM?)` | That number is outside any plausible mm value — classic inch entry (e.g. 1.25 instead of 32) | Re-measure with the **mm** side, re-type |
| `FINGER TOO BIG FOR HAND WIDTH - RECHECK BOTH` | The finger holes can't physically fit inside a body sized for that hand width | Re-measure both finger knuckle width and hand width — one of them is off |
| `PLUG TOO WIDE FOR THIS DESIGN (MAX 38MM)` | Your plug (at the prong end) is wider than the tool's end can open up | The design tops out near 38 mm plug width; if your plug is really that wide, this tool geometry can't grip it |
| `PLUG THICKER THAN 24MM - USE THE TWO-SIDED PULLER FILE` | Your plug is 24 mm thick or more at one end: too thick for this tool's pocket | Open the two-sided puller, `src/Plug_Puller_Two_Sided.scad` (or its single-file build), and fill in its Step 1; if the number is a mis-measurement, re-measure plug thickness at both ends |
| `PLUG LONGER THAN POCKET LIMIT - POCKET SHORTENED` | The plug is longer than the pocket budget inside the tool's 120 mm body ceiling, so the pocket was truncated — the tool still works but won't swallow the whole plug | Double-check plug length; if it's real, print and try it |
| `PLUG WIDTH TAPER TOO STEEP - RECHECK BOTH WIDTHS` | The two width measurements describe a taper steeper than the pocket walls can follow | Re-measure plug width at the prong end and at the cord end — one of them is probably off |
| `CORD TOO THICK FOR HOOK SLOT` | The hook slot can't open wide enough for that cord | Re-measure the cord's **thin** side; cords past ~9 mm don't fit the hook |
| `FINGER HOLES HIT PLUG POCKET` | Your finger + plug combination makes the holes collide with the plug pocket | Reduce finger knuckle width slightly, or re-check plug length |
| `FINGER HOLES TOO CLOSE - WEAK BRIDGE` | The strip of plastic between the two holes is too thin to be strong | Reduce finger knuckle width by 1 mm |
| `FINGER HOLES OUTSIDE BODY - INCREASE HAND WIDTH` | The holes for your fingers don't fit inside a body sized for your hand width | Increase hand width (or re-measure both) |
| `PLUG TOO WIDE FOR TOOL END - CHECK PLUG WIDTH` | The end notch came out wider than the tool's end itself | Re-measure plug width — it's probably too large |
| `PLUG SEAT OVERHANGS BODY - RECHECK PLUG WIDTH` / `PLUG POCKET OVERHANGS BODY - RECHECK PLUG WIDTH` | The plug pocket is wider than the tool body at that spot | Re-measure plug width, or go up a size so the body grows |
| `WING OPENING SMALLER THAN STRAP WIDTH` | The wing velcro slot is too narrow to pass the strap you set | Lower `strap_width` (Step 3), or switch `velcro_style` to `Classic slot` |
| `WING WEB COLLAPSED - NO ROOM FOR STRAP` | Features crowded the wing until no opening is left | Go up a size (bigger body) or lower `strap_width` |
| `ZIP TIE HOLES HIT FINGER HOLES` | A zip row landed too close to a finger hole (with `Auto` placement the rows now derive around the finger holes, so this fires for `Manual` `zip_pos_*` dials or Custom mode with auto-fit off) | Move the offending `zip_pos_*` dial, re-enable auto-fit, or lengthen the body |
| `ZIP TIE ROWS OVERLAP EACH OTHER` | Two manual zip rows landed on top of each other | Spread the `zip_pos_*` dials at least one hole diameter apart |
| `ZIP TIE HOLES HIT VELCRO SLOTS` | A zip row broke into a classic velcro slot | Move `zip_pos_*` or `velcro_pos` apart (Step 3) |
| `SEAT HAS NO RECESS - PLUG WONT NEST` / `POCKET HAS NO RECESS - PLUG WONT NEST` / `SEAT FLOOR TOO THIN TO PRINT` / `POCKET FLOOR TOO THIN TO PRINT` / `ZIP TIE GRID BELOW CORD END` / `ZIP TIE GRID OUTSIDE BODY` / anything else | An internal geometry check — with measured inputs this shouldn't happen | Re-check all numbers against the [Measuring Guide](measuring-guide.md); if it persists, open an issue with your numbers |
| `FINGER HOLES OUTSIDE BODY` / `POCKET SEAT WIDER THAN TOP EDGE` / `POCKET WIDER THAN BODY` / `WALL NOTCH WIDER THAN TOP EDGE` | `size = Custom` only: the Custom-mode wording of the finger-hole, seat, pocket and notch checks above | Adjust the custom sliders of that feature (finger holes, pocket seat, pocket or wall notch), or turn `custom_enable_auto_fit` back on |

Preview-only notes (never in the exported file):

| Note says | What it means | What to do |
| --------- | ------------- | ---------- |
| A **green** `MEDIUM: …` / `MEASURED: …` tag | Not a warning! Positive confirmation that your size and numbers were applied | Nothing |
| Orange `CUSTOM SLIDERS IGNORED - SET SIZE = CUSTOM` | A `custom_*` slider was moved while a non-Custom size is active; the console names each one | Set Step 2's `size = Custom` if you meant it, or leave the slider alone |
| Orange `AUTO-FIT ADJUSTED <n> VALUES - SEE CONSOLE` | `size = Custom` with auto-fit on: <n> sliders were clamped to keep the part printable | Read the console's `(clamped from …)` lines |

### Two-sided puller tags

These appear only in the two-sided puller, `src/Plug_Puller_Two_Sided.scad`:

| Tag says | What it means | What to do |
| -------- | ------------- | ---------- |
| `CORD TOO THICK FOR CABLE CHANNEL` | The cord won't fit the channel with clearance | Re-measure the cord thickness, or raise `plate_cable_clearance` |
| `PLUG TOO WIDE - ARMS BULGE PAST FINGER LOBES` | The plug is so wide the tapered arms would bulge wider than the finger lobes | Re-check plug width; a truly huge plug may exceed this tool |
| `NO GRIP BITE - PLUG WONT BE HELD` | `Flat sides` or the plug preset: `plate_grip_bite` is ≥ 0, so the arms don't squeeze | Set `plate_grip_bite` negative (e.g. −1) so the arms bite the plug |
| `PLATE THINNER THAN 2MM - TOO FLIMSY` | `plate_thickness` is under 2 mm | Raise `plate_thickness` to 3–5 mm |
| `ZIP STATION OFF THE ARM` | A manual zip position fell past the arm | Bring `plate_zip_pos_*` back within the arm length |
| `ZIP STATIONS OVERLAP EACH OTHER` | Two manual zip positions landed on top of each other | Spread `plate_zip_pos_*` at least one hole diameter apart |
| `ZIP STATION HITS VELCRO SLOT` | `Manual` placement only: a zip position broke into the velcro slot | Move `plate_zip_pos_2/3` — in `Auto` placement the slot always keeps clear of the stations |
| `PLUG TOO LONG - PLATE OVER 120MM, CHECK PLUG LENGTH` | The arms grow with the plug, and this plug length pushed the plate past 120 mm | Re-measure plug length (from the surface it plugs into to the plug's back end — not including the cord) |
| `PLUG WIDTH TAPER LOOKS WRONG - RECHECK BOTH ENDS` | The two width measurements are more than ~20° of taper apart — almost certainly a mis-measurement | Re-measure plug width at the prong end and at the cord end |
| `STEP 3 DISABLED ZIP HOLES - NOTHING SECURES THE TWO PLATES TOGETHER` | The zip-tie stations are gone, but zip ties are what cinch the two plates together. Both Step 3 choices keep them, so you should not see this | Set Step 3 to `Zip ties` or `Zip ties + Velcro strap` |
| `STRAP WIDER THAN ARM SLOT WINDOW - NARROW THE STRAP` | `Manual` placement only: your `strap_width` is wider than the slot length the arm can offer between the zip stations | Use a narrower strap, or raise `plate_velcro_slot_length` / rearrange `plate_zip_pos_*` to widen the window |
| `PLUG NARROWER THAN THE CORD CHANNEL - ARMS CANNOT TOUCH IT` | At one end the plug is narrower than the cord channel, so the arms cannot reach it there | Re-measure the plug widths and the cord — the cord itself, not its strain relief; a smaller `plate_cable_clearance` narrows the channel |
| `CRADLE SHALLOWER THAN ASKED - PLUG NARROW` | `Rounded sides`: the plug is so narrow next to its cord channel that the full cradle would make the gap at the outer face narrower than the cord channel, so the cradle was built shallower | A smaller `plate_cradle_depth`, or measure the cord itself, not its strain relief |
| Orange `STRAP SLOT LEFT OUT - PLUG TOO SHORT FOR ONE` (preview only) | `Auto` placement: the plug is too short for a strap slot in the arms, so it was left out; the zip ties still hold the plates | Nothing to fix; pick `Zip ties` in Step 3 and the note goes away |

> **Two-sided puller feels too flimsy?** Raise `plate_wall_boost` (the
> first slider in the **Advanced - Two-Sided Puller** section): it
> thickens **every** wall around the inner openings at once —
> finger-hole walls, the cord-channel web, both velcro-slot walls, and
> the zip-tie webs — while the automatic placement keeps all the holes
> clear of each other. For just the wall between the gripper teeth and
> the velcro slot, raise `plate_slot_inner_wall`. More plate dials: the
> [Power User Guide](power-user-guide.md).

## Printing problems (not fit problems)

| Symptom | Cause | Fix |
| ------- | ----- | --- |
| Slicer complains about floating/disconnected parts | You exported with a red warning tag present — the tag is a separate object | Fix the named measurement first; a clean one-sided export has exactly one body |
| Slicer shows two separate parts in a two-sided puller file | That is the design: `Both plates` puts the two plates side by side in one file | Print both; if the slicer asks, let it split them into separate objects |
| Layers split at the pocket floor | Under-extrusion or too few walls | 3–4 walls, 25 %+ infill; see the [README printing tips](../../README.md#3d-printing-tips) |
| Tool snapped at the hook while pulling | Printed in a brittle material or too-thin walls | Reprint in PETG with 4 walls (two-sided puller: raise `plate_wall_boost` and/or `plate_thickness`) |

## Still stuck?

Re-do the 5-minute [Measuring Guide](measuring-guide.md) from scratch —
most stubborn misfits trace back to one mis-read number. If the fit
still fails after two nudges, open a GitHub issue with your inputs and
a photo of the tool on the plug; that's exactly the feedback that
improves the fit formulas for everyone.
