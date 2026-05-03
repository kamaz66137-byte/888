#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
py_script="$script_dir/skill-seekers-update.py"

resolve_python_cmd() {
  if command -v python3 >/dev/null 2>&1; then
    echo "python3"
    return 0
  fi
  if command -v python >/dev/null 2>&1; then
    echo "python"
    return 0
  fi
  if command -v py >/dev/null 2>&1; then
    echo "py -3"
    return 0
  fi
  if command -v python.exe >/dev/null 2>&1; then
    echo "python.exe"
    return 0
  fi
  return 1
}

python_cmd="$(resolve_python_cmd)" || {
  echo "Error: No supported Python found (tried: python3, python, py -3, python.exe)" >&2
  exit 1
}

if [[ "$python_cmd" == "py -3" ]]; then
  exec py -3 "$py_script" "$@"
elif [[ "$python_cmd" == "python.exe" ]] && command -v wslpath >/dev/null 2>&1; then
  exec python.exe "$(wslpath -w "$py_script")" "$@"
else
  exec "$python_cmd" "$py_script" "$@"
fi
