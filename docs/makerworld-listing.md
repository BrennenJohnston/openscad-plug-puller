# MakerWorld Listing — Plug Puller

Status: **draft — do not upload.** The licensing decision gate below is
unresolved. Everything else in this document is finished and ready to paste.

Upload file: [`dist/Plug_Puller_SingleFile.scad`](../dist/Plug_Puller_SingleFile.scad).

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
| Upload file | `dist/Plug_Puller_SingleFile.scad` — this one file only. It is generated; see the pre-publish checklist. |
| Tags | `assistive technology`, `accessibility`, `arthritis`, `grip aid`, `plug puller`, `outlet`, `parametric`, `openscad`, `customizer`, `adaptive equipment`, `occupational therapy` |
| External link | <https://github.com/BrennenJohnston/openscad-plug-puller> (source repository) |

## Summary

A handheld assistive tool that helps people with limited grip strength,
arthritis, or small hands remove electrical plugs from wall outlets safely — by
pulling the plug, never the cord. Fully parametric: type a few ruler measurements
into the customizer and get a tool shaped to your exact plug, outlet plate, and
hand. Two tools in one model: a flat puller for typical plugs and a heavy-duty
clamshell for fat extension-cord plugs.

## Description

*Paste into MakerWorld's description body.*

**What it is**

The Plug Puller wraps around a plugged-in plug and gives you two large finger
holes and a cord hook, so removing the plug uses your whole hand instead of a
fingertip pinch. It touches only the plug's sides and back — never between the
plug face and the wall.

Two tool shapes come out of the same model, and Step 0 chooses between them for
you:

The **flat tool** is a single slab with a pocket shaped to your plug, two finger
holes, a J-hook for the cord, and slots for zip ties or a velcro strap. Slide it
over the plug and pull with your whole hand. Print one.

The **heavy-duty clamshell** is for fat round extension-cord plugs — anything 24
millimetres or more thick, which Step 0 detects automatically. Two serrated
plates grip the plug's sides and zip ties cinch them together. Print the same
plate **twice**, flip one, and zip-tie the pair face to face.

**Customize it to your plug and hand — this is the whole point**

Open the **Customize** panel and work top to bottom. The sections are numbered
and every measurement is in millimetres.

*Step 0 — Tool style.* Leave `tool_style` on `Auto from plug`. Slim plugs get the
flat tool; plugs 24 millimetres or thicker get the clamshell. Override it only if
you want to force a style.

*Step 1 — Your plug.* Either pick a preset in `plug_preset` — flat 2-prong lamp
plug (NEMA 1-15), standard 3-prong (NEMA 5-15), or heavy-duty round extension cord
— or set it to `Measure my plug` and type six numbers: plug length, width near the
wall, width near the cord, thickness near the wall, thickness near the cord, and
cord thickness. Then choose your wall-plate style in `measure_wall_plate_style`
(standard flat plate, Decora rocker, oversized jumbo, or no plate) so the tool
straddles the plate and sits flat against the wall.

*Step 2 — Size.* `size` offers Small, Medium (default), and Large grips, built
from ANSUR II 2012 hand anthropometry spanning roughly the 5th percentile female
to the 95th percentile male. Or set it to `Measure my hand` and type your finger
knuckle width and hand width.

*Step 3 — Attachment.* `attachment` gives you zip-tie holes, velcro strap slots,
both (the default), or none.

*Step 4 — Cord hook.* `hook_hand` is `Right` or `Left`.

Everything below Step 4 is optional power-user tuning.

**Bad numbers cannot fail silently.** If a measurement is out of range or the
geometry cannot work, the model renders a **red warning tag** naming the
measurement to fix — as actual 3D text you can see in the preview, not a console
message. A green tag confirms which numbers were applied. Fix the warning before
you export: the red tag is part of the exported model and would otherwise print
as an extra object on your bed.

**Print settings**

