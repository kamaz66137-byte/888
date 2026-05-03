"""tool.search_all — 全局搜索工具，同时搜索多个模块。"""
from __future__ import annotations

from pathlib import Path

from db import open_conn


_ALL_MODULES = {"notes", "tasks", "docs", "snippets", "dict", "prompt"}


def search_all(db_path: Path, query: str, modules: list[str] | None = None, limit: int = 5) -> str:
    target_modules = set(modules) & _ALL_MODULES if modules else _ALL_MODULES
    fts_q = '"{}"'.format(query.replace('"', '""'))
    like = f"%{query}%"
    sections: list[str] = []

    with open_conn(db_path) as conn:
        if "notes" in target_modules:
            try:
                rows = conn.execute(
                    "SELECT n.id, n.name, n.created_at FROM notes_fts JOIN notes n ON notes_fts.rowid = n.id WHERE notes_fts MATCH ? ORDER BY rank LIMIT ?",
                    (fts_q, limit),
                ).fetchall()
            except Exception:
                rows = conn.execute(
                    "SELECT id, name, created_at FROM notes WHERE name LIKE ? OR body LIKE ? ORDER BY id DESC LIMIT ?",
                    (like, like, limit),
                ).fetchall()
            if rows:
                lines = [f"  [{r['id']}] {r['name']} ({r['created_at']})" for r in rows]
                sections.append("【notes】\n" + "\n".join(lines))

        if "tasks" in target_modules:
            rows = conn.execute(
                "SELECT id, name, status, priority FROM tasks WHERE name LIKE ? OR description LIKE ? ORDER BY id DESC LIMIT ?",
                (like, like, limit),
            ).fetchall()
            if rows:
                lines = [f"  [{r['id']}] {r['name']} [{r['status']}] [{r['priority']}]" for r in rows]
                sections.append("【tasks】\n" + "\n".join(lines))

        if "docs" in target_modules:
            try:
                rows = conn.execute(
                    "SELECT d.id, d.scope, d.name, d.updated_at FROM docs_fts JOIN docs_knowledge d ON docs_fts.rowid = d.id WHERE docs_fts MATCH ? ORDER BY rank LIMIT ?",
                    (fts_q, limit),
                ).fetchall()
            except Exception:
                rows = conn.execute(
                    "SELECT id, scope, name, updated_at FROM docs_knowledge WHERE name LIKE ? OR content LIKE ? ORDER BY id DESC LIMIT ?",
                    (like, like, limit),
                ).fetchall()
            if rows:
                lines = [f"  [{r['id']}] [{r['scope']}] {r['name']} ({r['updated_at']})" for r in rows]
                sections.append("【docs】\n" + "\n".join(lines))

        if "snippets" in target_modules:
            try:
                rows = conn.execute(
                    "SELECT s.id, s.name, s.language, s.updated_at FROM snippets_fts JOIN snippets s ON snippets_fts.rowid = s.id WHERE snippets_fts MATCH ? ORDER BY rank LIMIT ?",
                    (fts_q, limit),
                ).fetchall()
            except Exception:
                rows = conn.execute(
                    "SELECT id, name, language, updated_at FROM snippets WHERE name LIKE ? OR content LIKE ? ORDER BY id DESC LIMIT ?",
                    (like, like, limit),
                ).fetchall()
            if rows:
                lines = [f"  [{r['id']}] {r['name']} | {r['language']} ({r['updated_at']})" for r in rows]
                sections.append("【snippets】\n" + "\n".join(lines))

        if "dict" in target_modules:
            rows = conn.execute(
                "SELECT id, scope, name, value FROM dict_items WHERE name LIKE ? OR value LIKE ? ORDER BY id DESC LIMIT ?",
                (like, like, limit),
            ).fetchall()
            if rows:
                lines = [f"  [{r['id']}] [{r['scope']}] {r['name']} = {(r['value'] or '')[:60]}" for r in rows]
                sections.append("【dict】\n" + "\n".join(lines))

        if "prompt" in target_modules:
            rows = conn.execute(
                "SELECT id, scope, name FROM prompt_items WHERE name LIKE ? OR content LIKE ? ORDER BY id DESC LIMIT ?",
                (like, like, limit),
            ).fetchall()
            if rows:
                lines = [f"  [{r['id']}] [{r['scope']}] {r['name']}" for r in rows]
                sections.append("【prompt】\n" + "\n".join(lines))

    if not sections:
        return "(empty)"
    return "\n\n".join(sections)


def dispatch_search_all_tool(name: str, arguments: dict, db_path: Path) -> str | None:
    if name != "search/all":
        return None
    query = str(arguments.get("query", "")).strip()
    if not query:
        return "ERR: query is required"
    modules_raw = arguments.get("modules")
    modules: list[str] | None = None
    if modules_raw:
        if isinstance(modules_raw, list):
            modules = [str(m).strip() for m in modules_raw]
        else:
            modules = [m.strip() for m in str(modules_raw).split(",") if m.strip()]
    limit = max(1, min(20, int(arguments.get("limit", 5))))
    return search_all(db_path, query=query, modules=modules, limit=limit)
