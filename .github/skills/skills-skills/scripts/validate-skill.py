#!/usr/bin/env python3
from __future__ import annotations

import argparse
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


def parse_args() -> argparse.Namespace:
  parser = argparse.ArgumentParser(description="Validate SKILL.md")
  parser.add_argument("skill_dir")
  parser.add_argument("--strict", action="store_true")
  return parser.parse_args()


def strip_fenced_blocks(text: str) -> str:
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


def warn(msg: str) -> None:
  print(f"Warning: {msg}")


def main() -> int:
  args = parse_args()
  skill_dir = Path(args.skill_dir)
  if not skill_dir.is_dir():
    raise SystemExit(f"Error: Not a directory: {skill_dir}")

  skill_md = skill_dir / "SKILL.md"
  if not skill_md.exists():
    raise SystemExit(f"Error: Missing SKILL.md: {skill_md}")

  content = skill_md.read_text(encoding="utf-8")
  fm = parse_frontmatter(content)

  name = fm.get("name", "")
  desc = fm.get("description", "")
  if not name:
    raise SystemExit("Error: Missing frontmatter field: name")
  if not desc:
    raise SystemExit("Error: Missing frontmatter field: description")
  if not re.fullmatch(r"[a-z][a-z0-9-]*", name):
    raise SystemExit(f"Error: Invalid name: '{name}' (expected ^[a-z][a-z0-9-]*$)")

  base_name = skill_dir.name
  if args.strict and name != base_name:
    raise SystemExit(f"Error: Strict mode: frontmatter name ('{name}') must match directory name ('{base_name}')")

  filtered = strip_fenced_blocks(content)
  lines = filtered.splitlines()

  for en, zh in REQUIRED_SECTIONS:
    pat = re.compile(rf"^##\s+({re.escape(en)}|{re.escape(zh)})\s*$")
    if not any(pat.match(line) for line in lines):
      msg = f"missing required section heading: '## {en}' or '## {zh}'"
      if args.strict:
        raise SystemExit(f"Error: Strict mode: {msg}")
      warn(msg)

  if args.strict and (skill_dir / "references").is_dir() and not (skill_dir / "references" / "index.md").exists():
    raise SystemExit("Error: Strict mode: references/ exists but references/index.md is missing")

  try:
    quick_idx = next(i for i, line in enumerate(lines) if re.match(r"^##\s+(Quick Reference|快速参考)\s*$", line))
    quick_end = next((i for i in range(quick_idx + 1, len(lines)) if re.match(r"^##\s+", lines[i])), len(lines))
    quick_len = quick_end - quick_idx - 1
    if quick_len > 250:
      msg = f"Quick Reference section is too long ({quick_len} lines). Move long-form text into references/."
      if args.strict:
        raise SystemExit(f"Error: Strict mode: {msg}")
      warn(msg)
  except StopIteration:
    pass

  try:
    ex_idx = next(i for i, line in enumerate(lines) if re.match(r"^##\s+(Examples|示例)\s*$", line))
    ex_end = next((i for i in range(ex_idx + 1, len(lines)) if re.match(r"^##\s+", lines[i])), len(lines))
    count = sum(1 for line in lines[ex_idx + 1 : ex_end] if re.match(r"^###\s+(Example|示例)", line))
    if count < 3:
      msg = f"expected >= 3 examples (found {count})."
      if args.strict:
        raise SystemExit(f"Error: Strict mode: {msg}")
      warn(msg)
  except StopIteration:
    pass

  print(f"OK: {skill_dir}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
