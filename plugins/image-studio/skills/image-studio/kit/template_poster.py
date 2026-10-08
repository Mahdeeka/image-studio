"""Starter template: one designed image (poster / story / WhatsApp post) with the image-studio kit.

Copy the kit into a project folder, copy this file to make_<name>.py, edit the CONFIG block, run it.
Layers, bottom to top: paper plate -> logo (if inputs/logo.png or .jpg exists) -> torn frame with the REAL photo (only cropped, scaled,
lightly graded) -> optional gold scratch foil -> seal + coin -> brush headline (verified library
word) -> typed text (Chrome, correct Arabic) -> footer.   Output: out/<OUT_NAME>.png
"""
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageChops

import logo
import series_lib as ms

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = ms.W, ms.H                   # work on the 1080x1920 canvas, crop to OUT_H at the end

# ================================ CONFIG ================================
FORMAT = "feed"                     # "feed" 1080x1350 (WhatsApp / Instagram post)  |  "story" 1080x1920
OUT_NAME = "image"
PHOTO = "inputs/photo.jpg"          # real photo: never regenerated
FOCUS = (0.5, 0.45)                 # point of the photo (fractions) kept in the middle of the frame
WORD, WORD_EXTRA = "dayf_mumayyaz", 0.80   # brush headline from words/INDEX.md, and its size
KICKER = "رح يستنانا"                # small line above the headline (None = skip)
SUB = "بكرا رح نعلن عنه"              # line under the headline (None = skip)
CTA = "الحق حالك قبل الكشف"          # green pill (None = skip)
SEAL = ("ضايل", "10", "أماكن بس")    # round seal: top / big / bottom (None = skip)
SEAL_RIM = "LAST SEATS • OFF THE MAP • THU 15.10 • "
FOOTER = "OFF THE MAP · THU 15.10 · 18:00 · YOUR VENUE"
SCRATCH = False                     # cover the photo with gold foil and scratch one peek window
PEEK = (560, 420, 860, 560)         # canvas box of that peek window
# ========================================================================

OUT_H, FRAME_BOT = {"feed": (1350, 780), "story": (1920, 1100)}[FORMAT]   # story: bottom 15% stays free for stickers


def frame_polygon(seed=3, y_bot=FRAME_BOT):
    """Torn-paper photo frame: series top edge (leaves room for the logo), bottom edge at y_bot."""
    rnd = random.Random(seed)
    xs = np.arange(-30, 1111, 5)
    yt = np.interp(xs, [-30, 60, 200, 420, 620, 760, 880, 1000, 1110], [262, 250, 240, 236, 242, 258, 290, 302, 306])
    yt = yt + ms.smooth_noise(len(xs), 14, 9, rnd) + ms.torn_walk(len(xs), 3.2, rnd)
    yb = np.interp(xs, [-30, 150, 420, 560, 750, 900, 1110], [y_bot + 28, y_bot + 36, y_bot + 26, y_bot + 2, y_bot - 12, y_bot - 22, y_bot - 34])
    yb = yb + ms.smooth_noise(len(xs), 14, 10, rnd) + ms.torn_walk(len(xs), 3.2, rnd)
    ys_r = np.arange(int(yt[-1]), int(yb[-1]), 5)
    xr = 1090 + ms.smooth_noise(len(ys_r), 12, 8, rnd) + ms.torn_walk(len(ys_r), 3, rnd)
    ys_l = np.arange(int(yb[0]), int(yt[0]), -5)
    xl = -12 + ms.smooth_noise(len(ys_l), 12, 8, rnd) + ms.torn_walk(len(ys_l), 3, rnd)
    pts = list(zip(xs, yt)) + list(zip(xr, ys_r)) + list(zip(xs[::-1], yb[::-1])) + list(zip(xl, ys_l))
    return [(float(x), float(y)) for x, y in pts]


def build_base():
    base = ms.build_plate()
    logo.place(base, (540, 112), 150, "line")
    photo_mask = ms.rough(ms.mask_from_poly(frame_polygon()), 11, 1.6, 0.25)
    border = ms.rough(ms.dilate(photo_mask, 9), 12, 1.6, 0.4)
    sh = Image.new("RGBA", (W, H), (60, 45, 25, 0)); sh.putalpha(border.filter(ImageFilter.GaussianBlur(12)).point(lambda v: v * 0.33))
    base.alpha_composite(sh, (0, 7))
    base.paste(Image.new("RGBA", (W, H), (251, 248, 240, 255)), (0, 0), border)
    # cover-fit the photo into the frame, keeping FOCUS in the middle
    x0, y0, x1, y1 = photo_mask.getbbox()
    ph = Image.open(PHOTO).convert("RGB")
    k = max((x1 - x0) / ph.width, (y1 - y0) / ph.height)
    ph = ph.resize((math.ceil(ph.width * k), math.ceil(ph.height * k)), Image.LANCZOS)
    px = int(min(x0, max(x1 - ph.width, (x0 + x1) / 2 - FOCUS[0] * ph.width)))
    py = int(min(y0, max(y1 - ph.height, (y0 + y1) / 2 - FOCUS[1] * ph.height)))
    ph = ImageEnhance.Color(ph).enhance(0.94)                                  # very slight grade only
    ph = Image.blend(ph, Image.new("RGB", ph.size, (236, 222, 196)), 0.05)
    full = Image.new("RGBA", (W, H), (0, 0, 0, 0)); full.paste(ph, (px, py))
    base.paste(full, (0, 0), photo_mask)
    ms.flakes(base, ms.edge_points(border, outer_px=6), 95, 21, big=0.035)
    return base, photo_mask


