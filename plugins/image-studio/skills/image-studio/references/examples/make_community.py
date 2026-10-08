"""OFF THE MAP: community announcement image (1080x1350, 4:5 so WhatsApp shows it uncropped).
Reference script: read and adapt it. It builds on make_poster.py and needs the same unshipped inputs.
kit/template_poster.py is the runnable, generic version of this layout.

Message: a special guest is coming, revealed tomorrow, only a few seats left. The guest stays
hidden as the gold figure cut from his real outline (same as the guess-who poster). All normal
text is typed (Chrome); «ضيف مميز» comes from a verified AI lettering sheet.
"""
import math
import os
import random

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

import logo
import make_poster as mp
import series_lib as ms

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = ms.W, ms.H                  # working canvas is the series' 1080x1920; cropped to OUT_H at the end
OUT_H = 1350

# ---------------------------------------------------------------- content
SHEET = "lettering_s.png"          # line 1 «مهدي كبها» (size reference), line 2 «ضيف مميز»
KICKER = "رح يستنانا"
SUB = "بكرا رح نعلن عنه"
CTA = "الحق حالك قبل الكشف"
SEATS = 10                         # change here if the number of free seats changes
FOOTER = "OFF THE MAP · THU 15.10 · 18:00 · YOUR VENUE"

# ---------------------------------------------------------------- layout
FRAME_BOT = 780                    # torn photo frame: poster's top edge, shorter bottom
ALP_SCALE, ALP_X0, ALP_Y0 = 0.74, -30, 190
FIGURE = dict(FIG_SCALE=0.50, FIG_X0=541, FIG_Y0=330, Q_FONT=165)
SEAL = (250, 585, 160, -8)         # cx, cy, radius, rotation
COIN = (478, 742)
KICK_TOP = 846
HEAD_BAND, HEAD_EXTRA = (896, 1086), 0.80
SUB_TOP = 1098
CTA_TOP = 1170
RULE_TOP, FOOT_TOP = 1262, 1278


def frame_polygon(seed=3, y_bot=FRAME_BOT):
    """Same torn-paper shape as the series frame, with the bottom edge raised."""
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


def remove_paraglider(alp, box=(1286, 90, 1398, 204)):
    """No room for it in the shorter sky: paint the sky back in (horizontal blend of its neighbours)."""
    a = np.asarray(alp, np.float32).copy()
    x0, y0, x1, y1 = box
    left = a[y0:y1, x0 - 40:x0 - 8].mean(1); right = a[y0:y1, x1 + 8:x1 + 40].mean(1)
    t = np.linspace(0, 1, x1 - x0)[None, :, None]
    a[y0:y1, x0:x1] = left[:, None, :] * (1 - t) + right[:, None, :] * t + np.random.default_rng(7).normal(0, 1.4, (y1 - y0, x1 - x0, 3))
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def build_base():
    base = ms.build_plate()
    logo.place(base, (540, 112), 150, "line")
    photo_mask = ms.rough(ms.mask_from_poly(frame_polygon()), 11, 1.6, 0.25)
    border = ms.rough(ms.dilate(photo_mask, 9), 12, 1.6, 0.4)
    sh = Image.new("RGBA", (W, H), (60, 45, 25, 0)); sh.putalpha(border.filter(ImageFilter.GaussianBlur(12)).point(lambda v: v * 0.33))
    base.alpha_composite(sh, (0, 7))
    base.paste(Image.new("RGBA", (W, H), (251, 248, 240, 255)), (0, 0), border)
    alp = remove_paraglider(Image.open("alpine.png").convert("RGB"))
    alp = alp.resize((round(alp.width * ALP_SCALE), round(alp.height * ALP_SCALE)), Image.LANCZOS)
    alp = ImageEnhance.Color(alp).enhance(0.92)
    alp = Image.blend(alp, Image.new("RGB", alp.size, (236, 222, 196)), 0.05)
    full = Image.new("RGBA", (W, H), (0, 0, 0, 0)); full.paste(alp, (ALP_X0, ALP_Y0))
    base.paste(full, (0, 0), photo_mask)
    ms.flakes(base, ms.edge_points(border, outer_px=6), 95, 21, big=0.035)
    return base, photo_mask


