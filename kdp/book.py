"""Build a KDP-ready paperback from a JSON recipe: interior PDF, cover PDF,
listing metadata and preview PNGs. Usage: python -m kdp.book books/foo.json"""
from __future__ import annotations

import base64
import json
import math
import random
import shutil
import subprocess
import sys
from pathlib import Path
from xml.sax.saxutils import escape

from . import specs
from .gen import bold, dots, mandala, maze, sudoku, wordsearch
from .svg import FONT, Page, fit, group

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"


# ---------- interior ----------

def outlined_label(page: Page, x, y, s, size):
    """Big hollow letters the child can colour in too."""
    page.text(x, y, s, size=size, fill="#fff",
              extra='stroke="#000" stroke-width="2.6" stroke-linejoin="round" paint-order="stroke"')


def page_number(page: Page, n: int):
    page.text(page.w / 2, page.h - 0.38 * specs.PT, str(n), size=10, weight="normal")


class Builder:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.trim = cfg.get("trim", "8.5x11")
        self.w_in, self.h_in = specs.TRIMS[self.trim]
        self.rng = random.Random(cfg.get("seed", 1))
        self.pages: list[Page] = []
        self.solutions: list[tuple[str, callable]] = []  # deferred solution drawers
        self.cover_art: list[str] = []  # coloured snippets in a 400x400 box for the cover
        self.colour_samples: list[Page] = []  # coloured-in copies of colouring pages (previews only)

    def new(self) -> Page:
        p = Page(self.w_in, self.h_in)
        self.pages.append(p)
        return p

    def blank_back(self):
        p = self.new()
        p.text(p.w / 2, p.h / 2, "This page is left blank so colours don't bleed through.",
               size=9, weight="normal", fill="#999")

    # Front matter
    def front_matter(self):
        c = self.cfg
        p = self.new()
        x, y, w, h = p.safe
        ty = y + h * .25
        for line in c.get("title_lines", [c["title"]]):
            p.text(p.w / 2, ty, line, size=40)
            ty += 46
        for line in _wrap(c.get("inner_subtitle", c.get("subtitle", "")), 60):
            p.text(p.w / 2, ty + 10, line, size=15, weight="normal")
            ty += 20
        if c.get("author"):
            p.text(p.w / 2, ty + 50, c["author"], size=13, weight="normal")
        p = self.new()  # copyright page (verso)
        p.text(p.w / 2, p.h - 2.2 * specs.PT, f"© {c.get('year', 2026)} {c.get('author', '')}. All rights reserved.",
               size=9, weight="normal")
        p.text(p.w / 2, p.h - 2.2 * specs.PT + 14,
               "No part of this book may be reproduced without written permission from the publisher.",
               size=8, weight="normal")
        p = self.new()  # belongs-to page
        x, y, w, h = p.safe
        p.add(f'<rect x="{x + 30:.1f}" y="{y + h * .25:.1f}" width="{w - 60:.1f}" height="{h * .4:.1f}" rx="28" '
              f'fill="none" stroke="#000" stroke-width="5"/>')
        outlined_label(p, p.w / 2, y + h * .38, "THIS BOOK", 46)
        outlined_label(p, p.w / 2, y + h * .46, "BELONGS TO", 46)
        p.add(f'<line x1="{x + 80:.1f}" y1="{y + h * .58:.1f}" x2="{x + w - 80:.1f}" y2="{y + h * .58:.1f}" '
              f'stroke="#000" stroke-width="2.5" stroke-dasharray="2,8" stroke-linecap="round"/>')
        self.new()  # blank verso so content starts on a right-hand page

    # Sections
    def section_bold(self, s):
        names = []
        for t in s["themes"]:
            names += bold.THEMES[t]
        names = list(dict.fromkeys(names))
        for i, name in enumerate(names):
            p = self.new()
            x, y, w, h = p.safe
            art_h = h - 80
            p.add(fit(bold.draw(name, stroke=s.get("stroke", 8)), 400, 400, x, y, w, art_h))
            outlined_label(p, p.w / 2, y + h - 18, name, 54 if len(name) < 11 else 42)
            if s.get("single_sided", True):
                self.blank_back()
        # Cover picks: config "cover_items" = [[NAME, {a:..,b:..}], ...] or first four.
        picks = self.cfg.get("cover_items") or [[n, bold.PALETTES[i % 3]] for i, n in enumerate(names[:4])]
        for name, pal in picks:
            full = dict(bold.PALETTES[0])
            full.update(pal)
            self.cover_art.append(bold.draw(name, 8, full))

    def section_ai_pages(self, s):
        """AI line art from art/<slug>/pages/ (made by `python -m kdp.aipages`)."""
        from .aipages import page_path
        src = s.get("from_slug", self.slug)  # reuse another book's pages
        missing = []
        for i, pg in enumerate(s["pages"], 1):
            f = page_path(src, pg.get("idx", i), pg["subject"])
            if not f.exists():
                missing.append(f.name)
                continue
            p = self.new()
            x, y, w, h = p.safe
            png = subprocess.run(["magick", str(f), "-type", "bilevel", "png:-"], capture_output=True, check=True).stdout
            # Toddler/kids pages get a big hollow word label; detailed/cozy pages use the whole page.
            labelled = s.get("style", "toddler") in ("toddler", "kids")
            art_h = h - 80 if labelled else h
            p.add(f'<image x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{art_h:.1f}" '
                  f'preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,{base64.b64encode(png).decode()}"/>')
            if labelled:
                label = pg["label"]
                outlined_label(p, p.w / 2, y + h - 18, label, 54 if len(label) < 11 else 42 if len(label) < 15 else 34)
            if i in s.get("coloured_samples", []):
                # preview-only copy of this page, coloured in, for the back cover and A+ image
                from .colourise import colourise
                cp = Page(self.w_in, self.h_in)
                cpng = base64.b64encode(colourise(f, seed=i)).decode()
                cp.add(f'<image x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{art_h:.1f}" '
                       f'preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,{cpng}"/>')
                if labelled:
                    outlined_label(cp, cp.w / 2, y + h - 18, label, 54 if len(label) < 11 else 42 if len(label) < 15 else 34)
                self.colour_samples.append(cp)
            if s.get("single_sided", True):
                self.blank_back()
        if missing:
            raise SystemExit(f"{len(missing)} AI pages missing (run python -m kdp.aipages): {missing[:5]}...")

    def section_mandala(self, s):
        for i in range(s["count"]):
            p = self.new()
            x, y, w, h = p.safe
            seed = self.rng.random()
            R = min(w, h) / 2 - 6
            art = mandala.mandala_svg(random.Random(seed), R=R, complexity=s.get("complexity", .3),
                                      stroke=s.get("stroke", 3.2))
            p.add(group(art, x + w / 2, y + h / 2))
            if s.get("single_sided", True):
                self.blank_back()
            if i < 1:
                pal = ["#ff6b6b", "#ffd93d", "#6bcbef", "#55c271", "#9b8cff", "#ffa45b", "#ff8fab"]
                self.cover_art.append(group(mandala.mandala_svg(
                    random.Random(seed), R=190, complexity=s.get("complexity", .3), stroke=2.4,
                    fill_cb=lambda k: pal[k % len(pal)]), 200, 200))

    def _titled(self, label: str) -> Page:
        p = self.new()
        x, y, w, h = p.safe
        outlined_label(p, p.w / 2, y + 30, label, 32)
        return p

    def section_maze(self, s):
        n = 0
        for level in s["levels"]:
            for _ in range(level["count"]):
                n += 1
                m = maze.Maze(level["cols"], level["rows"], self.rng)
                p = self._titled(f"MAZE {n}")
                x, y, w, h = p.safe
                body, mw, mh = m.svg(w - 20, h - 110, stroke=level.get("stroke", 3.5))
                ox, oy = x + (w - mw) / 2, y + 60 + (h - 110 - mh) / 2
                p.add(group(body, ox, oy))
                p.text(ox + 8, oy - 10, "START", size=13, anchor="start")
                p.text(ox + mw - 8, oy + mh + 22, "FINISH", size=13, anchor="end")
                self.solutions.append((f"Maze {n}", lambda bw, bh, m=m, st=level.get("stroke", 3.5):
                                       m.svg(bw, bh, stroke=st * .6, solution=True)))
                if n == 1:
                    sv, mw2, mh2 = m.svg(360, 360, stroke=6)
                    self.cover_art.append(group(sv, (400 - mw2) / 2, (400 - mh2) / 2))

    def section_wordsearch(self, s):
        for i, puzzle in enumerate(s["puzzles"], start=1):
            ws = wordsearch.WordSearch(puzzle["words"], s.get("size", 12), self.rng, diagonal=s.get("diagonal", False))
            p = self._titled(puzzle["title"].upper())
            x, y, w, h = p.safe
            box = min(w - 20, h * .66)
            ox = x + (w - box) / 2
            p.add(group(ws.svg(box), ox, y + 60))
            # word list in columns
            cols = 3
            words = ws.words
            per = math.ceil(len(words) / cols)
            for k, wd in enumerate(words):
                cx = x + w * (k // per + .5) / cols
                cy = y + 60 + box + 40 + (k % per) * 24
                p.add(f'<rect x="{cx - 70:.1f}" y="{cy - 13:.1f}" width="14" height="14" rx="3" fill="none" stroke="#000" stroke-width="1.6"/>')
                p.text(cx - 48, cy - 1, wd, size=15, anchor="start")
            self.solutions.append((puzzle["title"], lambda bw, bh, ws=ws: (ws.svg(min(bw, bh), True), min(bw, bh), min(bw, bh))))

    def section_dots(self, s):
        for i, shape in enumerate(s["shapes"], start=1):
            p = self._titled(f"DOT TO DOT {i}")
            x, y, w, h = p.safe
            box = min(w, h - 80)
            p.add(group(dots.dot_to_dot(shape, s.get("points", 30), box), x + (w - box) / 2, y + 60))
            self.solutions.append((f"Dot to dot {i}", lambda bw, bh, sh=shape, n=s.get("points", 30):
                                   (dots.dot_to_dot(sh, n, min(bw, bh), solution=True, font=9), min(bw, bh), min(bw, bh))))

    def section_sudoku(self, s):
        for i in range(1, s["count"] + 1):
            pz = sudoku.PictureSudoku(self.rng, blanks=s.get("blanks", 6) + (i - 1) * s.get("step", 0))
            p = self._titled(f"PICTURE SUDOKU {i}")
            x, y, w, h = p.safe
            p.text(p.w / 2, y + 82, "Draw the missing pictures.", size=16, weight="normal")
            p.text(p.w / 2, y + 104, "Every row, column and box has one of each.", size=16, weight="normal")
            box = min(w - 60, h - 260)
            p.add(group(pz.svg(box), x + (w - box) / 2, y + 140))
            # key: the four pictures
            ky = y + 140 + box + 60
            for k in range(4):
                p.add(sudoku.icon(k, x + w * (k + .5) / 4, ky, 56))
            self.solutions.append((f"Picture sudoku {i}", lambda bw, bh, pz=pz: (pz.svg(min(bw, bh), True), min(bw, bh), min(bw, bh))))

    def solution_pages(self):
        if not self.solutions:
            return
        p = self.new()
        outlined_label(p, p.w / 2, p.h / 2, "ANSWERS", 64)
        per_page = 4
        for k in range(0, len(self.solutions), per_page):
            p = self.new()
            x, y, w, h = p.safe
            cw, ch = w / 2, h / 2
            for j, (label, draw) in enumerate(self.solutions[k:k + per_page]):
                cx, cy = x + (j % 2) * cw, y + (j // 2) * ch
                body, bw, bh = draw(cw - 30, ch - 50)
                p.text(cx + cw / 2, cy + 18, label, size=12)
                p.add(group(body, cx + (cw - bw) / 2, cy + 32 + (ch - 50 - bh) / 2))

    def build_interior(self):
        self.front_matter()
        for s in self.cfg["sections"]:
            getattr(self, f"section_{s['type']}")(s)
        self.solution_pages()
        while len(self.pages) < specs.MIN_PAGES or len(self.pages) % 2:
            self.new()
        for n, p in enumerate(self.pages, start=1):
            if n > 4 and len(p.parts) > 1:
                page_number(p, n)

    # ---------- cover ----------

    def sample_pages(self, k: int) -> list[Page]:
        """Representative content pages (skips front matter, blank backs and answers)."""
        content = [pg for pg in self.pages[4:] if len(pg.parts) > 1]
        content = content[: max(1, int(len(content) * .7))]
        if not content:
            return []
        step = max(1, len(content) // k)
        picks = content[::step][:k]
        if self.colour_samples and k >= 3:
            # show a finished, coloured-in page at each end and a puzzle in the middle
            picks = [self.colour_samples[0], content[0], self.colour_samples[-1]] + picks[3:k]
        return picks

    def _front_vector(self, p, c, front_x, fw, fh, bleed, safe, accent):
        # title band
        p.add(f'<rect x="{front_x:.1f}" y="0" width="{fw + bleed:.1f}" height="{bleed + fh * .30:.1f}" fill="{accent}"/>')
        lines = c.get("title_lines", [c["title"]])
        ty = bleed + safe + 52
        for line in lines:
            size = min(64, (fw - 2 * safe) / (len(line) * .74))
            p.text(front_x + fw / 2, ty, line.upper(), size=size, fill="#fff",
                   extra='stroke="#000" stroke-width="4" paint-order="stroke" stroke-linejoin="round"')
            ty += size * 1.02
        cover_sub = c.get("cover_subtitle", c.get("subtitle", ""))
        if cover_sub:
            size = min(22, (fw - 2 * safe) / (len(cover_sub) * .56))
            p.text(front_x + fw / 2, bleed + fh * .30 + 34, cover_sub, size=size, fill="#222")
        # artwork grid
        art = self.cover_art[:4] or []
        gx, gy, gw, gh = front_x + safe, bleed + fh * .30 + 55, fw - 2 * safe, fh * .70 - 55 - safe - 50
        if len(art) >= 4:
            for i, a in enumerate(art):
                cx, cy = gx + (i % 2) * gw / 2, gy + (i // 2) * gh / 2
                p.add(f'<rect x="{cx + 6:.1f}" y="{cy + 6:.1f}" width="{gw / 2 - 12:.1f}" height="{gh / 2 - 12:.1f}" rx="22" fill="#fff" stroke="#000" stroke-width="3"/>')
                p.add(fit(a, 400, 400, cx + 16, cy + 16, gw / 2 - 32, gh / 2 - 32))
        elif art:
            p.add(fit(art[0], 400, 400, gx, gy, gw, gh))
        # age badge
        if c.get("badge"):
            # centre of the art grid: clear of the title, looks deliberate
            bx, by = gx + gw / 2, gy + gh / 2
            p.add(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="54" fill="#ffd93d" stroke="#000" stroke-width="3"/>')
            for k, part in enumerate(c["badge"].split("\n")):
                p.text(bx, by - 4 + k * 22, part, size=19)
        p.text(front_x + fw / 2, bleed + fh - safe - 8, c.get("cover_tagline", ""), size=20, fill="#222")

    def _front_ai(self, p, c, front_x, fw, fh, bleed, safe, accent, full_h):
        img = ROOT / c["cover_art"]
        jpg = subprocess.run(["magick", str(img), "-quality", "92", "jpg:-"], capture_output=True, check=True).stdout
        href = "data:image/jpeg;base64," + base64.b64encode(jpg).decode()
        p.add(f'<image x="{front_x:.1f}" y="0" width="{fw + bleed:.1f}" height="{full_h:.1f}" '
              f'preserveAspectRatio="xMidYMid slice" href="{href}"/>')
        lines = c.get("title_lines", [c["title"]])
        sizes = [min(70, (fw - 2 * safe - 40) / (len(l) * .74)) for l in lines]
        cover_sub = c.get("cover_subtitle", c.get("subtitle", ""))
        sub_size = min(22, (fw - 2 * safe - 50) / (len(cover_sub) * .56)) if cover_sub else 0
        box_h = sum(s * 1.02 for s in sizes) + (sub_size * 2.2 if cover_sub else 0) + 40
        p.add(f'<rect x="{front_x + safe:.1f}" y="{bleed + safe:.1f}" width="{fw - 2 * safe:.1f}" height="{box_h:.1f}" '
              f'rx="30" fill="#fff" fill-opacity=".93" stroke="#000" stroke-width="4"/>')
        ty = bleed + safe + 14
        for line, size in zip(lines, sizes):
            ty += size * .95
            p.text(front_x + fw / 2, ty, line.upper(), size=size, fill=accent,
                   extra='stroke="#000" stroke-width="4" paint-order="stroke" stroke-linejoin="round"')
            ty += size * .07
        if cover_sub:
            p.text(front_x + fw / 2, ty + sub_size * 1.35, cover_sub, size=sub_size, fill="#222")
        if c.get("badge"):
            bx, by = front_x + fw - safe - 62, bleed + fh - safe - 62
            p.add(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="58" fill="#ffd93d" stroke="#000" stroke-width="4"/>')
            for k, part in enumerate(c["badge"].split("\n")):
                p.text(bx, by - 4 + k * 23, part, size=21)

    def build_cover(self) -> Page:
        c = self.cfg
        n = len(self.pages)
        cw, chh = specs.cover_size(self.trim, n)
        P = specs.PT
        p = Page(cw, chh, bg=c.get("cover_bg", "#fff4d6"))
        bleed, spine = specs.COVER_BLEED * P, specs.spine_width(n) * P
        back_x, spine_x = bleed, bleed + self.w_in * P
        front_x = spine_x + spine
        fw, fh = self.w_in * P, self.h_in * P
        accent = c.get("cover_accent", "#ff6b6b")
        safe = 0.375 * P  # keep text well clear of trim
        if c.get("cover_art"):
            self._front_ai(p, c, front_x, fw, fh, bleed, safe, accent, chh * P)
        else:
            self._front_vector(p, c, front_x, fw, fh, bleed, safe, accent)
        # back
        p.add(f'<rect x="0" y="0" width="{spine_x:.1f}" height="{chh * P:.1f}" fill="{c.get("back_bg", "#fff")}"/>')
        by = bleed + safe + 50
        p.text(back_x + fw / 2, by, c.get("back_heading", c["title"]), size=26, fill="#222")
        by += 40
        for para in c.get("back_text", []):
            for line in _wrap(para, 52):
                p.text(back_x + safe + 20, by, line, size=15, weight="normal", anchor="start", fill="#222")
                by += 22
            by += 12
        samples = self.sample_pages(3)
        if samples:
            p.text(back_x + fw / 2, by + 24, "Peek inside:", size=18, fill="#222")
            tw = (fw - 2 * safe - 40) / 3
            for k, sp in enumerate(samples):
                p.add(page_thumb(sp, back_x + safe + k * (tw + 20), by + 40, tw))
        # barcode keep-clear area (KDP prints it here)
        bw, bh = specs.BARCODE_BOX[0] * P, specs.BARCODE_BOX[1] * P
        p.add(f'<rect x="{spine_x - safe - bw:.1f}" y="{bleed + fh - safe - bh:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="#fff"/>')
        # spine
        p.add(f'<rect x="{spine_x:.1f}" y="0" width="{spine:.1f}" height="{chh * P:.1f}" fill="{accent}"/>')
        if n >= specs.MIN_PAGES_SPINE_TEXT:
            # After rotate(90) glyphs grow from the baseline towards +x, so the baseline sits
            # half a glyph-height LEFT of centre. KDP rejects spine text closer than 0.0625" to
            # either spine edge (Christmas book was bounced on 2026-11-05 for exactly this).
            GLYPH = 0.74  # measured ink height / font size for Ubuntu Bold caps incl. '&'
            clear = specs.SPINE_TEXT_CLEARANCE * P + 1.0  # +1pt safety
            fs = min(14, (spine - 2 * clear) / GLYPH)
            if fs < 5:
                fs = 0  # spine too thin for legible text: leave it plain
            if fs:
                sx = spine_x + spine / 2
                base = sx - fs * GLYPH / 2
                assert base - spine_x >= clear - 0.01 and spine_x + spine - (base + fs * GLYPH) >= clear - 0.01
                p.add(f'<text transform="translate({base:.2f},{chh * P / 2:.1f}) rotate(90)" text-anchor="middle" '
                      f'font-family="{FONT}" font-weight="bold" font-size="{fs:.2f}" fill="#fff">'
                      f'{escape(c["title"].upper())}</text>')
        return p


def page_thumb(pg: Page, x, y, w) -> str:
    """Embed a real interior page, scaled, with a border and soft shadow."""
    h = w * pg.h / pg.w
    inner = "".join(pg.parts)
    return (f'<rect x="{x + 4:.1f}" y="{y + 5:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#000" fill-opacity=".18"/>'
            f'<svg x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" viewBox="0 0 {pg.w:.1f} {pg.h:.1f}">'
            f'<rect width="100%" height="100%" fill="#fff"/>{inner}</svg>'
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="none" stroke="#000" stroke-width="1.5"/>')


def aplus_banner(b: "Builder", out_png: Path):
    """970x600 A+ Content image: three real pages side by side."""
    pg = Page(970 / 72, 600 / 72, bg=b.cfg.get("cover_bg", "#fff"))
    pg.text(485, 62, b.cfg.get("aplus_heading", "Take a peek inside!"), size=40,
            fill=b.cfg.get("cover_accent", "#222"), extra='stroke="#000" stroke-width="2" paint-order="stroke"')
    tw, gap = 290, 25
    for k, sp in enumerate(b.sample_pages(3)):
        pg.add(page_thumb(sp, 485 - 1.5 * tw - gap + k * (tw + gap), 100, tw))
    pg.text(485, 560, b.cfg.get("aplus_caption", b.cfg.get("cover_tagline", "")), size=24, fill="#222")
    svg = out_png.with_suffix(".svg")
    svg.write_text(pg.render())
    subprocess.run(["rsvg-convert", "-w", "1940", "-o", str(out_png), str(svg)], check=True)
    svg.unlink()


def _wrap(text: str, width: int) -> list[str]:
    out, line = [], ""
    for word in text.split():
        if len(line) + len(word) + 1 > width:
            out.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    return out + ([line] if line else [])


def render_pdf(pages: list[Page], workdir: Path, out_pdf: Path):
    workdir.mkdir(parents=True, exist_ok=True)
    files = []
    for i, p in enumerate(pages, start=1):
        f = workdir / f"{i:04d}.svg"
        f.write_text(p.render())
        files.append(str(f))
    subprocess.run(["rsvg-convert", "-f", "pdf", "-o", str(out_pdf), *files], check=True)


def build(recipe: Path) -> Path:
    defaults = recipe.parent / "_defaults.json"
    cfg = json.loads(defaults.read_text()) if defaults.exists() else {}
    cfg.update(json.loads(recipe.read_text()))
    slug = recipe.stem
    out = OUT / slug
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    b = Builder(cfg)
    b.slug = slug
    b.build_interior()
    render_pdf(b.pages, out / "svg_interior", out / "interior.pdf")
    cover = b.build_cover()
    render_pdf([cover], out / "svg_cover", out / "cover.pdf")
    aplus_banner(b, out / "aplus_peek_inside.png")
    n = len(b.pages)
    price = cfg.get("price_usd", 9.99)
    listing = {
        "title": cfg["title"], "subtitle": cfg.get("subtitle", ""), "author": cfg.get("author", ""),
        "description_html": cfg.get("description_html", ""), "keywords": cfg.get("keywords", []),
        "categories": cfg.get("categories", []), "reading_age": cfg.get("reading_age", ""),
        "trim": cfg.get("trim", "8.5x11"), "bleed": False, "paper": "white", "interior": "black & white",
        "cover_finish": "matte", "low_content_book": False, "page_count": n,
        "cover_size_in": [round(v, 4) for v in specs.cover_size(cfg.get("trim", "8.5x11"), n)],
        "price_usd": price, "est_print_cost_usd": specs.print_cost_usd(n),
        "est_royalty_usd": specs.royalty_usd(price, n),
        "ai_disclosure": cfg.get("ai_disclosure", {}),
        "niche_test": cfg.get("niche_test", {}),
    }
    (out / "listing.json").write_text(json.dumps(listing, indent=2))
    # previews for QA
    subprocess.run(["pdftoppm", "-png", "-r", "40", str(out / "interior.pdf"), str(out / "prev")], check=True)
    subprocess.run(["pdftoppm", "-png", "-r", "45", str(out / "cover.pdf"), str(out / "cover_preview")], check=True)
    subprocess.run(["magick", "montage", *sorted(map(str, out.glob("prev-*.png"))), "-tile", "8x",
                    "-geometry", "+4+4", "-background", "#ccc", str(out / "contact_sheet.png")], check=True)
    for f in out.glob("prev-*.png"):
        f.unlink()
    shutil.rmtree(out / "svg_interior")
    shutil.rmtree(out / "svg_cover")
    print(f"{slug}: {n} pages, cover {listing['cover_size_in']} in, royalty ${listing['est_royalty_usd']} at ${price}")
    return out


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        build(Path(arg))
