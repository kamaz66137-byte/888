"""kv.service — 词典项业务逻辑层。"""
from __future__ import annotations

import json
from pathlib import Path

from db import open_conn
from domains.project.queries import project_exists


def normalize_tags(tags: object) -> str:
    if tags is None:
        return "[]"
    if isinstance(tags, list):
        clean = [str(item).strip() for item in tags if str(item).strip()]
        return json.dumps(clean, ensure_ascii=False)
    text = str(tags).strip()
    if not text:
        return "[]"
    parts = [p.strip() for p in text.split(",") if p.strip()]
    return json.dumps(parts, ensure_ascii=False)


def _row_to_str(row: object) -> str:
    return (
        f"id: {row['id']}\n"
        f"project_id: {row['project_id'] or '-'}\n"
        f"scope: {row['scope']}\n"
        f"name: {row['name']}\n"
        f"value: {row['value']}\n"
        f"tags: {row['tags']}\n"
        f"created_at: {row['created_at']}\n"
        f"updated_at: {row['updated_at']}"
    )


def add_dict(db_path: Path, name: str, value: str = "", tags: object = None, project_id: str = "") -> str:
    if project_id and not project_exists(db_path, project_id):
        return "ERR: project_id 不存在"
    scope = "project" if project_id else "public"
    project_value: object = project_id if project_id else None
    with open_conn(db_path) as conn:
        if conn.execute(
            "SELECT 1 FROM dict_items WHERE scope=? AND project_id IS ? AND name=?",
            (scope, project_value, name),
        ).fetchone():
            return "ERR: dict name 已存在"
        cursor = conn.execute(
            "INSERT INTO dict_items (project_id, scope, name, value, tags) VALUES (?, ?, ?, ?, ?)",
            (project_value, scope, name, value, normalize_tags(tags)),
        )
    return f"OK id={cursor.lastrowid}"


def get_dict(db_path: Path, dict_id: int) -> str:
    with open_conn(db_path) as conn:
        row = conn.execute(
            "SELECT id, project_id, scope, name, value, tags, created_at, updated_at FROM dict_items WHERE id=?",
            (dict_id,),
        ).fetchone()
    return _row_to_str(row) if row else "ERR: not found"


def get_dict_by_name(db_path: Path, name: str, scope: str = "auto", project_id: str = "") -> str:
    if project_id and not project_exists(db_path, project_id):
        return "ERR: project_id 不存在"
    with open_conn(db_path) as conn:
        if scope == "project":
            if not project_id:
                return "ERR: project scope 需要 project_id"
            row = conn.execute(
                "SELECT id, project_id, scope, name, value, tags, created_at, updated_at FROM dict_items WHERE scope='project' AND project_id=? AND name=?",
                (project_id, name),
            ).fetchone()
        elif scope == "public":
            row = conn.execute(
                "SELECT id, project_id, scope, name, value, tags, created_at, updated_at FROM dict_items WHERE scope='public' AND name=?",
                (name,),
            ).fetchone()
        else:
            row = None
            if project_id:
                row = conn.execute(
                    "SELECT id, project_id, scope, name, value, tags, created_at, updated_at FROM dict_items WHERE scope='project' AND project_id=? AND name=?",
                    (project_id, name),
                ).fetchone()
            if row is None:
                row = conn.execute(
                    "SELECT id, project_id, scope, name, value, tags, created_at, updated_at FROM dict_items WHERE scope='public' AND name=?",
                    (name,),
                ).fetchone()
    return _row_to_str(row) if row else "ERR: not found"


def list_dict(
    db_path: Path,
    scope: str = "all",
    project_id: str = "",
    query: str = "",
    limit: int = 20,
    offset: int = 0,
) -> str:
    where_parts: list[str] = []
    params: list[object] = []
    if scope == "public":
        where_parts.append("scope = 'public'")
    elif scope == "project":
        if not project_id:
            return "ERR: project scope 需要 project_id"
        where_parts.append("scope='project' AND project_id=?")
        params.append(project_id)
    elif project_id:
        where_parts.append("(scope='public' OR (scope='project' AND project_id=?))")
        params.append(project_id)
    if query:
        like = f"%{query}%"
        where_parts.append("(name LIKE ? OR value LIKE ? OR tags LIKE ?)")
        params.extend([like, like, like])
    where_sql = f"WHERE {' AND '.join(where_parts)}" if where_parts else ""
    params.extend([limit, offset])
    with open_conn(db_path) as conn:
        rows = conn.execute(
            f"SELECT id, scope, project_id, name, value, updated_at FROM dict_items {where_sql} ORDER BY id DESC LIMIT ? OFFSET ?",
            params,
        ).fetchall()
    if not rows:
        return "(空)"
    return "\n".join(
        f"[{r['id']}] [{r['scope']}] [{r['project_id'] or '-'}] {r['name']}={r['value']} ({r['updated_at']})"
        for r in rows
    )


def update_dict(db_path: Path, dict_id: int, fields: dict) -> str:
    updates: list[str] = []
    params: list[object] = []
    if "name" in fields:
        n = str(fields["name"]).strip()
        if not n:
            return "ERR: name 不能为空"
        updates.append("name = ?")
        params.append(n)
    if "value" in fields:
        updates.append("value = ?")
        params.append(str(fields["value"]))
    if "tags" in fields:
        updates.append("tags = ?")
        params.append(normalize_tags(fields["tags"]))
    if "project_id" in fields:
        new_pid = str(fields.get("project_id") or "").strip()
        if new_pid and not project_exists(db_path, new_pid):
            return "ERR: project_id 不存在"
        if new_pid:
            updates.extend(["project_id = ?", "scope = 'project'"])
            params.append(new_pid)
        else:
            updates.extend(["project_id = NULL", "scope = 'public'"])
    if not updates:
        return "ERR: 至少提供一个可更新字段"
    updates.append("updated_at = datetime('now')")
    params.append(dict_id)
    with open_conn(db_path) as conn:
        cursor = conn.execute(
            f"UPDATE dict_items SET {', '.join(updates)} WHERE id = ?", params
        )
    return "OK: updated" if cursor.rowcount else "ERR: not found"


def delete_dict(db_path: Path, dict_id: int) -> str:
    with open_conn(db_path) as conn:
        cursor = conn.execute("DELETE FROM dict_items WHERE id = ?", (dict_id,))
    return "OK: deleted" if cursor.rowcount else "ERR: not found"
