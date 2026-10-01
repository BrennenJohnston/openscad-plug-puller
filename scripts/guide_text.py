#!/usr/bin/env python3
"""The hand-written text of the guides: one source file per topic, and the
Markdown subset they use turned into HTML for the printed PDFs.

The four guide documents (the quick start and the full guide of each tool)
are assembled by ``scripts/build_dial_reference.py`` from the generated dial
cards plus small Markdown source files under ``docs/guides/source/``: one
topic each, written once, used by every document that needs it. A source
file may carry placeholders in braces, ``{tool}`` for "one-sided puller" and
so on (``PLACEHOLDERS`` lists them); the loader fills them for one tool.
Links and image paths in a source file are written as the assembled page
under ``docs/guides/<tool>/`` will use them.

``markdown_to_html`` handles exactly what the sources use: ATX headings,
paragraphs, bullet and numbered lists (one level deep, with an image inside
an item), pipe tables, fenced code, block quotes, images on their own line,
links, bold and inline code. HTML comments are dropped. Standard library
only.

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Callable, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = PROJECT_ROOT / "docs" / "guides" / "source"

# The one-link path into the OpenSCAD Assistive Forge: each manifest, with a
# copy of the tool's single file and presets, lives on the Forge's
# example-manifest branch under plug-puller/.
FORGE = ("https://openscad-assistive-forge.pages.dev/?manifest=https://raw.githubusercontent.com/BrennenJohnston/"
         "openscad-assistive-forge/example-manifest/plug-puller/")

# The words a source file may ask for, per tool.
PLACEHOLDERS: Dict[str, Dict[str, str]] = {
    "one-sided": {
        "tool": "one-sided puller",
        "Tool": "One-sided puller",
        "other_tool": "two-sided puller",
        "file": "src/Plug_Puller_Parametric.scad",
        "single_file": "dist/Plug_Puller_SingleFile.scad",
        "forge_url": FORGE + "forge-manifest-one-sided.json",
        "orientation": "flat face down on the bed, the plug pocket facing up",
        "part_word": "the tool",
        "zip_ties": "two zip ties up to 4.8 mm wide (about 200 mm long), or one hook-and-loop strap 10 to 25 mm wide",
        "quick_start_pdf": "Plug_Puller_One_Sided_Quick_Start.pdf",
        "full_guide_pdf": "Plug_Puller_One_Sided_Full_Guide.pdf",
        "step4": "Step 4 - Cord Hook",
        "layout_note": "",
        "print_photo": (
            "The picture shows nine one-sided pullers printed this way, in three sizes, all flat on the bed.\n\n"
            "![Nine one-sided pullers in three sizes printed flat on the printer bed, the pocket side up, no supports.]"
            "(../../images/print-bed-nine-tools.jpg)"
        ),
        "split_row": "",
        "strength_fix": "Reprint in PETG with 4 walls",
        "cli_example": (
            "```bash\n"
            "# A left-handed hook and the standard 3-prong preset\n"
            "openscad -o puller.stl --backend Manifold \\\n"
            "  -D 'plug_preset=\"Standard 3-prong plug - NEMA 5-15\"' -D 'hook_hand=\"Left\"' \\\n"
            "  src/Plug_Puller_Parametric.scad\n"
            "\n"
            "# A saved set of settings\n"
            "openscad -o puller.stl -p presets/Plug_Puller_Parametric.json \\\n"
            "  -P \"Left-handed + classic velcro slots\" src/Plug_Puller_Parametric.scad\n"
            "```"
        ),
        "presets_json": "presets/Plug_Puller_Parametric.json",
        "seat_words": "flat in the pocket with the cord in the hook",
    },
    "two-sided": {
        "tool": "two-sided puller",
        "Tool": "Two-sided puller",
        "other_tool": "one-sided puller",
        "file": "src/Plug_Puller_Two_Sided.scad",
        "single_file": "dist/Plug_Puller_Two_Sided_SingleFile.scad",
        "forge_url": FORGE + "forge-manifest-two-sided.json",
        "orientation": "both plates flat on the bed, exactly as the file lays them out",
        "part_word": "the plates",
        "zip_ties": "three zip ties up to 3.6 mm wide (about 200 mm long)",
        "quick_start_pdf": "Plug_Puller_Two_Sided_Quick_Start.pdf",
        "full_guide_pdf": "Plug_Puller_Two_Sided_Full_Guide.pdf",
        "step4": "Step 4 - Print Layout",
        "layout_note": (
            "The file holds both plates side by side. Most slicers load it as one object with two parts, which "
            "prints fine as it is; use your slicer's split-to-objects command if you want to move one plate on its own."
        ),
        "print_photo": "",
        "split_row": (
            "\n| The slicer shows two separate parts | That is the design: Both plates puts the two plates side by side "
            "in one file | Print both; if the slicer asks, let it split them into separate objects |"
        ),
        "strength_fix": "Reprint in PETG with 4 walls, or raise plate_wall_boost or plate_thickness",
        "cli_example": (
            "```bash\n"
            "# Both plates for the heavy-duty extension cord preset, with 2 mm thicker walls\n"
            "openscad -o plates.stl --backend Manifold \\\n"
            "  -D 'plug_preset=\"Heavy-duty extension cord - NEMA 5-15\"' -D plate_wall_boost=2 \\\n"
            "  src/Plug_Puller_Two_Sided.scad\n"
            "\n"
            "# A saved set of settings\n"
            "openscad -o plates.stl -p presets/Plug_Puller_Two_Sided.json \\\n"
            "  -P \"USB-C laptop tip\" src/Plug_Puller_Two_Sided.scad\n"
            "```"
        ),
        "presets_json": "presets/Plug_Puller_Two_Sided.json",
        "seat_words": "flat between the plates with the cord in its channel",
    },
}

_PLACEHOLDER = re.compile(r"\{([a-z_][a-z0-9_]*)\}", re.I)


def fill(text: str, values: Dict[str, str]) -> str:
    """Replace every known ``{placeholder}``; an unknown one is an error,
    so a typo in a source file cannot reach a reader."""
    def one(m: re.Match) -> str:
        key = m.group(1)
        if key not in values:
            raise KeyError(f"unknown placeholder {{{key}}} in a guide source file")
        return values[key]
    return _PLACEHOLDER.sub(one, text)


_KIND_BLOCK = re.compile(r"<!-- (quick-start|full-guide) -->\n?(.*?)<!-- /\1 -->\n?", re.S)


def load_source(name: str, tool: str, kind: Optional[str] = None) -> str:
    """The Markdown of one source file, filled for ``tool``, without a
    trailing newline. Text between ``<!-- full-guide -->`` and
    ``<!-- /full-guide -->`` (or ``quick-start``) is kept for that document
    only, so a topic can say more in the full guide; without ``kind`` every
    block stays."""
    path = SOURCE_DIR / f"{name}.md"
    text = fill(path.read_text(encoding="utf-8"), PLACEHOLDERS[tool])

    def keep(m: re.Match) -> str:
        return m.group(2) if kind is None or m.group(1) == kind else ""
    text = _KIND_BLOCK.sub(keep, text)
    # An empty placeholder or a dropped block leaves a gap; the page keeps one blank line.
    return re.sub(r"\n{3,}", "\n\n", text).strip("\n")


# ---------------------------------------------------------------------------
# Markdown to HTML
# ---------------------------------------------------------------------------

_HEADING = re.compile(r"^(#{1,6}) (.+?)\s*#*$")
_LIST_ITEM = re.compile(r"^(\s*)(?:[-*]|(\d+)\.) (.*)$")
_IMAGE_LINE = re.compile(r"^!\[([^\]]*)\]\(([^)\s]+)\)$")
_TABLE_SEP = re.compile(r"^\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?$")
_COMMENT = re.compile(r"<!--.*?-->", re.S)

_INLINE_CODE = re.compile(r"`([^`]+)`")
_BOLD = re.compile(r"\*\*(.+?)\*\*")
_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
_AUTOLINK = re.compile(r"&lt;(https?://[^&\s]+)&gt;")


def anchor(text: str) -> str:
    """A heading's id, as GitHub makes them: lower case, spaces to hyphens,
    punctuation dropped."""
    plain = re.sub(r"[`*_]", "", text)
    plain = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", plain)
    return re.sub(r"[^a-z0-9 -]", "", plain.lower()).strip().replace(" ", "-")


LinkSrc = Optional[Callable[[str], Optional[str]]]


def inline(text: str, link_src: LinkSrc = None) -> str:
    """Inline Markdown to HTML: code, bold, links, autolinks. ``link_src``
    maps a link's target to the one the page needs, or to None to keep the
    link's words without a link (the print drops links to other files)."""
    out = html.escape(text, quote=False)
    out = _INLINE_CODE.sub(lambda m: f"<code>{m.group(1)}</code>", out)
    out = _BOLD.sub(r"<b>\1</b>", out)

    def link(m: re.Match) -> str:
        href = link_src(m.group(2)) if link_src else m.group(2)
        if href is None:
            return m.group(1)
        return f'<a href="{html.escape(href, quote=True)}">{m.group(1)}</a>'
    out = _LINK.sub(link, out)
    out = _AUTOLINK.sub(r'<a href="\1">\1</a>', out)
    return out


