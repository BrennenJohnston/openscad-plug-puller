"""Two-sided puller: the see-through plug in the preview (R1 phase B4).

The owner chose "Build it, on by default in preview" (Q-09). The plug is
drawn under OpenSCAD's ``%`` background modifier, so it shows in the preview
and is never part of a render or an export:

* exports are identical with ``show_plug_preview`` on and off;
* the switch lives in Step 1 of the Customizer;
* the evaluated model tree (OpenSCAD's CSG export, which keeps modifiers)
  carries the see-through plug under ``%`` when the switch is on, and not
  when it is off. The CSG export needs no OpenGL, so this runs on CI too.

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TWO_SIDED_SCAD = PROJECT_ROOT / "src" / "Plug_Puller_Two_Sided.scad"
USB_C = {
    "plug_preset": "Measure my plug",
    "measure_plug_length": 23,
    "measure_plug_width_prong_end": 13,
    "measure_plug_width_cord_end": 13,
    "measure_cord_thickness": 7,
    "plug_sides": "Rounded sides",
    "attachment": "Zip ties",
}
# SkyBlue at 35 % opacity, as OpenSCAD writes it in a CSG export.
GHOST_RE = re.compile(
    r"^\s*%\s*color\(\[0\.529412, 0\.807843, 0\.921569, 0\.35\]\)", re.MULTILINE
)


def _define(name: str, value) -> list:
    if isinstance(value, bool):
        text = "true" if value else "false"
    elif isinstance(value, str):
        text = f'"{value}"'
    else:
        text = str(value)
    return ["-D", f"{name}={text}"]


def _export(runner, out: Path, show: bool) -> str:
    assert TWO_SIDED_SCAD.exists(), f"SCAD file missing: {TWO_SIDED_SCAD}"
    cmd = [str(runner.openscad_path), "-o", str(out)]
    for name, value in {**USB_C, "show_plug_preview": show}.items():
        cmd += _define(name, value)
    cmd.append(str(TWO_SIDED_SCAD))
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    assert result.returncode == 0 and out.exists(), (
        f"Export to {out.name} failed (returncode={result.returncode}):\n"
        f"{(result.stdout or '') + (result.stderr or '')}"
    )
    return (result.stdout or "") + (result.stderr or "")


def test_show_plug_preview_declared_in_step1() -> None:
    source = TWO_SIDED_SCAD.read_text(encoding="utf-8")
    step1 = source[source.index("/* [Step 1 - Your Plug] */"):source.index("/* [Step 2 - Size] */")]
    assert re.search(r"^show_plug_preview\s*=\s*true\s*;", step1, re.MULTILINE), (
        "show_plug_preview must be declared in Step 1, on by default (Q-09)."
    )


@pytest.mark.requires_openscad
@pytest.mark.slow
def test_ghost_never_exported(openscad_runner, tmp_path) -> None:
    import trimesh

    on, off = tmp_path / "ghost_on.stl", tmp_path / "ghost_off.stl"
    _export(openscad_runner, on, True)
    _export(openscad_runner, off, False)
    a, b = trimesh.load(on, force="mesh"), trimesh.load(off, force="mesh")
    assert len(a.split(only_watertight=False)) == len(b.split(only_watertight=False))
    assert abs(a.volume - b.volume) < 1e-6, f"volume {a.volume:.6f} vs {b.volume:.6f}"
    assert abs(a.area - b.area) < 1e-6, f"area {a.area:.6f} vs {b.area:.6f}"


@pytest.mark.requires_openscad
@pytest.mark.slow
def test_ghost_in_the_model_tree_only_when_on(openscad_runner, tmp_path) -> None:
    on, off = tmp_path / "ghost_on.csg", tmp_path / "ghost_off.csg"
    _export(openscad_runner, on, True)
    _export(openscad_runner, off, False)
    assert GHOST_RE.search(on.read_text(encoding="utf-8")), (
        "With show_plug_preview on, the model tree must carry the see-through "
        "plug under the % background modifier."
    )
    assert not GHOST_RE.search(off.read_text(encoding="utf-8")), (
        "With show_plug_preview off, the see-through plug must be absent."
    )
