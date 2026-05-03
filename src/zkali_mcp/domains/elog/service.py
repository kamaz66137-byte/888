"""elog.service — 事件日志业务逻辑层。"""
from __future__ import annotations

from pathlib import Path

from db import open_conn


def add_log(
    db_path: Path,
    summary: str,
    event_type: str = "info",
    project_id: object = None,
    detail: str = "",
) -> str:
    with open_conn(db_path) as conn:
        cursor = conn.execute(
            "INSERT INTO event_log (project_id, event_type, summary, detail) VALUES (?, ?, ?, ?)",
            (project_id, event_type, summary, detail),
        )
    return f"OK: log id={cursor.lastrowid}"


def get_log(db_path: Path, log_id: int) -> str:
    with open_conn(db_path) as conn:
        row = conn.execute(
            "SELECT id, project_id, event_type, summary, detail, created_at FROM event_log WHERE id = ?",
            (log_id,),
        ).fetchone()
    if row is None:
        return "ERR: not found"
    return (
        f"id={row['id']}\n"
        f"project_id={row['project_id'] or ''}\n"
        f"event_type={row['event_type']}\n"
        f"summary={row['summary']}\n"
        f"detail={row['detail']}\n"
        f"created_at={row['created_at']}"
    )


def list_logs(
    db_path: Path,
    project_id: object = None,
    event_type: object = None,
    limit: int = 30,
    offset: int = 0,
) -> str:
    conditions: list[str] = []
    params: list[object] = []
    if project_id:
        conditions.append("project_id = ?")
        params.append(project_id)
    if event_type:
        conditions.append("event_type = ?")
        params.append(event_type)
    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    params.extend([limit, offset])
    with open_conn(db_path) as conn:
        rows = conn.execute(
            f"SELECT id, project_id, event_type, summary, created_at FROM event_log {where} ORDER BY id DESC LIMIT ? OFFSET ?",
            params,
        ).fetchall()
    if not rows:
        return "(空)"
    return "\n".join(
        f"[{r['id']}] [{r['event_type']}] {r['summary']} ({r['created_at']})"
        for r in rows
    )


def clear_logs(db_path: Path, project_id: object = None, event_type: object = None) -> str:
    conditions: list[str] = []
    params: list[object] = []
    if project_id:
        conditions.append("project_id = ?")
        params.append(project_id)
    if event_type:
        conditions.append("event_type = ?")
        params.append(event_type)
    if not conditions:
        return "ERR: 至少提供 project_id 或 event_type 以防误删"
    where = f"WHERE {' AND '.join(conditions)}"
    with open_conn(db_path) as conn:
        cursor = conn.execute(f"DELETE FROM event_log {where}", params)
    return f"OK: deleted {cursor.rowcount} log(s)"
