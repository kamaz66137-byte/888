"""task.service — 任务业务逻辑层。"""
from __future__ import annotations

from pathlib import Path

from db import open_conn


def add_task(
    db_path: Path,
    name: str,
    description: str = "",
    priority: str = "medium",
    due_date: object = None,
) -> str:
    with open_conn(db_path) as conn:
        cursor = conn.execute(
            "INSERT INTO tasks (name, description, priority, due_date) VALUES (?, ?, ?, ?)",
            (name, description, priority, due_date),
        )
    return f"OK: task id={cursor.lastrowid}"


def list_tasks(
    db_path: Path,
    status: str = "all",
    priority: str = "all",
    limit: int = 20,
    offset: int = 0,
) -> str:
    where_parts: list[str] = []
    params: list[object] = []
    if status != "all":
        where_parts.append("status = ?")
        params.append(status)
    if priority != "all":
        where_parts.append("priority = ?")
        params.append(priority)
    where_sql = f"WHERE {' AND '.join(where_parts)}" if where_parts else ""
    params.extend([limit, offset])
    with open_conn(db_path) as conn:
        rows = conn.execute(
            f"SELECT id, name, status, priority, due_date FROM tasks {where_sql} ORDER BY id DESC LIMIT ? OFFSET ?",
            params,
        ).fetchall()
    if not rows:
        return "(空)"
    return "\n".join(
        f"[{r['id']}] [{r['status']}] [{r['priority']}] {r['name']} due={r['due_date'] or '-'}"
        for r in rows
    )


def update_task(db_path: Path, task_id: int, fields: dict) -> str:
    mutable = ["name", "description", "status", "priority", "due_date"]
    updates: list[str] = []
    params: list[object] = []
    for field in mutable:
        if field in fields:
            updates.append(f"{field} = ?")
            params.append(fields[field])
    if not updates:
        return "Error: 至少提供一个可更新字段"
    updates.append("updated_at = datetime('now')")
    params.append(task_id)
    with open_conn(db_path) as conn:
        cursor = conn.execute(
            f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?", params
        )
    return "OK: updated" if cursor.rowcount else "OK: not found"


def done_task(db_path: Path, task_id: int) -> str:
    with open_conn(db_path) as conn:
        cursor = conn.execute(
            "UPDATE tasks SET status = 'done', updated_at = datetime('now') WHERE id = ?",
            (task_id,),
        )
    return "OK: updated" if cursor.rowcount else "OK: not found"


def delete_task(db_path: Path, task_id: int) -> str:
    with open_conn(db_path) as conn:
        cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    return "OK: deleted" if cursor.rowcount else "OK: not found"


def stats_tasks(db_path: Path) -> str:
    with open_conn(db_path) as conn:
        rows = conn.execute(
            "SELECT status, COUNT(*) AS total FROM tasks GROUP BY status ORDER BY status"
        ).fetchall()
        total = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    stats = [f"total={total}"]
    for row in rows:
        stats.append(f"{row['status']}={row['total']}")
    return "\n".join(stats)
