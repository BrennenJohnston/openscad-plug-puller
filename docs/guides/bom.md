# Bill of materials

Nothing to solder and almost nothing to buy: filament, zip ties, and a strap if you want one. The measuring stencil is printed, not bought.

| Item | How many | Size | Where it goes |
| ---- | -------- | ---- | -------------- |
| Zip ties, one-sided puller | 2 per tool | up to 4.8 mm wide, about 200 mm long | the zip-tie holes beside the pocket, 5.08 mm across |
| Zip ties, two-sided puller | 3 per pair of plates | up to 3.6 mm wide, about 200 mm long | the zip-tie stations, 4 mm across |
| Hook-and-loop strap | 1 per tool, optional | 10, 13, 16, 20 or 25 mm wide | the two wing openings of the one-sided puller |
| Filament | see the table below | PETG, or PLA | the tool |
| A printer | 1 | a bed of 200 by 200 mm or larger for the stencil sheets | the tool, the stencil cards |
| Measuring stencil | 1 set | printed from `stl/Measuring-Stencil/` | matching a plug and sizing a finger |

About the strap: ONE-WRAP ties come in 10, 13, 16, 20 and 25 mm widths. Set the `strap_width` dial to the width you bought; its default of 15 mm is not a ONE-WRAP size, so change it. A narrower bed still prints the stencil one card at a time.

## Filament per tool

The numbers below are upper bounds: they are the solid volume of each shipped STL (from `stl/Plug-Puller/`, measured with trimesh) times 1.27 g per cubic centimeter for PETG. A print at 25 to 35 percent infill uses less. A two-sided file holds both plates.

| Tool and plug                                      | Small  | Medium | Large  |
| -------------------------------------------------- | ------ | ------ | ------ |
| One-sided, USB-C laptop tip                        | 12.4 g | 16.8 g | 21.3 g |
| One-sided, flat 2-prong lamp plug                  | 11.6 g | 15.9 g | 19.6 g |
| One-sided, wide 2-prong appliance plug             | 15.2 g | 21.3 g | 26.8 g |
| Two-sided, standard 3-prong plug (both plates)     | 17.5 g | 19.7 g | 21.6 g |
| Two-sided, heavy-duty extension cord (both plates) | 17.0 g | 19.2 g | 21.2 g |

The solid volumes behind these grams: one-sided USB-C 9.75, 13.25 and 16.78 cubic centimeters; one-sided lamp 9.12, 12.52 and 15.43; one-sided wide appliance 11.99, 16.81 and 21.11; two-sided standard 13.75, 15.48 and 16.98; two-sided heavy-duty cord 13.35, 15.15 and 16.70. A custom tool lands near the preset closest to its plug. For PLA multiply the grams by 0.98.
