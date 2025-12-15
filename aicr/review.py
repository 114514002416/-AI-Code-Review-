from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable, List, Optional

from .diff import FileDiff
from .heuristics import Issue, simple_checks
from .llm import suggest_with_llm, have_openai_like_creds


@dataclass
class ReviewResult:
    issues: List[Issue]
    llm_summary: Optional[str]


def _read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return ""


def analyze_paths(
    targets: Iterable[str],
    file_diffs: Optional[Iterable[FileDiff]] = None,
    use_llm: bool = False,
    model: str = "",
    base_url: str = "",
    max_comments: int = 50,
) -> ReviewResult:
    path_set = set(targets)
    diff_map = {d.path: d for d in (file_diffs or [])}

    all_issues: List[Issue] = []
    for p in sorted(path_set):
        # Skip obvious binaries
        if any(p.endswith(ext) for ext in (".png", ".jpg", ".jpeg", ".gif", ".pdf", ".lock", ".ico")):
            continue
        content = _read_file(p)
        if not content:
            continue

        issues = simple_checks(p, content)

        # focus on added lines if diff available
        if p in diff_map and diff_map[p].added_lines:
            added = diff_map[p].added_lines
            issues = [i for i in issues if (i.line is None or i.line in added)]

        all_issues.extend(issues)

    all_issues = all_issues[:max_comments]

    llm_summary: Optional[str] = None
    if use_llm and have_openai_like_creds():
        sample = []
        for p in list(path_set)[:5]:
            c = _read_file(p)
            if c:
                sample.append(f"FILE: {p}\n\n{c[:4000]}")
        prompt = (
            "Act as a senior reviewer. Provide concise, prioritized review points "
            "(max 10 bullets) focusing on correctness, security, performance, and maintainability.\n\n"
            + "\n\n".join(sample)
        )
        llm_summary = suggest_with_llm(prompt, model=model, base_url=base_url)

    return ReviewResult(issues=all_issues, llm_summary=llm_summary)


def render_summary(res: ReviewResult) -> str:
    lines: List[str] = []
    if res.llm_summary:
        lines.append("# AI 建议 (LLM)")
        lines.append(res.llm_summary)
        lines.append("")

    lines.append("# 规则与启发式发现")
    if not res.issues:
        lines.append("未发现问题，干得漂亮！")
    else:
        for i in res.issues:
            pos = f"{i.path}:{i.line}" if i.line else i.path
            lines.append(f"- [{i.severity}] {pos} — {i.title}: {i.detail}")
    return "\n".join(lines)
