"""snippet.service — 代码片段业务逻辑层。"""
from __future__ import annotations

from pathlib import Path

from db import open_conn
from project.queries import project_exists


def add_snippet(
    db_path: Path,
    name: str,
    language: str = "",
    content: str = "",
    tags: str = "[]",
    project_id: str = "",
) -> str:
    scope = "project" if project_id else "public"
    project_value: object = project_id if project_id else None
    if project_id and not project_exists(db_path, project_id):
        return f"ERR: project not found: {project_id}"
    with open_conn(db_path) as conn:
        cursor = conn.execute(
            "INSERT INTO snippets (name, language, content, tags, scope, project_id) VALUES (?, ?, ?, ?, ?, ?)",
            (name, language, content, tags, scope, project_value),
        )
    return f"OK: snippet id={cursor.lastrowid}"


def get_snippet(db_path: Path, snippet_id: int) -> str:
    with open_conn(db_path) as conn:
        row = conn.execute(
            "SELECT id, name, language, content, tags, scope, project_id, created_at, updated_at FROM snippets WHERE id = ?",
            (snippet_id,),
        ).fetchone()
    if row is None:
        return "ERR: not found"
    return (
        f"id={row['id']}\n"
        f"name={row['name']}\n"
        f"language={row['language']}\n"
        f"scope={row['scope']}\n"
        f"project_id={row['project_id'] or ''}\n"
        f"tags={row['tags']}\n"
        f"content={row['content']}\n"
        f"created_at={row['created_at']}\n"
        f"updated_at={row['updated_at']}"
    )


def list_snippets(
    db_path: Path,
    scope: str = "all",
    project_id: str = "",
    language: str = "",
    limit: int = 20,
    offset: int = 0,
) -> str:
    conditions: list[str] = []
    params: list[object] = []
    if scope == "public":
        conditions.append("scope = 'public'")
    elif scope == "project":
        conditions.append("scope = 'project'")
        if project_id:
            conditions.append("project_id = ?")
            params.append(project_id)
    elif project_id:
        conditions.append("(scope = 'public' OR project_id = ?)")
        params.append(project_id)
    if language:
        conditions.append("language = ?")
        params.append(language)
    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    params.extend([limit, offset])
    with open_conn(db_path) as conn:
        rows = conn.execute(
            f"SELECT id, name, language, scope, updated_at FROM snippets {where} ORDER BY id DESC LIMIT ? OFFSET ?",
            params,
        ).fetchall()
    if not rows:
        return "(空)"
    return "\n".join(
        f"[{r['id']}] {r['name']} | {r['language']} | {r['scope']} ({r['updated_at']})"
        for r in rows
    )


def search_snippets(db_path: Path, query: str, limit: int = 20, offset: int = 0) -> str:
    like = f"%{query}%"
    with open_conn(db_path) as conn:
        rows = conn.execute(
            "SELECT id, name, language, scope, updated_at FROM snippets WHERE name LIKE ? OR content LIKE ? OR tags LIKE ? ORDER BY id DESC LIMIT ? OFFSET ?",
            (like, like, like, limit, offset),
        ).fetchall()
    if not rows:
        return "(空)"
    return "\n".join(
        f"[{r['id']}] {r['name']} | {r['language']} | {r['scope']} ({r['updated_at']})"
        for r in rows
    )


def update_snippet(db_path: Path, snippet_id: int, fields: dict) -> str:
    allowed = ["name", "language", "content", "tags"]
    updates: list[str] = []
    params: list[object] = []
    for f in allowed:
        if f in fields:
            updates.append(f"{f} = ?")
            params.append(str(fields[f]))
    if not updates:
        return "ERR: 至少提供一个更新字段"
    updates.append("updated_at = datetime('now')")
    params.append(snippet_id)
    with open_conn(db_path) as conn:
        cursor = conn.execute(
            f"UPDATE snippets SET {', '.join(updates)} WHERE id = ?", params
        )
    return "OK: updated" if cursor.rowcount else "ERR: not found"


def delete_snippet(db_path: Path, snippet_id: int) -> str:
    with open_conn(db_path) as conn:
        cursor = conn.execute("DELETE FROM snippets WHERE id = ?", (snippet_id,))
    return "OK: deleted" if cursor.rowcount else "ERR: not found"
