## Advanced settings

Everything below Step 4 in the Customizer is optional. The **Advanced - Two-Sided Puller** section holds the plate dials, which work with your measured sizes and apply in every hand size; there is no Custom size in this file. Every one of these dials is described, with a picture, earlier in this guide.

### How the plate is sized

The plate takes its main sizes from Step 1. The arm's gripping edge follows the plug's own two widths, the prong-end width at the arm tips and the cord-end width at the plug's back end, blended in between. The arms grow so they always cover the whole plug length. The throat, where the gap closes down to the cord channel, sits just below the plug's back end. The cord channel comes from the cord thickness, and the finger holes from the Step 2 hand size. The plate dials tune that result; their defaults carry the field-tested grip: 2 mm teeth on a 2.8 mm pitch biting 1 mm deep, a grip bite of −1, with the toothed zone set automatically to the whole plug body.

Step 3's attachment offers Zip ties + Velcro strap (the default) and Zip ties. The three zip-tie stations per arm are always there, because the ties are what cinch the two plates together; the strap slot in each arm comes with the strap choice. The strap width sets the slot's length so the strap always threads through. In Auto placement, a plug too short for a slot gets none, with the orange preview note `STRAP SLOT LEFT OUT - PLUG TOO SHORT FOR ONE`.

### Rounded or flat sides: the cradle

Step 1's plug sides choice picks how the arms meet the plug. **Rounded sides**, the default, builds a sloped cradle: the gap between the arms is narrower at each plate's outer face than where the plates meet, by the cradle depth per side (2.5 mm by default, so the gap narrows by 5 mm), and the grip clearance (0.5 mm) is the extra room where the plates meet, so a hard plug drops in flat and the cradle does the holding. Stacked face to face, the two plates form a diamond-shaped channel that centers a round plug, a USB-C tip or a charger tip. The teeth follow the slope.

The cradle never makes the outer-face gap narrower than the cord channel. When a narrow plug would need that, the file builds a shallower cradle and shows `CRADLE SHALLOWER THAN ASKED - PLUG NARROW`; a smaller cradle depth, or measuring the cord itself rather than its strain relief, clears it.

**Flat sides** keeps the straight toothed edge, and there the grip bite sets the squeeze. The cradle depth and the grip clearance apply to Rounded sides only; the grip bite applies to Flat sides and to the plug presets, which carry their own tested grip.

### Print layout

Step 4's print layout is Both plates by default: the two identical plates side by side in one file, 8 mm apart at their widest points, so one export prints the whole tool. One plate exports a single plate. Either way, flip one plate over after printing and zip-tie the pair face to face around the plug.

### Strength

| Goal | Dial |
| ---- | ---- |
| A denser, stronger plate all around | Extra wall on the plate: every wall around the inner openings grows by that much; the holes move with it |
| A stiffer sandwich | Plate thickness (each plate; the pair is twice that) |
| A thicker wall between the teeth and the strap slot only | Wall between the teeth and the slot, measured from the deepest tooth bite, so bigger teeth never silently thin it |
| Less plastic | A wider or longer strap slot (the slots double as material reduction), or a cable strip thickness of 0 |

### Grip

| Goal | Dial |
| ---- | ---- |
| A steeper or gentler cradle (Rounded sides) | Cradle depth, per side; 0 is a straight edge |
| More or less room where the plates meet (Rounded sides) | Grip clearance, in total, not per side |
| Squeeze harder or looser (Flat sides and the presets) | Grip bite; negative squeezes, applied per side on top of the plug's own widths |
| Teeth that bite a soft plug body | Tooth size, tooth spacing and tooth depth |
| Where the teeth sit | Toothed zone start and toothed zone length, measured back from the arm tips; a length of 0 covers the whole plug body |
| Easier plug entry | Tip flare, which opens the gap at the tips |
| A cord that slides freely | Cord channel clearance |
| Finger security | Finger hole fit: the hole is the finger width plus this |

Manual zip-tie placement, with the three station position dials, trades the collision guarantees for full control; the red tags name a station that falls off the arm, overlaps another, or breaks into the strap slot.

The full list of dials with their ranges, steps and defaults is the machine-readable file [`parameter_mapping_two_sided.json`](../../../parameter_mapping_two_sided.json), checked against the model by the project's tests.

### Guard rails

The model never silently changes your input. Anything truly wrong prints a red warning tag flat on the bed beside the part, so an exported file shows its own defect, and writes the same message to the console. The see-through plug and the orange strap-slot note appear in the preview only and are never exported.
