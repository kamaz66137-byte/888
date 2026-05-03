#!/usr/bin/env python3
"""Skill 规范校验器。

对 .github/skills/<skill-name>/ 目录执行结构与内容检查，
支持基础模式（仅警告）和严格模式（违规即报错）。
输出格式支持纯文本（默认）与 JSON（--format json，适合 CI 集成）。
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REQUIRED_SECTIONS = [
  ("When to Use This Skill", "何时使用本技能"),
  ("Not For / Boundaries", "禁止使用 / 边界"),
  ("Quick Reference", "快速参考"),
  ("Examples", "示例"),
  ("References", "参考资料"),
  ("Maintenance", "维护说明"),
]

# 模板占位符残留检测：(正则模式, 描述)
TEMPLATE_RESIDUE_PATTERNS: list[tuple[str, str]] = [
  (r"\{\{skill_name\}\}", "未替换的模板占位符 {{skill_name}}"),
  (r"\[触发器", "未替换的触发器占位符 [触发器...]"),
  (r"\[能力", "未替换的能力占位符 [能力...]"),
  (r"\[领域", "未替换的领域占位符 [领域...]"),
  (r"YYYY-MM-DD", "未替换的日期占位符 YYYY-MM-DD"),
]

# 示例结构化关键词，严格模式下每个示例至少匹配其中2项
EXAMPLE_KEYWORDS = ["输入", "步骤", "预期输出"]

STATUS_OK = "ok"
STATUS_WARN = "warn"
STATUS_ERROR = "error"


def parse_args() -> argparse.Namespace:
  """解析命令行参数。

  Returns:
      包含 skill_dir、strict、format 字段的命名空间对象。
  """
  parser = argparse.ArgumentParser(description="Validate SKILL.md")
  parser.add_argument("skill_dir")
  parser.add_argument("--strict", action="store_true")
  parser.add_argument("--format", choices=["text", "json"], default="text",
                      help="输出格式：text（默认）或 json（适合 CI 集成）")
  return parser.parse_args()


def strip_fenced_blocks(text: str) -> str:
  """移除 Markdown 代码块内容，避免将代码中的示例模式误判为规范违规。

  Args:
      text: 原始 Markdown 文本。

  Returns:
      去除代码围栏块内容后的文本，用于章节结构检测。
  """
  out: list[str] = []
  in_fence = False
  for raw in text.splitlines():
    line = raw.rstrip("\r")
    if re.match(r"^\s*```", line):
      in_fence = not in_fence
      continue
    if not in_fence:
      out.append(line)
  return "\n".join(out) + "\n"


def parse_frontmatter(content: str) -> dict[str, str]:
  """解析 SKILL.md 开头的 YAML frontmatter 块。

  Args:
      content: SKILL.md 的完整文本内容。

  Returns:
      包含 name、description 等字段的字典（key 均小写）。

  Raises:
      SystemExit: frontmatter 缺失或格式不合法时退出并打印错误。
  """
  lines = content.splitlines()
  if not lines or lines[0].rstrip("\r") != "---":
    raise SystemExit("Error: SKILL.md must start with YAML frontmatter")

  fm: list[str] = []
  closed = False
  for line in lines[1:]:
    line = line.rstrip("\r")
    if line == "---":
      closed = True
      break
    fm.append(line)

  if not closed:
    raise SystemExit("Error: YAML frontmatter is not closed (missing ---)")

  data: dict[str, str] = {}
  for row in fm:
    if ":" not in row:
      continue
    k, v = row.split(":", 1)
    data[k.strip().lower()] = v.strip()
  return data


class ValidationResult:
  """单次验证的消息收集器，汇总警告与错误。"""

  def __init__(self) -> None:
    # 每条消息格式：{"level": "warn"|"error", "text": "..."}
    self.messages: list[dict[str, str]] = []

  def warn(self, msg: str) -> None:
    """记录一条警告消息。

    Args:
        msg: 警告描述文本。
    """
    self.messages.append({"level": "warn", "text": msg})

  def error(self, msg: str) -> None:
    """记录一条错误消息。

    Args:
        msg: 错误描述文本。
    """
    self.messages.append({"level": "error", "text": msg})

  def issue(self, msg: str, *, strict: bool) -> None:
    """在严格模式下记为错误，否则记为警告。

    Args:
        msg: 问题描述文本。
        strict: 是否处于严格模式。
    """
    if strict:
      self.error(msg)
    else:
      self.warn(msg)

  @property
  def status(self) -> str:
    """返回当前验证状态字符串：ok / warn / error。"""
    if any(m["level"] == "error" for m in self.messages):
      return STATUS_ERROR
    if any(m["level"] == "warn" for m in self.messages):
      return STATUS_WARN
    return STATUS_OK


def validate(skill_dir: Path, strict: bool) -> ValidationResult:
  """对指定技能目录执行全部验证规则。

  检查项包括：
  - frontmatter 格式与字段合法性
  - name/目录名一致性
  - description 长度质量
  - 必需章节完整性
  - references/index.md 存在性（严格模式）
  - 快速参考行数与子节数量
  - 示例数量与结构化内容（严格模式）
  - 模板残留占位符检测

  Args:
      skill_dir: 技能根目录路径。
      strict: 是否启用严格模式（违规记为错误而非警告）。

  Returns:
      包含所有验证消息的 ValidationResult 实例。

  Raises:
      SystemExit: 目录不存在、SKILL.md 缺失或 frontmatter 格式非法时退出。
  """
  result = ValidationResult()

  if not skill_dir.is_dir():
    raise SystemExit(f"Error: Not a directory: {skill_dir}")

  skill_md = skill_dir / "SKILL.md"
  if not skill_md.exists():
    raise SystemExit(f"Error: Missing SKILL.md: {skill_md}")

  content = skill_md.read_text(encoding="utf-8")
  fm = parse_frontmatter(content)

  name = fm.get("name", "")
  # description 值可能带有外层引号（YAML 惯例），需剥除后再检查内容
  desc = fm.get("description", "").strip('"').strip("'")
  if not name:
    raise SystemExit("Error: Missing frontmatter field: name")
  if not desc:
    raise SystemExit("Error: Missing frontmatter field: description")
  if not re.fullmatch(r"[a-z][a-z0-9-]*", name):
    raise SystemExit(f"Error: Invalid name: '{name}' (expected ^[a-z][a-z0-9-]*$)")

  # name 与目录名一致性：非严格模式也输出警告，保持可见性
  base_name = skill_dir.name
  if name != base_name:
    result.issue(f"frontmatter name ('{name}') 与目录名 ('{base_name}') 不一致", strict=strict)

  # description 质量：过短的描述激活可靠性差
  if len(desc) < 20:
    result.issue(f"description 过短（{len(desc)} 字符），建议 >= 20 字符以提升激活可靠性", strict=strict)

  filtered = strip_fenced_blocks(content)
  lines = filtered.splitlines()

  # 必需章节存在性检查
  for en, zh in REQUIRED_SECTIONS:
    pat = re.compile(rf"^##\s+({re.escape(en)}|{re.escape(zh)})\s*$")
    if not any(pat.match(line) for line in lines):
      result.issue(f"缺少必需章节标题：'## {en}' 或 '## {zh}'", strict=strict)

  # references/ 目录存在时必须有 index.md（严格模式）
  if strict and (skill_dir / "references").is_dir() and not (skill_dir / "references" / "index.md").exists():
    result.error("references/ 目录存在但缺少 references/index.md")

  # 快速参考：行数检查 + 子节数量检查
  try:
    quick_idx = next(i for i, line in enumerate(lines) if re.match(r"^##\s+(Quick Reference|快速参考)\s*$", line))
    quick_end = next((i for i in range(quick_idx + 1, len(lines)) if re.match(r"^##\s+", lines[i])), len(lines))
    quick_section = lines[quick_idx + 1: quick_end]
    quick_len = len(quick_section)
    if quick_len > 250:
      result.issue(f"快速参考章节过长（{quick_len} 行），请将长篇文本移至 references/", strict=strict)
    # 子节模式计数：过多的 ### 说明快速参考过于臃肿
    pattern_count = sum(1 for line in quick_section if re.match(r"^###\s+", line))
    if pattern_count >= 20:
      result.warn(f"快速参考子节过多（{pattern_count} 个），建议 < 20 个模式保持简洁")
  except StopIteration:
    pass

  # 示例章节：数量检查 + 严格模式下的结构化内容检查
  try:
    ex_idx = next(i for i, line in enumerate(lines) if re.match(r"^##\s+(Examples|示例)\s*$", line))
    ex_end = next((i for i in range(ex_idx + 1, len(lines)) if re.match(r"^##\s+", lines[i])), len(lines))
    ex_section = lines[ex_idx + 1: ex_end]
    ex_starts = [i for i, line in enumerate(ex_section) if re.match(r"^###\s+(Example|示例)", line)]
    count = len(ex_starts)
    if count < 3:
      result.issue(f"示例数量不足（{count} 个），期望 >= 3 个", strict=strict)
    # 严格模式：每个示例需包含输入/步骤/预期输出中至少2项
    if strict and count > 0:
      for k, start in enumerate(ex_starts):
        end = ex_starts[k + 1] if k + 1 < len(ex_starts) else len(ex_section)
        block_text = "\n".join(ex_section[start:end])
        hit = sum(1 for kw in EXAMPLE_KEYWORDS if kw in block_text)
        if hit < 2:
          result.error(
            f"示例 {k + 1} 缺少结构化内容"
            f"（[输入/步骤/预期输出] 至少包含2项，当前仅 {hit} 项）"
          )
  except StopIteration:
    pass

  # 模板残留检测：扫描过滤后内容（已剥除代码块），避免文档示例引发误报
  # 同时单独检查 frontmatter 字段，确保 name/description 中无残留
  fm_raw = fm.get("name", "") + " " + fm.get("description", "")
  residue_targets = [filtered, fm_raw]
  for pattern, label in TEMPLATE_RESIDUE_PATTERNS:
    if any(re.search(pattern, target) for target in residue_targets):
      result.warn(f"检测到模板残留：{label}")

  return result


def main() -> int:
  """主入口：解析参数，执行验证，按指定格式输出结果。

  Returns:
      0 = 验证通过（无错误，警告不影响退出码）；
      1 = 存在验证错误。
  """
  args = parse_args()
  skill_dir = Path(args.skill_dir)
  result = validate(skill_dir, strict=args.strict)

  if args.format == "json":
    output = {
      "skill": str(skill_dir),
      "status": result.status,
      "messages": result.messages,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
  else:
    for msg in result.messages:
      prefix = "Warning" if msg["level"] == "warn" else "Error"
      print(f"{prefix}: {msg['text']}")
    if result.status == STATUS_ERROR:
      print(f"FAIL: {skill_dir}")
    else:
      print(f"OK: {skill_dir}")

  return 1 if result.status == STATUS_ERROR else 0


if __name__ == "__main__":
  raise SystemExit(main())
