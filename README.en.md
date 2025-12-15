# AICR — Open-source AI Code Review (LLM + Heuristics)

[![Release](https://img.shields.io/github/v/release/114514002416/-AI-Code-Review-?sort=semver)](https://github.com/114514002416/-AI-Code-Review-/releases)
[![GitHub Action](https://img.shields.io/badge/GitHub%20Action-AI%20Code%20Review-blue)](https://github.com/marketplace?type=actions&query=ai+code+review)
[![License](https://img.shields.io/badge/License-Open--Source-green)](#)

AICR is an open-source AI-powered Code Review tool: run locally as a CLI or in GitHub as a Composite Action. It ships with useful static heuristics and can optionally integrate an LLM (OpenAI-compatible / local Ollama) for higher quality suggestions.

SEO/Discoverability keywords:
- AI Code Review, PR Review, GitHub Action, LLM, OpenAI, Ollama, GPT-4o, Code Quality, Static Analysis, Security, SAST

## Features
- Heuristics: TODO/FIXME, `eval/exec`, `subprocess(..., shell=True)`, unsafe `pickle` deserialization, suspected secrets, long functions/blocks
- Git diff aware: focuses on added lines
- Optional LLM summary: OpenAI-compatible API or Ollama (via `base-url`)
- GitHub Action: posts a single summarized PR comment (no spam)

## Quickstart (CLI)
```bash
pip install -e .
aicr                 # review current git diff
#aicr src/ tests/    # review specific paths

# Enable LLM suggestions (requires API)
export OPENAI_API_KEY=sk-...
aicr --use-llm --model gpt-4o-mini --base-url https://api.openai.com/v1
```

## GitHub Action
```yaml
name: AI Code Review
on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: your-org/your-repo@v1  # or uses: ./ if placed at repo root
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          use-llm: false
          max-comments: 50
          # model: gpt-4o-mini
          # base-url: https://api.openai.com/v1
```

Action inputs:
- `github-token` (optional): defaults to `GITHUB_TOKEN`
- `use-llm` (optional): `true/false` to enable LLM
- `model` (optional): LLM model name
- `base-url` (optional): OpenAI-compatible API or Ollama base URL, e.g., `http://localhost:11434/v1`
- `max-comments` (optional): max heuristic issues (default 50)

If enabling LLM, set secrets:
- `OPENAI_API_KEY` or `AICR_API_KEY`

### Improve Marketplace & Search visibility
- Set repository topics: `ai`, `code-review`, `github-actions`, `static-analysis`, `security`, `llm`, `openai`, `ollama`
  ```bash
  gh repo edit --add-topic ai --add-topic code-review --add-topic github-actions \
    --add-topic static-analysis --add-topic security --add-topic llm --add-topic openai --add-topic ollama
  ```
- Create a stable tag that always points to the latest release:
  ```bash
  git tag v0.1.0 && git push origin v0.1.0
  git tag -f v1 && git push -f origin v1
  ```
- Write a clear Release description and keep keywords visible in README.

## Development
```bash
pip install -e .
aicr --help
```

Issues and PRs are welcome!
