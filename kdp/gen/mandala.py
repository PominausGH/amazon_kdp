"""Procedural mandalas. Each ring is n-fold symmetric and built from closed
shapes, so every region is colourable. `complexity` 0..1 scales ring count
and petal count: ~0.2 suits ages 4-8 (big regions), ~0.8 suits teens/adults."""
from __future__ import annotations

import math
import random


def _petal(r0, r1, half_w, bulge):
    """Closed petal from radius r0 to r1 along the +x axis."""
    mid = r0 + (r1 - r0) * bulge
    return (f"M{r0:.2f},0 Q{mid:.2f},{-half_w:.2f} {r1:.2f},0 "
            f"Q{mid:.2f},{half_w:.2f} {r0:.2f},0Z")


def _rot(d, n, offset=0.0):
    return "".join(f'<path d="{d}" transform="rotate({offset + i * 360 / n:.3f})"/>' for i in range(n))


def mandala(rng: random.Random, R=300.0, complexity=0.3, fill_cb=None) -> str:
    """Return SVG centred on (0,0) with outer radius R.
    fill_cb(ring_index) -> colour lets the cover reuse the same art in colour."""
    fill = fill_cb or (lambda i: "#fff")
    rings = []
    n_rings = 3 + round(complexity * 5)
    base_n = rng.choice([6, 8, 8, 10, 12]) if complexity < .5 else rng.choice([12, 16, 18, 24])
    radii = sorted(rng.uniform(.12, .98) * R for _ in range(n_rings - 1)) + [R]
    # enforce minimum ring thickness so small kids can colour inside
    min_gap = R * (.07 if complexity > .5 else .11)
    clean = [R * .14]
    for r in radii:
        if r - clean[-1] >= min_gap:
            clean.append(r)
    if clean[-1] < R * .95:
        clean[-1] = R
    out = []
    # centre
    out.append(f'<circle r="{clean[0]:.2f}" fill="{fill(0)}"/>')
    if clean[0] > 25:
        k = rng.choice([5, 6, 8])
        out.append(f'<g fill="{fill(99)}">{_rot(_petal(0, clean[0]*.9, clean[0]*.28, .5), k)}</g>')
    for i, (r0, r1) in enumerate(zip(clean, clean[1:]), start=1):
        style = rng.choice(["petals", "petals", "double", "scallop", "teardrops", "band"])
        n = base_n * (2 if (complexity > .5 and i > 2 and rng.random() < .5) else 1)
        off = rng.choice([0, 180 / n])
        g = []
        if style in ("petals", "double"):
            hw = min((r1 - r0) * .55, math.pi * r1 / n * .95)
            g.append(f'<g fill="{fill(i)}">{_rot(_petal(r0, r1, hw, rng.uniform(.35, .65)), n, off)}</g>')
            if style == "double":
                g.append(f'<g fill="{fill(i+50)}">{_rot(_petal(r0, r0 + (r1 - r0) * .6, hw * .45, .5), n, off)}</g>')
            g.insert(0, f'<circle r="{r1:.2f}" fill="{fill(i+20)}"/>')
        elif style == "scallop":
            ang = 2 * math.pi / n
            pts = []
            for k in range(n):
                a0, a1 = k * ang, (k + 1) * ang
                pts.append(f"{'M' if k == 0 else 'L'}{r0 * math.cos(a0):.2f},{r0 * math.sin(a0):.2f}")
                pts.append(f"A{(r1 - r0) * .9:.2f},{(r1 - r0) * .9:.2f} 0 0 1 {r0 * math.cos(a1):.2f},{r0 * math.sin(a1):.2f}")
            # scallop bumps drawn as arcs outward from ring r0
            bump = ""
            for k in range(n):
                a = (k + .5) * ang
                cx, cy = (r0 + (r1 - r0) * .45) * math.cos(a), (r0 + (r1 - r0) * .45) * math.sin(a)
                rr = min((r1 - r0) * .42, math.pi * r0 / n * .9)
                bump += f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{rr:.2f}"/>'
            g.append(f'<circle r="{r1:.2f}" fill="{fill(i+20)}"/><g fill="{fill(i)}">{bump}</g>')
        elif style == "teardrops":
            hw = min((r1 - r0) * .35, math.pi * r1 / n * .7)
            d = (f"M{r0 + 4:.2f},0 C{r0 + (r1-r0)*.5:.2f},{-hw*1.6:.2f} {r1:.2f},{-hw*.4:.2f} {r1 - 2:.2f},0 "
                 f"C{r1:.2f},{hw*.4:.2f} {r0 + (r1-r0)*.5:.2f},{hw*1.6:.2f} {r0 + 4:.2f},0Z")
            g.append(f'<circle r="{r1:.2f}" fill="{fill(i+20)}"/><g fill="{fill(i)}">{_rot(d, n, off)}</g>')
        else:  # band of spokes making trapezoid cells
            g.append(f'<circle r="{r1:.2f}" fill="{fill(i)}"/>')
            spokes = "".join(
                f'<line x1="{r0 * math.cos(2*math.pi*k/n):.2f}" y1="{r0 * math.sin(2*math.pi*k/n):.2f}" '
                f'x2="{r1 * math.cos(2*math.pi*k/n):.2f}" y2="{r1 * math.sin(2*math.pi*k/n):.2f}"/>' for k in range(n))
            g.append(spokes)
        rings.append("".join(g))
    # Outer rings are drawn first so inner ones sit on top.
    body = "".join(reversed(rings)) + "".join(out)
    return f'<circle r="{R:.2f}" fill="{fill(98)}"/>{body}'


def mandala_svg(rng, R=300.0, complexity=0.3, stroke=3.0, fill_cb=None) -> str:
    return (f'<g stroke="#000" stroke-width="{stroke:.2f}" stroke-linejoin="round" stroke-linecap="round">'
            f'{mandala(rng, R, complexity, fill_cb)}</g>')
