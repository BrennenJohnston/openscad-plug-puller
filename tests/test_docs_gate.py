"""The documentation gate: ``scripts/check_docs.py`` over ``README.md`` and
every Markdown file under ``docs/`` (quick lane, standard library only)."""

from __future__ import annotations

from pathlib import Path

from scripts.check_docs import check_file, gate_files

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_docs_gate_reports_nothing() -> None:
    findings = []
    for path in gate_files(PROJECT_ROOT):
        findings += check_file(path)
    report = "\n".join(f.format() for f in findings)
    assert not findings, f"{len(findings)} finding(s):\n{report}"


def test_gate_rules_fire_on_a_bad_file(tmp_path: Path) -> None:
    bad = tmp_path / "bad.md"
    (tmp_path / "exists.md").write_text("# ok\n", encoding="utf-8")
    bad.write_text(
        "# One\n\n# Two\n\n#### Skipped\n\n![](missing.png)\n\n![photo of a thing](exists.md)\n\n"
        "Please [click here](exists.md) and check the console.\n\n"
        "We leverage a robust flat tool.\n\n"
        "| a | b |\n|---|---|\n| " + " ".join(["word"] * 23) + " | x |\n\n"
        "This is WCAG compliant.\n\n[gone](nowhere.md)\n",
        encoding="utf-8",
    )
    rules = {f.rule for f in check_file(bad)}
    for rule in ("one-h1", "heading-level", "alt-text", "alt-text-prefix", "link-text", "console",
                 "banned-word", "retired-word", "table-cell", "compliance-claim", "broken-link"):
        assert rule in rules, f"the {rule} rule did not fire; fired: {sorted(rules)}"
