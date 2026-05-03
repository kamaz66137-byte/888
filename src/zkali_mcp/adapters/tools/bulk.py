"""tool.bulk — 批量操作工具（bulk/note_add, bulk/task_add）。"""
from __future__ import annotations

from pathlib import Path

from db import open_conn


def bulk_note_add(db_path: Path, items: list[dict]) -> str:
    if not items:
        return "ERR: items 不能为空"
    ids: list[int] = []
    with open_conn(db_path) as conn:
        for item in items:
            name = str(item.get("name", "")).strip()
            if not name:
                continue
            body = str(item.get("body", ""))
            cursor = conn.execute(
                "INSERT INTO notes (name, body) VALUES (?, ?)",
                (name, body),
            )
            ids.append(cursor.lastrowid)
    return f"OK count={len(ids)} ids={ids}"


def bulk_task_add(db_path: Path, items: list[dict]) -> str:
    if not items:
        return "ERR: items 不能为空"
    ids: list[int] = []
    with open_conn(db_path) as conn:
        for item in items:
            name = str(item.get("name", "")).strip()
            if not name:
                continue
            description = str(item.get("description", ""))
            priority = str(item.get("priority", "medium"))
            if priority not in ("low", "medium", "high"):
                priority = "medium"
            due_date = item.get("due_date")
            cursor = conn.execute(
                "INSERT INTO tasks (name, description, priority, due_date) VALUES (?, ?, ?, ?)",
                (name, description, priority, due_date),
            )
            ids.append(cursor.lastrowid)
    return f"OK count={len(ids)} ids={ids}"


def dispatch_bulk_tool(name: str, arguments: dict, db_path: Path) -> str | None:
    if name == "bulk/note_add":
        items = arguments.get("items")
        if not isinstance(items, list):
            return "ERR: items 必须是数组"
        return bulk_note_add(db_path, items)
    if name == "bulk/task_add":
        items = arguments.get("items")
        if not isinstance(items, list):
            return "ERR: items 必须是数组"
        return bulk_task_add(db_path, items)
    return None
