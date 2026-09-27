#!/usr/bin/env python3
"""Render the preview pictures the guides embed, so they can be regenerated.

Three PNGs under ``docs/images/``, rendered with the canonical OpenSCAD
binary from today's model files:

* ``one-sided-medium-render.png``: the one-sided puller at its defaults;
* ``two-sided-plate-render.png``: the two-sided puller at its defaults,
  both plates;
* ``one-sided-warning-tag-preview.png``: the one-sided puller with a plug
  27 mm thick at both ends, so the W-20 warning fires and its red text lies
  beside the part (the plain PNG export is a preview: the see-through plug
  and the red text both show, as they do in the Customizer).

Usage:
    python scripts/render_doc_images.py
    python scripts/render_doc_images.py --only one-sided-warning-tag-preview

Standard library only. License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OPENSCAD = Path(r"C:\Program Files\OpenSCAD (Nightly)\openscad.com")
ONE_SIDED = PROJECT_ROOT / "src" / "Plug_Puller_Parametric.scad"
TWO_SIDED = PROJECT_ROOT / "src" / "Plug_Puller_Two_Sided.scad"
OUT_DIR = PROJECT_ROOT / "docs" / "images"

CAMERA = ["--imgsize=1200,900", "--camera=0,0,0,55,0,25,0", "--autocenter", "--viewall",
          "--colorscheme", "Cornfield"]

PICTURES: Dict[str, Dict[str, object]] = {
    "one-sided-medium-render": {"scad": ONE_SIDED, "defines": {}},
    "two-sided-plate-render": {"scad": TWO_SIDED, "defines": {}},
    "one-sided-warning-tag-preview": {
        "scad": ONE_SIDED,
        "defines": {"measure_plug_thickness_prong_end": 27, "measure_plug_thickness_cord_end": 27},
    },
}


def find_openscad() -> Path:
    if OPENSCAD.exists():
        return OPENSCAD
    raise FileNotFoundError(f"OpenSCAD not found at {OPENSCAD}; install the 2026.01.03 nightly")


def render(name: str, scad: Path, defines: Dict[str, object]) -> Path:
    out = OUT_DIR / f"{name}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd: List[str] = [str(find_openscad())] + CAMERA
    for key, value in defines.items():
        cmd += ["-D", f"{key}={value}"]
    cmd += ["-o", str(out), str(scad)]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0 or not out.exists():
        raise RuntimeError(f"render failed for {name} (rc={result.returncode}):\n{result.stderr[-800:]}")
    return out


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--only", action="append", default=[], metavar="NAME",
                        help="one picture by name, without .png (repeatable)")
    args = parser.parse_args(argv)
    names = args.only or list(PICTURES)
    unknown = [n for n in names if n not in PICTURES]
    if unknown:
        parser.error(f"unknown picture(s): {unknown}; choose from {list(PICTURES)}")
    for name in names:
        spec = PICTURES[name]
        out = render(name, spec["scad"], spec["defines"])  # type: ignore[arg-type]
        print(f"{out.relative_to(PROJECT_ROOT).as_posix()} {out.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
