# Fix Log

## 2026-09-30: the check script could not pass a text value with spaces

**The bug.** `scripts/scad-check.ps1 -Defines` could not check the model with a setting whose value has spaces, such as `size="Measure my hand"` or a plug preset name. Windows PowerShell strips the quotes from such a value twice: when it starts the script with `-File`, and again when the script hands the value to OpenSCAD. OpenSCAD then received `size=Measure my hand`, reported a syntax error on the file's last line, and the check failed however the quotes were written. Fixing that showed a second gap: OpenSCAD does not test a text value against the setting's dropdown list, so a misspelled choice passed the check while the model quietly used its default numbers.

**The fix.** The script now adds the quotes itself when a text value arrives without them, and starts OpenSCAD with a command line it builds by the rules programs use to split one, so no quote is lost on the way. Before OpenSCAD runs, the script reads the setting's dropdown list from the `.scad` file and prints a `WARNING:` line when a text value is not one of the choices, which fails the check. Numbers, `true` and `false`, lists and a run with no settings work as before.

**The check that passed.** From Windows PowerShell and from Git Bash, on `src/Plug_Puller_Parametric.scad`: `-Defines 'size=Measure my hand'` and `-Defines 'size="Measure my hand"'` both print "Derived values for size 'Measure my hand'" and CHECK PASSED; `-Defines 'plug_preset=Standard 3-prong plug - NEMA 5-15'` changes the pocket depth from 25.5 to 46.2 mm; `-Defines 'measure_plug_length=40'` gives a pocket depth of 40 mm; `-Defines 'size=Nonsense size'` prints the warning and CHECK FAILED; and with no `-Defines` the check passes as before.

A known limit, not changed: when PowerShell starts the script with `-File`, several settings given as `'a','b'` arrive joined into one, so give one setting per run there.