def seal_layer(cx, cy, R=160, rot=-8):
    top, big, bottom = SEAL
    r = R - 22
    svg = (f'<svg width="{2 * R + 40}" height="{2 * R + 40}" viewBox="{-R - 20} {-R - 20} {2 * R + 40} {2 * R + 40}" '
           f'style="position:absolute;left:{cx - R - 20}px;top:{cy - R - 20}px;transform:rotate({rot}deg);'
           f'filter:drop-shadow(0 9px 12px rgba(40,28,10,.5))">'
           f'<defs><path id="rim" d="M {-r},0 a {r},{r} 0 1,1 {2 * r},0 a {r},{r} 0 1,1 {-2 * r},0"/></defs>'
           f'<circle r="{R}" fill="#1E3A2B"/><circle r="{R - 6}" fill="none" stroke="#C9A35E" stroke-width="3"/>'
           f'<circle r="{R - 38}" fill="none" stroke="#C9A35E" stroke-width="1.6"/>'
           f'<text font-family="Mont" font-weight="700" font-size="17" fill="#E8D19C">'
           f'<textPath href="#rim" textLength="{2 * math.pi * r * 0.985:.1f}" lengthAdjust="spacing">{SEAL_RIM}</textPath></text>'
           f'<text y="-58" text-anchor="middle" direction="rtl" font-family="Taj" font-size="34" fill="#F4ECDB">{top}</text>'
           f'<text y="46" text-anchor="middle" font-family="Mont" font-weight="800" font-size="124" fill="#E2C27E">{big}</text>'
           f'<text y="90" text-anchor="middle" direction="rtl" font-family="Taj" font-size="32" fill="#F4ECDB">{bottom}</text></svg>')
    return ms.chrome_layer("t_seal", svg)


def text_layer():
    b = FRAME_BOT
    h = ""
    if KICKER: h += f'<div class="c prof" style="top:{b + 66}px;font-size:36px"><span class="rl"></span>{KICKER}<span class="rl"></span></div>'
    if SUB: h += f'<div class="c sub" style="top:{b + 318}px;font-size:46px">{SUB}</div>'
    if CTA: h += (f'<div style="position:absolute;left:540px;top:{b + 390}px;transform:translateX(-50%);background:#1E3A2B;'
                  f'color:#F4ECDB;font:34px/1 Taj;padding:16px 40px 14px;border-radius:999px;direction:rtl;white-space:nowrap;'
                  f'box-shadow:0 6px 14px rgba(40,28,10,.32)">{CTA}</div>')
    if FOOTER: h += (f'<div class="rule" style="top:{b + 482}px"></div>'
                     f'<div class="c foot" style="top:{b + 498}px;font-size:25px;letter-spacing:3px">{FOOTER}</div>')
    return ms.chrome_layer("t_text", h)


def main():
    os.chdir(HERE)
    img, photo_mask = build_base()
    if SCRATCH:
        peek = Image.new("L", (W, H), 0)
        ms.zigzag(ImageDraw.Draw(peek), PEEK, 99, (30, 42), slant=0.06, ragged=40)
        peek = ImageChops.multiply(ms.rough(peek, 199, 2.0, 0.3), photo_mask)
        ms.STREAKS.clear()
        ms.apply_foil(img, photo_mask, peek, 10, 45)
        ms.coin(img, PEEK[2] + 55, (PEEK[1] + PEEK[3]) // 2, 40, -12)
    else:
        ms.coin(img, 478, FRAME_BOT - 38, 38, -18)
    if SEAL:
        img.alpha_composite(seal_layer(250, FRAME_BOT - 195))
    ms.use_word("head", WORD)
    head, hb = ms.headline("head", (FRAME_BOT + 116, FRAME_BOT + 306), extra=WORD_EXTRA, star_on=False)
    img.alpha_composite(head)
    img.alpha_composite(text_layer())
    os.makedirs("out", exist_ok=True)
    out = os.path.join("out", f"{OUT_NAME}.png")
    img.convert("RGB").crop((0, 0, W, OUT_H)).save(out)
    print(out, "headline box", hb)


if __name__ == "__main__":
    main()
