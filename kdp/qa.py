"""Check built books against KDP paperback specs before upload.
Usage: python -m kdp.qa output/<slug> [...]   (exit 1 on any failure)"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from . import specs


def pdfinfo(path: Path) -> dict:
    out = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True, check=True).stdout
    pages = int(re.search(r"Pages:\s+(\d+)", out).group(1))
    w, h = map(float, re.search(r"Page size:\s+([\d.]+) x ([\d.]+)", out).groups())
    return {"pages": pages, "w_in": w / 72, "h_in": h / 72, "bytes": path.stat().st_size}


def check(book_dir: Path) -> list[str]:
    errs = []
    listing = json.loads((book_dir / "listing.json").read_text())
    tw, th = specs.TRIMS[listing["trim"]]
    i = pdfinfo(book_dir / "interior.pdf")
    if abs(i["w_in"] - tw) > .01 or abs(i["h_in"] - th) > .01:
        errs.append(f"interior page {i['w_in']:.3f}x{i['h_in']:.3f} != trim {tw}x{th}")
    if i["pages"] < specs.MIN_PAGES:
        errs.append(f"only {i['pages']} pages (min {specs.MIN_PAGES})")
    if i["pages"] % 2:
        errs.append("odd page count")
    if i["pages"] != listing["page_count"]:
        errs.append("listing page_count mismatch")
    if i["bytes"] > 650e6:
        errs.append("interior over 650MB")
    c = pdfinfo(book_dir / "cover.pdf")
    cw, ch = specs.cover_size(listing["trim"], i["pages"])
    if c["pages"] != 1 or abs(c["w_in"] - cw) > .01 or abs(c["h_in"] - ch) > .01:
        errs.append(f"cover {c['w_in']:.4f}x{c['h_in']:.4f} != expected {cw:.4f}x{ch:.4f}")
    if len(listing["keywords"]) > 7:
        errs.append("more than 7 keywords")
    if any(len(k) > 50 for k in listing["keywords"]):
        errs.append("keyword over 50 chars")
    if len(listing["title"]) + len(listing.get("subtitle", "")) > 200:
        errs.append("title+subtitle over 200 chars")
    return errs


if __name__ == "__main__":
    bad = 0
    for d in map(Path, sys.argv[1:]):
        errs = check(d)
        bad += bool(errs)
        print(f"{'FAIL' if errs else 'PASS'}  {d.name}" + "".join(f"\n      - {e}" for e in errs))
    sys.exit(1 if bad else 0)
