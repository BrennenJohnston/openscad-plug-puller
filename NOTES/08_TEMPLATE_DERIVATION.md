# Template derivation

What in this package is generic and what is this device's alone. Written at the end of each round so the next project can start from it.

## Generic

| Piece | Where it is here | Notes |
|---|---|---|
| The PDF builder | `scripts/build_open_at_pdf.py` | The template's builder with this project's `DOCUMENTS`, names and version |
| The PDF structure report | `scripts/pdf_structure_report.py` | Unchanged |
| The listing's Word copy and plain export | `scripts/makerworld_listing_docx.py`, `scripts/listing_description_markdown.py` | File names changed |
| The photo import | `scripts/photo_import.py` | Hand-set crop boxes instead of mat detection |
| The MakerWorld pictures | `scripts/makerworld_photos.py` | Hand-set crop boxes; renders drawn by OpenSCAD from the STLs |

## This device's alone

- Two tools in two files, split by the prong count; one tool per plug.
- A customizer is the custom part's generator, and the whole printed tool is the custom part.
- The plug size finder and the measuring form, generated from the preset table.

## Which question produced which section

| Question to the owner | What it produced |
|---|---|
| Which presets each tool keeps | The split in every guide, the finder's two groups, the prong question on the form |
| How the test prints held | The design rationale's split section, the listing's story, the fit notes |
| The two-sided assembly order | The assembly steps of every guide |
