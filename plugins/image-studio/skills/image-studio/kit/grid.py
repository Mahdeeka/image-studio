"""Draw a labelled coordinate grid on a photo, to find faces/subjects before placing layers.

Usage:  python grid.py <photo> [x0 y0 x1 y1] [--step 50] [--out grid.png]

Writes a copy of the photo (or of the crop box) with grid lines every --step px and labels every
100 px, in the photo's own pixel coordinates. Read the output image, note the face centre, the
subject's box, sky areas etc., then convert to canvas coordinates with your scale/offset.
Large photos are written at half size (labels still show original coordinates).
"""
import argparse

from PIL import Image, ImageDraw


def grid(photo, box=None, step=50, out="grid.png"):
    im = Image.open(photo).convert("RGB")
    box = box or (0, 0, im.width, im.height)
    c = im.crop(box)
    d = ImageDraw.Draw(c)
    for x in range((box[0] // step + 1) * step, box[2], step):
        major = x % 100 == 0
        d.line((x - box[0], 0, x - box[0], c.height), fill=(255, 0, 0) if major else (255, 170, 170), width=1)
        if major: d.text((x - box[0] + 3, 3), str(x), fill=(255, 255, 0))
    for y in range((box[1] // step + 1) * step, box[3], step):
        major = y % 100 == 0
        d.line((0, y - box[1], c.width, y - box[1]), fill=(255, 0, 0) if major else (255, 170, 170), width=1)
        if major: d.text((3, y - box[1] + 3), str(y), fill=(255, 255, 0))
    if max(c.size) > 1400:
        c = c.resize((c.width // 2, c.height // 2), Image.LANCZOS)
    c.save(out)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("photo")
    ap.add_argument("box", nargs="*", type=int)
    ap.add_argument("--step", type=int, default=50)
    ap.add_argument("--out", default="grid.png")
    a = ap.parse_args()
    print(grid(a.photo, tuple(a.box) if len(a.box) == 4 else None, a.step, a.out))
