"""The weekly job: build the next 2 books from books/queue.json, ready to upload.

    python -m kdp.weekly            # build the next 2 due books
    python -m kdp.weekly --dry-run  # show what would be built and the cost estimate

Steps per book: plan recipe (LLM) -> 50 AI pages -> AI review, redraw failures
(max 2 rounds) -> 3 cover options -> AI picks one -> build PDFs -> KDP spec QA.
It never touches KDP: uploading and publishing stay with a human.
Writes reports/<date>.md and exits non-zero if anything needs attention.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
import traceback
from pathlib import Path

from . import aiart, aipages, book, plan, qa, review
from .llm import credit_remaining

ROOT = Path(__file__).resolve().parent.parent
QUEUE = ROOT / "books" / "queue.json"
REPORTS = ROOT / "reports"
PER_WEEK = 2
COST_PER_BOOK = 7.0  # USD: ~50 pages x $0.10 + redraws + 3 4K covers + LLM calls
MAX_REDRAW_ROUNDS = 2


def due_books(q: dict, today: dt.date, n: int) -> list[dict]:
    out = []
    for b in q["books"]:
        if b.get("status") != "todo":
            continue
        nb = b.get("not_before")
        if nb and dt.date.fromisoformat(nb) > today:
            continue
        out.append(b)
        if len(out) == n:
            break
    return out


def save_queue(q: dict):
    QUEUE.write_text(json.dumps(q, indent=2, ensure_ascii=False) + "\n")


def make_pages(slug: str, recipe_path: Path, log: list[str]) -> list[str]:
    """Generate, review, redraw. Returns labels of pages still failing."""
    cfg = json.loads(recipe_path.read_text())
    ages = cfg.get("reading_age", "2-5")
    pages = cfg["sections"][0]["pages"]
    run_gen = lambda: subprocess.run([sys.executable, "-m", "kdp.aipages", str(recipe_path), "--jobs", "5"],
                                     cwd=ROOT, check=False, capture_output=True, text=True)
    run_gen()
    failing = []
    for rnd in range(MAX_REDRAW_ROUNDS + 1):
        items = [(aipages.page_path(slug, i, p["subject"]), p["subject"]) for i, p in enumerate(pages, 1)]
        missing = [p for p, _ in items if not p.exists()]
        present = [(p, s) for p, s in items if p.exists()]
        results = review.review_pages(present, ages)
        bad = [p for p, r in results.items() if not r["ok"]]
        failing = [(p, results[p]["problems"]) for p in bad] + [(p, ["not generated"]) for p in missing]
        log.append(f"  review round {rnd}: {len(present) - len(bad)}/{len(items)} pages pass")
        if not failing or rnd == MAX_REDRAW_ROUNDS:
            break
        for p, probs in failing:
            log.append(f"    redraw {p.name}: {'; '.join(probs)[:120]}")
            p.unlink(missing_ok=True)
        run_gen()
    return [f"{p.name}: {'; '.join(probs)}" for p, probs in failing]


def make_cover(slug: str, cfg: dict, log: list[str], n=3) -> Path | None:
    out = ROOT / "art" / slug
    out.mkdir(parents=True, exist_ok=True)
    opts = []
    for i in range(1, n + 1):
        f = out / f"option-{i}.png"
        if not f.exists():
            img, model = aiart.generate(f"{aiart.STYLE}\n\nScene: {cfg['cover_prompt']}\n\nVariation {i}.")
            f.write_bytes(img)
        opts.append(f)
    best, why = review.pick_cover(opts, cfg["title"])
    log.append(f"  cover: picked option {best} ({why})")
    return opts[best - 1] if best else None


def build_one(b: dict, log: list[str]) -> dict:
    slug = b["slug"]
    recipe_path = ROOT / "books" / f"{slug}.json"
    result = {"slug": slug, "problems": []}
    if not b.get("prebuilt"):
        if not recipe_path.exists():
            recipe = plan.plan(b)
            recipe_path.write_text(json.dumps(recipe, indent=2, ensure_ascii=False))
            log.append(f"  planned: {recipe['title']}")
        result["problems"] += make_pages(slug, recipe_path, log)
        cfg = json.loads(recipe_path.read_text())
        if not cfg.get("cover_art"):
            cover = make_cover(slug, cfg, log)
            if cover is None:
                result["problems"].append("no acceptable cover option: regenerate art/<slug>/option-*.png")
            else:
                cfg["cover_art"] = str(cover.relative_to(ROOT))
                recipe_path.write_text(json.dumps(cfg, indent=2, ensure_ascii=False))
    if result["problems"]:
        log.append(f"  NOT built: {len(result['problems'])} problems")
        return result
    out = book.build(recipe_path)
    errs = qa.check(out)
    result["problems"] += [f"QA: {e}" for e in errs]
    result["listing"] = json.loads((out / "listing.json").read_text())
    log.append(f"  built {out.relative_to(ROOT)}: {result['listing']['page_count']} pages, QA {'PASS' if not errs else 'FAIL'}")
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--today", help="override date (YYYY-MM-DD) for testing")
    a = ap.parse_args()
    today = dt.date.fromisoformat(a.today) if a.today else dt.date.today()
    q = json.loads(QUEUE.read_text())
    books = due_books(q, today, PER_WEEK)
    need = sum(0 if b.get("prebuilt") else COST_PER_BOOK for b in books)
    left = credit_remaining()
    log = [f"# KDP weekly build {today}", "",
           f"Books due: {', '.join(b['slug'] for b in books) or 'none'}",
           f"Estimated cost ${need:.2f}; OpenRouter credit left: {'no limit' if left is None else f'${left:.2f}'}", ""]
    if a.dry_run:
        print("\n".join(log))
        return 0
    if left is not None and left < need:
        log.append(f"**STOPPED: not enough OpenRouter credit (${left:.2f} < ${need:.2f}). "
                   f"Raise the key limit at https://openrouter.ai/settings/keys**")
        return finish(log, today, ok=False)
    ok = True
    for b in books:
        log.append(f"## {b['slug']}")
        try:
            r = build_one(b, log)
        except Exception as e:  # one book failing must not lose the other
            r = {"slug": b["slug"], "problems": [f"crashed: {e}"]}
            log.append("```\n" + traceback.format_exc()[-1500:] + "\n```")
        if r["problems"]:
            ok = False
            b["status"] = "needs-attention"
            log += ["  **Needs attention:**"] + [f"  - {p}" for p in r["problems"][:15]]
        else:
            b["status"] = "built"
            b["built"] = str(today)
            L = r["listing"]
            log += [f"  **Ready to upload:** {L['title']}: {L['subtitle']}",
                    f"  - files: output/{b['slug']}/interior.pdf, cover.pdf, listing.json",
                    f"  - preview: output/{b['slug']}/contact_sheet.png, cover_preview-1.png"]
        log.append("")
        save_queue(q)
    log.append("Next step: tell Claude \"upload this week's books\". Publishing stays a human click.")
    return finish(log, today, ok)


def finish(log: list[str], today: dt.date, ok: bool) -> int:
    REPORTS.mkdir(exist_ok=True)
    f = REPORTS / f"{today}.md"
    f.write_text("\n".join(log) + "\n")
    print("\n".join(log))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
