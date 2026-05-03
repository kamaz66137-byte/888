#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path


def parse_args() -> argparse.Namespace:
  parser = argparse.ArgumentParser(description="Import Skill Seekers output")
  parser.add_argument("skill_name")
  parser.add_argument("--force", action="store_true")
  return parser.parse_args()


def main() -> int:
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
