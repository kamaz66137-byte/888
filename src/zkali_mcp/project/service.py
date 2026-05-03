"""project.service — 项目/进度/待办业务逻辑层。

所有 SQL 和业务规则在此模块，tool/project.py 只做参数解析与分发。
"""
from __future__ import annotations

import json
from pathlib import Path

from db import open_conn
from project.queries import project_is_active


# ── 工具函数 ──────────────────────────────────────────────────────────────────

def normalize_json_list(value: object) -> str:
    if value is None:
        return "[]"
    if isinstance(value, list):
        clean = [str(item).strip() for item in value if str(item).strip()]
        return json.dumps(clean, ensure_ascii=False)
    text = str(value).strip()
    if not text:
        return "[]"
    if text.startswith("[") and text.endswith("]"):
        return text
    items = [p.strip() for p in text.split(",") if p.strip()]
    return json.dumps(items, ensure_ascii=False)


# ── Project ───────────────────────────────────────────────────────────────────

def add_project(
    db_path: Path,
    project_id: str,
    name: str,
    describe: str = "",
    location: str = "",
    environment: str = "",
    languages: object = None,
    libraries: object = None,
    status: str = "active",
    owner: str = "",
) -> str:
    with open_conn(db_path) as conn:
        if conn.execute("SELECT 1 FROM projects WHERE id = ?", (project_id,)).fetchone():
            return "ERR: project id 已存在"
        conn.execute(
            """
            INSERT INTO projects
            (id, name, describe, location, environment, languages, libraries, status, owner)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                project_id, name, describe, location, environment,
                normalize_json_list(languages), normalize_json_list(libraries),
                status, owner,
            ),
        )
    return f"OK id={project_id}"


def update_project(db_path: Path, project_id: str, fields: dict) -> str:
    updates: list[str] = []
    params: list[object] = []
    for f in ["name", "describe", "location", "environment", "status", "owner"]:
        if f in fields:
            updates.append(f"{f} = ?")
            params.append(str(fields[f]).strip())
    if "languages" in fields:
        updates.append("languages = ?")
        params.append(normalize_json_list(fields["languages"]))
    if "libraries" in fields:
        updates.append("libraries = ?")
        params.append(normalize_json_list(fields["libraries"]))
    if not updates:
        return "ERR: 至少提供一个可更新字段"
    updates.append("updated_at = datetime('now')")
    params.append(project_id)
    with open_conn(db_path) as conn:
        cursor = conn.execute(
            f"UPDATE projects SET {', '.join(updates)} WHERE id = ?", params
        )
    return "OK: updated" if cursor.rowcount else "ERR: not found"


def get_project_detail(db_path: Path, project_id: str) -> str:
    with open_conn(db_path) as conn:
        row = conn.execute(
            """
            SELECT id, name, describe, location, environment, languages, libraries,
                   status, owner, created_at, updated_at
            FROM projects WHERE id = ?
            """,
            (project_id,),
        ).fetchone()
        if row is None:
            return "ERR: not found"
        ps = conn.execute(
            """
            SELECT COUNT(*) AS total,
                   SUM(CASE WHEN status='todo' THEN 1 ELSE 0 END) AS todo,
                   SUM(CASE WHEN status='doing' THEN 1 ELSE 0 END) AS doing,
                   SUM(CASE WHEN status='done' THEN 1 ELSE 0 END) AS done
            FROM progress_items WHERE project_id = ?
            """,
            (project_id,),
        ).fetchone()
        ts = conn.execute(
            """
            SELECT COUNT(*) AS total,
                   SUM(CASE WHEN status='todo' THEN 1 ELSE 0 END) AS todo,
                   SUM(CASE WHEN status='doing' THEN 1 ELSE 0 END) AS doing,
                   SUM(CASE WHEN status='done' THEN 1 ELSE 0 END) AS done
            FROM project_todos WHERE project_id = ?
            """,
            (project_id,),
        ).fetchone()
    return (
        f"id: {row['id']}\n"
        f"name: {row['name']}\n"
        f"describe: {row['describe']}\n"
        f"location: {row['location']}\n"
        f"environment: {row['environment']}\n"
        f"languages: {row['languages']}\n"
        f"libraries: {row['libraries']}\n"
        f"status: {row['status']}\n"
        f"owner: {row['owner']}\n"
        f"progress_total: {ps['total'] or 0}\n"
        f"progress_todo: {ps['todo'] or 0}\n"
        f"progress_doing: {ps['doing'] or 0}\n"
        f"progress_done: {ps['done'] or 0}\n"
        f"todo_total: {ts['total'] or 0}\n"
        f"todo_todo: {ts['todo'] or 0}\n"
        f"todo_doing: {ts['doing'] or 0}\n"
        f"todo_done: {ts['done'] or 0}\n"
        f"created_at: {row['created_at']}\n"
        f"updated_at: {row['updated_at']}"
    )


def list_projects(db_path: Path, status: str = "all", limit: int = 20, offset: int = 0) -> str:
    where_sql = ""
    params: list[object] = []
    if status != "all":
        where_sql = "WHERE p.status = ?"
        params.append(status)
    params.extend([limit, offset])
    with open_conn(db_path) as conn:
        rows = conn.execute(
            f"""
            SELECT p.id, p.name, p.status, p.location,
                   COUNT(t.id) AS todo_total,
                   SUM(CASE WHEN t.status='done' THEN 1 ELSE 0 END) AS todo_done
            FROM projects p
            LEFT JOIN project_todos t ON p.id = t.project_id
            {where_sql}
            GROUP BY p.id, p.name, p.status, p.location
            ORDER BY p.id DESC LIMIT ? OFFSET ?
            """,
            params,
        ).fetchall()
    if not rows:
        return "(空)"
    return "\n".join(
        f"[{r['id']}] [{r['status']}] {r['name']} loc={r['location'] or '-'} todo={r['todo_done'] or 0}/{r['todo_total'] or 0}"
        for r in rows
    )


def delete_project(db_path: Path, project_id: str) -> str:
    with open_conn(db_path) as conn:
        conn.execute("DELETE FROM docs_knowledge WHERE project_id = ?", (project_id,))
        cursor = conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    return "OK: deleted" if cursor.rowcount else "ERR: not found"


# ── Progress ──────────────────────────────────────────────────────────────────

def add_progress(
    db_path: Path,
    project_id: str,
    name: str,
    feature: str = "",
    context: str = "",
    status: str = "todo",
    priority: str = "medium",
    progress: int = 0,
    milestone: str = "",
) -> str:
    ok, err = project_is_active(db_path, project_id)
    if not ok:
        return err
    with open_conn(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO progress_items
            (project_id, name, feature, context, status, priority, progress, milestone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (project_id, name, feature, context, status, priority, progress, milestone),
        )
    return f"OK id={cursor.lastrowid}"


def update_progress(db_path: Path, project_id: str, task_id: int, fields: dict) -> str:
    mutable = ["name", "feature", "context", "status", "priority", "progress", "milestone"]
    updates: list[str] = []
    params: list[object] = []
    for f in mutable:
        if f in fields:
            updates.append(f"{f} = ?")
            params.append(fields[f])
    if not updates:
        return "ERR: 至少提供一个可更新字段"
    updates.append("updated_at = datetime('now')")
    params.extend([project_id, task_id])
    with open_conn(db_path) as conn:
        cursor = conn.execute(
            f"UPDATE progress_items SET {', '.join(updates)} WHERE project_id = ? AND id = ?",
            params,
        )
    return "OK: updated" if cursor.rowcount else "ERR: not found"


def list_progress(db_path: Path, project_id: str, status: str = "all", limit: int = 20, offset: int = 0) -> str:
    where_sql = "WHERE project_id = ?"
    params: list[object] = [project_id]
    if status != "all":
        where_sql += " AND status = ?"
        params.append(status)
    params.extend([limit, offset])
    with open_conn(db_path) as conn:
        rows = conn.execute(
            f"SELECT id, name, feature, context, status, priority, progress, milestone FROM progress_items {where_sql} ORDER BY id DESC LIMIT ? OFFSET ?",
            params,
        ).fetchall()
    if not rows:
        return "(空)"
    return "\n".join(
        f"[{r['id']}] [{r['status']}] [{r['priority']}] {r['name']} feature={r['feature'] or '-'} progress={r['progress']} milestone={r['milestone'] or '-'}"
        for r in rows
    )


def stats_progress(db_path: Path, project_id: str) -> str:
    with open_conn(db_path) as conn:
        rows = conn.execute(
            "SELECT status, COUNT(*) AS total FROM progress_items WHERE project_id = ? GROUP BY status ORDER BY status",
            (project_id,),
        ).fetchall()
        total = conn.execute(
            "SELECT COUNT(*) FROM progress_items WHERE project_id = ?", (project_id,)
        ).fetchone()[0]
    lines = [f"total: {total}"]
    for r in rows:
        lines.append(f"{r['status']}: {r['total']}")
    return "\n".join(lines)


# ── Todo ──────────────────────────────────────────────────────────────────────

def add_todo(
    db_path: Path,
    project_id: str,
    name: str,
    feature: str = "",
    context: str = "",
    step_order: int = 1,
    status: str = "todo",
) -> str:
    ok, err = project_is_active(db_path, project_id)
    if not ok:
        return err
    with open_conn(db_path) as conn:
        cursor = conn.execute(
            "INSERT INTO project_todos (project_id, name, feature, context, step_order, status) VALUES (?, ?, ?, ?, ?, ?)",
            (project_id, name, feature, context, step_order, status),
        )
    return f"OK id={cursor.lastrowid}"


def update_todo(db_path: Path, project_id: str, todo_id: int, fields: dict) -> str:
    mutable = ["name", "feature", "context", "step_order", "status"]
    updates: list[str] = []
    params: list[object] = []
    for f in mutable:
        if f in fields:
            updates.append(f"{f} = ?")
            params.append(fields[f])
    if not updates:
        return "ERR: 至少提供一个可更新字段"
    updates.append("updated_at = datetime('now')")
    params.extend([project_id, todo_id])
    with open_conn(db_path) as conn:
        cursor = conn.execute(
            f"UPDATE project_todos SET {', '.join(updates)} WHERE project_id = ? AND id = ?",
            params,
        )
    return "OK: updated" if cursor.rowcount else "ERR: not found"


def done_todo(db_path: Path, project_id: str, todo_id: int) -> str:
    with open_conn(db_path) as conn:
        cursor = conn.execute(
            "UPDATE project_todos SET status='done', updated_at=datetime('now') WHERE project_id=? AND id=?",
            (project_id, todo_id),
        )
    return "OK: updated" if cursor.rowcount else "ERR: not found"


def list_todos(db_path: Path, project_id: str, status: str = "all", limit: int = 20, offset: int = 0) -> str:
    where_sql = "WHERE project_id = ?"
    params: list[object] = [project_id]
    if status != "all":
        where_sql += " AND status = ?"
        params.append(status)
    params.extend([limit, offset])
    with open_conn(db_path) as conn:
        rows = conn.execute(
            f"SELECT id, name, feature, context, step_order, status, updated_at FROM project_todos {where_sql} ORDER BY step_order ASC, id ASC LIMIT ? OFFSET ?",
            params,
        ).fetchall()
    if not rows:
        return "(空)"
    return "\n".join(
        f"[{r['id']}] step={r['step_order']} [{r['status']}] {r['name']} feature={r['feature'] or '-'} ({r['updated_at']})"
        for r in rows
    )


def delete_todo(db_path: Path, project_id: str, todo_id: int) -> str:
    with open_conn(db_path) as conn:
        cursor = conn.execute(
            "DELETE FROM project_todos WHERE project_id = ? AND id = ?", (project_id, todo_id)
        )
    return "OK: deleted" if cursor.rowcount else "ERR: not found"
