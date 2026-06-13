#!/usr/bin/env python3
"""
Anticipation Consulting — brand asset generator.

Builds the social/identity kit from the two brand typefaces:
  - GFS Didot (the rotated "A" mark)
  - Cormorant Garamond, variable wght (the "A-NTICIPATION Consulting" wordmark)

Run:  python3 brand/generate_assets.py
Fonts are fetched into brand/fonts/ by fetch_fonts.sh (or download_fonts()).
Outputs land in brand/dist/.
"""
import os, math, random
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")
DIST = os.path.join(HERE, "dist")
os.makedirs(DIST, exist_ok=True)

DIDOT = os.path.join(FONTS, "GFSDidot-Regular.ttf")
CORM  = os.path.join(FONTS, "CormorantGaramond-VF.ttf")
MONO  = os.path.join(FONTS, "IBMPlexMono-Regular.ttf")

# ---- brand palette (hex from assets/site.css, resolved to sRGB) -------------
BLUE      = (47, 111, 224)    # #2f6fe0  brand blue — the mark
INK       = (26, 29, 34)      # #1a1d22  near-black ground
PAPER     = (247, 246, 242)   # warm off-white
INK_SOFT  = (99, 107, 119)    # muted slate — "Consulting" on light
ON_INK    = (233, 231, 225)   # paper-tint text on dark
ON_INK_SOFT = (165, 172, 184) # "Consulting" on dark
LINE_DK   = (233, 231, 225)   # motif line base (used at low alpha)

ROT = 30  # CCW degrees — matches the site's rotate(-30) (SVG y-down)
SS = 3    # supersample factor for crisp downsampling

# ---- font helpers -----------------------------------------------------------
_didot_probe = ImageFont.truetype(DIDOT, 1000)
_l, _t, _r, _b = _didot_probe.getbbox("H")
DIDOT_CAP = (_b - _t) / 1000.0  # cap-height as fraction of em

def didot_font(cap_px):
    return ImageFont.truetype(DIDOT, max(1, int(round(cap_px / DIDOT_CAP))))

def cormorant(cap_px, weight):
    f = ImageFont.truetype(CORM, 1000)
    f.set_variation_by_axes([weight])
    l, t, r, b = f.getbbox("H")
    cap = (b - t) / 1000.0
    f = ImageFont.truetype(CORM, max(1, int(round(cap_px / cap))))
    f.set_variation_by_axes([weight])
    return f

def mono_font(px):
    return ImageFont.truetype(MONO, px)

