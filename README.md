# amazon_kdp: niche-test book factory

Generates print-ready KDP paperbacks (interior PDF + wrap cover PDF + listing metadata) from a JSON recipe, so niches can be tested cheaply. There are no dependencies beyond Python 3 and the system's `rsvg-convert`, `pdfinfo`, `pdftoppm` and ImageMagick.

```bash
python3 -m kdp.book books/*.json    # build -> output/<slug>/
python3 -m kdp.qa output/*/         # check against KDP specs (exit 1 on failure)
```

Each `output/<slug>/` contains:

| File | Use |
|---|---|
| `interior.pdf` | Upload as the manuscript (8.5x11, no bleed, white paper, B&W) |
| `cover.pdf` | Upload as the print-ready cover (sized with KDP's formula for the page count) |
| `listing.json` | Title, subtitle, description HTML, 7 keywords, categories, price, AI disclosure |
| `contact_sheet.png`, `cover_preview-1.png` | Eyeball check before uploading |

## Generators (`kdp/gen/`)

| Generator | What it makes | Art source |
|---|---|---|
| `bold.py` | Bold & easy toddler pages: 21 vehicles, 14 everyday objects, 21 Christmas items | Vector art written by an AI model (**disclose as AI-generated**) |
| `maze.py` | Rectangular mazes with a unique solution, plus answer pages | Algorithm |
| `wordsearch.py` | Themed word searches (kids mode: across/down only) | Algorithm |
| `dots.py` | Dot-to-dot from parametric curves and traced outlines | Algorithm |
| `mandala.py` | Symmetric mandalas, all regions closed, complexity 0..1 | Algorithm (not used in a book yet) |

A new book is just a new JSON file in `books/`. Copy an existing one and change the `sections`.

## KDP rules that shape the plan (checked 2026-11-03)

- **2 new titles per format per week** (since 21 Sep 2026). Saved drafts count. Resets Sunday 00:00 UTC. You can't bulk-publish, so we test 2 niches a week.
- **No upload API.** Listing is manual, or browser-assisted with you watching. Third-party auto-uploaders risk breaching KDP's terms.
- **AI disclosure is required** for AI-generated images and text: https://kdp.amazon.com/en_US/help/topic/G200672390
- **Royalty:** 50% below $9.99, 60% at $9.99 or more. A ≤110-page book costs $2.84 to print, so **$9.99 earns $3.15 and $7.99 earns $1.16**.
- **Don't tick "low-content book"** for colouring or activity books, so you get a free ISBN and Look Inside.
- No spine text under 79 pages. The builder handles this automatically.

## Test plan

See `niche-tests.csv`. For each book: publish, then give it 14 days, plus optionally a $5/day Sponsored Products auto campaign.

| Signal after 14 days | Decision |
|---|---|
| ≥3 organic sales, or ad CTR ≥0.4% and ACOS < 100% | **Scale**: make 2-3 sibling books (other themes, same format) |
| Impressions but no sales | Fix the cover/title/price once, then re-test |
| <1,000 ad impressions | Keywords or niche are dead: **kill** |

Queue (2 per week):
1. Week of 3 Nov: `christmas-bold-easy` (**submit by 5 Nov** for peak season), `things-that-go`
2. Week of 10 Nov: `christmas-activity-4-8`, `mazes-ages-4-8`
3. Then: dinosaurs bold & easy, Australian animals, capybara/axolotl, ages 8-12 mandalas

## Before the first upload

- [ ] Choose your pen name. `books/_defaults.json` currently says **"Crayon Cove Press"** as a placeholder.
- [ ] Open each `contact_sheet.png` and cover preview yourself.
- [ ] In KDP, order a **proof copy** of the first book before spending on ads.

## Pricing (set on KDP 2026-11-03)

Every price sits on or just above the store's 60%-royalty threshold. Below it the rate drops to 50%, which roughly halves the royalty.

| Store | Price | Royalty |
|---|---|---|
| Amazon.com | $9.99 | $3.15 |
| Amazon.com.au | AUD 13.99 (60% starts at 13.99) | AUD 3.11 |
| Amazon.co.uk | £7.99 | £2.64 |
| Amazon.ca | CAD 13.99 | CAD 4.86 |
| EU stores | €9.99 | €3.51 |

Expanded Distribution is off, because it only pays 40% (about $1.16).
