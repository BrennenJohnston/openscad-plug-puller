# Device Summary

The Plug Puller, version 1.0.0, in one place: what it is, who it is for, what is in it, its sizes, what changed, and where the files are.

## 1. What it is and who it is for

The Plug Puller is a 3D-printed tool for pulling an electrical plug out of an outlet with the whole hand instead of a fingertip pinch: two fingers go through two finger holes and pull straight back, and the tool touches only the plug's sides and back, never the outlet. It is for anyone who cannot grip a plug and pull it: arthritis, low grip strength, tremor, a small hand, one hand. The person who uses it, or someone for them, measures the plug and the hand, or picks a preset, and a customizer makes the tool for both.

## 2. How it works

The tool stays on its plug. Two finger holes take the pull, so the whole hand does the work, and a straight pull away from the outlet brings the plug out. It comes as two tools, each its own customizer file:

- the one-sided puller, one printed part with a pocket the plug lies in, a cord hook and zip-tie holes or strap openings, for plugs with 2 prongs and USB-C tips;
- the two-sided puller, two identical printed plates with toothed arms, zip-tied face to face around the plug, for plugs with 3 prongs and any plug 24 mm thick or more.

The split follows test prints: the one-sided puller held every 2-prong plug and let 3-prong plugs slip out; the two-sided plates held 3-prong plugs and let 2-prong plugs and a USB-C tip slip out.

## 3. What is in the kit

| Part | How many | What it is |
|---|---|---|
| One-sided puller | 1 | printed, made for the plug and the hand |
| Two-sided plate | 2, identical | printed, made for the plug and the hand; both in one file |
| Zip ties | 2 for the one-sided puller, 3 for the two-sided | bought; up to 4.8 mm wide (one-sided) or 3.6 mm (two-sided), about 200 mm long |
| Hook-and-loop strap | 1, optional | bought; 10 to 25 mm wide, one-sided puller only |
| Measuring stencil | 1 set, optional | printed cards for matching a plug and sizing a finger |

One tool is made per plug: a person with a 2-prong lamp plug and a 3-prong extension cord makes one of each. The plug presets: USB-C laptop tip, flat 2-prong lamp plug and wide 2-prong appliance plug (one-sided); standard 3-prong plug and heavy-duty extension cord (two-sided). Any other plug is measured.

## 4. Specifications

| What | Value |
|---|---|
| One-sided puller at Medium | about 72 by 71 by 6.3 mm |
| Two-sided plate at Medium | about 68 by 76 by 4 mm each, standard 3-prong plug |
| Hand sizes | Small, Medium, Large, or measured; finger holes 17.5 to 28.4 mm across at the three sizes |
| Plugs | 12 to 85 mm long, 5 to 40 mm wide; one-sided up to 24 mm thick |
| Filament per tool | about 12 to 27 g, an upper bound from the solid volume |
| Material | PETG suggested; PLA works |
| Electronics, fasteners, springs | none |

## 5. What changed from version 0.14.0

- The presets are split by the prong count: the one-sided puller carries the 2-prong plugs and a new USB-C laptop tip preset, the two-sided puller the 3-prong plugs; each preset was measured with a caliper on its own plug.
- The two-sided gap keeps the plug's prong-end width along its head, so a plug with a wide head is gripped along its whole side.
- The one-sided upload file is now `Plug_Puller_One_Sided_SingleFile.scad`, so the two files are told apart by name.
- A one-page plug size finder shows every preset at true size; the measuring form starts with the prong count.
- The document set follows the Makers Making Change Open AT layout: the Step 1, Step 2 and Step 3 guides, this summary, the design rationale and the bill of materials.

The full history is in [`CHANGELOG.md`](../CHANGELOG.md).

## 6. Cost and print time

The filament for one tool costs about $0.20 to $0.45 at $15.99 per kg, the replacement-spool price used for the owner's other projects in October 2026; the masses are upper bounds from the solid volume of each shipped STL, and a print at 25 to 35 % infill uses less. The zip ties and the strap come from any hardware store. Print times have not been measured on a sliced project yet.

## 7. Licenses

The design, the documents, the pictures and the scripts are under the [PolyForm Noncommercial License 1.0.0](../LICENSES/PolyForm-Noncommercial-1.0.0.txt): personal, hobby, educational, research and other noncommercial use is permitted. Downloads from MakerWorld are under Creative Commons Attribution-NonCommercial-ShareAlike 4.0, the listing license closest to it.

## 8. Where the files are

- The guides and this summary: [`Documentation/`](README.md).
- The customizer files: `src/` for the desktop program, `dist/` as single files for MakerWorld and the browser.
- The ready-made STLs: [`stl/`](../stl/README.md).
- The repository: <https://github.com/BrennenJohnston/openscad-plug-puller>
