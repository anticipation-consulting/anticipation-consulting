#!/usr/bin/env python3
"""CI guard: prove the committed image artifacts are still in sync with their
generator (brand/generate_assets.py).

Why this exists: images/og-image.png and assets/favicon.svg are *consumed by the
site* but *derived from the brand identity*. When the identity changes, a
hand-maintained copy silently goes stale (which is exactly what happened to the
old OG image). This regenerates every artifact into a throwaway tree and compares
it to what's committed:

  • SVGs        -> exact byte match     (vector text output is deterministic)
  • PNGs        -> identical dimensions + perceptual diff under a tolerance,
                   so cross-runner FreeType anti-aliasing can't cause false drift
  • og-image    -> dimensions must equal the og:image:width/height in head.html

Exit non-zero on any drift, naming the stale file. Run with no arguments:
    python3 brand/check_assets.py
"""
import os, re, sys, tempfile, subprocess
from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PNG_TOLERANCE = 3.0   # max mean abs per-channel diff on a 64x64 thumbnail (0..255).
# Calibration: an identical regen scores 0.0; an identity-scale change (e.g. wrong
# ground colour or wordmark) scores >200. 3.0 leaves wide margin for cross-runner
# font anti-aliasing while still catching a stale-after-redesign artifact.


def repo(*p):
    return os.path.join(ROOT, *p)


def png_drift(a_path, b_path):
    """Return (size_msg | diff_value). None if within tolerance."""
    a = Image.open(a_path).convert("RGB")
    b = Image.open(b_path).convert("RGB")
    if a.size != b.size:
        return f"dimensions {a.size} != regenerated {b.size}"
    ta, tb = a.resize((64, 64)), b.resize((64, 64))
    hist = ImageChops.difference(ta, tb).histogram()   # per-channel value counts
    mean = sum((i % 256) * c for i, c in enumerate(hist)) / (64 * 64 * 3)
    return f"content drift (mean diff {mean:.1f} > {PNG_TOLERANCE})" if mean > PNG_TOLERANCE else None


def main():
    tmp = tempfile.mkdtemp(prefix="brandcheck-")
    dist, images, assets = (os.path.join(tmp, d) for d in ("dist", "images", "assets"))
    env = dict(os.environ, BRAND_DIST=dist, BRAND_IMAGES=images, BRAND_ASSETS=assets)
    print(f"regenerating assets into {tmp} …")
    r = subprocess.run([sys.executable, os.path.join(HERE, "generate_assets.py")],
                       env=env, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout, r.stderr, sep="\n")
        sys.exit("generate_assets.py failed to run")

    # (committed path, freshly generated path) for every artifact the generator emits
    pairs = [(repo("brand", "dist", f), os.path.join(dist, f)) for f in sorted(os.listdir(dist))]
    pairs.append((repo("images", "og-image.png"), os.path.join(images, "og-image.png")))
    pairs.append((repo("assets", "favicon.svg"), os.path.join(assets, "favicon.svg")))

    fails = []
    for committed, fresh in pairs:
        name = os.path.relpath(committed, ROOT)
        if not os.path.exists(committed):
            fails.append(f"{name}: missing from the repo")
        elif committed.endswith(".svg"):
            if open(committed, "rb").read() != open(fresh, "rb").read():
                fails.append(f"{name}: out of date (svg differs)")
        else:
            msg = png_drift(committed, fresh)
            if msg:
                fails.append(f"{name}: {msg}")

    # The OG image must match the size the site advertises to crawlers.
    head = open(repo("_includes", "head.html")).read()
    mw = re.search(r'og:image:width"\s+content="(\d+)"', head)
    mh = re.search(r'og:image:height"\s+content="(\d+)"', head)
    og = repo("images", "og-image.png")
    if mw and mh and os.path.exists(og):
        declared = (int(mw.group(1)), int(mh.group(1)))
        actual = Image.open(og).size
        if actual != declared:
            fails.append(f"images/og-image.png is {actual} but head.html declares {declared}")

    if fails:
        print("\nBRAND / SITE ASSETS ARE OUT OF SYNC WITH THE GENERATOR:")
        for f in fails:
            print("  ✗", f)
        print("\nFix:  python3 brand/generate_assets.py   then commit the result.")
        sys.exit(1)
    print(f"✓ {len(pairs)} artifacts match the generator")


if __name__ == "__main__":
    main()
