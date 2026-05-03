"""tool.export_import — 项目数据导出/导入工具。"""
from __future__ import annotations

import json
from pathlib import Path

from db import open_conn


def _row_to_dict(row) -> dict:
    return dict(row)


def export_project(db_path: Path, project_id: str) -> str:
    with open_conn(db_path) as conn:
        project_row = conn.execute(
            "SELECT * FROM projects WHERE id = ?", (project_id,)
        ).fetchone()
        if project_row is None:
            return f"ERR: project not found: {project_id}"

        todos = [_row_to_dict(r) for r in conn.execute(
            "SELECT * FROM project_todos WHERE project_id = ? ORDER BY step_order", (project_id,)
        ).fetchall()]
        progress = [_row_to_dict(r) for r in conn.execute(
            "SELECT * FROM progress_items WHERE project_id = ? ORDER BY id", (project_id,)
        ).fetchall()]
        memories = [_row_to_dict(r) for r in conn.execute(
            "SELECT * FROM memories WHERE project_id = ? ORDER BY id", (project_id,)
        ).fetchall()]
        docs = [_row_to_dict(r) for r in conn.execute(
            "SELECT * FROM docs_knowledge WHERE project_id = ? ORDER BY id", (project_id,)
        ).fetchall()]
        env = [_row_to_dict(r) for r in conn.execute(
            "SELECT * FROM project_env WHERE project_id = ? ORDER BY key", (project_id,)
        ).fetchall()]
        snippets = [_row_to_dict(r) for r in conn.execute(
            "SELECT * FROM snippets WHERE project_id = ? ORDER BY id", (project_id,)
        ).fetchall()]
        dict_items = [_row_to_dict(r) for r in conn.execute(
            "SELECT * FROM dict_items WHERE project_id = ? ORDER BY id", (project_id,)
        ).fetchall()]
        prompts = [_row_to_dict(r) for r in conn.execute(
            "SELECT * FROM prompt_items WHERE project_id = ? ORDER BY id", (project_id,)
        ).fetchall()]

    data = {
        "project": _row_to_dict(project_row),
        "todos": todos,
        "progress": progress,
        "memories": memories,
        "docs": docs,
        "env": env,
        "snippets": snippets,
        "dict_items": dict_items,
        "prompts": prompts,
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def import_project(db_path: Path, data_str: str, overwrite: bool = False) -> str:
    try:
        data = json.loads(data_str)
    except json.JSONDecodeError as e:
        return f"ERR: JSON 解析失败: {e}"

    project = data.get("project")
    if not project or not isinstance(project, dict):
        return "ERR: 缺少 project 字段"

    project_id = str(project.get("id", "")).strip()
    if not project_id:
        return "ERR: project.id 不能为空"

    counts: dict[str, int] = {}

    with open_conn(db_path) as conn:
        exists = conn.execute("SELECT 1 FROM projects WHERE id = ?", (project_id,)).fetchone()
        if exists:
            if not overwrite:
                return f"ERR: project {project_id} 已存在，传 overwrite=true 强制覆盖"
            # Delete existing project data (cascades handle related tables)
            conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))

        conn.execute(
            """INSERT INTO projects (id, name, describe, location, environment, languages, libraries, status, owner)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                project_id,
                project.get("name", ""),
                project.get("describe", ""),
                project.get("location", ""),
                project.get("environment", ""),
                project.get("languages", "[]"),
                project.get("libraries", "[]"),
                project.get("status", "active"),
                project.get("owner", ""),
            ),
        )
        counts["project"] = 1

        for todo in data.get("todos", []):
            conn.execute(
                "INSERT INTO project_todos (project_id, name, feature, context, step_order, status) VALUES (?, ?, ?, ?, ?, ?)",
                (project_id, todo.get("name", ""), todo.get("feature", ""), todo.get("context", ""), todo.get("step_order", 1), todo.get("status", "todo")),
            )
        counts["todos"] = len(data.get("todos", []))

        for prog in data.get("progress", []):
            conn.execute(
                "INSERT INTO progress_items (project_id, name, feature, context, status, priority, progress, milestone) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (project_id, prog.get("name", ""), prog.get("feature", ""), prog.get("context", ""), prog.get("status", "todo"), prog.get("priority", "medium"), prog.get("progress", 0), prog.get("milestone", "")),
            )
        counts["progress"] = len(data.get("progress", []))

        for mem in data.get("memories", []):
            conn.execute(
                "INSERT OR IGNORE INTO memories (project_id, scope, namespace, key, value, ttl_seconds) VALUES (?, ?, ?, ?, ?, ?)",
                (project_id, mem.get("scope", "project"), mem.get("namespace", "default"), mem.get("key", ""), mem.get("value", ""), mem.get("ttl_seconds")),
            )
        counts["memories"] = len(data.get("memories", []))

        for doc in data.get("docs", []):
            conn.execute(
                "INSERT INTO docs_knowledge (project_id, scope, name, content, tags) VALUES (?, 'project', ?, ?, ?)",
                (project_id, doc.get("name", ""), doc.get("content", ""), doc.get("tags", "[]")),
            )
        counts["docs"] = len(data.get("docs", []))

        for env in data.get("env", []):
            conn.execute(
                "INSERT OR REPLACE INTO project_env (project_id, key, value, description) VALUES (?, ?, ?, ?)",
                (project_id, env.get("key", ""), env.get("value", ""), env.get("description", "")),
            )
        counts["env"] = len(data.get("env", []))

        for snip in data.get("snippets", []):
            conn.execute(
                "INSERT INTO snippets (project_id, scope, name, language, content, tags) VALUES (?, 'project', ?, ?, ?, ?)",
                (project_id, snip.get("name", ""), snip.get("language", ""), snip.get("content", ""), snip.get("tags", "[]")),
            )
        counts["snippets"] = len(data.get("snippets", []))

        for di in data.get("dict_items", []):
            conn.execute(
                "INSERT OR IGNORE INTO dict_items (project_id, scope, name, value, tags) VALUES (?, 'project', ?, ?, ?)",
                (project_id, di.get("name", ""), di.get("value", ""), di.get("tags", "[]")),
            )
        counts["dict_items"] = len(data.get("dict_items", []))

        for pr in data.get("prompts", []):
            conn.execute(
                "INSERT OR IGNORE INTO prompt_items (project_id, scope, name, content, tags) VALUES (?, 'project', ?, ?, ?)",
                (project_id, pr.get("name", ""), pr.get("content", ""), pr.get("tags", "[]")),
            )
        counts["prompts"] = len(data.get("prompts", []))

    summary = " ".join(f"{k}={v}" for k, v in counts.items())
    return f"OK id={project_id} {summary}"


def dispatch_export_import_tool(name: str, arguments: dict, db_path: Path) -> str | None:
    if name == "export/project":
        project_id = str(arguments.get("id", "")).strip()
        if not project_id:
            return "ERR: id is required"
        return export_project(db_path, project_id)
    if name == "import/project":
        data_str = str(arguments.get("data", "")).strip()
        if not data_str:
            return "ERR: data is required"
        overwrite = bool(arguments.get("overwrite", False))
        return import_project(db_path, data_str, overwrite=overwrite)
    return None
