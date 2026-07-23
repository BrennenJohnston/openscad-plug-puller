# Customize in Your Browser — No Install Needed

You can build a Plug Puller that fits **your** plug and **your** hand
without installing anything: the free
**[OpenSCAD Playground](https://ochafik.com/openscad2/)** runs OpenSCAD
entirely inside your web browser (nothing is uploaded — your numbers
stay on your device). It works on a laptop and, with a little patience,
on a phone or tablet too.

You still follow the same three moves as the desktop path — **measure,
type numbers, export** — so keep the
**[Measuring Guide](measuring-guide.md)** open in another tab.

> **Prefer the desktop app?** The
> **[Quick Start for Beginners](quick-start-beginner.md)** walks
> through the installed-OpenSCAD path instead. The desktop app renders
> faster and is the better choice if you plan to reprint or fine-tune.

---

## Step 1 — Open the model in the Playground

**Click this link** (it loads the whole model in one go):

> **[Open the Plug Puller in the OpenSCAD Playground](https://ochafik.com/openscad2/#url=https://raw.githubusercontent.com/BrennenJohnston/openscad-plug-puller/main/dist/Plug_Puller_SingleFile.scad)**

Give it a moment — the first visit downloads the OpenSCAD engine
(~10–20 MB) and then fetches the model. When it finishes you'll see
code on the left (ignore it) and a 3D preview on the right.

**If the link doesn't load the model** (some browsers or an outage can
interfere), load it manually — it's two steps:

1. Download the single-file model:
   [`dist/Plug_Puller_SingleFile.scad`](../../dist/Plug_Puller_SingleFile.scad)
   (on the GitHub page press the download button, or right-click **Raw**
   → *Save link as…*).
2. Open <https://ochafik.com/openscad2/> and **drag the downloaded file
   into the page** (or use the file menu in the top bar to open it).

## Step 2 — Find the customizer form

The Playground reads the model's parameter form the same way desktop
OpenSCAD does:

- Look for the **Customize** panel (on a wide screen it's a panel or
  tab beside the editor; on a phone it's a tab at the bottom).
- You'll see the same numbered sections as the desktop Customizer:
  **Step 0 - Tool Style**, **Step 1 - Your Plug**, **Step 2 - Size**,
  **Step 3 - Attachment**, **Step 4 - Cord Hook** — then the optional
  `Advanced -` and `(Custom size only)` sections you can ignore.

## Step 3 — Type your numbers

Work top to bottom, exactly as in the
[Measuring Guide](measuring-guide.md) worksheet:

1. **Step 0** — leave `tool_style` on **Auto from plug**.
2. **Step 1** — pick a `plug_preset` (the three most common US plugs
   are built in) or leave it on **Measure my plug** and type your six
   plug numbers.
3. **Step 2** — pick **Small / Medium / Large**, or **Measure my hand**
   and type your two hand numbers.
4. **Step 3** — pick the attachment (**Zip ties + Velcro** is the
   default).
5. **Step 4** — `hook_hand` = **Right** or **Left**.

The preview re-renders as you change values. A green tag next to the
model means your numbers were applied; **red text** names a measurement
that looks wrong (usually inches instead of millimetres) — fix it
before printing. The
**[Fit Troubleshooting Guide](fit-troubleshooting.md)** decodes every
message.

## Step 4 — Render and download the STL

1. Press the **Render** button (the Playground's equivalent of F6).
   In the browser this is slower than desktop OpenSCAD — expect roughly
   half a minute to a few minutes depending on your device.
2. When it finishes, press the **download / export STL** button and
   save the file.
3. Print it with the settings in the
   [README's 3D printing tips](../../README.md#3d-printing-tips)
   (flat face down, no supports, PETG recommended).

## Using a phone or tablet

The Playground works on mobile browsers, with caveats:

- **It's slow.** A full render can take several minutes on a phone.
  Leave the tab in the foreground while it works.
- **Screen space is tight.** Use the tabs to switch between the
  editor, the customizer form, and the preview; you never need to
  touch the code tab.
- **Memory limits.** If the tab crashes mid-render, close other tabs
  and retry, or drop the `quality` slider (bottom of the form's
  advanced sections) to `32` for testing — but export the final STL at
  the default `64`.
- You can measure, type, and render on the phone, then send the
  downloaded STL to whoever runs the printer.

## Troubleshooting

| Problem | Fix |
| ------- | --- |
| The link opens the Playground but the model isn't there | Use the manual path in Step 1 (download the file, drag it into the page). |
| "Failed to fetch" or a blank editor | The raw-GitHub fetch was blocked (offline, firewall, or the repository is temporarily unavailable). Use the manual path in Step 1. |
| The customizer form is empty | Wait for the first render to finish — the form is built from the model file after it loads. |
| Render button seems stuck | Browser renders are genuinely slow; give it a few minutes. If it never finishes, drop `quality` to `32` and retry. |
| The downloaded STL is tiny or empty | Render first, then export — same rule as the desktop app. |

---

## Other zero-install options

- **MakerWorld** — once the model is listed on MakerWorld, its
  Parametric Model Maker shows the same customizer form with a
  cloud-rendered preview (see
  [Publishing to MakerWorld](../../README.md#publishing-to-makerworld)
  in the README).
- **Ready-to-print STLs** — no customization at all: grab a
  pre-rendered Small / Medium / Large from
  [`stl/`](../../stl) and print.