def _table(lines: List[str], link_src: LinkSrc = None) -> str:
    rows = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in lines]
    head, body = rows[0], rows[2:]
    out = ["<table>", "<thead><tr>" + "".join(f"<th>{inline(c, link_src)}</th>" for c in head) + "</tr></thead>", "<tbody>"]
    for row in body:
        out.append("<tr>" + "".join(f"<td>{inline(c, link_src)}</td>" for c in row) + "</tr>")
    out += ["</tbody>", "</table>"]
    return "\n".join(out)


def _figure(alt: str, src: str, image_src: Optional[Callable[[str], str]]) -> str:
    href = image_src(src) if image_src else src
    caption = f"<figcaption>{html.escape(alt, quote=False)}</figcaption>" if alt else ""
    return f'<figure class="photo"><img src="{html.escape(href, quote=True)}" alt="{html.escape(alt, quote=True)}">{caption}</figure>'


def markdown_to_html(md: str, image_src: Optional[Callable[[str], str]] = None,
                     heading_ids: bool = True, link_src: LinkSrc = None) -> str:
    """The HTML of a Markdown source (see the module docstring for the
    subset). ``image_src`` maps an image path to the ``src`` the page needs
    (the print wants absolute file paths)."""
    return "\n".join(markdown_to_blocks(md, image_src, heading_ids, link_src))


