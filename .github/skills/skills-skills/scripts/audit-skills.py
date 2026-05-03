#!/usr/bin/env python3
"""技能目录批量验证器。

自动发现 .github/skills/ 下所有含 SKILL.md 的技能目录，
对每个技能调用 validate-skill.py 的验证逻辑并汇总结果。
支持 --strict 模式、--skip 跳过指定目录，以及 --format json 输出。

退出码：
  0 = 全部通过（无警告，无错误）
  1 = 存在警告（无错误）
  2 = 存在验证错误
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# 将当前脚本目录加入 sys.path，以便复用 validate_skill 模块
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
  sys.path.insert(0, str(_SCRIPTS_DIR))

# 动态导入时规避连字符：validate-skill.py -> validate_skill 模块别名
import importlib.util as _ilu

_spec = _ilu.spec_from_file_location("validate_skill", _SCRIPTS_DIR / "validate-skill.py")
if not (_spec and _spec.loader):
  raise SystemExit("Error: 无法加载 validate-skill.py 模块，请确认脚本文件存在")
_vs_mod = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_vs_mod)  # type: ignore[union-attr]

validate = _vs_mod.validate
STATUS_OK = _vs_mod.STATUS_OK
STATUS_WARN = _vs_mod.STATUS_WARN
STATUS_ERROR = _vs_mod.STATUS_ERROR


def parse_args() -> argparse.Namespace:
  """解析命令行参数。

  Returns:
      包含 skills_root、strict、skip、format 字段的命名空间对象。
  """
  parser = argparse.ArgumentParser(description="批量验证 .github/skills/ 下所有技能目录")
  parser.add_argument(
    "--skills-root",
    default="",
    help="技能根目录路径（默认自动推断为仓库的 .github/skills/）",
  )
  parser.add_argument("--strict", action="store_true", help="启用严格模式（违规记为错误）")
  parser.add_argument(
    "--skip",
    nargs="*",
    default=[],
    metavar="SKILL_NAME",
    help="跳过指定技能目录名（可多次指定），例如 --skip skills-skills",
  )
  parser.add_argument(
    "--format",
    choices=["text", "json"],
    default="text",
    help="输出格式：text（默认）或 json（适合 CI 集成）",
  )
  return parser.parse_args()


def discover_skills(root: Path, skip: list[str]) -> list[Path]:
  """发现 root 目录下所有含 SKILL.md 的直接子目录。

  Args:
      root: 技能根目录路径（通常为 .github/skills/）。
      skip: 需要跳过的目录名列表。

  Returns:
      按目录名排序后的技能目录路径列表。

  Raises:
      SystemExit: root 目录不存在时退出。
  """
  if not root.is_dir():
    raise SystemExit(f"Error: 技能根目录不存在：{root}")
  skills = sorted(
    p for p in root.iterdir()
    if p.is_dir() and (p / "SKILL.md").exists() and p.name not in skip
  )
  return skills


def resolve_skills_root(override: str) -> Path:
  """解析技能根目录路径。

  优先使用 override 参数；未指定时从脚本位置向上推断仓库根目录。

  Args:
      override: 用户通过 --skills-root 指定的路径字符串，空字符串表示未指定。

  Returns:
      技能根目录的绝对路径。
  """
  if override:
    return Path(override).resolve()
  # 脚本位于 .github/skills/skills-skills/scripts/，向上4级为仓库根
  repo_root = Path(__file__).resolve().parents[4]
  return repo_root / ".github" / "skills"


def main() -> int:
  """主入口：发现所有技能，批量验证，输出汇总结果。

  Returns:
      0 = 全部通过；1 = 存在警告；2 = 存在错误。
  """
  args = parse_args()
  skills_root = resolve_skills_root(args.skills_root)
  skip_set: list[str] = args.skip or []

  skill_dirs = discover_skills(skills_root, skip=skip_set)

  if not skill_dirs:
    msg = f"在 {skills_root} 下未发现任何技能目录（含 SKILL.md）"
    if args.format == "json":
      print(json.dumps({"status": STATUS_WARN, "summary": msg, "results": []}, ensure_ascii=False, indent=2))
    else:
      print(f"Warning: {msg}")
    return 1

  results: list[dict] = []
  for skill_dir in skill_dirs:
    try:
      vr = validate(skill_dir, strict=args.strict)
      results.append({
        "skill": skill_dir.name,
        "path": str(skill_dir),
        "status": vr.status,
        "messages": vr.messages,
      })
    except SystemExit as exc:
      # validate() 对致命错误直接 raise SystemExit；此处捕获并记为 error
      results.append({
        "skill": skill_dir.name,
        "path": str(skill_dir),
        "status": STATUS_ERROR,
        "messages": [{"level": "error", "text": str(exc)}],
      })

  n_ok = sum(1 for r in results if r["status"] == STATUS_OK)
  n_warn = sum(1 for r in results if r["status"] == STATUS_WARN)
  n_error = sum(1 for r in results if r["status"] == STATUS_ERROR)

  if args.format == "json":
    overall = STATUS_ERROR if n_error else (STATUS_WARN if n_warn else STATUS_OK)
    print(json.dumps({
      "status": overall,
      "summary": {"total": len(results), "ok": n_ok, "warn": n_warn, "error": n_error},
      "results": results,
    }, ensure_ascii=False, indent=2))
  else:
    for r in results:
      if r["status"] == STATUS_OK:
        print(f"  OK     {r['skill']}")
      elif r["status"] == STATUS_WARN:
        print(f"  WARN   {r['skill']}")
        for m in r["messages"]:
          print(f"           Warning: {m['text']}")
      else:
        print(f"  FAIL   {r['skill']}")
        for m in r["messages"]:
          prefix = "Warning" if m["level"] == "warn" else "Error"
          print(f"           {prefix}: {m['text']}")
    print()
    print(f"汇总：{len(results)} 个技能  通过 {n_ok}  警告 {n_warn}  失败 {n_error}")

  if n_error:
    return 2
  if n_warn:
    return 1
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
