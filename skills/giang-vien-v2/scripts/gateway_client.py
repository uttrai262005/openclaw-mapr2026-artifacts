from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def load_gateway_auth() -> Tuple[str, str]:
    token = os.environ.get("OPENCLAW_GATEWAY_TOKEN", "").strip()
    base_url = os.environ.get("OPENCLAW_GATEWAY_URL", "").strip()

    cfg_path = Path.home() / ".openclaw" / "openclaw.json"
    if cfg_path.exists() and (not token or not base_url):
        try:
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            port = cfg.get("gateway", {}).get("port", 18789)
            if not base_url:
                base_url = f"http://127.0.0.1:{port}"
            if not token:
                token = ((cfg.get("gateway", {}).get("auth", {}) or {}).get("token", "") or "").strip()
        except Exception:
            pass

    if not base_url:
        base_url = "http://127.0.0.1:18789"
    if not token:
        raise RuntimeError("Missing OpenClaw gateway token (OPENCLAW_GATEWAY_TOKEN or ~/.openclaw/openclaw.json)")

    return base_url.rstrip("/"), token


def _strip_control_chars(s: str) -> str:
    # Remove ASCII control chars that break json.loads (keep \n \r \t)
    return "".join(ch for ch in s if (ch >= " " or ch in "\n\r\t"))


def extract_json_object(text: str) -> Dict[str, Any]:
    text = _strip_control_chars((text or "").strip())
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass

    s = text.find("{")
    e = text.rfind("}")
    if s != -1 and e != -1 and e > s:
        obj = json.loads(text[s : e + 1])
        if isinstance(obj, dict):
            return obj
    raise ValueError(f"Could not parse JSON from model output: {text[:2000]}")


def chat_completion(
    messages: List[Dict[str, str]],
    *,
    temperature: float = 0.1,
    max_tokens: int = 700,
    model: str = "openclaw",
    agent_id: str = "main",
    timeout_s: int = 180,
    retries: int = 3,
    user: str = "",
) -> str:
    base_url, token = load_gateway_auth()
    url = f"{base_url}/v1/chat/completions"

    payload: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if user:
        payload["user"] = user

    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "x-openclaw-agent-id": agent_id,
    }

    last_err: Optional[Exception] = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                body = resp.read().decode("utf-8", errors="ignore")
            j = json.loads(body)
            return j["choices"][0]["message"]["content"]
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError) as e:
            last_err = e
            msg = str(e).lower()
            if attempt < retries and ("429" in msg or "rate" in msg or "timeout" in msg):
                time.sleep(min(30.0, 2.0 * (attempt + 1)))
                continue
            raise RuntimeError(f"Gateway completion failed: {e}") from e

    raise RuntimeError(f"Gateway completion failed: {last_err}")
