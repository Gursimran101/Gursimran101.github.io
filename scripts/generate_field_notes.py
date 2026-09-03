#!/usr/bin/env python3
"""Rubber-stamp travel field-notes poster.

Composes a 4:3 poster: the left 58% is a photo with restrained grading and a
whisper of film grain; the right 42% is warm aged paper carrying a small
multi-colour rubber stamp of the scene and a few lines of typewriter text.

Example (web-sized JPEG):
  python3 scripts/generate_field_notes.py \
      --source assets/source/golden-gate-misty.jpg \
      --out assets/statement/golden-gate-field-notes.jpg --out-width 1800

Needs Pillow, NumPy and SciPy, plus the macOS American Typewriter font.
"""

import argparse
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

W, H = 2400, 1800          # 4:3 poster
SPLIT = 0.58               # photo share of the width
S = 2                      # supersampling for stamp and text
PX_PER_MM = W / 297.0      # treat the sheet as A4-ish for "1-2 mm" offsets
FONT = "/System/Library/Fonts/Supplemental/AmericanTypewriter.ttc"

INKS = {                   # desaturated spot inks pulled from the photo
    "slate": ((92, 110, 128), 0.60),
    "taupe": ((112, 98, 78), 0.84),
    "red": ((150, 72, 56), 0.93),
}
TEXT_INK = (48, 44, 42)


# ----------------------------------------------------------------- noise ---
def value_noise(shape, cell, rng):
    h, w = shape
    gh, gw = max(2, math.ceil(h / cell) + 1), max(2, math.ceil(w / cell) + 1)
    g = rng.random((gh, gw)).astype(np.float32)
    return np.asarray(Image.fromarray(g).resize((w, h), Image.BICUBIC), np.float32)


def fractal(shape, cell, rng, octaves=4, persistence=0.5):
    out = np.zeros(shape, np.float32)
    amp, total = 1.0, 0.0
    for _ in range(octaves):
        out += amp * value_noise(shape, cell, rng)
        total += amp
        amp *= persistence
        cell = max(2, cell / 2)
    out /= total
    lo, hi = np.percentile(out, [0.5, 99.5])
    return np.clip((out - lo) / max(hi - lo, 1e-6), 0, 1)


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


# ----------------------------------------------------------------- paper ---
def make_paper(w, h, rng):
    base = np.array([239, 231, 212], np.float32)
    mottle = fractal((h, w), 260, rng, octaves=4) - 0.5
    fine = fractal((h, w), 6, rng, octaves=2) - 0.5
    grain = ndimage.gaussian_filter(rng.standard_normal((h, w)).astype(np.float32), 0.5)
    tone = 1.0 + 0.028 * mottle + 0.03 * fine + 0.010 * grain
    paper = base[None, None, :] * tone[:, :, None]
    warm = fractal((h, w), 400, rng, octaves=2) - 0.5
    paper[:, :, 2] *= 1.0 - 0.03 * warm
    paper[:, :, 0] *= 1.0 + 0.010 * warm

    # short fibres, some darker and some lighter than the sheet
    for sign, alpha in ((-1, 0.10), (1, 0.08)):
        fib = Image.new("L", (w, h), 0)
        d = ImageDraw.Draw(fib)
        for _ in range(int(w * h / 9000)):
            x, y = rng.uniform(0, w), rng.uniform(0, h)
            ang, length = rng.uniform(0, math.pi), rng.uniform(6, 34)
            mx = x + 0.5 * length * math.cos(ang) + rng.normal(0, 1.2)
            my = y + 0.5 * length * math.sin(ang) + rng.normal(0, 1.2)
            end = (x + length * math.cos(ang), y + length * math.sin(ang))
            d.line([(x, y), (mx, my), end], fill=int(rng.uniform(90, 255)), width=1)
        f = ndimage.gaussian_filter(np.asarray(fib, np.float32) / 255.0, 0.35)
        paper *= (1.0 + sign * alpha * f)[:, :, None]

    # faint usage marks: ragged foxing blotches
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    marks = np.zeros((h, w), np.float32)
    for _ in range(int(rng.integers(3, 6))):
        cx, cy, r = rng.uniform(0, w), rng.uniform(0, h), rng.uniform(30, 110)
        blob = np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r)))
        marks += blob * fractal((h, w), 40, rng, octaves=2) * rng.uniform(0.4, 1.0)
    marks = np.clip(marks, 0, 1)
    paper *= 1.0 - marks[:, :, None] * np.array([0.015, 0.03, 0.06], np.float32)

    # soft vignette
    vx = np.minimum(xx, w - 1 - xx) / w
    vy = np.minimum(yy, h - 1 - yy) / h
    v = np.clip(np.minimum(vx, vy) / 0.12, 0, 1)
    paper *= (0.965 + 0.035 * v)[:, :, None]
    return np.clip(paper, 0, 255)


