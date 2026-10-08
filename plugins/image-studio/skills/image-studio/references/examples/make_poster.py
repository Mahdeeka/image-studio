"""OFF THE MAP 'guess who' guest poster (1080x1920). Reference script: read and adapt it.

It needs inputs that are not shipped (the guest's photo and its GrabCut mask, an AI scene
"alpine.png", a lettering sheet "lettering_g.png"). Names and clues are placeholders.

Same look as the scratch-card story series: the guest is a gold-foil silhouette that
nobody has scratched yet. All normal text is typed and rendered through Chrome; the AI
parts are the Alps scene, the silhouette shape and the two brush words.
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageChops

import series_lib as ms
import logo

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = ms.W, ms.H

# ---------------------------------------------------------------- content
HOOK_SUB = "الضيف المميز اللي رح يكون معنا"
TALK_KICKER = "مداخلة بعنوان"
CLUES = [  # (centre, rotation, number, icon, text)
    ((340, 375), -2.0, 1, "arch", "التلميح الأول: مهنته"),
    ((300, 525), 1.5, 2, "mountain", "التلميح الثاني: شغفه"),
    ((342, 675), -1.2, 3, "drone", "التلميح الثالث: إنجاز مميز"),
]
FOOTER = "OFF THE MAP · THU 15.10 · 18:00 · YOUR VENUE"

# ---------------------------------------------------------------- layout
ALP_SCALE, ALP_X0, ALP_Y0 = 0.90, -150, 205       # Alps scene placement on the canvas
PERSON_MASK = "person_mask_gc.png"                # the guest's real outline, cut from inputs/guest.jpg (GrabCut)
FIG_SCALE, FIG_X0, FIG_Y0 = 0.62, 542, 458        # outline bbox -> canvas (bottom is hidden by the torn frame)
FACE_IN_PHOTO = (614, 768)                         # face centre in the original photo: the ؟ goes there
Q_FONT = 205
HOOK_BAND, HOOK_EXTRA = (1124, 1292), 0.82
SUB_TOP = 1310
TALK_BAND, TALK_EXTRA = (1420, 1540), 0.60
RULE_TOP, FOOT_TOP = 1578, 1594
COIN = (482, 1012)

ICONS = {
    "arch": '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="#1E3A2B" stroke-width="2.1" stroke-linejoin="round" stroke-linecap="round"><path d="M3 21h18M5 21V8l7-5 7 5v13M9 21v-6h6v6M9 11h1M14 11h1"/></svg>',
    "mountain": '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="#1E3A2B" stroke-width="2.1" stroke-linejoin="round" stroke-linecap="round"><path d="M2 20L9 7l4 6 3-4 6 11zM7.3 10.4l1.7 1.4 1.6-1.6"/></svg>',
    "drone": '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="#1E3A2B" stroke-width="2" stroke-linecap="round"><circle cx="5" cy="5" r="2.6"/><circle cx="19" cy="5" r="2.6"/><circle cx="5" cy="19" r="2.6"/><circle cx="19" cy="19" r="2.6"/><path d="M7 7l3 3M17 7l-3 3M7 17l3-3M17 17l-3-3"/><rect x="9.5" y="9.5" width="5" height="5" rx="1"/></svg>',
}


# ---------------------------------------------------------------- pieces
def key_white(path, lo=40, hi=235):
    """Black-on-white artwork -> alpha mask (soft edge), cropped to its ink."""
    a = np.asarray(Image.open(path).convert("RGB"), np.float32) @ np.array([0.299, 0.587, 0.114], np.float32)
    alpha = np.clip((hi - a) / (hi - lo), 0, 1)
    m = Image.fromarray((alpha * 255).astype(np.uint8))
    return m.crop(m.point(lambda v: 255 if v > 40 else 0).getbbox())


def move_paraglider(alp, src=(1286, 90, 1398, 204), shift=(-137, 26)):
    """Move the (AI) paraglider into the guest's line of sight; it was cut by the frame corner.
    Transfers only its difference from the sky, so the thin lines survive and the new sky matches."""
    a = np.asarray(alp, np.float32).copy()
    x0, y0, x1, y1 = src
    left = a[y0:y1, x0 - 40:x0 - 8].mean(1); right = a[y0:y1, x1 + 8:x1 + 40].mean(1)
    t = np.linspace(0, 1, x1 - x0)[None, :, None]
    sky = left[:, None, :] * (1 - t) + right[:, None, :] * t
    delta = a[y0:y1, x0:x1] - sky
    a[y0:y1, x0:x1] = sky + np.random.default_rng(7).normal(0, 1.4, sky.shape)
    dx, dy = shift
    a[y0 + dy:y1 + dy, x0 + dx:x1 + dx] += delta
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def build_base():
    base = ms.build_plate()
    logo.place(base, (540, 120), 170, "line")
    photo_mask = ms.rough(ms.mask_from_poly(ms.blob_polygon(3)), 11, 1.6, 0.25)
    border = ms.rough(ms.dilate(photo_mask, 9), 12, 1.6, 0.4)
    sh = Image.new("RGBA", (W, H), (60, 45, 25, 0)); sh.putalpha(border.filter(ImageFilter.GaussianBlur(12)).point(lambda v: v * 0.33))
    base.alpha_composite(sh, (0, 7))
    base.paste(Image.new("RGBA", (W, H), (251, 248, 240, 255)), (0, 0), border)
    alp = move_paraglider(Image.open("alpine.png").convert("RGB"))
    alp = alp.resize((round(alp.width * ALP_SCALE), round(alp.height * ALP_SCALE)), Image.LANCZOS)
    alp = ImageEnhance.Color(alp).enhance(0.92)
    alp = Image.blend(alp, Image.new("RGB", alp.size, (236, 222, 196)), 0.05)
    full = Image.new("RGBA", (W, H), (0, 0, 0, 0)); full.paste(alp, (ALP_X0, ALP_Y0))
    base.paste(full, (0, 0), photo_mask)
    ms.flakes(base, ms.edge_points(border, outer_px=6), 105, 21, big=0.035)
    return base, photo_mask


def silhouette_mask():
    """Full-canvas L mask of the gold guest figure."""
    sil = key_white("silhouette.png", 30, 200)
    k = SIL_H / sil.height
    sil = sil.resize((round(sil.width * k), SIL_H), Image.LANCZOS)
    m = Image.new("L", (W, H), 0)
    x0, y0 = round(SIL_CX - sil.width / 2), SIL_BOTTOM - SIL_H
    m.paste(sil, (x0, y0))
    return m, (x0, y0, x0 + sil.width, y0 + SIL_H)


def person_figure(photo_mask):
    """The guest's real outline as a canvas mask: smoothed, thin bits (sunglasses arm) removed, clipped to the frame."""
    import cv2
    m = cv2.imread(PERSON_MASK, cv2.IMREAD_GRAYSCALE)
    for y in range(1250, m.shape[0]):                # solid base: no gaps between arm and body
        xs = np.nonzero(m[y])[0]
        if len(xs): m[y, xs.min():xs.max() + 1] = 255
    m[1580:, :] = 0                                  # keep the cut above the table (frame hides it anyway)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    m = cv2.GaussianBlur(m, (0, 0), 4.0)
    m = np.where(m > 127, 255, 0).astype(np.uint8)
    ys, xs = np.nonzero(m)
    bx0, by0 = int(xs.min()), int(ys.min())
    crop = Image.fromarray(m[by0:int(ys.max()) + 1, bx0:int(xs.max()) + 1])
    crop = crop.resize((round(crop.width * FIG_SCALE), round(crop.height * FIG_SCALE)), Image.LANCZOS)
    full = Image.new("L", (W, H), 0); full.paste(crop, (FIG_X0, FIG_Y0))
    full = ImageChops.multiply(full, photo_mask)
    qx = FIG_X0 + (FACE_IN_PHOTO[0] - bx0) * FIG_SCALE
    qy = FIG_Y0 + (FACE_IN_PHOTO[1] - by0) * FIG_SCALE
    return full, (qx, qy)


