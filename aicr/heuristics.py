from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List, Optional


@dataclass
class Issue:
    path: str
    line: Optional[int]
    severity: str  # INFO/WARN/ERROR
    title: str
    detail: str


TODO_RE = re.compile(r"\b(TODO|FIXME|XXX)\b", re.IGNORECASE)
EVAL_RE = re.compile(r"\b(eval|exec)\b")
SUBPROCESS_SHELL_RE = re.compile(r"subprocess\.[A-Za-z_]+\(.*shell\s*=\s*True")
PICKLE_RE = re.compile(r"pickle\.(loads|load)\(")
SQL_STRING_RE = re.compile(r"SELECT\s+.*\s+FROM\s+.*\+|f\"")
AWS_KEY_RE = re.compile(r"AKIA[0-9A-Z]{16}")
SECRET_MARKER_RE = re.compile(r"(secret|password|token|api[_-]?key)\s*[:=]", re.IGNORECASE)


def _iter_lines(content: str) -> Iterable[tuple[int, str]]:
    for i, line in enumerate(content.splitlines(), start=1):
        yield i, line


def simple_checks(path: str, content: str) -> List[Issue]:
    issues: List[Issue] = []

    func_len = 0
    in_func = False
    func_start = 0

    for ln, s in _iter_lines(content):
        if TODO_RE.search(s):
            issues.append(Issue(path, ln, "INFO", "TODO/FIXME存在", "建议尽快处理或关联Issue。"))
        if EVAL_RE.search(s):
            issues.append(Issue(path, ln, "WARN", "使用eval/exec风险", "避免动态执行，考虑安全替代方案。"))
        if "subprocess" in s and "shell" in s and "True" in s:
            issues.append(Issue(path, ln, "WARN", "subprocess shell=True", "可能存在命令注入风险，尽量禁用shell或严格转义。"))
        if "pickle.load" in s or "pickle.loads" in s:
            issues.append(Issue(path, ln, "WARN", "不安全的pickle反序列化", "避免对不受信任数据使用pickle，改用安全格式如json。"))
        if AWS_KEY_RE.search(s):
            issues.append(Issue(path, ln, "ERROR", "可能的AWS访问密钥泄露", "请移除并轮换密钥，改用环境变量或密钥管理。"))
        if SECRET_MARKER_RE.search(s) and ("=\"" in s or "='" in s):
            issues.append(Issue(path, ln, "ERROR", "疑似硬编码密钥", "不要硬编码敏感信息，改用配置或CI密钥。"))

        # naive function boundary detection for Python/JS
        if re.match(r"^\s*(def |function |class )", s):
            in_func = True
            func_len = 1
            func_start = ln
        elif in_func:
            func_len += 1
            if re.match(r"^\s*$", s):
                # blank line might indicate end; report if long
                if func_len >= 120:
                    issues.append(Issue(
                        path, func_start, "INFO", "函数/块过长",
                        f"此块约{func_len}行，考虑拆分以提升可维护性。",
                    ))
                in_func = False

    return issues