# ----------------------------------------------------------------- photo ---
def prepare_photo(src, pw, ph, crop_x, rng):
    im = Image.open(src).convert("RGB")
    sw, sh = im.size
    aspect = pw / ph
    cw, ch = min(sw, int(round(sh * aspect))), sh
    if cw == sw:
        ch = int(round(sw / aspect))
    x0 = int(round(crop_x * (sw - cw)))
    y0 = (sh - ch) // 2
    im = im.crop((x0, y0, x0 + cw, y0 + ch)).resize((pw, ph), Image.LANCZOS)

    a = np.asarray(im, np.float32) / 255.0
    lum = a @ np.array([0.299, 0.587, 0.114], np.float32)
    a = a * 0.90 + lum[..., None] * 0.10                 # ease saturation
    a = 0.025 + a * 0.955                                # lift blacks, soften whites
    a = 0.5 + (a - 0.5) * 1.04                           # a touch of contrast
    a = a + (lum[..., None] ** 2) * np.array([0.010, 0.004, -0.010], np.float32)
    grain = ndimage.gaussian_filter(rng.standard_normal(lum.shape).astype(np.float32), 0.45)
    a = a + 0.011 * grain[..., None]                     # fine film grain
    return np.clip(a, 0, 1) * 255


# ----------------------------------------------------------------- stamp ---
def bezier(p0, p1, p2, n=80):
    t = np.linspace(0, 1, n)
    x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
    y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
    return list(zip(x, y))


def draw_stamp_layers(bw, bh, pad):
    """Clean masks (one per ink) of the compressed scene, in a padded canvas."""
    cw, ch = bw + 2 * pad, bh + 2 * pad

    def P(x, y):
        return (pad + x * bw, pad + y * bh)

    layers = {}

    # slate: far shoreline and a few intermittent ripples
    L = Image.new("L", (cw, ch), 0)
    d = ImageDraw.Draw(L)
    shore = [P(0.0, 0.735), P(0.0, 0.712), P(0.06, 0.694), P(0.14, 0.686),
             P(0.22, 0.690), P(0.30, 0.703), P(0.38, 0.720), P(0.44, 0.735)]
    d.polygon(shore, fill=255)
    for xa, xb, y in [(0.04, 0.17, 0.845), (0.23, 0.31, 0.86), (0.09, 0.19, 0.90),
                      (0.30, 0.40, 0.915), (0.16, 0.26, 0.955)]:
        d.line([P(xa, y), P(xb, y)], fill=255, width=max(2, int(0.007 * bw)))
    layers["slate"] = L

    # taupe: the Marin headland
    L = Image.new("L", (cw, ch), 0)
    d = ImageDraw.Draw(L)
    hill = [P(0.60, 0.815), P(0.60, 0.80), P(0.64, 0.735), P(0.69, 0.70),
            P(0.735, 0.645), P(0.79, 0.60), P(0.85, 0.585), P(0.91, 0.565),
            P(0.96, 0.57), P(1.0, 0.585), P(1.0, 0.90)]
    d.polygon(hill, fill=255)
    layers["taupe"] = L

    # red: tower, cables, deck, sparse suspenders
    L = Image.new("L", (cw, ch), 0)
    d = ImageDraw.Draw(L)
    cx, top, base = 0.50, 0.10, 0.745
    for side in (-1, 1):
        xt, xb = cx + side * 0.060, cx + side * 0.074
        wt, wb = 0.026, 0.034
        d.polygon([P(xt - wt / 2, top), P(xt + wt / 2, top),
                   P(xb + wb / 2, base), P(xb - wb / 2, base)], fill=255)
    for y, t in [(0.10, 0.030), (0.215, 0.034), (0.345, 0.036), (0.48, 0.038), (0.62, 0.040)]:
        f = (y - top) / (base - top)
        half = (0.060 + 0.014 * f) + (0.026 + 0.008 * f) / 2
        d.rectangle([P(cx - half, y), P(cx + half, y + t)], fill=255)
    deck = [P(0.10, 0.742), P(0.50, 0.735), P(0.99, 0.80),
            P(0.99, 0.885), P(0.50, 0.775), P(0.10, 0.760)]
    d.polygon(deck, fill=255)
    cable_w = max(2, int(0.011 * bw))
    near = bezier((0.545, 0.112), (0.74, 0.40), (1.02, 0.56))
    far = bezier((0.455, 0.112), (0.22, 0.44), (-0.02, 0.66))
    d.line([P(*q) for q in near], fill=255, width=cable_w, joint="curve")
    d.line([P(*q) for q in far], fill=255, width=int(cable_w * 0.8), joint="curve")

    def cable_y(curve, x):
        return min(curve, key=lambda q: abs(q[0] - x))[1]

    for x in (0.64, 0.75, 0.86, 0.95):
        d.line([P(x, cable_y(near, x)), P(x, 0.735 + (x - 0.5) * 0.13)],
               fill=255, width=max(2, int(0.0045 * bw)))
    for x in (0.36, 0.27, 0.18):
        d.line([P(x, cable_y(far, x)), P(x, 0.742)], fill=255, width=max(2, int(0.004 * bw)))
    layers["red"] = L
    return layers


