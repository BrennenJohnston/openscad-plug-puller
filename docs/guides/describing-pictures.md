# Describing pictures

Every picture in this project's guides has two text parts: a short alt text that says what the picture is, and a long description that carries what the picture shows. The dial pictures under `docs/dials/`, the storyboards and the measuring form sheets get theirs from `scripts/generate_dial_diagrams.py` and `scripts/generate_measuring_form.py`, written by rules, so all of them have the same shape; the owner reads a sample before they ship. This page gives the ten rules with their sources, the two templates the generator fills in, three examples as generated, and what to do when you write one by hand for a photo.

## The ten rules

1. **Two parts for every complex picture.** A short alt text that identifies the picture and says where the long description is, and a long description in the page text with the information the picture carries. Source: the W3C Web Accessibility Initiative, [Complex images](https://www.w3.org/WAI/tutorials/images/complex/); NCAM's guideline 4 (a brief summary followed by extended description), read 2026-09-26.
2. **No "image of".** The alt text never opens with "image of", "picture of", "photo of" or "diagram of"; a screen reader already says it is an image. It names the kind of picture only when the kind matters, as in "before and after". Source: [WebAIM, Alternative Text](https://webaim.org/techniques/alttext/), read 2026-09-26; the Accessible MakerWorld Documentation Standard, section 1.4; the docs gate (`scripts/check_docs.py`) enforces it.
3. **Overview first, then details.** One sentence on what the picture is, then the panels left to right, then the marked parts as a numbered list whose numbers are the ones drawn on the picture. Source: [NCAM, Guidelines for Describing STEM Images](https://www.wgbh.org/foundation/services/ncam/tools-resources/effective-practices-for-description-of-science-content-guidelines-for-describing-stem-images), guideline 4, read 2026-09-26; Zong and others, [Rich Screen Reader Experiences for Accessible Data Visualization](https://arxiv.org/abs/2205.04917), 2022, on structure and navigation; the Perkins School for the Blind, [Creating image descriptions](https://www.perkins.org/resource/creating-image-descriptions-alt-text/), "general to specific", read 2026-09-27.
4. **Say the data, not the appearance.** The values with their units, the direction of the change, and the part names the guides use; a color is named in the key and never carries the meaning alone. Source: NCAM, guidelines 2 and 5; WebAIM (accurate and equivalent); Perkins, "be objective".
5. **One spatial vocabulary everywhere.** The plug end is the top of the picture and the cord end the bottom; left and right as printed; the part names are the ones the catalog's "Moves" lines and the picture's key use. Source: Perkins, "consider your audience" and "tone and language" (the reader's own vocabulary); the DIAGRAM Center's image description guidelines say the same by report (see the note under the sources).
6. **Short.** An alt text of at most 150 characters; a dial's long description of at most 90 words, a storyboard's of at most 150; no sentence repeats the card's own text. Source: WebAIM (succinct, not redundant); NCAM, guideline 1 (brevity); Perkins, "be concise".
7. **A process is a numbered list.** One line per stage, never a paragraph. Source: NCAM, guideline 6.
8. **Say what did not change** when the change is small or none. Source: Zong and others, 2022 (readers compare); the project's accessibility rule that a text reader must never have to guess.
9. **Where the text lives.** The SVG's `desc` element carries the long description; the Markdown page puts it as visible text right under the image; the PDF wraps the picture in a `figure` with the long description as its caption; no `longdesc` attribute. Source: the W3C tutorial's figure approach; WebAIM (`longdesc` is deprecated).
10. **Every description is a reviewed string.** Each alt text and long description is a flagged row in the round's strings pack, proposed until the owner has read the sample. Source: the project's accessibility rule 12 and the planning kit's strings rule.

## The sources, and the two not opened

The W3C tutorial pages, WebAIM, NCAM and the arXiv abstract were read on 2026-09-26; the Perkins page on 2026-09-27 in a browser (it names the DIAGRAM Center and WebAIM as its own sources and adds "context is key", "consider your audience", "be concise", "be objective", "general to specific", "tone and language"; nothing in it contradicts the rules above). The DIAGRAM Center's [Image Description Guidelines](http://diagramcenter.org/table-of-contents-2.html) could not be opened on either day: the fetch tool rejected the site's certificate on 2026-09-26 and a browser showed an error page for both its http and https addresses on 2026-09-27. What this page says about them is by report only (a search result and the Perkins page): a two-part text alternative, and processes as nested lists, which rules 1 and 7 already say.

## The alt text template

```text
{title}: before and after, {before} to {after} {unit}; red marks {the parts, each with "the", joined with commas and "and"}.
```

When that runs past 150 characters, the parts are counted instead: `…; red marks 6 parts, named below.` A dial that changes no shape gets `{title}: changes no shape.` The two-sided print layout, drawn as one panel, gets `{title}: one view, {before} to {after}; the layout with both plates, nothing marked.`

## The long description template

```text
Two top views of {the one-sided puller | one plate of the two-sided puller}, before left and after right, the plug end at the top.
Left: the defaults{ with {dial} set to {value}}, a {w} mm wide plug in teal.
Right: {title} {at {value} {unit} | set to {value}}: {the changes sentence}.
Marked in red: 1, {the part}: {where it sits}. 2, {the parts}: {where they sit}{, removed}. …
{The unnamed parts, up to four} stay where they were. | Everything else follows the outline.
```

A section row opens with `Two vertical slices of {the tool} at {x | y} = {at} mm, before left and after right, the top face up.` and its left panel says `the plug in teal in the cut`. When the whole runs past 90 words, the generator drops the closing sentence first, then the changes sentence, then the locations of the entries that carry several names, then every location; the numbered list itself is never dropped. Where a part sits comes from one table per tool in the generator (`FEATURE_LOCATIONS`): for the one-sided puller the body edge is "the outer outline", the pocket "the plug recess on the centerline", the seat "the round recess at the plug end", the wall notch "the notch in the top edge", the wing openings "the two openings beside the pocket", the zip-tie holes "the four small holes beside the pocket", the finger holes "the two large holes in the lower half", the hook "the cord hook slot in the bottom edge"; for the two-sided puller the plate edge is "the outer outline", the arms "the two toothed arms in the upper half", the teeth "the serrated inner edges of the arms", the finger lobes "the two rounded lobes in the lower half", the cord channel "the gap between the lobes at the bottom", the zip stations "the three small holes along each arm", the strap slot "the long slot in each arm".

## Three examples, as generated

**Plug width at the prong end** (one-sided, 25 to 32 mm).

Alt text: Plug width at the prong end: before and after, 25 to 32 mm; red marks 5 parts, named below.

Long description: Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults, a 25 mm wide plug in teal. Right: plug width at the prong end at 32 mm. Marked in red: 1, the zip-tie holes: the four small holes beside the pocket. 2, the wing openings: the two openings beside the pocket. 3, the wall notch, the seat and the body edge: the notch in the top edge; the round recess at the plug end; the outer outline.

**Pocket depth** (one-sided, Custom size, 24.5 to 34 mm).

Alt text: Pocket depth: before and after, 24.5 to 34 mm; red marks the pocket and the wing openings.

Long description: Two top views of the one-sided puller, before left and after right, the plug end at the top. Left: the defaults with hand size set to Custom, a 25 mm wide plug in teal. Right: pocket depth at 34 mm: runs the plug recess farther from the plug end toward the finger holes. Marked in red: 1, the pocket: the plug recess on the centerline. 2, the wing openings: the two openings beside the pocket.

**Cord thickness** (two-sided, 4 to 9 mm).

Alt text: Cord thickness: before and after, 4 to 9 mm; red marks the arms, the cord channel, the finger lobes and the zip stations.

Long description: Two top views of one plate of the two-sided puller, before left and after right, the plug end at the top. Left: the defaults, a 20 mm wide plug in teal. Right: cord thickness at 9 mm. Marked in red: 1, the finger lobes and the cord channel. 2, the finger lobes: the two rounded lobes in the lower half. 3, the finger lobes and the arms. 4, the zip stations: the three small holes along each arm.

Every generated text is in `docs/dials/dial_diagrams_index.json` (`alt` and `long_description`) and on the page [Dial diagrams](../dials/README.md), the alt on the image and the long description right under it.

## When you write one by hand

A photo in the Maker Guide or the User Guide follows the same rules, by hand: say what the photo shows and what the reader is meant to see in it, in the guides' own words for the parts; never open with "photo of"; keep it under 150 characters and put anything longer in the paragraph next to it; say the numbers with "mm"; and flag the text for the owner's reading before it ships, as the Accessible MakerWorld Documentation Standard, section 1.4, asks. The docs gate checks every image for an alt text and for the forbidden openers; it cannot check that the words are true, so someone reads them.
