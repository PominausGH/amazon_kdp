"""Colour in a black & white line-art page for marketing previews (back cover, A+).
The printed interior stays black & white; this only shows buyers what a finished page looks like."""
from __future__ import annotations

import io
import random
from pathlib import Path

from PIL import Image, ImageDraw

PALETTE = [(230, 57, 70), (85, 194, 113), (255, 217, 61), (77, 150, 255), (255, 164, 91),
           (255, 143, 171), (155, 140, 255), (160, 82, 45), (107, 203, 239)]
BG = (255, 255, 254)  # near-white marker for the page background so it stays white


def colourise(png: Path, seed: int = 7, width: int = 900) -> bytes:
    im = Image.open(png).convert("L")
    im = im.resize((width, round(im.height * width / im.width)))
    im = im.point(lambda v: 255 if v > 128 else 0).convert("RGB")
    W, H = im.size
    # background: flood from every border pixel that is still white
    for x in range(0, W, 7):
        for y in (0, H - 1):
            if im.getpixel((x, y)) == (255, 255, 255):
                ImageDraw.floodfill(im, (x, y), BG)
    for y in range(0, H, 7):
        for x in (0, W - 1):
            if im.getpixel((x, y)) == (255, 255, 255):
                ImageDraw.floodfill(im, (x, y), BG)
    rng = random.Random(seed)
    step = max(6, W // 90)
    for y in range(step // 2, H, step):
        for x in range(step // 2, W, step):
            if im.getpixel((x, y)) == (255, 255, 255):
                ImageDraw.floodfill(im, (x, y), rng.choice(PALETTE))
    # anything left near-white (outside) back to pure white
    px = im.load()
    for y in range(H):
        for x in range(W):
            if px[x, y] == BG:
                px[x, y] = (255, 255, 255)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return buf.getvalue()
