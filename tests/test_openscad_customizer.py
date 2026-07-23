"""OpenSCAD Customizer hygiene tests.

These tests are *static* — they parse ``src/Plug_Puller_Parametric.scad``
with regular expressions and never invoke OpenSCAD itself, so they run in
under a second on CI's quick lane.

Why each check exists:

* :meth:`TestOpenSCADCustomizer.test_no_value_colon_label_format` —
  OpenSCAD's Customizer can render the legacy ``// [value:Label]`` dropdown
  syntax as duplicate entries in newer builds. The braille generator ate this
  bug in mid-2025; we keep the guard rail in this project too.
* :meth:`TestOpenSCADCustomizer.test_dropdown_default_matches_option` —
  When a dropdown's declared default doesn't match any option literal, the
  Customizer silently injects the default as an extra entry. Detected by
  parsing every ``param = "default"; // [opt1, opt2]`` line.
* :meth:`TestOpenSCADCustomizer.test_no_duplicate_dropdown_options` —
  Defensive deduplication check (catches copy-paste typos in the option list).
* :meth:`TestOpenSCADCustomizer.test_size_dropdown_options` —
  Hardcodes the v5.1 contract: the ``size`` dropdown must offer
  Small / Medium / Large / Measure my hand / Custom. Breaks loudly if a
  future refactor renames one of them without updating the routing / README.
* :meth:`TestOpenSCADCustomizer.test_attachment_dropdown_options` —
  Same for the ``attachment`` dropdown (zip ties / velcro quick options).
* :meth:`TestOpenSCADCustomizer.test_plug_measurements_lead_the_customizer` —
  The plug measurements are the primary input and must stay the FIRST
  Customizer section (file order = UI order in OpenSCAD).
* :meth:`TestOpenSCADCustomizer.test_render_mode_hidden_section` —
  ``render_mode`` is a hidden-section parameter (programmatic switch), not a
  user-facing dropdown. Enforce that it stays under ``/* [Hidden] */`` so the
  Customizer UI is not cluttered with 13 render variants.

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCAD_FILE = PROJECT_ROOT / "src" / "Plug_Puller_Parametric.scad"

EXPECTED_SIZE_OPTIONS = ["Small", "Medium", "Large", "Measure my hand", "Custom"]
EXPECTED_ATTACHMENT_OPTIONS = [
    "Zip ties", "Velcro strap", "Zip ties + Velcro", "None",
]


class TestOpenSCADCustomizer:
    """Static structural checks on the v5 Customizer block."""

    @pytest.fixture
    def scad_content(self) -> str:
        assert SCAD_FILE.exists(), f"v5 SCAD missing: {SCAD_FILE}"
        return SCAD_FILE.read_text(encoding="utf-8")

    def test_scad_file_exists(self) -> None:
        assert SCAD_FILE.exists(), f"v5 SCAD missing: {SCAD_FILE}"

    def test_no_value_colon_label_format(self, scad_content: str) -> None:
        """Reject ``// [value:Label]`` style dropdowns (causes duplicates)."""
        offenders = []
        for line in scad_content.splitlines():
            if "=" not in line or line.strip().startswith("//"):
                continue
            bracket_match = re.search(r"//\s*\[([^\]]+)\]", line)
            if not bracket_match:
                continue
            content = bracket_match.group(1).strip()
            # Skip numeric range sliders: [min:step:max]
            if re.match(r"^-?[\d.]+:-?[\d.]+:-?[\d.]+$", content):
                continue
            # Look for the value:Label pattern (alphanumeric value, capitalized label).
            if re.search(r"[a-zA-Z]\w*:[A-Z]", content):
                offenders.append(line.strip())
        if offenders:
            pytest.fail(
                "Dropdown definitions using the deprecated `value:Label` format "
                "were found. This format can produce duplicate entries in the "
                "OpenSCAD Customizer. Convert to `// [Label1, Label2, ...]` with "
                "the default value matching one of the labels.\n"
                + "\n".join(f"  - {line}" for line in offenders)
            )

    def test_dropdown_default_matches_option(self, scad_content: str) -> None:
        pattern = re.compile(
            r'(\w+)\s*=\s*"([^"]+)"\s*;\s*//\s*\[([^\]]+)\]'
        )
        mismatches = []
        for match in pattern.finditer(scad_content):
            var, default, options_str = match.group(1), match.group(2), match.group(3)
            options = [opt.strip() for opt in options_str.split(",")]
            if default not in options:
                mismatches.append((var, default, options))
        if mismatches:
            details = "\n".join(
                f"  - {v}: default '{d}' not in {o}" for v, d, o in mismatches
            )
            pytest.fail(
                "Dropdown defaults that don't match any option (causes the "
                "Customizer to inject the default as an extra entry):\n" + details
            )

    def test_no_duplicate_dropdown_options(self, scad_content: str) -> None:
        pattern = re.compile(r'(\w+)\s*=\s*"[^"]+"\s*;\s*//\s*\[([^\]]+)\]')
        duplicates = []
        for match in pattern.finditer(scad_content):
            var, options_str = match.group(1), match.group(2)
            options = [opt.strip() for opt in options_str.split(",")]
            seen: set[str] = set()
            for opt in options:
                if opt in seen:
                    duplicates.append((var, opt))
                seen.add(opt)
        if duplicates:
            pytest.fail(
                "Duplicate options inside dropdown definitions:\n"
                + "\n".join(f"  - {v}: '{o}'" for v, o in duplicates)
            )

    def test_no_parentheses_in_dropdown_options(self, scad_content: str) -> None:
        """Reject parentheses inside dropdown option labels.

        The OpenSCAD Customizer fails to parse enum values containing
        parentheses and silently reverts the selection to the default;
        MakerWorld's Parametric Model Maker follows Customizer behaviour.
        (Section headers may use parentheses — only option labels matter.)
        """
        pattern = re.compile(r'(\w+)\s*=\s*"[^"]+"\s*;\s*//\s*\[([^\]]+)\]')
        offenders = []
        for match in pattern.finditer(scad_content):
            var, options_str = match.group(1), match.group(2)
            for opt in (o.strip() for o in options_str.split(",")):
                if "(" in opt or ")" in opt:
                    offenders.append((var, opt))
        if offenders:
            pytest.fail(
                "Dropdown option labels must not contain parentheses (the "
                "OpenSCAD Customizer silently reverts such selections to the "
                "default; MakerWorld PMM inherits this):\n"
                + "\n".join(f"  - {v}: '{o}'" for v, o in offenders)
            )

    def test_size_dropdown_options(self, scad_content: str) -> None:
        match = re.search(
            r'^size\s*=\s*"([^"]+)"\s*;\s*//\s*\[([^\]]+)\]',
            scad_content,
            re.MULTILINE,
        )
        assert match, "Could not find the `size` dropdown declaration in v5 SCAD."
        default = match.group(1)
        options = [opt.strip() for opt in match.group(2).split(",")]
        missing = [name for name in EXPECTED_SIZE_OPTIONS if name not in options]
        assert not missing, (
            f"Size dropdown is missing required options {missing}. "
            f"Found: {options}. The v5.1 contract requires Small / Medium / "
            f"Large / Measure my hand / Custom because the routing, README, "
            f"and guides document them."
        )
        assert default == "Medium", (
            f"The size default must be 'Medium' (= the original Plug Puller), "
            f"got '{default}'."
        )

    def test_attachment_dropdown_options(self, scad_content: str) -> None:
        match = re.search(
            r'^attachment\s*=\s*"([^"]+)"\s*;\s*//\s*\[([^\]]+)\]',
            scad_content,
            re.MULTILINE,
        )
        assert match, (
            "Could not find the `attachment` dropdown declaration in v5 SCAD."
        )
        default = match.group(1)
        options = [opt.strip() for opt in match.group(2).split(",")]
        missing = [
            name for name in EXPECTED_ATTACHMENT_OPTIONS if name not in options
        ]
        assert not missing, (
            f"Attachment dropdown is missing required options {missing}. "
            f"Found: {options}."
        )
        assert default == "Zip ties + Velcro", (
            f"The attachment default must be 'Zip ties + Velcro' (the v6 "
            f"reference device is a hybrid: zip-tie holes plus wing velcro "
            f"slots), got '{default}'."
        )

    def test_plug_measurements_lead_the_customizer(self, scad_content: str) -> None:
        """v7 leads with Step 0 (tool style), then Step 1 (the plug inputs):
        `tool_style` is the very first Customizer parameter, and the plug
        quick-select (`plug_preset`) is the first parameter of the plug
        section, immediately followed by `measure_plug_width`."""
        sections = re.findall(r"/\*\s*\[([^\]]+)\]\s*\*/", scad_content)
        assert sections, "No Customizer sections found in the v7 SCAD."
        assert "Tool Style" in sections[0], (
            f"The tool-style Step 0 section must come first in the Customizer, "
            f"but the first section is '[{sections[0]}]'."
        )
        assert "Your Plug" in sections[1], (
            f"The plug-input section (Step 1) must follow Step 0, but the "
            f"second section is '[{sections[1]}]'."
        )
        first_param = re.search(
            r"^(\w+)\s*=\s*[^;]+;",
            scad_content[scad_content.find(sections[0]):],
            re.MULTILINE,
        )
        assert first_param and first_param.group(1) == "tool_style", (
            "The first Customizer parameter must be `tool_style` (Step 0), "
            f"got `{first_param.group(1) if first_param else None}`."
        )
        plug_params = re.findall(
            r"^(\w+)\s*=\s*[^;]+;", scad_content[scad_content.find(sections[1]):],
            re.MULTILINE,
        )
        assert plug_params and plug_params[0] == "plug_preset", (
            "The first parameter of the plug section must be `plug_preset` "
            f"(the plug quick-select), got `{plug_params[0] if plug_params else None}`."
        )
        assert "measure_plug_length" in plug_params[:3], (
            "`measure_plug_length` must lead the manual plug measurements, "
            f"right after the preset quick-select; got {plug_params[:3]}."
        )
        assert plug_params[1:6] == [
            "measure_plug_length",
            "measure_plug_width_wall",
            "measure_plug_width_cable",
            "measure_plug_thickness_wall",
            "measure_plug_thickness_cable",
        ], (
            "The two-station plug measurements must appear in reading order "
            "(length, then width wall/cable, then thickness wall/cable); "
            f"got {plug_params[1:6]}."
        )

    def test_render_mode_hidden_section(self, scad_content: str) -> None:
        """``render_mode`` must live under ``/* [Hidden] */`` (programmatic switch)."""
        idx = scad_content.find("render_mode")
        assert idx != -1, "render_mode declaration not found in v5 SCAD."
        preceding = scad_content[:idx]
        last_section_match = list(re.finditer(r"/\*\s*\[([^\]]+)\]\s*\*/", preceding))
        assert last_section_match, (
            "Could not find any Customizer section header before `render_mode`. "
            "Expected it to follow `/* [Hidden] */`."
        )
        last_section = last_section_match[-1].group(1).strip().lower()
        assert last_section == "hidden", (
            f"`render_mode` must live under `/* [Hidden] */` so the Customizer UI "
            f"is not cluttered with 13 render variants, but it currently appears "
            f"under section `[{last_section}]`."
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
