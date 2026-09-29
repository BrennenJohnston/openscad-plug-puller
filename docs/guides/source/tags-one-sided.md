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
| `SEAT HAS NO RECESS - PLUG WONT NEST`, `POCKET HAS NO RECESS - PLUG WONT NEST` | An internal geometry check; with measured numbers it should not happen | Check every number against the measuring guide; if it persists, open an issue with your numbers |
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
