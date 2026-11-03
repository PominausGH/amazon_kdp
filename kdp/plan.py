"""Turn a one-line niche brief from books/queue.json into a full book recipe.

Usage: python -m kdp.plan <slug>      (writes books/<slug>.json)
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from .llm import PLANNER, LLMError, chat_json

ROOT = Path(__file__).resolve().parent.parent
QUEUE = ROOT / "books" / "queue.json"

EXAMPLE = ROOT / "books" / "christmas-bold-easy.json"

SYSTEM = """You plan children's colouring books for Amazon KDP. You write the listing and the page plan.
Rules:
- Original subjects only. NO trademarked characters or brands (no Bluey, Disney, Pokemon, Paw Patrol, Peppa,
  Hot Wheels, Barbie, Minecraft, Lego etc.), no real people, no lookalikes.
- Each page is ONE clear subject a child of the stated age can colour. Subjects are concrete and visual.
  Never ask for words, letters, numbers, signs with writing, logos, or borders in a picture.
- Labels: UPPERCASE, max 16 characters, the plain name of the subject (e.g. "DUMP TRUCK", "KOALA").
- All pages must be different subjects or clearly different scenes. No near-duplicates.
- Keywords: exactly 7, each <= 50 characters, buyer search phrases, no brand names, no repeats of title words only.
- Title + subtitle together <= 190 characters. Subtitle states page count and age range.
- description_html: short, scannable: bold opening line, 4-5 <li> bullets (page count, single-sided/no bleed-through,
  thick lines, examples of subjects, 8.5 x 11), a gift line. Only <p>, <b>, <ul>, <li>.
- cover_prompt: a bright cheerful SCENE featuring 4-6 of the book's best subjects together, for a full-colour cover.
- Australian English is fine in back text; US spelling ("coloring") in title, subtitle and keywords (bigger market).
Reply with ONE JSON object only."""

FIELDS = """{
 "title": str, "title_lines": [2-3 short lines for the cover, e.g. ["Dinosaur", "Coloring Book"]],
 "subtitle": str, "cover_subtitle": str (<= 52 chars), "badge": "AGES\\nX-Y",
 "cover_tagline": str (<= 45 chars), "cover_accent": "#hex (bright, readable white text on it)",
 "cover_bg": "#hex (very light)", "back_heading": str, "back_text": [2-3 short paragraphs],
 "page_background": "what simple background details are allowed, e.g. 'a simple ground line and a few small clouds'",
 "pages": [{"label": str, "subject": "visual description, simple, toddler-friendly"} x N],
 "keywords": [7 str], "categories": [2 str, Amazon category paths],
 "description_html": str, "cover_prompt": str, "reading_age": "X-Y",
 "aplus_heading": str (<= 30 chars), "aplus_caption": str (<= 60 chars)
}"""


def slug_ok(s: str) -> bool:
    return bool(re.fullmatch(r"[a-z0-9-]{3,60}", s))


def validate(r: dict, n: int) -> list[str]:
    errs = []
    pages = r.get("pages", [])
    if len(pages) != n:
        errs.append(f"need {n} pages, got {len(pages)}")
    labels = [p.get("label", "") for p in pages]
    if len(set(labels)) != len(labels):
        errs.append("duplicate labels")
    errs += [f"label too long: {l}" for l in labels if len(l) > 16]
    kws = r.get("keywords", [])
    if len(kws) != 7 or any(len(k) > 50 for k in kws):
        errs.append("need 7 keywords each <= 50 chars")
    if len(r.get("title", "")) + len(r.get("subtitle", "")) > 190:
        errs.append("title+subtitle too long")
    banned = re.compile(r"\b(bluey|disney|pokemon|paw patrol|peppa|hot wheels|barbie|minecraft|lego|marvel|frozen)\b", re.I)
    if banned.search(json.dumps(r)):
        errs.append("contains a trademarked name")
    for k in ("title", "subtitle", "cover_prompt", "description_html", "title_lines"):
        if not r.get(k):
            errs.append(f"missing {k}")
    return errs


def plan(brief: dict) -> dict:
    n = brief.get("pages", 50)
    example = json.loads(EXAMPLE.read_text())
    example_view = {k: example[k] for k in ("title", "subtitle", "keywords", "description_html", "cover_prompt")}
    example_view["pages"] = example["sections"][0]["pages"][:5]
    msgs = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": (
            f"Brief: {json.dumps(brief)}\nNumber of pages: {n}\n\n"
            f"Return JSON with exactly these fields:\n{FIELDS}\n\n"
            f"Example of the style (a different book, partial):\n{json.dumps(example_view, indent=1)}")},
    ]
    for attempt in range(3):
        r = chat_json(msgs, PLANNER, max_tokens=8000)
        errs = validate(r, n)
        if not errs:
            break
        msgs += [{"role": "assistant", "content": json.dumps(r)},
                 {"role": "user", "content": "Fix these problems and return the full JSON again: " + "; ".join(errs)}]
    else:
        raise LLMError(f"plan for {brief['slug']} still invalid: {errs}")
    pages = r.pop("pages")
    recipe = {**r,
              "seed": abs(hash(brief["slug"])) % 100000,
              "sections": [{"type": "ai_pages", "single_sided": True, "pages": pages}],
              "price_usd": 9.99,
              "ai_disclosure": {"images": "AI-generated (Google Gemini via OpenRouter), cleaned to black & white",
                                "text": "AI-generated (Claude)"},
              "niche_test": {"niche": brief["theme"], "hypothesis": brief.get("why", ""), "planned_by": PLANNER}}
    return recipe


def main():
    slug = sys.argv[1]
    q = json.loads(QUEUE.read_text())
    brief = next(b for b in q["books"] if b["slug"] == slug)
    recipe = plan(brief)
    out = ROOT / "books" / f"{slug}.json"
    out.write_text(json.dumps(recipe, indent=2, ensure_ascii=False))
    print(f"wrote {out.relative_to(ROOT)}: {recipe['title']} ({len(recipe['sections'][0]['pages'])} pages)")


if __name__ == "__main__":
    main()
