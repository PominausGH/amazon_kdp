"""Chat client for planning (text) and page review (vision): local `claude` CLI by default,
OpenRouter when KDP_LLM_BACKEND=openrouter (e.g. on the VPS, where there is no claude CLI)."""
from __future__ import annotations

import base64
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

from .aiart import GeminiError, openrouter_key

API = "https://openrouter.ai/api/v1/chat/completions"
PLANNER = "anthropic/claude-sonnet-5.5"
REVIEWER = "anthropic/claude-haiku-5.5"
# "local" (default) = the `claude` CLI on this machine (subscription, free per call).
# "openrouter" = paid API: only when explicitly set (KDP_LLM_BACKEND=openrouter). Never a silent fallback.
BACKEND = os.environ.get("KDP_LLM_BACKEND", "local")


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


def _local_model(model: str) -> str:
    for alias in ("haiku", "sonnet", "opus"):
        if alias in model:
            return alias
    return "sonnet"


def chat_local(messages: list, model: str, timeout=600) -> str:
    """Run the prompt through the local `claude` CLI (the user's subscription, no OpenRouter cost).
    Images are written to a temp dir and read by Claude with the Read tool."""
    with tempfile.TemporaryDirectory(prefix="kdp-llm-") as tmp:
        parts, n = [], 0
        for m in messages:
            content = m["content"]
            if isinstance(content, str):
                parts.append(content)
                continue
            for c in content:
                if c.get("type") == "text":
                    parts.append(c["text"])
                elif c.get("type") == "image_url":
                    n += 1
                    f = Path(tmp) / f"image-{n}.png"
                    f.write_bytes(base64.b64decode(c["image_url"]["url"].split(",", 1)[1]))
                    parts.append(f"[Image {n}: use the Read tool to view {f}]")
        prompt = "\n\n".join(parts)
        if n:
            prompt = (f"First use the Read tool to view all {n} image file(s) listed below, then answer. "
                      "Your final message must be the answer only.\n\n" + prompt)
        cmd = ["claude", "-p", "--model", _local_model(model), "--output-format", "text",
               "--no-session-persistence", "--tools", "Read" if n else "", "--add-dir", tmp]
        if n:
            cmd += ["--allowedTools", "Read"]
        try:
            r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=timeout, cwd=tmp)
        except subprocess.TimeoutExpired as e:
            raise LLMError(f"local claude ({model}): timed out after {timeout}s") from e
        if r.returncode != 0:
            raise LLMError(f"local claude ({model}): exit {r.returncode}: {(r.stderr or r.stdout)[:300]}")
        return r.stdout.strip()


def chat(messages: list, model: str, max_tokens=4000, temperature=0.7) -> str:
    if BACKEND == "local":
        if not shutil.which("claude"):
            raise LLMError("local backend: `claude` CLI not found (set KDP_LLM_BACKEND=openrouter to pay instead)")
        return chat_local(messages, model)
    body ={"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature}
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


def chat_json(messages: list, model: str, retries: int = 3, **kw):
    """Ask for JSON and parse it, tolerating ```json fences and transient empty/malformed replies."""
    last_err: Exception | None = None
    for attempt in range(retries):
        text = chat(messages, model, **kw)
        if not text:
            last_err = LLMError(f"{model}: empty reply (None/blank)")
            time.sleep(2 * (attempt + 1))
            continue
        m = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
        raw = m.group(1) if m else text
        start = min([i for i in (raw.find("{"), raw.find("[")) if i >= 0], default=0)
        try:
            return json.loads(raw[start:])
        except json.JSONDecodeError as e:
            last_err = LLMError(f"{model}: reply was not JSON: {text[:300]}")
            last_err.__cause__ = e
            time.sleep(2 * (attempt + 1))
    raise last_err or LLMError(f"{model}: failed to get JSON")


def credit_remaining() -> float | None:
    """USD actually spendable: the lower of the key's own limit and the shared
    account balance (other projects draw on the same account). None = unlimited."""
    h = {"Authorization": f"Bearer {_key()}"}
    with urllib.request.urlopen(urllib.request.Request("https://openrouter.ai/api/v1/key", headers=h), timeout=30) as r:
        key_left = json.load(r)["data"].get("limit_remaining")
    with urllib.request.urlopen(urllib.request.Request("https://openrouter.ai/api/v1/credits", headers=h), timeout=30) as r:
        c = json.load(r)["data"]
    account_left = (c.get("total_credits") or 0) - (c.get("total_usage") or 0)
    return account_left if key_left is None else min(key_left, account_left)


__all__ = ["chat", "chat_json", "image_part", "credit_remaining", "LLMError", "GeminiError", "PLANNER", "REVIEWER"]
