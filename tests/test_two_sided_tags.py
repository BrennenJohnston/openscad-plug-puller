"""Two-sided puller: its red tags use the file's own measurement word, width.

The two-sided file measures the plug's width across the arms (at the prong
end and at the cord end). The owner chose the words at Q-21 ("Say WIDE and
WIDTH"): WC-2 and WC-9 name the width, and no two-sided tag says "thick"
about the plug.

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TWO_SIDED_SCAD = PROJECT_ROOT / "src" / "Plug_Puller_Two_Sided.scad"
CASES = {
    # name: (parameters, the tag it must print)
    "wc2_plug_too_wide": (
        {"measure_plug_width_prong_end": 45, "measure_plug_width_cord_end": 45},
        "PLUG TOO WIDE - ARMS BULGE PAST FINGER LOBES",
    ),
    "wc9_width_taper": (
        {"measure_plug_length": 12, "measure_plug_width_prong_end": 10, "measure_plug_width_cord_end": 30},
        "PLUG WIDTH TAPER LOOKS WRONG - RECHECK BOTH ENDS",
    ),
}


def _warnings(runner, tmp_path: Path, name: str, params: Dict[str, object]):
    assert TWO_SIDED_SCAD.exists(), f"SCAD file missing: {TWO_SIDED_SCAD}"
    out = tmp_path / f"{name}.stl"
    result = runner.generate_stl(
        scad_file=TWO_SIDED_SCAD, output_stl=out, parameters={**params, "render_mode": "One plate"}
    )
    assert result.success, f"Render failed (returncode={result.returncode}):\n{result.stderr}"
    console = (result.stdout or "") + (result.stderr or "")
    return [line.strip() for line in console.splitlines() if "WARNING:" in line]


@pytest.mark.requires_openscad
@pytest.mark.slow
@pytest.mark.parametrize("case", sorted(CASES))
def test_tags_name_the_width(openscad_runner, tmp_path, case) -> None:
    params, tag = CASES[case]
    warnings = _warnings(openscad_runner, tmp_path, case, params)
    assert any(tag in line for line in warnings), f"Expected the tag {tag!r}; warnings: {warnings}"
    assert not any("THICK" in line for line in warnings), (
        f"A two-sided tag still says thick about the plug: {warnings}"
    )
