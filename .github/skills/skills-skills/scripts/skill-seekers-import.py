#!/usr/bin/env python3
"""Skill Seekers 输出导入工具。

将 Skill Seekers 生成的 output/<skill_name>/ 目录导入到仓库标准路径
.github/skills/<skill_name>/，供后续校验与迭代使用。

使用示例：
  python skill-seekers-import.py react
  python skill-seekers-import.py react --force
"""
from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path


def parse_args() -> argparse.Namespace:
  """解析命令行参数。

  Returns:
      包含 skill_name、force 字段的命名空间对象。
  """
  parser = argparse.ArgumentParser(description="将 Skill Seekers 输出导入到 .github/skills/")
  parser.add_argument("skill_name", help="目标技能名称，必须匹配 ^[a-z][a-z0-9-]*$")
  parser.add_argument("--force", action="store_true", help="目标目录已存在时强制覆盖")
  return parser.parse_args()


def main() -> int:
  """主入口：校验名称、定位源目录、执行导入。

  Returns:
      0 表示成功导入。

  Raises:
      SystemExit: 技能名称不合法、源目录缺失或目标 SKILL.md 已存在（未指定 --force）时退出。
  """
  args = parse_args()
  if not re.fullmatch(r"[a-z][a-z0-9-]*", args.skill_name):
    raise SystemExit("Error: skill-name must match ^[a-z][a-z0-9-]*$")

  repo_root = Path(__file__).resolve().parents[4]
  src_dir = repo_root / "output" / args.skill_name
  dest_dir = repo_root / ".github" / "skills" / args.skill_name

  if not src_dir.is_dir():
    raise SystemExit(f"Error: Missing Skill Seekers output dir: {src_dir}")
  if not (src_dir / "SKILL.md").exists():
    raise SystemExit(f"Error: Missing output SKILL.md: {src_dir / 'SKILL.md'}")

  dest_dir.mkdir(parents=True, exist_ok=True)
  if (dest_dir / "SKILL.md").exists() and not args.force:
    raise SystemExit(f"Error: Refusing to overwrite existing: {dest_dir / 'SKILL.md'} (use --force)")

  # 清空目标目录后重新复制，保证与源目录完全同步
  if dest_dir.exists():
    for p in dest_dir.iterdir():
      if p.is_dir():
        shutil.rmtree(p)
      else:
        p.unlink()

  for p in src_dir.rglob("*"):
    rel = p.relative_to(src_dir)
    target = dest_dir / rel
    if p.is_dir():
      target.mkdir(parents=True, exist_ok=True)
    else:
      target.parent.mkdir(parents=True, exist_ok=True)
      shutil.copy2(p, target)

  print(f"OK: imported to: {dest_dir}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
