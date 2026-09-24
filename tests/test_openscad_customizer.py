"""OpenSCAD Customizer hygiene tests.

These tests are *static* — they parse the two tool files
(``src/Plug_Puller_Parametric.scad``, the one-sided puller, and
``src/Plug_Puller_Two_Sided.scad``, the two-sided puller) with regular
expressions and never invoke OpenSCAD itself, so they run in under a second
on CI's quick lane.

Why each check exists (``TestCustomizerHygiene`` runs on both files):

* :meth:`TestCustomizerHygiene.test_no_value_colon_label_format` —
  OpenSCAD's Customizer can render the legacy ``// [value:Label]`` dropdown
  syntax as duplicate entries in newer builds. The braille generator ate this
  bug in mid-2025; we keep the guard rail in this project too.
* :meth:`TestCustomizerHygiene.test_dropdown_default_matches_option` —
  When a dropdown's declared default doesn't match any option literal, the
  Customizer silently injects the default as an extra entry. Detected by
  parsing every ``param = "default"; // [opt1, opt2]`` line.
* :meth:`TestCustomizerHygiene.test_no_duplicate_dropdown_options` —
  Defensive deduplication check (catches copy-paste typos in the option list).
* :meth:`TestCustomizerHygiene.test_no_parentheses_in_dropdown_options` —
  The Customizer (and MakerWorld's PMM) silently reverts selections whose
  label contains parentheses.
* :meth:`TestCustomizerHygiene.test_render_mode_hidden_section` —
  ``render_mode`` is a hidden-section parameter (programmatic switch), not a
  user-facing dropdown. Enforce that it stays under ``/* [Hidden] */``.
* :class:`TestOneSidedCustomizer` — the one-sided file's size and attachment
  option contracts and its Step order (the routing, README and guides
  document them).
* :class:`TestTwoSidedCustomizer` — the two-sided file leads with Step 1, its
  size and attachment options are exactly the owner's choices (Q-12), and
  none of the one-sided puller's controls appear in it.

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCAD_FILE = PROJECT_ROOT / "src" / "Plug_Puller_Parametric.scad"
TWO_SIDED_SCAD_FILE = PROJECT_ROOT / "src" / "Plug_Puller_Two_Sided.scad"
SCAD_FILES = {"one_sided": SCAD_FILE, "two_sided": TWO_SIDED_SCAD_FILE}

EXPECTED_SIZE_OPTIONS = ["Small", "Medium", "Large", "Measure my hand", "Custom"]
EXPECTED_ATTACHMENT_OPTIONS = [
    "Zip ties", "Velcro strap", "Zip ties + Velcro", "None",
]

TWO_SIDED_SIZE_OPTIONS = ["Small", "Medium", "Large", "Measure my hand"]
TWO_SIDED_ATTACHMENT_OPTIONS = ["Zip ties + Velcro strap", "Zip ties"]
ONE_SIDED_ONLY_PARAMETERS = [
    "measure_plug_width_wall",
    "measure_plug_width_cable",
    "measure_plug_thickness_wall",
    "measure_plug_thickness_cable",
    "measure_plug_thickness_prong_end",
    "measure_plug_thickness_cord_end",
    "measure_wall_plate_style",
    "measure_hand_width",
    "tool_style",
    "velcro_style",
    "hook_hand",
]


def _read(path: Path) -> str:
    assert path.exists(), f"SCAD file missing: {path}"
    return path.read_text(encoding="utf-8")


def _dropdown(scad_content: str, name: str):
    match = re.search(
        rf'^{name}\s*=\s*"([^"]+)"\s*;\s*//\s*\[([^\]]+)\]',
        scad_content,
        re.MULTILINE,
    )
    assert match, f"Could not find the `{name}` dropdown declaration."
    return match.group(1), [opt.strip() for opt in match.group(2).split(",")]


@pytest.fixture(params=sorted(SCAD_FILES), ids=sorted(SCAD_FILES))
def scad_content(request) -> str:
    return _read(SCAD_FILES[request.param])


class TestCustomizerHygiene:
    """Static structural checks on both files' Customizer blocks."""

    @pytest.mark.parametrize("which", sorted(SCAD_FILES))
    def test_scad_file_exists(self, which: str) -> None:
        assert SCAD_FILES[which].exists(), f"SCAD missing: {SCAD_FILES[which]}"

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

    def test_render_mode_hidden_section(self, scad_content: str) -> None:
        """``render_mode`` must live under ``/* [Hidden] */`` (programmatic switch)."""
        idx = scad_content.find("render_mode")
        assert idx != -1, "render_mode declaration not found."
        preceding = scad_content[:idx]
        last_section_match = list(re.finditer(r"/\*\s*\[([^\]]+)\]\s*\*/", preceding))
        assert last_section_match, (
            "Could not find any Customizer section header before `render_mode`. "
            "Expected it to follow `/* [Hidden] */`."
        )
        last_section = last_section_match[-1].group(1).strip().lower()
        assert last_section == "hidden", (
            f"`render_mode` must live under `/* [Hidden] */` so the Customizer UI "
            f"is not cluttered with render variants, but it currently appears "
            f"under section `[{last_section}]`."
        )


