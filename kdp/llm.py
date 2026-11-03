"""Small OpenRouter chat client for planning (text) and page review (vision)."""
from __future__ import annotations

import base64
import json
import re
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

from .aiart import GeminiError, openrouter_key

API = "https://openrouter.ai/api/v1/chat/completions"
PLANNER = "anthropic/claude-sonnet-5.5"
REVIEWER = "anthropic/claude-haiku-5.5"


class LLMError(RuntimeError):
    pass


def _key() -> str:
    k = openrouter_key()
    if not k:
        raise LLMError("OPENROUTER_API_KEY not configured")
    return k


def image_part(path: Path, max_px=640) -> dict:
    """Downscale before sending: review needs shape, not print resolution."""
    png = subprocess.run(["magick", str(path), "-resize", f"{max_px}x{max_px}>", "png:-"],
                         capture_output=True, check=True).stdout
    return {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(png).decode()}}


def chat(messages: list, model: str, max_tokens=4000, temperature=0.7) -> str:
    body = {"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature}
    req = urllib.request.Request(API, data=json.dumps(body).encode(), headers={
        "Content-Type": "application/json", "Authorization": f"Bearer {_key()}", "X-Title": "amazon_kdp"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        raise LLMError(f"{model}: HTTP {e.code} {e.read().decode(errors='replace')[:300]}") from e
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        raise LLMError(f"{model}: unexpected response {json.dumps(data)[:300]}") from e


def chat_json(messages: list, model: str, **kw):
    """Ask for JSON and parse it, tolerating ```json fences."""
    text = chat(messages, model, **kw)
    m = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    raw = m.group(1) if m else text
    start = min([i for i in (raw.find("{"), raw.find("[")) if i >= 0], default=0)
    try:
        return json.loads(raw[start:])
    except json.JSONDecodeError as e:
        raise LLMError(f"{model}: reply was not JSON: {text[:300]}") from e


def credit_remaining() -> float | None:
    """USD left on the key's limit (None = no limit set)."""
    req = urllib.request.Request("https://openrouter.ai/api/v1/key", headers={"Authorization": f"Bearer {_key()}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["data"].get("limit_remaining")


__all__ = ["chat", "chat_json", "image_part", "credit_remaining", "LLMError", "GeminiError", "PLANNER", "REVIEWER"]
