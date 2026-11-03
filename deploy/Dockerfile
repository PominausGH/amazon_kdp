# Weekly KDP book builder. Build from the repo root:
#   docker build -f deploy/Dockerfile -t kdp-weekly .
FROM python:3.13-slim-trixie

RUN apt-get update && apt-get install -y --no-install-recommends \
        librsvg2-bin poppler-utils imagemagick fontconfig fonts-dejavu-core git ca-certificates openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Same fonts as the laptop so layouts (title fitting, labels) render identically.
COPY fonts/*.ttf /usr/local/share/fonts/kdp/
RUN fc-cache -f && fc-list | grep -q "Ubuntu" && magick -version | head -1

WORKDIR /repo
# The repo itself is bind-mounted at /repo so the job can commit and push its output.
COPY deploy/run-weekly.sh /usr/local/bin/run-weekly
ENTRYPOINT ["/usr/local/bin/run-weekly"]