def seal_layer():
    cx, cy, R, rot = SEAL
    r = R - 22
    circ = 2 * math.pi * r
    svg = (f'<svg width="{2 * R + 40}" height="{2 * R + 40}" viewBox="{-R - 20} {-R - 20} {2 * R + 40} {2 * R + 40}" '
           f'style="position:absolute;left:{cx - R - 20}px;top:{cy - R - 20}px;transform:rotate({rot}deg);'
           f'filter:drop-shadow(0 9px 12px rgba(40,28,10,.5))">'
           f'<defs><path id="rim" d="M {-r},0 a {r},{r} 0 1,1 {2 * r},0 a {r},{r} 0 1,1 {-2 * r},0"/></defs>'
           f'<circle r="{R}" fill="#1E3A2B"/>'
           f'<circle r="{R - 6}" fill="none" stroke="#C9A35E" stroke-width="3"/>'
           f'<circle r="{R - 38}" fill="none" stroke="#C9A35E" stroke-width="1.6"/>'
           f'<text font-family="Mont" font-weight="700" font-size="17" fill="#E8D19C">'
           f'<textPath href="#rim" textLength="{circ * 0.985:.1f}" lengthAdjust="spacing">LAST SEATS • OFF THE MAP • THU 15.10 • </textPath></text>'
           f'<text y="-58" text-anchor="middle" direction="rtl" font-family="Taj" font-size="34" fill="#F4ECDB">ضايل</text>'
           f'<text y="46" text-anchor="middle" font-family="Mont" font-weight="800" font-size="124" fill="#E2C27E">{SEATS}</text>'
           f'<text y="90" text-anchor="middle" direction="rtl" font-family="Taj" font-size="32" fill="#F4ECDB">أماكن بس</text>'
           f'</svg>')
    return ms.chrome_layer("c_seal", svg)


def text_layer():
    h = (f'<div class="c prof" style="top:{KICK_TOP}px;font-size:36px"><span class="rl"></span>{KICKER}<span class="rl"></span></div>'
         f'<div class="c sub" style="top:{SUB_TOP}px;font-size:46px">{SUB}</div>'
         f'<div style="position:absolute;left:540px;top:{CTA_TOP}px;transform:translateX(-50%);background:#1E3A2B;color:#F4ECDB;'
         f'font:34px/1 Taj;padding:16px 40px 14px;border-radius:999px;direction:rtl;white-space:nowrap;'
         f'box-shadow:0 6px 14px rgba(40,28,10,.32)">{CTA}</div>'
         f'<div class="rule" style="top:{RULE_TOP}px"></div>'
         f'<div class="c foot" style="top:{FOOT_TOP}px;font-size:25px;letter-spacing:3px">{FOOTER}</div>')
    return ms.chrome_layer("c_text", h)


def main():
    os.chdir(HERE)
    b = [x for x in ms.ink_bands(SHEET) if x[1] - x[0] > 60]
    ms.SHEET_SCALE[SHEET] = 929 / b[0][2]
    ms.BANDS["special"] = (SHEET, b[1][0], b[1][1])
    for k, v in FIGURE.items():
        setattr(mp, k, v)

    img, photo_mask = build_base()
    mask, q_at = mp.person_figure(photo_mask)
    mp.gold_figure(img, mask, q_at)
    ms.coin(img, *COIN, 38, -18)
    img.alpha_composite(seal_layer())
    head, hb = ms.headline("special", HEAD_BAND, extra=HEAD_EXTRA, star_on=False)
    img.alpha_composite(head)
    img.alpha_composite(text_layer())
    print("bands", b, "figure", mask.getbbox(), "headline", hb)
    os.makedirs("out", exist_ok=True)
    img.convert("RGB").crop((0, 0, W, OUT_H)).save("out/community.png")


if __name__ == "__main__":
    main()
