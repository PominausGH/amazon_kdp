"""Crayon Cove Press brand assets: logo (Author Central photo) and A+ banners.

python -m kdp.brand logo       -> brand/logo-art-N.png options, then brand/logo.png (+ .jpg)
python -m kdp.brand aplus SLUG -> output/SLUG/aplus_970x600.jpg (A+ 'image header' module size)
"""
from __future__ import annotations

import base64
import subprocess
import sys
from pathlib import Path

from .aiart import generate
from .svg import FONT

ROOT = Path(__file__).resolve().parent.parent
BRAND = ROOT / "brand"

LOGO_PROMPT = (
    "A simple, friendly logo emblem for a children's colouring book publisher called Crayon Cove: "
    "three chunky crayons (red, yellow, blue) standing in a little sandy cove with a gentle wave and a small sun, "
    "inside a circle. Flat vector style, bold clean black outlines, bright cheerful colours, white background, "
    "centred, lots of breathing room. Absolutely NO text, letters or numbers. Not a mockup."
)


def logo(n=2):
    BRAND.mkdir(exist_ok=True)
    for i in range(1, n + 1):
        f = BRAND / f"logo-art-{i}.png"
        if not f.exists():
            img, _ = generate(f"{LOGO_PROMPT}\nVariation {i}.", aspect="1:1", size="2K")
            f.write_bytes(img)
        print(f.relative_to(ROOT))


def compose(art: Path, out: Path, size=1200):
    """Emblem on top, name underneath. Square, white background (Author Central photo)."""
    b64 = base64.b64encode(art.read_bytes()).decode()
    s = size
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 {s} {s}">'
           f'<rect width="100%" height="100%" fill="#fff"/>'
           f'<image x="{s*.14}" y="{s*.04}" width="{s*.72}" height="{s*.72}" href="data:image/png;base64,{b64}"/>'
           f'<text x="{s/2}" y="{s*.86}" text-anchor="middle" font-family="{FONT}" font-weight="bold" '
           f'font-size="{s*.105}" fill="#e63946" stroke="#000" stroke-width="{s*.006}" paint-order="stroke">CRAYON COVE</text>'
           f'<text x="{s/2}" y="{s*.95}" text-anchor="middle" font-family="{FONT}" font-weight="bold" '
           f'font-size="{s*.06}" fill="#333" letter-spacing="{s*.012}">PRESS</text></svg>')
    tmp = out.with_suffix(".svg")
    tmp.write_text(svg)
    subprocess.run(["rsvg-convert", "-o", str(out), str(tmp)], check=True)
    subprocess.run(["magick", str(out), "-quality", "92", str(out.with_suffix(".jpg"))], check=True)
    tmp.unlink()


def aplus(slug: str):
    src = ROOT / "output" / slug / "aplus_peek_inside.png"
    out = ROOT / "output" / slug / "aplus_970x600.jpg"
    subprocess.run(["magick", str(src), "-resize", "970x600!", "-quality", "92", str(out)], check=True)
    print(out.relative_to(ROOT))


if __name__ == "__main__":
    if sys.argv[1] == "logo":
        logo()
    elif sys.argv[1] == "compose":
        compose(BRAND / sys.argv[2], BRAND / "logo.png")
        print("brand/logo.png, brand/logo.jpg")
    elif sys.argv[1] == "aplus":
        aplus(sys.argv[2])
