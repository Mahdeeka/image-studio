"""OFF THE MAP: 4 reveal stories for the special guest (1080x1920). Reference script: read and adapt it.

It needs inputs that are not shipped (the guest's photo, lettering sheets with the guest's name).
Names, roles and clues are placeholders.

The guest's real photo sits under the series' gold scratch foil and is revealed step by step:
  1 «احزر مين؟»  sealed card + 3 clues + a peek at the hat
  2 «عرفتوه؟»    hat, jacket and hand revealed, face still under foil
  3 face revealed, name still under foil
  4 full reveal: the guest's name as a brush word
The photo is only cropped and lightly graded. All normal text is typed (Chrome); the brush
words come from verified AI lettering sheets.
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageChops, ImageEnhance, ImageFilter

import logo
import make_poster as mp
import series_lib as ms

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = ms.W, ms.H

# ---------------------------------------------------------------- content
PHOTO = "inputs/guest.jpg"
SUB_GUESS = "الضيف المميز اللي رح يكون معنا"
SUB_KNEW = "كشطنا شوي… والوجه لسا تحت الكرت"
ROLES = "المهنة · الصفة أو المشروع"
TALK_KICKER = "مداخلة بعنوان"
FOOTER = "OFF THE MAP · THU 15.10 · 18:00 · YOUR VENUE"
CLUES = [  # (centre, rotation, number, icon, text): use true, verified facts
    ((330, 335), -2.0, 1, "arch", "التلميح الأول: مهنته"),
    ((318, 628), 1.5, 2, "mountain", "التلميح الثاني: شغفه"),
    ((362, 888), -1.2, 3, "drone", "التلميح الثالث: إنجاز مميز"),
]

# ---------------------------------------------------------------- layout
PS, PX0, PY0 = 1.04, -60, -160                    # photo 1124x2000 -> canvas
def p2c(x, y): return x * PS + PX0, y * PS + PY0
FACE = (564, 684)                                 # face centre
FACE_R = (152, 142)
PEEP = (455, 425, 700, 515)                       # first peek: a detail (the hat)
SEAL = (928, 404, 80, -10)                        # cx, cy, radius, rotation
HEAD_BAND = (1118, 1300)
SUB_TOP = 1316
KICK_TOP = 1378
TALK_BAND, TALK_EXTRA = (1420, 1540), 0.60
RULE_TOP, FOOT_TOP = 1578, 1594
TEXT_ZONE = (90, 1366, 990, 1622)                 # keep foil crumbs off visible text


# ---------------------------------------------------------------- pieces
def build_base():
    base = ms.build_plate()
    logo.place(base, (540, 120), 170, "line")
    photo_mask = ms.rough(ms.mask_from_poly(ms.blob_polygon(3)), 11, 1.6, 0.25)
    border = ms.rough(ms.dilate(photo_mask, 9), 12, 1.6, 0.4)
    sh = Image.new("RGBA", (W, H), (60, 45, 25, 0)); sh.putalpha(border.filter(ImageFilter.GaussianBlur(12)).point(lambda v: v * 0.33))
    base.alpha_composite(sh, (0, 7))
    base.paste(Image.new("RGBA", (W, H), (251, 248, 240, 255)), (0, 0), border)
    photo = Image.open(PHOTO).convert("RGB")
    photo = photo.resize((round(photo.width * PS), round(photo.height * PS)), Image.LANCZOS)
    photo = ImageEnhance.Color(photo).enhance(0.97)
    photo = Image.blend(photo, Image.new("RGB", photo.size, (236, 222, 196)), 0.04)
    full = Image.new("RGBA", (W, H), (0, 0, 0, 0)); full.paste(photo, (PX0, PY0))
    base.paste(full, (0, 0), photo_mask)
    ms.flakes(base, ms.edge_points(border, outer_px=6), 105, 21, big=0.035)
    return base, photo_mask


def seal_layer():
    cx, cy, R, rot = SEAL
    r = R - 19
    circ = 2 * math.pi * r
    svg = (f'<svg width="{2 * R + 40}" height="{2 * R + 40}" viewBox="{-R - 20} {-R - 20} {2 * R + 40} {2 * R + 40}" '
           f'style="position:absolute;left:{cx - R - 20}px;top:{cy - R - 20}px;transform:rotate({rot}deg);'
           f'filter:drop-shadow(0 7px 9px rgba(40,28,10,.45))">'
           f'<defs><path id="rim" d="M {-r},0 a {r},{r} 0 1,1 {2 * r},0 a {r},{r} 0 1,1 {-2 * r},0"/></defs>'
           f'<circle r="{R}" fill="#1E3A2B"/>'
           f'<circle r="{R - 5}" fill="none" stroke="#C9A35E" stroke-width="2.5"/>'
           f'<circle r="{R - 31}" fill="none" stroke="#C9A35E" stroke-width="1.5"/>'
           f'<text font-family="Mont" font-weight="700" font-size="14.5" fill="#E8D19C">'
           f'<textPath href="#rim" textLength="{circ * 0.985:.1f}" lengthAdjust="spacing">SPECIAL GUEST • OFF THE MAP • </textPath></text>'
           f'<text y="-3" text-anchor="middle" font-family="Taj" font-size="27" fill="#F4ECDB">ضيف</text>'
           f'<text y="25" text-anchor="middle" font-family="Taj" font-size="27" fill="#F4ECDB">مميز</text>'
           f'</svg>')
    return ms.chrome_layer("g_seal", svg)


def clue_tags():
    h = ""
    for (cx, cy), rot, n, ic, t in CLUES:
        h += (f'<div class="tag" style="left:{cx}px;top:{cy}px;font-size:33px;transform:translate(-50%,-50%) rotate({rot}deg)">'
              f'<span class="num">{n}</span>{mp.ICONS[ic]}<span>{t}</span></div>')
    return ms.chrome_layer("g_clues", h)


def text_layer(name, sub=None, roles=None):
    h = ""
    if sub: h += f'<div class="c sub" style="top:{SUB_TOP}px;font-size:48px">{sub}</div>'
    if roles: h += f'<div class="c" style="top:{SUB_TOP + 4}px;font:36px/1 TajBold;direction:rtl">{roles}</div>'
    h += (f'<div class="c prof" style="top:{KICK_TOP}px;font-size:32px"><span class="rl"></span>{TALK_KICKER}<span class="rl"></span></div>'
          f'<div class="rule" style="top:{RULE_TOP}px"></div>'
          f'<div class="c foot" style="top:{FOOT_TOP}px">{FOOTER}</div>')
    return ms.chrome_layer(name, h)


def load_sheet(sheet):
    b = [x for x in ms.ink_bands(sheet) if x[1] - x[0] > 60]
    ms.SHEET_SCALE[sheet] = 929 / b[0][2]          # line 1 is always «مهدي كبها»: same letter size everywhere
    return b


def load_lettering():
    mp.load_lettering()                            # «احزر مين؟» (hook), «ما وراء الجرأة» (talk)
    bn = load_sheet("lettering_n_b.png")           # line 2: the guest's name (verified letter by letter)
    bk = load_sheet("lettering_n_a.png")           # line 3: «عرفتوه؟» (verified; the other sheet had «حرفتوه»)
    ms.BANDS["gname"] = ("lettering_n_b.png", bn[1][0], bn[1][1])
    ms.BANDS["knew"] = ("lettering_n_a.png", bk[2][0], bk[2][1])


def alpha_bbox(layer, y0, y1):
    a = np.asarray(layer.getchannel("A"))[y0:y1]
    cols = np.where(a.max(0) > 30)[0]
    return int(cols.min()), int(cols.max())


# ---------------------------------------------------------------- main
def main():
    os.chdir(HERE)
    load_lettering()
    base, photo_mask = build_base()
    seal = seal_layer()
    talk, _ = ms.headline("talk", TALK_BAND, extra=TALK_EXTRA, star_on=False, swoosh_k=0.62)
    hook, _ = ms.headline("hook", HEAD_BAND, extra=0.82)
    knew, _ = ms.headline("knew", HEAD_BAND, extra=0.84)
    name, nb = ms.headline("gname", HEAD_BAND, extra=0.86)
    t_guess = text_layer("g_t1", sub=SUB_GUESS)
    t_knew = text_layer("g_t2", sub=SUB_KNEW)
    t_name = text_layer("g_t34", roles=ROLES)
    rx0, rx1 = alpha_bbox(t_name, SUB_TOP - 6, SUB_TOP + 46)
    print("name box", nb, "roles x", rx0, rx1)

    # ---- reveal masks (every stage keeps what the stage before revealed)
    peek = Image.new("L", (W, H), 0)
    ms.zigzag(ImageDraw.Draw(peek), PEEP, 99, (26, 36), slant=0.04, ragged=30)
    peek = ImageChops.multiply(ms.rough(peek, 199, 2.0, 0.3), photo_mask)
    ms.STREAKS.clear()

    z = Image.new("L", (W, H), 0); d = ImageDraw.Draw(z)
    ms.zigzag(d, (430, 340, 760, 560), 201, (32, 44), slant=0.05, ragged=40)      # hat + sunglasses
    ms.zigzag(d, (-10, 700, 420, 1110), 202, (40, 56), slant=0.08, ragged=80)     # left shoulder
    ms.zigzag(d, (690, 640, 1090, 1110), 203, (40, 56), slant=-0.06, ragged=80)   # right shoulder
    ms.zigzag(d, (380, 820, 760, 1110), 204, (36, 50), slant=0.04, ragged=60)     # hand + chest
    z = ms.rough(z, 205, 2.5, 0.35)
    face = ms.rough(ms.mask_from_poly(ms.blob(FACE[0], FACE[1], FACE_R[0], FACE_R[1], 7)), 207, 2.0, 0.3)
    s2 = ImageChops.subtract(ImageChops.lighter(peek, z), face)
    ms.apply_streaks(s2)
    ms.leftovers(s2, 302, 120)
    s2 = ImageChops.multiply(ImageChops.subtract(s2, face), photo_mask)
    ms.STREAKS.clear()

    s3 = photo_mask.copy()
    ms.leftovers(s3, 303, 70, avoid=[(FACE[0] - 170, FACE[1] - 150, FACE[0] + 170, FACE[1] + 160)])
    panel = ms.rough(ms.mask_from_poly(ms.torn_polygon(min(nb[0], rx0) - 34, 1100, max(nb[2], rx1) + 34, 1362, 4, 9, 31)), 209, 2.5, 0.3)
    cover3 = ImageChops.lighter(photo_mask, panel)

    stories = []
    # 1: guess who: sealed card, clues, a peek at the hat
    img = base.copy(); img.alpha_composite(hook); img.alpha_composite(talk); img.alpha_composite(t_guess)
    ms.apply_foil(img, photo_mask, peek, 10, 40)
    img.alpha_composite(clue_tags()); img.alpha_composite(seal)
    ms.coin(img, PEEP[2] + 62, PEEP[1] + 52, 40, -12)
    stories.append(img)
    # 2: did you recognise him? hat, jacket and hand revealed, face under foil
    img = base.copy(); img.alpha_composite(knew); img.alpha_composite(talk); img.alpha_composite(t_knew)
    ms.apply_foil(img, photo_mask, s2, 20, 200, avoid=[TEXT_ZONE])
    img.alpha_composite(seal)
    ms.coin(img, FACE[0] + FACE_R[0] + 26, FACE[1] - 40, 40, -20)
    stories.append(img)
    # 3: face revealed, name still under foil
    img = base.copy(); img.alpha_composite(name); img.alpha_composite(talk); img.alpha_composite(t_name)
    ms.apply_foil(img, cover3, s3, 30, 160, avoid=[TEXT_ZONE])
    img.alpha_composite(seal)
    ms.coin(img, max(nb[2], rx1) + 30, 1150, 40, -15)
    stories.append(img)
    # 4: full reveal
    img = base.copy(); img.alpha_composite(name); img.alpha_composite(talk); img.alpha_composite(t_name)
    ms.flakes(img, ms.edge_points(photo_mask, outer_px=3), 45, 44)
    img.alpha_composite(seal)
    ms.coin(img, 1003, 1580, 36, -15)
    stories.append(img)

    os.makedirs("out", exist_ok=True)
    for i, s in enumerate(stories, 1):
        s.convert("RGB").save(f"out/guest_story_{i}.png")
    strip = Image.new("RGB", (W * 4 + 60, H), (40, 40, 40))
    for i, s in enumerate(stories): strip.paste(s.convert("RGB"), (i * (W + 20), 0))
    strip.resize((strip.width // 3, H // 3), Image.LANCZOS).save("out/guest_contact.png")


if __name__ == "__main__":
    main()
