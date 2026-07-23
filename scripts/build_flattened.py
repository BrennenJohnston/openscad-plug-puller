"""Build the flattened single-file SCAD artifact for web customizers.

Deterministically inlines the include tree (``fit_measured.scad`` +
``presets.scad``) into ``dist/Plug_Puller_SingleFile.scad`` so the model
can be loaded by front-ends that do not support local ``include <>`` trees:

* MakerWorld Parametric Model Maker (single ``.scad`` upload only), and
* openscad-playground / customizer deployments via a ``?src=<raw URL>`` load.

The output is a *generated artifact*: it is committed so beginners can
download one file, and CI verifies freshness on every run
(``python scripts/build_flattened.py --check`` in the lint job, plus the
render-parity tests in ``tests/test_flattened_build.py``).

Determinism and safety rails:

* Only the includes listed in ``EXPECTED_INCLUDES`` are inlined, in the
  order they appear in the source. Any other ``include``/``use`` statement —
  or a nested include inside an inlined file — is a hard error, so an
  unexpected change to the include graph fails the build instead of
  silently producing a broken artifact.
* The generated header carries the PolyForm Noncommercial 1.0.0 notice and a
  do-not-edit marker. No timestamps or commit hashes are embedded, so the
  artifact is byte-stable for identical sources.

Usage:

    python scripts/build_flattened.py            # (re)write dist/
    python scripts/build_flattened.py --check    # exit 1 if dist/ is stale

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
MAIN_SCAD = SRC_DIR / "Plug_Puller_Parametric.scad"
OUTPUT_FILE = PROJECT_ROOT / "dist" / "Plug_Puller_SingleFile.scad"

# The exact include graph this script knows how to flatten. Order matters
# (fit_measured must precede presets — see the include-order note in the
# main SCAD); the script asserts the source agrees.
EXPECTED_INCLUDES = ["fit_measured.scad", "presets.scad"]

INCLUDE_RE = re.compile(r"^\s*(include|use)\s*<([^>]+)>\s*;?\s*$")

HEADER = """\
// =============================================================================
// Plug_Puller_SingleFile.scad — GENERATED FILE, DO NOT EDIT
// =============================================================================
//
// Flattened single-file build of the Plug Puller 0.8 parametric model, with
// fit_measured.scad and presets.scad inlined. Generated from the canonical
// sources in src/ — edit those files, not this one.
//
// Purpose: web customizers (MakerWorld Parametric Model Maker,
// openscad-playground `?src=` loading) accept only a single .scad file with
// no local include tree. This artifact renders identically to the modular
// build.
//
// Source repository:
//   https://github.com/BrennenJohnston/openscad-plug-puller
//
// License: PolyForm Noncommercial 1.0.0
//   https://polyformproject.org/licenses/noncommercial/1.0.0/
//   Personal, hobby, educational, research, and other noncommercial use is
//   permitted. Contact the maintainer for commercial use.
// =============================================================================

"""


def _inline_marker(name: str, kind: str) -> str:
    bar = "=" * 75
    return (
        f"// ── {bar}\n"
        f"// ── {kind}: {name} (inlined by scripts/build_flattened.py)\n"
        f"// ── {bar}\n"
    )


def build_flattened_source() -> str:
    """Return the flattened single-file SCAD content as a string."""
    main_source = MAIN_SCAD.read_text(encoding="utf-8")

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
                f"Unexpected `use <{target}>` in {MAIN_SCAD.name}; this "
                f"script only knows how to flatten `include` statements "
                f"of {EXPECTED_INCLUDES}."
            )
        if target not in EXPECTED_INCLUDES:
            raise RuntimeError(
                f"Unexpected `include <{target}>` in {MAIN_SCAD.name}. The "
                f"include graph changed — update EXPECTED_INCLUDES (and the "
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

    if seen_includes != EXPECTED_INCLUDES:
        raise RuntimeError(
            f"Include graph mismatch: expected {EXPECTED_INCLUDES} in order, "
            f"found {seen_includes}. fit_measured.scad must be included "
            f"before presets.scad (FIT_MEASURED assignment order)."
        )

    flattened = HEADER + "".join(out_lines)

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
        help="Do not write; exit 1 if the committed dist/ artifact is stale.",
    )
    args = parser.parse_args()

    flattened = build_flattened_source()

    if args.check:
        if not OUTPUT_FILE.exists():
            print(f"STALE: {OUTPUT_FILE} does not exist. Run: python {__file__}")
            return 1
        committed = OUTPUT_FILE.read_text(encoding="utf-8")
        if committed != flattened:
            print(
                f"STALE: {OUTPUT_FILE} does not match the sources. "
                f"Run: python scripts/build_flattened.py"
            )
            return 1
        print(f"OK: {OUTPUT_FILE} is up to date ({len(flattened)} chars).")
        return 0

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(flattened, encoding="utf-8", newline="\n")
    print(f"Wrote {OUTPUT_FILE} ({len(flattened)} chars).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