def gold_figure(img, mask, q_at):
    # cast shadow onto the scene, then the foil figure (bevel + light catch like the scratch foil)
    sh = Image.new("RGBA", (W, H), (35, 25, 10, 0)); sh.putalpha(mask.filter(ImageFilter.GaussianBlur(14)).point(lambda v: v * 0.5))
    img.alpha_composite(sh, (12, 14))
    ms.apply_foil(img, mask, Image.new("L", (W, H), 0), 31, 0)
    # embossed Arabic question mark on the chest
    qx, qy = q_at
    q = ms.chrome_layer("q", f'<div style="position:absolute;left:{qx - 150}px;top:{qy - 150}px;width:300px;height:300px;'
                             f'font:{Q_FONT}px/300px TajB;text-align:center;color:#5E4518">؟</div>')
    qa = ImageChops.multiply(q.getchannel("A"), mask.filter(ImageFilter.MinFilter(9)))
    hi = Image.new("RGBA", (W, H), (250, 232, 178, 0)); hi.putalpha(qa.point(lambda v: v * 0.55))
    dk = Image.new("RGBA", (W, H), (94, 69, 24, 0)); dk.putalpha(qa.point(lambda v: v * 0.85))
    img.alpha_composite(hi, (2, 3))
    img.alpha_composite(dk)


