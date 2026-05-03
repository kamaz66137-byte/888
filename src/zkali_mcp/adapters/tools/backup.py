"""tool.backup — 数据库备份工具。"""
from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path


def backup_db(db_path: Path, dest: str = "") -> str:
    if not dest:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = str(db_path.parent / f"zkali_backup_{timestamp}.db")

    dest_path = Path(dest)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    src = sqlite3.connect(db_path)
    try:
        dst = sqlite3.connect(dest_path)
        try:
            src.backup(dst)
        finally:
            dst.close()
    finally:
        src.close()

    size = dest_path.stat().st_size
    return f"OK backup={dest} size={size}bytes"


def dispatch_backup_tool(name: str, arguments: dict, db_path: Path) -> str | None:
    if name == "backup/db":
        dest = str(arguments.get("dest", "")).strip()
        return backup_db(db_path, dest=dest)
    return None
