"""Step 3 attachment wiring on the heavy-duty clamshell.

Workstream: the Step 3 ``attachment`` dropdown must gate the clamshell's
zip-tie stations and velcro arm slot (previously it only drove the flat
tool). This suite renders the clamshell plate at the heavy-duty preset with
three Step 3 choices and asserts:

* every render is watertight;
* material ordering holds — "None" (no zip holes, no slot) is the densest
  plate, "Zip ties" (holes but no slot) is denser than the default
  "Zip ties + Velcro" (holes and slot);
* the default render still matches the idealized parity reference (Step 3's
  defaults are geometry-preserving) with the full feature inventory.

Renders with ``attachment="None"`` carry the WC-10 red warning coupon (a
separate text body next to the plate), so volume comparisons use the largest
connected component — the plate itself.

Skips (rather than fails) when OpenSCAD is unavailable.

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
IDEAL_PLATE = (
    PROJECT_ROOT
    / "plug references"
    / "3 Prong Heavy Ideal Sample"
    / "Plug Puller_3_Prong_Idealized_Sample_Plug_Bottom.stl"
)
HD_PRESET = "Heavy-duty extension cord - NEMA 5-15"

ATTACHMENT_CHOICES = {
    "default": "Zip ties + Velcro",
    "zip_only": "Zip ties",
    "none": "None",
}


def _loop_area(loop: np.ndarray) -> float:
    x, y = loop[:, 0], loop[:, 1]
    return abs(0.5 * np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))


def _plate_stats(stl_path: Path) -> Dict[str, Any]:
    """Load a rendered STL and measure the plate body (largest component).

    Warning coupons export as separate small text bodies, so all plate
    metrics are taken on the largest connected component only.
    """
    import trimesh

    mesh = trimesh.load(stl_path, force="mesh")
    parts = mesh.split(only_watertight=False)
    plate = max(parts, key=lambda m: m.volume) if len(parts) else mesh

    lo, hi = plate.bounds
    plate.apply_translation([-(lo[0] + hi[0]) / 2, -lo[1], -lo[2]])
    lo, hi = plate.bounds
    env = (hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2])

    # Mid-thickness slice: count the interior cutouts (finger bores, zip
    # stations, velcro slots) exactly like the parity suite does.
    section = plate.section(plane_origin=[0, 0, env[2] / 2], plane_normal=[0, 0, 1])
    loops = sorted(
        (np.asarray(p)[:, :2] for p in section.discrete),
        key=_loop_area,
        reverse=True,
    )
    finger, ziph, velcro = [], [], []
    for lp in loops[2:]:
        area = _loop_area(lp)
        w = float(lp[:, 0].max() - lp[:, 0].min())
        h = float(lp[:, 1].max() - lp[:, 1].min())
        aspect = max(w, h) / max(1e-6, min(w, h))
        if aspect > 1.6:
            velcro.append(area)
        elif max(w, h) > 12:
            finger.append(area)
        elif area > 3:
            ziph.append(area)
    return {
        "watertight": bool(mesh.is_watertight),
        "volume": float(plate.volume),
        "envelope": env,
        "n_finger": len(finger),
        "n_zip": len(ziph),
        "n_velcro": len(velcro),
    }


@pytest.fixture(scope="module")
def attachment_renders(
    scad_file: Path, openscad_runner, tmp_path_factory
) -> Dict[str, Dict[str, Any]]:
    out_dir = tmp_path_factory.mktemp("clamshell_attachment")
    stats: Dict[str, Dict[str, Any]] = {}
    for label, choice in ATTACHMENT_CHOICES.items():
        out = out_dir / f"plate_{label}.stl"
        result = openscad_runner.generate_stl(
            scad_file=scad_file,
            output_stl=out,
            parameters={
                "plug_preset": HD_PRESET,
                "attachment": choice,
                "render_mode": "Clamshell Plate",
                "quality": 64,
            },
        )
        assert result.success, (
            f"Clamshell render failed for attachment={choice!r} "
            f"(returncode={result.returncode}):\n{result.stderr}"
        )
        stats[label] = _plate_stats(out)
    return stats


@pytest.mark.requires_openscad
@pytest.mark.slow
class TestClamshellAttachment:
    """Step 3 gates the clamshell zip stations and velcro slot."""

    def test_all_watertight(self, attachment_renders) -> None:
        for label, stats in attachment_renders.items():
            assert stats["watertight"], f"attachment={label}: mesh not watertight"

    def test_default_has_full_inventory(self, attachment_renders) -> None:
        got = attachment_renders["default"]
        assert got["n_finger"] == 2, f"expected 2 finger bores, got {got['n_finger']}"
        assert got["n_zip"] == 6, f"expected 6 zip stations, got {got['n_zip']}"
        assert got["n_velcro"] == 2, f"expected 2 velcro slots, got {got['n_velcro']}"

    def test_zip_only_drops_slots(self, attachment_renders) -> None:
        got = attachment_renders["zip_only"]
        assert got["n_zip"] == 6, f"expected 6 zip stations, got {got['n_zip']}"
        assert got["n_velcro"] == 0, (
            f"attachment='Zip ties' must remove the arm slots, got "
            f"{got['n_velcro']}"
        )

    def test_none_drops_everything(self, attachment_renders) -> None:
        got = attachment_renders["none"]
        assert got["n_zip"] == 0, (
            f"attachment='None' must remove the zip stations, got {got['n_zip']}"
        )
        assert got["n_velcro"] == 0, (
            f"attachment='None' must remove the arm slots, got {got['n_velcro']}"
        )

    def test_volume_ordering(self, attachment_renders) -> None:
        v_none = attachment_renders["none"]["volume"]
        v_zip = attachment_renders["zip_only"]["volume"]
        v_default = attachment_renders["default"]["volume"]
        assert v_none > v_zip > v_default, (
            f"Expected volume(None) > volume(Zip ties) > volume(default); got "
            f"{v_none:.0f} / {v_zip:.0f} / {v_default:.0f} mm^3"
        )

    def test_default_matches_parity_reference(self, attachment_renders) -> None:
        """Step 3 defaults must keep the clamshell parity envelope intact."""
        if not IDEAL_PLATE.exists():
            pytest.skip(f"Idealized clamshell plate missing: {IDEAL_PLATE}")
        import trimesh

        ideal = trimesh.load(IDEAL_PLATE, force="mesh")
        lo, hi = ideal.bounds
        ref = (hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2])
        got = attachment_renders["default"]["envelope"]
        assert got[0] == pytest.approx(ref[0], abs=2.5), (
            f"Plate width X {got[0]:.2f} vs ideal {ref[0]:.2f} (> 2.5 mm)"
        )
        assert got[1] == pytest.approx(ref[1], abs=2.5), (
            f"Plate length Y {got[1]:.2f} vs ideal {ref[1]:.2f} (> 2.5 mm)"
        )
        assert got[2] == pytest.approx(ref[2], abs=1.0), (
            f"Plate thickness Z {got[2]:.2f} vs ideal {ref[2]:.2f} (> 1.0 mm)"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
