# The OFF THE MAP style, and using your own brand

OFF THE MAP is the ready look that ships with the kit: textured paper, forest green and muted gold.
It was designed for a Harmony Community (مجتمع هارموني) meetup about travel stories. Use it as it is,
or keep the layered method and swap in another brand's palette, fonts and logo.

## Logo
- The kit ships **without a logo**. Put the user's logo at `inputs/logo.png` or `inputs/logo.jpg`.
- `logo.place(img, (540, 112), 150, "line")`: line-art in the brand colour, for light paper (the default).
- `logo.place(img, center, size, "badge")`: the logo as a solid disc, for photos or dark areas.
- Top centre, inside the top ~12% of stories.
- `logo.py` expects a round logo drawn light-on-dark, and recolours the line-art with `logo.GREEN`:
  set that to the brand colour. For any other kind of logo, composite the file as it is. Never
  redraw or regenerate a logo.

## Colours
| use | hex |
|---|---|
| main text, seals, pins, pills | forest green `#1E3A2B` |
| logo line-art (default) | `#0C6C47` |
| rules, swoosh, dashed routes | muted gold `#B8975A` / `#C4A05C` |
| seal rims | gold `#C9A35E` |
| big numbers on green, rim text | light gold `#E2C27E`, `#E8D19C` |
| highlighted words in typed text | dark gold `#8C6A2F` |
| tags, text on green | cream `#F4ECDB`; paper `#F5EEDF` |

## Fonts (`kit/fonts`, `@font-face` names in `chrome_layer`)
- `Taj` = Tajawal ExtraBold: sublines and clue tags (46–56 px).
- `TajBold` = Tajawal Bold: profession and role lines, kickers (31–38 px).
- `TajB` = Tajawal Black: heavy marks (the embossed «؟»).
- `Mont` = Montserrat variable: English capitals with letter-spacing, footers, numbers (600–800).
- Big Arabic headlines: brush words from `kit/words/`.

Both families are under the SIL Open Font License (texts in `kit/fonts/`).

## The look
Off-white textured paper (`plate2.png`) with faint contour lines, a compass rose top right, and a
torn-paper photo frame with a white paper border, soft shadow and scattered gold-leaf flakes. A gold
dashed route with waypoint circles leads to a green map pin (`draw_pin`, with a number) and a cream
tag (`draw_tag`). Gold scratch foil with coin strokes, bevel and crumbs, a gold coin with a star,
and round green seals with gold rims and text along the rim.

Footer line: `EVENT NAME · DAY DD.MM · HH:MM · VENUE`. The templates carry the placeholder
`OFF THE MAP · THU 15.10 · 18:00 · YOUR VENUE`: change it in `series_lib.FOOTER` and in the
`FOOTER` / `SEAL_RIM` constants of the script you are editing.

## Another brand
1. Replace the hex colours above (they appear in `series_lib.chrome_layer`'s CSS, `GREEN`/`GOLD`, and
   the seal SVGs) with the brand's palette.
2. Swap the fonts in `kit/fonts` and the `@font-face` lines if the brand has its own Arabic and Latin
   faces. Keep the licence of any font you add.
3. Generate a new paper or background plate with the prompts in `prompts.md`. For brush words in a
   new style, make a new reference sheet and keep one fixed phrase as line 1 of every sheet, so
   `add_word.py` can scale all words to the same letter size (see `lettering.md`).
