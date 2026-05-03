"""env.service — 项目环境变量业务逻辑层。"""
from __future__ import annotations

from pathlib import Path

from db import open_conn
from project.queries import project_exists


def set_env(
    db_path: Path,
    project_id: str,
    key: str,
    value: str = "",
    description: str = "",
) -> str:
    if not project_exists(db_path, project_id):
        return "ERR: project not found"
    with open_conn(db_path) as conn:
        conn.execute(
            """
            INSERT INTO project_env (project_id, key, value, description, updated_at)
            VALUES (?, ?, ?, ?, datetime('now'))
            ON CONFLICT(project_id, key) DO UPDATE SET
                value = excluded.value,
                description = excluded.description,
                updated_at = datetime('now')
            """,
            (project_id, key, value, description),
        )
    return "OK: env set"


def get_env(db_path: Path, project_id: str, key: str) -> str:
    with open_conn(db_path) as conn:
        row = conn.execute(
            "SELECT project_id, key, value, description, updated_at FROM project_env WHERE project_id = ? AND key = ?",
            (project_id, key),
        ).fetchone()
    if row is None:
        return "ERR: not found"
    return (
        f"project_id={row['project_id']}\n"
        f"key={row['key']}\n"
        f"value={row['value']}\n"
        f"description={row['description']}\n"
        f"updated_at={row['updated_at']}"
    )


def list_env(db_path: Path, project_id: str, limit: int = 50, offset: int = 0) -> str:
    with open_conn(db_path) as conn:
        rows = conn.execute(
            "SELECT key, value, description, updated_at FROM project_env WHERE project_id = ? ORDER BY key LIMIT ? OFFSET ?",
            (project_id, limit, offset),
        ).fetchall()
    if not rows:
        return "(空)"
    return "\n".join(
        f"{r['key']}={r['value']}"
        + (f"  # {r['description']}" if r["description"] else "")
        for r in rows
    )


def delete_env(db_path: Path, project_id: str, key: str) -> str:
    with open_conn(db_path) as conn:
        cursor = conn.execute(
            "DELETE FROM project_env WHERE project_id = ? AND key = ?",
            (project_id, key),
        )
    return "OK: deleted" if cursor.rowcount else "ERR: not found"
