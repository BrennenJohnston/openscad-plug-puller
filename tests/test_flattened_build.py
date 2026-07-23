"""Tests for the flattened single-file build (``dist/Plug_Puller_SingleFile.scad``).

Quick lane (no OpenSCAD):

* The committed ``dist/`` artifact is byte-identical to what
  ``scripts/build_flattened.py`` produces from the current sources
  (freshness — also enforced by the CI lint job's ``--check`` step).
* The artifact contains no ``include``/``use`` statements and carries the
  PolyForm NC notice header (M3 acceptance).

Render lane (``@requires_openscad``):

* The flattened file renders mesh-equivalent output to the modular build for
  the ``Medium`` and ``Measure my hand`` defaults, compared against the
  ``medium`` golden fixture within the ``compare_config.json`` tolerances
  (both are mesh-identical to it by the Medium-parity invariant).

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from scripts.build_flattened import OUTPUT_FILE, build_flattened_source

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestFlattenedArtifact:
    """Static checks on the committed dist/ artifact."""

    def test_artifact_exists(self) -> None:
        assert OUTPUT_FILE.exists(), (
            f"Flattened artifact missing: {OUTPUT_FILE}. "
            f"Run: python scripts/build_flattened.py"
        )

    def test_artifact_is_fresh(self) -> None:
        expected = build_flattened_source()
        committed = OUTPUT_FILE.read_text(encoding="utf-8")
        assert committed == expected, (
            "dist/Plug_Puller_SingleFile.scad is stale relative to the "
            "src/ sources. Run: python scripts/build_flattened.py"
        )

    def test_no_include_or_use_statements(self) -> None:
        content = OUTPUT_FILE.read_text(encoding="utf-8")
        include_re = re.compile(r"^\s*(include|use)\s*<", re.MULTILINE)
        offenders = include_re.findall(content)
        assert not offenders, (
            "The flattened artifact must be fully self-contained (MakerWorld "
            "PMM and `?src=` playground loading cannot resolve local "
            f"includes), but include/use statements remain: {offenders}"
        )

    def test_carries_polyform_notice(self) -> None:
        content = OUTPUT_FILE.read_text(encoding="utf-8")
        assert "PolyForm Noncommercial 1.0.0" in content, (
            "The flattened artifact must carry the PolyForm NC license notice."
        )
        assert "GENERATED FILE, DO NOT EDIT" in content, (
            "The flattened artifact must carry the do-not-edit marker."
        )

    def test_customizer_surface_preserved(self) -> None:
        """All user-facing parameters must survive flattening (the web
        customizer renders its form from this file's Customizer block)."""
        from tests.validate_parameter_schema import ParameterSchemaValidator

        mapping = PROJECT_ROOT / "parameter_mapping.json"
        validator = ParameterSchemaValidator(OUTPUT_FILE, mapping)
        ok, results = validator.validate()
        if not ok:
            errors = [
                r for r in results if r["severity"] == "error" and not r["passed"]
            ]
            details = "\n".join(f"  - {r['message']}" for r in errors)
            pytest.fail(
                f"Flattened artifact failed schema validation "
                f"({len(errors)} error(s)):\n{details}"
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
