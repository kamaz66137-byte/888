#!/usr/bin/env python3
"""Skill Seekers 内置源码快照更新工具。

从上游 GitHub 仓库下载最新源码 tarball，按排除规则过滤后
替换 Skill_Seekers-development/ 目录内容。需要网络访问 GitHub codeload。

使用示例：
  python skill-seekers-update.py
  python skill-seekers-update.py --ref main
  python skill-seekers-update.py --dry-run
"""
from __future__ import annotations

import argparse
import shutil
import tarfile
import tempfile
import urllib.request
from pathlib import Path


def parse_args() -> argparse.Namespace:
  """解析命令行参数。

  Returns:
      包含 repo、ref、dry_run 字段的命名空间对象。
  """
  parser = argparse.ArgumentParser(description="从上游更新 vendored Skill Seekers 源码快照")
  parser.add_argument("--repo", default="yusufkaraaslan/Skill_Seekers", help="上游仓库（owner/name）")
  parser.add_argument("--ref", default="main", help="要拉取的 Git 引用（branch/tag/commit）")
  parser.add_argument("--dry-run", action="store_true", help="仅打印计划，不实际写入磁盘")
  return parser.parse_args()


def should_exclude(path: Path) -> bool:
  """判断给定路径是否应在导入时跳过。

  排除规则：.git 目录、docs 目录、tests 目录、.claude 目录，
  以及已知的 Markdown 文档文件（CHANGELOG、ROADMAP 等）。

  Args:
      path: 相对于 archive 根目录的路径。

  Returns:
      True 表示应跳过，False 表示保留。
  """
  rel = path.as_posix()
  excluded_prefixes = [".git", "docs", "tests", ".claude"]
  excluded_names = {
    ".gitignore",
    "CHANGELOG.md",
    "ROADMAP.md",
    "FUTURE_RELEASES.md",
    "ASYNC_SUPPORT.md",
    "STRUCTURE.md",
    "CONTRIBUTING.md",
    "QUICKSTART.md",
    "BULLETPROOF_QUICKSTART.md",
    "FLEXIBLE_ROADMAP.md",
  }
  if path.name in excluded_names:
    return True
  if path.suffix.lower() == ".md":
    return True
  return any(rel == p or rel.startswith(p + "/") for p in excluded_prefixes)


def main() -> int:
  """主入口：下载 tarball、过滤内容、替换本地快照目录。

  Returns:
      0 表示成功（含 dry-run）。

  Raises:
      SystemExit: 无法从 archive 中定位解压根目录时退出。
  """
  args = parse_args()
  script_dir = Path(__file__).resolve().parent
  target_dir = script_dir / "Skill_Seekers-development"

  url = f"https://codeload.github.com/{args.repo}/tar.gz/{args.ref}"

  with tempfile.TemporaryDirectory() as tmp:
    tmp_path = Path(tmp)
    archive = tmp_path / "skill-seekers.tgz"
    urllib.request.urlretrieve(url, archive)

    with tarfile.open(archive, "r:gz") as tf:
      tf.extractall(tmp_path)

    extracted = next((p for p in tmp_path.iterdir() if p.is_dir()), None)
    if extracted is None:
      raise SystemExit("Error: Failed to locate extracted archive root")

    if args.dry_run:
      print("DRY RUN:")
      print(f"  repo: {args.repo}")
      print(f"  ref:  {args.ref}")
      print(f"  from: {extracted}")
      print(f"  to:   {target_dir}")
      return 0

    if target_dir.exists():
      shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    for src in extracted.rglob("*"):
      rel = src.relative_to(extracted)
      if should_exclude(rel):
        continue
      dest = target_dir / rel
      if src.is_dir():
        dest.mkdir(parents=True, exist_ok=True)
      else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)

  print(f"OK: updated vendored source in: {target_dir}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
