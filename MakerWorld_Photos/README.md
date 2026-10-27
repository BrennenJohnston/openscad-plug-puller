# MakerWorld photos

The pictures for the MakerWorld listing, cut to the shapes and sizes of its upload form, one folder for each section of the form. `scripts/makerworld_photos.py` makes them: each photograph from its full-size master (the October 2026 test series of the two-sided puller on the standard and heavy-duty plugs, and the July 2026 one-sided series), each rendering by OpenSCAD from a shipped STL.

| Folder | Where it goes on the upload form | Size |
|---|---|---|
| `Cover/` | `1_desktop_4x3.jpg` is the desktop cover, `2_mobile_3x4.jpg` the mobile app cover | 1600 by 1200; 768 by 1024 |
| `Real_Photos/` | The real photos, uploaded in the order of their numbers | 1600 by 1200 |
| `Renders/` | The 3D renderings | 1600 by 1200 |

The form asks for real photos of the printed object from the front, the side and the top: `01_front_both_plates.jpg` is the front view and shows the whole printed object, `02_top_finished_standard_plug.jpg` and `03_top_finished_heavy_duty_plug.jpg` are top views, and `04_side_pulling_heavy_duty_plug.jpg` is the side view, taken in use. A side view of the finished tool on its own is still to be photographed. `07_one_sided_on_lamp_plug.jpg` shows the one-sided puller; the October series shows only the two-sided puller.

The sizes are the ones users report MakerWorld shows uncropped. If the upload form recommends other sizes, change `GALLERY` and `MOBILE` near the top of the script and run it again, naming the photo folders:

    python scripts/makerworld_photos.py --masters "<October 2026 photo folder>" --july "<July 2026 edited photos>"