def stampify(mask, rng, dropout=0.42, wobble=2.0, notch=0.58, ghost=0.14):
    """Turn a clean mask into a hand-stamped impression."""
    h, w = mask.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dx = (fractal((h, w), 28 * S, rng, octaves=3) - 0.5) * 2 * wobble * S
    dy = (fractal((h, w), 28 * S, rng, octaves=3) - 0.5) * 2 * wobble * S
    m = ndimage.map_coordinates(mask, [yy + dy, xx + dx], order=1, mode="constant", cval=0.0)

    # carving notches and fractured edges along the contours
    k = int(2.5 * S) | 1
    edge = np.clip(m - ndimage.grey_erosion(m, size=(k, k)), 0, 1)
    m = np.clip(m - edge * (fractal((h, w), 5 * S, rng, octaves=2) > notch), 0, 1)

    # uneven line width: thinner patches
    k2 = int(1.5 * S) | 1
    thin = ndimage.grey_erosion(m, size=(k2, k2))
    m = np.where(fractal((h, w), 40 * S, rng, octaves=2) > 0.62, thin, m)

    # hand-engraving marks: thin scratches with a loosely shared tool direction
    sc = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(sc)
    for _ in range(int(w * h / (1500 * S * S))):
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        ang, length = rng.normal(-0.35, 0.3), rng.uniform(6, 26) * S
        d.line([(x, y), (x + length * math.cos(ang), y + length * math.sin(ang))],
               fill=int(rng.uniform(120, 255)), width=max(1, int(0.6 * S)))
    m *= 1.0 - 0.75 * np.asarray(sc, np.float32) / 255.0

    # granular ink with hard paper show-through, dry patches, uneven pressure
    speck = ndimage.gaussian_filter(rng.random((h, w)).astype(np.float32), 0.7 * S)
    speck = (speck - speck.min()) / (speck.max() - speck.min() + 1e-6)
    dry = fractal((h, w), 90 * S, rng, octaves=3)
    press = fractal((h, w), 400 * S, rng, octaves=1)
    ink = 0.55 * speck + 0.30 * dry + 0.15 * press
    cov = smoothstep(dropout - 0.05, dropout + 0.07, ink)
    out = m * (0.10 + 0.90 * cov)
    out *= np.where(dry < 0.20, 0.35, 1.0)

    # partial ghost impression, slightly offset
    gdx, gdy = int(rng.uniform(2.5, 5) * S), int(rng.uniform(1, 3) * S)
    g = np.roll(np.roll(m * cov, gdy, 0), gdx, 1) * ghost
    out = np.clip(out + g * (1 - out), 0, 1)
    return ndimage.gaussian_filter(out, 0.22 * S)


def misregister(cov, rng):
    """Small per-colour offset and rotation, as separately pressed blocks."""
    ang = rng.uniform(-0.5, 0.5)
    dist = rng.uniform(0.5, 1.2) * PX_PER_MM * S
    th = rng.uniform(0, 2 * math.pi)
    cov = ndimage.rotate(cov, ang, reshape=False, order=1)
    return ndimage.shift(cov, (dist * math.sin(th), dist * math.cos(th)), order=1)


def downsample(a, w, h):
    return np.clip(np.asarray(Image.fromarray(a.astype(np.float32)).resize((w, h), Image.LANCZOS), np.float32), 0, 1)


def multiply_ink(region, alpha, color):
    c = np.array(color, np.float32) / 255.0
    region *= 1.0 - alpha[..., None] * (1.0 - c)