def clue_tags():
    h = ""
    for (cx, cy), rot, n, ic, t in CLUES:
        h += (f'<div class="tag" style="left:{cx}px;top:{cy}px;font-size:33px;transform:translate(-50%,-50%) rotate({rot}deg)">'
              f'<span class="num">{n}</span>{ICONS[ic]}<span>{t}</span></div>')
    return ms.chrome_layer("p_clues", h)


def text_layer():
    h = (f'<div class="c sub" style="top:{SUB_TOP}px;font-size:50px">{HOOK_SUB}</div>'
         f'<div class="c prof" style="top:{TALK_BAND[0] - 44}px;font-size:32px"><span class="rl"></span>{TALK_KICKER}<span class="rl"></span></div>'
         f'<div class="rule" style="top:{RULE_TOP}px"></div>'
         f'<div class="c foot" style="top:{FOOT_TOP}px">{FOOTER}</div>')
    return ms.chrome_layer("p_text", h)


def load_lettering(sheet="lettering_g.png"):
    b = [x for x in ms.ink_bands(sheet) if x[1] - x[0] > 60]
    ms.SHEET_SCALE[sheet] = 929 / b[0][2]
    ms.BANDS["hook"] = (sheet, b[1][0], b[1][1])
    ms.BANDS["talk"] = (sheet, b[2][0], b[2][1])
    return b


def main():
    os.chdir(HERE)
    print("bands", load_lettering())
    img, photo_mask = build_base()
    mask, q_at = person_figure(photo_mask)
    gold_figure(img, mask, q_at)
    box = mask.getbbox()
    img.alpha_composite(clue_tags())
    ms.coin(img, *COIN, 40, -18)
    hook, hb = ms.headline("hook", HOOK_BAND, extra=HOOK_EXTRA)
    talk, tb = ms.headline("talk", TALK_BAND, extra=TALK_EXTRA, star_on=False, swoosh_k=0.62)
    img.alpha_composite(hook)
    img.alpha_composite(talk)
    img.alpha_composite(text_layer())
    print("silhouette", box, "hook", hb, "talk", tb)
    os.makedirs("out", exist_ok=True)
    img.convert("RGB").save("out/poster.png")


if __name__ == "__main__":
    main()
