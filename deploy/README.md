# Deploying the weekly builder (VPS2 / openrouter box)

Runs every **Monday 08:00 AEST** (Sunday 22:00 UTC), right after KDP's weekly
title limit resets (Sunday 00:00 UTC). It builds the next 2 due books from `books/queue.json`,
commits the PDFs and a report to GitHub, and opens a GitHub issue, which emails you.

Installed on VPS2 (Tailscale `srv1351673-openrouter`, 100.111.4.8) on 2026-11-03:

```bash
ssh root@100.111.4.8          # Tailscale SSH
cd /opt/docker/kdp-weekly     # repo/ (public clone over https), secrets/env (600)
# secrets/env:
#   OPENROUTER_API_KEY=sk-or-...
#   GH_TOKEN=github_pat_...   (fine-grained, this repo only: Contents read/write + Issues read/write)
docker build -f repo/deploy/Dockerfile -t kdp-weekly repo
# test without spending money:
docker run --rm --env-file secrets/env -v $PWD/repo:/repo --entrypoint python3 kdp-weekly -m kdp.weekly --dry-run
```

Cron (root, server clock is UTC):

```
0 22 * * 0  cd /opt/docker/kdp-weekly && git -C repo pull -q && docker build -q -f repo/deploy/Dockerfile -t kdp-weekly repo >/dev/null && docker run --rm --env-file secrets/env -v $PWD/repo:/repo kdp-weekly >> weekly.log 2>&1
```

Without `GH_TOKEN` the job still builds, but the results stay on the server and no email is sent.

The job never logs in to KDP. Uploading and **publishing stay with a human**
(say "upload this week's books" to Claude on the laptop).
