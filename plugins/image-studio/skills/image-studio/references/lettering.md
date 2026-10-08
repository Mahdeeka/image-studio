# Brush lettering: generate, verify, reuse

Brush headlines (big hand-painted Arabic words) are the only place an image model draws letters, and
it gets them wrong often. Every word must be checked before it touches a design.

## 1. Check the library first

`kit/words/INDEX.md` lists words already verified («احزر مين؟», «حزّر وين؟», «تلميحات», «صوّت!»,
«جاي؟», «عرفتوه؟», «ضيف مميز», «ما وراء الجرأة», «أول/تاني/تالت رحلة»…).
If the word is there, use it:

```python
import series_lib as ms
ms.use_word("head", "dayf_mumayyaz")
layer, box = ms.headline("head", band=(896, 1086), extra=0.8, star_on=False, swoosh_k=1.0)
img.alpha_composite(layer)
```

`headline()` centres the word horizontally in `band`, adds the gold swoosh (and an optional sparkle
star), and returns the layer and the word's box. Library words are stored at headline size for
`extra=1.0` (a 9-letter name is ~730 px wide); typical `extra` is 0.6–0.9.

## 2. Generate a new word (two attempts, in the background)

Always attach `kit/lettering.png` as the style reference and keep «مهدي كبها» as **line 1**. That
phrase (the skill author's name) is only the size reference and never appears in a design:
`add_word.py` scales every sheet so that line is 929 px wide, which keeps every word in the library at
the same letter size. A person's name is generated the same way, as line 2 or 3 of a sheet.

```bash
PR="Lettering sheet, portrait 1024x1536. Use EXACTLY the same hand-painted Arabic brush lettering style as the attached sheet: same very bold stroke weight, same dark forest-green (#1E3A2B), same rough dry-brush edges and light scratches inside the strokes, same letter size as the attached sheet. Perfectly flat pure white (#FFFFFF) background, no texture, no shadows, no gold, no decorations, nothing else. Two separate phrases stacked vertically and centered, with lots of empty white space between them. Line 1: مهدي كبها . Line 2: <WORD> . CRITICAL SPELLING: <letter-by-letter spec>. Spell everything exactly as written, right to left, with correctly connected letters."
./gen.sh "$PWD/lettering_x_a.png" "$PWD/lettering.png" "$PR" &
./gen.sh "$PWD/lettering_x_b.png" "$PWD/lettering.png" "$PR" &
wait
```

Run it in the background and keep working on the layout in the meantime. Up to three
phrases fit on one sheet (line 1 plus two words).

**Writing the letter-by-letter spec** is what makes the model get it right. Name each letter, say
where its dots go, and spell out the traps:
- dots: «ض has one dot above», «ي has two dots below», «ق has two dots above», «ش has three dots above»
- taa marbuta: «ends with ة (a small closed loop with two dots above), NOT the open ت»
- non-joining letters: «ر never joins the next letter, so the ة after it stands alone»
- hamza: «أ is an alef with the hamza ABOVE it», «وراء ends with a standalone ء on the line»
- question mark: «followed by the Arabic question mark ؟»
- shadda, when needed: «حزّر has a shadda on the ز»

## 3. Verify, letter by letter

Look at the whole sheet, then crop each line at full resolution (1.5–2× if dots are small):

```python
from PIL import Image
im = Image.open("lettering_x_a.png")
im.crop((30, 650, 1010, 960)).save("zoom.png")   # then Read zoom.png
```

For each word check: letter order and count, every dot (count and above/below), joins, ة versus ت,
hamza, shadda, ؟ (the mirrored Arabic form), and that no extra word has appeared. Compare the two
attempts. Keep one that is fully correct. If neither is, regenerate with a stricter spec. Never fix
letters by hand.

Failures actually seen:

| asked for | got | problem |
|---|---|---|
| أول رحلة | أول رحلت | ة became ت |
| أول رحلة | ر joined to ح | a non-joining letter was joined |
| a name starting with محمد | حمد … | first letter missing |
| احزر مين؟ | احزر وين؟ | different word |
| عرفتوه؟ | حرفتوه؟ | wrong first letter |

## 4. Add it to the library

```bash
python add_word.py lettering_x_a.png 2 my_slug "<the arabic word>"
```

It keys out the white, scales the word to library size, saves `words/my_slug.png` and updates
`words/INDEX.md`. Then use it with `ms.use_word(key, "my_slug")`. The word is added to the project's
copy of the kit. To reuse it in later projects, keep that `words/` folder and copy it into the next
project (an installed skill's own folder may be read-only or replaced on update).

## When not to use brush lettering

Small or long text, numbers, dates, prices and anything exact belong in typed fonts (Tajawal
ExtraBold or Black through `chrome_layer`). Typed text is always correct. Brush lettering is only for
the one big headline.
