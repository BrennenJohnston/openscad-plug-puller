#!/usr/bin/env python3
"""Write ``Documentation/Shot_List.md``: every photograph the guides still ask for.

A guide asks for a picture it does not have yet with a comment on its own
line, ``<!-- shot: NAME | angle: WORDS | show: WHAT -->``, where the picture
would go. This script collects them from ``Documentation/*.md`` in file
order and writes one table row each. ``--check`` exits 1 when the page is
not what the guides give (the quick test lane runs it).

Usage:
    python scripts/shot_list.py
    python scripts/shot_list.py --check

Standard library only. License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "Documentation"
OUT = DOCS / "Shot_List.md"
_SHOT = re.compile(r"<!--\s*shot:\s*([^|]+?)\s*\|\s*angle:\s*([^|]+?)\s*\|\s*show:\s*(.+?)\s*-->")


def shots() -> List[Tuple[str, str, str, str]]:
    out = []
    for page in sorted(DOCS.glob("*.md")):
        if page == OUT:
            continue
        for m in _SHOT.finditer(page.read_text(encoding="utf-8")):
            out.append((m.group(1), m.group(2), m.group(3), page.name))
    return out


def page_text() -> str:
    lines = ["# Shot List", "",
             "Every photograph the guides still ask for, collected from the shot requests in the pages by "
             "`scripts/shot_list.py`. Shoot each on the grey mat at the camera's full resolution; the five view "
             "words are standard, top, low, close and hands.", "",
             "| Name | View | What it shows | Asked for in |", "|---|---|---|---|"]
    found = shots()
    for name, angle, show, page in found:
        lines.append(f"| {name} | {angle} | {show} | {page} |")
    if not found:
        lines.append("| none | | | |")
    return "\n".join(lines) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    text = page_text()
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
            print(f"{OUT.relative_to(ROOT).as_posix()} is stale; run python scripts/shot_list.py")
            return 1
        print(f"{OUT.relative_to(ROOT).as_posix()} is current")
        return 0
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"{OUT.relative_to(ROOT).as_posix()}: {len(shots())} shot(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
