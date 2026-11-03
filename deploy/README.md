# Deploying the weekly builder (VPS2 / openrouter box)

Runs every **Monday 08:00 AEST** (Sunday 22:00 UTC), right after KDP's weekly
title limit resets (Sunday 00:00 UTC). It builds the next 2 due books from `books/queue.json`,
commits the PDFs and a report to GitHub, and opens a GitHub issue, which emails you.

```bash
ssh openrouter
sudo mkdir -p /opt/docker/kdp-weekly && cd /opt/docker/kdp-weekly
git clone -b worktree-kdp-pipeline git@github.com:PominausGH/amazon_kdp.git repo   # needs a deploy key with write access
mkdir -p secrets && chmod 700 secrets
# secrets/env  (chmod 600):
#   OPENROUTER_API_KEY=sk-or-...
#   GH_TOKEN=github_pat_...   (fine-grained, this repo only, Issues: read/write)
docker build -f repo/deploy/Dockerfile -t kdp-weekly repo
# test without spending money:
docker run --rm --env-file secrets/env -v $PWD/repo:/repo -v ~/.ssh:/root/.ssh:ro --entrypoint python3 kdp-weekly -m kdp.weekly --dry-run
```

Cron (`crontab -e` as the user that owns the repo):

```
0 22 * * 0  cd /opt/docker/kdp-weekly && docker run --rm --env-file secrets/env -v $PWD/repo:/repo -v $HOME/.ssh:/root/.ssh:ro kdp-weekly >> weekly.log 2>&1
```

The job never logs in to KDP. Uploading and **publishing stay with a human**
(say "upload this week's books" to Claude on the laptop).
