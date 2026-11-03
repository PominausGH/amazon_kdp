"""Cover illustrations from Gemini's Nano Banana image models, via OpenRouter
(preferred: OPENROUTER_API_KEY in ~/.config/kdp/openrouter.env) or the Gemini API
directly (GEMINI_API_KEY in ~/.config/kdp/gemini.env). Env vars override files.
Text is never drawn by the model (it misspells); titles are overlaid by cover.py.

Usage: python -m kdp.aiart books/foo.json [--n 3]   -> art/<slug>/option-1.png ...
Then set "cover_art": "art/<slug>/option-2.png" in the recipe and rebuild.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEY_FILE = Path.home() / ".config/kdp/gemini.env"
# Tried in order; first one that the key can use wins.
MODELS = ["gemini-3.1-flash-image-preview", "gemini-2.5-flash-image"]
API = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

STYLE = (
    "Children's colouring book COVER illustration. Style: bold thick clean black outlines, flat bright "
    "cheerful colours, simple rounded cute shapes, no gradients, no shading, no texture, like a modern "
    "kids' sticker or toddler board book. Match the style of simple bold-and-easy colouring pages. "
    "Absolutely NO text, letters, numbers, words, logos or watermarks anywhere in the image. "
    "Leave the TOP 30% of the image as plain simple background (sky or soft pattern) with nothing important "
    "in it, because a title banner will be placed there. Keep the main subjects in the middle and lower "
    "area, away from the edges."
)


class GeminiError(RuntimeError):
    pass


def api_key() -> str:
    if os.environ.get("GEMINI_API_KEY"):
        return os.environ["GEMINI_API_KEY"]
    if KEY_FILE.exists():
        for line in KEY_FILE.read_text().splitlines():
            if line.startswith("GEMINI_API_KEY="):
                return line.split("=", 1)[1].strip()
    raise GeminiError(f"No image key. Put OPENROUTER_API_KEY=... in {OR_KEY_FILE} "
                      f"(or GEMINI_API_KEY=... in {KEY_FILE})")


OR_KEY_FILE = Path.home() / ".config/kdp/openrouter.env"
OR_API = "https://openrouter.ai/api/v1/chat/completions"
OR_MODELS = ["google/gemini-3.1-flash-image", "google/gemini-3.1-flash-image-preview", "google/gemini-2.5-flash-image"]


def openrouter_key() -> str | None:
    if os.environ.get("OPENROUTER_API_KEY"):
        return os.environ["OPENROUTER_API_KEY"]
    if OR_KEY_FILE.exists():
        for line in OR_KEY_FILE.read_text().splitlines():
            if line.startswith("OPENROUTER_API_KEY="):
                return line.split("=", 1)[1].strip()
    return None


def generate_openrouter(key: str, prompt: str, aspect: str) -> tuple[bytes, str]:
    last = None
    for model in OR_MODELS:
        body = {"model": model, "modalities": ["image", "text"],
                "messages": [{"role": "user", "content": prompt}],
                "image_config": {"aspect_ratio": aspect}}
        req = urllib.request.Request(OR_API, data=json.dumps(body).encode(), headers={
            "Content-Type": "application/json", "Authorization": f"Bearer {key}",
            "X-Title": "amazon_kdp cover art"})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                data = json.load(r)
        except urllib.error.HTTPError as e:
            last = f"{model}: HTTP {e.code} {e.read().decode(errors='replace')[:400]}"
            if e.code in (400, 404):
                continue  # model id not available: try next
            raise GeminiError(last) from e  # auth / credit / rate errors: stop and report
        for choice in data.get("choices", []):
            for im in choice.get("message", {}).get("images", []) or []:
                url = im.get("image_url", {}).get("url", "")
                if url.startswith("data:"):
                    return base64.b64decode(url.split(",", 1)[1]), f"openrouter:{model}"
        last = f"{model}: no image in response ({json.dumps(data)[:300]})"
    raise GeminiError(last or "no OpenRouter model available")


def generate(prompt: str, aspect="3:4", size="2K") -> tuple[bytes, str]:
    """OpenRouter if its key is set, otherwise Gemini direct."""
    ork = openrouter_key()
    if ork:
        return generate_openrouter(ork, prompt, aspect)
    key = api_key()
    last = None
    for model in MODELS:
        image_cfg = {"aspectRatio": aspect}
        if "3.1" in model:
            image_cfg["imageSize"] = size
        body = {"contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": image_cfg}}
        req = urllib.request.Request(API.format(model=model), data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json", "x-goog-api-key": key})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                data = json.load(r)
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")[:400]
            last = f"{model}: HTTP {e.code} {msg}"
            if e.code in (400, 404, 403, 429):
                continue  # try the next model; report all if none work
            raise GeminiError(last) from e
        for cand in data.get("candidates", []):
            for part in cand.get("content", {}).get("parts", []):
                if "inlineData" in part:
                    return base64.b64decode(part["inlineData"]["data"]), model
        last = f"{model}: no image in response ({json.dumps(data)[:300]})"
    raise GeminiError(last or "no model available")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("recipe")
    ap.add_argument("--n", type=int, default=3)
    a = ap.parse_args()
    recipe = Path(a.recipe)
    cfg = json.loads(recipe.read_text())
    subject = cfg.get("cover_prompt")
    if not subject:
        sys.exit(f"{recipe} has no cover_prompt")
    out = ROOT / "art" / recipe.stem
    out.mkdir(parents=True, exist_ok=True)
    for i in range(1, a.n + 1):
        img, model = generate(f"{STYLE}\n\nScene: {subject}\n\nVariation {i}.")
        f = out / f"option-{i}.png"
        f.write_bytes(img)
        print(f"{f.relative_to(ROOT)}  ({model}, {len(img) // 1024} KB)")


if __name__ == "__main__":
    main()
