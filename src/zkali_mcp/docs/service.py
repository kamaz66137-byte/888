"""docs.service — 知识文档业务逻辑层。"""
from __future__ import annotations

import json
from pathlib import Path

from db import open_conn
from project.queries import project_exists


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


def _scope_filter(
    scope: str, project_id: str, alias: str = ""
) -> tuple[str, list[object]]:
    """Build WHERE clause for scope/project filtering (without query).

    Args:
        alias: optional table alias prefix (e.g. "d") to qualify column names.
    """
    pfx = f"{alias}." if alias else ""
    where_parts: list[str] = []
    params: list[object] = []
    if scope == "public":
        where_parts.append(f"{pfx}scope = 'public'")
    elif scope == "project":
        if not project_id:
            raise ValueError("project scope 需要 project_id")
        where_parts.append(f"{pfx}scope = 'project' AND {pfx}project_id = ?")
        params.append(project_id)
    elif project_id:
        where_parts.append(f"({pfx}scope = 'public' OR ({pfx}scope = 'project' AND {pfx}project_id = ?))")
        params.append(project_id)
    where_sql = f"WHERE {' AND '.join(where_parts)}" if where_parts else ""
    return where_sql, params


def add_docs(db_path: Path, name: str, content: str = "", tags: object = None, project_id: str = "") -> str:
    if project_id and not project_exists(db_path, project_id):
        return "ERR: project_id 不存在"
    scope = "project" if project_id else "public"
    project_value: object = project_id if project_id else None
    with open_conn(db_path) as conn:
        cursor = conn.execute(
            "INSERT INTO docs_knowledge (project_id, scope, name, content, tags) VALUES (?, ?, ?, ?, ?)",
            (project_value, scope, name, content, normalize_tags(tags)),
        )
    return f"OK id={cursor.lastrowid}"


def get_docs(db_path: Path, doc_id: int) -> str:
    with open_conn(db_path) as conn:
        row = conn.execute(
            "SELECT id, project_id, scope, name, content, tags, created_at, updated_at FROM docs_knowledge WHERE id = ?",
            (doc_id,),
        ).fetchone()
    if row is None:
        return "ERR: not found"
    return (
        f"id: {row['id']}\n"
        f"project_id: {row['project_id'] or '-'}\n"
        f"scope: {row['scope']}\n"
        f"name: {row['name']}\n"
        f"content: {row['content']}\n"
        f"tags: {row['tags']}\n"
        f"created_at: {row['created_at']}\n"
        f"updated_at: {row['updated_at']}"
    )


def list_docs(
    db_path: Path,
    scope: str = "all",
    project_id: str = "",
    query: str = "",
    limit: int = 20,
    offset: int = 0,
) -> str:
    with open_conn(db_path) as conn:
        if query:
            fts_q = '"{}"'.format(query.replace('"', '""'))
            try:
                # Use FTS5 to find matching ids, then apply scope filter with alias
                fts_ids = [
                    row[0]
                    for row in conn.execute(
                        "SELECT rowid FROM docs_fts WHERE docs_fts MATCH ? LIMIT 500",
                        (fts_q,),
                    ).fetchall()
                ]
                if not fts_ids:
                    return "(空)"
                try:
                    scope_where, scope_params = _scope_filter(scope, project_id, alias="d")
                except ValueError as e:
                    return f"ERR: {e}"
                id_placeholders = ",".join("?" * len(fts_ids))
                id_where = f"d.id IN ({id_placeholders})"
                if scope_where:
                    combined_where = f"WHERE {id_where} AND ({scope_where[6:]})"
                else:
                    combined_where = f"WHERE {id_where}"
                rows = conn.execute(
                    f"SELECT d.id, d.scope, d.project_id, d.name, d.updated_at FROM docs_knowledge d {combined_where} ORDER BY d.id DESC LIMIT ? OFFSET ?",
                    fts_ids + scope_params + [limit, offset],
                ).fetchall()
            except Exception:
                # Fallback to LIKE
                try:
                    where_sql, params = _scope_filter(scope, project_id)
                except ValueError as e:
                    return f"ERR: {e}"
                like = f"%{query}%"
                query_clause = "(name LIKE ? OR content LIKE ? OR tags LIKE ?)"
                full_where = f"{where_sql} AND {query_clause}" if where_sql else f"WHERE {query_clause}"
                rows = conn.execute(
                    f"SELECT id, scope, project_id, name, updated_at FROM docs_knowledge {full_where} ORDER BY id DESC LIMIT ? OFFSET ?",
                    params + [like, like, like, limit, offset],
                ).fetchall()
        else:
            try:
                where_sql, params = _scope_filter(scope, project_id)
            except ValueError as e:
                return f"ERR: {e}"
            rows = conn.execute(
                f"SELECT id, scope, project_id, name, updated_at FROM docs_knowledge {where_sql} ORDER BY id DESC LIMIT ? OFFSET ?",
                params + [limit, offset],
            ).fetchall()

    if not rows:
        return "(空)"
    return "\n".join(
        f"[{r['id']}] [{r['scope']}] [{r['project_id'] or '-'}] {r['name']} ({r['updated_at']})"
        for r in rows
    )


def update_docs(db_path: Path, doc_id: int, fields: dict) -> str:
    updates: list[str] = []
    params: list[object] = []
    if "name" in fields:
        updates.append("name = ?")
        params.append(str(fields["name"]).strip())
    if "content" in fields:
        updates.append("content = ?")
        params.append(str(fields["content"]))
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
    params.append(doc_id)
    with open_conn(db_path) as conn:
        cursor = conn.execute(
            f"UPDATE docs_knowledge SET {', '.join(updates)} WHERE id = ?", params
        )
    return "OK: updated" if cursor.rowcount else "ERR: not found"


def delete_docs(db_path: Path, doc_id: int) -> str:
    with open_conn(db_path) as conn:
        cursor = conn.execute("DELETE FROM docs_knowledge WHERE id = ?", (doc_id,))
    return "OK: deleted" if cursor.rowcount else "ERR: not found"
