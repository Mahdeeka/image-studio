"""Add a VERIFIED brush word to the word library (kit/words/).

Usage:  python add_word.py <sheet.png> <line> <slug> "<arabic text>"

  sheet  an AI lettering sheet made with gen.sh whose line 1 is «مهدي كبها» (the size reference)
  line   which line of the sheet holds the word (usually 2 or 3)
  slug   ascii file name, e.g. dayf_mumayyaz

Writes words/<slug>.png (white keyed out, scaled so every word in the library shares the
same letter size) and adds a row to words/INDEX.md. Only add words you have read letter by
letter at full zoom: a word in the library is trusted and reused without re-checking.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
WORDS = os.path.join(HERE, "words")
LSCALE = 725 / 929          # library size = what series_lib.headline() draws at extra=1.0


def ink_bands(sheet, gap=25):
    a = np.asarray(Image.open(sheet).convert("RGB"), np.float32) @ np.array([0.299, 0.587, 0.114], np.float32)
    ink = a < 200
    rows = np.where(ink.sum(1) > 3)[0]
    bands, s0, p = [], rows[0], rows[0]
    for r in rows[1:]:
        if r > p + gap: bands.append((s0, p)); s0 = r
        p = r
    bands.append((s0, p))
    out = []
    for b0, b1 in bands:
        cols = np.where(ink[b0:b1 + 1].sum(0) > 0)[0]
        out.append((int(b0), int(b1), int(cols.max() - cols.min())))
    return [b for b in out if b[1] - b[0] > 60]


def key_out(sheet, y0, y1):
    src = Image.open(sheet).convert("RGB")
    a = np.asarray(src.crop((0, y0 - 6, src.width, y1 + 6)), np.float32)
    lum = a @ np.array([0.299, 0.587, 0.114], np.float32)
    alpha = np.clip((250 - lum) / (250 - 45), 0, 1)
    rgb = np.clip((a - (1 - alpha[..., None]) * 255) / np.maximum(alpha[..., None], 1e-3), 0, 255)
    rgb = np.where(alpha[..., None] > 0.02, rgb, 0)
    im = Image.fromarray(np.dstack([rgb, alpha * 255]).astype(np.uint8), "RGBA")
    return im.crop(im.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox())


def add_word(sheet, line, slug, text):
    bands = ink_bands(sheet)
    k = LSCALE * 929 / bands[0][2]                  # line 1 «مهدي كبها» is the size reference
    y0, y1, _ = bands[line - 1]
    im = key_out(sheet, y0, y1)
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    os.makedirs(WORDS, exist_ok=True)
    im.save(os.path.join(WORDS, f"{slug}.png"))
    index = os.path.join(WORDS, "INDEX.md")
    rows = []
    if os.path.exists(index):
        rows = [r for r in open(index, encoding="utf-8").read().splitlines() if r.startswith("| ") and not r.startswith("| slug") and f"| {slug} |" not in r]
    rows.append(f"| {slug} | {text} | {os.path.basename(sheet)} line {line} | {im.width}x{im.height} |")
    with open(index, "w", encoding="utf-8") as f:
        f.write("# Verified brush words\n\nEvery word here was read letter by letter before it was added. "
                "Use with `series_lib.use_word(key, slug)`, then `series_lib.headline(key, ...)`.\n\n"
                "| slug | word | source | size |\n|---|---|---|---|\n" + "\n".join(rows) + "\n")
    return im.size


if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    print(add_word(sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]))
