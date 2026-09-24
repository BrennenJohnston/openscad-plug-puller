"""Two-sided puller: the strap slot on short plugs, the thin-plug warning, and
the derived-values echo (R1 phase B2).

* A short plug (the owner's USB-C numbers, 23 mm long) with the default
  attachment keeps all six zip stations: the strap slot is left out instead
  of running into them, and no red tag prints (defect D-001).
* A plug narrower than the cord-channel floor gets the WC-12 tag instead of
  silently loose arms (D-006).
* A long plug still gets both strap slots (regression guard).
* Manual zip placement keeps the slot where the stations put it and still
  reports a collision with a red tag (regression guard).
* The heavy-duty preset plate is unchanged (regression guard).
* Every render echoes the derived-values block (D-007).

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

import pytest

from tests.test_clamshell_parity import _classify

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TWO_SIDED_SCAD = PROJECT_ROOT / "src" / "Plug_Puller_Two_Sided.scad"
FIXTURE = PROJECT_ROOT / "tests" / "fixtures" / "two_sided_plate"
ECHO_HEADER = "=== Two-sided puller derived values (mm) ==="
WC12 = "PLUG NARROWER THAN THE CORD CHANNEL - ARMS CANNOT TOUCH IT"
USB_C = {
    "measure_plug_length": 23,
    "measure_plug_width_prong_end": 13,
    "measure_plug_width_cord_end": 13,
    "measure_cord_thickness": 7,
    "render_mode": "Clamshell Plate",
}


def _render(runner, tmp_path: Path, name: str, params: Dict[str, object]):
    import trimesh

    assert TWO_SIDED_SCAD.exists(), f"SCAD file missing: {TWO_SIDED_SCAD}"
    out = tmp_path / f"{name}.stl"
    result = runner.generate_stl(scad_file=TWO_SIDED_SCAD, output_stl=out, parameters=params)
    assert result.success, f"Render failed (returncode={result.returncode}):\n{result.stderr}"
    console = (result.stdout or "") + (result.stderr or "")
    mesh = trimesh.load(out, force="mesh")
    parts = mesh.split(only_watertight=False)
    plate = max(parts, key=lambda p: abs(p.volume)) if len(parts) else mesh
    return plate, console


def _warnings(console: str):
    return [line.strip() for line in console.splitlines() if "WARNING:" in line]


@pytest.mark.requires_openscad
@pytest.mark.slow
def test_short_plug_keeps_six_zip_stations(openscad_runner, tmp_path) -> None:
    plate, console = _render(openscad_runner, tmp_path, "usbc_default_attachment", USB_C)
    inventory = _classify(plate)
    assert len(inventory["zip"]) == 6, (
        f"A 23 mm plug must keep all six zip stations, got {len(inventory['zip'])} "
        f"(the strap slot ran into them)."
    )
    assert len(inventory["velcro"]) == 0, (
        f"A 23 mm plug has no room for the strap slot, got {len(inventory['velcro'])} slot loop(s)."
    )
    assert not _warnings(console), f"No red tag expected, got: {_warnings(console)}"
    assert ECHO_HEADER in console, "The derived-values block is missing from the console."


@pytest.mark.requires_openscad
@pytest.mark.slow
def test_plug_narrower_than_cord_channel_warns(openscad_runner, tmp_path) -> None:
    params = {
        "measure_plug_width_prong_end": 4,
        "measure_plug_width_cord_end": 4,
        "measure_cord_thickness": 4,
        "render_mode": "Clamshell Plate",
    }
    _plate, console = _render(openscad_runner, tmp_path, "narrow_plug", params)
    assert any(WC12 in line for line in _warnings(console)), (
        f"Expected the WC-12 tag for a 4 mm plug on a 4 mm cord; warnings: {_warnings(console)}"
    )


@pytest.mark.requires_openscad
@pytest.mark.slow
def test_long_plug_keeps_both_strap_slots(openscad_runner, tmp_path) -> None:
    plate, console = _render(
        openscad_runner, tmp_path, "long_plug",
        {"measure_plug_length": 45, "render_mode": "Clamshell Plate"},
    )
    inventory = _classify(plate)
    assert len(inventory["velcro"]) == 2, f"Expected 2 strap slots, got {len(inventory['velcro'])}."
    assert len(inventory["zip"]) == 6, f"Expected 6 zip stations, got {len(inventory['zip'])}."
    assert not _warnings(console), f"No red tag expected, got: {_warnings(console)}"


@pytest.mark.requires_openscad
@pytest.mark.slow
def test_manual_placement_still_reports_the_slot(openscad_runner, tmp_path) -> None:
    params = {
        "plug_preset": "Heavy-duty extension cord - NEMA 5-15",
        "plate_zip_placement": "Manual",
        "plate_zip_pos_2": 45,
        "render_mode": "Clamshell Plate",
    }
    _plate, console = _render(openscad_runner, tmp_path, "manual_squeezed_window", params)
    assert any("STRAP WIDER THAN ARM SLOT WINDOW" in line for line in _warnings(console)), (
        f"Manual placement that squeezes the slot window must still warn; got {_warnings(console)}"
    )


@pytest.mark.requires_openscad
@pytest.mark.slow
def test_preset_plate_unchanged(openscad_runner, mesh_comparator, tmp_path) -> None:
    import trimesh

    params = json.loads((FIXTURE / "params.json").read_text(encoding="utf-8"))["parameters"]
    out = tmp_path / "preset.stl"
    result = openscad_runner.generate_stl(scad_file=TWO_SIDED_SCAD, output_stl=out, parameters=params)
    assert result.success, result.stderr
    comparison = mesh_comparator.compare(FIXTURE / "reference.stl", out)
    assert comparison.passed, "; ".join(comparison.failures)
    got = trimesh.load(out, force="mesh")
    ref = trimesh.load(FIXTURE / "reference.stl", force="mesh")
    assert abs(got.volume - ref.volume) < 1e-6 and abs(got.area - ref.area) < 1e-6
