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
