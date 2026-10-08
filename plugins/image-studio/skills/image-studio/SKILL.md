---
name: image-studio
description: Design posters, Instagram stories, WhatsApp/community images, flyers, invitations and multi-image story series with flawless Arabic text and untouched real photos. The image is composed in code from layers. All text is typed with real fonts through a headless browser, and AI image generation (Codex CLI / ChatGPT, or any image model) is used only for text-free backgrounds, scenes and textures, plus isolated brush lettering that is read letter by letter before use. Ships a ready toolkit (OFF THE MAP paper-and-gold-foil style, scratch-card reveals, guess-who silhouettes, a library of verified Arabic brush words). Use this whenever the user asks for any designed image, such as بوستر، ستوري، صورة، تصميم، إعلان، دعوة، غلاف, or a picture to send to a community or post on Instagram/WhatsApp, especially with Arabic text, a real person's photo, event announcements, teasers/reveals, or several images that belong together, even if they never mention AI image generation or this skill.
---

# Image Studio

One-shot AI images misspell Arabic (missing dots, ة turned into ت, letters dropped) and quietly
redraw faces. So build every image in **layers, in code**. Code places everything. AI paints only
things that contain no normal text. Every word is either typed with a real font or an AI brush word
that was read letter by letter. This is the method behind Harmony Community's OFF THE MAP campaign,
which went out with no text errors.

## Setup for a new design

The toolkit is the `kit/` folder next to this file. Copy it into a fresh project folder and work there:

```bash
mkdir -p "<project>" && cp -r "<this skill's folder>/kit/." "<project>/"
```

Use one folder per design or series, in a place the user can open (their documents or project
folder; in a cloud sandbox, the working directory). Put the user's photo at `inputs/photo.jpg` and,
if they have one, their logo at `inputs/logo.png` or `inputs/logo.jpg`.

What the kit needs:

- **Python 3 with Pillow and numpy.** OpenCV (`opencv-python`) is needed only for `cutout.py`.
- **A Chromium-based browser** (Chrome, Edge or Chromium) for typed text. `series_lib` finds it on
  Windows, macOS and Linux; set the `CHROME` environment variable to point at a specific one.
- **Optional: the Codex CLI logged in with ChatGPT** (`codex login status`) for `gen.sh`. Without it,
  use any image generator with the prompts in `references/prompts.md`.

Pillow usually has **no Arabic shaping**, so never draw Arabic with `ImageDraw.text`. Text always
goes through `series_lib.chrome_layer`.

## The rules, and why

1. **Compose in code.** Usual layer order: paper or background, real photo in a torn frame, shapes
   and decorations, foil, seals and coins, brush headline, typed text, logo. Layers make every
   element exact, movable and repeatable across a series.
2. **Normal text is never drawn by an image model.** Sublines, clue tags, names in small text,
   dates, footers and numbers are typed HTML rendered by a headless browser
   (`series_lib.chrome_layer`), which shapes and joins Arabic correctly.
3. **AI only for:** text-free paper and textures, scenes and landscapes, silhouettes on white, and
   brush display words generated alone on pure white. Read every brush word letter by letter,
   generate two attempts in parallel, keep a correct one, and never patch a wrong one by hand.
   Read `references/lettering.md` before generating any word.
4. **Real photos, faces and logos are never regenerated.** Crop, scale, mask into shapes and apply
   a very slight grade (colour about 0.94, about 5% toward cream). Nothing else: people notice
   when a face changes.
5. **Keep the user's wording exactly**, including dialect, and tell them about any change you
   suggest. Facts in clues must be true. Research people and places online when asked
   ("اقرأ عنه") and give sources.
6. **Series:** one base design, and change only what is meant to change. In reveals, each stage
   keeps everything revealed before it. Hidden things (face, name, answer) must not leak early.
7. **Verify by looking.** Open the full image, then zoomed crops of every text area, face, seal and
   edge. Fix and re-check. Most bugs show up only when zoomed in: overlaps, crumbs on text, a
   sliver of face showing.
8. **Deliver well:** numbered PNGs in posting order, in a clear folder. Hand them to the user the way
   your environment allows (attach the files, or open the output folder for them). Keep earlier
   versions instead of overwriting them.

## Toolkit (`kit/`)

