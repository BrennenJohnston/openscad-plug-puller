"""One-sided puller: a plug too thick for it points to the two-sided file (W-20).

Since R1 phase C1 the one-sided file builds only the one-sided puller. A plug
24 mm thick or more no longer switches silently to another tool: it gets the
red tag "PLUG THICKER THAN 24MM - USE THE TWO-SIDED PULLER FILE", whether the
thickness is typed or comes from a plug preset. Thinner plugs stay silent.

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ONE_SIDED_SCAD = PROJECT_ROOT / "src" / "Plug_Puller_Parametric.scad"
W20 = "PLUG THICKER THAN 24MM - USE THE TWO-SIDED PULLER FILE"
CASES = {
    # name: (parameters, whether W-20 must fire)
    "typed_27mm": ({"measure_plug_thickness_wall": 27, "measure_plug_thickness_cable": 27}, True),
    "typed_20mm": ({"measure_plug_thickness_wall": 20, "measure_plug_thickness_cable": 20}, False),
    "heavy_duty_preset": ({"plug_preset": "Heavy-duty extension cord - NEMA 5-15"}, True),
}


def _warnings(runner, tmp_path: Path, name: str, params: Dict[str, object]):
    assert ONE_SIDED_SCAD.exists(), f"SCAD file missing: {ONE_SIDED_SCAD}"
    out = tmp_path / f"{name}.stl"
    result = runner.generate_stl(
        scad_file=ONE_SIDED_SCAD, output_stl=out, parameters={**params, "render_mode": "Full"}
    )
    assert result.success, f"Render failed (returncode={result.returncode}):\n{result.stderr}"
    console = (result.stdout or "") + (result.stderr or "")
    return [line.strip() for line in console.splitlines() if "WARNING:" in line]


@pytest.mark.requires_openscad
@pytest.mark.slow
@pytest.mark.parametrize("case", sorted(CASES))
def test_w20_points_thick_plugs_to_the_two_sided_file(openscad_runner, tmp_path, case) -> None:
    params, fires = CASES[case]
    warnings = _warnings(openscad_runner, tmp_path, case, params)
    got = any(W20 in line for line in warnings)
    assert got == fires, (
        f"{case}: W-20 {'expected' if fires else 'must stay silent'}; warnings: {warnings}"
    )
