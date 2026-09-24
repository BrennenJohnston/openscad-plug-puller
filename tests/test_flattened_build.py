"""Tests for the flattened single-file builds in ``dist/``.

``scripts/build_flattened.py`` writes one artifact per tool (``BUILDS``):
``dist/Plug_Puller_SingleFile.scad`` (the one-sided puller) and
``dist/Plug_Puller_Two_Sided_SingleFile.scad`` (the two-sided puller).

Quick lane (no OpenSCAD), for every artifact:

* The committed ``dist/`` artifact is byte-identical to what
  ``scripts/build_flattened.py`` produces from the current sources
  (freshness — also enforced by the CI lint job's ``--check`` step).
* The artifact contains no ``include``/``use`` statements and carries the
  PolyForm NC notice header (M3 acceptance).
* Every Customizer parameter survives flattening, checked against the
  artifact's own parameter mapping (the two-sided mapping arrives in B1).

Render lane (``@requires_openscad``):

* The one-sided artifact renders mesh-equivalent output to the modular build
  for the ``Medium`` and ``Measure my hand`` defaults, compared against the
  ``medium`` golden fixture within the ``compare_config.json`` tolerances
  (both are mesh-identical to it by the Medium-parity invariant).
* The two-sided artifact renders the ``two_sided_plate`` fixture's
  parameters to the same plate: the comparator passes and volume, surface
  area and bounds agree to 6 decimals.

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from scripts.build_flattened import BUILDS, OUTPUT_FILE, build_flattened_source

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BUILD_IDS = [build.output.name for build in BUILDS]
MAPPINGS = {
    "Plug_Puller_SingleFile.scad": PROJECT_ROOT / "parameter_mapping.json",
    "Plug_Puller_Two_Sided_SingleFile.scad": PROJECT_ROOT / "parameter_mapping_two_sided.json",
}
TWO_SIDED_ARTIFACT = next(
    build.output for build in BUILDS if build.main.name == "Plug_Puller_Two_Sided.scad"
)


def _require_artifact(path: Path) -> None:
    assert path.exists(), (
        f"Flattened artifact missing: {path}. Run: python scripts/build_flattened.py"
    )


@pytest.mark.parametrize("build", BUILDS, ids=BUILD_IDS)
class TestFlattenedArtifact:
    """Static checks on every committed dist/ artifact."""

    def test_artifact_exists(self, build) -> None:
        _require_artifact(build.output)

    def test_artifact_is_fresh(self, build) -> None:
        _require_artifact(build.output)
        expected = build_flattened_source(build)
        committed = build.output.read_text(encoding="utf-8")
        assert committed == expected, (
            f"{build.output.name} is stale relative to the src/ sources. "
            f"Run: python scripts/build_flattened.py"
        )

    def test_no_include_or_use_statements(self, build) -> None:
        _require_artifact(build.output)
        content = build.output.read_text(encoding="utf-8")
        include_re = re.compile(r"^\s*(include|use)\s*<", re.MULTILINE)
        offenders = include_re.findall(content)
        assert not offenders, (
            "The flattened artifact must be fully self-contained (MakerWorld "
            "PMM and `?src=` playground loading cannot resolve local "
            f"includes), but include/use statements remain: {offenders}"
        )

    def test_carries_polyform_notice(self, build) -> None:
        _require_artifact(build.output)
        content = build.output.read_text(encoding="utf-8")
        assert "PolyForm Noncommercial 1.0.0" in content, (
            "The flattened artifact must carry the PolyForm NC license notice."
        )
        assert "GENERATED FILE, DO NOT EDIT" in content, (
            "The flattened artifact must carry the do-not-edit marker."
        )

    def test_customizer_surface_preserved(self, build) -> None:
        """All user-facing parameters must survive flattening (the web
        customizer renders its form from this file's Customizer block)."""
        from tests.validate_parameter_schema import ParameterSchemaValidator

        mapping = MAPPINGS[build.output.name]
        if not mapping.exists():
            pytest.skip(f"{mapping.name} arrives in phase B1.")
        _require_artifact(build.output)
        validator = ParameterSchemaValidator(build.output, mapping)
        ok, results = validator.validate()
        if not ok:
            errors = [
                r for r in results if r["severity"] == "error" and not r["passed"]
            ]
            details = "\n".join(f"  - {r['message']}" for r in errors)
            pytest.fail(
                f"Flattened artifact {build.output.name} failed schema "
                f"validation ({len(errors)} error(s)):\n{details}"
            )


@pytest.mark.requires_openscad
@pytest.mark.slow
@pytest.mark.parametrize("size_name", ["Medium", "Measure my hand"])
def test_flattened_render_matches_medium_fixture(
    size_name: str,
    fixtures_dir: Path,
    openscad_runner,
    mesh_comparator,
    tmp_path: Path,
) -> None:
    """Flattened build renders the same mesh as the modular build.

    Both sizes' defaults are mesh-identical to the `medium` golden fixture
    ("Measure my hand" by the Medium-parity invariant), so one reference
    covers both comparisons.
    """
    reference = fixtures_dir / "medium" / "reference.stl"
    if not reference.exists():
        pytest.skip("medium fixture reference.stl not committed/hydrated.")

    output_stl = tmp_path / f"flattened_{size_name.replace(' ', '_')}.stl"
    result = openscad_runner.generate_stl(
        scad_file=OUTPUT_FILE,
        output_stl=output_stl,
        parameters={"size": size_name, "render_mode": "Full", "quality": 64},
    )
    assert result.success, (
        f"Flattened render failed for size '{size_name}' "
        f"(returncode={result.returncode}):\n{result.stderr}"
    )

    comparison = mesh_comparator.compare(reference, output_stl)
    if not comparison.passed:
        details = "\n".join(f"  - {f}" for f in comparison.failures)
        pytest.fail(
            f"Flattened build for size '{size_name}' is not "
            f"mesh-equivalent to the modular build:\n{details}\n"
            f"Volume drift {comparison.volume_diff_percent:.3f}%, "
            f"area drift {comparison.surface_area_diff_percent:.3f}%, "
            f"bbox drift {comparison.bounding_box_diff_mm:.4f}mm."
        )


@pytest.mark.requires_openscad
@pytest.mark.slow
def test_two_sided_artifact_matches_fixture(
    fixtures_dir: Path,
    openscad_runner,
    mesh_comparator,
    tmp_path: Path,
) -> None:
    """The flattened two-sided file renders the fixture's plate exactly."""
    import trimesh

    fixture = fixtures_dir / "two_sided_plate"
    reference = fixture / "reference.stl"
    payload = json.loads((fixture / "params.json").read_text(encoding="utf-8"))
    _require_artifact(TWO_SIDED_ARTIFACT)

    output_stl = tmp_path / "flattened_two_sided.stl"
    result = openscad_runner.generate_stl(
        scad_file=TWO_SIDED_ARTIFACT,
        output_stl=output_stl,
        parameters=payload["parameters"],
    )
    assert result.success, (
        f"Flattened two-sided render failed (returncode={result.returncode}):\n"
        f"{result.stderr}"
    )

    comparison = mesh_comparator.compare(reference, output_stl)
    assert comparison.passed, "; ".join(comparison.failures)
    got = trimesh.load(output_stl, force="mesh")
    ref = trimesh.load(reference, force="mesh")
    assert abs(got.volume - ref.volume) < 1e-6, f"volume {got.volume:.6f} vs {ref.volume:.6f}"
    assert abs(got.area - ref.area) < 1e-6, f"area {got.area:.6f} vs {ref.area:.6f}"
    bounds_diff = float(abs(got.bounds - ref.bounds).max())
    assert bounds_diff < 1e-6, f"bounds differ by {bounds_diff:.6f} mm"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
