from __future__ import annotations

import os
from .diff import collect_git_diff
from .review import analyze_paths, render_summary
from .github_api import read_pr_event, post_issue_comment


def main() -> int:
    event = read_pr_event()
    if not event or event.get("pull_request") is None:
        print("This action must run on pull_request events.")
        return 1

    pr = event["pull_request"]
    number = int(pr["number"])
    base_sha = pr["base"]["sha"]
    head_sha = pr["head"]["sha"]

    owner_repo = pr["base"]["repo"]["full_name"].split("/")
    owner, repo = owner_repo[0], owner_repo[1]

    token = os.getenv("INPUT_GITHUB_TOKEN") or os.getenv("GITHUB_TOKEN") or ""
    model = os.getenv("INPUT_MODEL", "")
    base_url = os.getenv("INPUT_BASE_URL", "")
    max_comments = int(os.getenv("INPUT_MAX_COMMENTS", "50"))
    use_llm = os.getenv("INPUT_USE_LLM", "false").lower() == "true"

    rev_range = f"{base_sha}...{head_sha}"
    diffs = collect_git_diff(rev_range)
    targets = [d.path for d in diffs]

    res = analyze_paths(
        targets=targets,
        file_diffs=diffs,
        use_llm=use_llm,
        model=model,
        base_url=base_url,
        max_comments=max_comments,
    )

    body = render_summary(res)
    ok = post_issue_comment(owner, repo, number, body, token)
    print("Posted PR comment:" if ok else "Failed to post PR comment.")
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
