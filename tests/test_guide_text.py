"""The guide sources' Markdown subset turns into the HTML the printed guides
use, and every placeholder a source file asks for exists.

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import re

import pytest

from scripts.guide_text import PLACEHOLDERS, SOURCE_DIR, anchor, fill, headings, load_source, markdown_to_html

SAMPLE = """## Assemble

You need **two** zip ties, see the [bill of materials](../bom.md). <!-- photo: shot 3 -->

1. Seat the tool on the plug.
2. Press the cord into the hook.

   ![The cord pressed into the hook.](../../images/hook.jpg)

3. Pull the tie tight and cut off the tail.

- `strap_width` is the strap you bought
- keep it dry

| Setting | Value |
| ------- | ----- |
| Walls | 3 to 4 |

> Looser always beats tighter.

![Nine tools on the bed.](../../images/bed.jpg)

```bash
openscad -o out.stl
```

Go to <https://openscad.org/downloads.html>.
"""


def test_markdown_subset() -> None:
    out = markdown_to_html(SAMPLE, image_src=lambda p: "file:///abs/" + p.split("/")[-1])
    assert '<h2 id="assemble">Assemble</h2>' in out
    assert "<b>two</b>" in out and '<a href="../bom.md">bill of materials</a>' in out
    assert "shot 3" not in out, "an HTML comment reached the page"
    assert out.count("<ol>") == 1 and out.count("<li>") == 5
    assert '<li>Press the cord into the hook.<figure class="photo"><img src="file:///abs/hook.jpg" alt="The cord pressed into the hook.">' in out
    assert "<code>strap_width</code>" in out
    assert "<table>" in out and "<th>Setting</th>" in out and "<td>3 to 4</td>" in out
    assert "<blockquote><p>Looser always beats tighter.</p></blockquote>" in out
    assert '<figure class="photo"><img src="file:///abs/bed.jpg" alt="Nine tools on the bed."><figcaption>Nine tools on the bed.</figcaption></figure>' in out
    assert "<pre><code>openscad -o out.stl</code></pre>" in out
    assert '<a href="https://openscad.org/downloads.html">https://openscad.org/downloads.html</a>' in out
    assert "<p>Go to " in out


def test_inline_escaping() -> None:
    out = markdown_to_html("A 3 < 4 check & `a<b>` code.")
    assert "3 &lt; 4" in out and "&amp;" in out and "<code>a&lt;b&gt;</code>" in out


def test_fill_and_placeholders() -> None:
    assert fill("the {tool}, {file}", PLACEHOLDERS["one-sided"]) == "the one-sided puller, src/Plug_Puller_Parametric.scad"
    with pytest.raises(KeyError):
        fill("{nonsense}", PLACEHOLDERS["one-sided"])
    assert set(PLACEHOLDERS["one-sided"]) == set(PLACEHOLDERS["two-sided"])


def test_anchor() -> None:
    assert anchor("Step 1 - Your Plug") == "step-1---your-plug"
    assert anchor("Render, export and print") == "render-export-and-print"


def test_every_source_fills_for_both_tools() -> None:
    """Every source file loads for both tools, keeps its headings at H2 or
    deeper (the assembled page owns the H1), and names only images that
    exist."""
    sources = sorted(SOURCE_DIR.glob("*.md"))
    assert sources, f"no guide sources under {SOURCE_DIR}"
    for path in sources:
        for tool in ("one-sided", "two-sided"):
            text = load_source(path.stem, tool)
            for level, heading in headings(text):
                assert level >= 2, f"{path.name}: H1 '{heading}' belongs to the assembled page"
            for target in re.findall(r"!\[[^\]]*\]\(([^)\s]+)\)", text):
                assert (SOURCE_DIR.parent / "one-sided" / target).exists(), f"{path.name}: image {target} is missing"


def test_kind_blocks() -> None:
    """A source keeps a full-guide-only or quick-start-only block for that
    document alone, drops the markers, and keeps every block without a
    document named."""
    both = load_source("stencil-cards", "one-sided")
    quick = load_source("stencil-cards", "one-sided", "quick-start")
    full = load_source("stencil-cards", "one-sided", "full-guide")
    assert "<!--" not in quick and "<!--" not in full and "<!--" not in both
    assert "Folding the tactile flaps" in full and "Folding the tactile flaps" not in quick
    assert "The full guide covers a smaller bed" in quick and "The full guide covers a smaller bed" not in full
    assert "Folding the tactile flaps" in both and "The full guide covers a smaller bed" in both
    assert "\n\n\n" not in quick and "\n\n\n" not in full
    assert "**No 3D printer yet?**" in quick and "**No 3D printer yet?**" in full