| File | Purpose |
|---|---|
| `template_poster.py` | **Start here.** One image (feed 1080×1350 or story 1080×1920): paper, logo, torn frame with the real photo, optional foil peek, seal, coin, brush headline, typed text, footer. Edit the CONFIG block. |
| `series_lib.py` | Core library (and the 8-story series script). `build_plate`, `blob_polygon`/`rough`/`dilate`/`mask_from_poly` (torn frames), `chrome_layer` (typed text), `use_word` + `headline` (brush words with gold swoosh), `zigzag`/`apply_foil`/`leftovers`/`apply_streaks` (scratch foil), `coin`, `flakes`, `edge_points`, `catmull`, `star`. |
| `words/` + `words/INDEX.md` | Library of verified brush words («احزر مين؟», «ضيف مميز», «صوّت!», «تلميحات»…). Reuse them without regenerating: `ms.use_word("head", "dayf_mumayyaz")`. |
| `add_word.py` | Add a newly verified word from a lettering sheet to the library. |
| `gen.sh` | Generate an image with Codex: `./gen.sh "$PWD/out.png" "$PWD/ref.png"\|none "<prompt>"`. |
| `grid.py` | Draw a coordinate grid on a photo to find the face and subject before placing layers. |
| `cutout.py` | Cut a person's outline out of a real photo (GrabCut), e.g. for a gold "guess who" figure. |
| `logo.py` | The user's logo, if `inputs/logo.png` or `.jpg` exists: `place(img, center, size, "line")` on paper, `"badge"` on photos or dark areas. Without a logo file it does nothing. |
| `plate2.png`, `foil.png`, `lettering.png`, `fonts/` | Paper background, gold foil texture, brush-style reference sheet, Tajawal and Montserrat fonts (SIL Open Font License). |

Scripts read their files relative to the project folder, so run them from there.

## Workflow

1. **Pin down the request:** what, how many images, platform and size (Instagram story 1080×1920
   with the logo in the top ~12% and the bottom 15% free for stickers; WhatsApp or feed post
   1080×1350, which WhatsApp shows uncropped), exact text, photos, and brand. The kit's ready look
   is OFF THE MAP (paper, forest green, gold); for another brand take the palette, fonts and logo
   from the user's references and keep the same layered method. Ask only if something essential is
   missing. Otherwise choose and say so.
2. **Locate things in photos:** `python grid.py inputs/photo.jpg`, then read the grid image (face
   centre, subject box, clear sky). Use these coordinates, not guesses.
3. **Start the AI parts first, in the background** (each takes 1–5 min): any new brush words (two
   attempts in parallel) and any scene or texture. Check `words/INDEX.md` first: the word may
   already exist.
4. **While they run,** write `make_<name>.py` from `template_poster.py`, or adapt an example from
   `references/examples/` (see `references/recipes.md`).
5. **Verify each new brush word** letter by letter, then add it with `add_word.py`.
6. **Render, look, zoom, fix** using the checklist below.
7. **Deliver** (rule 8) with a short summary in the user's language: what each image is, what is AI
   and what is real or typed, any assumptions they should confirm, and suggested stickers or
   posting order for series.

## Verification checklist

- Every Arabic word matches the requested text: letters, dots, joins, ة/ت, hamza, ؟ (mirrored Arabic form).
- Nothing collides: decorations or stars against text, the swoosh against rules, tags against edges or peek windows.
- No foil crumbs or specks on text (pass the text zones as `avoid=` to `apply_foil` and `leftovers`).
- Hidden things stay hidden at every stage: zoom on the face patch and the name panel.
- Exact size, safe zones respected, logo present (if the user has one), footer readable.
- The real photo is only cropped and graded, and not stretched (use its real width and height, never assume a size).
- Placeholder text from the template (event line, venue, seal text) has been replaced with the user's.

## Gotchas learned the hard way

- `codex exec -i <ref> ...` swallows the prompt unless it is preceded by `--` (`gen.sh` already does this).
- Headless Chrome renders «» guillemets backwards in RTL lines, so use straight quotes "…".
- Mixed Arabic/Latin lines (e.g. "الـAI") render fine, but zoom to check the order.
- A star or sparkle above a headline can hit the line above it. Use `star_on=False`, or move it.
- A gold swoosh under a short headline can touch the footer rule. Use `swoosh_k=0.6`.
- With foil crumbs on a clean sky, use fewer crumbs (`crumb_n` around 110).
- Time-zone clues change with daylight-saving time, so check the date. Prefer timeless facts.
- An Instagram **Quiz** reveals the right answer as soon as someone taps. Use a **Poll** before the reveal.
- AI scenes may contain objects that clash with the layout (a paraglider cut by the frame). Move or
  remove them by transferring the object's difference from the interpolated sky (see `references/recipes.md`).
- If `chrome_layer` raises "did not render", the browser was not found or could not start: set
  `CHROME` to the browser's full path and run again.

## References (read when needed)

- `references/lettering.md`: generating and verifying brush words (prompt template, failures seen).
- `references/recipes.md`: scratch-card story series, guess-who poster with the real outline, reveal
  stories, community image, AI-scene fixes, the Instagram engagement playbook, writing clues.
- `references/style-off-the-map.md`: the OFF THE MAP palette, fonts, logo placement and look, and how
  to swap in another brand.
- `references/prompts.md`: copy-paste prompts for when the user wants to use ChatGPT or another
  image tool themselves.
- `references/examples/`: reference scripts from the original campaign (guess-who poster, guest
  reveal stories, community image), with names and facts replaced by placeholders.

## Without Codex or a browser

The method is the same anywhere. If Codex isn't available, give the user the brush-word prompt from
`references/prompts.md` to run in ChatGPT or another image generator, ask them to upload the result,
and verify it the same way. If no Chromium-based browser is available, render text with any engine
that shapes Arabic, and confirm by looking at the result.
