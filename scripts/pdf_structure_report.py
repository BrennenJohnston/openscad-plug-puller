#!/usr/bin/env python3
"""The reading order of a tagged PDF, as text.

Walks the PDF's structure tree (what a screen reader follows) and prints
one line per element in tree order, indented by depth: the element's type,
its alt text when it has one, and a table cell's scope. A heading out of
order, a figure without alt text, or a caption that did not land inside
its figure shows up as a line in the wrong place.

Usage:
    python scripts/pdf_structure_report.py Documentation/Step_3_Guide_Plug_Puller_User_Guide.pdf
    python scripts/pdf_structure_report.py <pdf> --max-depth 3 --limit 80

Local lane: needs pypdf (never run with ``python -I``). License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Sequence

from pypdf import PdfReader
from pypdf.generic import ArrayObject, DictionaryObject, IndirectObject

SKIP = {"/Type", "/K", "/P", "/Pg", "/S", "/A", "/ID"}


def _resolve(obj):
    return obj.get_object() if isinstance(obj, IndirectObject) else obj


def walk(node, depth: int, out: List[str], max_depth: int) -> None:
    node = _resolve(node)
    if not isinstance(node, DictionaryObject):
        return
    kind = node.get("/S")
    if kind is not None:
        detail = []
        if "/Alt" in node:
            detail.append(f'Alt="{node["/Alt"]}"')
        attrs = _resolve(node.get("/A"))
        for a in (attrs if isinstance(attrs, ArrayObject) else [attrs] if attrs is not None else []):
            a = _resolve(a)
            if isinstance(a, DictionaryObject) and "/Scope" in a:
                detail.append(f"Scope={a['/Scope']}")
        out.append("  " * depth + str(kind).lstrip("/") + (" " + " ".join(detail) if detail else ""))
        depth += 1
    if depth > max_depth:
        return
    kids = node.get("/K")
    if kids is None:
        return
    kids = _resolve(kids)
    for kid in (kids if isinstance(kids, ArrayObject) else [kids]):
        kid = _resolve(kid)
        if isinstance(kid, DictionaryObject):
            walk(kid, depth, out, max_depth)


def report(pdf: Path, max_depth: int) -> List[str]:
    reader = PdfReader(str(pdf))
    root = reader.trailer["/Root"]
    if "/StructTreeRoot" not in root:
        raise SystemExit(f"{pdf.name} has no structure tree: it is not a tagged PDF")
    out: List[str] = []
    walk(root["/StructTreeRoot"], 0, out, max_depth)
    return out


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--max-depth", type=int, default=6, help="how deep into the tree to print (default 6)")
    ap.add_argument("--limit", type=int, default=0, help="print at most this many lines (default all)")
    args = ap.parse_args(argv)
    lines = report(args.pdf, args.max_depth)
    shown = lines[:args.limit] if args.limit else lines
    print("\n".join(shown))
    if args.limit and len(lines) > args.limit:
        print(f"... {len(lines) - args.limit} more lines")
    counts = {}
    for line in lines:
        kind = line.strip().split(" ", 1)[0]
        counts[kind] = counts.get(kind, 0) + 1
    print("counts:", ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
