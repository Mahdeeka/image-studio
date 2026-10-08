"""Image-studio core library (and the OFF THE MAP 8-story scratch-card series script).

Import it for the building blocks: build_plate, blob_polygon/rough/dilate (torn frames), chrome_layer
(typed text with correct Arabic shaping), headline + use_word (brush words), apply_foil/zigzag/
leftovers (scratch foil), coin, flakes, catmull/star. Run it directly to render the 8-story series
whose constants sit at the top of this file (needs only the project's inputs/photo.jpg; the brush words
come from kit/lettering.png and kit/words).

The series constants below (trip title, clues, coordinates) are the author's own first series and are
kept as a worked example: replace them with yours.
"""
import math, random, subprocess, os, shutil, sys, glob
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance, ImageChops

W, H = 1080, 1920
GREEN = (30, 58, 43)
GOLD = (184, 151, 90)
FONT = "fonts/Montserrat.ttf"
def find_chrome():
    """A Chromium-based browser for rendering text. Set CHROME=/path/to/browser to choose one."""
    env = os.environ.get("CHROME") or os.environ.get("CHROME_PATH")
    if env: return env
    paths = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
             r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
             r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
             r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
             "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
             "/Applications/Chromium.app/Contents/MacOS/Chromium",
             "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"]
    paths += [shutil.which(n) for n in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome", "microsoft-edge")]
    paths += sorted(glob.glob(os.path.join(os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers"), "chromium-*", "chrome-linux*", "chrome")))
    return next((p for p in paths if p and os.path.exists(p)), "chrome")


CHROME = find_chrome()
HERE = os.path.dirname(os.path.abspath(__file__))
FOOTER = "OFF THE MAP · THU 15.10 · 18:00 · YOUR VENUE"      # event line under the rule: change per event

# photo placement: canvas = orig * PS + offset (photo is 1125x1500, never redrawn)
PS, PX0, PY0 = 0.96, 0, -165
def p2c(x, y): return x * PS + PX0, y * PS + PY0
def o2n(x, y):                                   # v2 canvas point -> same photo point in v3
    return (x + 11) / 0.98 * PS + PX0, (y + 150) / 0.98 * PS + PY0
def o2n_box(b):
    a = o2n(b[0], b[1]); c = o2n(b[2], b[3]); return (round(a[0]), round(a[1]), round(c[0]), round(c[1]))

FACE = p2c(322, 795)                       # rider's head centre
PIN = tuple(round(v) for v in o2n(175, 400))
TAG = o2n_box((222, 420, 402, 480))        # "180 KM" tag box
PEEP = o2n_box((700, 548, 985, 728))                # first peek: lake shore
HEAD_Y = (1090, 1350)                      # headline band
PROF_TOP, SUB_TOP, EN_TOP, RULE_TOP, FOOT_TOP = 1370, 1428, 1506, 1556, 1574
AR_TOP = 1500
MEETUP_LINE = "القصة كاملة باللقاء الجاي"
BANNER = ("حابين نكشفلكم أول رحلة", "رح تكون معنا باللقاء الجاي")
TEXT_ZONE = (90, 1362, 990, 1608)          # keep foil specks off visible text
TRIP_TITLE = "سيبيريا على ظهر خيل"
PROFESSION = "محامي، مهندس برمجيات"


# ---------------------------------------------------------------- helpers
def smooth_noise(n, scale, amp, rnd):
    k = max(2, n // scale + 2)
    ctrl = np.array([rnd.uniform(-1, 1) for _ in range(k)])
    return np.interp(np.linspace(0, k - 1, n), np.arange(k), ctrl) * amp


def torn_walk(n, amp, rnd):
    off, out = 0.0, []
    for _ in range(n):
        off = 0.55 * off + rnd.uniform(-amp, amp)
        out.append(off)
    return np.array(out)


def blob_polygon(seed=3):
    """Organic torn photo shape, bleeding off both sides like the reference."""
    rnd = random.Random(seed)
    xs = np.arange(-30, 1111, 5)
    yt = np.interp(xs, [-30, 60, 200, 420, 620, 760, 880, 1000, 1110], [262, 250, 240, 236, 242, 258, 290, 302, 306])
    yt = yt + smooth_noise(len(xs), 14, 9, rnd) + torn_walk(len(xs), 3.2, rnd)
    yb = np.interp(xs, [-30, 150, 420, 560, 750, 900, 1110], [1098, 1106, 1096, 1072, 1058, 1048, 1036])
    yb = yb + smooth_noise(len(xs), 14, 10, rnd) + torn_walk(len(xs), 3.2, rnd)
    ys_r = np.arange(int(yt[-1]), int(yb[-1]), 5)
    xr = 1090 + np.interp(ys_r, [300, 450, 600, 1080], [0, -26, 0, 0]) + smooth_noise(len(ys_r), 12, 8, rnd) + torn_walk(len(ys_r), 3, rnd)
    ys_l = np.arange(int(yb[0]), int(yt[0]), -5)
    xl = -12 + np.interp(ys_l[::-1], [250, 800, 900, 1000, 1110], [0, 0, 26, 0, 0])[::-1] + smooth_noise(len(ys_l), 12, 8, rnd) + torn_walk(len(ys_l), 3, rnd)
    pts = list(zip(xs, yt)) + list(zip(xr, ys_r)) + list(zip(xs[::-1], yb[::-1])) + list(zip(xl, ys_l))
    return [(float(x), float(y)) for x, y in pts]


def torn_polygon(x0, y0, x1, y1, amp, step, seed):
    rnd = random.Random(seed); pts = []
    def edge(ax, ay, bx, by):
        n = max(2, int(math.hypot(bx - ax, by - ay) / step))
        nx, ny = (by - ay), -(bx - ax); L = math.hypot(nx, ny); nx, ny = nx / L, ny / L
        off = 0
        for i in range(n):
            t = i / n; off = 0.6 * off + rnd.uniform(-amp, amp)
            pts.append((ax + (bx - ax) * t + nx * off, ay + (by - ay) * t + ny * off))
    edge(x0, y0, x1, y0); edge(x1, y0, x1, y1); edge(x1, y1, x0, y1); edge(x0, y1, x0, y0)
    return pts


def mask_from_poly(pts):
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).polygon(pts, fill=255); return m


def rough(mask, seed, radius=3.0, noise=0.35):
    rng = np.random.default_rng(seed)
    a = np.asarray(mask.filter(ImageFilter.GaussianBlur(radius)), np.float32) / 255
    n = rng.random((H // 4, W // 4)).astype(np.float32)
    n = np.asarray(Image.fromarray((n * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32) / 255
    fine = rng.random((H, W)).astype(np.float32)
    a = a + (n - 0.5) * noise + (fine - 0.5) * 0.18
    return Image.fromarray(((a > 0.5) * 255).astype(np.uint8))


def dilate(mask, px):
    a = np.asarray(mask.filter(ImageFilter.GaussianBlur(px)), np.float32)
    return Image.fromarray(((a > 18) * 255).astype(np.uint8))


def flakes(img, pts_src, n, seed, sizes=(1.5, 2, 2.5, 3, 4, 5, 7), spread=10, big=0.08):
    """Gold-leaf flakes with a soft shadow."""
    rnd = random.Random(seed)
    xs, ys = pts_src
    if not len(xs): return
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    shl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ds = ImageDraw.Draw(shl)
    for _ in range(n):
        i = rnd.randrange(len(xs))
        x = xs[i] + rnd.uniform(-spread, spread); y = ys[i] + rnd.uniform(-spread, spread)
        r = rnd.choice(sizes) * (2.2 if rnd.random() < big else 1)
        k = rnd.randint(5, 9)
        pts = [(x + math.cos(t) * r * rnd.uniform(0.45, 1.3), y + math.sin(t) * r * rnd.uniform(0.45, 1.3)) for t in np.linspace(0, 2 * math.pi, k + 1)[:-1]]
        g = rnd.randint(-30, 28)
        d.polygon(pts, fill=(min(255, 198 + g), min(255, 160 + g), min(255, 82 + g), 255))
        ds.polygon([(p[0] + 1.2, p[1] + 1.8) for p in pts], fill=(50, 35, 15, 100))
    img.alpha_composite(shl.filter(ImageFilter.GaussianBlur(1.1)))
    img.alpha_composite(lay)


def edge_points(mask, inner_px=2, outer_px=10):
    a = np.asarray(dilate(mask, outer_px)).astype(bool) & ~np.asarray(mask).astype(bool)
    ys, xs = np.nonzero(a)
    return xs, ys


# ---------------------------------------------------------------- text via Chrome (correct Arabic shaping)
def chrome_layer(name, body_html, css=""):
    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:Taj;src:url(fonts/Tajawal-ExtraBold.ttf)}}
@font-face{{font-family:TajB;src:url(fonts/Tajawal-Black.ttf)}}
@font-face{{font-family:TajBold;src:url(fonts/Tajawal-Bold.ttf)}}
@font-face{{font-family:Mont;src:url(fonts/Montserrat.ttf)}}
html,body{{margin:0;background:transparent;width:{W}px;height:{H}px;overflow:hidden}}
.c{{position:absolute;left:0;width:{W}px;text-align:center;color:#1E3A2B}}
.sub{{font:56px/1 Taj;direction:rtl}}
.prof{{font:38px/1 TajBold;direction:rtl;display:flex;justify-content:center;align-items:center;gap:20px}}
.rl{{display:inline-block;width:56px;height:2px;background:#B8975A}}
.ar2{{font:35px/1 TajBold;direction:rtl}}
.banner{{position:absolute;direction:rtl;text-align:center;color:#1E3A2B;background:#F4ECDB;padding:24px 46px 22px;box-shadow:0 9px 18px rgba(40,28,10,.4);outline:2px solid #B8975A;outline-offset:-11px;white-space:nowrap}}
.b1{{font:47px/1.15 Taj}}
.b2{{font:35px/1.2 TajBold;margin-top:6px}}
.en{{font:600 27px/1 Mont;letter-spacing:7px}}
.rule{{position:absolute;left:130px;width:820px;height:2px;background:#B8975A}}
.foot{{font:600 23px/1 Mont;letter-spacing:4px}}
.tag{{position:absolute;display:flex;align-items:center;gap:16px;direction:rtl;background:#F4ECDB;
  padding:16px 26px 16px 30px;box-shadow:0 7px 14px rgba(40,28,10,.38),0 1px 0 rgba(255,255,255,.6) inset;
  color:#1E3A2B;font:37px/1 Taj;white-space:nowrap}}
.num{{width:50px;height:50px;border-radius:50%;background:#1E3A2B;color:#F4ECDB;font:700 27px/50px Mont;text-align:center;flex:none}}
.ic{{width:42px;height:42px;flex:none}}
{css}</style></head><body>{body_html}</body></html>"""
    path = os.path.join(HERE, f"_{name}.html"); out = os.path.join(HERE, f"_{name}.png")
    open(path, "w", encoding="utf-8").write(html)
    if os.path.exists(out): os.remove(out)             # never reuse a stale render
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
           "--default-background-color=00000000", f"--window-size={W},{H}", f"--screenshot={out}"]
    if sys.platform.startswith("linux") and hasattr(os, "geteuid") and os.geteuid() == 0:
        cmd.append("--no-sandbox")                     # Chrome refuses to start as root otherwise (containers)
    try:
        r = subprocess.run(cmd + [Path(path).as_uri()], capture_output=True)
    except FileNotFoundError:
        raise RuntimeError("No Chromium-based browser found. Install Chrome, Edge or Chromium, or set CHROME=/path/to/browser.")
    if not os.path.exists(out):
        raise RuntimeError(f"Browser '{CHROME}' did not render {name}: {r.stderr.decode(errors='replace')[-400:]}")
    im = Image.open(out).convert("RGBA")
    if im.size != (W, H):                              # some builds shave the window: fit it back onto the canvas
        full = Image.new("RGBA", (W, H), (0, 0, 0, 0)); full.paste(im.crop((0, 0, W, H)), (0, 0)); im = full
    return im


def text_block(sub, en, footer=True, prof=None, sub_top=SUB_TOP, en_top=EN_TOP, ar=None):
    h = ""
    if ar: h += f'<div class="c ar2" style="top:{AR_TOP}px">{ar}</div>'
    if prof: h += f'<div class="c prof" style="top:{PROF_TOP}px"><span class="rl"></span>{prof}<span class="rl"></span></div>'
    if sub: h += f'<div class="c sub" style="top:{sub_top}px">{sub}</div>'
    if en: h += f'<div class="c en" style="top:{en_top}px">{en}</div>'
    if footer:
        h += f'<div class="rule" style="top:{RULE_TOP}px"></div>'
        h += f'<div class="c foot" style="top:{FOOT_TOP}px">{FOOTER}</div>'
    return h


ICONS = {
    "clock": '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="#1E3A2B" stroke-width="2.2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/></svg>',
    "snow": '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="#1E3A2B" stroke-width="2.2" stroke-linecap="round"><path d="M12 2v20M3.3 7l17.4 10M3.3 17L20.7 7M9 4l3 2.5L15 4M9 20l3-2.5 3 2.5"/></svg>',
    "train": '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="#1E3A2B" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="3" width="14" height="14" rx="3"/><path d="M5 11h14M9 21l1.5-4M15 21l-1.5-4"/><circle cx="9" cy="14" r=".6" fill="#1E3A2B"/><circle cx="15" cy="14" r=".6" fill="#1E3A2B"/></svg>',
    "waves": '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="#1E3A2B" stroke-width="2.2" stroke-linecap="round"><path d="M2 8c2.5-2 4.5-2 7 0s4.5 2 7 0 4.5-2 6 0M2 13c2.5-2 4.5-2 7 0s4.5 2 7 0 4.5-2 6 0M2 18c2.5-2 4.5-2 7 0s4.5 2 7 0 4.5-2 6 0"/></svg>',
}
CLUES = [  # (centre, rotation, number, icon, text)
    ((585, 322), -2.0, 1, "waves", "فيها أعمق بحيرة بالعالم"),
    ((326, 600), 1.6, 2, "snow", "الشتا بيوصل 40 تحت الصفر"),
    ((560, 862), -1.2, 3, "train", "أطول سكة قطار بالعالم بتقطعها"),
]


def clue_tags():
    h = ""
    for (cx, cy), rot, n, ic, t in CLUES:
        h += (f'<div class="tag" style="left:{cx}px;top:{cy}px;transform:translate(-50%,-50%) rotate({rot}deg)">'
              f'<span class="num">{n}</span>{ICONS[ic]}<span>{t}</span></div>')
    return chrome_layer("clues", h)


# ---------------------------------------------------------------- brush headline (AI lettering, keyed out)
BANDS = {"name": ("lettering.png", 197, 521), "guess": ("lettering.png", 636, 935), "clues": ("lettering.png", 1070, 1383)}
LSCALE = 725 / 929
SHEET_SCALE = {"lettering.png": 1.0}        # second sheet is calibrated on its own "مهدي كبها" line


def use_word(key, slug):
    """Use a verified word from kit/words/ (see words/INDEX.md) as headline `key`."""
    BANDS[key] = os.path.join(HERE, "words", f"{slug}.png")


def lettering(key, extra=1.0):
    if isinstance(BANDS[key], str):              # verified library word: already keyed, at library size
        im = Image.open(BANDS[key]).convert("RGBA")
        return im.resize((round(im.width * extra), round(im.height * extra)), Image.LANCZOS)
    sheet, y0, y1 = BANDS[key]
    src = Image.open(sheet).convert("RGB")
    crop = src.crop((0, y0 - 6, src.width, y1 + 6))
    a = np.asarray(crop, np.float32)
    lum = a @ np.array([0.299, 0.587, 0.114], np.float32)
    alpha = np.clip((250 - lum) / (250 - 45), 0, 1)
    rgb = np.clip((a - (1 - alpha[..., None]) * 255) / np.maximum(alpha[..., None], 1e-3), 0, 255)
    rgb = np.where(alpha[..., None] > 0.02, rgb, 0)
    rgba = np.dstack([rgb, alpha * 255]).astype(np.uint8)
    im = Image.fromarray(rgba, "RGBA")
    bb = im.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox()
    im = im.crop(bb)
    k = LSCALE * SHEET_SCALE[sheet] * extra
    return im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)


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
    return out


def load_sheet2():
    """Vote-story lettering: line 1 is 'مهدي كبها' again, used to match the scale of sheet 1."""
    b = [x for x in ink_bands("lettering2.png") if x[1] - x[0] > 60]
    name_w = b[0][2]
    SHEET_SCALE["lettering2.png"] = 929 / name_w
    BANDS["vote"] = ("lettering2.png", b[1][0], b[1][1])
    BANDS["coming"] = ("lettering2.png", b[2][0], b[2][1])
    return b


def load_sheet3():
    b = [x for x in ink_bands("lettering3.png") if x[1] - x[0] > 60]
    SHEET_SCALE["lettering3.png"] = 929 / b[0][2]
    BANDS["first"] = ("lettering3.png", b[1][0], b[1][1])
    return b


INTRO_BAND = (1180, 1414)
def intro_text():
    h = ('<div class="c prof" style="top:1120px;font:44px/1 Taj"><span class="rl"></span>رح نكشف<span class="rl"></span></div>'
         '<div class="c sub" style="top:1436px;font-size:52px">رح تكون معنا <span style="color:#8C6A2F">ب15/10</span></div>'
         '<div class="c en" style="top:1510px">MEETUP · TRAVEL STORIES</div>'
         f'<div class="rule" style="top:{RULE_TOP}px"></div>'
         f'<div class="c foot" style="top:{FOOT_TOP}px">{FOOTER}</div>')
    return chrome_layer("t_intro", h)


def catmull(points, per=24):
    pts = [points[0]] + points + [points[-1]]; out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = map(np.array, pts[i - 1:i + 3])
        for t in np.linspace(0, 1, per, endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(np.array(points[-1])); return [tuple(p) for p in out]


def star(d, cx, cy, rv, rh, col):
    w = rv * 0.11
    d.polygon([(cx, cy - rv), (cx + w, cy - w), (cx + rh, cy), (cx + w, cy + w), (cx, cy + rv), (cx - w, cy + w), (cx - rh, cy), (cx - w, cy - w)], fill=col)


def headline(key, band=None, extra=1.0, star_on=True, swoosh_k=1.0):
    """Brush lettering + gold swoosh behind it + sparkle star, as one RGBA layer."""
    let = lettering(key, extra)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    band = band or HEAD_Y
    cy = (band[0] + band[1]) / 2
    x0, y0 = round(540 - let.width / 2), round(cy - let.height / 2)
    S = 3  # supersampled swoosh
    sw = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0)); d = ImageDraw.Draw(sw)
    path = catmull([(x0 - 40, cy + 70 * swoosh_k), (x0 + 160, cy + 10 * swoosh_k), (540, cy - 18 * swoosh_k), (x0 + let.width - 120, cy + 8 * swoosh_k), (x0 + let.width + 40, cy + 92 * swoosh_k)], 40)
    n = len(path)
    for i in range(n - 1):
        t = i / (n - 1); w = 1.0 + 2.6 * math.sin(math.pi * t) ** 0.8
        (ax, ay), (bx, by) = path[i], path[i + 1]
        d.line((ax * S, ay * S, bx * S, by * S), fill=(196, 160, 92, 255), width=max(1, int(w * S)))
    if star_on: star(d, (x0 + let.width * 0.47) * S, (y0 - 6) * S, 46 * S, 24 * S, (200, 162, 90, 255))
    sw = sw.resize((W, H), Image.LANCZOS)
    lay.alpha_composite(sw)
    lay.alpha_composite(let, (x0, y0))
    return lay, (x0, y0, x0 + let.width, y0 + let.height)


# ---------------------------------------------------------------- base design
def build_plate():
    plate = Image.open("plate2.png").convert("RGB")
    s = max(W / plate.width, H / plate.height)
    plate = plate.resize((round(plate.width * s), round(plate.height * s)), Image.LANCZOS)
    ox = (plate.width - W) // 2
    plate = plate.crop((ox, 0, ox + W, H))
    # move the compass a little higher and smaller so the photo can start under it
    comp = plate.crop((835, 110, 1080, 380))
    clean = plate.crop((350, 600, 640, 920))
    cm = Image.new("L", clean.size, 0); ImageDraw.Draw(cm).rectangle((14, 14, clean.width - 1, clean.height - 14), fill=255)
    plate.paste(clean, (800, 85), cm.filter(ImageFilter.GaussianBlur(9)))
    cs = 0.78
    comp = comp.resize((round(comp.width * cs), round(comp.height * cs)), Image.LANCZOS)
    fm2 = Image.new("L", comp.size, 0); ImageDraw.Draw(fm2).rounded_rectangle((8, 8, comp.width - 8, comp.height - 8), 40, fill=255)
    plate.paste(comp, (round(962 - comp.width / 2), round(184 - comp.height / 2)), fm2.filter(ImageFilter.GaussianBlur(6)))
    return plate.convert("RGBA")


ROUTE = [(-20, 330), (60, 362), (125, 420), (175, 470), (245, 520), (310, 555), (420, 572), (520, 600), (610, 650), (690, 720),
         (770, 815), (880, 862), (990, 900), (1100, 935)]
WAYPOINTS = [(60, 362), (310, 555), (610, 650), (880, 862)]
ROUTE = [o2n(*p) for p in ROUTE]
WAYPOINTS = [o2n(*p) for p in WAYPOINTS]


def draw_route(img):
    S = 2
    lay = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    sh = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
    path = catmull(ROUTE, 30)
    dist, acc = 0.0, []
    for i in range(len(path) - 1):
        acc.append(dist); dist += math.dist(path[i], path[i + 1])
    dash, gap, pos, on = 16, 11, 0.0, True
    seg = []
    for i in range(len(path) - 1):
        (ax, ay), (bx, by) = path[i], path[i + 1]
        L = math.dist(path[i], path[i + 1])
        if L == 0: continue
        t = 0.0
        while t < L:
            step = min((dash if on else gap) - pos, L - t)
            if on:
                p = (ax + (bx - ax) * t / L, ay + (by - ay) * t / L); q = (ax + (bx - ax) * (t + step) / L, ay + (by - ay) * (t + step) / L)
                for dd, col, off in ((ds, (20, 15, 5, 120), 1.5), (d, (247, 226, 168, 255), 0)):
                    dd.line(((p[0] + off) * S, (p[1] + off) * S, (q[0] + off) * S, (q[1] + off) * S), fill=col, width=4 * S)
            pos += step; t += step
            if pos >= (dash if on else gap): pos, on = 0.0, not on
    for x, y in WAYPOINTS:
        ds.ellipse(((x - 10 + 1.5) * S, (y - 10 + 1.5) * S, (x + 10 + 1.5) * S, (y + 10 + 1.5) * S), fill=(20, 15, 5, 110))
        d.ellipse(((x - 10) * S, (y - 10) * S, (x + 10) * S, (y + 10) * S), fill=(247, 236, 208, 255), outline=(200, 160, 82, 255), width=3 * S)
    img.alpha_composite(sh.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.2)))
    img.alpha_composite(lay.resize((W, H), Image.LANCZOS))


def draw_tag(img, text="180 KM"):
    tag = Image.new("RGBA", (TAG[2] - TAG[0] + 40, TAG[3] - TAG[1] + 40), (0, 0, 0, 0))
    td = ImageDraw.Draw(tag)
    td.rectangle((20, 20, tag.width - 20, tag.height - 20), fill=(244, 236, 219, 255))
    f = ImageFont.truetype(FONT, 31); f.set_variation_by_axes([700])
    td.text((tag.width / 2, tag.height / 2 + 1), text, font=f, fill=GREEN, anchor="mm")
    tag = tag.rotate(6, resample=Image.BICUBIC)
    tsh = Image.new("RGBA", tag.size, (40, 30, 15, 0)); tsh.putalpha(tag.getchannel("A").filter(ImageFilter.GaussianBlur(5)).point(lambda v: v * 0.45))
    img.alpha_composite(tsh, (TAG[0] - 20 + 3, TAG[1] - 20 + 5)); img.alpha_composite(tag, (TAG[0] - 20, TAG[1] - 20))


def build_base(seed=3):
    base = build_plate()
    d = ImageDraw.Draw(base)
    import logo
    logo.place(base, (540, 120), 170, "line")             # your logo from inputs/ (skipped if there is none)

    photo_mask = rough(mask_from_poly(blob_polygon(seed)), 11, 1.6, 0.25)
    border = rough(dilate(photo_mask, 9), 12, 1.6, 0.4)
    sh = Image.new("RGBA", (W, H), (60, 45, 25, 0)); sh.putalpha(border.filter(ImageFilter.GaussianBlur(12)).point(lambda v: v * 0.33))
    base.alpha_composite(sh, (0, 7))
    base.paste(Image.new("RGBA", (W, H), (251, 248, 240, 255)), (0, 0), border)

    photo = Image.open("inputs/photo.jpg").convert("RGB")
    photo = photo.resize((round(photo.width * PS), round(photo.height * PS)), Image.LANCZOS)
    photo = ImageEnhance.Color(photo).enhance(0.94)
    photo = ImageEnhance.Contrast(photo).enhance(0.97)
    photo = Image.blend(photo, Image.new("RGB", photo.size, (236, 222, 196)), 0.05)
    full = Image.new("RGBA", (W, H), (0, 0, 0, 0)); full.paste(photo, (PX0, PY0))
    base.paste(full, (0, 0), photo_mask)
    draw_route(base)                 # route is printed on the photo (under the foil)
    draw_tag(base)
    flakes(base, edge_points(border, outer_px=6), 105, 21, big=0.035)
    return base, photo_mask, border


def draw_pin(img):
    x, y = PIN
    S = 3
    lay = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
    r = 36
    poly = [(x - r * 0.72, y + r * 0.7), (x, y + r + 34), (x + r * 0.72, y + r * 0.7)]
    ds.ellipse((x - r, y - r, x + r, y + r), fill=(0, 0, 0, 110)); ds.polygon(poly, fill=(0, 0, 0, 110))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)), (3, 6))
    d.ellipse(((x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S), fill=GREEN + (255,))
    d.polygon([(px * S, py * S) for px, py in poly], fill=GREEN + (255,))
    d.ellipse(((x - 9) * S, (y + r + 30) * S, (x + 9) * S, (y + r + 48) * S), fill=(246, 240, 226, 255), outline=GOLD + (255,), width=3 * S)
    lay = lay.resize((W, H), Image.LANCZOS)
    f = ImageFont.truetype(FONT, 30); f.set_variation_by_axes([700])
    ImageDraw.Draw(lay).text((x, y + 1), "02", font=f, fill=(246, 240, 226), anchor="mm")
    img.alpha_composite(lay)


def coin(img, cx, cy, r=40, angle=-25):
    S = 4; R = r * S; size = 2 * R + 40 * S
    c = Image.new("RGBA", (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(c); o = size // 2
    for i in range(R, 0, -1):
        t = i / R; k = (1 - t) ** 0.6
        d.ellipse((o - i - 10 * S * (1 - t), o - i - 10 * S * (1 - t), o + i - 10 * S * (1 - t), o + i - 10 * S * (1 - t)),
                  fill=(int(150 + 75 * k), int(118 + 70 * k), int(62 + 50 * k), 255))
    d.ellipse((o - R, o - R, o + R, o + R), outline=(120, 92, 45, 255), width=3 * S)
    d.ellipse((o - R * 0.78, o - R * 0.78, o + R * 0.78, o + R * 0.78), outline=(138, 106, 55, 255), width=2 * S)
    for k in range(60):
        a = 2 * math.pi * k / 60
        d.line((o + math.cos(a) * R * 0.88, o + math.sin(a) * R * 0.88, o + math.cos(a) * R * 0.97, o + math.sin(a) * R * 0.97), fill=(140, 108, 56, 255), width=S)
    pts = []
    for k in range(8):
        a = math.pi / 4 * k - math.pi / 2; rr = R * (0.5 if k % 2 == 0 else 0.14)
        pts.append((o + math.cos(a) * rr, o + math.sin(a) * rr))
    d.polygon(pts, fill=(132, 100, 50, 255))
    c = c.rotate(angle, resample=Image.BICUBIC).resize((size // S, size // S), Image.LANCZOS)
    sh = Image.new("RGBA", c.size, (40, 28, 10, 0)); sh.putalpha(c.getchannel("A").filter(ImageFilter.GaussianBlur(5)).point(lambda v: v * 0.5))
    img.alpha_composite(sh, (int(cx - c.width / 2 + 4), int(cy - c.height / 2 + 7)))
    img.alpha_composite(c, (int(cx - c.width / 2), int(cy - c.height / 2)))


# ---------------------------------------------------------------- scratching
STREAKS = []


def zigzag(d, box, seed, width=(34, 50), slant=0.25, ragged=55):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    y = y0 + rnd.uniform(5, 15); left = True
    while y < y1:
        w = rnd.uniform(*width)
        xa = x0 + rnd.uniform(-ragged * 0.4, ragged); xb = x1 + rnd.uniform(-ragged, ragged * 0.4)
        ya = y; yb = y + rnd.uniform(-10, 24) + (xb - xa) * slant * rnd.uniform(0.2, 1)
        n = 12
        pts = [(xa + (xb - xa) * i / n + rnd.uniform(-4, 4), ya + (yb - ya) * i / n + rnd.uniform(-6, 6)) for i in range(n + 1)]
        if not left: pts.reverse()
        d.line(pts, fill=255, width=int(w), joint="curve")
        for p in (pts[0], pts[-1]):
            d.ellipse((p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2), fill=255)
        for _ in range(rnd.randint(0, 3)):
            off = rnd.uniform(-w * 0.4, w * 0.4); a = rnd.uniform(0.05, 0.5); b = a + rnd.uniform(0.15, 0.5)
            seg = pts[int(a * n):int(min(b, 1) * n) + 1]
            if len(seg) > 1: STREAKS.append(([(p[0], p[1] + off) for p in seg], rnd.choice([1, 1, 2, 3])))
        y += w * rnd.uniform(0.62, 0.98); left = not left


def apply_streaks(mask, keep_clear=()):
    d = ImageDraw.Draw(mask)
    for pts, w in STREAKS:
        if any(all(b[0] - 10 < p[0] < b[2] + 10 and b[1] - 10 < p[1] < b[3] + 10 for p in pts) for b in keep_clear): continue
        d.line(pts, fill=0, width=w)


def leftovers(mask, seed, n=60, avoid=()):
    rnd = random.Random(seed); d = ImageDraw.Draw(mask)
    ys, xs = np.nonzero(np.asarray(mask))
    for _ in range(n):
        i = rnd.randrange(len(xs)); x, y = xs[i], ys[i]
        if any(b[0] - 10 < x < b[2] + 10 and b[1] - 6 < y < b[3] + 6 for b in avoid): continue
        r = rnd.uniform(1.5, 5)
        d.polygon([(x + math.cos(k) * r * rnd.uniform(0.5, 1.4), y + math.sin(k) * r * rnd.uniform(0.3, 1)) for k in np.linspace(0, 2 * math.pi, 7)[:-1]], fill=0)


def blob(cx, cy, rx, ry, seed, lumps=14):
    rnd = random.Random(seed); pts = []
    for k in range(lumps * 6):
        a = 2 * math.pi * k / (lumps * 6)
        j = 1 + 0.08 * math.sin(a * lumps + rnd.uniform(0, 6)) + rnd.uniform(-0.04, 0.04)
        pts.append((cx + math.cos(a) * rx * j, cy + math.sin(a) * ry * j))
    return pts


_FOIL = None
def foil_tex():
    global _FOIL
    if _FOIL is None:
        tex = Image.open("foil.png").convert("RGB").resize((1080, 1080), Image.LANCZOS)
        big = Image.new("RGB", (W, H)); big.paste(tex, (0, 0)); big.paste(tex.transpose(Image.FLIP_TOP_BOTTOM), (0, 1080))
        rng = np.random.default_rng(5)
        _FOIL = Image.fromarray(np.clip(np.asarray(big, np.float32) * 0.96 + rng.normal(0, 7, (H, W, 1)), 0, 255).astype(np.uint8)).convert("RGBA")
    return _FOIL.copy()


def apply_foil(img, cover, reveal, seed, crumb_n, avoid=()):
    foil = foil_tex()
    alpha = ImageChops.subtract(cover, reveal)
    rim = ImageChops.subtract(alpha, alpha.filter(ImageFilter.MinFilter(5)))
    foil.paste(Image.new("RGBA", (W, H), (122, 94, 48, 255)), (0, 0), rim.point(lambda v: v * 0.75))
    hi = ImageChops.subtract(alpha, ImageChops.offset(alpha, 2, 2)).filter(ImageFilter.GaussianBlur(0.8))
    foil.paste(Image.new("RGBA", (W, H), (245, 226, 170, 255)), (0, 0), hi.point(lambda v: v * 0.7))
    foil.putalpha(alpha)
    sh = Image.new("RGBA", (W, H), (45, 32, 12, 0)); sh.putalpha(alpha.filter(ImageFilter.GaussianBlur(2.5)).point(lambda v: v * 0.45))
    img.alpha_composite(sh, (1, 3)); img.alpha_composite(foil)
    # crumbs just off the scratched edges
    edge = ImageChops.multiply(ImageChops.subtract(alpha.filter(ImageFilter.MaxFilter(9)), alpha), reveal)
    ys, xs = np.nonzero(np.asarray(edge) > 128)
    keep = np.ones(len(xs), bool)
    for b in avoid: keep &= ~((xs > b[0] - 18) & (xs < b[2] + 18) & (ys > b[1] - 8) & (ys < b[3] + 8))
    flakes(img, (xs[keep], ys[keep]), crumb_n, seed + 1, sizes=(1.5, 2, 2.5, 3, 3.5, 4.5, 6), spread=13, big=0.0)


# ---------------------------------------------------------------- build
def main():
    os.chdir(HERE)
    base, photo_mask, border = build_base()
    head_name, nb = headline("name")
    head_guess, _ = headline("guess")
    head_clues, _ = headline("clues")
    use_word("vote", "sawwit")                 # verified library words (kit/words), no extra sheets needed
    head_vote, _ = headline("vote")
    name_txt = chrome_layer("t_name", text_block(TRIP_TITLE, None, prof=PROFESSION, ar=MEETUP_LINE))
    s1_txt = chrome_layer("t_s1", text_block("قبل ما نكشط الكرت…", "FIRST REVEAL · GUESS WHERE", sub_top=1384, en_top=1466))
    banner = chrome_layer("banner", f'<div class="banner" style="left:588px;top:352px;transform:translate(-50%,-50%) rotate(-1.5deg)">'
                                    f'<div class="b1">{BANNER[0]}</div><div class="b2">{BANNER[1]}</div></div>')
    s2_txt = chrome_layer("t_s2", text_block("فكّر منيح… بالستوري الجاي بتصوّت", "3 CLUES · 1 DESTINATION", sub_top=1384, en_top=1466))
    vote_txt = chrome_layer("t_vote", text_block(None, None, footer=False, prof="الجواب تحت الكرت"))
    clues = clue_tags()

    # ---- reveal masks (each stage keeps everything before it)
    peep = Image.new("L", (W, H), 0)
    zigzag(ImageDraw.Draw(peep), PEEP, 99, (30, 42), slant=0.06, ragged=40)
    peep = ImageChops.multiply(rough(peep, 199, 2.0, 0.3), photo_mask)
    STREAKS.clear()
    first = Image.new("L", (W, H), 0)
    ImageDraw.Draw(first).line([(PEEP[0] + 40, PEEP[1] + 62), (PEEP[0] + 120, PEEP[1] + 70), (PEEP[0] + 190, PEEP[1] + 66)], fill=255, width=26, joint="curve")
    s0 = ImageChops.multiply(rough(first, 198, 1.6, 0.3), peep)

    t1 = Image.new("L", (W, H), 0)
    zigzag(ImageDraw.Draw(t1), (TAG[0] - 8, TAG[1] - 12, TAG[2] + 6, TAG[3] - 4), 101, (26, 34), slant=0.05, ragged=20)
    t1 = rough(t1, 201, 2.0, 0.3)
    s1 = ImageChops.multiply(ImageChops.lighter(peep, t1), photo_mask)

    z2 = Image.new("L", (W, H), 0); d2 = ImageDraw.Draw(z2)
    zigzag(d2, o2n_box((-10, 690, 560, 1150)), 102, (40, 58), slant=0.12, ragged=90)
    zigzag(d2, o2n_box((370, 560, 640, 740)), 103, (30, 44), slant=0.2, ragged=70)
    zigzag(d2, o2n_box((-10, 560, 265, 740)), 104, (30, 44), slant=-0.1, ragged=60)
    zigzag(d2, o2n_box((560, 930, 900, 1100)), 105, (36, 50), slant=-0.05, ragged=110)
    z2 = rough(z2, 202, 2.5, 0.35)
    face_big = rough(mask_from_poly(blob(FACE[0], FACE[1] + 2, 60, 64, 7)), 207, 2.0, 0.3)
    s2 = ImageChops.subtract(ImageChops.lighter(s1, z2), face_big)
    apply_streaks(s2, keep_clear=[TAG])
    leftovers(s2, 302, 140, avoid=[TAG])
    s2 = ImageChops.multiply(ImageChops.lighter(s2, t1), photo_mask)

    panel = rough(mask_from_poly(torn_polygon(55, 1086, 1025, 1546, 1.2, 6, 21)), 3, 1.0, 0.15)
    cover = ImageChops.lighter(photo_mask, panel)
    face_p = rough(mask_from_poly(blob(FACE[0], FACE[1] + 2, 54, 58, 8)), 208, 2.0, 0.3)
    name_p = ImageChops.multiply(rough(mask_from_poly(torn_polygon(nb[0] - 34, 1080, nb[2] + 34, 1356, 5, 9, 31)), 209, 3.0, 0.35), panel)
    patches = ImageChops.lighter(face_p, name_p)
    s3 = ImageChops.lighter(ImageChops.subtract(cover, patches), s2)
    leftovers(s3, 303, 110, avoid=[TAG, TEXT_ZONE])
    s3 = ImageChops.subtract(s3, patches)

    stories = []
    use_word("first", "awwal_rihla")
    head_first, hb = headline("first", INTRO_BAND, extra=0.84, star_on=False)
    print("intro headline box", hb)
    # 0 — intro: the card is still sealed, the coin has just started
    img = base.copy(); img.alpha_composite(head_first); img.alpha_composite(intro_text())
    apply_foil(img, photo_mask, s0, 9, 18)
    draw_pin(img); coin(img, PEEP[0] + 228, PEEP[1] + 70, 40, -10); stories.append(img)
    # 1 — hook: sealed card with one peek at the lake
    img = base.copy(); img.alpha_composite(head_guess); img.alpha_composite(s1_txt)
    apply_foil(img, photo_mask, peep, 10, 45)
    draw_pin(img); coin(img, 912, 732); stories.append(img)
    # 2 — clues on the sealed card, quiz below
    img = base.copy(); img.alpha_composite(head_clues); img.alpha_composite(s2_txt)
    apply_foil(img, photo_mask, peep, 10, 45)
    draw_pin(img); img.alpha_composite(clues); coin(img, 985, 968); stories.append(img)
    # 3 — vote: same sealed card + clue recap, big empty slot for the Instagram poll
    img = base.copy(); img.alpha_composite(head_vote); img.alpha_composite(vote_txt)
    apply_foil(img, photo_mask, peep, 10, 45)
    draw_pin(img); img.alpha_composite(clues); coin(img, 985, 968); stories.append(img)
    # 3..5 — scratch stages over the full design
    for i, (rev, cn, cpos) in enumerate([(s1, 120, (458, 472)), (s2, 220, (585, 1026)), (s3, 260, (396, 560))]):
        img = base.copy(); img.alpha_composite(head_name); img.alpha_composite(name_txt)
        apply_foil(img, cover, rev, 20 + i, cn, avoid=[TAG, TEXT_ZONE])
        draw_pin(img); coin(img, *cpos); stories.append(img)
    # 6 — full reveal
    img = base.copy(); img.alpha_composite(head_name); img.alpha_composite(name_txt)
    flakes(img, edge_points(photo_mask, outer_px=3), 45, 44)
    draw_pin(img); coin(img, 1003, 1580, 36, -15); stories.append(img)


    os.makedirs("out", exist_ok=True)
    for i, s in enumerate(stories, 1):
        s.convert("RGB").save(f"out/story_{i}.png")
    tot = np.asarray(cover).astype(bool).sum()
    for k, s in (("s1", s1), ("s2", s2), ("s3", s3)):
        print(k, round(100 * (np.asarray(s).astype(bool) & np.asarray(cover).astype(bool)).sum() / tot), "% of foil scratched")
    strip = Image.new("RGB", (W * 8 + 140, H), (40, 40, 40))
    for i, s in enumerate(stories): strip.paste(s.convert("RGB"), (i * (W + 20), 0))
    strip.resize((strip.width // 4, H // 4), Image.LANCZOS).save("out/contact.png")


if __name__ == "__main__":
    main()
