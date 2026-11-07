# OpenSCAD Guide

How to make a Plug Puller for one plug and one hand in OpenSCAD, the free desktop program, and export it as an STL file to print. The [Browser Customizer Guide](Step_1_Guide_Option_1_Plug_Puller_Browser_Customizer_Guide.md) does the same with nothing to install.

## What you are making

The Plug Puller is a 3D-printed tool for pulling an electrical plug out of an outlet with the whole hand instead of a fingertip pinch: two fingers go through two finger holes and pull straight back, and the tool touches only the plug's sides and back, never the outlet. It comes as two tools, each its own file, made for a measured plug and hand: the one-sided puller, one printed part, for plugs with 2 prongs and USB-C tips; and the two-sided puller, two printed plates zip-tied around the plug, for plugs with 3 prongs.

## Why the desktop program

OpenSCAD on the desktop renders faster than the browser and keeps the files on your computer, which suits fine-tuning and reprinting. Only one panel of it is used, the Customizer, a form; the code beside it is never touched.

## Make the tool in OpenSCAD

### Step 1: Install OpenSCAD

Download OpenSCAD from the project's downloads page, <https://openscad.org/downloads.html>, and install it. The Development Snapshot renders fastest; this project is tested with the snapshot of 2026-01-03. The regular 2021.01 release works too, only slower.

### Step 2: Get the files

Download the tool's file from the repository, <https://github.com/BrennenJohnston/openscad-plug-puller>: either the whole project (the green **Code** button, then **Download ZIP**, and unzip it anywhere) or the one file for your tool.

| The plug | The tool | The file to open |
|---|---|---|
| 2 prongs, or a USB-C tip | One-sided puller | `src/Plug_Puller_Parametric.scad`, or the one file `dist/Plug_Puller_One_Sided_SingleFile.scad` |
| 3 prongs, or 24 mm thick or more | Two-sided puller | `src/Plug_Puller_Two_Sided.scad`, or the one file `dist/Plug_Puller_Two_Sided_SingleFile.scad` |

Each tool is its own file, and no setting inside one makes the other: for the other tool, open its file.

### Step 3: Open the file and show the Customizer

1. Open the file in OpenSCAD: double-click it, or use **File**, then **Open**.
2. In the **View** menu, make sure **Hide Customizer** is not ticked. In older versions the Customizer is under **Window**.

<!-- shot: screen-openscad-customizer | angle: screen | show: the one-sided puller open, the Customizer showing Step 1; red box 1 on Hide Customizer -->

### Step 4: Fill in the four steps

The Customizer's sections read top to bottom: **Step 1 - Your Plug**, **Step 2 - Size**, **Step 3 - Attachment** and Step 4 (the one-sided puller's cord hook, or the two-sided puller's print layout). Everything below Step 4 is optional.

1. In **plug_preset**, pick your plug if it is on the list: every plug number fills in. Otherwise leave **Measure my plug** and type your numbers into the settings below it, in mm.
2. Pick the hand size in Step 2, the attachment in Step 3, and Step 4.
3. Press **F5** to preview: a see-through plug drawn from your numbers sits in the tool. It is never exported.

What each setting does, how to measure each number, and a picture of what every setting moves are in each tool's quick start and full guide: [one-sided quick start](../docs/guides/one-sided/quick-start.md), [two-sided quick start](../docs/guides/two-sided/quick-start.md).

**Check:** no red text lies beside the tool in the preview. Red text names a number to fix; each tool's full guide decodes every message. The console under the preview lists the same messages.

<!-- shot: screen-openscad-preview | angle: screen | show: the lamp plug preset picked, the preview with its see-through plug; red box 1 on plug_preset -->

### Step 5: Render and export the STL

1. Press **F6** to render the finished tool.
2. Use **File**, then **Export**, then **Export as STL**, and save the file.

The two-sided puller's file holds both plates. Printing and putting the tool on the plug are in the [Maker Guide](Step_2_Guide_Option_3_Plug_Puller_Maker_Guide.md).
