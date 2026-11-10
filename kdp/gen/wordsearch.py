"""Word search grids. Kids' mode = only forwards across / down (+ optional diagonal)."""
from __future__ import annotations

import random
import string

KIDS_DIRS = [(1, 0), (0, 1)]
OLDER_DIRS = [(1, 0), (0, 1), (1, 1), (1, -1)]
# Letters that are easily confused or produce rude accidental words get used less.
FILL = "".join(c for c in string.ascii_uppercase if c not in "QXZ")


class WordSearch:
    def __init__(self, words: list[str], size: int, rng: random.Random, diagonal=False, tries=400):
        self.size = size
        self.dirs = OLDER_DIRS if diagonal else KIDS_DIRS
        # tie-break alphabetically: set order changes per process (hash randomisation), which made
        # every build of a word-search book different
        words = sorted({w.upper().replace(" ", "") for w in words}, key=lambda w: (-len(w), w))
        for attempt in range(tries):
            grid = [[""] * size for _ in range(size)]
            placed = {}
            ok = True
            for wd in words:
                if len(wd) > size:
                    ok = False
                    break
                spots = []
                for dx, dy in self.dirs:
                    for y in range(size):
                        for x in range(size):
                            ex, ey = x + dx * (len(wd) - 1), y + dy * (len(wd) - 1)
                            if not (0 <= ex < size and 0 <= ey < size):
                                continue
                            overlap, fits = 0, True
                            for i, ch in enumerate(wd):
                                g = grid[y + dy * i][x + dx * i]
                                if g and g != ch:
                                    fits = False
                                    break
                                overlap += g == ch
                            if fits:
                                spots.append((overlap, rng.random(), x, y, dx, dy))
                if not spots:
                    ok = False
                    break
                # Mostly random placement, small preference for crossing words.
                spots.sort(key=lambda s: (-s[0] * 0.3 + s[1]))
                _, _, x, y, dx, dy = spots[0]
                for i, ch in enumerate(wd):
                    grid[y + dy * i][x + dx * i] = ch
                placed[wd] = (x, y, dx, dy)
            if ok:
                break
        else:
            raise ValueError(f"could not place words in {size}x{size}: {words}")
        for row in grid:
            for i, ch in enumerate(row):
                if not ch:
                    row[i] = rng.choice(FILL)
        self.grid, self.placed, self.words = grid, placed, sorted(placed)

    def svg(self, box: float, solution=False) -> str:
        cell = box / self.size
        out = [f'<rect x="0" y="0" width="{box:.2f}" height="{box:.2f}" rx="{cell*.4:.2f}" fill="none" stroke="#000" stroke-width="2.5"/>']
        if solution:
            for wd, (x, y, dx, dy) in self.placed.items():
                n = len(wd) - 1
                x1, y1 = (x + .5) * cell, (y + .5) * cell
                x2, y2 = (x + dx * n + .5) * cell, (y + dy * n + .5) * cell
                out.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="#000" '
                           f'stroke-opacity=".18" stroke-width="{cell*.8:.2f}" stroke-linecap="round"/>')
        fs = cell * .62
        for y, row in enumerate(self.grid):
            for x, ch in enumerate(row):
                out.append(f'<text x="{(x+.5)*cell:.2f}" y="{(y+.5)*cell + fs*.36:.2f}" font-family="Ubuntu Mono, DejaVu Sans Mono, monospace" '
                           f'font-size="{fs:.2f}" font-weight="bold" text-anchor="middle">{ch}</text>')
        return "".join(out)
