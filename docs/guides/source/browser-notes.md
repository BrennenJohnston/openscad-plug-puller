### Working in the browser

The Playground and the desktop program show the same form. Three differences:

- The Playground's preview does not draw the see-through plug; the desktop program does. Both show the red text of a warning.
- Rendering in the browser is slower: half a minute to a few minutes on a laptop, several minutes on a phone. Keep the tab in front while it works.
- On a phone the screen is tight: use the tabs to switch between the editor, the form and the preview. You never need the editor tab. If the tab crashes during a render, close other tabs and try again, or set the `quality` dial (in **Advanced - Render Quality**) to 32 while you test, and back to 64 before the final export.

You can measure, type and render on a phone, then send the downloaded file to whoever runs the printer.

| Problem | What to do |
| ------- | ---------- |
| The link opens the Playground but the model is not there | Download the single file and drag it into the page, as described under Get the file. |
| "Failed to fetch", or a blank editor | The download from GitHub was blocked: offline, a firewall, or GitHub is down. Use the single file. |
| The form is empty | Wait for the first render to finish; the form is built after the model loads. |
| The Render button seems stuck | Browser renders are slow; give it a few minutes. If it never finishes, set `quality` to 32 and try again. |
| The downloaded file is tiny or empty | Render first, then export. |