- Orientation: flat face down, pocket up. No supports.
- Layer height: 0.2 millimetres, or 0.16 for crisper rim fillets.
- Walls: 3 to 4. Infill: 25 to 35 percent, cubic or gyroid.
- Material: **PETG recommended** — it handles repeated flexing and the warmth near
  an outlet better than PLA. PLA, ABS, and ASA all work. **Do not use flexible
  filament**; the tool has to stay rigid to transmit force to the plug.
- Clamshell: print the plate **twice**, flip one copy, and zip-tie the pair face
  to face around the plug.
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
flat tool with the standard 3-prong preset, and it needs its own photograph of the
actual printed result.

## Gallery plan

1. **Cover — the tool in use on a real outlet.** A hand with fingers through both
   finger holes, tool seated on a plugged-in plug.
   **Alt text:** A printed plug puller seated over a plug in a wall outlet, with a
   hand's fingers through its two large finger holes, ready to pull.

2. **The flat tool alone, pocket up.** Three-quarter view showing the plug pocket,
   finger holes, J-hook, and attachment slots.
   **Alt text:** A flat printed tool about 80 millimetres long with a shaped
   pocket at one end, two round finger holes, a J-shaped hook, and slots for zip
   ties.

3. **The tool straddling a wall plate.** Side view against the outlet, showing it
   sits flat and touches only the plug's sides and back.
   **Alt text:** Side view of the tool against a wall outlet, straddling the
   cover plate and gripping only the sides and back of the plug — nothing between
   the plug and the outlet.

4. **Clamshell pair on an extension cord.** Two plates zip-tied face to face
   around a fat round plug.
   **Alt text:** Two printed plates zip-tied face to face around a thick round
   extension-cord plug, their serrated inner arms gripping the plug body.

5. **Clamshell plates apart.** Both plates side by side, showing the serrated
   grip zone and the zip-tie stations.
   **Alt text:** Two identical printed plates side by side, each with a curved
   serrated inner edge, a finger lobe, and three zip-tie slots.

6. **The three hand sizes, printed.** Small, Medium, and Large flat tools together
   with a ruler.
   **Alt text:** Three printed plug pullers in small, medium and large sizes beside
   a ruler, the largest about 78 millimetres wide across the finger holes.

7. **A red warning tag in the preview.** Screenshot of the customizer showing the
   red 3D warning text on a deliberately bad measurement.
   **Alt text:** The customizer preview showing red three-dimensional text reading
   "WARNING — CHECK PLUG WIDTH MEASUREMENTS (MM?)" above the model, which is how
   the tool reports a measurement that is out of range.

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
- [ ] **`dist/Plug_Puller_SingleFile.scad` is fresh.** It is generated, not
      hand-edited. Run `python scripts/build_flattened.py --check`; if it fails,
      run `python scripts/build_flattened.py` and commit the result. Uploading a
      stale flattened file ships different geometry than `src/`.
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
- [ ] **Creator Portal smoke test.** Upload via Creator Portal → Open SCAD File
      and click through Steps 0–4 in MakerWorld's parameter form.
- [ ] **Cloud render verified for both tool shapes.** Render the default Medium
      flat tool, then switch `plug_preset` to the heavy-duty extension cord and
      confirm the clamshell dispatch works in the hosted renderer and finishes
      inside its timeout.
- [ ] **Warning tags confirmed visible on MakerWorld.** Set
      `measure_plug_width_wall` to an out-of-range value and confirm the red 3D
      warning text renders in the hosted preview. This model's warnings are real
      geometry rather than console output, which is exactly why it works on a
      platform with no console — verify it, because it is the model's main
      accessibility feature.
- [ ] **Every gallery image has alt text pasted into MakerWorld's field.**
- [ ] **Cover photo is a real printed object,** in use on an actual outlet.
- [ ] **Quick start linked from the description** — either the GitHub link to
      [`MAKERWORLD_QUICK_START.md`](MAKERWORLD_QUICK_START.md) or its content
      pasted into the instructions area.
