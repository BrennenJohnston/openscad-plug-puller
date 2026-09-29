## Render, export and print

1. On the computer, press **F6** (or **Design ▸ Render**) and wait for the progress bar to finish; a render takes from a few seconds to a minute. In Forge, the preview draws on its own: wait for **Preview ready** under the picture.
2. Look for red text beside the part. If there is any, read it: it names the measurement to fix, and the part will not fit until it is gone.
3. Save the file: on the computer, **File ▸ Export ▸ Export as STL**; in Forge, **Export STL**. If you export without rendering, OpenSCAD asks you to render first: press F6 and export again. The quick preview (F5) looks complete but cannot be exported.

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