class TestOneSidedCustomizer:
    """The one-sided file's option contracts and Step order."""

    @pytest.fixture
    def scad_content(self) -> str:
        return _read(SCAD_FILE)

    def test_size_dropdown_options(self, scad_content: str) -> None:
        default, options = _dropdown(scad_content, "size")
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
        default, options = _dropdown(scad_content, "attachment")
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
        """The one-sided file leads with Step 1 (the plug inputs): the plug
        quick-select (`plug_preset`) is the very first Customizer parameter,
        followed by the plug measurements in reading order. The two-sided
        puller has its own file, so there is no tool-style step."""
        sections = re.findall(r"/\*\s*\[([^\]]+)\]\s*\*/", scad_content)
        assert sections, "No Customizer sections found in the one-sided SCAD."
        assert sections[0] == "Step 1 - Your Plug", (
            f"The first Customizer section must be 'Step 1 - Your Plug', "
            f"but it is '[{sections[0]}]'."
        )
        assert not re.search(r"^tool_style\s*=", scad_content, re.MULTILINE), (
            "The one-sided file must not declare `tool_style`: the two-sided "
            "puller is its own file."
        )
        plug_params = re.findall(
            r"^(\w+)\s*=\s*[^;]+;", scad_content[scad_content.find(sections[0]):],
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
            "measure_plug_width_prong_end",
            "measure_plug_width_cord_end",
            "measure_plug_thickness_prong_end",
            "measure_plug_thickness_cord_end",
        ], (
            "The two-station plug measurements must appear in reading order "
            "(length, then width prong end/cord end, then thickness prong "
            "end/cord end); "
            f"got {plug_params[1:6]}."
        )

    def test_section_titles_name_no_tool(self, scad_content: str) -> None:
        """The file builds one tool, so no Customizer section title names a
        tool (owner answer Q-24: drop "- Flat Tool")."""
        sections = re.findall(r"/\*\s*\[([^\]]+)\]\s*\*/", scad_content)
        named = [s for s in sections if "Flat Tool" in s or "Clamshell" in s]
        assert not named, f"Section titles still name a tool: {named}"


class TestTwoSidedCustomizer:
    """The two-sided file shows only the two-sided puller's controls."""

    @pytest.fixture
    def scad_content(self) -> str:
        return _read(TWO_SIDED_SCAD_FILE)

    def test_step1_leads_with_plug_preset(self, scad_content: str) -> None:
        sections = re.findall(r"/\*\s*\[([^\]]+)\]\s*\*/", scad_content)
        assert sections and sections[0] == "Step 1 - Your Plug", (
            f"The first Customizer section must be 'Step 1 - Your Plug', got "
            f"{sections[:1]}."
        )
        first_param = re.search(
            r"^(\w+)\s*=\s*[^;]+;",
            scad_content[scad_content.find(sections[0]):],
            re.MULTILINE,
        )
        assert first_param and first_param.group(1) == "plug_preset", (
            "The first Customizer parameter must be `plug_preset`, got "
            f"`{first_param.group(1) if first_param else None}`."
        )

    def test_size_options(self, scad_content: str) -> None:
        default, options = _dropdown(scad_content, "size")
        assert options == TWO_SIDED_SIZE_OPTIONS, (
            f"Two-sided size options must be exactly {TWO_SIDED_SIZE_OPTIONS} "
            f"(no Custom: the plate has no custom geometry), got {options}."
        )
        assert default == "Medium", f"Size default must be 'Medium', got '{default}'."

    def test_attachment_options(self, scad_content: str) -> None:
        default, options = _dropdown(scad_content, "attachment")
        assert options == TWO_SIDED_ATTACHMENT_OPTIONS, (
            f"Two-sided attachment options must be exactly "
            f"{TWO_SIDED_ATTACHMENT_OPTIONS} (owner answer to Q-12: both other "
            f"options build a plate nothing holds together), got {options}."
        )
        assert default == "Zip ties + Velcro strap", (
            f"Attachment default must be 'Zip ties + Velcro strap' (the preset "
            f"plate has the strap slot), got '{default}'."
        )

    def test_no_one_sided_parameters(self, scad_content: str) -> None:
        declared = set(re.findall(r"^(\w+)\s*=", scad_content, re.MULTILINE))
        present = [name for name in ONE_SIDED_ONLY_PARAMETERS if name in declared]
        assert not present, (
            f"The two-sided file must not declare one-sided or renamed "
            f"parameters, but declares {present}."
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
