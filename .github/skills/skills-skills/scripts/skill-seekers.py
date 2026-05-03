#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
from pathlib import Path


def parse_args() -> tuple[argparse.Namespace, list[str]]:
  parser = argparse.ArgumentParser(description="Run Skill Seekers from vendored source")
  parser.add_argument("--venv", default="", help="Venv directory")
  args, rest = parser.parse_known_args()
  return args, rest


def resolve_python(default_venv: Path, override_venv: str) -> list[str]:
  venv_dir = Path(override_venv) if override_venv else default_venv
  candidates = [venv_dir / "bin" / "python", venv_dir / "Scripts" / "python.exe"]
  for c in candidates:
    if c.exists():
      return [str(c)]
  for cmd in ("python3", "python", "py"):
    found = shutil.which(cmd)
    if found:
      if cmd == "py":
        return [found, "-3"]
      return [found]
  pyexe = shutil.which("python.exe")
  if pyexe:
    return [pyexe]
  raise SystemExit("Error: No supported Python found (tried: python3, python, py -3, python.exe)")


def main() -> int:
  args, rest = parse_args()
  script_dir = Path(__file__).resolve().parent
  tool_src = script_dir / "Skill_Seekers-development" / "src"
  if not tool_src.exists():
    raise SystemExit(f"Error: Missing vendored source dir: {tool_src}")

  python_cmd = resolve_python(script_dir / ".venv-skill-seekers", args.venv)
  env = os.environ.copy()

  py_path = str(tool_src)
  if python_cmd[0].lower().endswith("python.exe") and shutil.which("wslpath"):
    try:
      win_src = subprocess.check_output(["wslpath", "-w", py_path], text=True).strip()
      py_path = win_src
    except Exception:
      pass

  env["PYTHONPATH"] = py_path + ((":" + env["PYTHONPATH"]) if env.get("PYTHONPATH") else "")

  cmd = [*python_cmd, "-m", "skill_seekers.cli.main", *rest]
  completed = subprocess.run(cmd, env=env)
  return int(completed.returncode)


if __name__ == "__main__":
  raise SystemExit(main())
