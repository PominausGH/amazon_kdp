"""Dot-to-dot puzzles from parametric curves and hand-placed outlines.
Each shape yields an ordered list of points in a unit-ish box; we normalise,
number them, and push labels outward so they don't sit on the line."""
from __future__ import annotations

import math


def _param(f, n, t0=0.0, t1=2 * math.pi):
    return [f(t0 + (t1 - t0) * i / n) for i in range(n)]


def heart(n):
    return _param(lambda t: (16 * math.sin(t) ** 3,
                             -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))), n)


def star(n, k=5):
    pts = []
    for i in range(2 * k):
        r = 1.0 if i % 2 == 0 else .42
        a = -math.pi / 2 + i * math.pi / k
        pts.append((r * math.cos(a), r * math.sin(a)))
    return pts


def butterfly(n):
    def f(t):
        r = math.exp(math.sin(t)) - 2 * math.cos(4 * t)
        return (r * math.cos(t + math.pi / 2), -r * math.sin(t + math.pi / 2))
    return _param(f, n)


def fish(n):
    return _param(lambda t: (math.cos(t) - math.sin(t) ** 2 / math.sqrt(2), -math.cos(t) * math.sin(t)), n)


def flower(n, k=5):
    return _param(lambda t: ((1 + .45 * math.cos(k * t)) * math.cos(t), (1 + .45 * math.cos(k * t)) * math.sin(t)), n)


def apple(n):
    return _param(lambda t: (math.sin(t) * (1 + .15 * math.cos(t)),
                             -(math.cos(t) + .25 * abs(math.sin(t)) ** 8 - .35 * (math.cos(t) > .6) * (1 - abs(math.sin(t)) * 3))), n)


# Hand-placed outlines (x right, y down), traced once.
HOUSE = [(0, 10), (0, 4), (5, 0), (10, 4), (10, 10), (6.5, 10), (6.5, 6.5), (3.5, 6.5), (3.5, 10)]
ROCKET = [(5, 0), (6.6, 2.2), (7, 5.5), (7, 9), (8.8, 11.2), (8.8, 13), (7, 12), (6, 13.6), (5, 12.4),
          (4, 13.6), (3, 12), (1.2, 13), (1.2, 11.2), (3, 9), (3, 5.5), (3.4, 2.2)]
SAILBOAT = [(5, 0), (5, 7), (9, 7), (8.5, 7), (7.5, 9), (2.5, 9), (1.5, 7), (5, 7), (5, 6), (1.5, 6), (5, .8)]
CAT = [(2, 0), (3.3, 2.3), (6.7, 2.3), (8, 0), (8.6, 3.5), (9, 6), (8, 8.3), (5, 9.3), (2, 8.3), (1, 6), (1.4, 3.5)]
DINO = [(0, 8), (2, 6.2), (3.5, 4.2), (5, 3.6), (6.5, 4), (7.4, 2.2), (8.2, 1), (9.6, 1.1), (10.2, 2),
        (9.4, 2.8), (8.4, 3.1), (8, 5.2), (7.6, 7.2), (7.6, 9.8), (6.6, 9.8), (6.4, 8.2), (4.6, 8.4),
        (4.6, 9.8), (3.6, 9.8), (3.4, 8.1), (2, 8.3)]
TRUCK = [(0, 7.5), (0, 1), (6, 1), (6, 3), (8.4, 3), (10, 5.2), (10, 7.5), (8.8, 7.5), (8.2, 6.6),
         (7.2, 6.6), (6.6, 7.5), (3.4, 7.5), (2.8, 6.6), (1.8, 6.6), (1.2, 7.5)]
DIAMOND = [(5, 0), (10, 4), (5, 12), (0, 4)]
WHALE = [(0, 4), (1.5, 1.5), (4.5, .6), (7.5, 1.5), (9, 3.4), (10.2, 2.2), (11.6, 1.4), (11, 3.6), (11.6, 5.6),
         (10.2, 4.8), (8.8, 4.9), (7, 6.4), (4.5, 6.8), (2, 6.4)]


def _densify(poly, n):
    """Spread n points along a closed polyline, always keeping its corners."""
    segs = list(zip(poly, poly[1:] + poly[:1]))
    lens = [math.dist(a, b) for a, b in segs]
    total = sum(lens)
    out = []
    for (a, b), L in zip(segs, lens):
        k = max(1, round(n * L / total))
        for j in range(k):
            t = j / k
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


