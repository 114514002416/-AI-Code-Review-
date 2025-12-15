from __future__ import annotations

import dataclasses
import os
import subprocess
from typing import List, Optional


@dataclasses.dataclass
class FileDiff:
    path: str
    added_lines: set[int]
    removed_lines: set[int]


def _run(cmd: list[str], cwd: Optional[str] = None) -> str:
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)
    if res.returncode != 0:
        return ""
    return res.stdout


def _merge_base() -> Optional[str]:
    # Try to find merge-base with origin/main else main
    for base in ("origin/main", "origin/master", "main", "master"):
        out = _run(["git", "merge-base", base, "HEAD"]) or ""
        sha = out.strip()
        if sha:
            return sha
    return None


def collect_git_diff(rev_range: Optional[str] = None, repo_root: Optional[str] = None) -> List[FileDiff]:
    repo_root = repo_root or os.getcwd()
    if rev_range:
        range_arg = rev_range
    else:
        base = _merge_base()
        range_arg = f"{base}...HEAD" if base else "HEAD^...HEAD"

    # Use unified=0 to get exact line numbers of added hunks
    diff = _run([
        "git", "diff", "--unified=0", "--no-color", range_arg, "--", "."
    ], cwd=repo_root)

    files: list[FileDiff] = []
    path = None
    added: set[int] = set()
    removed: set[int] = set()

    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            # finalize previous
            if path is not None:
                files.append(FileDiff(path=path, added_lines=added, removed_lines=removed))
            path = line[6:]
            added = set()
            removed = set()
        elif line.startswith("@@"):
            # Example: @@ -12,0 +13,5 @@
            try:
                header = line.split("@@")[1].strip()
                left, right = header.split(" ")[:2]
                plus = right.lstrip("+")
                start_count = plus.split(",")
                start = int(start_count[0])
                count = int(start_count[1]) if len(start_count) > 1 else 1
                for i in range(start, start + count):
                    added.add(i)
            except Exception:
                # ignore parse errors
                pass
        elif line.startswith("-") and not line.startswith("--- "):
            # removed lines don't carry numbers here; we captured via header
            pass

    if path is not None:
        files.append(FileDiff(path=path, added_lines=added, removed_lines=removed))

    return files
