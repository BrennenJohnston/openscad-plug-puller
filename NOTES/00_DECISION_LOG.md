# Decision log

One entry per decision that shaped the package, newest last. "Decided by" names who settled it: the owner (Brennen Johnston), the writer, or a rule already in force. A decision the owner has not yet confirmed says so. Decisions from before this record began are summarized from the changelog and the owner's answers as they were given.

## 2026-09-30, the MakerWorld license

- D1. MakerWorld downloads use Creative Commons Attribution-NonCommercial-ShareAlike 4.0, the listing license closest to the repository's PolyForm Noncommercial 1.0.0; the repository itself stays PolyForm Noncommercial. Offered and declined: staying off MakerWorld, with the Assistive Forge link as the only no-install path. Decided by the owner.

## 2026-10-08, the preset refit and the document package

- D2. The two-sided gap keeps the plug's prong-end width along a new head length, and every preset is re-measured with a caliper on its own plug; the presets of version 0.14.0 had come from development sample plugs and held loosely. Decided by the owner.
- D3. The standard 3-prong plug's length is 46.1 mm, the whole-plug measurement; its three sections, which add to 50.9 mm, are scaled to fit. Decided by the owner.
- D4. The heavy-duty extension cord keeps Flat sides and the grip bite; its prong-end width is the widest measurement, 26.56 mm. Decided by the owner.
- D5. The Open AT document set is added beside the code layout: new `Documentation/`, `Photos/`, `MakerWorld_Photos/`, `LICENSES/`, `NOTES/` and `CHANGES.txt`; `src/`, `dist/`, `stl/` and `docs/` stay where they are. Decided by the owner.
- D6. Makers Making Change is asked first whether PolyForm Noncommercial qualifies; relicensing is planned only if they refuse. Decided by the owner; the question is drafted, not yet sent.
- D7. The full Open AT document set: three Step 1 guides, three editions of the assembly guide, the User Guide, the Device Summary, the Design Rationale, the bill of materials and the listing. Decided by the owner.

## 2026-10-11, numbers the owner could not measure

- D8. The lamp plug's thicknesses, 18.6 and 8.6 mm, and its cord's thin side, 3.6 mm, stay the development sample plug's, marked as estimates; a thickness only sets the one-sided pocket's recess, so an error moves the pocket floor well under a millimeter. Decided by the owner ("Proceed with best guess").
- D9. The standard plug's 9.25 mm cord rides past the one-sided cord slider's 9 mm; the slider stays. (The standard plug has since moved to the two-sided puller, D11.) Decided by the owner.
- D10. The owner slices the Medium presets later for the print times; the bill of materials and the listing leave the times open until then. Decided by the owner.

## 2026-10-27, the preset split and version 1.0.0

- D11. The line between the tools is the prong count. The one-sided puller carries the 2-prong plugs and the USB-C tip (presets: USB-C laptop tip, flat 2-prong lamp plug, wide 2-prong appliance plug); the two-sided puller carries the 3-prong plugs (standard 3-prong plug, heavy-duty extension cord) and any plug 24 mm thick or more. No preset is in both. Offered: keeping only the heavy-duty preset on the two-sided puller. The owner named the two 3-prong plugs as the heavy-duty pair and asked the writer to judge the line; the writer chose the prong count because counting needs no ruler and the test prints split exactly there. Decided by the owner and the writer.
- D12. The October test prints: the one-sided puller held every 2-prong plug well and 3-prong plugs slipped out; the two-sided puller held both 3-prong plugs well and every 2-prong plug and the USB-C tip fell out however tight the ties were pulled. The owner's reading: slick PLA on a slick USB-C tip, and the curved sides of a 2-prong plug, give the teeth too little to grip, while a 3-prong plug's straight sides meet them along their whole length. Reported by the owner.
- D13. The release is 1.0.0: the preset split, the USB-C one-sided preset and the document set together; the "public preview" wording retires. Offered: 0.15.0, keeping 1.0.0 for after the Makers Making Change submission. Decided by the owner.
- D14. The USB-C tip's thickness, which the owner's measurements did not include, is 6.5 mm at both ends, the USB Type-C specification's largest recommended overmold thickness, so the estimate errs thick; marked as an estimate. Decided by the writer, from the owner's "attempt ... based on the measurements provided".
- D15. The USB-C laptop tip preset also sets the wall plate style to No plate / flush: a laptop or charger has no cover plate. Decided by the writer.
- D16. The one-sided upload file is renamed `Plug_Puller_One_Sided_SingleFile.scad`, so the two customizer files are told apart by name on MakerWorld and in the browser; the desktop files in `src/` keep their names. Decided by the owner.
- D17. A one-page plug size finder, every preset of both tools at true size by tool with a 50 mm calibration square, replaces the paper stencil sheet's plug row; the stencil sheet keeps the square, the ruler and the finger circles. The printed stencil's P1 to P4 cards are unchanged, P2 and P3 now name the two-sided puller, and the USB-C tip gets no card. The measuring form opens with a Start here box: the prong count and the closest finder outline. Decided by the writer, from the owner's request.
- D18. Every guide teaches the two-sided assembly in the order of the October photographs: the plug on the first plate, the second plate on top, then each tie through both plates and across the plug. Offered: the July written order, the ties through one side first. Decided by the owner.
- D19. The guide and listing photographs of the two-sided puller come only from the October series' standard and heavy-duty plugs, the larger plugs; the one-sided puller keeps its July photographs on the lamp plug. Decided by the owner.
- D20. The printed tool is the custom part, so its print settings live once, in the Maker Guide's print table, and the Step 1 guides point there. The Visual Assembly Guide's panels are the October photographs, without drawn arrows or parts boxes. Decided by the writer, from the template.

## Fixed vocabulary (DRAFT until signed)

- one-sided puller: the one-part tool for plugs with 2 prongs and USB-C tips.
- two-sided puller: the tool of two plates for plugs with 3 prongs.
- plate: one of the two identical parts of the two-sided puller.
- prong end, cord end: the two ends of a plug, where it is measured.
- head: the part of a plug behind its prongs that keeps the prong-end width.
- arms, teeth: the two-sided plate's two toothed extensions and the rows of small rounded bumps on their inner edges.
- finger holes: the two round holes the pull is made with, on both tools.
- cord channel: the slot between a plate's finger holes where the cord lies.
- pocket, wall notch, cord hook, wing openings, zip-tie holes: the one-sided puller's features.
- strap slot: the long slot in each arm of a plate, for an optional strap.
- Rounded sides, Flat sides: the two-sided puller's plug-sides setting.
- Never used: heavy-duty for a tool (it names a plug only); flat tool; clamshell; shell.
