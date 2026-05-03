#!/usr/bin/env python3
"""Skill Seekers 内置工具运行入口。

从 vendored 源码目录（Skill_Seekers-development/src）运行 Skill Seekers，
将文档站/GitHub 仓库/PDF 转换为 Skill 初稿并输出到 output/<name>/。

使用示例：
  python skill-seekers.py -- --version
  python skill-seekers.py -- github --repo facebook/react --name react
  python skill-seekers.py -- scrape --config ./scripts/Skill_Seekers-development/configs/react.json
"""
from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
from pathlib import Path


def parse_args() -> tuple[argparse.Namespace, list[str]]:
  """解析本脚本自身的参数，其余参数转发给 Skill Seekers。

  Returns:
      (本脚本参数命名空间, 转发给 Skill Seekers 的参数列表)。
  """
  parser = argparse.ArgumentParser(description="从 vendored 源码运行 Skill Seekers")
  parser.add_argument("--venv", default="", help="指定 venv 目录（默认使用 .venv-skill-seekers）")
  args, rest = parser.parse_known_args()
  return args, rest


def resolve_python(default_venv: Path, override_venv: str) -> list[str]:
  """按优先级解析可用的 Python 可执行命令。

  优先使用指定 venv 中的 Python，其次依次尝试 python3、python、py -3、python.exe。

  Args:
      default_venv: 默认 venv 目录路径（由 skill-seekers-bootstrap.py 创建）。
      override_venv: 用户通过 --venv 指定的目录路径字符串，空字符串表示未指定。

  Returns:
      可直接传入 subprocess 的 Python 命令列表，例如 ["python3"] 或 ["py", "-3"]。

  Raises:
      SystemExit: 找不到可用 Python 时退出。
  """
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
  """主入口：构建运行环境并以子进程方式调用 Skill Seekers。

  Returns:
      Skill Seekers 子进程的退出码。
  """
  args, rest = parse_args()
  script_dir = Path(__file__).resolve().parent
  tool_src = script_dir / "Skill_Seekers-development" / "src"
  if not tool_src.exists():
    raise SystemExit(f"Error: Missing vendored source dir: {tool_src}")

  python_cmd = resolve_python(script_dir / ".venv-skill-seekers", args.venv)
  env = os.environ.copy()

  py_path = str(tool_src)
  # 在 WSL 环境中使用 Windows Python 时，需将 POSIX 路径转换为 Windows 路径
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
