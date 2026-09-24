"""Build the flattened single-file SCAD artifacts for web customizers.

Deterministically inlines each tool's include tree into one file in
``dist/`` so the model can be loaded by front-ends that do not support local
``include <>`` trees:

* ``dist/Plug_Puller_SingleFile.scad`` — the one-sided puller
  (``src/Plug_Puller_Parametric.scad`` with ``fit_sizes.scad`` +
  ``fit_measured.scad`` + ``presets.scad`` inlined), and
* ``dist/Plug_Puller_Two_Sided_SingleFile.scad`` — the two-sided puller
  (``src/Plug_Puller_Two_Sided.scad`` with ``fit_sizes.scad`` inlined),

for:

* MakerWorld Parametric Model Maker (single ``.scad`` upload only), and
* openscad-playground / customizer deployments via a ``?src=<raw URL>`` load.

The outputs are *generated artifacts*: they are committed so beginners can
download one file, and CI verifies freshness on every run
(``python scripts/build_flattened.py --check`` in the lint job, plus the
render-parity tests in ``tests/test_flattened_build.py``).

Determinism and safety rails:

* Only the includes listed for a build are inlined, in the order they appear
  in the source. Any other ``include``/``use`` statement — or a nested
  include inside an inlined file — is a hard error, so an unexpected change
  to the include graph fails the build instead of silently producing a
  broken artifact.
* The generated header carries the PolyForm Noncommercial 1.0.0 notice and a
  do-not-edit marker. No timestamps or commit hashes are embedded, so each
  artifact is byte-stable for identical sources.

Usage:

    python scripts/build_flattened.py            # (re)write dist/
    python scripts/build_flattened.py --check    # exit 1 if any artifact is stale

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import argparse
import re
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
DIST_DIR = PROJECT_ROOT / "dist"


@dataclass(frozen=True)
class Build:
    """One flattened artifact: a main file, its include graph, its output."""

    main: Path
    includes: Tuple[str, ...]  # the exact include graph, in source order
    output: Path
    title: str


BUILDS: Tuple[Build, ...] = (
    Build(
        main=SRC_DIR / "Plug_Puller_Parametric.scad",
        includes=("fit_sizes.scad", "fit_measured.scad", "presets.scad"),
        output=DIST_DIR / "Plug_Puller_SingleFile.scad",
        title="Plug Puller — one-sided puller",
    ),
    Build(
        main=SRC_DIR / "Plug_Puller_Two_Sided.scad",
        includes=("fit_sizes.scad",),
        output=DIST_DIR / "Plug_Puller_Two_Sided_SingleFile.scad",
        title="Plug Puller — two-sided puller",
    ),
)

# Aliases for the first build, kept for callers written before there were two.
MAIN_SCAD = BUILDS[0].main
OUTPUT_FILE = BUILDS[0].output
EXPECTED_INCLUDES = list(BUILDS[0].includes)

INCLUDE_RE = re.compile(r"^\s*(include|use)\s*<([^>]+)>\s*;?\s*$")

_RULE = "// " + "=" * 77


def _header(build: Build) -> str:
    names = list(build.includes)
    if len(names) == 1:
        inlined = names[0]
    else:
        inlined = ", ".join(names[:-1]) + " and " + names[-1]
    summary = (
        f"{build.title}: the flattened single-file build of "
        f"src/{build.main.name}, with {inlined} inlined. Generated from the "
        f"canonical sources in src/ — edit those files, not this one."
    )
    summary_lines = "\n".join(
        "// " + line for line in textwrap.wrap(summary, width=76)
    )
    return (
        f"{_RULE}\n"
        f"// {build.output.name} — GENERATED FILE, DO NOT EDIT\n"
        f"{_RULE}\n"
        "//\n"
        f"{summary_lines}\n"
        "//\n"
        "// Purpose: web customizers (MakerWorld Parametric Model Maker,\n"
        "// openscad-playground `?src=` loading) accept only a single .scad file with\n"
        "// no local include tree. This artifact renders identically to the modular\n"
        "// build.\n"
        "//\n"
        "// Source repository:\n"
        "//   https://github.com/BrennenJohnston/openscad-plug-puller\n"
        "//\n"
        "// License: PolyForm Noncommercial 1.0.0\n"
        "//   https://polyformproject.org/licenses/noncommercial/1.0.0/\n"
        "//   Personal, hobby, educational, research, and other noncommercial use is\n"
        "//   permitted. Contact the maintainer for commercial use.\n"
        f"{_RULE}\n"
        "\n"
    )


def _inline_marker(name: str, kind: str) -> str:
    bar = "=" * 75
    return (
        f"// ── {bar}\n"
        f"// ── {kind}: {name} (inlined by scripts/build_flattened.py)\n"
        f"// ── {bar}\n"
    )


def build_flattened_source(build: Optional[Build] = None) -> str:
    """Return one flattened single-file SCAD artifact (default: the first build)."""
    build = build or BUILDS[0]
    expected = list(build.includes)
    main_source = build.main.read_text(encoding="utf-8")

    seen_includes: list[str] = []
    out_lines: list[str] = []

    for line in main_source.splitlines(keepends=True):
        match = INCLUDE_RE.match(line)
        if not match:
            out_lines.append(line)
            continue

        kind, target = match.group(1), match.group(2)
        if kind == "use":
            raise RuntimeError(
                f"Unexpected `use <{target}>` in {build.main.name}; this "
                f"script only knows how to flatten `include` statements "
                f"of {expected}."
            )
        if target not in expected:
            raise RuntimeError(
                f"Unexpected `include <{target}>` in {build.main.name}. The "
                f"include graph changed — update BUILDS (and the "
                f"web-customizer docs) deliberately."
            )
        seen_includes.append(target)

        included_path = SRC_DIR / target
        included_source = included_path.read_text(encoding="utf-8")
        for inner in included_source.splitlines():
            if INCLUDE_RE.match(inner):
                raise RuntimeError(
                    f"Nested include/use found inside {target}: {inner.strip()!r}. "
                    f"Flattening only supports a one-level include graph."
                )

        out_lines.append(_inline_marker(target, "BEGIN"))
        out_lines.append(included_source)
        if not included_source.endswith("\n"):
            out_lines.append("\n")
        out_lines.append(_inline_marker(target, "END"))

    if seen_includes != expected:
        raise RuntimeError(
            f"Include graph mismatch in {build.main.name}: expected {expected} "
            f"in order, found {seen_includes} (top-level assignments evaluate "
            f"in source order)."
        )

    flattened = _header(build) + "".join(out_lines)

    for line in flattened.splitlines():
        if INCLUDE_RE.match(line):
            raise RuntimeError(
                f"Flattened output still contains an include/use statement: "
                f"{line.strip()!r}"
            )
    return flattened


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="Do not write; exit 1 if any committed dist/ artifact is stale.",
    )
    args = parser.parse_args()

    stale = 0
    for build in BUILDS:
        flattened = build_flattened_source(build)

        if args.check:
            if not build.output.exists():
                print(f"STALE: {build.output} does not exist. Run: python scripts/build_flattened.py")
                stale += 1
                continue
            committed = build.output.read_text(encoding="utf-8")
            if committed != flattened:
                print(
                    f"STALE: {build.output} does not match the sources. "
                    f"Run: python scripts/build_flattened.py"
                )
                stale += 1
                continue
            print(f"OK: {build.output} is up to date ({len(flattened)} chars).")
            continue

        build.output.parent.mkdir(parents=True, exist_ok=True)
        build.output.write_text(flattened, encoding="utf-8", newline="\n")
        print(f"Wrote {build.output} ({len(flattened)} chars).")

    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
