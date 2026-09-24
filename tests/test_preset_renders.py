"""Every saved Customizer preset must render clean.

For each parameter set in ``presets/Plug_Puller_Parametric.json`` (rendered
with the one-sided file) and ``presets/Plug_Puller_Two_Sided.json`` (rendered
with the two-sided file) this suite does a full render via OpenSCAD's native
preset loading (``-p`` / ``-P`` — the same path the GUI uses) and asserts:

* the render succeeds and the mesh is watertight, and
* the console carries no ``WARNING:`` line (the in-model validation tags
  echo through this prefix, as do OpenSCAD's own warnings) and no
  ``undefined`` fragment (the v5-era ``-undefined`` echo bug class, where an
  undef leaked into a derived value's echo string).

Informational autofit clamp echoes (``… (clamped from …)``) are allowed:
bounds-clamping measured sizes against the body envelope is documented
behavior, not a defect.

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PRESET_FILES = [
    (PROJECT_ROOT / "presets" / "Plug_Puller_Parametric.json",
     PROJECT_ROOT / "src" / "Plug_Puller_Parametric.scad"),
    (PROJECT_ROOT / "presets" / "Plug_Puller_Two_Sided.json",
     PROJECT_ROOT / "src" / "Plug_Puller_Two_Sided.scad"),
]
PRESET_FILE_IDS = [presets.name for presets, _scad in PRESET_FILES]

FORBIDDEN_FRAGMENTS = ("WARNING:", "undefined")


def _preset_names(presets_json: Path) -> list[str]:
    with open(presets_json, "r", encoding="utf-8") as fh:
        return list(json.load(fh)["parameterSets"].keys())


def _preset_cases() -> list:
    cases = []
    for presets_json, scad in PRESET_FILES:
        if not presets_json.exists():
            cases.append(pytest.param(
                presets_json, scad, None, id=f"{presets_json.name}::MISSING"))
            continue
        for name in _preset_names(presets_json):
            cases.append(pytest.param(presets_json, scad, name, id=f"{presets_json.name}::{name}"))
    return cases


@pytest.mark.parametrize("presets_json, scad", PRESET_FILES, ids=PRESET_FILE_IDS)
def test_presets_file_parses(presets_json: Path, scad: Path) -> None:
    assert presets_json.exists(), f"Presets file missing: {presets_json}"
    names = _preset_names(presets_json)
    assert names, f"{presets_json.name} has no parameterSets"


@pytest.mark.requires_openscad
@pytest.mark.slow
@pytest.mark.parametrize("presets_json, scad, preset_name", _preset_cases())
def test_preset_renders_clean(
    presets_json: Path, scad: Path, preset_name, openscad_runner, tmp_path: Path
) -> None:
    assert preset_name is not None, f"Presets file missing: {presets_json}"
    output = tmp_path / "preset_render.stl"
    cmd = [
        str(openscad_runner.openscad_path),
        "-o",
        str(output),
        "-p",
        str(presets_json),
        "-P",
        preset_name,
    ]
    if openscad_runner.use_manifold:
        cmd.extend(["--backend", "Manifold"])
    cmd.append(str(scad))

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    console = (result.stdout or "") + (result.stderr or "")

    assert result.returncode == 0 and output.exists(), (
        f"Preset '{preset_name}' failed to render "
        f"(returncode={result.returncode}):\n{console[-2000:]}"
    )

    offenders = [
        line.strip()
        for line in console.splitlines()
        if any(fragment in line for fragment in FORBIDDEN_FRAGMENTS)
    ]
    assert not offenders, (
        f"Preset '{preset_name}' rendered with warnings/undefined values:\n"
        + "\n".join(f"  {line}" for line in offenders)
    )

    import trimesh

    mesh = trimesh.load(output, force="mesh")
    assert isinstance(mesh, trimesh.Trimesh)
    assert mesh.is_watertight, f"Preset '{preset_name}' produced a non-watertight mesh."


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
