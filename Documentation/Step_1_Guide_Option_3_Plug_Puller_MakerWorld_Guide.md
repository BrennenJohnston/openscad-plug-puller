# MakerWorld Guide

How to make a Plug Puller for one plug and one hand in MakerWorld's customizer, the Parametric Model Maker, and download it as an STL file to print. The [Browser Customizer Guide](Step_1_Guide_Option_1_Plug_Puller_Browser_Customizer_Guide.md) and the [OpenSCAD Guide](Step_1_Guide_Option_2_Plug_Puller_OpenSCAD_Guide.md) do the same elsewhere.

## What you are making

The Plug Puller is a 3D-printed tool for pulling an electrical plug out of an outlet with the whole hand instead of a fingertip pinch: two fingers go through two finger holes and pull straight back, and the tool touches only the plug's sides and back, never the outlet. It comes as two tools, each its own file, made for a measured plug and hand: the one-sided puller, one printed part, for plugs with 2 prongs and USB-C tips; and the two-sided puller, two printed plates zip-tied around the plug, for plugs with 3 prongs.

## Two tools, two customizer files

The MakerWorld listing carries both tools, each as its own customizable file: `Plug_Puller_One_Sided_SingleFile.scad` for a plug with 2 prongs or a USB-C tip, and `Plug_Puller_Two_Sided_SingleFile.scad` for a plug with 3 prongs or any plug 24 mm thick or more. No setting inside one file makes the other tool: count the plug's prongs first, then open that tool's file.

## Make the tool on MakerWorld

### Step 1: Open the tool's file in the customizer

On the Plug Puller's MakerWorld listing, press **Customize** and pick the file for your tool from the list.

### Step 2: Fill in the four steps

The form reads top to bottom: **Step 1 - Your Plug**, **Step 2 - Size**, **Step 3 - Attachment** and Step 4 (the one-sided puller's cord hook, or the two-sided puller's print layout). Everything below Step 4 is optional.

1. In **plug_preset**, pick your plug if it is on the list: every plug number fills in. Otherwise leave **Measure my plug** and type your numbers in mm.
2. Pick the hand size in Step 2, the attachment in Step 3, and Step 4.

What each setting does and how to measure each number are in each tool's quick start: [one-sided](../docs/guides/one-sided/quick-start.md), [two-sided](../docs/guides/two-sided/quick-start.md).

### Step 3: Render and look for red text

Generate the model and look at the render for red text beside the part.

**Check:** no red text. Red text names a number to fix and is part of the model: downloaded with it, it prints as an extra object on the bed. Each tool's full guide decodes every message.

### Step 4: Download the STL

Download the STL. The two-sided puller's file holds both plates. Printing and putting the tool on the plug are in the [Maker Guide](Step_2_Guide_Option_3_Plug_Puller_Maker_Guide.md).

## What MakerWorld's render does not show

MakerWorld shows the finished model only. The red warning text shows, because it is part of the model. These do not: the see-through plug drawn from your numbers, the green note naming the numbers that were applied (one-sided), and the orange notes about ignored Custom settings, auto-fit adjustments (one-sided) and a strap slot left out for a short plug (two-sided). The desktop program and the browser customizer show the see-through plug.
