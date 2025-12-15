from __future__ import annotations

import os
import requests
from typing import Optional


def _env(key: str, default: str = "") -> str:
    return os.getenv(key, default)


def have_openai_like_creds() -> bool:
    return bool(_env("OPENAI_API_KEY") or _env("AICR_API_KEY"))


def suggest_with_llm(prompt: str, model: str = "", base_url: str = "") -> Optional[str]:
    api_key = _env("AICR_API_KEY") or _env("OPENAI_API_KEY")
    if not api_key:
        return None

    base = base_url or _env("AICR_BASE_URL") or "https://api.openai.com/v1"
    mdl = model or _env("AICR_MODEL") or "gpt-4o-mini"

    url = f"{base}/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {
        "model": mdl,
        "messages": [
            {"role": "system", "content": "You are a concise, rigorous code reviewer."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 600,
    }

    try:
        resp = requests.post(url, headers=headers, json=body, timeout=60)
        if resp.status_code >= 300:
            return None
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return None
