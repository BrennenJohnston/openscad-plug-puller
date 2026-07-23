"""Pytest wrapper around :mod:`tests.validate_parameter_schema`.

Skips gracefully when ``parameter_mapping.json`` is absent so a fresh clone
without the generated schema still lints; once present, every commit is
gated on this validator passing.

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.validate_parameter_schema import ParameterSchemaValidator


def test_parameter_schema_matches_scad(
    scad_file: Path, parameter_mapping_file: Path
) -> None:
    if not parameter_mapping_file.exists():
        pytest.skip(
            f"parameter_mapping.json not present ({parameter_mapping_file})."
        )

    validator = ParameterSchemaValidator(scad_file, parameter_mapping_file)
    ok, results = validator.validate()

    if not ok:
        errors = [r for r in results if r["severity"] == "error" and not r["passed"]]
        details = "\n".join(f"  - {r['message']}" for r in errors)
        pytest.fail(
            f"Parameter schema validation failed with {len(errors)} error(s):\n{details}"
        )
