# Ready-to-print STL library

Pre-rendered, watertight STLs for every default configuration — no OpenSCAD or
Customizer needed. Pick the file that matches your plug and hand and print it.

Everything here is generated from source by
[`scripts/build_release_stls.py`](../scripts/build_release_stls.py); do not edit
the STLs by hand. Re-run that script and commit the result after any intentional
model change (the shipped files are guarded by `tests/test_shipped_stls.py`).

```
stl/
  Plug-Puller/                 # 9 tools: 3 plug families x 3 hand sizes
  Measuring-Stencil/
    Visual/                    # debossed printed labels (8 files)
    Tactile/                   # raised ADA characters + braille (8 files)
```

## Plug-Puller/

Pick your **plug family**, then your **hand size** — `Small` / `Medium` /
`Large`. Medium is the reference device (start there); Small ≈ 5th-percentile
female hand, Large ≈ 95th-percentile male hand.

| Plug family | File pattern | Tool type |
| ----------- | ------------ | --------- |
| Flat 2-prong lamp — NEMA 1-15 | `Plug-Puller_Flat-2-Prong-Lamp-NEMA-1-15_{Small,Medium,Large}.stl` | flat tool (one part) |
| Standard 3-prong — NEMA 5-15 | `Plug-Puller_Standard-3-Prong-NEMA-5-15_{Small,Medium,Large}.stl` | flat tool (one part) |
| Heavy-duty round cord — NEMA 5-15 | `Plug-Puller_Heavy-Duty-Cord-NEMA-5-15_Clamshell-Plate_{Small,Medium,Large}.stl` | clamshell **plate** |

> **Clamshell tools take two plates.** Each heavy-duty file is a single plate.
> Print it **twice**, flip one over, and zip-tie the two together around the plug.

Not sure which plug you have, or which size fits? Print a
[1:1 paper outline sheet](../docs/guides/print-preview-outlines.md) or the
measuring stencil below first.

## Measuring-Stencil/

Thin measuring cards that answer the fit worksheet without a caliper. Print the
full packed set (`..._All-Cards.stl`) or just the one card you need. Two label
modes — pick **`Visual/`** for debossed printed text, or **`Tactile/`** for
raised ADA-size characters plus a fold-flat Grade 2 braille flap on every card
(see the [Starter Guide](../docs/guides/starter-guide.md#tactile-version-raised-characters--braille)).

| Card | Purpose |
| ---- | ------- |
| `All-Cards` | the full packed set — every card on one plate |
| `P1_Lamp-Plug-Gauge` | flat 2-prong lamp plug silhouette (NEMA 1-15) |
| `P2_Standard-3-Prong-Gauge` | standard 3-prong plug silhouette (NEMA 5-15) |
| `P3_Heavy-Duty-Cord-Gauge` | heavy-duty round cord silhouette (NEMA 5-15) |
| `R1_Ruler-100mm` | a tactile 100 mm ruler |
| `C1_Cord-Gauge` | open-slot cord gauge that slides onto an installed cord |
| `F1_Finger-Sizing-15-25mm` | finger-sizing holes Ø 15–25 mm |
| `F2_Finger-Sizing-26-32mm` | finger-sizing holes Ø 26–32 mm |
