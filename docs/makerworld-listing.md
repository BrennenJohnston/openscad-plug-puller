# MakerWorld Listing — Plug Puller

Status: **draft — do not upload.** The licensing decision gate below is
unresolved. Everything else in this document is finished and ready to paste.

Upload files: [`dist/Plug_Puller_SingleFile.scad`](../dist/Plug_Puller_SingleFile.scad)
(the one-sided puller) and
[`dist/Plug_Puller_Two_Sided_SingleFile.scad`](../dist/Plug_Puller_Two_Sided_SingleFile.scad)
(the two-sided puller).

Written to the shared
[Accessible MakerWorld Documentation Standard](https://github.com/BrennenJohnston/accessible-makerworld-doc-standard/blob/main/ACCESSIBLE_MAKERWORLD_DOC_STANDARD.md).

---

## Licensing decision gate — maintainer sign-off required

This repository is licensed **PolyForm Noncommercial 1.0.0**. Publishing to
MakerWorld requires accepting MakerWorld's terms of service, which grant the
platform a license to host, display, and distribute the uploaded model, and
require choosing one of MakerWorld's listing licenses (a Creative Commons variant
or Bambu Lab's Standard Digital File License) for downloaders. That platform grant
sits **alongside** — and for MakerWorld downloads, effectively in front of —
PolyForm NC.

**Decision for the maintainer:**

- **Option A — publish on MakerWorld:** accept the platform grant and pick the
  listing license closest to PolyForm NC's intent (recommended: **CC BY-NC-SA
  4.0** — noncommercial, attribution, share-alike). Downloads via MakerWorld
  follow that CC license; the GitHub repo stays PolyForm NC.
- **Option B — stay playground-only:** skip MakerWorld; the zero-install path
  remains the OpenSCAD Playground link in the README, which serves the file
  straight from this repo under PolyForm NC with no platform grant.

Until Option A is explicitly chosen, **do not upload**.

---

## Upload fields

| Field | Value |
|-------|-------|
| Model title | `Plug Puller - Parametric Assistive Plug Remover (fits YOUR plug and YOUR hand)` |
| Designer | Brennen Johnston |
| Category | Health & Personal Care → Assistive Devices (or Tools → Hand Tools if unavailable) |
| License | Blocked on the gate above. Recommended pick if Option A: **CC BY-NC-SA 4.0**. |
| Upload files | `dist/Plug_Puller_SingleFile.scad` (the one-sided puller) and `dist/Plug_Puller_Two_Sided_SingleFile.scad` (the two-sided puller), each as its own customizable file. Both are generated; see the pre-publish checklist. |
| Tags | `assistive technology`, `accessibility`, `arthritis`, `grip aid`, `plug puller`, `outlet`, `parametric`, `openscad`, `customizer`, `adaptive equipment`, `occupational therapy` |
| External link | <https://github.com/BrennenJohnston/openscad-plug-puller> (source repository) |

## Summary

A handheld assistive tool that helps people with limited grip strength,
arthritis, or small hands remove electrical plugs from wall outlets safely — by
pulling the plug, never the cord. Fully parametric: type a few ruler measurements
into the customizer and get a tool shaped to your exact plug, outlet plate, and
hand. Two tools, two customizable files: a one-sided puller for typical plugs and
a two-sided puller — two plates that zip-tie around the plug — for fat
extension-cord plugs, USB-C tips, and charger plugs.

## Description

*Paste into MakerWorld's description body.*

**What it is**

The Plug Puller grips a plugged-in plug and gives you two large finger holes, so
removing the plug uses your whole hand instead of a fingertip pinch. It touches
only the plug's sides and back — never between the plug face and the wall.

Two tools, each in its own customizable file:

The **one-sided puller** is a single slab with a pocket shaped to your plug, two
finger holes, a J-hook for the cord, and slots for zip ties or a velcro strap.
Slide it over the plug and pull with your whole hand. Print one.

The **two-sided puller** is for fat round extension-cord plugs, USB-C tips, and
charger plugs. Two identical serrated plates grip the plug's sides and zip ties
cinch them together. The download holds **both plates**: print it, flip one
plate over, and zip-tie the pair face to face. If your plug is 24 millimetres or
more thick, the one-sided file shows a red tag sending you here.

**Customize it to your plug and hand — this is the whole point**

Open the **Customize** panel on the file for your tool and work top to bottom.
The sections are numbered and every measurement is in millimetres.

In the one-sided puller:

*Step 1 — Your plug.* Either pick a preset in `plug_preset` — flat 2-prong lamp
plug (NEMA 1-15) or standard 3-prong (NEMA 5-15) — or set it to
`Measure my plug` and type six numbers: plug length, width at the prong end,
width at the cord end, thickness at the prong end, thickness at the cord end,
and cord thickness. Then choose your wall-plate style in
`measure_wall_plate_style` (standard flat plate, Decora rocker, oversized jumbo,
or no plate) so the tool straddles the plate and sits flat against the wall.

