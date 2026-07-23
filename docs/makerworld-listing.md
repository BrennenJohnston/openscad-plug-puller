# MakerWorld Listing — Draft (NOT YET PUBLISHED)

Prepared listing text for publishing the Plug Puller to MakerWorld's
Parametric Model Maker (PMM). Upload file:
[`dist/Plug_Puller_SingleFile.scad`](../dist/Plug_Puller_SingleFile.scad).

> ## ⚠ Licensing decision gate — maintainer sign-off required
>
> This repository is licensed **PolyForm Noncommercial 1.0.0**.
> Publishing to MakerWorld requires accepting MakerWorld's terms of
> service, which grant the platform a license to host, display, and
> distribute the uploaded model, and require choosing one of
> MakerWorld's listing licenses (a Creative Commons variant or Bambu
> Lab's Standard Digital File License) for downloaders. That platform
> grant sits **alongside** — and for MakerWorld downloads, effectively
> in front of — PolyForm NC.
>
> **Decision for the maintainer:**
>
> - **Option A — publish on MakerWorld:** accept the platform grant and
>   pick the listing license closest to PolyForm NC's intent
>   (recommended: **CC BY-NC-SA 4.0** — noncommercial, attribution,
>   share-alike). Downloads via MakerWorld follow that CC license;
>   the GitHub repo stays PolyForm NC.
> - **Option B — stay playground-only:** skip MakerWorld; the
>   zero-install path remains the OpenSCAD Playground link in the
>   README, which serves the file straight from this repo under
>   PolyForm NC with no platform grant.
>
> Until Option A is explicitly chosen, **do not upload**.

---

## Title

**Plug Puller — Parametric Assistive Plug Remover (fits YOUR plug and YOUR hand)**

## Summary (short description)

A handheld assistive tool that helps people with limited grip strength,
arthritis, or small hands remove electrical plugs from wall outlets
safely — pulling the plug, never the cord. Fully parametric: type a few
ruler measurements into the customizer and get a tool shaped to your
exact plug, outlet plate, and hand. Two tools in one model: a flat
puller for typical plugs and a heavy-duty clamshell for fat
extension-cord plugs.

## Description

### What it is

The Plug Puller wraps around a plugged-in plug and gives you two big
finger holes and a cord hook, so removing the plug uses your whole hand
instead of a fingertip pinch. It touches only the plug's sides and back
— never between the plug face and the wall.

### Customize it to your plug and hand (the whole point!)

Open the **Customize** panel and work top to bottom — the form is
numbered:

- **Step 0 — Tool style:** leave on *Auto from plug*. Slim plugs get
  the flat tool; fat plugs (≥ 24 mm thick) get the heavy-duty
  clamshell (two serrated plates that zip-tie around the plug — print
  the plate twice and flip one).
- **Step 1 — Your plug:** pick a quick preset (flat 2-prong lamp plug,
  standard 3-prong, heavy-duty round extension cord) **or** type six
  ruler/caliper measurements: plug length, width near the wall, width
  near the cord, thickness near the wall, thickness near the cord, and
  cord thickness. Plus a picture-quiz choice of your wall-plate style
  (standard / Decora rocker / jumbo / flush) so the tool straddles the
  plate and sits flat.
- **Step 2 — Size:** Small / Medium / Large grips (research-grounded
  ANSUR-II hand data, ≈ 5th percentile female to ≈ 95th percentile
  male), or *Measure my hand* — type your finger-knuckle width and
  hand width and the grip is built for them.
- **Step 3 — Attachment:** zip-tie holes, velcro strap slots, both
  (default), or none.
- **Step 4 — Cord hook:** right- or left-handed J-hook.

Everything below Step 4 is optional power-user tuning. All measurements
are in millimetres. Bad numbers can't fail silently: the model prints a
red warning tag naming the measurement to fix, and a green tag confirms
your numbers were applied.

### Print settings

- **Orientation:** flat face down, pocket up — no supports.
- **Layer height:** 0.2 mm (0.16 mm for crisper rim fillets).
- **Walls:** 3–4 · **Infill:** 25–35 % cubic/gyroid.
- **Material:** PETG recommended (fatigue + outlet heat tolerance);
  PLA/ABS/ASA fine. Avoid flexible filament — the tool must stay rigid.
- **Clamshell:** print the plate **twice**, flip one copy, zip-tie the
  pair face-to-face around the plug.

### Safety

The tool grips only the plug body's sides and back face. Nothing is
inserted between the plug and the outlet, and no conductive parts are
involved. Inspect prints for cracks before use; reprint if damaged.

### More resources (GitHub)

Full measuring guide with per-measurement photos, printable 1:1
try-before-you-print outline sheets, a finger-sizing stencil, fit
troubleshooting, and the engineering reference live in the source
repository: <https://github.com/BrennenJohnston/openscad-plug-puller>

## Tags

`assistive technology` `accessibility` `arthritis` `grip aid`
`plug puller` `outlet` `parametric` `openscad` `customizer`
`adaptive equipment` `occupational therapy`

## Category

Health & Personal Care → Assistive Devices (or Tools → Hand Tools if
unavailable)

## Listing checklist (before publish)

- [ ] Maintainer has signed off on the licensing decision above
- [ ] Repo is public (the listing links back to GitHub)
- [ ] Test the upload via **Creator Portal → Open SCAD File** and click
      through Steps 0–4 in MakerWorld's parameter form
- [ ] Verify a cloud render of the default Medium and of the
      heavy-duty preset (clamshell dispatch works in PMM)
- [ ] Upload gallery photos: printed tool on a plug, finger grip in
      use, clamshell pair on an extension cord, customizer screenshot
