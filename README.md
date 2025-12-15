# AICR — 开源 AI Code Review（LLM + 启发式）

<p align="center">
	<img src="assets/aicr-logo.svg" alt="AICR: AI Code Review (LLM + Heuristics)" width="520" />
</p>

[![Release](https://img.shields.io/github/v/release/114514002416/-AI-Code-Review-?sort=semver)](https://github.com/114514002416/-AI-Code-Review-/releases)
[![GitHub Action](https://img.shields.io/badge/GitHub%20Action-AI%20Code%20Review-blue)](https://github.com/marketplace?type=actions&query=ai+code+review)
[![License](https://img.shields.io/badge/License-Open--Source-green)](#)

AICR 是一个开源的 AI 代码审查工具：本地作为 CLI 使用，或在 GitHub 中作为 Composite Action 运行。内置静态启发式检查，可选接入 LLM（OpenAI 兼容/本地 Ollama）生成更高质量的审查建议。

面向搜索引擎与 Marketplace 发现的关键词（SEO/Discoverability）：
- AI Code Review, PR Review, GitHub Action, LLM, OpenAI, Ollama, GPT-4o, Code Quality, Static Analysis, Security, SAST
- 代码审查, PR 审查, 静态分析, 安全扫描, 密钥泄露, 可维护性, 自动化, GitHub Actions

## 功能特性
- 启发式检查：TODO/FIXME、`eval/exec`、`subprocess(..., shell=True)`、不安全 `pickle` 反序列化、疑似密钥、过长函数块等
- Git diff 感知：优先关注新增行
- 可选 LLM 总结：OpenAI 兼容 API 或 Ollama（通过 `base-url` 指定）
- GitHub Action：对 PR 自动发表评论（单条汇总，避免过度刷屏）

## 本地快速开始（CLI）

```bash
# 安装（开发目录）
pip install -e .

# 对当前变更执行审查（自动检测 git diff）
aicr

# 指定路径执行审查
aicr src/ tests/

# 启用 LLM 建议（需要 API 配置）
export OPENAI_API_KEY=sk-...
aicr --use-llm --model gpt-4o-mini --base-url https://api.openai.com/v1
```

## GitHub Action 使用

1. 将本仓库作为 Action（或直接复用本仓库）。
2. 在你的仓库添加工作流文件 `.github/workflows/aicr.yml`：

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
			- uses: 你的组织/你的仓库@v1 # 推荐使用版本标签；若在同仓库根目录可改用 ./
				with:
					github-token: ${{ secrets.GITHUB_TOKEN }}
					use-llm: false
					max-comments: 50
					# model: gpt-4o-mini
					# base-url: https://api.openai.com/v1
```

Action 输入参数：
- `github-token`（可选）：默认使用 `GITHUB_TOKEN`
- `use-llm`（可选）：`true/false` 是否启用 LLM
- `model`（可选）：LLM 模型名称
- `base-url`（可选）：OpenAI 兼容 API 或 Ollama 的 base URL，例如 `http://localhost:11434/v1`
- `max-comments`（可选）：最多输出的启发式问题数（默认 50）

如果启用 LLM，请在仓库 Secrets 配置：
- `OPENAI_API_KEY` 或 `AICR_API_KEY`

### 提升 Marketplace 与搜索可见性
- 设置仓库 Topics（强烈推荐）：`ai`, `code-review`, `github-actions`, `static-analysis`, `security`, `llm`, `openai`, `ollama`
	- 可使用命令（需要 gh 登录）：
		```bash
		gh repo edit --add-topic ai --add-topic code-review --add-topic github-actions \
			--add-topic static-analysis --add-topic security --add-topic llm --add-topic openai --add-topic ollama
		```
- 创建稳定版本标签并指向最新发布：
	```bash
	git tag v0.1.0 && git push origin v0.1.0
	git tag -f v1 && git push -f origin v1  # 永远指向最新稳定
	```
- 在 Releases 中撰写清晰的「What’s New」与关键字。
- README 顶部保留清晰关键词与使用示例（已完成）。

## 设计与范围
- 先以启发式保证“即装即用”，LLM 作为可选增强
- 暂以单条 PR 评论汇总，后续可扩展成逐文件/逐行注释
- 不与语言特定 Linter 冲突，更多是补全维度（安全、密钥、复杂度）

## 常见问题
- 无法定位变更？本地 CLI 默认选择 `merge-base` 与 `HEAD` 间的 diff，或使用 `--rev origin/main...HEAD` 指定范围。
- 无法调用 LLM？确认 `OPENAI_API_KEY`（或 `AICR_API_KEY`）和 `--base-url`（若非官方）是否设置正确。

## 开发

```bash
pip install -e .
aicr --help
```

欢迎提 Issue / PR 共同改进。

---

如果希望英文读者也能快速发现，建议同步查看与传播 [README.en.md](README.en.md)。