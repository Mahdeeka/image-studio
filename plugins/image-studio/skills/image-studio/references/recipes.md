# Recipes

Proven designs from the OFF THE MAP campaign. Each recipe names its reference script in
`references/examples/`. Those scripts are for reading and adapting: their photos, scenes and extra
lettering sheets are not included, and names and facts are placeholders.

## Contents
1. Scratch-card story series (8 stories)
2. Guess-who poster with the guest's real outline in gold
3. Guest reveal stories (4)
4. Community / WhatsApp image (4:5)
5. Fixing objects in an AI scene
6. Instagram engagement playbook
7. Writing clues

---

## 1. Scratch-card story series (8 stories, 1080×1920)

Reference: `kit/series_lib.py` (its `main()` is the series script; the constants at the top belong to
one speaker). The speaker's real photo sits in a torn frame under gold scratch foil, and each story
scratches more.

| # | story | foil state | headline | suggested sticker |
|---|---|---|---|---|
| 1 | intro «رح نكشف / أول·تاني·تالت رحلة / رح تكون معنا ب15/10» | sealed, one tiny scratch | brush word | Countdown |
| 2 | «حزّر وين؟» | small peek window (a hint: towers, lake…) | brush | none |
| 3 | «تلميحات»: 3 clue tags with icons | same peek | brush | none |
| 4 | «صوّت!»: still sealed, the clues again, empty space for the poll | same peek | brush | **Poll** (not Quiz) |
| 5 | first scratch reveals the pin tag (e.g. "180 KM") | + tag | speaker's name, hidden under foil | Emoji slider |
| 6 | subject revealed, face still under a foil blob | + body and landscape | same | Question box |
| 7 | answer revealed (trip title, profession), face and name still hidden by two patches | everything except the patches | same | share the poll result |
| 8 | full reveal: name, title, «القصة كاملة باللقاء الجاي» | none | name | Link + mention |

How the masks work (all are canvas-size L images; white = scratched):
- `peep`: `zigzag(draw, PEEP_BOX, …)` → `rough()` → × `photo_mask`. `STREAKS.clear()` keeps the peek clean.
- Each later stage = `ImageChops.lighter(previous, new strokes)`, so reveals are cumulative.
- Face kept hidden: `subtract(stage, rough(mask_from_poly(blob(FACE, rx, ry))))`. Make the blob a
  bit bigger than the face, and zoom to check that no sliver of face shows.
- Name kept hidden: a torn foil panel over the text block (`cover = lighter(photo_mask, panel)`),
  minus the reveal, keeping a `name_p` patch over the name.
- `apply_foil(img, cover, reveal, seed, crumb_n, avoid=[TAG, TEXT_ZONE])` draws the foil with bevel,
  shadow and crumbs. The `avoid` boxes keep crumbs off text.

Per-speaker edits: `TRIP_TITLE`, `PROFESSION`, `MEETUP_LINE`, `CLUES` (+ `ICONS`), the photo placement
`PS, PX0, PY0`, `FACE`, `PEEP`, `PIN`, `TAG`, `ROUTE`/`WAYPOINTS`, the `zigzag(d2, …)` boxes, the pin
number in `draw_pin`, the tag text in `draw_tag`, and which lettering sheet supplies the name and
intro word. Find every coordinate with `grid.py` on the photo, then convert:
canvas = photo × PS + offset.

## 2. Guess-who poster with the guest's real outline in gold

Reference: `examples/make_poster.py` (`person_figure`, `gold_figure`). It needs the guest's real photo.
Without a photo, use an AI silhouette on white (prompt in `prompts.md`), keyed with `key_white()`.

1. Cut the outline: `cutout.person_mask(photo, rect, fg=[…], bg=[…], bg_polys=[…], out="person_mask.png")`.
   Check `person_mask_preview.png` (red = cut away). Mark narrow gaps (between arm and body, chair
   studs) and the table as background.
2. Clean it: `cutout.clean_silhouette(mask, solid_from_y=<row below the shoulders>)` removes thin bits
   (glasses arms) and makes the lower body one solid bust.
3. Place it: crop to the mask bbox, scale (~0.5–0.62), paste at (x0, y0) on the canvas, × `photo_mask`.
4. Gold: drop shadow, then `apply_foil(img, mask, empty_reveal, seed, 0)`, then an embossed «؟» on the
   face (typed via `chrome_layer`, masked to the figure, light offset under a dark gold copy).
5. Clue tags on the left, a coin near the figure, headline «احزر مين؟», talk title, footer.

The silhouette is recognisable to people who know the guest, and it matches the later reveal exactly.

## 3. Guest reveal stories (4, 1080×1920)

Reference: `examples/make_guest_stories.py`.
1. «احزر مين؟»: sealed foil over the guest's real photo, 3 clue tags, a peek at a detail (a hat).
2. «عرفتوه؟»: hat, jacket and hand revealed; face under a foil blob.
3. Face revealed; the name panel still under foil.
4. Full reveal: name (brush), role line, talk title.
A small green seal «ضيف مميز / SPECIAL GUEST» on every story marks the guest as special. The talk title
stays on all four, so people remember it.

## 4. Community / WhatsApp image (1080×1350)

Reference: `examples/make_community.py`; generic version: `kit/template_poster.py`.
4:5 shows uncropped in WhatsApp chats. Layout: logo → torn frame (scene + hidden gold figure) →
round seal with the urgent number («ضايل / 10 / أماكن بس») → kicker «رح يستنانا» → brush headline
«ضيف مميز» → sub «بكرا رح نعلن عنه» → green pill CTA «الحق حالك قبل الكشف» → rule and footer.
The user writes the message text themselves; the image carries the headline, the urgency and the
event line, so it still works when forwarded without the text. Keep the number in a constant: it
changes.

## 5. Fixing objects in an AI scene

To move or remove something on a clean background (e.g. a paraglider cut by the frame), interpolate
the sky across its box from the columns on each side, then add the object's difference from that
sky at the new place (`make_poster.move_paraglider`). Removing is the same without the add
(`make_community.remove_paraglider`). Thin lines survive, and the new sky matches. Do not do this on
textured areas (mountains): pick a clean destination.

## 6. Instagram engagement playbook

- Order: hook → clues → vote → reveal in stages → full reveal with the call to action.
- Use a **Poll**, not a Quiz, before the reveal (a Quiz shows the right answer on tap). Put the right
  answer second, not first, and make the wrong options plausible traps. Example: منغوليا / سيبيريا
  ✓ / ألاسكا / كازاخستان, with منغوليا as the strongest trap.
- Stickers: Countdown on the intro, Question box mid-way, Emoji slider on a "dare" moment, share the
  poll result on the answer story, and Link + @mention of the speaker on the final story (their
  reshare reaches their followers).
- Cadence: stories 1–4 together (people vote while the clues are fresh), 5–6 a few hours later, 7–8 in
  the evening. Save the series to a Highlight.
- An announcement line on the first and last story («حابين نكشفلكم أول رحلة رح تكون معنا باللقاء
  الجاي», «القصة كاملة باللقاء الجاي») lets viewers who only see one story understand the context.
- Leave the bottom ~15% of every story empty for stickers.

## 7. Writing clues

Three true, specific facts that point to the answer without naming it, from broad to telling.
Personal facts from the trip beat encyclopedia facts. When the user gives the clues, use their
wording exactly. When you write them, research and say so. Watch facts that expire, like time
zones that change with daylight-saving time. Make sure the answer appears only from the answer story
onwards: check the trip title, tags and sublines of the earlier stories for leaks.
