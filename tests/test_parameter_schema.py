"""Pytest wrapper around :mod:`tests.validate_parameter_schema`.

Each tool file has its own committed parameter mapping:
``src/Plug_Puller_Parametric.scad`` ↔ ``parameter_mapping.json`` (the
one-sided puller) and ``src/Plug_Puller_Two_Sided.scad`` ↔
``parameter_mapping_two_sided.json`` (the two-sided puller). A missing
mapping fails the test: both are committed files, and every commit is gated
on the validator passing for both pairs.

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.validate_parameter_schema import ParameterSchemaValidator

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PAIRS = [
    ("src/Plug_Puller_Parametric.scad", "parameter_mapping.json"),
    ("src/Plug_Puller_Two_Sided.scad", "parameter_mapping_two_sided.json"),
]


@pytest.mark.parametrize("scad_rel, mapping_rel", PAIRS, ids=[p[1] for p in PAIRS])
def test_parameter_schema_matches_scad(scad_rel: str, mapping_rel: str) -> None:
    scad_file = PROJECT_ROOT / scad_rel
    mapping_file = PROJECT_ROOT / mapping_rel
    assert scad_file.exists(), f"SCAD file missing: {scad_file}"
    assert mapping_file.exists(), f"Parameter mapping missing: {mapping_file}"

    validator = ParameterSchemaValidator(scad_file, mapping_file)
    ok, results = validator.validate()

    if not ok:
        errors = [r for r in results if r["severity"] == "error" and not r["passed"]]
        details = "\n".join(f"  - {r['message']}" for r in errors)
        pytest.fail(
            f"Parameter schema validation failed for {mapping_rel} with "
            f"{len(errors)} error(s):\n{details}"
        )
