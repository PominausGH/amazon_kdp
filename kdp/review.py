"""AI quality review: checks every interior page and picks the best cover option.

Replaces the by-eye review: stray text, borders, mockups, clutter and broken
anatomy are the things that got pages redrawn by hand in the first two books.
"""
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .llm import REVIEWER, LLMError, chat_json, image_part

PAGE_RUBRIC = """You are checking ONE page of a colouring book for {ages} year olds. Intended subject: "{subject}".
FAIL the page if ANY of these are true:
1. any letters, words, numbers or writing anywhere (including on signs, vehicles, labels)
2. a border or frame drawn around the whole picture
3. it is a photo or mockup instead of flat line art
4. large solid black filled areas (small eyes/pupils are fine)
5. {detail_rule}
6. the subject is not clearly recognisable as the intended subject
7. visible drawing glitches: extra/missing limbs, merged or floating parts, broken outlines
Reply JSON only: {{"ok": true|false, "problems": ["short reason", ...]}}"""

COVER_RUBRIC = """These are {n} candidate front-cover illustrations for a children's colouring book: "{title}".
The title will be overlaid on the TOP ~30% of the image. Pick the best one for selling on Amazon.
Disqualify any that: contain letters/words/numbers, are a photo/mockup of a book, have important content in the top 30%,
or have obvious drawing glitches.
Reply JSON only: {{"best": <1-based index or 0 if all disqualified>, "reasons": "one sentence"}}"""


DETAIL_RULES = {
    "toddler": "too much fine detail or clutter for a toddler (should be big simple shapes)",
    "kids": "so much tiny detail that a 4-8 year old could not colour it",
    "detailed": "too SIMPLE for older kids/adults (should be a full detailed scene with many regions), or regions so tiny they are just texture",
    "cozy": "messy or chaotic instead of calm and cute, or line work too thin/fine for a 'bold and easy' style",
}


def review_page(path: Path, subject: str, ages: str, style: str = "toddler") -> dict:
    try:
        r = chat_json([{"role": "user", "content": [
            {"type": "text", "text": PAGE_RUBRIC.format(subject=subject, ages=ages, detail_rule=DETAIL_RULES[style])},
            image_part(path)]}], REVIEWER, max_tokens=300, temperature=0)
        return {"ok": bool(r.get("ok")), "problems": r.get("problems", [])}
    except LLMError as e:
        # A reviewer outage must not silently pass pages: report as not reviewed.
        return {"ok": False, "problems": [f"review failed: {e}"], "error": True}


def review_pages(items: list[tuple[Path, str]], ages: str, style: str = "toddler", jobs=6) -> dict[Path, dict]:
    with ThreadPoolExecutor(jobs) as ex:
        res = ex.map(lambda it: review_page(it[0], it[1], ages, style), items)
    return {p: r for (p, _), r in zip(items, res)}


def pick_cover(paths: list[Path], title: str) -> tuple[int, str]:
    content = [{"type": "text", "text": COVER_RUBRIC.format(n=len(paths), title=title)}]
    for i, p in enumerate(paths, 1):
        content += [{"type": "text", "text": f"Option {i}:"}, image_part(p, 768)]
    r = chat_json([{"role": "user", "content": content}], REVIEWER, max_tokens=300, temperature=0)
    return int(r.get("best", 0)), r.get("reasons", "")


if __name__ == "__main__":
    import sys
    p = Path(sys.argv[1])
    print(json.dumps(review_page(p, sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "2-5"), indent=1))
