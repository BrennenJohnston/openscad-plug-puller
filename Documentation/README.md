# Documentation

The written guides for the Plug Puller, version 1.0.0, in the Makers Making Change Open AT layout, and the files behind them.

## What is here

| File | What it is |
|---|---|
| `Step_1_Guide_Option_1_Plug_Puller_Browser_Customizer_Guide.md` and `.pdf` | Making the tool in the browser, every step with a marked screenshot |
| `Step_1_Guide_Option_2_Plug_Puller_OpenSCAD_Guide.md` and `.pdf` | Making the tool in the free OpenSCAD desktop program |
| `Step_1_Guide_Option_3_Plug_Puller_MakerWorld_Guide.md` and `.pdf` | Making the tool in MakerWorld's customizer |
| `Step_2_Guide_Option_1_Plug_Puller_Visual_Assembly_Guide.md` and `.pdf` | The assembly without words: one picture a step |
| `Step_2_Guide_Option_2_Plug_Puller_Assembly_Guide_By_Touch.md` and `.pdf` | The full edition: every part described for the hands, every step with what to feel |
| `Step_2_Guide_Option_3_Plug_Puller_Maker_Guide.md` and `.pdf` | The short edition: pick the tool, make it, print it, fit it, test it |
| `Step_3_Guide_Plug_Puller_User_Guide.md` and `.pdf` | For whoever uses the tool: the pull, safety, what to do when it does not go well |
| `Plug_Puller_BOM.csv` | The bill of materials, in the Makers Making Change layout |
| `Plug_Puller_Device_Summary.md` and `.pdf` | What the device is, who it is for, what is in it, its sizes, what changed, licenses |
| `Plug_Puller_Design_Rationale.md` and `.pdf` | Why each default is what it is |
| `Plug_Puller_MakerWorld_Listing.md` and `.docx` | The MakerWorld listing, field by field; `scripts/makerworld_listing_docx.py` writes the Word copy to paste from |
| `Plug_Puller_Listing_Description.md` | The listing's description as plain Markdown for Thingiverse and Printables; written by `scripts/listing_description_markdown.py` |
| `COMPLIANCE_CHECKLIST.md` | The seventeen Makers Making Change checklist items and where each is met |
| `Shot_List.md` | Every photograph the guides still ask for |
| `parts.json` | The facts about each part: name, file, old names, size in mm, what it does, how it feels |
| `images.json` | Every picture under `Photos/`: its source, what it shows, its alt text and caption, and its review state |

Each Markdown page is the source of every sentence and the screen-reader edition. The guides carry the step they belong to in front of their names (Step 1 makes the tool, Step 2 builds it, Step 3 uses it), so a folder of them sorts in the order they are read.

Each tool also keeps its own quick start and full guide under `docs/guides/`: the dial-by-dial reference with a picture of what every setting moves, the measuring form, the plug size finder and the paper stencil at true size. The Step 1 guides point there for the settings rather than repeating them.

## Only what changes the outcome

Every sentence in a guide earns its place by one test: if it were removed and the reader never knew, would the reader be less able to finish the task, or less able to understand the directions? If the answer to both is no, the sentence goes. What stays is a part's shape and where its features are, a step, a check, a warning, and the fix for a problem that has happened.

## No repeated information

A fact, rule or instruction is stated once in a document, where the reader needs it, and pointed to from anywhere else. The three editions of the assembly guide repeat each other by design, and every page opens with the same short description of the device so it can be read alone; no page repeats itself.

## Suggestions, not demands

The guides suggest and explain; they do not order. Where a reader has a choice (which tool's file, which customizer, a setting, the material), the page says what each option is for, may say which one the writers would start with and why, and leaves the choice with the reader. A procedure step stays a plain imperative, and a safety warning stays a warning.

## How the PDF is built

`python scripts/build_open_at_pdf.py --document all` turns each Markdown page into one HTML file and has headless Microsoft Edge or Google Chrome print it to a tagged PDF (`--document user-guide` prints one). The HTML stays in `build/open_at_pdf/` for checking. The script reads the PDF back and refuses to finish unless every page is US Letter; the PDF is tagged, names its language and shows its title; there is a bookmark for every heading in order; every picture is a Figure with the alt text from the page, grouped with its caption; every table's headers carry their scope; the contents page's numbers are the pages the sections land on; and every link on the page is a link in the PDF.

The build writes a record a document under `scripts/pdf_records/`, the SHA-256 of the PDF and of every file it was printed from. `tests/test_open_at_pdf.py` compares that record with the files as they are, so a change to a guide, a picture or the builder without a new print fails the tests. `python scripts/pdf_structure_report.py Documentation/<a PDF>` prints the PDF's structure tree as text, the order a screen reader follows.

## What a person still checks

The checks above are mechanical. Before a release, someone reads each PDF with a screen reader (NVDA on Windows) and confirms:

1. Press H through the headings: every section and every step is announced, in order.
2. Press G to each graphic: the alt text is read, and the caption follows it.
3. Press T to a table: the column headers are announced as you move across a row.
4. Read one whole step from its heading to its By touch paragraph: the Careful, Check and By touch paragraphs are read in place.
5. Open the contents page and activate one entry: it lands on that section.

The result goes into `NOTES/07_SESSIONS/` with the date. This repository makes no claim that the PDF meets PDF/UA, WCAG or any other standard; the checks say what was verified.
