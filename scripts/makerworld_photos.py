#!/usr/bin/env python3
"""Make the MakerWorld listing's pictures into ``MakerWorld_Photos/``.

One folder for each section of MakerWorld's upload form: ``Cover/`` (the
desktop cover at 4:3 and the app cover at 3:4), ``Real_Photos/`` (photographs
of the printed tools, numbered in upload order) and ``Renders/`` (computer
renderings, kept apart as the form asks). Each photograph is cut from its
full-size master, never from a guide copy, framed so the tool fills most of
it; each render is drawn by OpenSCAD from a shipped STL. Nothing is scaled
up: a crop smaller than the slot's size is saved at its own size.

The sizes are the ones users report the site shows uncropped: 1600 x 1200
for the desktop cover and every gallery picture, 768 x 1024 for the app's
cover. If the upload form recommends other sizes, change them below.

Run from the repository root, naming the photo session folders:

    python scripts/makerworld_photos.py --masters "<October 2026 session>" --july "<July 2026 edited photos>"

Needs Pillow and OpenSCAD (the nightly's console wrapper). License:
PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional, Sequence

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.photo_import import cut, save_jpeg  # noqa: E402

OUT = PROJECT_ROOT / "MakerWorld_Photos"
OPENSCAD = Path(os.environ.get("OPENSCAD_EXE", r"C:\Program Files\OpenSCAD (Nightly)\openscad.com"))
GALLERY = (1600, 1200)
MOBILE = (768, 1024)
SERIES = "Two Sided Photos/"

# (folder, file, master set, source, crop box in source pixels, slot size)
PHOTOS = [
    ("Cover", "1_desktop_4x3.jpg", "masters", SERIES + "20261013_102324.jpg", [241, 0, 2529, 1716], GALLERY),
    ("Cover", "2_mobile_3x4.jpg", "masters", SERIES + "20261013_101748.jpg", [1614, 404, 2439, 1504], MOBILE),
    ("Real_Photos", "01_front_both_plates.jpg", "masters", SERIES + "20261013_101905.jpg", [757, 10, 2987, 1682], GALLERY),
    ("Real_Photos", "02_top_finished_standard_plug.jpg", "masters", SERIES + "20261013_101748.jpg", [1200, 334, 2853, 1574], GALLERY),
    ("Real_Photos", "03_top_finished_heavy_duty_plug.jpg", "masters", SERIES + "20261013_102246.jpg", [1277, 329, 2930, 1569], GALLERY),
    ("Real_Photos", "04_side_pulling_heavy_duty_plug.jpg", "masters", SERIES + "20261013_102342.jpg", [556, 0, 2844, 1716], GALLERY),
    ("Real_Photos", "05_pulling_standard_plug.jpg", "masters", SERIES + "20261013_101812.jpg", [356, 0, 2644, 1716], GALLERY),
    ("Real_Photos", "06_plates_and_heavy_duty_plug.jpg", "masters", SERIES + "20261013_101923.jpg", [1108, 19, 3108, 1519], GALLERY),
    ("Real_Photos", "07_one_sided_on_lamp_plug.jpg", "july", "P1_H2.jpg", [0, 0, 1891, 1351], GALLERY),
]

# (file, STL under stl/Plug-Puller/, colour)
RENDERS = [
    ("01_two_sided_standard_plug_medium.png", "Plug-Puller_Two-Sided_Standard-3-Prong-NEMA-5-15_Medium.stl", "MediumSeaGreen"),
    ("02_two_sided_heavy_duty_plug_medium.png", "Plug-Puller_Two-Sided_Round-Extension-Cord-NEMA-5-15_Medium.stl", "MediumSeaGreen"),
    ("03_one_sided_lamp_plug_medium.png", "Plug-Puller_Flat-2-Prong-Lamp-NEMA-1-15_Medium.stl", "YellowGreen"),
    ("04_one_sided_usb_c_tip_medium.png", "Plug-Puller_USB-C-Laptop-Tip_Medium.stl", "YellowGreen"),
]
RENDER_CAMERA = ["--camera=0,0,0,50,0,20,0", "--autocenter", "--viewall", "--colorscheme", "Tomorrow"]


def render(stl: Path, colour: str, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        scad = Path(tmp) / "render.scad"
        scad.write_text(f'color("{colour}") import("{stl.as_posix()}");\n', encoding="utf-8")
        cmd = [str(OPENSCAD), f"--imgsize={GALLERY[0]},{GALLERY[1]}", *RENDER_CAMERA, "-o", str(out), str(scad)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0 or not out.exists():
            raise RuntimeError(f"OpenSCAD could not render {stl.name}:\n{result.stderr}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--masters", type=Path, default=os.environ.get("PLUG_PULLER_MASTERS"))
    parser.add_argument("--july", type=Path, default=os.environ.get("PLUG_PULLER_JULY_PHOTOS"))
    parser.add_argument("--skip-renders", action="store_true")
    args = parser.parse_args(argv)
    roots = {"masters": args.masters, "july": args.july}
    for folder, name, root, source, box, size in PHOTOS:
        if roots[root] is None:
            raise SystemExit(f"--{root} names the folder that holds {source}")
        im = cut(Path(roots[root]) / source, box, size[0] / size[1], max(size))
        out = OUT / folder / name
        save_jpeg(im, out)
        print(f"{out.relative_to(PROJECT_ROOT).as_posix()}  {im.width} x {im.height}")
    if not args.skip_renders:
        for name, stl, colour in RENDERS:
            out = OUT / "Renders" / name
            render(PROJECT_ROOT / "stl" / "Plug-Puller" / stl, colour, out)
            print(f"{out.relative_to(PROJECT_ROOT).as_posix()}  {GALLERY[0]} x {GALLERY[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
