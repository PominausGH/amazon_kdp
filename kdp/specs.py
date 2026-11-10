"""KDP paperback print specs (black & white interior, white paper).

Sources (checked 2026-11):
  - Trim/bleed/margins: https://kdp.amazon.com/en_US/help/topic/GVBQ3CMEQW3W2VL6
  - Cover size calculator: https://kdp.amazon.com/en_US/cover-calculator
All units are inches unless noted. Pages are drawn in points (72/in).
"""

PT = 72  # points per inch

# White paper, B&W interior. Cream is 0.0025.
SPINE_PER_PAGE_WHITE = 0.002252
COVER_BLEED = 0.125
MIN_PAGES = 24
MIN_PAGES_SPINE_TEXT = 79  # KDP won't allow spine text below this
SPINE_TEXT_CLEARANCE = 0.0625  # min gap between spine text and each spine edge (inches)
BARCODE_BOX = (2.0, 1.2)   # KDP places the barcode bottom-right of the back cover

TRIMS = {
    "8.5x11": (8.5, 11.0),
    "8x10": (8.0, 10.0),
    "8.5x8.5": (8.5, 8.5),
    "6x9": (6.0, 9.0),
    "8.25x11": (8.25, 11.0),  # hardcover's nearest size to 8.5x11
}

# ---------- hardcover (case laminate) ----------
# From KDP's Cover Calculator (hardcover, B&W, white paper, 8.25x11), read 2026-11-10.
HC_WRAP = 0.591          # wraps round the board on every outer edge
HC_HINGE = 0.394         # fold zone beside the spine on each panel: keep content out
HC_MARGIN = 0.125        # content margin inside each panel
HC_BARCODE_MARGIN = (0.25, 0.375)
HC_PANEL = {"8.25x11": (8.447, 11.236)}   # board is larger than the trim
# Hardcover spine comes from a KDP table, not a formula: only use measured values.
HC_SPINE = {"8.25x11": {104: 0.423, 114: 0.446}}
HC_MIN_PAGES = 75


def inside_margin(page_count: int) -> float:
    """Minimum gutter margin for a given page count (no-bleed interior)."""
    if page_count <= 150:
        return 0.375
    if page_count <= 300:
        return 0.5
    if page_count <= 500:
        return 0.625
    if page_count <= 700:
        return 0.75
    return 0.875


OUTSIDE_MARGIN = 0.25
# We keep all artwork inside a much safer box than KDP's minimum, so pages
# can't fail the margin check no matter which side of the spread they land on.
SAFE_MARGIN = 0.6


def spine_width(page_count: int) -> float:
    return page_count * SPINE_PER_PAGE_WHITE


def cover_geom(trim: str, page_count: int, binding: str = "paperback") -> dict:
    """Cover layout in inches: outer edge (bleed or wrap), panel size, spine, hinge, full size."""
    if binding == "hardcover":
        if page_count not in HC_SPINE.get(trim, {}):
            raise SystemExit(f"no measured hardcover spine for {trim} / {page_count} pages: "
                             "read it from https://kdp.amazon.com/en_US/cover-calculator and add to HC_SPINE")
        pw, ph = HC_PANEL[trim]
        edge, spine, hinge = HC_WRAP, HC_SPINE[trim][page_count], HC_HINGE
    else:
        pw, ph = TRIMS[trim]
        edge, spine, hinge = COVER_BLEED, spine_width(page_count), 0.0
    return {"edge": edge, "panel_w": pw, "panel_h": ph, "spine": spine, "hinge": hinge,
            "full_w": 2 * edge + 2 * pw + spine, "full_h": 2 * edge + ph}


def cover_size(trim: str, page_count: int, binding: str = "paperback") -> tuple[float, float]:
    g = cover_geom(trim, page_count, binding)
    return (g["full_w"], g["full_h"])


def print_cost_usd(page_count: int) -> float:
    """Amazon.com B&W paperback, large trim (>6.12in wide). Source:
    https://kdp.amazon.com/en_US/help/topic/G201834340 (checked 2026-11).
    24-110 pages: flat $2.84. Over 110: $1.00 + $0.017/page."""
    if page_count <= 110:
        return 2.84
    return 1.00 + 0.017 * page_count


def hc_print_cost_usd(page_count: int) -> float:
    """Amazon.com B&W hardcover, 8.25x11, white paper. MEASURED on KDP's pricing page 2026-11-10:
    104 pages = $7.49, 114 pages = $7.59 -> $6.45 + $0.01/page. (Third-party guides said $6.80
    flat for 75-108 pages: wrong for this trim.) Re-check if trim or page range changes a lot."""
    return round(6.45 + 0.01 * page_count, 2)


def royalty_usd(list_price: float, page_count: int, binding: str = "paperback") -> float:
    """Since 10 Jun 2025: 50% below $9.99, 60% at $9.99+ (Amazon.com). Same tiers for hardcover."""
    rate = 0.60 if list_price >= 9.99 else 0.50
    cost = hc_print_cost_usd(page_count) if binding == "hardcover" else print_cost_usd(page_count)
    return round(rate * list_price - cost, 2)