SHAPES = {
    "heart": lambda n: heart(n), "star": lambda n: _densify(star(n), n), "butterfly": butterfly,
    "fish": fish, "flower": flower, "house": lambda n: _densify(HOUSE, n),
    "rocket": lambda n: _densify(ROCKET, n), "sailboat": lambda n: _densify(SAILBOAT, n),
    "cat": lambda n: _densify(CAT, n), "dinosaur": lambda n: _densify(DINO, n),
    "truck": lambda n: _densify(TRUCK, n), "diamond": lambda n: _densify(DIAMOND, n),
    "whale": lambda n: _densify(WHALE, n),
}


# ---------- Christmas outlines ----------

def _arc(cx, cy, r, a0, a1, k):
    """Points on a circle from angle a0 to a1 (degrees, y down so +90 is UP)."""
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / k)),
             cy - r * math.sin(math.radians(a0 + (a1 - a0) * i / k))) for i in range(k + 1)]


XMAS_TREE = [(5, 0), (7, 3), (6, 3), (8.5, 6), (7, 6), (10, 9.5), (6, 9.5), (6, 11.5), (4, 11.5), (4, 9.5),
             (0, 9.5), (3, 6), (1.5, 6), (4, 3), (3, 3)]
BELL = [(4, 0), (6, 0), (6, 1), (7.5, 2), (8.3, 5), (8.6, 8), (10, 9.5), (10, 10.5), (6, 10.5), (5, 11.8),
        (4, 10.5), (0, 10.5), (0, 9.5), (1.4, 8), (1.7, 5), (2.5, 2), (4, 1)]
STOCKING = [(2, 0), (7, 0), (7, 1.8), (6.6, 1.8), (6.6, 7), (9, 8.6), (9.6, 10.2), (8.6, 11.6), (6.4, 11.6),
            (2.6, 9.4), (2.4, 1.8), (2, 1.8)]
GIFT = [(0, 4), (0, 3), (3, 3), (2, 1.2), (3, .4), (5, 2.4), (7, .4), (8, 1.2), (7, 3), (10, 3), (10, 4),
        (9.4, 4), (9.4, 11), (.6, 11), (.6, 4)]
GINGERBREAD = [(5, 0), (6.4, .6), (7, 2), (6.6, 3.2), (9.4, 3.8), (10, 5), (9.4, 5.8), (7, 5.6), (7.2, 8),
               (8.8, 11), (8.2, 12), (7, 11.6), (5, 9), (3, 11.6), (1.8, 12), (1.2, 11), (2.8, 8), (3, 5.6),
               (.6, 5.8), (0, 5), (.6, 3.8), (3.4, 3.2), (3, 2), (3.6, .6)]
MITTEN = [(2, 12), (2, 10.5), (1.6, 8), (1, 5), (.4, 4), (.6, 2.8), (1.6, 2.8), (2.4, 4.4), (2.8, 2), (4, .4),
          (6, .2), (7.6, 1.4), (8.2, 4), (8, 8), (7.6, 10.5), (7.6, 12)]
CANDLE = [(5, 0), (6, 1.8), (5.6, 3), (7, 3), (7, 12), (3, 12), (3, 3), (4.4, 3), (4, 1.8)]
SANTA_HAT = [(.5, 11), (.5, 9), (2, 9), (4, 3), (7, .8), (9.4, 1.6), (9.8, 3.2), (8.2, 3.4), (7, 4), (8, 9),
             (9.5, 9), (9.5, 11)]
SLEIGH = [(0, 2), (1.4, 2), (2, 6), (8, 6), (9, 3), (10.4, 2.6), (10, 4), (9.4, 7), (8, 8), (9.6, 8),
          (10.4, 7.4), (10.8, 8.2), (9.8, 9.4), (.8, 9.4), (.4, 8.4), (1, 8), (2.6, 8), (1.2, 7), (.4, 3.2)]
LANTERN = [(4, 0), (6, 0), (6, 1), (7.5, 1), (8.5, 2.6), (7.5, 2.6), (7.5, 10), (8.5, 10), (8.5, 11.5), (1.5, 11.5),
           (1.5, 10), (2.5, 10), (2.5, 2.6), (1.5, 2.6), (2.5, 1), (4, 1)]
GINGER_HOUSE = [(0, 11), (0, 5), (5, .6), (7, 2.4), (7, .8), (8.4, .8), (8.4, 3.6), (10, 5), (10, 11),
                (6.2, 11), (6.2, 7.4), (3.8, 7.4), (3.8, 11)]


