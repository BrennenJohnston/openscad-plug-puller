#!/usr/bin/env python3
"""Take the browser customizer guide's screenshots from the live Assistive Forge.

Headless Microsoft Edge opens the one-sided puller's one-link address in the
OpenSCAD Assistive Forge and walks the steps the Browser Customizer Guide
teaches: the first-visit choice, the shared-project prompt, Step 1 with a
plug preset picked, the preview, and Generate with the download. Each
screenshot gets red boxes numbered in the order the guide's words name the
controls, and is saved to ``Photos/screens/``.

The Forge reads the tool's files from its example branch, which is updated
when a version is released. So the screenshots show this repository's files
today, the browser is handed them in place of the branch's copies: the
single file from ``dist/``, the saved sets from ``presets/`` and the manifest
written here (``MANIFEST``, the copy the release puts on the branch).

Run from the repository root (needs the network and Playwright with Edge):

    python scripts/forge_screenshots.py

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import Page, sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "Photos" / "screens"
BRANCH = "https://raw.githubusercontent.com/BrennenJohnston/openscad-assistive-forge/example-manifest/plug-puller/"
URL = "https://openscad-assistive-forge.pages.dev/?manifest=" + BRANCH + "forge-manifest-one-sided.json"
VIEW = {"width": 1400, "height": 900}
PRESET = "Flat 2-prong lamp plug - NEMA 1-15"
RED = (216, 27, 27)
FONT_PATH = r"C:\Windows\Fonts\arialbd.ttf"

MANIFEST = {
    "forgeManifest": "1.0",
    "name": "Plug Puller, one-sided puller",
    "author": "Brennen Johnston",
    "description": ("A 3D-printed tool that pulls a plug with your whole hand instead of a fingertip pinch, shaped to "
                    "your plug and your hand. The one-sided puller is for a plug with 2 prongs or a USB-C tip: a "
                    "pocket around the plug's back and sides with two finger holes below it. A plug with 3 prongs "
                    "needs the two-sided puller, a separate file. Fill in Step 1 to Step 4; everything else is "
                    "optional."),
    "homepage": "https://github.com/BrennenJohnston/openscad-plug-puller",
    "files": {"main": "Plug_Puller_One_Sided_SingleFile.scad", "presets": "Plug_Puller_Parametric.json"},
    "defaults": {"autoPreview": True, "starterParameters": [
        "plug_preset", "measure_plug_length", "measure_plug_width_prong_end", "measure_plug_width_cord_end",
        "measure_plug_thickness_prong_end", "measure_plug_thickness_cord_end", "measure_cord_thickness",
        "measure_wall_plate_style", "show_plug_preview", "size", "measure_finger_width", "measure_hand_width",
        "attachment", "velcro_style", "strap_width", "hook_hand"]},
}
SERVED = {
    "forge-manifest-one-sided.json": ("application/json", json.dumps(MANIFEST).encode("utf-8")),
    "Plug_Puller_One_Sided_SingleFile.scad": ("text/plain", (ROOT / "dist" / "Plug_Puller_One_Sided_SingleFile.scad").read_bytes()),
    "Plug_Puller_Parametric.json": ("application/json", (ROOT / "presets" / "Plug_Puller_Parametric.json").read_bytes()),
}


def serve(route) -> None:
    name = route.request.url.rsplit("/", 1)[-1].split("?", 1)[0]
    if name not in SERVED:
        route.abort()
        return
    kind, body = SERVED[name]
    route.fulfill(status=200, body=body, headers={"Content-Type": kind, "Access-Control-Allow-Origin": "*"})


def box_of(page: Page, locator) -> Tuple[float, float, float, float]:
    locator.scroll_into_view_if_needed()
    b = locator.bounding_box()
    if b is None:
        raise RuntimeError(f"{locator} is not on the screen")
    return b["x"], b["y"], b["x"] + b["width"], b["y"] + b["height"]


def shot(page: Page, name: str, marks: Sequence[Tuple[float, float, float, float]]) -> Path:
    """The screen with a red box and a numbered badge around each mark."""
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    page.screenshot(path=str(path))
    im = Image.open(path).convert("RGB")
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype(FONT_PATH, 22)
    for n, (x0, y0, x1, y1) in enumerate(marks, start=1):
        pad = 4
        draw.rectangle([x0 - pad, y0 - pad, x1 + pad, y1 + pad], outline=RED, width=4)
        r = 15
        cx, cy = max(x0 - pad, r + 2), max(y0 - pad, r + 2)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
        draw.text((cx, cy), str(n), fill="white", font=font, anchor="mm")
    im.save(path, optimize=True)
    print(f"{path.relative_to(ROOT).as_posix()}  {len(marks)} mark(s)")
    return path


def main(argv: Optional[Sequence[str]] = None) -> int:
    del argv
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport=VIEW, accept_downloads=True)
        page.route(BRANCH + "**", serve)
        page.goto(URL, timeout=90000)
        page.get_by_role("button", name="Download & Continue").wait_for(timeout=60000)
        shot(page, "screen-browser-first-visit.png",
             [box_of(page, page.get_by_text("Assistive Forge", exact=True).first),
              box_of(page, page.get_by_role("button", name="Download & Continue"))])
        page.get_by_role("button", name="Download & Continue").click()
        save = page.get_by_role("dialog").get_by_role("button", name="Save My Copy")
        save.wait_for(timeout=120000)
        page.get_by_text("Loading OpenSCAD Engine").wait_for(state="hidden", timeout=180000)
        page.wait_for_timeout(1500)
        shot(page, "screen-browser-save-copy.png", [box_of(page, save)])
        save.click()
        page.wait_for_timeout(3000)
        preset = page.locator("#param-plug_preset")
        preset.wait_for(timeout=60000)
        preset.select_option(PRESET)
        page.wait_for_timeout(2000)
        page.get_by_text("Generating preview").first.wait_for(state="hidden", timeout=180000)
        ready = page.get_by_text("✓ Preview ready").first
        ready.wait_for(timeout=120000)
        page.wait_for_timeout(1500)
        marks: List[Tuple[float, float, float, float]] = [box_of(page, preset), box_of(page, ready)]
        shot(page, "screen-browser-step-1-preset.png", marks)
        generate = page.get_by_role("button", name="Generate STL file from current parameters")
        shot(page, "screen-browser-generate.png", [box_of(page, generate)])
        generate.click()
        download = page.get_by_role("button", name="Download generated STL file (full quality)")
        download.wait_for(timeout=180000)
        shot(page, "screen-browser-download.png", [box_of(page, download)])
        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
