#!/usr/bin/env python3
"""Import the guide photographs into ``Photos/`` from their full-size masters.

Every record of ``Documentation/images.json`` whose ``origin.kind`` is
``photo`` and whose ``use`` is ``guide`` is cut from its master by its
``crop`` box (source pixels, ``[left, top, right, bottom]``), opened out to
3:2 when the box is another shape, scaled to 1600 px on the long edge (never
up), and saved as ``Photos/<group>/<name>``: JPEG quality 85, sRGB, no EXIF.
The saved file's SHA-256 goes back into the record (``origin.imported_sha256``)
so ``tests/test_images_manifest.py`` can tell a stale import.

A master is found under the folder named by ``--masters`` (or the
``PLUG_PULLER_MASTERS`` environment variable) by its ``origin.source`` path;
a source that starts with ``docs/`` is a picture already in this repository.
The masters stay outside the repository; their SHA-256 in the record proves
which file a picture came from.

Run from the repository root:

    python scripts/photo_import.py --masters "<the photo session folder>"

Needs Pillow. License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from PIL import Image, ImageCms, ImageOps

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "Documentation" / "images.json"
PHOTOS = ROOT / "Photos"
LONG_EDGE = 1600
QUALITY = 85
FRAME_ASPECT = 3 / 2


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def master_path(record: Dict[str, Any], masters: Optional[Path]) -> Path:
    source = record["origin"]["source"]
    if source.startswith("docs/"):
        return ROOT / source
    if masters is None:
        raise SystemExit("--masters (or PLUG_PULLER_MASTERS) names the photo session folder")
    return masters / source


def open_out(box: Sequence[int], size: Sequence[int], aspect: float) -> List[int]:
    """Grow the crop box to ``aspect`` about its center, inside the image."""
    left, top, right, bottom = box
    w, h = right - left, bottom - top
    if w / h < aspect:
        w = h * aspect
    else:
        h = w / aspect
    cx, cy = (left + right) / 2, (top + bottom) / 2
    W, H = size
    w, h = min(w, W), min(h, H)
    if w / h > aspect + 1e-6:
        w = h * aspect
    elif w / h < aspect - 1e-6:
        h = w / aspect
    x0 = min(max(cx - w / 2, 0), W - w)
    y0 = min(max(cy - h / 2, 0), H - h)
    return [round(x0), round(y0), round(x0 + w), round(y0 + h)]


def to_srgb(im: Image.Image) -> Image.Image:
    icc = im.info.get("icc_profile")
    if icc:
        src = ImageCms.ImageCmsProfile(io.BytesIO(icc))
        im = ImageCms.profileToProfile(im, src, ImageCms.createProfile("sRGB"), outputMode="RGB")
    return im.convert("RGB")


def cut(master: Path, box: Sequence[int], aspect: float, long_edge: int) -> Image.Image:
    im = to_srgb(ImageOps.exif_transpose(Image.open(master)))
    full = open_out(box, im.size, aspect)
    out = im.crop(full)
    scale = min(1.0, long_edge / max(out.size))
    if scale < 1.0:
        out = out.resize((round(out.width * scale), round(out.height * scale)), Image.LANCZOS)
    return out


def save_jpeg(im: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, "JPEG", quality=QUALITY, optimize=True, progressive=False)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--masters", type=Path, default=os.environ.get("PLUG_PULLER_MASTERS"))
    parser.add_argument("--only", action="append", default=[], help="one picture name (repeatable)")
    args = parser.parse_args(argv)
    masters = Path(args.masters) if args.masters else None
    records = json.loads(MANIFEST.read_text(encoding="utf-8"))
    done = 0
    for rec in records:
        if rec["origin"]["kind"] != "photo" or rec["use"] != "guide":
            continue
        if args.only and rec["name"] not in args.only:
            continue
        master = master_path(rec, masters)
        if sha256(master) != rec["origin"]["sha256"]:
            raise SystemExit(f"{rec['name']}: {master} is not the master the record names (SHA-256 differs)")
        out = PHOTOS / rec["group"] / rec["name"]
        save_jpeg(cut(master, rec["crop"], FRAME_ASPECT, LONG_EDGE), out)
        rec["origin"]["imported_sha256"] = sha256(out)
        rec["pixels"] = list(Image.open(out).size)
        done += 1
        print(f"{out.relative_to(ROOT).as_posix()}  {rec['pixels'][0]} x {rec['pixels'][1]}")
    MANIFEST.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"{done} picture(s) imported; {MANIFEST.relative_to(ROOT).as_posix()} updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
