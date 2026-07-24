"""Mesh-health guards for the ready-to-print STLs shipped under ``stl/``.

Quick lane (no OpenSCAD):

* Every shipped STL is watertight with consistent winding — the historical
  failure class here was non-watertight minkowski output (v5-era), so this
  pins the fix permanently.
* The shipped Small / Medium / Large flat tools stay mesh-equivalent to
  their golden fixtures (``tests/fixtures/{small,medium,large}``), so the
  downloads can never silently drift from the validated model.

Render lane (``@requires_openscad``):

* ``Measuring_Stencil.scad`` still renders watertight and
  mesh-equivalent to the shipped ``stl/Measuring_Stencil.stl`` (Visual
  labels) and ``stl/Measuring_Stencil_Tactile.stl`` (``label_mode=Tactile``:
  raised ADA characters + braille flaps) — the Tactile case doubles as the
  render smoke test for that mode.

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STL_DIR = PROJECT_ROOT / "stl"

SHIPPED_STLS = [
    "Plug_Puller_Small.stl",
    "Plug_Puller_Medium.stl",
    "Plug_Puller_Large.stl",
    "Measuring_Stencil.stl",
    "Measuring_Stencil_Tactile.stl",
]

# Shipped stencil STL -> the label_mode it was rendered with.
STENCIL_MODE_PAIRS = [
    ("Measuring_Stencil.stl", "Visual"),
    ("Measuring_Stencil_Tactile.stl", "Tactile"),
]

# Shipped size STL -> golden fixture rendered from the same parameters.
SIZE_FIXTURE_PAIRS = [
    ("Plug_Puller_Small.stl", "small"),
    ("Plug_Puller_Medium.stl", "medium"),
    ("Plug_Puller_Large.stl", "large"),
]


@pytest.mark.parametrize("stl_name", SHIPPED_STLS)
def test_shipped_stl_watertight(stl_name: str) -> None:
    import trimesh

    path = STL_DIR / stl_name
    assert path.exists(), f"Shipped STL missing: {path}"

    mesh = trimesh.load(path, force="mesh")
    assert isinstance(mesh, trimesh.Trimesh), f"{stl_name} did not load as a mesh"
    assert mesh.is_watertight, (
        f"{stl_name} is not watertight — slicers may reject or mis-slice it. "
        f"Re-render it from the source SCAD and investigate the geometry."
    )
    assert mesh.is_winding_consistent, (
        f"{stl_name} has inconsistent face winding (flipped normals)."
    )


@pytest.mark.parametrize(("stl_name", "fixture_name"), SIZE_FIXTURE_PAIRS)
def test_shipped_stl_matches_golden_fixture(
    stl_name: str, fixture_name: str, fixtures_dir: Path, mesh_comparator
) -> None:
    reference = fixtures_dir / fixture_name / "reference.stl"
    if not reference.exists():
        pytest.skip(f"golden fixture missing: {reference}")

    comparison = mesh_comparator.compare(reference, STL_DIR / stl_name)
    if not comparison.passed:
        details = "\n".join(f"  - {f}" for f in comparison.failures)
        pytest.fail(
            f"stl/{stl_name} has drifted from the '{fixture_name}' golden "
            f"fixture:\n{details}\n"
            f"If the model changed intentionally, re-render the shipped STL "
            f"and regenerate the fixtures together."
        )


@pytest.mark.requires_openscad
@pytest.mark.slow
@pytest.mark.parametrize(("stl_name", "label_mode"), STENCIL_MODE_PAIRS)
def test_stencil_render_matches_shipped_stl(
    stl_name: str, label_mode: str, openscad_runner, mesh_comparator, tmp_path: Path
) -> None:
    scad = PROJECT_ROOT / "Measuring_Stencil.scad"
    assert scad.exists(), f"Stencil SCAD missing: {scad}"

    output = tmp_path / f"stencil_render_{label_mode.lower()}.stl"
    result = openscad_runner.generate_stl(
        scad_file=scad,
        output_stl=output,
        parameters={"label_mode": label_mode},
    )
    assert result.success, (
        f"Stencil render ({label_mode}) failed "
        f"(returncode={result.returncode}):\n{result.stderr}"
    )
    assert output.stat().st_size > 0, f"Stencil render ({label_mode}) is empty."

    import trimesh

    mesh = trimesh.load(output, force="mesh")
    assert mesh.is_watertight, (
        f"Fresh stencil render ({label_mode}) is not watertight."
    )

    comparison = mesh_comparator.compare(STL_DIR / stl_name, output)
    if not comparison.passed:
        details = "\n".join(f"  - {f}" for f in comparison.failures)
        pytest.fail(
            f"Fresh stencil render ({label_mode}) no longer matches the "
            f"shipped stl/{stl_name}:\n{details}\n"
            f"If the stencil changed intentionally, re-render the shipped STL."
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
