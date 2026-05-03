#!/usr/bin/env python3
"""Skill Seekers 依赖初始化脚本。

为内置 vendored Skill Seekers 工具创建专用 Python venv 并安装依赖。
只需执行一次；若 venv 已存在则跳过创建，直接更新依赖。

使用示例：
  python skill-seekers-bootstrap.py
  python skill-seekers-bootstrap.py --venv /path/to/custom-venv
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


def parse_args() -> argparse.Namespace:
  """解析命令行参数。

  Returns:
      包含 venv 字段的命名空间对象。
  """
  parser = argparse.ArgumentParser(description="为 vendored Skill Seekers 初始化 venv 并安装依赖")
  parser.add_argument("--venv", default="", help="指定 venv 目录路径（默认为 .venv-skill-seekers）")
  return parser.parse_args()


def resolve_python() -> list[str]:
  """按优先级解析系统中可用的 Python 可执行命令。

  Returns:
      可直接传入 subprocess 的 Python 命令列表。

  Raises:
      SystemExit: 找不到可用 Python 时退出。
  """
  for cmd in ("python3", "python", "py"):
    found = shutil.which(cmd)
    if found:
      return [found, "-3"] if cmd == "py" else [found]
  pyexe = shutil.which("python.exe")
  if pyexe:
    return [pyexe]
  raise SystemExit("Error: No supported Python found (tried: python3, python, py -3, python.exe)")


def venv_python(venv: Path) -> list[str]:
  """返回指定 venv 目录中的 Python 可执行命令列表。

  Args:
      venv: venv 根目录路径。

  Returns:
      指向 venv Python 的命令列表。

  Raises:
      SystemExit: venv 中找不到 Python 可执行文件时退出。
  """
  for p in (venv / "bin" / "python", venv / "Scripts" / "python.exe"):
    if p.exists():
      return [str(p)]
  raise SystemExit(f"Error: Cannot find venv python in: {venv}")


def main() -> int:
  """主入口：创建 venv、升级 pip 并安装 Skill Seekers 依赖。

  Returns:
      0 表示成功。

  Raises:
      SystemExit: vendored 工具目录或 requirements.txt 缺失时退出。
  """
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
