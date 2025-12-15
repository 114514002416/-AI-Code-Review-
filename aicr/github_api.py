from __future__ import annotations

import json
import os
import requests
from typing import Optional


def post_issue_comment(owner: str, repo: str, issue_number: int, body: str, token: str) -> bool:
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    }
    try:
        resp = requests.post(url, headers=headers, data=json.dumps({"body": body}), timeout=30)
        return resp.status_code < 300
    except Exception:
        return False


def read_pr_event(env_path: Optional[str] = None) -> Optional[dict]:
    path = env_path or os.getenv("GITHUB_EVENT_PATH")
    if not path or not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None
