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
}


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


def cover_size(trim: str, page_count: int) -> tuple[float, float]:
    w, h = TRIMS[trim]
    return (2 * w + spine_width(page_count) + 2 * COVER_BLEED, h + 2 * COVER_BLEED)


def print_cost_usd(page_count: int) -> float:
    """Amazon.com B&W paperback, large trim (>6.12in wide). Source:
    https://kdp.amazon.com/en_US/help/topic/G201834340 (checked 2026-11).
    24-110 pages: flat $2.84. Over 110: $1.00 + $0.017/page."""
    if page_count <= 110:
        return 2.84
    return 1.00 + 0.017 * page_count


def royalty_usd(list_price: float, page_count: int) -> float:
    """Since 10 Jun 2025: 50% below $9.99, 60% at $9.99+ (Amazon.com)."""
    rate = 0.60 if list_price >= 9.99 else 0.50
    return round(rate * list_price - print_cost_usd(page_count), 2)
