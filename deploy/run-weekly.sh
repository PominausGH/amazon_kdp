#!/bin/sh
# Runs inside the container with the repo mounted at /repo.
# Pull latest queue/recipes, build this week's books, commit + push results,
# then open a GitHub issue so the owner gets an email.
set -u
cd /repo
git config --global --add safe.directory /repo
git config user.name  "kdp-weekly (VPS2)"
git config user.email "kdp-weekly@localhost"

BRANCH=${KDP_BRANCH:-worktree-kdp-pipeline}
git fetch -q origin "$BRANCH" && git checkout -q "$BRANCH" && git reset -q --hard "origin/$BRANCH"

TODAY=$(date +%F)
python3 -m kdp.weekly
STATUS=$?

git add -A books art output reports
git commit -q -m "Weekly build $TODAY (exit $STATUS)" || true
git push -q origin "$BRANCH" || echo "push failed" >&2

# Email notification via a GitHub issue (needs GH_TOKEN with issues:write on the repo).
if [ -n "${GH_TOKEN:-}" ] && [ -f "reports/$TODAY.md" ]; then
    if [ "$STATUS" -eq 0 ]; then TITLE="KDP: books ready to upload ($TODAY)"; else TITLE="KDP: weekly build needs attention ($TODAY)"; fi
    python3 - "$TITLE" "reports/$TODAY.md" <<'EOF'
import json, os, sys, urllib.request
title, path = sys.argv[1], sys.argv[2]
body = open(path).read()[:60000]
req = urllib.request.Request(
    f"https://api.github.com/repos/{os.environ.get('GH_REPO', 'PominausGH/amazon_kdp')}/issues",
    data=json.dumps({"title": title, "body": body}).encode(),
    headers={"Authorization": f"Bearer {os.environ['GH_TOKEN']}", "Accept": "application/vnd.github+json"})
print("issue:", json.load(urllib.request.urlopen(req, timeout=30))["html_url"])
EOF
fi
exit $STATUS