*Step 2 — Size.* `size` offers Small, Medium (default), and Large grips, built
from ANSUR II 2012 hand anthropometry spanning roughly the 5th percentile female
to the 95th percentile male. Or set it to `Measure my hand` and type your finger
knuckle width and hand width.

*Step 3 — Attachment.* `attachment` gives you zip-tie holes, velcro strap slots,
both (the default), or none.

*Step 4 — Cord hook.* `hook_hand` is `Right` or `Left`.

In the two-sided puller:

*Step 1 — Your plug.* Pick the heavy-duty extension cord preset, or set
`plug_preset` to `Measure my plug` and type four numbers: plug length, the
plug's width at the prong end and at the cord end (the size the two plates close
across), and cord thickness. Then pick `plug_sides`: `Rounded sides` for a round
plug, a USB-C or charger tip (the plates get a sloped cradle that centers it), or
`Flat sides` for a boxy plug.

*Step 2 — Size.* Small, Medium (default), Large, or `Measure my hand` with your
finger knuckle width.

*Step 3 — Attachment.* Zip ties plus a velcro strap slot in each arm (the
default), or zip ties only. The zip ties hold the two plates together.

*Step 4 — Print layout.* Keep `Both plates`: one download prints the whole tool.

Everything below Step 4 is optional power-user tuning.

**Bad numbers cannot fail silently.** If a measurement is out of range or the
geometry cannot work, the model renders a **red warning tag** naming the
measurement to fix — as actual 3D text in the rendered model, not a console
message. Fix the warning before you export: the red tag is part of the exported
model and would otherwise print as an extra object on your bed. (In the desktop
app's preview, a green tag also confirms which numbers were applied; MakerWorld
renders the finished model only, so it does not show there.)

**Print settings**

- Orientation: flat face down, pocket up; the two-sided puller's plates flat, as
  they lie in the file. No supports.
- Layer height: 0.2 millimetres, or 0.16 for crisper rim fillets.
- Walls: 3 to 4. Infill: 25 to 35 percent, cubic or gyroid.
- Material: **PETG recommended** — it handles repeated flexing and the warmth near
  an outlet better than PLA. PLA, ABS, and ASA all work. **Do not use flexible
  filament**; the tool has to stay rigid to transmit force to the plug.
- Two-sided puller: the file holds **both plates**; flip one after printing and
  zip-tie the pair face to face around the plug.
- The `quality` slider defaults to 64 circle segments, which is print-ready. Drop
  it to 32 for fast test renders and put it back before you export.

**Safety**

The tool grips only the plug body's sides and back face. Nothing is inserted
between the plug and the outlet and no conductive parts are involved. Inspect
prints for cracks before each use and reprint if damaged. For round plugs with
little for the pocket to grip, a zip tie through the attachment holes adds
security.

**Try it before you print**

The source repository has printable 1:1 outline sheets so you can hold a paper
version of the tool against your plug before committing filament, and a printable
**measuring stencil** — a set of thin cards with plug silhouette gauges, a 100
millimetre tactile ruler, a cord-thickness gauge, and eighteen finger-sizing holes.
The stencil lets you find your numbers by matching shapes instead of reading a
ruler, which matters if reading a ruler is the hard part.

The stencil comes in a **tactile version** with raised ADA-size characters and a
**braille title flap on every card**. The braille is generated at build time with
liblouis in UEB Grade 2 and baked into the model, so there is no translation step
for you — the labels are simply there. Note that the measuring stencil is a
separate file in the repository, not part of this MakerWorld model.

**More resources**

The full measuring guide with per-measurement photos, the outline sheets, the
measuring stencil, fit troubleshooting, and the engineering reference are in the
source repository: <https://github.com/BrennenJohnston/openscad-plug-puller>

**Credits**

- Design and code: Brennen Johnston.
- Hand sizing from ANSUR II (2012) and Rogers (2008) anthropometry.
- Tactile stencil labels follow the 2010 ADA Standards §703.2 raised-character
  and §703.3 braille figures; braille translation by the open-source liblouis
  library.

## Print profile notes

There is no `.3mf` to attach — the geometry depends on the user's plug and hand
measurements, so no single sliced profile fits. The settings are stated as text in
the description, which is also the accessible choice: a screen-reader user cannot
read a slicer screenshot, and a 2025 study of Cura, PrusaSlicer, and Bambu Studio
found much of their interfaces invisible to the accessibility APIs screen readers
depend on.

| Setting | Value |
|---------|-------|
| Orientation | flat face down, pocket up |
| Layer height | 0.2 mm (0.16 mm for crisper rim fillets) |
| Walls | 3–4 |
| Infill | 25–35% cubic or gyroid |
| Material | PETG recommended; PLA / ABS / ASA fine; no flexibles |
| Supports | none |
| `quality` | 64 for export, 32 for test renders |

If a print profile is added later, the sensible candidate is the default Medium
one-sided puller with the standard 3-prong preset, and it needs its own photograph
of the actual printed result.

## Gallery plan

1. **Cover — the tool in use on a real outlet.** A hand with fingers through both
   finger holes, tool seated on a plugged-in plug.
   **Alt text:** A printed plug puller seated over a plug in a wall outlet, with a
   hand's fingers through its two large finger holes, ready to pull.

