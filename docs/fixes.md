# Fix Log

## 2026-09-30: the check script could not pass a text value with spaces

**The bug.** `scripts/scad-check.ps1 -Defines` could not check the model with a setting whose value has spaces, such as `size="Measure my hand"` or a plug preset name. Windows PowerShell strips the quotes from such a value twice: when it starts the script with `-File`, and again when the script hands the value to OpenSCAD. OpenSCAD then received `size=Measure my hand`, reported a syntax error on the file's last line, and the check failed however the quotes were written. Fixing that showed a second gap: OpenSCAD does not test a text value against the setting's dropdown list, so a misspelled choice passed the check while the model quietly used its default numbers.

**The fix.** The script now adds the quotes itself when a text value arrives without them, and starts OpenSCAD with a command line it builds by the rules programs use to split one, so no quote is lost on the way. Before OpenSCAD runs, the script reads the setting's dropdown list from the `.scad` file and prints a `WARNING:` line when a text value is not one of the choices, which fails the check. Numbers, `true` and `false`, lists and a run with no settings work as before.

**The check that passed.** From Windows PowerShell and from Git Bash, on `src/Plug_Puller_Parametric.scad`: `-Defines 'size=Measure my hand'` and `-Defines 'size="Measure my hand"'` both print "Derived values for size 'Measure my hand'" and CHECK PASSED; `-Defines 'plug_preset=Standard 3-prong plug - NEMA 5-15'` changes the pocket depth from 25.5 to 46.2 mm; `-Defines 'measure_plug_length=40'` gives a pocket depth of 40 mm; `-Defines 'size=Nonsense size'` prints the warning and CHECK FAILED; and with no `-Defines` the check passes as before.

A known limit, not changed: when PowerShell starts the script with `-File`, several settings given as `'a','b'` arrive joined into one, so give one setting per run there.

## 2026-10-01: the guides printed "{step4}" instead of the fourth step's name

**The bug.** All four documents, the quick starts and the full guides of both tools, as pages and as PDFs, ended a sentence in their Get the file section with "then {step4}" instead of "then Step 4 - Cord Hook" (one-sided puller) or "then Step 4 - Print Layout" (two-sided puller), and a screen reader read the braces aloud. The guide builder fills a source file's `{name}` placeholders from a table, and an unknown name stops the build. The pattern that finds them in `scripts/guide_text.py` accepted letters and underscores only, so a name with a digit, like `step4`, was neither filled nor reported. No release carried it.

**The fix.** The pattern now accepts a name that starts with a letter or an underscore and goes on with letters, digits or underscores, so `{step4}` is filled like every other placeholder, and an unknown name with a digit stops the build. A quick-lane test loads every guide source for both tools and fails if any `{name}` is left unfilled. All four documents are rebuilt; each PDF changes on one page.

**The check that passed.** `tests/test_guide_text.py::test_every_source_fills_for_both_tools` failed before the change ("unfilled ['{step4}']") and passes after it. After rebuilding the four documents, `{step4}` appears under `docs/guides` only in its source file, `docs/guides/source/get-the-file.md`. The builders' PDF checks pass with 15, 88, 13 and 54 pages, as before. The quick lane passes (243) and `scripts/check_docs.py` is clean.

## 2026-10-01: an outline sheet's zip-tie spacing label could read negative

**The bug.** On a one-sided outline sheet, the label between the top two zip-tie holes printed the signed difference between their positions, so it read negative whenever the sheet generator found the right-hand hole first. The committed lamp-plug sheets read "-20.5" (Medium) and "-17.71" (Small), and regenerating the sheets for 0.14.0 would have added "-20.54" (lamp, Large) and "-30.98" (wide appliance plug, Large). The vertical label beside it already printed the plain distance.

**The fix.** `scripts/generate_outline_sheets.py` prints the plain distance for that label too. All 21 sheets and the outline sheets PDF are regenerated. A quick-lane test, `tests/test_outline_sheets.py`, fails if any label on any sheet starts with a minus sign.

**The check that passed.** The new test failed before the change on the two committed lamp sheets and passes after it. The four labels read 17.71, 20.52, 20.54 and 30.98, each equal to the length of its drawn line. All 21 sheets pass the generator's parity checks, the PDF passes its own checks (22 pages, the title, 31 bookmarks), the quick lane passes (250) and `scripts/check_docs.py` is clean.
