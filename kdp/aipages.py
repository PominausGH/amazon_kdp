"""AI-drawn interior colouring pages, cleaned to pure black & white.

Usage: python -m kdp.aipages books/foo.json [--only 4] [--jobs 4]
Reads every section with "type": "ai_pages" and makes one image per subject in
art/<slug>/pages/. Existing images are kept, so re-runs only fill gaps and a
bad page can be redone by deleting its file.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .aiart import generate

ROOT = Path(__file__).resolve().parent.parent

PAGE_STYLE = (
    "A black and white colouring page for toddlers and preschoolers (ages 2-5), bold and easy style. "
    "Subject: {subject}. "
    "Rules: very thick, bold, clean, smooth black outlines of even weight; large simple rounded shapes; "
    "big open white areas that are easy to colour; every shape fully closed; cute friendly look. "
    "Pure white background with at most {background}. "
    "NO shading, NO grey, NO gradients, NO hatching, NO texture, NO filled black areas except small eyes. "
    "NO text, NO letters, NO numbers, NO border, NO frame. Not a photo or mockup: just the flat line art. "
    "Single centred subject that fills most of the square frame."
)


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def page_path(book_slug: str, idx: int, subject: str) -> Path:
    return ROOT / "art" / book_slug / "pages" / f"{idx:02d}-{slugify(subject)[:40]}.png"


def clean_bw(raw: Path, out: Path):
    """Greyscale -> hard threshold -> pure 1-bit black/white, trimmed with margin."""
    subprocess.run(["magick", str(raw), "-colorspace", "gray", "-threshold", "55%",
                    "-bordercolor", "white", "-border", "1", "-trim", "+repage",
                    "-bordercolor", "white", "-border", "20", "-type", "bilevel", str(out)], check=True)


def make_page(book_slug: str, idx: int, subject: str, size: str, background: str) -> str:
    out = page_path(book_slug, idx, subject)
    if out.exists():
        return f"skip {out.name}"
    out.parent.mkdir(parents=True, exist_ok=True)
    img, model = generate(PAGE_STYLE.format(subject=subject, background=background), aspect="1:1", size=size)
    raw = out.with_suffix(".raw.png")
    raw.write_bytes(img)
    clean_bw(raw, out)
    raw.unlink()
    return f"made {out.name} ({model})"


def subjects(cfg: dict) -> list[str]:
    out = []
    for s in cfg["sections"]:
        if s["type"] == "ai_pages":
            out += [p["subject"] for p in s["pages"]]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("recipe")
    ap.add_argument("--only", type=int, help="generate just the first N (style test)")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--size", default="2K")
    a = ap.parse_args()
    recipe = Path(a.recipe)
    cfg = json.loads(recipe.read_text())
    subs = subjects(cfg)[: a.only]
    background = cfg.get("page_background", "a simple ground line and one or two small simple details")
    with ThreadPoolExecutor(a.jobs) as ex:
        futs = {ex.submit(make_page, recipe.stem, i, s, a.size, background): s for i, s in enumerate(subs, 1)}
        for f in as_completed(futs):
            try:
                print(f.result(), flush=True)
            except Exception as e:  # report and carry on; re-run fills the gap
                print(f"FAILED {futs[f]}: {e}", flush=True)


if __name__ == "__main__":
    main()
