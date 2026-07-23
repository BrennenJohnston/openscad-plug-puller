"""End-to-end render + mesh-property tests.

Each test in this module renders the v5 SCAD with a known parameter set and
compares the resulting mesh against the committed golden fixture
(``tests/fixtures/<name>/reference.stl``) via :class:`MeshComparator`.

Fixtures live in ``tests/fixtures/<name>/``:

* ``params.json``    — exact ``{key: value}`` parameter overrides passed to
                       OpenSCAD with ``-D``.
* ``reference.stl``  — committed golden mesh produced by the same SCAD on the
                       pinned OpenSCAD version.
* ``metadata.json``  — provenance: OpenSCAD version, generation date,
                       and trimesh sanity metrics.

Tests are auto-skipped (rather than failing) when:

* OpenSCAD is unavailable (handled by the session-scoped fixture).
* The fixture directory exists but no ``reference.stl`` is present yet.

This lets the lint lane pass on a clean checkout before Phase 8 commit #10
ships the actual fixture STLs. Once fixtures land, the same tests start
asserting mesh parity.

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.mesh_comparison import MeshComparator
from tests.openscad_runner import OpenSCADRunner


def _discover_fixtures(fixtures_dir: Path) -> list[str]:
    """Return the list of fixture names that have a ``params.json``.

    Fixtures missing ``reference.stl`` are still discovered — the test
    function decides whether to skip or run the comparison.
    """
    if not fixtures_dir.exists():
        return []
    return sorted(
        p.name for p in fixtures_dir.iterdir()
        if p.is_dir() and (p / "params.json").exists()
    )


FIXTURE_NAMES = _discover_fixtures(
    Path(__file__).resolve().parent / "fixtures"
)


@pytest.mark.requires_openscad
@pytest.mark.slow
@pytest.mark.parametrize("fixture_name", FIXTURE_NAMES or ["__none__"])
def test_render_matches_golden_fixture(
    fixture_name: str,
    scad_file: Path,
    fixtures_dir: Path,
    openscad_runner: OpenSCADRunner,
    mesh_comparator: MeshComparator,
    tmp_path: Path,
) -> None:
    """Render the fixture's params and assert mesh parity with reference.stl."""
    if fixture_name == "__none__":
        pytest.skip(
            "No fixtures discovered under tests/fixtures/. "
            "Phase 8 commit #10 ships the initial golden STL set."
        )

    fixture_dir = fixtures_dir / fixture_name
    params_path = fixture_dir / "params.json"
    reference_path = fixture_dir / "reference.stl"

    assert params_path.exists(), f"Missing params.json: {params_path}"
    if not reference_path.exists():
        pytest.skip(
            f"Golden STL not committed yet for '{fixture_name}'. "
            f"Run scripts/regenerate_fixtures.py (or commit reference.stl manually) "
            f"to activate this test."
        )

    with open(params_path, "r", encoding="utf-8") as fh:
        payload = json.load(fh)
    parameters = payload.get("parameters", payload)

    output_stl = tmp_path / f"{fixture_name}.stl"
    result = openscad_runner.generate_stl(
        scad_file=scad_file,
        output_stl=output_stl,
        parameters=parameters,
    )

    assert result.success, (
        f"OpenSCAD render failed for fixture '{fixture_name}' "
        f"(returncode={result.returncode}):\n{result.stderr}"
    )
    assert output_stl.exists(), f"Output STL not produced: {output_stl}"

    comparison = mesh_comparator.compare(reference_path, output_stl)
    if not comparison.passed:
        details = "\n".join(f"  - {f}" for f in comparison.failures)
        pytest.fail(
            f"Mesh parity failed for fixture '{fixture_name}':\n{details}\n"
            f"Volume drift {comparison.volume_diff_percent:.3f}%, "
            f"area drift {comparison.surface_area_diff_percent:.3f}%, "
            f"bbox drift {comparison.bounding_box_diff_mm:.4f}mm."
        )

    # The comparator already enforces the watertightness contract (test must
    # match reference; a watertight reference forbids a non-watertight test).
    # Since the v5.1 fillet rework (slice-based rim flares replaced the
    # minkowski shells) every shipped fixture reference is watertight.


@pytest.mark.requires_openscad
@pytest.mark.slow
def test_default_full_render_is_watertight(
    scad_file: Path,
    openscad_runner: OpenSCADRunner,
    tmp_path: Path,
) -> None:
    """Smoke test: the no-parameter default render produces a watertight solid.

    This catches catastrophic regressions (broken CSG, missing size table,
    etc.) even before any fixture comparison kicks in. It runs with the
    defaults declared in the SCAD file (size = Medium — the original
    device — with render_mode = Full).
    """
    import trimesh

    output_stl = tmp_path / "default_full.stl"
    result = openscad_runner.generate_stl(
        scad_file=scad_file,
        output_stl=output_stl,
        parameters={},
    )
    assert result.success, (
        f"Default render failed (returncode={result.returncode}):\n{result.stderr}"
    )
    mesh = trimesh.load(output_stl, force="mesh")
    assert isinstance(mesh, trimesh.Trimesh), (
        f"Default render did not load as Trimesh: {type(mesh).__name__}"
    )
    assert mesh.is_watertight, (
        "Default Medium / Full render is not watertight. "
        "Inspect OpenSCAD stderr for non-manifold warnings."
    )
    # Sanity bounds: the Medium size (= the original device) is
    # 66.7 x 63.5 x 6.35 mm.
    extent = mesh.bounds[1] - mesh.bounds[0]
    assert extent[0] > 50, f"X extent suspiciously small: {extent[0]} mm"
    assert extent[1] > 50, f"Y extent suspiciously small: {extent[1]} mm"
    assert extent[2] > 5, f"Z extent suspiciously small: {extent[2]} mm"
