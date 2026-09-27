# Design rationale

Every default in the two files has a reason. This page gives each one in the same shape: the decision, the number, the evidence, and what happens if you change it. The numbers come from the files named beside them.

## The 24 mm split between the two tools

**The decision.** A plug up to 24 mm thick gets the one-sided puller; a thicker plug gets the two-sided puller.

**The number.** 24 mm, from `docs/Plug_Puller_Reference.md` section 1 and the W-20 check in `src/Plug_Puller_Parametric.scad`.

**The evidence.** The one-sided puller holds the plug in a pocket cut into a slab 6.35 mm thick at Medium (`README.md`, Sizes); the pocket's side walls and the zip ties do the holding, from one side only. The two-sided plates close across the plug from both sides, so the plug's thickness sets their gap instead of limiting them. The reference states the 24 mm rule and the tag; it does not state how the number was chosen, and this page does not guess.

**What you may change.** Nothing here is a dial. If you type a thickness of 24 mm or more into the one-sided file it prints the red tag `PLUG THICKER THAN 24MM - USE THE TWO-SIDED PULLER FILE` beside the part and the part is still built, so you can see it, but it will not hold that plug.

## Three sizes from measured hands

**The decision.** `Small`, `Medium` and `Large` are hand sizes, not tool sizes: each sets a finger width and a hand width, and the finger holes and the body follow.

**The numbers.** Finger and hand width: Small 16.5 and 72 mm, Medium 20 and 85 mm, Large 23 and 96 mm, in `src/fit_sizes.scad`. The finger holes come out at 17.5, 21 and 24 mm across in the two-sided puller (`docs/Plug_Puller_Reference.md` section 2).

**The evidence.** The pairs come from the ANSUR II (2012) hand breadth survey and Rogers (2008) knuckle breadth, as `README.md` (Sizes) states: Small is about a 5th-percentile female hand, Large about a 95th-percentile male hand, and Medium is the reference device the owner printed and tested. The reference does not state the exact percentile behind each number beyond that.

**What you may change.** `Measure my hand` replaces the pair with your own two numbers and everything follows. A finger hole is sized to the knuckle, so a hole that is too tight pinches and one that is too loose lets the finger slip: measure at the widest knuckle, as the [Measuring Guide](measuring-guide.md) shows.

## The two-sided cradle and the bite

**The decision.** The two-sided plates grip a plug in one of two ways: `Rounded sides` cuts a sloped cradle into each arm; `Flat sides` keeps the arms straight and squeezes.

**The numbers.** `plate_cradle_depth` 2.5 mm per side and `plate_grip_clearance` 0.5 mm for `Rounded sides`; `plate_grip_bite` of minus 1 mm for `Flat sides` and the presets. All three are dials in `src/Plug_Puller_Two_Sided.scad`; the geometry is in `docs/Plug_Puller_Reference.md` section 6.1.

**The evidence.** Stacked, the two cradles form a diamond-shaped channel that is widest where the plates meet and 2.5 mm narrower per side at the outer faces, so a round or oval plug rests on four sloped faces and centers itself; the half millimeter of clearance lets a hard plug drop in flat and forgives a small measuring error. A boxy plug has no curve to center on, so the arms stay straight and close 1 mm tighter than the plug on each side: the teeth bite and the plates cannot slide.

**What you may change.** A deeper cradle is steeper; the file will not let it go below the cord channel's width and says so with the tag `CRADLE SHALLOWER THAN ASKED - PLUG NARROW`. A bite of zero or more means the arms never squeeze a flat-sided plug, and the tag `NO GRIP BITE - PLUG WONT BE HELD` appears.

## PETG

**The decision.** PETG is the recommended filament; PLA, ABS and ASA work; flexible filament does not.

**The evidence.** `README.md` (3D printing tips) and `docs/makerworld-listing.md` (print settings): the cord hook and the finger holes flex a little on every pull, and PETG takes that repeated flexing without cracking where PLA can; it also shrugs off the warmth near a misbehaving outlet. A flexible filament bends instead of pulling.

**What you may change.** The material is your slicer's choice, not the file's. Whatever you print in, 3 to 4 walls keep the hook and the zip-tie holes strong (the [Fit Troubleshooting guide](fit-troubleshooting.md) names a snapped hook as the sign of too few walls).

## Red tags as error messages you can hold

**The decision.** When a number cannot work, the file does not stop: it builds the part and lays red text beside it that names the measurement to fix, as real geometry.

**The evidence.** `docs/Plug_Puller_Reference.md` section 10 lists the twenty one-sided checks (W-1 to W-20) and the thirteen two-sided checks (WC-1 to WC-13). The tag is geometry because the customizer on MakerWorld shows only the finished model: a message that lived only in a text pane would be invisible there. A red coupon in the preview, and on the bed if you export anyway, cannot be missed by anyone.

**What you may change.** Nothing turns the tags off. Fix the number and the tag goes away; the [Fit Troubleshooting guide](fit-troubleshooting.md) decodes every one.

## The see-through plug in the preview

**The decision.** Both files draw a translucent plug in the pocket or between the arms while you customize, and leave it out of the export.

**The evidence.** `docs/Plug_Puller_Reference.md` sections 5.5 and 10: the plug is drawn from your numbers, so if it looks wrong on the screen, the numbers are wrong. It never reaches the STL.

**What you may change.** `show_plug_preview` turns it off; nothing else changes.

## Measured presets only

**The decision.** A plug preset exists only for a plug the owner measured at two stations, the prong end and the cord end; there are no presets typed from a catalog.

**The evidence.** `docs/Plug_Puller_Reference.md` section 2.1: only the prongs of a plug are standardized, not the body, so two plugs that fit the same outlet can differ by millimeters in every dimension that matters here. Each preset carries the length, both widths, both thicknesses and the cord of one measured plug, taken just behind the prongs and where the cord leaves the body.

**What you may change.** `Measure my plug` with your own six numbers is always the safer choice for a plug that is not on the list; the outline sheets and the stencil cards let you check before you print.

## Print settings as text

**The decision.** Every print setting is written out in words (the [Maker Guide](maker-guide.md), section 4), never only in a slicer profile or a screenshot.

**The evidence.** The Accessible MakerWorld Documentation Standard, section 2 (its canonical evidence library), copied here as it stands:

> **Ballarin, Stangl, Oswal, Whiting — "A Framework-Informed Analysis of
> Accessibility Barriers in Desktop 3D Printing Software," DIS 2025 Companion,
> pp. 477–482.** DOI
> [10.1145/3715668.3736342](https://doi.org/10.1145/3715668.3736342)
>
> Why it matters: measured with NVDA that Cura, PrusaSlicer, and Bambu Studio
> hide much of their interface from the accessibility APIs screen readers use —
> print settings unreachable, controls unlabelled, print errors unannounced.
> This is why a listing must state print settings **as text** and why a
> ready-sliced print profile is an accessibility feature: it removes a step the
> user may not be able to complete.

**What you may change.** The settings are a starting point; a stiffer print (more walls) never hurts this tool.
