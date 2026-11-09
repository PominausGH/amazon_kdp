"""4x4 picture sudoku for ages 4-8: each row, column and 2x2 box holds each picture once.
Puzzles are checked to have exactly one solution."""
from __future__ import annotations

import itertools
import random


def _full_grid(rng: random.Random) -> list[list[int]]:
    base = [[0, 1, 2, 3], [2, 3, 0, 1], [1, 0, 3, 2], [3, 2, 1, 0]]  # valid 4x4 with 2x2 boxes
    syms = list(range(4))
    rng.shuffle(syms)
    rows = rng.sample([0, 1], 2) + [2 + i for i in rng.sample([0, 1], 2)]
    if rng.random() < .5:
        rows = rows[2:] + rows[:2]
    cols = rng.sample([0, 1], 2) + [2 + i for i in rng.sample([0, 1], 2)]
    if rng.random() < .5:
        cols = cols[2:] + cols[:2]
    return [[syms[base[r][c]] for c in cols] for r in rows]


def _ok(g, r, c, v):
    if v in g[r] or v in (g[i][c] for i in range(4)):
        return False
    br, bc = r // 2 * 2, c // 2 * 2
    return all(g[i][j] != v for i in range(br, br + 2) for j in range(bc, bc + 2))


def count_solutions(g, limit=2) -> int:
    for r, c in itertools.product(range(4), range(4)):
        if g[r][c] is None:
            n = 0
            for v in range(4):
                if _ok(g, r, c, v):
                    g[r][c] = v
                    n += count_solutions(g, limit - n)
                    g[r][c] = None
                    if n >= limit:
                        return n
            return n
    return 1


class PictureSudoku:
    def __init__(self, rng: random.Random, blanks: int = 6):
        self.solution = _full_grid(rng)
        self.grid = [row[:] for row in self.solution]
        cells = [(r, c) for r in range(4) for c in range(4)]
        rng.shuffle(cells)
        removed = 0
        for r, c in cells:
            if removed >= blanks:
                break
            keep = self.grid[r][c]
            self.grid[r][c] = None
            if count_solutions([row[:] for row in self.grid]) == 1:
                removed += 1
            else:
                self.grid[r][c] = keep
        assert count_solutions([row[:] for row in self.grid]) == 1

    def svg(self, size: float, solution=False) -> str:
        cell = size / 4
        out = [f'<rect x="0" y="0" width="{size:.1f}" height="{size:.1f}" fill="#fff" stroke="#000" stroke-width="4"/>']
        for i in range(1, 4):
            sw = 4 if i == 2 else 1.6
            out.append(f'<line x1="{i * cell:.1f}" y1="0" x2="{i * cell:.1f}" y2="{size:.1f}" stroke="#000" stroke-width="{sw}"/>')
            out.append(f'<line x1="0" y1="{i * cell:.1f}" x2="{size:.1f}" y2="{i * cell:.1f}" stroke="#000" stroke-width="{sw}"/>')
        for r in range(4):
            for c in range(4):
                v = self.grid[r][c]
                if v is None and solution:
                    v = self.solution[r][c]
                    out.append(f'<rect x="{c * cell + 2:.1f}" y="{r * cell + 2:.1f}" width="{cell - 4:.1f}" '
                               f'height="{cell - 4:.1f}" fill="#ddd"/>')
                if v is not None:
                    out.append(icon(v, c * cell + cell / 2, r * cell + cell / 2, cell * .62))
        return "".join(out)


def icon(v: int, cx: float, cy: float, s: float) -> str:
    """Four simple, colourable outline pictures: star, tree, heart, bell."""
    st = f'fill="#fff" stroke="#000" stroke-width="{max(1.5, s / 26):.2f}" stroke-linejoin="round"'
    h = s / 2
    if v == 0:  # star
        import math
        pts = []
        for i in range(10):
            r = h if i % 2 == 0 else h * .42
            a = -math.pi / 2 + i * math.pi / 5
            pts.append(f"{cx + r * math.cos(a):.1f},{cy + r * math.sin(a) + h * .08:.1f}")
        return f'<polygon points="{" ".join(pts)}" {st}/>'
    if v == 1:  # tree
        return (f'<rect x="{cx - h * .14:.1f}" y="{cy + h * .62:.1f}" width="{h * .28:.1f}" height="{h * .36:.1f}" {st}/>'
                f'<polygon points="{cx:.1f},{cy - h:.1f} {cx + h * .55:.1f},{cy - h * .2:.1f} {cx + h * .3:.1f},{cy - h * .2:.1f} '
                f'{cx + h * .8:.1f},{cy + h * .62:.1f} {cx - h * .8:.1f},{cy + h * .62:.1f} {cx - h * .3:.1f},{cy - h * .2:.1f} '
                f'{cx - h * .55:.1f},{cy - h * .2:.1f}" {st}/>')
    if v == 2:  # heart
        return (f'<path d="M{cx:.1f},{cy + h * .85:.1f} C{cx - h * 1.25:.1f},{cy - h * .05:.1f} {cx - h * .65:.1f},{cy - h * 1.05:.1f} '
                f'{cx:.1f},{cy - h * .4:.1f} C{cx + h * .65:.1f},{cy - h * 1.05:.1f} {cx + h * 1.25:.1f},{cy - h * .05:.1f} '
                f'{cx:.1f},{cy + h * .85:.1f} Z" {st}/>')
    # bell
    return (f'<circle cx="{cx:.1f}" cy="{cy + h * .78:.1f}" r="{h * .16:.1f}" {st}/>'
            f'<path d="M{cx - h * .85:.1f},{cy + h * .62:.1f} Q{cx - h * .55:.1f},{cy + h * .3:.1f} {cx - h * .55:.1f},{cy - h * .2:.1f} '
            f'Q{cx - h * .5:.1f},{cy - h * .95:.1f} {cx:.1f},{cy - h * .95:.1f} Q{cx + h * .5:.1f},{cy - h * .95:.1f} '
            f'{cx + h * .55:.1f},{cy - h * .2:.1f} Q{cx + h * .55:.1f},{cy + h * .3:.1f} {cx + h * .85:.1f},{cy + h * .62:.1f} Z" {st}/>')
