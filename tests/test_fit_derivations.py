"""Tests for the measurement → parameter derivation layer.

Two lanes:

* **Quick lane** (no OpenSCAD): drives :mod:`tests.fit_formulas` — the
  pure-Python mirror of ``src/fit_measured.scad`` — through the
  Medium-parity invariant, clamp-edge vectors, size-override precedence,
  and monotonicity spot checks.
* **Render lane** (``@requires_openscad``): renders the SCAD with
  ``-o <tmp>.echo`` for several input vectors and asserts every
  ``fit_derived: <key>=<value>`` line matches the Python formulas
  (the SCAD-vs-Python derivation contract), plus a mesh-level golden
  comparison of the "Measure my hand" default render against the ``medium``
  fixture (the Medium-parity invariant, end to end).

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any, Dict

import pytest

from tests.fit_formulas import (
    DEFAULT_MEASUREMENTS,
    FIT_SIZE_TABLE,
    FIT_ZIP_FINGER_WEB,
    derive,
)
from tests.test_preset_routing import _parse_preset_table

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PRESETS_FILE = PROJECT_ROOT / "src" / "presets.scad"
MAPPING_FILE = PROJECT_ROOT / "parameter_mapping.json"

# Slider min/max per numeric measurement input (mirrors the SCAD Customizer
# declarations; also validated against parameter_mapping.json in the schema
# lint). These double as the W-1 plausibility windows.
MEASURE_RANGES: Dict[str, tuple[float, float]] = {
    "measure_plug_length": (12, 85),
    "measure_plug_width_wall": (12, 45),
    "measure_plug_width_cable": (12, 45),
    "measure_plug_thickness_wall": (8, 40),
    "measure_plug_thickness_cable": (8, 40),
    "measure_cord_thickness": (2, 9),
    "measure_finger_width": (14, 32),
    "measure_hand_width": (60, 110),
}

# Derived keys whose values may legitimately leave the `custom_<key>` slider
# range at extreme measurements. The schema slider bounds are Custom-mode UI
# affordances, not physical safety bounds — safety for these keys comes from
# the derivation clamp chain plus the main SCAD's always-on auto-fit, which
# re-clamps placement against the body envelope at render time. The widened
# bounds below are the derivation clamps' own hard limits.
RANGE_EXCEPTIONS: Dict[str, tuple[float, float]] = {
    # Velcro placement is derived from the body envelope; auto-fit re-clamps
    # the final position at render time.
    "velcro_hole_x_center": (0, 45),
    "velcro_hole_y_center": (25, 110),
    # Dome pocket dimensions have their own derivation clamps. The pocket
    # depth follows the full plug length (D-19's 120 mm-ceiling budget), so
    # its bound is the measure_plug_length slider maximum.
    "pocket_seat_diameter": (10, 45),
    "pocket_width": (10, 45),
    "pocket_depth": (5, 85),
    # J-hook catch scales with the cord/crossbar; auto-fit re-clamps the stem
    # offset and catch reach against the crossbar at render time. Upper bounds
    # are the derivation maxima at the thickest cord (measure_cord_thickness 9).
    "t_hook_stem_offset": (0, 10),
    "t_hook_catch_reach": (0, 10),
}

# The "realistic vacuum plug" vector (pins the derivation → geometry path
# somewhere other than the parity point; also the `measured_hand` golden
# fixture's parameter set). Straight-sided 34-wide / 16-thick body, so both
# stations carry the same value — the derived geometry is identical to the
# pre-two-station fixture.
VACUUM_PLUG_VECTOR: Dict[str, Any] = {
    "size": "Measure my hand",
    "measure_plug_length": 38,
    "measure_plug_width_wall": 34,
    "measure_plug_width_cable": 34,
    "measure_plug_thickness_wall": 16,
    "measure_plug_thickness_cable": 16,
    "measure_cord_thickness": 5,
    "measure_wall_plate_style": "Rocker / Decora",
    "measure_finger_width": 22,
    "measure_hand_width": 88,
}

ALL_MIN_VECTOR: Dict[str, Any] = {
    "size": "Measure my hand",
    **{k: lo for k, (lo, _hi) in MEASURE_RANGES.items()},
}
ALL_MAX_VECTOR: Dict[str, Any] = {
    "size": "Measure my hand",
    **{k: hi for k, (_lo, hi) in MEASURE_RANGES.items()},
}


@pytest.fixture(scope="module")
def medium_table() -> Dict[str, Any]:
    source = PRESETS_FILE.read_text(encoding="utf-8")
    return _parse_preset_table(source, "PRESET_MEDIUM")


@pytest.fixture(scope="module")
def custom_slider_ranges() -> Dict[str, tuple[float, float]]:
    """Map derived key -> (min, max) of the matching `custom_<key>` slider."""
    with open(MAPPING_FILE, "r", encoding="utf-8") as fh:
        mapping = json.load(fh)
    out: Dict[str, tuple[float, float]] = {}
    for param in mapping["parameters"]:
        name = param["openscad_name"]
        if not name.startswith("custom_") or "range" not in param:
            continue
        out[name[len("custom_"):]] = (
            float(param["range"][0]),
            float(param["range"][1]),
        )
    return out


class TestMediumParity:
    """The calibration invariant: size=Medium at default measurements
    reproduces PRESET_MEDIUM (= the measured original device) exactly."""

    def test_medium_parity(self, medium_table: Dict[str, Any]) -> None:
        derived = derive()
        assert set(derived.keys()) == set(medium_table.keys()), (
            "FIT_MEASURED (Python mirror) and PRESET_MEDIUM disagree on the "
            "key set — the routing contract requires identical keys.\n"
            f"  only in derived: {sorted(set(derived) - set(medium_table))}\n"
            f"  only in medium:  {sorted(set(medium_table) - set(derived))}"
        )
        mismatches = []
        for key, expected in medium_table.items():
            actual = derived[key]
            if isinstance(expected, bool) or isinstance(actual, bool):
                ok = expected == actual
            elif isinstance(expected, str) or isinstance(actual, str):
                ok = str(expected) == str(actual)
            else:
                ok = abs(float(expected) - float(actual)) < 1e-9
            if not ok:
                mismatches.append((key, expected, actual))
        assert not mismatches, (
            "Medium defaults must reproduce PRESET_MEDIUM exactly (the "
            "original-device calibration invariant):\n"
            + "\n".join(
                f"  - {k}: medium={e!r}, derived={a!r}" for k, e, a in mismatches
            )
        )

    def test_measure_my_hand_defaults_equal_medium(self) -> None:
        """'Measure my hand' with default sliders (20 / 85) must equal the
        Medium size — the Medium hand pair IS the default slider pair."""
        assert derive({"size": "Measure my hand"}) == derive({"size": "Medium"})

    def test_default_vector_matches_scad_defaults(self) -> None:
        """The Python defaults must equal the SCAD input declarations."""
        scad = (
            PROJECT_ROOT / "src" / "Plug_Puller_Parametric.scad"
        ).read_text(encoding="utf-8")
        for name, expected in DEFAULT_MEASUREMENTS.items():
            match = re.search(rf"^{name}\s*=\s*([^;]+);", scad, re.MULTILINE)
            assert match, f"`{name}` not declared in the v6 SCAD"
            raw = match.group(1).strip()
            if raw.startswith('"'):
                assert raw.strip('"') == expected, (
                    f"Default mismatch for {name}: scad={raw}, python={expected!r}"
                )
            else:
                assert abs(float(raw) - float(expected)) < 1e-9, (
                    f"Default mismatch for {name}: scad={raw}, python={expected!r}"
                )


class TestClampEdges:
    """No input vector may escape the documented value ranges."""

    @pytest.mark.parametrize(
        "vector_name,vector",
        [(f"{key}={val}", {"size": "Measure my hand", key: val})
         for key, (lo, hi) in MEASURE_RANGES.items()
         for val in (lo, hi)]
        + [
            ("all_min", ALL_MIN_VECTOR),
            ("all_max", ALL_MAX_VECTOR),
            ("vacuum_plug", VACUUM_PLUG_VECTOR),
            ("small_extremes", {"size": "Small",
                                "measure_plug_width_wall": 45,
                                "measure_plug_width_cable": 45,
                                "measure_plug_length": 85}),
            ("large_extremes", {"size": "Large",
                                "measure_plug_width_wall": 12,
                                "measure_plug_width_cable": 12,
                                "measure_plug_length": 12}),
            ("fat_at_cable", {"size": "Medium",
                              "measure_plug_width_wall": 20,
                              "measure_plug_width_cable": 34,
                              "measure_plug_thickness_wall": 18,
                              "measure_plug_thickness_cable": 30,
                              "measure_plug_length": 62}),
        ],
    )
    def test_clamp_edges(
        self,
        vector_name: str,
        vector: Dict[str, Any],
        custom_slider_ranges: Dict[str, tuple[float, float]],
    ) -> None:
        derived = derive(vector)
        violations = []
        for key, value in derived.items():
            if isinstance(value, (bool, str)):
                continue
            lo_hi = RANGE_EXCEPTIONS.get(key) or custom_slider_ranges.get(key)
            if lo_hi is None:
                continue
            lo, hi = lo_hi
            if not (lo - 1e-9 <= float(value) <= hi + 1e-9):
                violations.append((key, value, lo, hi))
        assert not violations, (
            f"Vector '{vector_name}' produced out-of-range derived values:\n"
            + "\n".join(
                f"  - {k} = {v} outside [{lo}, {hi}]" for k, v, lo, hi in violations
            )
        )

    @pytest.mark.parametrize("style,expected_depth", [
        ("Standard flat plate", 3.81),
        ("Rocker / Decora", 5.3),
        ("Oversized / Jumbo", 6.3),
        ("No plate / flush", 1.5),
    ])
    def test_wall_plate_style_lookup(self, style: str, expected_depth: float) -> None:
        derived = derive({"measure_wall_plate_style": style})
        assert derived["plug_wall_notch_height"] == pytest.approx(expected_depth)


class TestSizeOverride:
    """The size table overrides the two numeric hand inputs."""

    @pytest.mark.parametrize("size_name", sorted(FIT_SIZE_TABLE))
    def test_named_sizes_ignore_numeric_inputs(self, size_name: str) -> None:
        # Deliberately contradictory numeric inputs — the size must win.
        finger, hand = FIT_SIZE_TABLE[size_name]
        derived = derive({
            "size": size_name,
            "measure_finger_width": 32,
            "measure_hand_width": 60,
        })
        expected = derive({
            "size": "Measure my hand",
            "measure_finger_width": finger,
            "measure_hand_width": hand,
        })
        assert derived == expected, (
            f"Size '{size_name}' must behave exactly like finger={finger} / "
            f"hand={hand} and ignore the numeric hand inputs."
        )

    def test_measure_my_hand_honors_numeric_inputs(self) -> None:
        base = derive({"size": "Measure my hand"})
        bigger = derive({"size": "Measure my hand", "measure_finger_width": 26})
        assert bigger["finger_hole_diameter"] > base["finger_hole_diameter"], (
            "'Measure my hand' must honor measure_finger_width."
        )

    def test_sizes_are_ordered(self) -> None:
        """Small < Medium < Large on the primary grip dimensions."""
        small = derive({"size": "Small"})
        medium = derive({"size": "Medium"})
        large = derive({"size": "Large"})
        for key in ("finger_hole_diameter", "puller_bottom_width",
                    "body_thickness"):
            assert small[key] < medium[key] < large[key], (
                f"Expected Small < Medium < Large for {key}, got "
                f"{small[key]} / {medium[key]} / {large[key]}"
            )


class TestMonotonicity:
    """Bigger measurement → never a smaller derived fit dimension."""

    @staticmethod
    def _assert_monotonic(measure_key: str, derived_key: str) -> None:
        lo, hi = MEASURE_RANGES[measure_key]
        steps = 40
        values = [
            derive({"size": "Measure my hand",
                    measure_key: lo + (hi - lo) * i / steps})[derived_key]
            for i in range(steps + 1)
        ]
        for i in range(steps):
            assert values[i + 1] >= values[i] - 1e-9, (
                f"{derived_key} must be monotonically non-decreasing in "
                f"{measure_key}, but dropped from {values[i]} to "
                f"{values[i + 1]} near "
                f"{measure_key}={lo + (hi - lo) * i / steps:.2f}"
            )

    def test_plug_width_widens_notch(self) -> None:
        self._assert_monotonic("measure_plug_width_wall", "plug_wall_notch_width")

    def test_plug_width_widens_pocket(self) -> None:
        self._assert_monotonic("measure_plug_width_wall", "pocket_width")

    def test_finger_width_widens_hole(self) -> None:
        self._assert_monotonic("measure_finger_width", "finger_hole_diameter")

    def test_plug_length_deepens_pocket(self) -> None:
        self._assert_monotonic("measure_plug_length", "pocket_depth")

    def test_hand_width_widens_body(self) -> None:
        self._assert_monotonic("measure_hand_width", "puller_bottom_width")


# Plug quick-select prefills (mirrors the `_eff_*` ternaries in the v7 SCAD;
# two-station values measured by scripts/measure_plug_references.py).
PLUG_PRESET_VECTORS: Dict[str, Dict[str, Any]] = {
    "lamp_1_15": {
        "measure_plug_length": 37.0,
        "measure_plug_width_wall": 25.0, "measure_plug_width_cable": 11.2,
        "measure_plug_thickness_wall": 18.6, "measure_plug_thickness_cable": 8.6,
        "measure_cord_thickness": 3.6,
    },
    "standard_5_15": {
        "measure_plug_length": 46.2,
        "measure_plug_width_wall": 26.6, "measure_plug_width_cable": 13.4,
        "measure_plug_thickness_wall": 18.9, "measure_plug_thickness_cable": 15.0,
        "measure_cord_thickness": 7,
    },
    "heavy_duty_5_15": {
        "measure_plug_length": 43.8,
        "measure_plug_width_wall": 25.8, "measure_plug_width_cable": 21.9,
        "measure_plug_thickness_wall": 27.0, "measure_plug_thickness_cable": 27.0,
        "measure_cord_thickness": 8.2,
    },
}


def _zip_finger_wall(derived: Dict[str, Any]) -> float:
    """Smallest bore-to-bore wall between a zip hole and a finger hole."""
    zip_top_y = (
        derived["puller_length"]
        - derived["plug_wall_notch_height"]
        - derived["zip_tie_distance_from_notch"]
    )
    zip_bottom_y = zip_top_y - derived["zip_tie_height_spacing"]
    dx = abs(
        derived["finger_hole_spacing"] / 2 - derived["zip_tie_width_spacing"] / 2
    )
    walls = [
        math.hypot(dx, row_y - derived["finger_hole_y_position"])
        - derived["finger_hole_diameter"] / 2
        - derived["zip_tie_hole_diameter"] / 2
        for row_y in (zip_bottom_y, zip_top_y)
    ]
    return min(walls)


class TestZipFingerBarrier:
    """The zip-tie grid must never merge into the finger holes (the grid
    hangs from the top edge, the fingers anchor near the cord end, so
    shallow plugs used to pull them together — D-20's zip-grid floor)."""

    @pytest.mark.parametrize("preset_name", sorted(PLUG_PRESET_VECTORS))
    @pytest.mark.parametrize("size", ["Small", "Medium", "Large"])
    def test_plug_presets_keep_barrier(self, preset_name: str, size: str) -> None:
        vector = {**PLUG_PRESET_VECTORS[preset_name], "size": size}
        wall = _zip_finger_wall(derive(vector))
        assert wall >= FIT_ZIP_FINGER_WEB - 1e-9, (
            f"Plug preset '{preset_name}' at size {size} leaves only a "
            f"{wall:.2f} mm wall between the zip grid and the finger holes "
            f"(need {FIT_ZIP_FINGER_WEB})."
        )

    def test_measurement_sweep_keeps_barrier(self) -> None:
        """Worst case is the shortest plug with the biggest fingers."""
        violations = []
        for length in (12, 16, 20, 25.5, 30):
            for finger in (14, 20, 26, 32):
                vector = {
                    "size": "Measure my hand",
                    "measure_plug_length": length,
                    "measure_finger_width": finger,
                }
                wall = _zip_finger_wall(derive(vector))
                if wall < FIT_ZIP_FINGER_WEB - 1e-9:
                    violations.append((length, finger, wall))
        assert not violations, (
            "Zip grid / finger hole barrier violated:\n"
            + "\n".join(
                f"  - plug_length={d}, finger_width={f}: wall={w:.2f}"
                for d, f, w in violations
            )
        )

    def test_shipped_sizes_unchanged_at_defaults(self) -> None:
        """The zip-grid floor must be inactive for the golden-fixture sizes
        (default measurements) — those meshes are pinned by fixtures."""
        for size in ("Small", "Medium", "Large"):
            derived = derive({"size": size})
            gap_driven = (
                derived["pocket_depth"] + 5.5
                + derived["finger_hole_y_position"]
                + derived["finger_hole_diameter"] / 2
            )
            assert derived["puller_length"] == pytest.approx(gap_driven), (
                f"Size {size}: puller_length is no longer the pocket/finger "
                "formula — the zip-grid floor engaged at default "
                "measurements, which changes the shipped fixtures."
            )


# ═══════════════════════════════════════════════════════════════════════════════
# Render lane — SCAD ↔ Python derivation contract + mesh parity
# ═══════════════════════════════════════════════════════════════════════════════

ECHO_LINE_RE = re.compile(r'ECHO: "fit_derived: (\w+)=(.+?)"\s*$')

ECHO_VECTORS = [
    ("defaults", {}),
    ("small", {"size": "Small"}),
    ("large", {"size": "Large"}),
    ("vacuum_plug", VACUUM_PLUG_VECTOR),
    ("all_min", ALL_MIN_VECTOR),
    ("all_max", ALL_MAX_VECTOR),
]


def _parse_echo_values(echo_text: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for line in echo_text.splitlines():
        match = ECHO_LINE_RE.match(line.strip())
        if not match:
            continue
        key, raw = match.group(1), match.group(2)
        if raw == "true":
            out[key] = True
        elif raw == "false":
            out[key] = False
        else:
            try:
                out[key] = float(raw)
            except ValueError:
                out[key] = raw
    return out


@pytest.mark.requires_openscad
@pytest.mark.parametrize("vector_name,vector", ECHO_VECTORS)
def test_echo_matches_python(
    vector_name: str,
    vector: Dict[str, Any],
    scad_file: Path,
    openscad_runner,
    tmp_path: Path,
) -> None:
    """Render `-o <tmp>.echo` and compare fit_derived lines to fit_formulas."""
    parameters: Dict[str, Any] = dict(vector)
    parameters.setdefault("size", "Medium")
    echo_out = tmp_path / f"fit_{vector_name}.echo"
    result = openscad_runner.generate_stl(
        scad_file=scad_file,
        output_stl=echo_out,
        parameters=parameters,
    )
    assert result.success, (
        f"Echo render failed for vector '{vector_name}' "
        f"(returncode={result.returncode}):\n{result.stderr}"
    )

    scad_values = _parse_echo_values(echo_out.read_text(encoding="utf-8"))
    python_values = derive(vector)

    assert set(scad_values.keys()) == set(python_values.keys()), (
        f"Echo output key set differs from the Python mirror for "
        f"'{vector_name}':\n"
        f"  only in SCAD:   {sorted(set(scad_values) - set(python_values))}\n"
        f"  only in Python: {sorted(set(python_values) - set(scad_values))}"
    )

    mismatches = []
    for key, py_val in python_values.items():
        scad_val = scad_values[key]
        if isinstance(py_val, bool):
            ok = scad_val is py_val
        elif isinstance(py_val, str):
            ok = scad_val == py_val
        else:
            # OpenSCAD's echo prints numbers at 6 significant digits
            # (e.g. 28.235294117647058 -> "28.2353"), so round the Python
            # value to the same printed precision before the exact compare.
            py_printed = float(f"{float(py_val):.6g}")
            ok = abs(float(scad_val) - py_printed) < 1e-9
        if not ok:
            mismatches.append((key, scad_val, py_val))
    assert not mismatches, (
        f"SCAD and Python derivations disagree for vector '{vector_name}' "
        f"(fit_measured.scad and tests/fit_formulas.py are out of sync):\n"
        + "\n".join(
            f"  - {k}: scad={s!r}, python={p!r}" for k, s, p in mismatches
        )
    )


@pytest.mark.requires_openscad
@pytest.mark.slow
def test_measured_parity_against_medium_fixture(
    scad_file: Path,
    fixtures_dir: Path,
    openscad_runner,
    mesh_comparator,
    tmp_path: Path,
) -> None:
    """'Measure my hand' defaults must be mesh-identical to the `medium`
    fixture.

    Pins the Medium-parity invariant end to end at mesh level: any drift in
    the derivation formulas that changes the default geometry shows up here
    even if the unit-level parity test is also updated.
    """
    reference = fixtures_dir / "medium" / "reference.stl"
    if not reference.exists():
        pytest.skip("medium fixture reference.stl not committed/hydrated.")

    output_stl = tmp_path / "measured_default.stl"
    result = openscad_runner.generate_stl(
        scad_file=scad_file,
        output_stl=output_stl,
        parameters={
            "size": "Measure my hand",
            "render_mode": "Full",
            "quality": 64,
        },
    )
    assert result.success, (
        f"'Measure my hand' default render failed "
        f"(returncode={result.returncode}):\n{result.stderr}"
    )

    comparison = mesh_comparator.compare(reference, output_stl)
    if not comparison.passed:
        details = "\n".join(f"  - {f}" for f in comparison.failures)
        pytest.fail(
            "'Measure my hand' default render is not mesh-equivalent to the "
            f"medium fixture (parity invariant broken):\n{details}\n"
            f"Volume drift {comparison.volume_diff_percent:.3f}%, "
            f"area drift {comparison.surface_area_diff_percent:.3f}%, "
            f"bbox drift {comparison.bounding_box_diff_mm:.4f}mm."
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
