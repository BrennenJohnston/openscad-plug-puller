"""The plug size finder page (``scripts/generate_plug_finder.py``).

The page is a 1:1 print a person lays their plug on, so its numbers are the
accessibility feature: every outline must be exactly as long and as wide as
its preset, every preset of both tool files must be on the page once, in the
right tool's group, and the calibration square must be 50 mm. The committed
SVG must be what the script writes today.

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts import generate_plug_finder as finder  # noqa: E402
from scripts.generate_outline_sheets import ONE_SIDED, PLUG_PRESETS, TWO_SIDED  # noqa: E402

ONE_SIDED_SCAD = PROJECT_ROOT / "src" / "Plug_Puller_Parametric.scad"
TWO_SIDED_SCAD = PROJECT_ROOT / "src" / "Plug_Puller_Two_Sided.scad"
TOLERANCE = 0.02  # mm; the rounded corners never touch the measured extents


def _dropdown(scad: Path) -> list:
    text = scad.read_text(encoding="utf-8")
    match = re.search(r'^plug_preset\s*=\s*"[^"]+"\s*;\s*//\s*\[([^\]]+)\]', text, re.M)
    assert match, f"no plug_preset dropdown in {scad.name}"
    return [o.strip() for o in match.group(1).split(",")][1:]


def test_every_preset_of_both_files_is_on_the_page_once() -> None:
    labels = [PLUG_PRESETS[k]["customizer"] for k in finder.SHAPES]
    assert sorted(labels) == sorted(_dropdown(ONE_SIDED_SCAD) + _dropdown(TWO_SIDED_SCAD))
    assert len(set(labels)) == len(labels)


@pytest.mark.parametrize("key", list(finder.SHAPES))
def test_outline_is_its_preset_size(key: str) -> None:
    shape = finder.SHAPES[key]
    nums = finder.preset_numbers(key)
    minx, miny, maxx, maxy = finder.outline(shape).bounds
    assert maxy - miny == pytest.approx(nums["measure_plug_length"], abs=TOLERANCE)
    first, last = shape.stations[0], shape.stations[-1]
    widest = max(w for _y, w in shape.stations)
    assert first[0] == 0.0 and first[1] <= widest
    assert widest == pytest.approx(nums["measure_plug_width_prong_end"])
    assert last[1] == pytest.approx(nums["measure_plug_width_cord_end"])
    assert maxx - minx == pytest.approx(widest, abs=TOLERANCE)


@pytest.mark.parametrize("key", list(finder.SHAPES))
def test_prongs_match_the_tool(key: str) -> None:
    """3 prongs are the two-sided puller's; 2 prongs and the USB-C tip the
    one-sided puller's: the rule the page teaches."""
    prongs = finder.SHAPES[key].prongs
    tool = finder.tool_of(key)
    assert tool == (TWO_SIDED if prongs == "3" else ONE_SIDED), f"{key}: {prongs} prongs in the {tool} group"
    x0, x1 = finder.GROUP_SPANS[tool]
    assert x0 <= finder.COLUMNS[key] <= x1


def test_outlines_and_labels_stay_apart() -> None:
    """No outline reaches its neighbor's, and no two label lines overlap
    (Helvetica bold averages 0.55 em a character)."""
    keys = sorted(finder.SHAPES, key=lambda k: finder.COLUMNS[k])
    for a, b in zip(keys, keys[1:]):
        wa = max(w for _y, w in finder.SHAPES[a].stations) / 2
        wb = max(w for _y, w in finder.SHAPES[b].stations) / 2
        assert finder.COLUMNS[a] + wa + 5 < finder.COLUMNS[b] - wb, f"{a} and {b} outlines too close"
        la = max(len(s) for s in finder.label_lines(a)) * 3.0 * 0.55 / 2
        lb = max(len(s) for s in finder.label_lines(b)) * 3.0 * 0.55 / 2
        assert finder.COLUMNS[a] + la < finder.COLUMNS[b] - lb, f"{a} and {b} labels overlap"


def test_page_size_and_calibration_square() -> None:
    svg = finder.build_page().svg()
    assert 'width="210mm" height="279mm" viewBox="0 0 210 279"' in svg
    x, y = finder.CAL
    assert f'<rect x="{x:.3f}" y="{y:.3f}" width="50.000" height="50.000"' in svg


def test_every_drawing_stays_on_the_page() -> None:
    for key, shape in finder.SHAPES.items():
        cx = finder.COLUMNS[key]
        length = shape.stations[-1][0]
        top = finder.Y_FACE - max(finder.PIN_L, finder.BLADE_L, finder.USB_TIP_L)
        bottom = finder.Y_FACE + length + finder.CORD_RUN + 1.2
        assert top > 45.0, f"{key}: prongs reach the group heading"
        assert bottom < finder.LABEL_Y - 4.0, f"{key}: cord reaches the label"
        assert 5.0 < cx - max(w for _y, w in shape.stations) / 2


def test_committed_page_is_fresh() -> None:
    committed = finder.DEFAULT_OUT.read_text(encoding="utf-8")
    assert committed == finder.build_page().svg(), (
        "docs/guides/plug-size-finder.svg is stale: run python scripts/generate_plug_finder.py")


def test_text_equivalent_lists_every_outline() -> None:
    text = finder.finder_text()
    for key in finder.SHAPES:
        assert f"| {PLUG_PRESETS[key]['customizer']} |" in text
