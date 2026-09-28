### Match a card instead of measuring

The measuring stencil is a set of thin printed cards. Each has a two-letter name raised on its face, so you can find it by touch. Hold your plug in the plug cards: if it fills one card's openings, snug with no big gaps, that card names the preset to pick in Step 1, and you type no numbers at all.

| Card | What it is | What it answers |
| ---- | ---------- | --------------- |
| P1 | The flat 2-prong lamp plug (NEMA 1-15) | the preset `Flat 2-prong lamp plug - NEMA 1-15` |
| P2 | The standard 3-prong plug (NEMA 5-15) | the preset `Standard 3-prong plug - NEMA 5-15` |
| P3 | The heavy-duty extension cord plug (NEMA 5-15) | the two-sided puller's preset `Heavy-duty extension cord - NEMA 5-15` |
| P4 | The wide 2-prong appliance plug (NEMA 1-15) | the one-sided puller's preset `Wide 2-prong appliance plug - NEMA 1-15` |
| R1 | A ruler: raised mm ticks, numbers every 10 mm, and a notch every 10 mm you can count by touch | the plug's length, widths and thicknesses |
| C1 | A cord gauge: open slots 3 to 9 mm wide along one edge, slid onto the cord from the side | the cord thickness: the smallest slot that slips over the cord |
| F1, F2 | Finger holes 15 to 25 mm across (F1) and 26 to 32 mm (F2) | your finger width: the smallest hole your middle finger passes through comfortably, minus 5 |

Each P card has three openings: W for the plug's width, T for its thickness, and an open slot that slides onto the cord. If no card fits, your plug is between presets: measure it instead. The measured tool fits better than any preset.

**Printing the cards.** Print [`stl/Measuring-Stencil/Visual/Measuring-Stencil_Visual_All-Cards.stl`](../../../stl/Measuring-Stencil/Visual/Measuring-Stencil_Visual_All-Cards.stl): 1.2 mm thick cards, no supports, any rigid filament. Or print one card at a time from [`stl/Measuring-Stencil/`](../../../stl/Measuring-Stencil). The cards pack onto sheets for a 200 by 200 mm bed. For a smaller bed, open [`Measuring_Stencil.scad`](../../../Measuring_Stencil.scad) in OpenSCAD, set `bed_width` and `bed_depth` to your bed, and export `part_index` 1, then 2, and so on, one sheet at a time. `part_index` 0 previews every sheet at once; do not print that one.

**The tactile version** ([`stl/Measuring-Stencil/Tactile/`](../../../stl/Measuring-Stencil/Tactile), or `label_mode` set to Tactile in the file) prints every label as a raised character at ADA size and adds a Grade 2 braille title flap to every card. The flap prints leaning back, held by thin fins. Snap the fins off, then fold the flap away from the card until it lies flat, so the braille lands face up beyond the card's edge. Fold once, gently; a PETG or PP hinge folds more reliably than PLA.

**No 3D printer yet?** The last pages of the printed quick start are paper versions of the cards at true size: the plug outlines, a 100 mm ruler and the finger circles. Print them at 100 % (actual size, never fit to page) and check the 50 by 50 mm square with a ruler before you trust them. On their own they are [`stencil-sheet.svg`](../stencil-sheet.svg) and [`stencil-sheet-2.svg`](../stencil-sheet-2.svg).
