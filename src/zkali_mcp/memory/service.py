"""memory.service — 项目记忆业务逻辑层。"""
from __future__ import annotations

from pathlib import Path

from db import open_conn
from project.queries import project_exists


def add_memory(
    db_path: Path,
    project_id: str,
    key: str,
    value: str,
    scope: str = "project",
    namespace: str = "default",
    ttl_seconds: int | None = None,
) -> str:
    if not project_exists(db_path, project_id):
        return "ERR: not found"
    with open_conn(db_path) as conn:
        if conn.execute(
            "SELECT id FROM memories WHERE project_id=? AND scope=? AND namespace=? AND key=?",
            (project_id, scope, namespace, key),
        ).fetchone():
            return "ERR: memory key 已存在"
        cursor = conn.execute(
            "INSERT INTO memories (project_id, scope, namespace, key, value, ttl_seconds) VALUES (?, ?, ?, ?, ?, ?)",
            (project_id, scope, namespace, key, value, ttl_seconds),
        )
    return f"OK id={cursor.lastrowid}"


def get_memory(
    db_path: Path,
    project_id: str,
    key: str,
    scope: str = "project",
    namespace: str = "default",
) -> str:
    with open_conn(db_path) as conn:
        row = conn.execute(
            "SELECT id, project_id, scope, namespace, key, value, ttl_seconds, updated_at FROM memories WHERE project_id=? AND scope=? AND namespace=? AND key=?",
            (project_id, scope, namespace, key),
        ).fetchone()
    if row is None:
        return "ERR: not found"
    return (
        f"id: {row['id']}\n"
        f"project_id: {row['project_id']}\n"
        f"scope: {row['scope']}\n"
        f"namespace: {row['namespace']}\n"
        f"key: {row['key']}\n"
        f"value: {row['value']}\n"
        f"ttl_seconds: {row['ttl_seconds']}\n"
        f"updated_at: {row['updated_at']}"
    )


def list_memory(
    db_path: Path,
    project_id: str,
    scope: str = "all",
    namespace: str = "",
    limit: int = 20,
    offset: int = 0,
) -> str:
    where_parts = ["project_id = ?"]
    params: list[object] = [project_id]
    if scope != "all":
        where_parts.append("scope = ?")
        params.append(scope)
    if namespace:
        where_parts.append("namespace = ?")
        params.append(namespace)
    where_sql = f"WHERE {' AND '.join(where_parts)}"
    params.extend([limit, offset])
    with open_conn(db_path) as conn:
        rows = conn.execute(
            f"SELECT id, scope, namespace, key, updated_at FROM memories {where_sql} ORDER BY id DESC LIMIT ? OFFSET ?",
            params,
        ).fetchall()
    if not rows:
        return "(空)"
    return "\n".join(
        f"[{r['id']}] [{r['scope']}] [{r['namespace']}] {r['key']} ({r['updated_at']})"
        for r in rows
    )


def update_memory(
    db_path: Path,
    project_id: str,
    key: str,
    value: str,
    scope: str = "project",
    namespace: str = "default",
    ttl_seconds: int | None = None,
) -> str:
    with open_conn(db_path) as conn:
        cursor = conn.execute(
            "UPDATE memories SET value=?, ttl_seconds=?, updated_at=datetime('now') WHERE project_id=? AND scope=? AND namespace=? AND key=?",
            (value, ttl_seconds, project_id, scope, namespace, key),
        )
    return "OK: updated" if cursor.rowcount else "ERR: not found"


def delete_memory(
    db_path: Path,
    project_id: str,
    key: str,
    scope: str = "project",
    namespace: str = "default",
) -> str:
    with open_conn(db_path) as conn:
        cursor = conn.execute(
            "DELETE FROM memories WHERE project_id=? AND scope=? AND namespace=? AND key=?",
            (project_id, scope, namespace, key),
        )
    return "OK: deleted" if cursor.rowcount else "ERR: not found"


def clear_memory(db_path: Path, project_id: str, scope: str = "session") -> str:
    with open_conn(db_path) as conn:
        cursor = conn.execute(
            "DELETE FROM memories WHERE project_id=? AND scope=?", (project_id, scope)
        )
    return f"OK deleted={cursor.rowcount}"
