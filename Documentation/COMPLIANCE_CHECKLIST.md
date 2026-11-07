# Makers Making Change documentation checklist

Where each of the seventeen items of the Open AT Template Guide's Final Documentation Checklist (V1.0.0, September 2024, pages 42 and 43) is met in this repository, and what is not met. The status words are: met, the item is satisfied by files here; owner, a step the designer still has to do; not met, the item cannot be satisfied and the reason is given; not applicable, the item is not about this device.

## The seventeen items

| Item | Status | Where, or why not |
|---|---|---|
| 1. At least one open source license applied | owner | `LICENSES/`: PolyForm Noncommercial 1.0.0, named in `README.md` and `okh.yml`; whether Makers Making Change accepts it is asked first |
| 2. Alt text on every image in every document | met | Every picture in every page has alt text; `images.json` records each as draft until the designer has read it |
| 3. Device Summary completed | met | `Plug_Puller_Device_Summary.md` and `.pdf` |
| 4. PDF created for the User Guide | met | `Step_3_Guide_Plug_Puller_User_Guide.pdf`, printed from its Markdown by `scripts/build_open_at_pdf.py` |
| 5. PDF created for the Maker Guide | met | `Step_2_Guide_Option_3_Plug_Puller_Maker_Guide.pdf`; the Assembly Guide By Touch and the Visual Assembly Guide are its two further editions |
| 6. PDF created for the Design Workbook or Design Rationale | met | `Plug_Puller_Design_Rationale.pdf` |
| 7. Bill of materials saved as a CSV file | met | `Plug_Puller_BOM.csv`; masses are upper bounds from the STL volumes until a sliced project exists |
| 8. All image files renamed, none left as a camera name | met | `tests/test_images_manifest.py` refuses any camera-style name under `Photos/` and `MakerWorld_Photos/` |
| 9. CAD design files added | met | The OpenSCAD sources in `src/` are the design files, with single-file copies in `dist/` |
| 10. STEP files added | not met | OpenSCAD writes no STEP file; the design is parametric OpenSCAD, and a STEP of one size would not carry the customizer |
| 11. 3D printing files added | met | `stl/Plug-Puller/` (15 tools: every preset at three hand sizes) and `stl/Measuring-Stencil/` |
| 12. Custom PCB design files (if required) | not applicable | No electronics |
| 13. Custom PCB build files (if required) | not applicable | No electronics |
| 14. GitHub repository created | met | <https://github.com/BrennenJohnston/openscad-plug-puller>, public |
| 15. Unnecessary template folders and files removed | met | Only folders with content are kept, beside the code layout (`src/`, `dist/`, `stl/`, `docs/`); `NOTES/` is the record |
| 16. GitHub README complete | owner | `README.md` follows the Open AT headings; the Makers Making Change link is filled in when Makers Making Change assigns it |
| 17. Open Know-How manifest complete | met | `okh.yml` names every document, the printing files, the license and the lead picture |

## Beyond the checklist

These are not checklist items, but the template's guidance asks for them.

- Document names follow `Plug_Puller_<Document>`; the guides carry the step they belong to in front, `Step_<N>_Guide_Option_<M>_`, so they sort in the order they are used.
- Pictures are at least 500 by 350 pixels, shown in the pages at their figure size; the lead picture in `README.md` is a photograph of the tool in use.
- Every PDF is tagged, names its language, shows its title, has a bookmark for every heading, and carries each picture's alt text; `Documentation/README.md` says how that is checked and what a screen-reader check still has to confirm by hand.
- Print orientation is stated for every part in the Maker Guide's print table; no sliced project exists yet.

## Where this list is kept up to date

Change this page when a document is added or an item's status changes; `README.md` links to it from its documentation table.
