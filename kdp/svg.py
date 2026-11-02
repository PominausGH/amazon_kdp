"""Tiny SVG page builder. Coordinates are points (72 per inch)."""
from __future__ import annotations

from dataclasses import dataclass, field
from xml.sax.saxutils import escape

from .specs import PT, SAFE_MARGIN

FONT = "Ubuntu, DejaVu Sans, sans-serif"
INK = "#000"


@dataclass
class Page:
    w_in: float
    h_in: float
    parts: list[str] = field(default_factory=list)
    bg: str | None = "#fff"

    @property
    def w(self) -> float:
        return self.w_in * PT

    @property
    def h(self) -> float:
        return self.h_in * PT

    @property
    def safe(self) -> tuple[float, float, float, float]:
        """x, y, width, height of the area artwork must stay inside."""
        m = SAFE_MARGIN * PT
        return m, m, self.w - 2 * m, self.h - 2 * m

    def add(self, s: str) -> "Page":
        self.parts.append(s)
        return self

    def text(self, x, y, s, size=24, weight="bold", anchor="middle", fill=INK,
             family=FONT, extra="") -> "Page":
        return self.add(
            f'<text x="{x:.2f}" y="{y:.2f}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" text-anchor="{anchor}" fill="{fill}" {extra}>{escape(s)}</text>'
        )

    def render(self) -> str:
        bg = f'<rect width="100%" height="100%" fill="{self.bg}"/>' if self.bg else ""
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w_in}in" height="{self.h_in}in" '
            f'viewBox="0 0 {self.w:.2f} {self.h:.2f}">{bg}{"".join(self.parts)}</svg>'
        )


def group(content: str, tx=0.0, ty=0.0, scale=1.0, rotate=0.0, extra="") -> str:
    t = f"translate({tx:.2f},{ty:.2f})"
    if rotate:
        t += f" rotate({rotate:.2f})"
    if scale != 1.0:
        t += f" scale({scale:.4f})"
    return f'<g transform="{t}" {extra}>{content}</g>'


def fit(content: str, box_w: float, box_h: float, x: float, y: float, w: float, h: float) -> str:
    """Scale content drawn in a box_w x box_h canvas to fit inside (x,y,w,h), centred."""
    s = min(w / box_w, h / box_h)
    ox = x + (w - box_w * s) / 2
    oy = y + (h - box_h * s) / 2
    return group(content, ox, oy, s)
