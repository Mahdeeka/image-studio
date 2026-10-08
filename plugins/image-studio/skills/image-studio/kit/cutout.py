"""Cut a person's outline out of a real photo (OpenCV GrabCut) - e.g. for a gold "guess who" silhouette.

The photo itself is never changed; you get a black/white mask of the person.

    from cutout import person_mask
    m = person_mask("inputs/guest.jpg",
                    rect=(60, 480, 1080, 1580),                    # box that surely contains the whole person
                    fg=[(500, 540, 720, 660), (500, 700, 700, 880)],  # boxes surely ON the person (face, torso...)
                    bg=[(0, 0, 1124, 470)],                        # boxes surely background (above head, table...)
                    bg_polys=[[(0, 960), (240, 960), (60, 1580), (0, 1580)]],
                    out="person_mask.png")                         # also writes person_mask_preview.png

Find the coordinates with grid.py first. Mark narrow gaps (between an arm and the body, chair studs)
as background, otherwise they get filled in. Check the preview (red = cut away), adjust hints, re-run.
Cut the mask just above tables/desks: the frame usually hides the bottom anyway.
"""
import cv2
import numpy as np


def person_mask(photo, rect, fg, bg=(), bg_polys=(), scale=0.5, iters=10, smooth=2.2, out=None):
    img = cv2.imread(photo)
    small = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    h, w = small.shape[:2]
    S = lambda v: int(round(v * scale))
    m = np.full((h, w), cv2.GC_PR_BGD, np.uint8)
    cv2.rectangle(m, (S(rect[0]), S(rect[1])), (S(rect[2]), S(rect[3])), cv2.GC_PR_FGD, -1)
    for x0, y0, x1, y1 in bg:
        m[S(y0):S(y1), S(x0):S(x1)] = cv2.GC_BGD
    for poly in bg_polys:
        cv2.fillPoly(m, [np.array([[S(x), S(y)] for x, y in poly], np.int32)], cv2.GC_BGD)
    for x0, y0, x1, y1 in fg:
        m[S(y0):S(y1), S(x0):S(x1)] = cv2.GC_FGD
    bgd, fgd = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    cv2.grabCut(small, m, None, bgd, fgd, iters, cv2.GC_INIT_WITH_MASK)
    fgm = np.where((m == cv2.GC_FGD) | (m == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(fgm, 8)            # keep the person (largest blob)
    fgm = np.where(lab == 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA]), 255, 0).astype(np.uint8)
    inv = cv2.bitwise_not(fgm)                                                # fill enclosed holes
    n2, lab2, st2, _ = cv2.connectedComponentsWithStats(inv, 4)
    for i in range(1, n2):
        x, y, ww, hh, _a = st2[i]
        if x > 0 and y > 0 and x + ww < w and y + hh < h: fgm[lab2 == i] = 255
    full = cv2.resize(fgm, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_LINEAR)
    full = np.where(cv2.GaussianBlur(full, (0, 0), smooth) > 127, 255, 0).astype(np.uint8)
    if out:
        cv2.imwrite(out, full)
        prev = img.copy(); outside = full < 128
        prev[outside] = (prev[outside] * 0.35 + np.array([40, 40, 200]) * 0.65).astype(np.uint8)
        cv2.imwrite(out.replace(".png", "_preview.png"), cv2.resize(prev, None, fx=0.5, fy=0.5))
    return full


def clean_silhouette(mask, solid_from_y=None, open_px=15, blur=4.0):
    """Smooth the outline for a gold figure: drop thin bits (glasses arms, straps) and optionally
    make every row below `solid_from_y` solid, so the arms/torso read as one clean bust."""
    m = cv2.morphologyEx(mask, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (open_px, open_px)))
    if solid_from_y is not None:
        for y in range(solid_from_y, m.shape[0]):
            xs = np.nonzero(m[y])[0]
            if len(xs): m[y, xs.min():xs.max() + 1] = 255
    return np.where(cv2.GaussianBlur(m, (0, 0), blur) > 127, 255, 0).astype(np.uint8)
