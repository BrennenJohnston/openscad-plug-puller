"""Pytest configuration and shared fixtures for plug-puller v7 validation.

This module wires the four core resources every STL test needs:

* :data:`PROJECT_ROOT` — repo root (so tests can be invoked from any cwd).
* The ``scad_file`` fixture pointing at ``src/Plug_Puller_Parametric.scad``.
* An :class:`OpenSCADRunner` session fixture that auto-discovers the binary,
  optionally enforces the CI-pinned version, and is skipped (rather than
  errored) when OpenSCAD is missing so lint-only test runs still pass.
* A :class:`MeshComparator` fixture sourced from ``tests/compare_config.json``.

Markers (``requires_openscad``, ``slow``) are registered with
``pytest_configure`` instead of pytest.ini so this module stays the single
source of truth for fixture wiring.

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tests.mesh_comparison import MeshComparator  # noqa: E402
from tests.openscad_runner import OpenSCADNotFoundError, OpenSCADRunner  # noqa: E402

logger = logging.getLogger(__name__)


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers used by the suite."""
    config.addinivalue_line(
        "markers",
        "requires_openscad: test requires the OpenSCAD CLI to be installed",
    )
    config.addinivalue_line(
        "markers",
        "slow: test is slower than 10 seconds (typically renders + compares)",
    )


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--regenerate-fixtures",
        action="store_true",
        default=False,
        help="Re-render every fixture's reference.stl in place. Use after intentional model changes.",
    )


@pytest.fixture(scope="session")
def project_root() -> Path:
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def tests_dir(project_root: Path) -> Path:
    return project_root / "tests"


@pytest.fixture(scope="session")
def fixtures_dir(tests_dir: Path) -> Path:
    return tests_dir / "fixtures"


@pytest.fixture(scope="session")
def scad_file(project_root: Path) -> Path:
    """Path to the canonical SCAD file."""
    path = project_root / "src" / "Plug_Puller_Parametric.scad"
    if not path.exists():
        pytest.skip(f"SCAD file missing: {path}")
    return path


@pytest.fixture(scope="session")
def presets_file(project_root: Path) -> Path:
    """Path to the preset table include file."""
    path = project_root / "src" / "presets.scad"
    if not path.exists():
        pytest.skip(f"presets.scad missing: {path}")
    return path


@pytest.fixture(scope="session")
def parameter_mapping_file(project_root: Path) -> Path:
    """Path to ``parameter_mapping.json``.

    Tests using this fixture should call :func:`pytest.skip` when the file is
    absent so the suite stays green if the schema has not been generated yet.
    """
    return project_root / "parameter_mapping.json"


@pytest.fixture(scope="session")
def comparison_config(tests_dir: Path) -> Dict[str, Any]:
    config_path = tests_dir / "compare_config.json"
    with open(config_path, "r", encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="session")
def mesh_comparator(comparison_config: Dict[str, Any]) -> MeshComparator:
    return MeshComparator(comparison_config)


@pytest.fixture(scope="session")
def openscad_runner() -> OpenSCADRunner:
    """Locate the OpenSCAD CLI once per test session.

    CI mode (``CI=true`` env var) enforces the pinned version from
    ``tests/compare_config.json`` and requires the Manifold backend. Local
    runs degrade gracefully: missing OpenSCAD skips the test rather than
    erroring.
    """
    try:
        is_ci = os.environ.get("CI", "").lower() in ("true", "1", "yes")
        enforce = None
        if is_ci:
            cfg_path = PROJECT_ROOT / "tests" / "compare_config.json"
            with open(cfg_path, "r", encoding="utf-8") as fh:
                cfg = json.load(fh)
            enforce = cfg["tool_versions"]["openscad"]["ci_version"]

        runner = OpenSCADRunner(enforce_version=enforce)
        logger.info("OpenSCAD available: %s", runner.get_version())

        if is_ci:
            runner.check_manifold_backend(require_manifold=True)
            logger.info("Manifold backend verified (CI mode)")
        elif not runner.use_manifold:
            logger.warning(
                "Manifold backend not available — local renders may differ "
                "from CI golden fixtures."
            )
        return runner
    except OpenSCADNotFoundError as exc:
        pytest.skip(f"OpenSCAD not available: {exc}")
        raise  # pragma: no cover — pytest.skip raises, this satisfies type checkers
