# What the pipeline needs from a project

The inputs the scripts and tests expect, and the constants in them that hold this device's data.

| Script | Constant | What it holds for this device |
|---|---|---|
| `scripts/build_open_at_pdf.py` | `DOCUMENTS`, `PROJECT`, `REPO`, `PROJECT_EYEBROW`, `MODEL_VERSION`, `COVER_SOURCE` | The nine documents and the names on their covers |
| `scripts/photo_import.py` | `--masters` or `PLUG_PULLER_MASTERS` | The October 2026 photo folder, outside the repository |
| `scripts/makerworld_photos.py` | `PHOTOS`, `RENDERS`, `--masters`, `--july` | Each slot's master and crop box; the STLs rendered |
| `scripts/forge_screenshots.py` | `MANIFEST`, `PRESET` | The manifest the release puts on the Forge's example branch; the preset shown |
| `scripts/makerworld_bundle.py` | `STEP_GUIDES`, `TOOL_GUIDES` | The seven step guides and the four per-tool guides in the ZIP |
