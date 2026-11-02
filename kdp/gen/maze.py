"""Rectangular mazes (recursive backtracker = one unique solution) with solutions."""
from __future__ import annotations

import random
from collections import deque

N, S, E, W = 1, 2, 4, 8
DX = {N: 0, S: 0, E: 1, W: -1}
DY = {N: -1, S: 1, E: 0, W: 0}
OPP = {N: S, S: N, E: W, W: E}


class Maze:
    def __init__(self, cols: int, rows: int, rng: random.Random):
        self.cols, self.rows = cols, rows
        self.cells = [[0] * cols for _ in range(rows)]  # bitmask of open sides
        stack = [(0, 0)]
        seen = {(0, 0)}
        while stack:
            x, y = stack[-1]
            dirs = [d for d in (N, S, E, W)
                    if 0 <= x + DX[d] < cols and 0 <= y + DY[d] < rows
                    and (x + DX[d], y + DY[d]) not in seen]
            if not dirs:
                stack.pop()
                continue
            d = rng.choice(dirs)
            nx, ny = x + DX[d], y + DY[d]
            self.cells[y][x] |= d
            self.cells[ny][nx] |= OPP[d]
            seen.add((nx, ny))
            stack.append((nx, ny))
        self.start = (0, 0)
        self.end = (cols - 1, rows - 1)

    def solve(self) -> list[tuple[int, int]]:
        prev = {self.start: None}
        q = deque([self.start])
        while q:
            c = q.popleft()
            if c == self.end:
                break
            x, y = c
            for d in (N, S, E, W):
                if self.cells[y][x] & d:
                    n = (x + DX[d], y + DY[d])
                    if n not in prev:
                        prev[n] = c
                        q.append(n)
        path, c = [], self.end
        while c is not None:
            path.append(c)
            c = prev[c]
        return path[::-1]

    def svg(self, size_w: float, size_h: float, stroke: float, solution=False) -> tuple[str, float, float]:
        """Return (svg, width, height) drawn at the largest cell size fitting the box."""
        cell = min(size_w / self.cols, size_h / self.rows)
        w, h = cell * self.cols, cell * self.rows
        segs = []
        # Top & left borders with gaps for entrance (top-left) and exit (bottom-right).
        segs.append(f"M{cell:.2f},0H{w:.2f}")
        segs.append(f"M0,0V{h:.2f}")
        for y in range(self.rows):
            for x in range(self.cols):
                c = self.cells[y][x]
                x0, y0 = x * cell, y * cell
                if not c & E:
                    segs.append(f"M{x0 + cell:.2f},{y0:.2f}V{y0 + cell:.2f}")
                if not c & S and not (x == self.cols - 1 and y == self.rows - 1):
                    segs.append(f"M{x0:.2f},{y0 + cell:.2f}H{x0 + cell:.2f}")
        out = [f'<path d="{"".join(segs)}" fill="none" stroke="#000" stroke-width="{stroke:.2f}" '
               f'stroke-linecap="round" stroke-linejoin="round"/>']
        if solution:
            pts = " ".join(f"{(x + .5) * cell:.2f},{(y + .5) * cell:.2f}" for x, y in self.solve())
            pts = f"{.5 * cell:.2f},{-.5 * cell:.2f} " + pts + f" {(self.cols - .5) * cell:.2f},{h + .5 * cell:.2f}"
            out.append(f'<polyline points="{pts}" fill="none" stroke="#000" stroke-dasharray="{cell*.25:.2f},{cell*.2:.2f}" '
                       f'stroke-width="{max(stroke * .8, cell * .18):.2f}" stroke-linecap="round" stroke-linejoin="round" opacity=".55"/>')
        return "".join(out), w, h
