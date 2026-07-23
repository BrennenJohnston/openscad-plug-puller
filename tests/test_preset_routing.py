"""Plug Puller size routing tests.

These tests verify the *contract* between ``src/presets.scad``,
``src/fit_measured.scad``, and ``src/Plug_Puller_Parametric.scad``
after the v5.1 size/attachment rework:

1. ``PRESET_MEDIUM`` (the measured original-device reference table) and the
   computed ``FIT_MEASURED`` table cover exactly the same key set.
2. Every key referenced via ``preset_value(_p, "<key>", ...)`` in the main
   SCAD has a corresponding row in both tables — otherwise a measured size
   would silently leak through to the ``custom_*`` sliders.
3. Every ``preset_value`` call uses the matching ``custom_<key>`` slider as
   its fallback argument (so "Custom" preserves the user's slider value).
4. ``preset_lookup`` / ``preset_value`` return ``undef``/``fallback`` for
   unknown keys and route "Custom" / "Medium Defaults" correctly.
5. The include order (fit_measured before presets) is pinned — OpenSCAD
   evaluates top-level assignments in source order, so FIT_MEASURED must
   exist before ``preset_value()`` first resolves against it.

All assertions parse source files; no OpenSCAD render is required, so the
quick CI lane can run them in well under a second.

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, Set

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCAD_FILE = PROJECT_ROOT / "src" / "Plug_Puller_Parametric.scad"
PRESETS_FILE = PROJECT_ROOT / "src" / "presets.scad"
FIT_MEASURED_FILE = PROJECT_ROOT / "src" / "fit_measured.scad"


def _parse_preset_table(presets_source: str, table_name: str) -> Dict[str, Any]:
    """Extract a ``TABLE = [["key", value], ...]`` table into a dict.

    Numeric values are returned as int when no decimal point is present,
    else float. Booleans are returned as Python bools. Other tokens are
    returned as strings (quoted strings keep their quotes stripped;
    arithmetic expressions like ``32 / 15`` are evaluated).
    """
    block_re = re.compile(
        rf"{re.escape(table_name)}\s*=\s*\[(.*?)\]\s*;", re.DOTALL
    )
    block_match = block_re.search(presets_source)
    assert block_match, (
        f"Could not locate `{table_name}`. The size routing contract depends "
        f"on this declaration."
    )
    body = block_match.group(1)
    row_re = re.compile(r'\[\s*"([^"]+)"\s*,\s*([^\]]+?)\s*\]')
    out: Dict[str, Any] = {}
    for key, raw_value in row_re.findall(body):
        raw = raw_value.strip()
        if raw == "true":
            out[key] = True
        elif raw == "false":
            out[key] = False
        elif raw.startswith('"') and raw.endswith('"'):
            out[key] = raw.strip('"')
        elif re.fullmatch(r"-?\d+", raw):
            out[key] = int(raw)
        elif re.fullmatch(r"-?\d+\.\d*([eE][+\-]?\d+)?", raw):
            out[key] = float(raw)
        elif re.fullmatch(r"[\d\s./*+()-]+", raw):
            out[key] = float(eval(raw))  # noqa: S307 — numeric literals only
        else:
            out[key] = raw
    return out


def _parse_table_keys(source: str, table_name: str) -> Set[str]:
    """Extract only the KEYS of a ``TABLE = [["key", <expr>], ...]`` table.

    FIT_MEASURED's values are derivation *expressions*
    (``_fit_puller_length`` etc.), not literals, so the value parser of
    :func:`_parse_preset_table` must not be reused here.
    """
    block_re = re.compile(
        rf"{re.escape(table_name)}\s*=\s*\[(.*?)\]\s*;", re.DOTALL
    )
    block_match = block_re.search(source)
    assert block_match, (
        f"Could not locate `{table_name}` — the size routing contract "
        f"depends on this declaration."
    )
    key_re = re.compile(r'\[\s*"([^"]+)"\s*,')
    return set(key_re.findall(block_match.group(1)))


def _extract_preset_value_calls(scad_source: str) -> Dict[str, str]:
    """Map every ``preset_value(_p, "<key>", <fallback>)`` -> fallback expression."""
    call_re = re.compile(
        r'preset_value\(\s*_p\s*,\s*"(\w+)"\s*,\s*([^)]+?)\s*\)'
    )
    out: Dict[str, str] = {}
    for match in call_re.finditer(scad_source):
        key = match.group(1)
        fallback = match.group(2).strip()
        out[key] = fallback
    return out


@pytest.fixture(scope="module")
def presets_source() -> str:
    assert PRESETS_FILE.exists(), f"presets.scad missing: {PRESETS_FILE}"
    return PRESETS_FILE.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def scad_source() -> str:
    assert SCAD_FILE.exists(), f"v5 SCAD missing: {SCAD_FILE}"
    return SCAD_FILE.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def fit_measured_source() -> str:
    assert FIT_MEASURED_FILE.exists(), (
        f"fit_measured.scad missing: {FIT_MEASURED_FILE}"
    )
    return FIT_MEASURED_FILE.read_text(encoding="utf-8")


class TestMediumTable:
    """Structural checks on the PRESET_MEDIUM reference table."""

    def test_table_parses(self, presets_source: str) -> None:
        table = _parse_preset_table(presets_source, "PRESET_MEDIUM")
        assert table, "Parsed `PRESET_MEDIUM` is empty — regex or format drift?"

    def test_table_has_minimum_size(self, presets_source: str) -> None:
        table = _parse_preset_table(presets_source, "PRESET_MEDIUM")
        # The v6 MakerWorld cleanup ships 48 [key, value] rows (side clamp,
        # Steps plates, and dropdown-owned keys removed). Treat the current
        # value as a floor to catch accidental truncation.
        assert len(table) >= 40, (
            f"PRESET_MEDIUM has only {len(table)} keys; expected at least 40. "
            f"Did a refactor drop rows?"
        )

    def test_medium_matches_original_device_anchors(
        self, presets_source: str
    ) -> None:
        """Spot-pin the measured v6 CAD-reference dimensions (inch-native).

        These literals were measured from the v6 CAD reference ("Plug Puller
        3.1 - B") during development in the historical dev repo. If one
        changes, the Medium size no longer reproduces the v6 reference device.
        """
        table = _parse_preset_table(presets_source, "PRESET_MEDIUM")
        anchors = {
            "puller_length": 65.5,
            "body_thickness": 6.35,          # 1/4 in
            "finger_hole_diameter": 25.4,    # 1 in
            "finger_hole_spacing": 33,
            "finger_hole_y_position": 21.8,
            "t_hook_base_gap": 4.7625,       # 3/16 in
            "t_hook_length": 10.16,          # 2/5 in
            "t_hook_holder_width": 11.1125,  # 7/16 in
            "t_hook_holder_length": 5.08,    # 1/5 in
            "t_hook_stem_offset": 4.5,       # J-hook stem offset
            "t_hook_catch_reach": 4.55,      # J-hook catch lip
            "plug_wall_notch_width": 26.67,  # 1.05 in
            "plug_wall_notch_height": 3.81,  # 0.15 in
            "zip_tie_hole_diameter": 5.08,   # 1/5 in
            "zip_tie_height_spacing": 17.78, # 0.7 in
            "zip_tie_width_spacing": 17.7,
            "pocket_seat_diameter": 30.5,
            "pocket_width": 31.7,
            "pocket_depth": 25.5,
            "pocket_seat_floor": 3.175,      # 1/8 in (seat floor height)
            "pocket_floor": 3.81,            # plug-recess floor height
        }
        mismatches = [
            (key, expected, table.get(key))
            for key, expected in anchors.items()
            if table.get(key) != pytest.approx(expected)
        ]
        assert not mismatches, (
            "PRESET_MEDIUM no longer matches the measured original device:\n"
            + "\n".join(
                f"  - {k}: expected {e!r}, table has {a!r}"
                for k, e, a in mismatches
            )
        )


class TestPresetValueRouting:
    """``preset_value`` <-> table key parity."""

    def test_every_preset_value_key_exists_in_tables(
        self,
        scad_source: str,
        presets_source: str,
        fit_measured_source: str,
    ) -> None:
        calls = _extract_preset_value_calls(scad_source)
        assert calls, (
            "No `preset_value(_p, \"...\", ...)` calls found in the v5 SCAD. "
            "Did the size routing refactor get reverted?"
        )
        for table_name, source in (
            ("PRESET_MEDIUM", presets_source),
            ("FIT_MEASURED", fit_measured_source),
        ):
            keys = _parse_table_keys(source, table_name)
            missing = sorted(set(calls.keys()) - keys)
            assert not missing, (
                f"preset_value() keys referenced by the main SCAD have no "
                f"row in {table_name}. A measured size would silently fall "
                f"through to `custom_*` for these:\n"
                + "\n".join(f"  - {k}" for k in missing)
            )

    def test_every_medium_key_consumed_by_main(
        self, scad_source: str, presets_source: str
    ) -> None:
        calls = _extract_preset_value_calls(scad_source)
        medium = _parse_preset_table(presets_source, "PRESET_MEDIUM")
        unused = sorted(set(medium.keys()) - set(calls.keys()))
        assert not unused, (
            "PRESET_MEDIUM declares keys that the main SCAD never reads via "
            "`preset_value`. These are dead data:\n"
            + "\n".join(f"  - {k}" for k in unused)
        )

    def test_fallback_is_matching_custom_slider(self, scad_source: str) -> None:
        """Each ``preset_value(_p, "<key>", <fallback>)`` uses ``custom_<key>``."""
        calls = _extract_preset_value_calls(scad_source)
        wrong_fallbacks = []
        for key, fallback in calls.items():
            expected = f"custom_{key}"
            if fallback != expected:
                wrong_fallbacks.append((key, fallback, expected))
        assert not wrong_fallbacks, (
            "preset_value() fallback (third argument) must equal `custom_<key>` "
            "so Custom mode preserves the user's slider value:\n"
            + "\n".join(
                f"  - key='{k}': got `{got}`, expected `{exp}`"
                for k, got, exp in wrong_fallbacks
            )
        )


class TestFitMeasuredTable:
    """``FIT_MEASURED`` routing and key-parity contract."""

    def test_fit_measured_key_parity_with_medium(
        self, fit_measured_source: str, presets_source: str
    ) -> None:
        """FIT_MEASURED must cover exactly PRESET_MEDIUM's key set.

        A missing key would silently fall through to the user's `custom_*`
        slider in the measured sizes; an extra key would be dead data.
        """
        fit_keys = _parse_table_keys(fit_measured_source, "FIT_MEASURED")
        medium_keys = set(
            _parse_preset_table(presets_source, "PRESET_MEDIUM").keys()
        )
        assert fit_keys == medium_keys, (
            "FIT_MEASURED and PRESET_MEDIUM disagree on the key set:\n"
            f"  missing from FIT_MEASURED: {sorted(medium_keys - fit_keys)}\n"
            f"  extra in FIT_MEASURED:     {sorted(fit_keys - medium_keys)}"
        )

    def test_main_scad_includes_fit_measured_before_presets(
        self, scad_source: str
    ) -> None:
        """Include-order contract: FIT_MEASURED must be assigned before
        presets.scad's `preset_value()` references it (OpenSCAD evaluates
        top-level assignments in source order)."""
        fit_idx = scad_source.find("include <fit_measured.scad>")
        presets_idx = scad_source.find("include <presets.scad>")
        assert fit_idx != -1, "Main SCAD no longer includes fit_measured.scad."
        assert presets_idx != -1, "Main SCAD no longer includes presets.scad."
        assert fit_idx < presets_idx, (
            "`include <fit_measured.scad>` must precede `include "
            "<presets.scad>` — otherwise FIT_MEASURED is undef when "
            "preset_value() resolves a measured size."
        )


class TestPresetHelperContract:
    """``preset_lookup`` / ``preset_value`` invariants."""

    def test_preset_lookup_uses_wrapped_search(self, presets_source: str) -> None:
        """``search([key], list)`` is the only form that does whole-string match.

        OpenSCAD's bare ``search(key, list)`` treats ``key`` as a sequence of
        characters and matches per-character — silently wrong for our string
        keys. Guard against an accidental refactor that drops the wrap.
        """
        assert re.search(
            r"function\s+preset_lookup\b[^{}]*?search\s*\(\s*\[\s*key\s*\]",
            presets_source,
            re.DOTALL,
        ), (
            "`preset_lookup` no longer uses the `search([key], list)` wrapped "
            "form. OpenSCAD's bare `search(key, list)` does per-character "
            "matching and will silently mismatch keys."
        )

    def test_preset_lookup_returns_undef_on_miss(self, presets_source: str) -> None:
        assert re.search(
            r"is_num\(\s*m\[0\]\s*\)\s*\?\s*preset_list\[\s*m\[0\]\s*\]\[\s*1\s*\]\s*:\s*undef",
            presets_source,
        ), (
            "`preset_lookup` must return `undef` when the key is not found "
            "(checked via `is_num(m[0])`). The miss-shape of OpenSCAD's "
            "search() is `[[]]`, so a naive `m[0] != []` check silently fails."
        )

    def test_preset_value_routing_chain(self, presets_source: str) -> None:
        """Custom -> undef (fallback), Medium Defaults -> PRESET_MEDIUM,
        everything else -> FIT_MEASURED."""
        assert re.search(
            r'p\s*==\s*"Custom"\s*\?\s*undef', presets_source
        ), "`preset_value` must route 'Custom' to undef (slider fallback)."
        assert re.search(
            r'p\s*==\s*"Medium Defaults"\s*\?\s*preset_lookup\(\s*PRESET_MEDIUM',
            presets_source,
        ), (
            "`preset_value` must route the internal 'Medium Defaults' name "
            "(one-shot reset_custom_to_medium) to PRESET_MEDIUM."
        )
        assert re.search(
            r"preset_lookup\(\s*FIT_MEASURED\s*,\s*key\s*\)", presets_source
        ), "`preset_value` must route measured sizes to FIT_MEASURED."
        # Helper terminator: `val == undef ? fallback : val`.
        assert re.search(
            r"val\s*==\s*undef\s*\?\s*fallback\s*:\s*val", presets_source
        ), "`preset_value` must return `fallback` when the lookup misses."

    def test_reset_rewrites_custom_to_medium_defaults(
        self, scad_source: str
    ) -> None:
        assert re.search(
            r'_p\s*=\s*\(\s*size\s*==\s*"Custom"\s*&&\s*reset_custom_to_medium\s*\)'
            r'\s*\?\s*"Medium Defaults"\s*:\s*size\s*;',
            scad_source,
        ), (
            "The one-shot reset contract changed: `_p` must rewrite "
            "Custom + reset_custom_to_medium to the internal "
            "'Medium Defaults' name."
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