def didot_A(cap_px, color):
    """A rendered in Didot, tight-cropped, rotated to match the mark."""
    f = didot_font(cap_px)
    pad = int(cap_px * 2.2) + 8
    tmp = Image.new("RGBA", (pad, pad), (0, 0, 0, 0))
    ImageDraw.Draw(tmp).text((pad // 2, pad // 2), "A", font=f,
                             fill=color + (255,), anchor="mm")
    tmp = tmp.crop(tmp.getbbox())
    return tmp.rotate(ROT, expand=True, resample=Image.BICUBIC)

def tracked(draw, xy, s, font, fill, track):
    """Draw letter-tracked text on the baseline; return end-x."""
    x, y = xy
    for ch in s:
        draw.text((x, y), ch, font=font, fill=fill, anchor="ls")
        x += font.getlength(ch) + track
    return x

# ---- wordmark lockup --------------------------------------------------------
def compose_wordmark(text_col, soft_col, cap=210):
    H = cap * SS
    W = int(H * 36)
    canvas = Image.new("RGBA", (W, H * 6), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    baseline = H * 3
    x = H * 0.3

    A = didot_A(int(H * 1.16), BLUE)
    ay = int(baseline - H * 0.5 - A.height / 2)
    canvas.alpha_composite(A, (int(x), ay))
    x += A.width + H * 0.14

    fsemi = cormorant(H, 600)
    x = tracked(d, (x, baseline), "NTICIPATION", fsemi, text_col + (255,),
                0.12 * fsemi.size)
    x += 0.42 * H
    flight = cormorant(H, 300)
    tracked(d, (x, baseline), "Consulting", flight, soft_col + (255,),
            0.04 * flight.size)

    bbox = canvas.getbbox()
    pad = int(H * 0.30)
    crop = canvas.crop((bbox[0] - pad, bbox[1] - pad,
                        bbox[2] + pad, bbox[3] + pad))
    return crop.resize((crop.width // SS, crop.height // SS), Image.LANCZOS)

# ---- avatar (square mark) ---------------------------------------------------
def avatar(bg, a_col, size=1000):
    S = size * SS
    img = Image.new("RGBA", (S, S), bg + (255,))
    A = didot_A(int(S * 0.44), a_col)
    img.alpha_composite(A, ((S - A.width) // 2, (S - A.height) // 2))
    return img.resize((size, size), Image.LANCZOS).convert("RGB")

# ---- node-link motif (echo of the site's canvas background) -----------------
def draw_motif(img, seed=11, n=46, color=LINE_DK, alpha=34):
    rng = random.Random(seed)
    W, H = img.size
    pts = [(rng.uniform(0, W), rng.uniform(0, H)) for _ in range(n)]
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    link = int(min(W, H) * 0.26)
    for i in range(n):
        for j in range(i + 1, n):
            dx = pts[i][0] - pts[j][0]; dy = pts[i][1] - pts[j][1]
            dist = math.hypot(dx, dy)
            if dist < link:
                a = int(alpha * (1 - dist / link))
                d.line([pts[i], pts[j]], fill=color + (a,), width=max(1, SS))
    for k, (x, y) in enumerate(pts):
        r = SS * (3 if k % 7 else 5)
        c = BLUE if k % 7 == 0 else color
        d.ellipse([x - r, y - r, x + r, y + r], fill=c + (150 if k % 7 == 0 else 70,))
    img.alpha_composite(layer)

# ---- banner -----------------------------------------------------------------
def banner(w, h, name, tagline=True):
    W, H = w * SS, h * SS
    img = Image.new("RGBA", (W, H), INK + (255,))
    draw_motif(img, seed=11, n=int(W * H / 95000), alpha=30)
    d = ImageDraw.Draw(img)

    # fit the wordmark by width AND height, whichever binds first
    wm = compose_wordmark(ON_INK, ON_INK_SOFT, cap=210)
    scale = min(W * 0.80 / wm.width, H * 0.34 / wm.height)
    wm = wm.resize((int(wm.width * scale), int(wm.height * scale)), Image.LANCZOS)

    f = mono_font(int(H * 0.043))
    tg = "WHAT  YOU  DIDN'T  KNOW  TO  ASK"
    tg_w = sum(f.getlength(c) + 0.18 * f.size for c in tg)
    gap = int(H * 0.085)
    block_h = wm.height + gap + int(f.size * 1.1)
    wx = int(W * 0.07)
    wy = (H - block_h) // 2

    img.alpha_composite(wm, (wx, wy))
    if tagline:
        ry = wy + wm.height + gap // 2
        d.line([(wx + 3, ry), (wx + int(W * 0.04), ry)], fill=BLUE + (255,),
               width=max(1, SS))
        ty = wy + wm.height + gap
        tracked(d, (wx + int(W * 0.052), ty + f.size), tg, f, ON_INK_SOFT + (255,),
                0.18 * f.size)

    return img.resize((w, h), Image.LANCZOS).convert("RGB")

# ---- mark-A.svg (vector, glyph outline) -------------------------------------
def write_mark_svg():
    from fontTools.ttLib import TTFont
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.boundsPen import BoundsPen
    font = TTFont(DIDOT)
    gs = font.getGlyphSet()
    gname = font.getBestCmap()[ord("A")]
    pen = SVGPathPen(gs); gs[gname].draw(pen); dd = pen.getCommands()
    bp = BoundsPen(gs); gs[gname].draw(bp)
    x0, y0, x1, y1 = bp.bounds
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    V = 1000
    s = (V * 0.62) / (y1 - y0)
    # translate to centre · rotate · flip-y · recentre glyph
    tform = (f"translate({V/2:.2f},{V/2:.2f}) rotate(-{ROT}) "
             f"scale({s:.5f},{-s:.5f}) translate({-cx:.2f},{-cy:.2f})")
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{V}" height="{V}" '
           f'viewBox="0 0 {V} {V}" role="img" aria-label="Anticipation Consulting">\n'
           f'  <g transform="{tform}" fill="#2f6fe0"><path d="{dd}"/></g>\n</svg>\n')
    open(os.path.join(DIST, "mark-A.svg"), "w").write(svg)
    # tinted-ground variants
    for fn, ground, fill in [("mark-A-on-ink.svg", "#1a1d22", "#2f6fe0"),
                             ("mark-A-on-blue.svg", "#2f6fe0", "#f7f6f2")]:
        s2 = svg.replace('fill="#2f6fe0"><path', f'fill="{fill}"><path').replace(
            f'viewBox="0 0 {V} {V}">',
            f'viewBox="0 0 {V} {V}"><rect width="{V}" height="{V}" fill="{ground}"/>')
        # ensure rect sits behind: insert after opening tag instead
        s2 = svg.replace('aria-label="Anticipation Consulting">\n',
                         f'aria-label="Anticipation Consulting">\n  '
                         f'<rect width="{V}" height="{V}" fill="{ground}"/>\n')
        s2 = s2.replace('fill="#2f6fe0"><path', f'fill="{fill}"><path')
        open(os.path.join(DIST, fn), "w").write(s2)

# ---- build ------------------------------------------------------------------
def save(img, name):
    img.save(os.path.join(DIST, name))
    print("  •", name, "%dx%d" % img.size)

def main():
    print("avatars…")
    save(avatar(INK, BLUE, 1000),  "avatar-ink-1000.png")
    save(avatar(INK, BLUE, 400),   "avatar-ink-400.png")
    save(avatar(BLUE, PAPER, 1000), "avatar-blue-1000.png")
    save(avatar(PAPER, BLUE, 1000), "avatar-paper-1000.png")

    print("wordmarks…")
    wl = compose_wordmark(INK, INK_SOFT)
    wd = compose_wordmark(ON_INK, ON_INK_SOFT)
    save(wl, "wordmark-light.png")   # for light backgrounds (transparent)
    save(wd, "wordmark-dark.png")    # for dark backgrounds (transparent)

    print("banners…")
    save(banner(1500, 500, "bluesky"),  "banner-1500x500.png")
    save(banner(1584, 396, "linkedin"), "banner-linkedin-1584x396.png")

    print("vector…")
    write_mark_svg()
    print("  • mark-A.svg (+ on-ink / on-blue)")

    # preview montage
    print("preview…")
    pv = Image.new("RGB", (1600, 1180), (222, 224, 228))
    av = [Image.open(os.path.join(DIST, f)) for f in
          ("avatar-ink-1000.png", "avatar-blue-1000.png", "avatar-paper-1000.png")]
    for i, a in enumerate(av):
        a = a.resize((360, 360))
        pv.paste(a, (40 + i * 400, 40))
    def band(wm, bg, y):
        b = Image.new("RGB", (1520, 180), bg)
        fit = min(1440 / wm.width, 150 / wm.height)
        r = wm.resize((int(wm.width * fit), int(wm.height * fit)), Image.LANCZOS)
        b.paste(r, (40, (180 - r.height) // 2), r)
        pv.paste(b, (40, y))
    band(wl, PAPER, 440)
    band(wd, INK, 640)
    bn = Image.open(os.path.join(DIST, "banner-1500x500.png")).resize((1520, 300))
    pv.paste(bn, (40, 850))
    pv.save(os.path.join(DIST, "_preview.png"))
    print("  • _preview.png")

if __name__ == "__main__":
    main()
