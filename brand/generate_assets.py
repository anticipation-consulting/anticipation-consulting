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
COPPER    = (181, 120, 63)    # logo triad — copper node  (assets/site.js)
GREEN     = (47, 125, 84)     # logo triad — green node
LOGO_TRI  = [BLUE, COPPER, GREEN]  # fixed node palette, independent of theme

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

# ---- interactive network background (faithful port of assets/site.js) -------
def _lerp(c0, c1, t):
    return (round(c0[0] + (c1[0] - c0[0]) * t),
            round(c0[1] + (c1[1] - c0[1]) * t),
            round(c0[2] + (c1[2] - c0[2]) * t))

def network_rgba(w, h, seed=11, ground=None, ss=SS):
    """A still frame of the site's #net-bg canvas (assets/site.js), rendered at
    `ss` supersample. Triangle nodes in the logo triad, joined by gradient links
    whose opacity fades with distance. `w`,`h` are logical (CSS) pixels; pass a
    `ground` colour for an opaque field, or None for a transparent layer."""
    rng = random.Random(seed)
    # node count mirrors seedNodes(): round(area / 12500), clamped to [44, 170]
    n = max(44, min(round(w * h / 12500), 170))
    nodes = [{
        "x": rng.random() * w, "y": rng.random() * h,
        "r": 1.1 + rng.random() * 1.9,
        "big": rng.random() > 0.9,
        "col": LOGO_TRI[int(rng.random() * 3)],
        "flip": rng.random() > 0.5,
    } for _ in range(n)]

    W, H = w * ss, h * ss
    base = Image.new("RGBA", (W, H),
                     (ground + (255,)) if ground else (0, 0, 0, 0))

    # links — each on its own tile so crossings composite (source-over) correctly
    links = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    LINK = 124.0                 # px link radius, matches the live canvas
    seg = max(2, int(round(7 * ss)))
    for i in range(n):
        a = nodes[i]
        for j in range(i + 1, n):
            b = nodes[j]
            d = math.hypot(a["x"] - b["x"], a["y"] - b["y"])
            if d >= LINK:
                continue
            alpha = round((1 - d / LINK) * 0.42 * 255)
            if alpha < 1:
                continue
            ax, ay, bx, by = a["x"] * ss, a["y"] * ss, b["x"] * ss, b["y"] * ss
            x0, y0 = int(min(ax, bx)) - ss, int(min(ay, by)) - ss
            x1, y1 = int(max(ax, bx)) + ss, int(max(ay, by)) + ss
            tile = Image.new("RGBA", (max(1, x1 - x0), max(1, y1 - y0)), (0, 0, 0, 0))
            dt = ImageDraw.Draw(tile)
            length = math.hypot(bx - ax, by - ay)
            steps = max(2, int(length / seg))
            for k in range(steps):
                t0, t1 = k / steps, (k + 1) / steps
                col = _lerp(a["col"], b["col"], (t0 + t1) / 2)
                dt.line([(ax + (bx - ax) * t0 - x0, ay + (by - ay) * t0 - y0),
                         (ax + (bx - ax) * t1 - x0, ay + (by - ay) * t1 - y0)],
                        fill=col + (alpha,), width=ss)
            links.alpha_composite(tile, (x0, y0))
    base.alpha_composite(links)

    # nodes drawn last — small triangles, flipped half the time (triPath in JS)
    nlayer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dn = ImageDraw.Draw(nlayer)
    for a in nodes:
        k = -1 if a["flip"] else 1
        rr = ((a["r"] + 1.5) if a["big"] else a["r"]) * 1.75 * ss
        x, y = a["x"] * ss, a["y"] * ss
        dn.polygon([(x, y - rr * k),
                    (x - rr * 0.866, y + rr * 0.5 * k),
                    (x + rr * 0.866, y + rr * 0.5 * k)],
                   fill=a["col"] + (round((0.72 if a["big"] else 0.5) * 255),))
    base.alpha_composite(nlayer)
    return base

def network_bg(w, h, ground, seed=11):
    """Flattened banner-sized PNG of the network background on a solid ground."""
    return network_rgba(w, h, seed=seed, ground=ground, ss=SS) \
        .resize((w, h), Image.LANCZOS).convert("RGB")

# ---- banner -----------------------------------------------------------------
def banner(w, h, name, tagline=True):
    W, H = w * SS, h * SS
    img = network_rgba(w, h, seed=11, ground=INK)   # faithful site #net-bg
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

    print("network backgrounds…")   # banner-sized stills of the live #net-bg
    for bw, bh, tag in [(1500, 500, "1500x500"),
                        (1584, 396, "linkedin-1584x396"),
                        (1280, 640, "1280x640"),
                        (1920, 1080, "1920x1080")]:
        save(network_bg(bw, bh, PAPER, seed=11), "network-bg-%s.png" % tag)
        save(network_bg(bw, bh, INK,   seed=11), "network-bg-%s-ink.png" % tag)

    print("vector…")
    write_mark_svg()
    print("  • mark-A.svg (+ on-ink / on-blue)")

    # preview montage
    print("preview…")
    pv = Image.new("RGB", (1600, 1700), (222, 224, 228))
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
    # network-background stills, paper + ink, side by side
    nbp = Image.open(os.path.join(DIST, "network-bg-1500x500.png")).resize((740, 247))
    nbi = Image.open(os.path.join(DIST, "network-bg-1500x500-ink.png")).resize((740, 247))
    pv.paste(nbp, (40, 1190)); pv.paste(nbi, (820, 1190))
    nbl = Image.open(os.path.join(DIST, "network-bg-1920x1080.png")).resize((1520, 220))
    pv.paste(nbl, (40, 1460))
    pv.save(os.path.join(DIST, "_preview.png"))
    print("  • _preview.png")

if __name__ == "__main__":
    main()
