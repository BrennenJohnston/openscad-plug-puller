"""Validate the Customizer parameter declarations against ``parameter_mapping.json``.

Adapted from ``braille-stl-generator-openscad/tests/validate_parameter_schema.py``
and trimmed to the plug-puller's surface:

* Plug-puller has a single front-end (OpenSCAD itself), so there is no "web
  API name" / "web UI label" axis to validate. We only check that every
  ``custom_<key>`` slider declared inside the Customizer sections agrees with
  one row in ``parameter_mapping.json`` on:

    - default value
    - declared type (string / float / integer / boolean / enum)
    - slider range (``[min:step:max]`` comments) where present
    - enum option list (for ``// [Small, Medium, Large, ...]`` dropdowns)

* Hidden / programmatic parameters (under ``/* [Hidden] */``) are skipped —
  they are render-control switches consumed by tests, not user-facing.

The validator can be run directly as a CLI for ad-hoc checking, or invoked
via the pytest wrapper in ``test_parameter_schema.py``.

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import json
import logging
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class ParameterSchemaValidator:
    """Diff a SCAD file's customizer block against a parameter_mapping.json schema."""

    def __init__(self, scad_file: Path, parameter_mapping_file: Path) -> None:
        self.scad_file = scad_file
        self.parameter_mapping_file = parameter_mapping_file

        with open(parameter_mapping_file, "r", encoding="utf-8") as fh:
            self.mapping_data = json.load(fh)

        self.parameters = self.mapping_data["parameters"]
        self.openscad_params = self._extract_openscad_parameters()

    def _extract_openscad_parameters(self) -> Dict[str, Dict[str, Any]]:
        """Walk the Customizer sections and parse each slider/dropdown declaration."""
        params: Dict[str, Dict[str, Any]] = {}
        current_section: Optional[str] = None

        lines = self.scad_file.read_text(encoding="utf-8").splitlines()
        for raw in lines:
            line = raw.strip()

            section_match = re.match(r"/\*\s*\[([^\]]+)\]\s*\*/", line)
            if section_match:
                section = section_match.group(1).strip()
                # OpenSCAD Customizer semantics: `/* [Hidden] */` only hides
                # parameters *until the next section marker* — it does not end
                # the Customizer body. Treat it as a skip-state (parameters in
                # a hidden section are render-control switches, not user-facing)
                # and resume at the next named section. The previous
                # implementation `break`-ed here, which silently skipped every
                # section declared after the first `[Hidden]` marker — in the
                # v5 SCAD that was all 59 geometry parameters.
                if section.lower() == "hidden":
                    current_section = None
                    continue
                current_section = section
                continue

            # Stop at the first piece of executable code (or marker comments).
            if (
                line.startswith("module ")
                or line.startswith("function ")
                or "PRESET DEFINITIONS" in line
                or "include <presets.scad>" in line
            ):
                break

            param_match = re.match(
                r"^(\w+)\s*=\s*([^;]+);(?:\s*//\s*(.*))?$", line
            )
            if not param_match or current_section is None:
                continue

            name = param_match.group(1)
            value_str = param_match.group(2).strip()
            comment = param_match.group(3) or ""

            value = self._parse_openscad_value(value_str)
            enum_values, slider_range = self._parse_bracket_spec(comment)
            description = re.sub(r"\[([^\]]+)\]", "", comment).strip()

            params[name] = {
                "name": name,
                "default": value,
                "section": current_section,
                "description": description,
                "enum_values": enum_values,
                "slider_range": slider_range,
            }
        return params

    @staticmethod
    def _parse_openscad_value(value_str: str) -> Any:
        value_str = value_str.strip()
        if value_str.startswith('"') and value_str.endswith('"'):
            return value_str[1:-1]
        if value_str.lower() == "true":
            return True
        if value_str.lower() == "false":
            return False
        try:
            if "." in value_str or "e" in value_str.lower():
                return float(value_str)
            return int(value_str)
        except ValueError:
            return value_str

    @staticmethod
    def _parse_bracket_spec(
        comment: str,
    ) -> Tuple[Optional[List[str]], Optional[Tuple[float, float, float]]]:
        """Return (enum_values, slider_range) from a Customizer-style comment.

        Supports both ``// [a, b, c]`` (dropdown) and ``// [min:step:max]``
        (numeric slider). Returns ``(None, None)`` when no bracket spec.
        """
        match = re.search(r"\[([^\]]+)\]", comment)
        if not match:
            return None, None
        content = match.group(1).strip()
        slider = re.match(
            r"^\s*(-?\d+(?:\.\d+)?)\s*:\s*(-?\d+(?:\.\d+)?)\s*:\s*(-?\d+(?:\.\d+)?)\s*$",
            content,
        )
        if slider:
            return None, (
                float(slider.group(1)),
                float(slider.group(2)),
                float(slider.group(3)),
            )
        enum_values: List[str] = []
        for opt in content.split(","):
            opt = opt.strip()
            if ":" in opt:
                value, _label = opt.split(":", 1)
                enum_values.append(value.strip().strip('"'))
            else:
                enum_values.append(opt.strip().strip('"'))
        return enum_values, None

    def validate(self) -> Tuple[bool, List[Dict[str, Any]]]:
        results: List[Dict[str, Any]] = []
        results.extend(self._check_all_mapped())
        results.extend(self._check_defaults_match())
        results.extend(self._check_types_compatible())
        results.extend(self._check_enums_match())
        results.extend(self._check_slider_ranges_match())
        errors = [r for r in results if r["severity"] == "error" and not r["passed"]]
        return len(errors) == 0, results

    def _check_all_mapped(self) -> List[Dict[str, Any]]:
        mapped = {p["openscad_name"] for p in self.parameters}
        results: List[Dict[str, Any]] = []
        for name in self.openscad_params:
            if name not in mapped:
                results.append(
                    {
                        "check": "all_openscad_params_mapped",
                        "severity": "error",
                        "passed": False,
                        "message": f"OpenSCAD parameter '{name}' has no row in parameter_mapping.json",
                        "parameter": name,
                    }
                )
        if not results:
            results.append(
                {
                    "check": "all_openscad_params_mapped",
                    "severity": "error",
                    "passed": True,
                    "message": f"All {len(self.openscad_params)} OpenSCAD parameters are mapped",
                }
            )
        return results

    def _check_defaults_match(self) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for param in self.parameters:
            name = param["openscad_name"]
            if name not in self.openscad_params:
                continue
            expected = param.get("default")
            actual = self.openscad_params[name]["default"]
            if not self._values_match(expected, actual):
                results.append(
                    {
                        "check": "default_values_match",
                        "severity": "error",
                        "passed": False,
                        "message": (
                            f"Default mismatch for '{name}': "
                            f"mapping={expected!r}, openscad={actual!r}"
                        ),
                        "parameter": name,
                        "expected": expected,
                        "actual": actual,
                    }
                )
        if not results:
            results.append(
                {
                    "check": "default_values_match",
                    "severity": "error",
                    "passed": True,
                    "message": "All default values match",
                }
            )
        return results

    def _check_types_compatible(self) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        type_to_python = {
            "string": (str,),
            "boolean": (bool,),
            "integer": (int,),
            "float": (int, float),
            "enum": (str,),
        }
        for param in self.parameters:
            name = param["openscad_name"]
            if name not in self.openscad_params:
                continue
            expected_type = param["type"]
            allowed = type_to_python.get(expected_type)
            actual = self.openscad_params[name]["default"]
            if allowed is None:
                continue
            # Booleans are a subclass of int in Python; force-exclude bool when
            # not expected.
            if expected_type != "boolean" and isinstance(actual, bool):
                results.append(
                    {
                        "check": "types_compatible",
                        "severity": "error",
                        "passed": False,
                        "message": (
                            f"Type mismatch for '{name}': expected {expected_type}, "
                            f"got boolean default"
                        ),
                        "parameter": name,
                    }
                )
                continue
            if not isinstance(actual, allowed):
                results.append(
                    {
                        "check": "types_compatible",
                        "severity": "error",
                        "passed": False,
                        "message": (
                            f"Type mismatch for '{name}': expected {expected_type}, "
                            f"got {type(actual).__name__}"
                        ),
                        "parameter": name,
                    }
                )
        if not results:
            results.append(
                {
                    "check": "types_compatible",
                    "severity": "error",
                    "passed": True,
                    "message": "All types compatible",
                }
            )
        return results

    def _check_enums_match(self) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for param in self.parameters:
            if param["type"] != "enum":
                continue
            name = param["openscad_name"]
            if name not in self.openscad_params:
                continue
            expected = set(param.get("values") or [])
            actual = set(self.openscad_params[name].get("enum_values") or [])
            if expected != actual:
                results.append(
                    {
                        "check": "enums_match",
                        "severity": "error",
                        "passed": False,
                        "message": (
                            f"Enum mismatch for '{name}': "
                            f"mapping={sorted(expected)}, openscad={sorted(actual)}"
                        ),
                        "parameter": name,
                    }
                )
        return results

    def _check_slider_ranges_match(self) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        checked = 0
        for param in self.parameters:
            mapping_range = param.get("range")
            if not mapping_range:
                continue
            name = param["openscad_name"]
            scad_param = self.openscad_params.get(name)
            if scad_param is None or scad_param.get("slider_range") is None:
                continue
            checked += 1
            scad_min, _step, scad_max = scad_param["slider_range"]
            try:
                exp_min, exp_max = float(mapping_range[0]), float(mapping_range[1])
            except (TypeError, ValueError, IndexError):
                results.append(
                    {
                        "check": "slider_ranges_match",
                        "severity": "error",
                        "passed": False,
                        "message": (
                            f"`range` for '{name}' is malformed: {mapping_range!r}; "
                            f"expected [min, max]."
                        ),
                        "parameter": name,
                    }
                )
                continue
            if abs(scad_min - exp_min) > 1e-9 or abs(scad_max - exp_max) > 1e-9:
                results.append(
                    {
                        "check": "slider_ranges_match",
                        "severity": "error",
                        "passed": False,
                        "message": (
                            f"Slider range mismatch for '{name}': "
                            f"openscad=[{scad_min}, {scad_max}], "
                            f"mapping=[{exp_min}, {exp_max}]"
                        ),
                        "parameter": name,
                    }
                )
        if checked == 0:
            results.append(
                {
                    "check": "slider_ranges_match",
                    "severity": "info",
                    "passed": True,
                    "message": "No slider ranges declared in mapping; check skipped",
                }
            )
        elif not any(r["check"] == "slider_ranges_match" and not r["passed"] for r in results):
            results.append(
                {
                    "check": "slider_ranges_match",
                    "severity": "error",
                    "passed": True,
                    "message": f"All {checked} slider ranges match",
                }
            )
        return results

    @staticmethod
    def _values_match(expected: Any, actual: Any) -> bool:
        if isinstance(expected, bool) or isinstance(actual, bool):
            return expected == actual
        if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            return abs(float(expected) - float(actual)) < 1e-9
        return expected == actual


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate v5 Customizer parameters against parameter_mapping.json"
    )
    parser.add_argument(
        "--scad-file",
        type=Path,
        default=PROJECT_ROOT / "src" / "Plug_Puller_Parametric.scad",
    )
    parser.add_argument(
        "--mapping-file",
        type=Path,
        default=PROJECT_ROOT / "parameter_mapping.json",
    )
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    if not args.mapping_file.exists():
        logger.error("parameter_mapping.json not found: %s", args.mapping_file)
        return 2

    try:
        validator = ParameterSchemaValidator(args.scad_file, args.mapping_file)
        logger.info(
            "Validating %s (%d customizer params, %d mapping rows)",
            args.scad_file.name,
            len(validator.openscad_params),
            len(validator.parameters),
        )
        ok, results = validator.validate()

        failed = [r for r in results if not r["passed"] and r["severity"] == "error"]
        for r in failed:
            print(f"ERROR  {r['message']}")
        passed_checks = [
            r for r in results if r["passed"] and r["severity"] == "error"
        ]
        for r in passed_checks:
            print(f"OK     {r['message']}")

        if args.output_json:
            with open(args.output_json, "w", encoding="utf-8") as fh:
                json.dump(
                    {
                        "passed": ok,
                        "total_checks": len(results),
                        "errors": len(failed),
                        "results": results,
                    },
                    fh,
                    indent=2,
                )

        return 0 if ok else 1
    except Exception as exc:  # noqa: BLE001
        logger.error("Validation error: %s", exc, exc_info=args.verbose)
        return 1


if __name__ == "__main__":
    sys.exit(main())
