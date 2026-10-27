#!/usr/bin/env python3
"""The guides ZIP the MakerWorld listing needs beside its model files.

MakerWorld's model-file slot takes 3D and CAD files only (stl, 3mf, step,
scad and the like) and refuses a PDF, so the documents travel inside a ZIP,
which the slot does take. This script writes
``build/makerworld/Plug_Puller_Guides.zip``: the step-numbered guides of
``Documentation/`` (``Step_1_...`` to ``Step_3_...``), the Device Summary
and the Design Rationale as tagged PDFs, and each tool's quick start and
full guide from ``docs/``. The STL files and the two customizable files
upload on their own; the listing's field 11 lists what goes where.

Usage:
    python scripts/makerworld_bundle.py

Standard library only. License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path
from typing import List, Optional, Sequence

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build" / "makerworld" / "Plug_Puller_Guides.zip"
DOCS = ROOT / "Documentation"
STEP_GUIDES = 7
TOOL_GUIDES = [
    ROOT / "docs" / "Plug_Puller_One_Sided_Quick_Start.pdf",
    ROOT / "docs" / "Plug_Puller_One_Sided_Full_Guide.pdf",
    ROOT / "docs" / "Plug_Puller_Two_Sided_Quick_Start.pdf",
    ROOT / "docs" / "Plug_Puller_Two_Sided_Full_Guide.pdf",
]


def guide_files() -> List[Path]:
    steps = sorted(DOCS.glob("Step_*_Guide_*Plug_Puller_*.pdf"))
    if len(steps) != STEP_GUIDES:
        raise FileNotFoundError(f"expected the {STEP_GUIDES} step guides, found {len(steps)}")
    others = [DOCS / "Plug_Puller_Device_Summary.pdf", DOCS / "Plug_Puller_Design_Rationale.pdf"]
    return steps + others + TOOL_GUIDES


def write_zip(out: Path, files: Sequence[Path]) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for f in files:
            if not f.exists():
                raise FileNotFoundError(f)
            z.write(f, f.name)
    return out


def main(argv: Optional[Sequence[str]] = None) -> int:
    del argv
    z = write_zip(OUT, guide_files())
    with zipfile.ZipFile(z) as zf:
        names = zf.namelist()
    print(f"{z.relative_to(ROOT).as_posix()}: {len(names)} files, {z.stat().st_size // 1024} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
