"""Your logo on the design: line-art (brand colour on paper) or a solid badge.

Put the logo at inputs/logo.png or inputs/logo.jpg. If there is no logo file, place() does nothing,
so every script still runs without one.

Made for a round logo drawn in a light colour on a dark background (light ring and mark on a solid
colour). "line" keeps only the light artwork and recolours it with GREEN, for light paper; "badge"
keeps the logo as a solid disc, for photos or dark areas. For a different kind of logo (dark on
white, or one with transparency), paste it yourself with Image.alpha_composite: never redraw it.
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

CANDIDATES = ("inputs/logo.png", "inputs/logo.jpg", "inputs/logo.jpeg")
GREEN = (12, 108, 71)          # line-art colour: change it to your brand colour


def source():
    return next((p for p in CANDIDATES if os.path.exists(p)), None)


def _geom(a_cream):
    ys, xs = np.nonzero(a_cream > 0.5)
    cx, cy = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
    r = max(xs.max() - xs.min(), ys.max() - ys.min()) / 2
    return cx, cy, r


def logo(size, style="line"):
    im = Image.open(source()).convert("RGB")
    a = np.asarray(im, np.float32)
    lum = a @ np.array([0.299, 0.587, 0.114], np.float32)
    cream = np.clip((lum - 95) / (215 - 95), 0, 1)
    cx, cy, r = _geom(cream)
    pad = 14
    if style == "line":
        rgba = np.zeros((*cream.shape, 4), np.uint8)
        rgba[..., :3] = GREEN
        rgba[..., 3] = (cream * 255).astype(np.uint8)
        out = Image.fromarray(rgba, "RGBA")
        box = (int(cx - r - 2), int(cy - r - 2), int(cx + r + 3), int(cy + r + 3))
        out = out.crop(box)
    else:  # badge: solid disc with a thin rim outside the light ring
        bg = im.getpixel((2, 2))
        big = Image.new("RGB", (im.width + 2 * pad, im.height + 2 * pad), bg)
        big.paste(im, (pad, pad))
        S = 4
        m = Image.new("L", (big.width * S, big.height * S), 0)
        R = (r + 9) * S; X = (cx + pad) * S; Y = (cy + pad) * S
        ImageDraw.Draw(m).ellipse((X - R, Y - R, X + R, Y + R), fill=255)
        m = m.resize(big.size, Image.LANCZOS)
        out = big.convert("RGBA"); out.putalpha(m)
        out = out.crop(out.getchannel("A").getbbox())
    return out.resize((size, size), Image.LANCZOS)


def place(img, center, size, style="line"):
    if not source():           # no logo supplied: leave the space empty
        return False
    lg = logo(size, style)
    if style == "badge":   # soft drop shadow so the badge sits on the paper
        sh = Image.new("RGBA", lg.size, (40, 28, 10, 0))
        sh.putalpha(lg.getchannel("A").filter(ImageFilter.GaussianBlur(6)).point(lambda v: v * 0.35))
        img.alpha_composite(sh, (int(center[0] - size / 2 + 2), int(center[1] - size / 2 + 5)))
    img.alpha_composite(lg, (int(center[0] - size / 2), int(center[1] - size / 2)))
    return True
