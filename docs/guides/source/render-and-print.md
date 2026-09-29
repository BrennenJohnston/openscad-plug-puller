## Render, export and print

1. Press **F6** (or **Design ▸ Render**) and wait for the progress bar to finish. In the browser, press **Render**. A render takes from a few seconds to a minute on a computer, longer in a browser.
2. Look for red text beside the part. If there is any, read it: it names the measurement to fix, and the part will not fit until it is gone.
3. Save the file: **File ▸ Export ▸ Export as STL** on the computer, or the download button in the browser. If you export without rendering, OpenSCAD asks you to render first: press F6 and export again. The quick preview (F5) looks complete but cannot be exported.

Load the STL into your slicer with these settings:

| Setting | Value |
| ------- | ----- |
| Orientation | {orientation}. No supports. |
| Layer height | 0.2 mm |
| Walls | 3 to 4: you pull hard on this part |
| Infill | 25 to 35 percent |
| Material | PETG. PLA, ABS and ASA work too. Never a flexible filament: the tool has to stay stiff. |

{layout_note}

{print_photo}
