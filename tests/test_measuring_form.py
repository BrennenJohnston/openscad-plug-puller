"""Quick-lane rules for the two measuring form sheets and their text twins
(``docs/guides/<tool>/measuring-form.svg`` and ``.md``), drawn by
``scripts/generate_measuring_form.py`` from the parameter mappings and the
catalog's ``measure`` rows.

The sheet is the printed form a person fills in before opening the
Customizer: one row per Step dial in Customizer order, a schematic plug on
the right, and a numbered leader from every measured row to a dimension line
on the schematic. These tests keep the committed sheets in step with the
mappings and the catalog, and keep the twin saying what the sheet shows.

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

from tests.test_dial_catalog import _mapping_rows

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CATALOG_FILE = PROJECT_ROOT / "dial_catalog.json"
TOOLS = ("one-sided", "two-sided")
QUIZ_ANCHORS = {"wall_plate", "plug_sides"}


def _fmt(v: float) -> str:
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return s if s else "0"


def _step_rows(tool: str) -> List[Dict]:
    return [r for r in _mapping_rows(tool) if r["section"].startswith("Step")]


def _measure_rows() -> Dict[Tuple[str, str], Dict]:
    rows = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    return {(r["file"], r["name"]): r for r in rows}


def _svg(tool: str) -> str:
    path = PROJECT_ROOT / "docs" / "guides" / tool / "measuring-form.svg"
    assert path.exists(), f"{path} is missing"
    return path.read_text(encoding="utf-8")


def _twin(tool: str) -> str:
    path = PROJECT_ROOT / "docs" / "guides" / tool / "measuring-form.md"
    assert path.exists(), f"{path} is missing"
    return path.read_text(encoding="utf-8")


def _segments_cross(a: Tuple[float, float, float, float], b: Tuple[float, float, float, float]) -> bool:
    """True when two straight leaders share a point that is not a shared endpoint."""
    def orient(px, py, qx, qy, rx, ry):
        v = (qx - px) * (ry - py) - (qy - py) * (rx - px)
        return 0 if abs(v) < 1e-9 else (1 if v > 0 else -1)

    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    o1 = orient(ax1, ay1, ax2, ay2, bx1, by1)
    o2 = orient(ax1, ay1, ax2, ay2, bx2, by2)
    o3 = orient(bx1, by1, bx2, by2, ax1, ay1)
    o4 = orient(bx1, by1, bx2, by2, ax2, ay2)
    return o1 != o2 and o3 != o4


def test_rows_follow_the_customizer() -> None:
    """The sheet's rows are exactly the mapping's Step dials in mapping order,
    and every numeric row's default reads as the mapping's default with its
    unit."""
    from scripts.generate_measuring_form import OUT_DIRS  # noqa: F401  (the script exists)

    for tool in TOOLS:
        svg = _svg(tool)
        found = re.findall(r'<text[^>]* class="dial" data-row="(\d+)" data-default="([^"]*)"[^>]*>([^<]*)</text>', svg)
        rows = _step_rows(tool)
        assert [name for _, _, name in found] == [r["openscad_name"] for r in rows], (
            f"{tool}: the sheet's rows differ from the mapping's Step dials")
        assert [int(n) for n, _, _ in found] == list(range(1, len(rows) + 1)), f"{tool}: rows are numbered 1..n"
        for (_, default, name), row in zip(found, rows):
            if row["type"] in ("enum", "boolean"):
                expected = str(row["default"]) if row["type"] == "enum" else ("on" if row["default"] else "off")
            else:
                expected = f"{_fmt(row['default'])} {row.get('unit') or 'mm'}"
            assert default == expected, f"{tool} {name}: default {default!r} != {expected!r}"


def test_every_number_row_has_a_leader() -> None:
    """Each row whose catalog measure.anchor is a number anchor has a leader
    group and a dimension group carrying its row number; the two quiz rows
    and the unmeasured rows have neither; no two leaders cross."""
    for tool in TOOLS:
        svg = _svg(tool)
        measures = _measure_rows()
        rows = _step_rows(tool)
        leaders = {int(n) for n in re.findall(r'<g class="leader" data-row="(\d+)">', svg)}
        dimensions = {int(n) for n in re.findall(r'<g class="dimension" data-row="(\d+)">', svg)}
        expected = set()
        for k, row in enumerate(rows, start=1):
            measure = measures[(tool, row["openscad_name"])]["measure"]
            if measure is not None and measure["anchor"] not in QUIZ_ANCHORS:
                expected.add(k)
        assert leaders == expected, f"{tool}: leaders on rows {sorted(leaders)}, expected {sorted(expected)}"
        assert dimensions == expected, f"{tool}: dimension lines on rows {sorted(dimensions)}, expected {sorted(expected)}"
        segments = []
        for n, body in re.findall(r'<g class="leader" data-row="(\d+)">(.*?)</g>', svg, re.S):
            m = re.search(r'<line x1="([\d.]+)" y1="([\d.]+)" x2="([\d.]+)" y2="([\d.]+)"', body)
            assert m, f"{tool}: leader {n} has no line"
            segments.append((int(n), tuple(float(v) for v in m.groups())))
        for i, (n1, s1) in enumerate(segments):
            for n2, s2 in segments[i + 1:]:
                assert not _segments_cross(s1, s2), f"{tool}: leaders {n1} and {n2} cross"


def test_twin_matches() -> None:
    """The Markdown twin's table has the sheet's rows in the same order with
    the same defaults, and its long description names every numbered
    leader."""
    for tool in TOOLS:
        twin = _twin(tool)
        rows = _step_rows(tool)
        measures = _measure_rows()
        table = [ln for ln in twin.splitlines() if re.match(r"\|\s*\d+\s*\|", ln)]
        assert len(table) == len(rows), f"{tool}: the twin's table has {len(table)} rows, the sheet {len(rows)}"
        for k, (line, row) in enumerate(zip(table, rows), start=1):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            assert len(cells) == 5, f"{tool} row {k}: five cells"
            assert int(cells[0]) == k, f"{tool} row {k}: numbered in order"
            assert cells[1] == f"`{row['openscad_name']}`", f"{tool} row {k}: the Customizer name"
            if row["type"] == "enum":
                expected = str(row["default"])
            elif row["type"] == "boolean":
                expected = "on" if row["default"] else "off"
            else:
                expected = f"{_fmt(row['default'])} {row.get('unit') or 'mm'}"
            assert cells[3] == expected, f"{tool} row {k}: default {cells[3]!r} != {expected!r}"
            assert all(len(c.split()) <= 22 for c in cells), f"{tool} row {k}: a cell over 22 words"
        for k, row in enumerate(rows, start=1):
            measure = measures[(tool, row["openscad_name"])]["measure"]
            if measure is not None and measure["anchor"] not in QUIZ_ANCHORS:
                assert f"Arrow {k} points to" in twin, f"{tool}: the twin does not describe arrow {k}"
        assert "Type them into the Customizer in this order." in twin
