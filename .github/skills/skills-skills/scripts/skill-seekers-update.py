#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tarfile
import tempfile
import urllib.request
from pathlib import Path


def parse_args() -> argparse.Namespace:
  parser = argparse.ArgumentParser(description="Update vendored Skill Seekers snapshot")
  parser.add_argument("--repo", default="yusufkaraaslan/Skill_Seekers")
  parser.add_argument("--ref", default="main")
  parser.add_argument("--dry-run", action="store_true")
  return parser.parse_args()


def should_exclude(path: Path) -> bool:
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