# ------------------------------------------------------------------ text ---
def typewriter_text(lines, font_path, size, rng):
    font = ImageFont.truetype(font_path, size * S)
    line_h = int(size * S * 1.45)
    w = int(max(font.getlength(l) for l in lines) * 1.12) + 40 * S
    h = line_h * len(lines) + 20 * S
    mask = Image.new("L", (w, h), 0)
    y = 10 * S
    for line in lines:
        x = 10 * S
        for ch in line:
            adv = font.getlength(ch)
            if ch != " ":
                gw, gh = int(adv) + 16 * S, line_h + 8 * S
                glyph = Image.new("L", (gw, gh), 0)
                ImageDraw.Draw(glyph).text((8 * S, 4 * S), ch, font=font, fill=int(rng.uniform(185, 255)))
                glyph = glyph.rotate(rng.normal(0, 1.3), resample=Image.BICUBIC,
                                     center=(8 * S + adv / 2, 4 * S + size * S * 0.6))
                px = int(x - 8 * S + rng.normal(0, 0.9 * S))
                py = int(y - 4 * S + rng.normal(0, 1.1 * S))
                if rng.random() < 0.12:                       # occasional double strike
                    faint = glyph.point(lambda v: int(v * 0.35))
                    mask.paste(faint, (px + int(1.5 * S), py + S), faint)
                mask.paste(glyph, (px, py), glyph)
            x += adv * (1 + rng.normal(0, 0.012))
        y += line_h
    m = np.asarray(mask, np.float32) / 255.0
    tex = fractal(m.shape, 3 * S, rng, octaves=2)            # ribbon texture
    m *= 0.55 + 0.45 * np.clip((tex - 0.25) / 0.5, 0, 1)
    return np.clip(ndimage.gaussian_filter(m, 0.45 * S), 0, 1)


# ------------------------------------------------------------------ main ---
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--crop-x", type=float, default=0.83, help="horizontal crop position, 0 = left, 1 = right")
    ap.add_argument("--font", default=FONT)
    ap.add_argument("--text-size", type=int, default=24)
    ap.add_argument("--title", default="GOLDEN GATE BRIDGE")
    ap.add_argument("--place", default="San Francisco, California")
    ap.add_argument("--number", default="No. 001")
    ap.add_argument("--keywords", default="FOG · STEEL · STRAIT")
    ap.add_argument("--year", default="2026")
    ap.add_argument("--out-width", type=int, default=None, help="resize the finished poster to this width (e.g. 1800 for the web)")
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    pw = int(round(W * SPLIT))
    photo = prepare_photo(args.source, pw, H, args.crop_x, rng)
    paper = make_paper(W, H, rng)
    canvas = paper.copy()
    canvas[:, :pw] = photo * (0.94 + 0.06 * paper[:, :pw] / 255.0)   # one sheet, one surface

    # stamp block: lower-middle of the paper, about a third of its height
    panel_w = W - pw
    sh = int(round(H * 0.335))
    sw = int(round(sh * 1.25))
    pad = int(round(0.06 * sw))
    box_x = pw + (panel_w - sw) // 2
    box_y = int(round(H * 0.455))
    layers = draw_stamp_layers(sw * S, sh * S, pad * S)
    region = canvas[box_y - pad:box_y + sh + pad, box_x - pad:box_x + sw + pad]
    ch, cw = region.shape[:2]
    for name in ("slate", "taupe", "red"):
        cov = stampify(np.asarray(layers[name], np.float32) / 255.0, rng)
        if name == "red":                                     # far span dissolves into mist
            xs = (np.arange(cov.shape[1], dtype=np.float32) - pad * S) / (sw * S)
            ys = (np.arange(cov.shape[0], dtype=np.float32) - pad * S) / (sh * S)
            cov *= smoothstep(0.06, 0.42, xs)[None, :]
            cov *= (0.78 + 0.22 * smoothstep(0.06, 0.32, ys))[:, None]
        cov = misregister(cov, rng)
        color, opacity = INKS[name]
        multiply_ink(region, downsample(cov, cw, ch) * opacity, color)

    # typewriter caption below the stamp
    lines = [args.title, args.place, args.number, args.keywords, args.year]
    tm = typewriter_text(lines, args.font, args.text_size, rng)
    th, tw = tm.shape[0] // S, tm.shape[1] // S
    tx = box_x + int(sw * 0.05)
    ty = box_y + sh + int(H * 0.025)
    tregion = canvas[ty:ty + th, tx:tx + tw]
    multiply_ink(tregion, downsample(tm, tw, th)[:tregion.shape[0], :tregion.shape[1]] * 0.92, TEXT_INK)

    out = Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8))
    if args.out_width and args.out_width != W:
        out = out.resize((args.out_width, int(round(args.out_width * H / W))), Image.LANCZOS)
    jpeg = args.out.lower().endswith((".jpg", ".jpeg"))
    out.save(args.out, **({"quality": 90, "subsampling": 0, "optimize": True} if jpeg else {}))
    print("wrote", args.out, f"{out.size[0]}x{out.size[1]}")


if __name__ == "__main__":
    main()
