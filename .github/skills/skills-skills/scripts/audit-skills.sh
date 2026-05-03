#!/usr/bin/env bash
# 薄封装入口：转发所有参数到 audit-skills.py
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/audit-skills.py" "$@"