def candy_cane(n):
    cx, cy, R, r = 4.2, 3.2, 3.2, 1.6
    pts = [(cx - R, 12)] + _arc(cx, cy, R, 180, 0, 10) + [(cx + R, 5.4), (cx + r, 5.4)]
    pts += _arc(cx, cy, r, 0, 180, 6) + [(cx - r, 12)]
    return _densify(pts, n)


def ornament(n):
    # bauble (centre 5,5.6 r 4.2) with a cap on top
    c, R, half = (5, 5.6), 4.2, 1.0
    a = math.degrees(math.asin(half / R))  # where the cap meets the ball
    pts = [(5 - half, 0), (5 + half, 0), (5 + half, c[1] - R * math.cos(math.radians(a)))]
    pts += _arc(c[0], c[1], R, 90 - a, -270 + a, 18)
    return _densify(pts, n)


def snowman(n):
    # union of head (5,3.2 r2.4) and body (5,8.5 r3.5); they cross at y=5.238, x=5+-1.268
    yi, xi = 5.2377, 1.268
    top = math.degrees(math.atan2(-(yi - 3.2), xi))       # right crossing on the head
    bot = math.degrees(math.atan2(-(yi - 8.5), xi))       # right crossing on the body
    pts = _arc(5, 3.2, 2.4, top, 180 - top, 12) + _arc(5, 8.5, 3.5, 180 - bot, 360 + bot, 16)[1:]
    return _densify(pts[:-1], n)


def snowflake(n):
    pts = []
    for i in range(12):
        r = 1.0 if i % 2 == 0 else .38
        a = -math.pi / 2 + i * math.pi / 6
        pts.append((r * math.cos(a), r * math.sin(a)))
    return _densify(pts, n)


SHAPES.update({
    "xmas_tree": lambda n: _densify(XMAS_TREE, n), "bell": lambda n: _densify(BELL, n),
    "stocking": lambda n: _densify(STOCKING, n), "gift": lambda n: _densify(GIFT, n),
    "gingerbread": lambda n: _densify(GINGERBREAD, n), "mitten": lambda n: _densify(MITTEN, n),
    "candle": lambda n: _densify(CANDLE, n), "santa_hat": lambda n: _densify(SANTA_HAT, n),
    "sleigh": lambda n: _densify(SLEIGH, n), "gingerbread_house": lambda n: _densify(GINGER_HOUSE, n), "lantern": lambda n: _densify(LANTERN, n),
    "candy_cane": candy_cane, "ornament": ornament, "snowman": snowman, "snowflake": snowflake,
})


def dot_to_dot(shape: str, n: int, box: float, solution=False, font=13.0) -> str:
    raw = SHAPES[shape](n)
    span = max(max(p[0] for p in raw) - min(p[0] for p in raw), max(p[1] for p in raw) - min(p[1] for p in raw))
    pts = []
    for q in raw:  # drop near-duplicate dots (they print as overlapping numbers)
        if not pts or math.dist(q, pts[-1]) > span * .02:
            pts.append(q)
    if len(pts) > 2 and math.dist(pts[0], pts[-1]) <= span * .02:
        pts.pop()
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    w, h = max(xs) - min(xs), max(ys) - min(ys)
    s = box * .86 / max(w, h)
    ox = (box - w * s) / 2 - min(xs) * s
    oy = (box - h * s) / 2 - min(ys) * s
    P = [(x * s + ox, y * s + oy) for x, y in pts]
    cx, cy = sum(p[0] for p in P) / len(P), sum(p[1] for p in P) / len(P)
    out = []
    if solution:
        out.append(f'<polygon points="{" ".join(f"{x:.2f},{y:.2f}" for x, y in P)}" fill="none" stroke="#000" stroke-width="3" stroke-linejoin="round"/>')
    for i, (x, y) in enumerate(P, start=1):
        dx, dy = x - cx, y - cy
        d = math.hypot(dx, dy) or 1
        lx, ly = x + dx / d * font * 1.05, y + dy / d * font * 1.05 + font * .35
        r = 4.2 if i > 1 else 6
        out.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="#000"/>')
        out.append(f'<text x="{lx:.2f}" y="{ly:.2f}" font-family="Ubuntu, DejaVu Sans, sans-serif" font-size="{font}" '
                   f'text-anchor="middle" font-weight="{"bold" if i == 1 else "normal"}">{i}</text>')
    if not solution:
        # star marks the start
        x, y = P[0]
        out.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="10" fill="none" stroke="#000" stroke-width="1.5"/>')
    return "".join(out)
