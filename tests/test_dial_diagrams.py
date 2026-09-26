"""Tests for ``scripts/generate_dial_diagrams.py``, the per-dial diagram
generator behind ``docs/dials/``.

Quick lane (no OpenSCAD): the diff and the SVG composer on two synthetic
polygons, and the "no shape" diagram. Render lane: two catalog rows
regenerate into a temporary folder and land within one changed region of
the committed index.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from shapely.geometry import Polygon

from scripts.generate_dial_diagrams import (
    LEGEND_LINE,
    NO_SHAPE_SENTENCE,
    changed_regions,
    compose_none_svg,
    compose_svg,
    load_catalog,
    run_rows,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INDEX = PROJECT_ROOT / "docs" / "dials" / "dial_diagrams_index.json"

BEFORE = Polygon([(0, 0), (40, 0), (40, 30), (0, 30)])
AFTER = Polygon([(0, 0), (43, 0), (43, 30), (0, 30)])


def test_changed_regions_synthetic() -> None:
    regions, area = changed_regions(BEFORE, AFTER)
    assert len(regions) == 1
    assert abs(area - 90.0) < 0.5
    assert abs(regions[0].area - 90.0) < 0.5


def test_small_slivers_dropped() -> None:
    regions, area = changed_regions(BEFORE, BEFORE.buffer(0.005))
    assert regions == []
    assert area == 0.0


def test_svg_text_equivalent() -> None:
    svg = compose_svg(
        before=BEFORE,
        after=AFTER,
        plug=None,
        title="Test dial",
        changes="Moves the right edge.",
        name="test_dial",
        before_value=40,
        after_value=43,
        context={},
        style="fill",
        crop=None,
    )
    assert "<title>Test dial</title>" in svg
    assert "<desc>" in svg and "Moves the right edge." in svg
    assert "Before: 40. After: 43." in svg
    for piece in LEGEND_LINE.split("; "):
        assert piece in svg
    assert svg.count('stroke="#d81b1b"') == 1
    assert "href=" not in svg and "url(http" not in svg


def test_none_svg() -> None:
    svg = compose_none_svg(note="changes no shape", title="A dial", name="a_dial")
    assert NO_SHAPE_SENTENCE in svg
    assert "changes no shape" in svg
    assert "<title>A dial</title>" in svg


@pytest.mark.requires_openscad
@pytest.mark.slow
def test_two_rows_regenerate_within_one_region(tmp_path: Path) -> None:
    """The two planning-prototype dials come out within one changed region of
    the committed index (identical renders are not byte-identical, so region
    counts, not files, are compared)."""
    committed = {
        (row["file"], row["name"]): row for row in json.loads(INDEX.read_text(encoding="utf-8"))
    }
    wanted = [("one-sided", "measure_plug_width_prong_end"), ("two-sided", "plate_wall_boost")]
    rows = [r for r in load_catalog() if (r["file"], r["name"]) in wanted]
    assert len(rows) == 2
    produced = run_rows(rows, out_dir=tmp_path / "dials", cache_dir=tmp_path / "cache", force=True)
    assert len(produced) == 2
    for entry in produced:
        ref = committed[(entry["file"], entry["name"])]
        assert abs(entry["regions"] - ref["regions"]) <= 1, (entry["name"], entry["regions"], ref["regions"])
        assert (tmp_path / "dials" / entry["svg"]).exists()
