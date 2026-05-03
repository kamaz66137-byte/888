#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


def parse_args() -> argparse.Namespace:
  parser = argparse.ArgumentParser(description="Bootstrap Skill Seekers venv")
  parser.add_argument("--venv", default="", help="Venv directory")
  return parser.parse_args()


def resolve_python() -> list[str]:
  for cmd in ("python3", "python", "py"):
    found = shutil.which(cmd)
    if found:
      return [found, "-3"] if cmd == "py" else [found]
  pyexe = shutil.which("python.exe")
  if pyexe:
    return [pyexe]
  raise SystemExit("Error: No supported Python found (tried: python3, python, py -3, python.exe)")


def venv_python(venv: Path) -> list[str]:
  for p in (venv / "bin" / "python", venv / "Scripts" / "python.exe"):
    if p.exists():
      return [str(p)]
  raise SystemExit(f"Error: Cannot find venv python in: {venv}")


def main() -> int:
  args = parse_args()
  script_dir = Path(__file__).resolve().parent
  tool_dir = script_dir / "Skill_Seekers-development"
  venv_dir = Path(args.venv).resolve() if args.venv else script_dir / ".venv-skill-seekers"

  req = tool_dir / "requirements.txt"
  if not tool_dir.exists():
    raise SystemExit(f"Error: Missing vendored tool dir: {tool_dir}")
  if not req.exists():
    raise SystemExit(f"Error: Missing requirements.txt: {req}")

  if not venv_dir.exists():
    subprocess.check_call([*resolve_python(), "-m", "venv", str(venv_dir)])

  py = venv_python(venv_dir)
  subprocess.check_call([*py, "-m", "pip", "install", "--upgrade", "pip"])
  subprocess.check_call([*py, "-m", "pip", "install", "-r", str(req)])
  subprocess.check_call([*py, "-m", "pip", "install", "-e", str(tool_dir)])

  print(f"OK: venv ready: {venv_dir}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
