"""Render the upload-ready STL library for MakerWorld / Thingiverse / Printables.

Every default preset the two models ship gets its own named STL so downloaders
can print a standard configuration without opening OpenSCAD:

* Plug Puller (``src/Plug_Puller_Parametric.scad``) — each of the 3 plug
  presets x each of the 3 finger/hand sizes = 9 tools. Only ``plug_preset`` and
  ``size`` vary; the attachment (zip ties + velcro) and every other dial stay at
  their defaults. ``tool_style`` is left on "Auto from plug", so the heavy-duty
  round-cord preset resolves to a single heavy-duty clamshell plate (the tool is
  two of these — print each file twice).

* Measuring Stencil (``Measuring_Stencil.scad``) — every individual card
  (P1/P2/P3 plug gauges, R1 ruler, C1 cord gauge, F1/F2 finger sizing) rendered
  on its own via the ``export_card`` selector, in both label modes (Visual and
  Tactile), plus the full packed set for each mode. 2 x (7 cards + 1 full set)
  = 16 files.

Files land under ``stl/`` in a folder tree that mirrors the upload layout
(this is the committed ready-to-print library the README links to):

    stl/
      Plug-Puller/
        Plug-Puller_Flat-2-Prong-Lamp-NEMA-1-15_Small.stl
        ...
      Measuring-Stencil/
        Visual/   Measuring-Stencil_Visual_P1_Lamp-Plug-Gauge.stl  ...
        Tactile/  Measuring-Stencil_Tactile_P1_Lamp-Plug-Gauge.stl ...

Run from the repo root:

    python scripts/build_release_stls.py
    python scripts/build_release_stls.py --only plug-puller
    python scripts/build_release_stls.py --only stencil --verbose

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tests.openscad_runner import OpenSCADRunner  # noqa: E402

logger = logging.getLogger(__name__)

PLUG_SCAD = PROJECT_ROOT / "src" / "Plug_Puller_Parametric.scad"
STENCIL_SCAD = PROJECT_ROOT / "Measuring_Stencil.scad"
DEFAULT_OUT = PROJECT_ROOT / "stl"

SIZES = ["Small", "Medium", "Large"]

# Plug presets exactly as they read in the Step 1 dropdown, paired with a
# filesystem-safe descriptor and whether "Auto from plug" resolves them to the
# heavy-duty clamshell (a single plate — the finished tool is two of them).
PLUG_PRESETS = [
    {
        "customizer": "Flat 2-prong lamp plug - NEMA 1-15",
        "desc": "Flat-2-Prong-Lamp-NEMA-1-15",
        "clamshell": False,
    },
    {
        "customizer": "Standard 3-prong plug - NEMA 5-15",
        "desc": "Standard-3-Prong-NEMA-5-15",
        "clamshell": False,
    },
    {
        "customizer": "Heavy-duty extension cord - NEMA 5-15",
        "desc": "Heavy-Duty-Cord-NEMA-5-15",
        "clamshell": True,
    },
]

# Stencil cards: export_card ID -> filesystem-safe descriptor. Order follows
# the fixed card list in Measuring_Stencil.scad.
STENCIL_CARDS = [
    ("P1", "P1_Lamp-Plug-Gauge"),
    ("P2", "P2_Standard-3-Prong-Gauge"),
    ("P3", "P3_Heavy-Duty-Cord-Gauge"),
    ("R1", "R1_Ruler-100mm"),
    ("C1", "C1_Cord-Gauge"),
    ("F1", "F1_Finger-Sizing-15-25mm"),
    ("F2", "F2_Finger-Sizing-26-32mm"),
]
STENCIL_MODES = ["Visual", "Tactile"]


@dataclass
class Job:
    group: str  # "plug-puller" | "stencil"
    scad: Path
    out_rel: Path  # path under the output root
    params: Dict[str, object] = field(default_factory=dict)


def plug_jobs() -> List[Job]:
    jobs: List[Job] = []
    for preset in PLUG_PRESETS:
        for size in SIZES:
            parts = ["Plug-Puller", preset["desc"]]
            if preset["clamshell"]:
                parts.append("Clamshell-Plate")
            parts.append(size)
            name = "_".join(parts) + ".stl"
            jobs.append(
                Job(
                    group="plug-puller",
                    scad=PLUG_SCAD,
                    out_rel=Path("Plug-Puller") / name,
                    params={
                        "render_mode": "Full",
                        "plug_preset": preset["customizer"],
                        "size": size,
                    },
                )
            )
    return jobs


def stencil_jobs() -> List[Job]:
    jobs: List[Job] = []
    for mode in STENCIL_MODES:
        # Full packed set for the mode.
        jobs.append(
            Job(
                group="stencil",
                scad=STENCIL_SCAD,
                out_rel=Path("Measuring-Stencil") / mode
                / f"Measuring-Stencil_{mode}_All-Cards.stl",
                params={"label_mode": mode, "export_card": "All cards"},
            )
        )
        # Individual cards.
        for card_id, desc in STENCIL_CARDS:
            jobs.append(
                Job(
                    group="stencil",
                    scad=STENCIL_SCAD,
                    out_rel=Path("Measuring-Stencil") / mode
                    / f"Measuring-Stencil_{mode}_{desc}.stl",
                    params={"label_mode": mode, "export_card": card_id},
                )
            )
    return jobs


def check_watertight(stl: Path) -> Optional[bool]:
    """Best-effort watertight check. Returns None if trimesh is unavailable."""
    try:
        import trimesh
    except ImportError:
        return None
    mesh = trimesh.load(stl, force="mesh")
    return bool(getattr(mesh, "is_watertight", False))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--out", type=Path, default=DEFAULT_OUT,
        help="Output root for the release STL tree (default: release/).",
    )
    parser.add_argument(
        "--only", choices=["plug-puller", "stencil"],
        help="Render only one model group.",
    )
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    jobs = plug_jobs() + stencil_jobs()
    if args.only:
        jobs = [j for j in jobs if j.group == args.only]

    runner = OpenSCADRunner()
    logger.info("OpenSCAD: %s", runner.version_string)
    logger.info("Manifold backend: %s", "on" if runner.use_manifold else "off")
    logger.info("Rendering %d STL(s) into %s", len(jobs), args.out)

    failures: List[str] = []
    not_watertight: List[str] = []
    for job in jobs:
        out = args.out / job.out_rel
        res = runner.generate_stl(job.scad, out, job.params)
        if not res.success:
            logger.error("FAIL %s\n%s", job.out_rel, res.stderr[-400:])
            failures.append(str(job.out_rel))
            continue
        wt = check_watertight(out)
        wt_note = {True: "watertight", False: "NOT watertight", None: "?"}[wt]
        if wt is False:
            not_watertight.append(str(job.out_rel))
        size_kb = out.stat().st_size / 1024
        logger.info(
            "OK   %-58s %7.0f KB  %.1fs  %s",
            job.out_rel.as_posix(), size_kb, res.duration_seconds, wt_note,
        )

    logger.info("-" * 72)
    logger.info("Done: %d rendered, %d failed.", len(jobs) - len(failures), len(failures))
    if not_watertight:
        logger.warning("Not watertight (%d): %s", len(not_watertight), not_watertight)
    if failures:
        logger.error("Failed jobs: %s", failures)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
