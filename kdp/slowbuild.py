"""Free, unattended build: pages drawn by Antigravity (agy), reviewed by local Claude.

    nohup python -m kdp.slowbuild christmas-dinosaurs-bold-easy aussie-animals-bold-easy >> reports/slowbuild.log 2>&1 &
    python -m kdp.slowbuild --weekly   # resume 'building-local' books, then start the next 2 due 'todo' books

agy's image quota allows only ~10 pictures per ~5 hours, so this loops: draw what it can,
sleep when the quota is exhausted, carry on. Once every page exists it reviews them,
redraws rejects (max REDRAW_ROUNDS), then builds the PDFs and runs QA if the recipe has
cover_art. Books are done strictly in the order given.

Human overrides: art/<slug>/approved.txt lists page filenames that skip review
(pages a person has looked at and accepted despite reviewer nitpicks).
"""
from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import sys
import time
from pathlib import Path

os.environ.setdefault("KDP_IMAGE_BACKEND", "agy")
os.environ.setdefault("KDP_LLM_BACKEND", "local")

from . import aipages, book, plan, qa, review, weekly  # noqa: E402  (env must be set first)

ROOT = Path(__file__).resolve().parent.parent
REDRAW_ROUNDS = 2
WAIT_S = 30 * 60  # quota resets in hours; check every 30 min


def log(msg: str):
    print(f"[{dt.datetime.now():%Y-%m-%d %H:%M}] {msg}", flush=True)


def page_items(slug: str, cfg: dict) -> list[tuple[Path, str]]:
    pages = cfg["sections"][0]["pages"]
    return [(aipages.page_path(slug, i, p["subject"]), p["subject"]) for i, p in enumerate(pages, 1)]


def draw_missing(slug: str, recipe: Path, cfg: dict):
    """Run the page generator until every page exists, sleeping through quota resets."""
    while True:
        missing = [p for p, _ in page_items(slug, cfg) if not p.exists()]
        if not missing:
            return
        log(f"{slug}: drawing, {len(missing)} pages missing")
        r = subprocess.run([sys.executable, "-m", "kdp.aipages", str(recipe), "--jobs", "1"],
                           cwd=ROOT, capture_output=True, text=True)
        still = sum(1 for p, _ in page_items(slug, cfg) if not p.exists())
        if still and still >= len(missing):  # nothing new: quota exhausted (or agy broken)
            tail = [ln for ln in r.stdout.splitlines() if ln.startswith("FAILED")][-1:]
            log(f"{slug}: no progress; waiting {WAIT_S // 60} min. {tail[0][-200:] if tail else ''}")
            time.sleep(WAIT_S)


def approved(slug: str) -> set[str]:
    f = ROOT / "art" / slug / "approved.txt"
    return set(f.read_text().split()) if f.exists() else set()


def build(slug: str) -> bool:
    recipe = ROOT / "books" / f"{slug}.json"
    cfg = json.loads(recipe.read_text())
    ages = cfg.get("reading_age", "2-5")
    style = cfg["sections"][0].get("style", "toddler")
    for rnd in range(REDRAW_ROUNDS + 1):
        draw_missing(slug, recipe, cfg)
        ok_names = approved(slug)
        todo = [(p, s) for p, s in page_items(slug, cfg) if p.name not in ok_names]
        results = review.review_pages(todo, ages, style, jobs=4)
        rejected = [p for p, r in results.items() if not r["ok"] and not r.get("error")]
        errors = [p for p, r in results.items() if r.get("error")]
        passed = [p for p, r in results.items() if r["ok"]]
        # Passed pages never need reviewing again.
        f = ROOT / "art" / slug / "approved.txt"
        f.write_text("\n".join(sorted(ok_names | {p.name for p in passed})) + "\n")
        log(f"{slug}: review round {rnd}: {len(passed)} passed, {len(rejected)} rejected, "
            f"{len(errors)} reviewer errors, {len(ok_names)} already approved")
        if not rejected or rnd == REDRAW_ROUNDS:
            for p in rejected:
                log(f"  still rejected (check by eye, add to approved.txt to accept): {p.name}: "
                    f"{'; '.join(results[p]['problems'])[:150]}")
            break
        for p in rejected:
            log(f"  redraw {p.name}: {'; '.join(results[p]['problems'])[:120]}")
            p.unlink(missing_ok=True)
    if rejected or errors:
        log(f"{slug}: NOT built: {len(rejected)} rejected, {len(errors)} unreviewed pages")
        return False
    if not cfg.get("cover_art"):
        cover = None
        while cover is None:
            try:
                cover = weekly.make_cover(slug, cfg, notes := [])
                for n in notes:
                    log(f"{slug}:{n}")
            except Exception as e:  # agy quota: options drawn so far are kept on disk
                log(f"{slug}: cover not done ({str(e)[-150:]}); waiting {WAIT_S // 60} min")
                time.sleep(WAIT_S)
                continue
            if cover is None:
                log(f"{slug}: NOT built: no acceptable cover option; delete art/{slug}/option-*.png to redraw")
                return False
        cfg["cover_art"] = str(cover.relative_to(ROOT))
        recipe.write_text(json.dumps(cfg, indent=2, ensure_ascii=False))
    out = book.build(recipe)
    errs = qa.check(out)
    log(f"{slug}: built {out.relative_to(ROOT)}; QA {'PASS' if not errs else 'FAIL: ' + '; '.join(errs)}")
    return not errs


def set_status(slug: str, status: str):
    q = json.loads(weekly.QUEUE.read_text())
    for b in q["books"]:
        if b["slug"] == slug:
            b["status"] = status
            if status == "built":
                b["built"] = str(dt.date.today())
    weekly.save_queue(q)


def weekly_slugs() -> list[str]:
    """Books already being built locally, then the next due 'todo' books (planned with local Claude)."""
    q = json.loads(weekly.QUEUE.read_text())
    slugs = [b["slug"] for b in q["books"] if b.get("status") == "building-local"]
    for b in weekly.due_books(q, dt.date.today(), weekly.PER_WEEK):
        recipe = ROOT / "books" / f"{b['slug']}.json"
        if not b.get("prebuilt") and not recipe.exists():
            log(f"{b['slug']}: planning with local Claude")
            recipe.write_text(json.dumps(plan.plan(b), indent=2, ensure_ascii=False))
        set_status(b["slug"], "building-local")
        slugs.append(b["slug"])
    return slugs


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    import fcntl
    lock = open(ROOT / "reports" / ".slowbuild.lock", "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        log("another slowbuild is already running: exiting")
        return
    slugs = weekly_slugs() if args == ["--weekly"] else args
    log(f"books: {', '.join(slugs) or 'none due'}")
    for slug in slugs:
        log(f"=== {slug} ===")
        try:
            ok = build(slug)
            set_status(slug, "built" if ok else "needs-attention")
        except Exception as e:  # keep going with the next book
            log(f"{slug}: crashed: {e!r}")
            set_status(slug, "needs-attention")
    log("all done")


if __name__ == "__main__":
    main()
