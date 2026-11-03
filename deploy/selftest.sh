#!/bin/sh
# Free container self-test: rebuild an existing book from cached art, run KDP QA,
# and dry-run the weekly planner. Spends no OpenRouter credit except a key check.
# docker run --rm -v $PWD:/repo -v ~/.config/kdp:/root/.config/kdp:ro --entrypoint /repo/deploy/selftest.sh kdp-weekly
set -e
cp -r /repo /tmp/r
cd /tmp/r
python3 -m kdp.book books/christmas-bold-easy.json
python3 -m kdp.qa output/christmas-bold-easy
python3 -m kdp.weekly --dry-run --today 2026-11-10
mkdir -p /repo/.playwright-mcp
cp output/christmas-bold-easy/cover_preview-1.png /repo/.playwright-mcp/docker-cover.png
echo SELFTEST OK