def markdown_to_blocks(md: str, image_src: Optional[Callable[[str], str]] = None,
                       heading_ids: bool = True, link_src: LinkSrc = None) -> List[str]:
    """``markdown_to_html`` as one string per block (a heading, a paragraph,
    a list, a table, ...), for a caller that keeps a heading with the block
    after it."""
    lines = _COMMENT.sub("", md).splitlines()
    out: List[str] = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
        if stripped.startswith("```"):
            code: List[str] = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            out.append("<pre><code>" + html.escape("\n".join(code), quote=False) + "</code></pre>")
            continue
        m = _HEADING.match(stripped)
        if m:
            level = len(m.group(1))
            text = m.group(2)
            id_attr = f' id="{anchor(text)}"' if heading_ids else ""
            out.append(f"<h{level}{id_attr}>{inline(text, link_src)}</h{level}>")
            i += 1
            continue
        if stripped.startswith("|") and i + 1 < n and _TABLE_SEP.match(lines[i + 1].strip()):
            block = []
            while i < n and lines[i].strip().startswith("|"):
                block.append(lines[i])
                i += 1
            out.append(_table(block, link_src))
            continue
        if stripped.startswith(">"):
            quote: List[str] = []
            while i < n and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip()[1:].strip())
                i += 1
            out.append('<blockquote><p>' + inline(" ".join(q for q in quote if q), link_src) + "</p></blockquote>")
            continue
        m = _IMAGE_LINE.match(stripped)
        if m and not line.startswith(" "):
            out.append(_figure(m.group(1), m.group(2), image_src))
            i += 1
            continue
        m = _LIST_ITEM.match(line)
        if m and not m.group(1):
            ordered = m.group(2) is not None
            items: List[str] = []
            while i < n:
                lm = _LIST_ITEM.match(lines[i])
                if lm and not lm.group(1):
                    parts = [inline(lm.group(3), link_src)]
                    i += 1
                    # Indented lines belong to the item: text continues it, an image sits inside it.
                    while i < n and (lines[i].startswith(" ") or (not lines[i].strip() and i + 1 < n and lines[i + 1].startswith(" "))):
                        cont = lines[i].strip()
                        i += 1
                        if not cont:
                            continue
                        im = _IMAGE_LINE.match(cont)
                        if im:
                            parts.append(_figure(im.group(1), im.group(2), image_src))
                        else:
                            parts[0] += " " + inline(cont, link_src)
                    items.append("<li>" + "".join(parts) + "</li>")
                elif not lines[i].strip() and i + 1 < n and _LIST_ITEM.match(lines[i + 1]) and not _LIST_ITEM.match(lines[i + 1]).group(1):
                    i += 1
                else:
                    break
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(items) + f"</{tag}>")
            continue
        para: List[str] = []
        while i < n and lines[i].strip() and not _HEADING.match(lines[i].strip()) and not lines[i].strip().startswith(("```", ">", "|")) and not (_LIST_ITEM.match(lines[i]) and not _LIST_ITEM.match(lines[i]).group(1)) and not _IMAGE_LINE.match(lines[i].strip()):
            para.append(lines[i].strip())
            i += 1
        if not para:
            para.append(stripped)
            i += 1
        out.append("<p>" + inline(" ".join(para), link_src) + "</p>")
    return out


def headings(md: str) -> List[tuple]:
    """(level, text) of every ATX heading in a Markdown text, fenced code
    left out."""
    out = []
    in_fence = False
    for ln in md.splitlines():
        if ln.strip().startswith("```"):
            in_fence = not in_fence
            continue
        m = _HEADING.match(ln.strip())
        if m and not in_fence:
            out.append((len(m.group(1)), m.group(2)))
    return out
