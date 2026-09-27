# Bill of materials

Nothing to solder and almost nothing to buy: filament, zip ties, and a strap if you want one. The measuring stencil is printed, not bought.

| Item | How many | Size | Where it goes |
|---|---|---|---|
| Zip ties, one-sided puller | 2 per tool | up to 4.8 mm wide, about 200 mm long | the zip-tie holes beside the pocket, 5.08 mm across |
| Zip ties, two-sided puller | 3 per pair of plates | up to 3.6 mm wide, about 200 mm long | the zip-tie stations, 4 mm across |
| Hook-and-loop strap | 1 per tool, optional | 10, 13, 16, 20 or 25 mm wide | the two wing openings of the one-sided puller |
| Filament | see the table below | PETG, or PLA | the tool |
| A printer | 1 | a bed of 200 by 200 mm or larger for the stencil sheets | the tool, the stencil cards |
| Measuring stencil | 1 set | printed from `stl/Measuring-Stencil/` | matching a plug and sizing a finger |

About the strap: ONE-WRAP ties come in 10, 13, 16, 20 and 25 mm widths. Set the `strap_width` dial to the width you bought; its default of 15 mm is not a ONE-WRAP size, so change it. A narrower bed still prints the stencil one card at a time.

## Filament per tool

The numbers below are upper bounds: they are the solid volume of each shipped STL (from `stl/Plug-Puller/`, measured with trimesh) times 1.27 g per cubic centimeter for PETG. A print at 25 to 35 percent infill uses less. A two-sided file holds both plates.

| Tool and plug | Small | Medium | Large |
|---|---|---|---|
| One-sided, flat 2-prong lamp plug | 12.0 g | 17.0 g | 21.2 g |
| One-sided, standard 3-prong plug | 16.7 g | 23.8 g | 30.1 g |
| One-sided, wide 2-prong appliance plug | 15.2 g | 21.3 g | 26.8 g |
| Two-sided, heavy-duty extension cord (both plates) | 15.0 g | 17.1 g | 19.0 g |
| Two-sided, USB-C laptop tip (both plates) | 13.0 g | 14.8 g | 16.4 g |
| Two-sided, flat 2-prong lamp plug (both plates) | 15.4 g | 17.5 g | 19.4 g |
| Two-sided, standard 3-prong plug (both plates) | 17.4 g | 19.6 g | 21.8 g |

The solid volumes behind these grams: one-sided lamp 9.48, 13.36 and 16.66 cubic centimeters; one-sided standard 13.13, 18.70 and 23.69; one-sided wide appliance 11.99, 16.81 and 21.11; two-sided heavy-duty cord 11.83, 13.49 and 14.94; two-sided USB-C 10.21, 11.66 and 12.94; two-sided lamp 12.12, 13.82 and 15.30; two-sided standard 13.69, 15.41 and 17.13. A custom tool lands near the preset closest to its plug. For PLA multiply the grams by 0.98.
