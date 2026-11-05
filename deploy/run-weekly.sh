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
# Never `reset --hard` here: if last week's push failed, the unpushed commit holds
# books and paid-for AI art. Retry that push first, then rebase onto GitHub's copy.
git fetch -q origin "$BRANCH" && git checkout -q "$BRANCH"
if [ -n "$(git rev-list "origin/$BRANCH..HEAD" 2>/dev/null)" ] && [ -n "${GH_TOKEN:-}" ]; then
    echo "retrying push of unpushed commits from a previous run" >&2
    git push -q "https://x-access-token:${GH_TOKEN}@github.com/${GH_REPO:-PominausGH/amazon_kdp}.git" "HEAD:$BRANCH" || true
    git fetch -q origin "$BRANCH"
fi
git rebase -q "origin/$BRANCH" || { git rebase --abort; echo "rebase failed: building on local copy" >&2; }

TODAY=$(date +%F)
python3 -m kdp.weekly
STATUS=$?

git add -A books art output reports
git commit -q -m "Weekly build $TODAY (exit $STATUS)" || true
if [ -n "${GH_TOKEN:-}" ]; then
    # Token in the URL for this one push only; never written to .git/config.
    git push -q "https://x-access-token:${GH_TOKEN}@github.com/${GH_REPO:-PominausGH/amazon_kdp}.git" "HEAD:$BRANCH" \
        || echo "push failed" >&2
else
    echo "GH_TOKEN not set: results kept on this server only" >&2
fi

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
