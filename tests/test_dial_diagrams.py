"""Tests for ``scripts/generate_dial_diagrams.py``, the per-dial diagram
generator behind ``docs/dials/``.

Quick lane (no OpenSCAD): the diff and the SVG composer on two synthetic
polygons, and the "no shape" diagram. Render lane: two catalog rows
regenerate into a temporary folder and land within one changed region of
the committed index.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import trimesh
from shapely.geometry import Polygon

from scripts.generate_dial_diagrams import (
    LEGEND_LINE,
    NO_SHAPE_SENTENCE,
    changed_regions,
    compose_none_svg,
    compose_pair_svg,
    load_catalog,
    run_rows,
    section_polygons,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INDEX = PROJECT_ROOT / "docs" / "dials" / "dial_diagrams_index.json"
README = PROJECT_ROOT / "docs" / "dials" / "README.md"

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
    """The pair picture's text equivalent: a title, a desc carrying the
    changes sentence and both values, no legend inside the picture (the page
    carries it), nothing fetched from anywhere."""
    region = Polygon([(40, 0), (43, 0), (43, 30), (40, 30)])
    svg = compose_pair_svg(
        before_outline=BEFORE,
        after_outline=AFTER,
        before_plug=None,
        after_plug=None,
        title="Test dial",
        changes="Moves the right edge.",
        name="test_dial",
        before_value=40,
        after_value=43,
        unit="mm",
        context={},
        style="fill",
        crop=None,
        regions_named=[(region, ["body edge"])],
    )
    assert "<title>Test dial</title>" in svg
    assert "<desc>" in svg and "Moves the right edge." in svg
    assert "Before: 40. After: 43." in svg
    for piece in LEGEND_LINE.split("; "):
        assert piece not in svg
    assert "href=" not in svg and "url(http" not in svg


def test_section_polygons_box() -> None:
    """A vertical section of a 40 x 30 x 6 mm box: at x = 0 one polygon of
    30 x 6 mm, at y = 0 one polygon of 40 x 6 mm."""
    box = trimesh.creation.box(extents=(40, 30, 6))
    px = section_polygons(box, axis="x", at=0)
    assert len(px) == 1 and abs(px[0].area - 180.0) < 0.5
    py = section_polygons(box, axis="y", at=0)
    assert len(py) == 1 and abs(py[0].area - 240.0) < 0.5


def test_none_svg() -> None:
    svg = compose_none_svg(note="changes no shape", title="A dial", name="a_dial")
    assert NO_SHAPE_SENTENCE in svg
    assert "changes no shape" in svg
    assert "<title>A dial</title>" in svg


def test_index_covers_catalog() -> None:
    """Every catalog row has an index entry naming the features its trace
    touches (a no-shape row's list is ["none"])."""
    index = {(r["file"], r["name"]): r for r in json.loads(INDEX.read_text(encoding="utf-8"))}
    for row in load_catalog():
        entry = index.get((row["file"], row["name"]))
        assert entry is not None, f"{row['file']}/{row['name']} has no index row"
        features = entry.get("features")
        assert isinstance(features, list) and features, f"{row['name']}: no features"
        if row["diagram"]["view"] == "none":
            assert features == ["none"], row["name"]
        else:
            assert "none" not in features, row["name"]


def test_readme_lists_every_dial() -> None:
    """docs/dials/README.md: one H1, no skipped heading levels, and for every
    catalog row a backticked name, an image whose alt text is the index's
    generated alt, and the long description right under the image."""
    text = README.read_text(encoding="utf-8")
    levels = [len(m.group(1)) for m in re.finditer(r"^(#{1,6}) ", text, re.M)]
    assert levels.count(1) == 1, f"{levels.count(1)} H1 headings"
    for prev, cur in zip(levels, levels[1:]):
        assert cur <= prev + 1, f"heading level jumps from {prev} to {cur}"
    images = {m.group(2): m.group(1) for m in re.finditer(r"!\[([^\]]*)\]\(([^)]+)\)", text)}
    for alt in images.values():
        assert alt.strip(), "an image has empty alt text"
    index = {(r["file"], r["name"]): r for r in json.loads(INDEX.read_text(encoding="utf-8"))}
    text_lines = text.splitlines()
    for row in load_catalog():
        assert f"`{row['name']}`" in text, f"{row['name']} is not listed"
        path = f"{row['file']}/{row['name']}.svg"
        assert path in images, f"{row['name']}: no image line"
        entry = index[(row["file"], row["name"])]
        assert images[path] == entry["alt"], f"{row['name']}: alt text is not the index's alt"
        at = next(i for i, line in enumerate(text_lines) if f"]({path})" in line)
        following = " ".join(text_lines[at + 1:at + 3])
        assert entry["long_description"] in following, f"{row['name']}: the long description does not follow its image"


def test_pair_svg_two_panels() -> None:
    """The pair picture (FD-48): a before panel, an arrow with the two values,
    an after panel whose moved edges alone are red, and a numbered key beside
    it; no dial name and no legend inside the picture."""
    region = Polygon([(40, 0), (43, 0), (43, 30), (40, 30)])
    svg = compose_pair_svg(
        before_outline=BEFORE,
        after_outline=AFTER,
        before_plug=None,
        after_plug=None,
        title="Test dial",
        changes="Moves the right edge.",
        name="test_dial",
        before_value=40,
        after_value=43,
        unit="mm",
        context={},
        style="fill",
        crop=None,
        regions_named=[(region, ["body edge"])],
    )
    assert svg.count('<g class="panel"') == 2
    assert svg.count('<g class="arrow"') == 1
    assert "40 \u2192 43 mm" in svg
    assert svg.count('<g class="key"') == 1 and "1 body edge" in svg
    assert "<title>Test dial</title>" in svg and "<desc>" in svg
    assert "test_dial" not in svg
    for words in ("black =", "teal =", "red dashed", "red dotted ="):
        assert words not in svg
    assert not re.search(r'<path[^>]*fill="#d81b1b"', svg)
    before = svg[svg.index('<g class="panel" id="before"'):svg.index('<g class="arrow"')]
    after = svg[svg.index('<g class="panel" id="after"'):svg.index('<g class="key"')]
    red_paths = re.findall(r'<path[^>]*stroke="#d81b1b"', svg)
    assert red_paths and len(re.findall(r'<path[^>]*stroke="#d81b1b"', after)) == len(red_paths)
    assert "#d81b1b" not in before
    assert "href=" not in svg and "url(http" not in svg


def test_regions_named_in_index() -> None:
    """Every index row carries ``regions_named``, one ``[area_mm2, [names]]``
    pair per changed region in drawing order, whose distinct names are the
    row's ``features``; a no-shape row's list is empty."""
    rows = {(r["file"], r["name"]): r for r in load_catalog()}
    for entry in json.loads(INDEX.read_text(encoding="utf-8")):
        row = rows[(entry["file"], entry["name"])]
        view = row["diagram"]["view"]
        assert "regions_named" in entry, f"{entry['file']}/{entry['name']}: no regions_named"
        named = entry["regions_named"]
        assert isinstance(named, list), entry["name"]
        if view == "none":
            assert named == [], entry["name"]
            continue
        assert len(named) == entry["regions"], entry["name"]
        for item in named:
            assert isinstance(item, list) and len(item) == 2, entry["name"]
            area, names = item
            assert isinstance(area, (int, float)) and area > 0, entry["name"]
            assert isinstance(names, list) and names and all(isinstance(n, str) for n in names), entry["name"]
        distinct = sorted({n for _area, names in named for n in names})
        assert distinct == sorted(entry["features"]), (entry["name"], distinct, entry["features"])


def test_descriptions_follow_rules() -> None:
    """Every index row carries the two-part text alternative of FD-45: an
    alt of at most 150 characters that never opens with "image of" and the
    like, names the row's title and, unless it says "named below", every
    feature red marks; a long description of at most 90 words that opens
    with "Two " (a pair), "One " (a single panel) or "This dial changes no
    shape" (a no-shape row), carries one numbered item per key entry, and
    whose numbered list names only the features of its own tool (the quoted
    changes sentence is the catalog's own words)."""
    from scripts.generate_dial_diagrams import FEATURE_LOCATIONS, SINGLE_PANEL_ROWS

    rows = {(r["file"], r["name"]): r for r in load_catalog()}
    for entry in json.loads(INDEX.read_text(encoding="utf-8")):
        key = (entry["file"], entry["name"])
        row = rows[key]
        alt, long = entry.get("alt"), entry.get("long_description")
        assert isinstance(alt, str) and alt.strip(), f"{key}: no alt"
        assert len(alt) <= 150, (key, len(alt))
        assert not alt.lower().startswith(("image of", "photo of", "picture of", "diagram of")), key
        assert row["title"] in alt, (key, alt)
        if entry["view"] != "none" and key not in SINGLE_PANEL_ROWS and "named below" not in alt:
            for name in entry["features"]:
                assert name in alt, (key, name, alt)
        assert isinstance(long, str) and long.strip(), f"{key}: no long_description"
        assert len(long.split()) <= 90, (key, len(long.split()))
        if entry["view"] == "none":
            assert long.startswith("This dial changes no shape"), key
        elif key in SINGLE_PANEL_ROWS:
            assert long.startswith("One "), key
        else:
            assert long.startswith("Two "), key
            for n, names, _removed in entry["callouts"]:
                assert f"{n}, the {names[0]}" in long, (key, n, names, long)
        own = FEATURE_LOCATIONS[entry["file"]]
        marked = long[long.find("Marked in red:"):] if "Marked in red:" in long else ""
        for other, table in FEATURE_LOCATIONS.items():
            if other == entry["file"]:
                continue
            for name in table:
                if name not in own:
                    assert name not in marked, (key, name)


def test_dimension_callout_endpoints() -> None:
    """A dimension callout on the plug's width at the prong end: the anchor
    gives the plug's top corners, and the picture draws a dimension group
    whose line spans them, labelled with the dial's value."""
    from scripts.generate_dial_diagrams import Outline, anchor_dimension

    body = Polygon([(-20, 0), (20, 0), (20, 60), (-20, 60)])
    recess = Polygon([(-10, 30), (10, 30), (10, 60), (-10, 60)])
    after = Outline(solids=[body], recess=[recess])
    plug = Polygon([(-10, 63), (10, 63), (10, 33), (-10, 33)])
    dim = anchor_dimension("plug_width_prong_end", "one-sided", {}, after, plug, "top", 0.0, 20, "mm")
    assert dim is not None and dim["kind"] == "h"
    assert abs(dim["x0"] - (-10)) < 1e-6 and abs(dim["x1"] - 10) < 1e-6
    assert abs(dim["y_obj"] - 63) < 1e-6 and dim["y_dim"] > 63
    assert dim["label"] == "20 mm"
    svg = compose_pair_svg(
        before_outline=Outline(solids=[body], recess=[recess]),
        after_outline=after,
        before_plug=plug,
        after_plug=plug,
        title="Plug width at the prong end",
        changes="Widens the pocket.",
        name="measure_plug_width_prong_end",
        before_value=18,
        after_value=20,
        unit="mm",
        context={},
        style="fill",
        crop=None,
        regions_named=[],
        dimension=dim,
    )
    assert svg.count('<g class="dimension"') == 1
    group = svg[svg.index('<g class="dimension"'):]
    group = group[:group.index("</g>")]
    assert ">20 mm<" in group
    lines = re.findall(r'<line x1="([\d.-]+)" y1="([\d.-]+)" x2="([\d.-]+)" y2="([\d.-]+)"', group)
    spans = [abs(float(x2) - float(x1)) for x1, y1, x2, y2 in lines if abs(float(y1) - float(y2)) < 1e-6]
    assert any(abs(s - 20) < 0.05 for s in spans), spans


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
