#!/usr/bin/env python3
"""The listing's description as plain Markdown, for Thingiverse and Printables.

Those sites strip the formatting of pasted rich text but render Markdown
typed or pasted into their description field, so this script writes the
MakerWorld listing's description (its section 3) as
``Documentation/Plug_Puller_Listing_Description.md``: the
model title as the heading, the summary as the first line, each section as
a second-level heading, bold, lists and links kept, every picture left out
(the sites take pictures in their own gallery), and the one sentence that
points to MakerWorld's license field dropped. ``--check`` exits 1 when the file is not
what the listing gives (the test runs it).

Usage:
    python scripts/listing_description_markdown.py           # write the page
    python scripts/listing_description_markdown.py --check   # compare, exit 1 if stale

Standard library only. License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Optional, Sequence

ROOT = Path(__file__).resolve().parent.parent
LISTING = ROOT / "Documentation" / "Plug_Puller_MakerWorld_Listing.md"
OUT = ROOT / "Documentation" / "Plug_Puller_Listing_Description.md"
_IMAGE = re.compile(r"^!\[[^\]]*\]\([^)]+\)\s*$")
_AUTOLINK = re.compile(r"<(https?://[^>\s]+)>")
SITE_ONLY = ("Downloads from this listing are under the license picked below.",)


def field(text: str, number: int) -> str:
    m = re.search(rf"^## {number}\. [^\n]+\n(.*?)(?=^## \d+\. |\Z)", text, re.S | re.M)
    if not m:
        raise ValueError(f"the listing has no field {number}")
    return m.group(1).strip()


def page_text() -> str:
    text = LISTING.read_text(encoding="utf-8")
    title = field(text, 1)
    summary = field(text, 2)
    lines = [f"# {title}", "", summary, ""]
    for line in field(text, 3).splitlines():
        if _IMAGE.match(line) or line.startswith(SITE_ONLY):
            continue
        line = _AUTOLINK.sub(r"\1", line)
        if line.startswith("### "):
            line = "## " + line[4:]
        lines.append(line)
    out = "\n".join(lines).rstrip("\n") + "\n"
    return re.sub(r"\n{3,}", "\n\n", out)


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="exit 1 when the page is stale")
    args = ap.parse_args(argv)
    text = page_text()
    name = OUT.relative_to(ROOT).as_posix()
    if args.check:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != text:
            print(f"{name} is stale; run python scripts/listing_description_markdown.py")
            return 1
        print(f"{name} is current")
        return 0
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"{name} written, {len(text.splitlines())} lines")
    return 0


if __name__ == "__main__":
    sys.exit(main())
