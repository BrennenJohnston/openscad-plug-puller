"""Quick-lane rules for ``dial_catalog.json``, the one data file that names
every Customizer dial of both tool files in plain words and says how to draw
its diagram.

The two parameter mappings (``parameter_mapping.json`` for the one-sided
puller, ``parameter_mapping_two_sided.json`` for the two-sided puller) stay
the source of each dial's default, range, step, type and unit; the catalog
never repeats them. These tests keep the catalog in step with the mappings:
one row per mapped dial, in mapping order, with a nudged ``after`` value the
mapping allows, a real ``context`` and plain-language text.

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List

import pytest

from tests.validate_parameter_schema import ParameterSchemaValidator

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CATALOG_FILE = PROJECT_ROOT / "dial_catalog.json"

FILES = {
    "one-sided": ("src/Plug_Puller_Parametric.scad", "parameter_mapping.json"),
    "two-sided": ("src/Plug_Puller_Two_Sided.scad", "parameter_mapping_two_sided.json"),
}

ROW_KEYS = {"file", "name", "section", "tier", "quick_start", "title", "changes",
            "diagram", "note"}
DIAGRAM_KEYS = {"view", "style", "before", "after", "context", "plug", "crop"}
VIEWS = {"top", "side", "section-x", "section-y", "none"}
STYLES = {"fill", "trace"}
TIERS = {"step", "advanced", "custom"}

BANNED_WORDS = ("leverage", "utilize", "ensure", "facilitate", "streamline",
                "comprehensive", "robust", "seamless", "harness", "empower")
RETIRED_WORDS = ("clamshell", "flat tool", "flat-tool", "step 0", "tool_style",
                 "near the wall", "near the cord")


def _mapping_rows(file_key: str) -> List[Dict[str, Any]]:
    scad_rel, mapping_rel = FILES[file_key]
    validator = ParameterSchemaValidator(PROJECT_ROOT / scad_rel, PROJECT_ROOT / mapping_rel)
    return validator.parameters


@pytest.fixture(scope="module")
def mappings() -> Dict[str, Dict[str, Dict[str, Any]]]:
    """Per file: the mapping rows keyed by ``openscad_name`` (insertion order kept)."""
    return {key: {row["openscad_name"]: row for row in _mapping_rows(key)} for key in FILES}


@pytest.fixture(scope="module")
def catalog() -> List[Dict[str, Any]]:
    if not CATALOG_FILE.exists():
        pytest.fail(f"dial_catalog.json not found at {CATALOG_FILE}")
    with open(CATALOG_FILE, "r", encoding="utf-8") as fh:
        rows = json.load(fh)
    assert isinstance(rows, list), "dial_catalog.json must be a JSON list"
    return rows


def _expected_tier(section: str) -> str:
    if section.startswith("Step"):
        return "step"
    if section.startswith("Advanced"):
        return "advanced"
    return "custom"


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _value_allowed(mapping_row: Dict[str, Any], value: Any) -> bool:
    """True when ``value`` is a value the mapping lets this dial take."""
    ptype = mapping_row["type"]
    if ptype == "enum":
        return value in mapping_row["values"]
    if ptype == "boolean":
        return isinstance(value, bool)
    if not _is_number(value):
        return False
    rng = mapping_row.get("range")
    if rng is None:
        return True
    return rng[0] <= value <= rng[1]


# ---------------------------------------------------------------------------
# a, b: the file, one row per mapped dial, in mapping order
# ---------------------------------------------------------------------------

def test_catalog_exists_and_is_a_list(catalog: List[Dict[str, Any]]) -> None:
    assert catalog, "dial_catalog.json is empty"


def test_one_row_per_mapped_dial_in_mapping_order(catalog, mappings) -> None:
    for file_key, rows in mappings.items():
        names_in_catalog = [r["name"] for r in catalog if r.get("file") == file_key]
        assert names_in_catalog == list(rows.keys()), (
            f"{file_key}: catalog rows must be exactly the mapping's dials in "
            f"the mapping's order")
    unknown = [r for r in catalog if r.get("file") not in FILES]
    assert not unknown, f"rows with an unknown file: {[r.get('name') for r in unknown]}"
    keys = [(r["file"], r["name"]) for r in catalog]
    assert len(keys) == len(set(keys)), "duplicate (file, name) rows"
    files_in_order = [r["file"] for r in catalog]
    first_two_sided = files_in_order.index("two-sided")
    assert all(f == "one-sided" for f in files_in_order[:first_two_sided]), (
        "one-sided rows come first")
    assert all(f == "two-sided" for f in files_in_order[first_two_sided:]), (
        "two-sided rows come last, together")


# ---------------------------------------------------------------------------
# c, d: the row shape, section, tier, quick_start
# ---------------------------------------------------------------------------

def test_row_keys(catalog) -> None:
    for row in catalog:
        assert set(row.keys()) == ROW_KEYS, f"{row.get('name')}: keys {sorted(row.keys())}"
        diagram = row["diagram"]
        assert isinstance(diagram, dict), f"{row['name']}: diagram must be an object"
        extra = set(diagram.keys()) - DIAGRAM_KEYS - {"at"}
        missing = DIAGRAM_KEYS - set(diagram.keys())
        assert not extra and not missing, (
            f"{row['name']}: diagram keys {sorted(diagram.keys())}")


def test_section_tier_and_quick_start(catalog, mappings) -> None:
    for row in catalog:
        mapping_row = mappings[row["file"]][row["name"]]
        assert row["section"] == mapping_row["section"], (
            f"{row['name']}: section {row['section']!r} != mapping {mapping_row['section']!r}")
        assert row["tier"] in TIERS, f"{row['name']}: tier {row['tier']!r}"
        assert row["tier"] == _expected_tier(row["section"]), (
            f"{row['name']}: tier {row['tier']!r} does not match section {row['section']!r}")
        assert isinstance(row["quick_start"], bool), f"{row['name']}: quick_start must be a bool"
        assert row["quick_start"] == row["section"].startswith("Step"), (
            f"{row['name']}: quick_start is true exactly for the Step sections")


# ---------------------------------------------------------------------------
# e: before is the default; after is a real nudge the mapping allows
# ---------------------------------------------------------------------------

def test_before_is_the_default_and_after_is_a_nudge(catalog, mappings) -> None:
    for row in catalog:
        mapping_row = mappings[row["file"]][row["name"]]
        diagram = row["diagram"]
        default = mapping_row["default"]
        assert diagram["before"] == default, (
            f"{row['name']}: before {diagram['before']!r} != mapping default {default!r}")
        after = diagram["after"]
        if diagram["view"] == "none":
            assert after is None, f"{row['name']}: a 'none' row draws nothing, so after is null"
            continue
        ptype = mapping_row["type"]
        if ptype == "enum":
            assert after in mapping_row["values"], (
                f"{row['name']}: after {after!r} is not one of the dropdown's values")
            assert after != default, f"{row['name']}: after equals the default"
        elif ptype == "boolean":
            assert isinstance(after, bool) and after != default, (
                f"{row['name']}: a boolean's after is the other value")
        else:
            assert _is_number(after), f"{row['name']}: after must be a number"
            rng = mapping_row["range"]
            step = mapping_row["step"]
            assert rng[0] <= after <= rng[1], (
                f"{row['name']}: after {after} outside range {rng}")
            assert abs(after - default) >= step - 1e-9, (
                f"{row['name']}: after {after} is less than one step ({step}) from {default}")


# ---------------------------------------------------------------------------
# f: view, style, note, at, crop
# ---------------------------------------------------------------------------

def test_view_style_note_at_and_crop(catalog) -> None:
    for row in catalog:
        diagram = row["diagram"]
        name = row["name"]
        assert diagram["view"] in VIEWS, f"{name}: view {diagram['view']!r}"
        assert diagram["style"] in STYLES, f"{name}: style {diagram['style']!r}"
        if diagram["view"] == "none":
            assert isinstance(row["note"], str) and row["note"].strip(), (
                f"{name}: a 'none' row needs a note saying why")
        else:
            assert row["note"] is None or (isinstance(row["note"], str) and row["note"].strip()), (
                f"{name}: note is null or a non-empty string")
        if "at" in diagram:
            assert diagram["view"].startswith("section-"), (
                f"{name}: 'at' belongs to section views only")
            assert _is_number(diagram["at"]), f"{name}: 'at' must be a number"
        crop = diagram["crop"]
        if crop is not None:
            assert isinstance(crop, list) and len(crop) == 4, f"{name}: crop is [x0, y0, x1, y1]"
            assert all(_is_number(c) for c in crop), f"{name}: crop values must be numbers"
            x0, y0, x1, y1 = crop
            assert x0 < x1 and y0 < y1, f"{name}: crop must have x0 < x1 and y0 < y1"


# ---------------------------------------------------------------------------
# g: context names real dials with valid values; plug is a real preset
# ---------------------------------------------------------------------------

def test_context_and_plug(catalog, mappings) -> None:
    for row in catalog:
        rows_of_file = mappings[row["file"]]
        diagram = row["diagram"]
        context = diagram["context"]
        assert isinstance(context, dict), f"{row['name']}: context must be an object"
        for key, value in context.items():
            assert key in rows_of_file, f"{row['name']}: context names unknown dial {key!r}"
            assert key != row["name"], f"{row['name']}: a dial is not its own context"
            assert _value_allowed(rows_of_file[key], value), (
                f"{row['name']}: context {key}={value!r} is not a value that dial takes")
        plug = diagram["plug"]
        presets = rows_of_file["plug_preset"]["values"]
        assert plug == "default" or plug in presets, (
            f"{row['name']}: plug {plug!r} is neither 'default' nor a plug_preset value")


# ---------------------------------------------------------------------------
# h: the words
# ---------------------------------------------------------------------------

def test_title_and_changes_wording(catalog) -> None:
    for row in catalog:
        name = row["name"]
        title = row["title"]
        changes = row["changes"]
        assert isinstance(title, str) and title.strip(), f"{name}: empty title"
        assert isinstance(changes, str) and changes.strip(), f"{name}: empty changes"
        assert "`" not in title, f"{name}: title must not contain backticks"
        assert changes.endswith("."), f"{name}: changes must end with a period"
        assert ". " not in changes, f"{name}: changes must be one sentence"
        for text, label in ((title, "title"), (changes, "changes")):
            lowered = text.lower()
            for word in BANNED_WORDS:
                assert not re.search(rf"\b{word}\b", lowered), (
                    f"{name}: {label} uses the banned word {word!r}")
            for word in RETIRED_WORDS:
                assert word not in lowered, f"{name}: {label} uses the retired word {word!r}"


def test_counts(catalog) -> None:
    assert len(catalog) == 118, f"expected 118 rows, found {len(catalog)}"
    assert sum(1 for r in catalog if r["quick_start"]) == 28, "28 quick-start rows (Steps 1-4)"
