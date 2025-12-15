import argparse
import os
import sys
from .diff import collect_git_diff
from .review import analyze_paths, render_summary


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="aicr",
        description="Open-source AI Code Review (CLI)",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=None,
        help="Files or directories to review. If omitted, use git diff.",
    )
    parser.add_argument(
        "--rev",
        default=None,
        help="Git revision range (e.g. origin/main...HEAD). Overrides automatic base/head detection.",
    )
    parser.add_argument(
        "--use-llm",
        action="store_true",
        help="Enable LLM suggestions if API is configured.",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("AICR_MODEL", ""),
        help="LLM model name (OpenAI-compatible or Ollama).",
    )
    parser.add_argument(
        "--base-url",
        default=os.getenv("AICR_BASE_URL", ""),
        help="LLM base URL for OpenAI-compatible or Ollama API.",
    )
    parser.add_argument(
        "--max-comments",
        type=int,
        default=int(os.getenv("AICR_MAX_COMMENTS", "50")),
        help="Maximum number of comments in the output.",
    )

    args = parser.parse_args()

    if args.paths:
        targets = args.paths
        file_diffs = None
    else:
        file_diffs = collect_git_diff(args.rev)
        targets = [fd.path for fd in file_diffs]

    results = analyze_paths(
        targets=targets,
        file_diffs=file_diffs,
        use_llm=args.use_llm,
        model=args.model,
        base_url=args.base_url,
        max_comments=args.max_comments,
    )

    print(render_summary(results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