2. **The one-sided puller alone, pocket up.** Three-quarter view showing the plug pocket,
   finger holes, J-hook, and attachment slots.
   **Alt text:** A flat printed tool about 80 millimetres long with a shaped
   pocket at one end, two round finger holes, a J-shaped hook, and slots for zip
   ties.

3. **The tool straddling a wall plate.** Side view against the outlet, showing it
   sits flat and touches only the plug's sides and back.
   **Alt text:** Side view of the tool against a wall outlet, straddling the
   cover plate and gripping only the sides and back of the plug — nothing between
   the plug and the outlet.

4. **The two-sided puller on an extension cord.** Two plates zip-tied face to
   face around a fat round plug.
   **Alt text:** Two printed plates zip-tied face to face around a thick round
   extension-cord plug, their serrated inner arms gripping the plug body.

5. **The two plates apart.** Both plates side by side, as they come off the
   printer, showing the serrated grip zone and the zip-tie stations.
   **Alt text:** Two identical printed plates side by side, each with two large
   finger holes, two arms with serrated inner edges, and small round zip-tie
   holes.

6. **The three hand sizes, printed.** Small, Medium, and Large one-sided pullers
   on three plugs (`docs/images/one-sided-three-sizes.jpg`).
   **Alt text:** Three one-sided pullers side by side on the printer bed, Large on an orange extension-cord plug, Medium on a black three-prong plug, Small on a black lamp plug.

7. **A red warning tag in the preview.** The preview with the red 3D warning text
   on a deliberately bad measurement (`docs/images/one-sided-warning-tag-preview.png`,
   rendered by `scripts/render_doc_images.py` with a 27 mm thick plug).
   **Alt text:** The one-sided puller in the preview with red text lying beside it reading WARNING: PLUG THICKER THAN 24MM - USE THE TWO-SIDED PULLER FILE, which is how the tool reports a plug it cannot hold.

8. **The measuring stencil, tactile version.** Printed cards with raised
   characters and the braille flaps.
   **Alt text:** Thin printed measuring cards with plug-shaped cutouts, a
   notched ruler, and raised braille labels on a folded flap along each card's
   edge.

The cover must be a photograph of the actual printed object, not a render.
MakerWorld requires at least one real print photo per model and per print
profile.

## Pre-publish checklist

- [ ] **Maintainer has signed off on the licensing decision above.** This is the
      hard blocker; nothing else matters until it is resolved.
- [ ] **Repo is public** — the listing links back to GitHub.
- [ ] **Both single files are fresh** — `dist/Plug_Puller_SingleFile.scad` and
      `dist/Plug_Puller_Two_Sided_SingleFile.scad`. They are generated, not
      hand-edited. Run `python scripts/build_flattened.py --check` (it checks
      both); if it fails, run `python scripts/build_flattened.py` and commit the
      result. Uploading a stale flattened file ships different geometry than
      `src/`.
- [ ] **Both files uploaded,** each as its own customizable file on the one
      design page.
- [ ] **Single-file requirement verified.** The build script asserts the output
      contains no remaining `include`/`use` statements, and
      `tests/test_flattened_build.py` verifies render parity against the golden
      fixtures.
- [ ] **Customizer dropdown hygiene verified.** Run `pytest -m
      "not requires_openscad"` —
      `tests/test_openscad_customizer.py::test_no_parentheses_in_dropdown_options`
      is the important one, because a parenthesis in an option label makes the
      customizer silently revert the user's selection. The same module checks for
      `value:Label` syntax, defaults missing from their own option list, and that
      `render_mode` stays in the Hidden section.
- [ ] **Creator Portal smoke test.** Upload each file via Creator Portal → Open
      SCAD File and click through Steps 1–4 in MakerWorld's parameter form.
- [ ] **Cloud render verified for both tools.** Render the default Medium
      one-sided puller, then the two-sided file at its defaults and with the
      heavy-duty extension cord preset, and confirm each finishes inside the
      hosted renderer's timeout.
- [ ] **Pair download verified.** The two-sided file's download holds both
      plates side by side (two separate parts in one STL).
- [ ] **Plug preset label confirmed.** The maintainer has decided whether
      `Heavy-duty extension cord - NEMA 5-15` keeps its name (it names the plug,
      not the tool).
- [ ] **Warning tags confirmed visible on MakerWorld.** Set
      `measure_plug_width_prong_end` to an out-of-range value and confirm the red 3D
      warning text renders in the hosted preview. This model's warnings are real
      geometry rather than console output, which is exactly why it works on a
      platform with no console — verify it, because it is the model's main
      accessibility feature.
- [ ] **Every gallery image has alt text pasted into MakerWorld's field.**
- [ ] **Cover photo is a real printed object,** in use on an actual outlet.
- [ ] **Quick start linked from the description** — either the GitHub link to
      [`MAKERWORLD_QUICK_START.md`](MAKERWORLD_QUICK_START.md) or its content
      pasted into the instructions area.
