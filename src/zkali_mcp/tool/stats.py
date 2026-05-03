"""tool.stats — 全局统计工具 + 过期记忆清理工具。"""
from __future__ import annotations

from pathlib import Path

from db import open_conn


def stats_all(db_path: Path) -> str:
    with open_conn(db_path) as conn:
        notes_count = conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0]

        task_row = conn.execute(
            "SELECT COUNT(*) total, "
            "SUM(CASE WHEN status='todo' THEN 1 ELSE 0 END) todo, "
            "SUM(CASE WHEN status='doing' THEN 1 ELSE 0 END) doing, "
            "SUM(CASE WHEN status='done' THEN 1 ELSE 0 END) done "
            "FROM tasks"
        ).fetchone()

        proj_row = conn.execute(
            "SELECT COUNT(*) total, "
            "SUM(CASE WHEN status='active' THEN 1 ELSE 0 END) active, "
            "SUM(CASE WHEN status='paused' THEN 1 ELSE 0 END) paused, "
            "SUM(CASE WHEN status='archived' THEN 1 ELSE 0 END) archived "
            "FROM projects"
        ).fetchone()

        docs_row = conn.execute(
            "SELECT COUNT(*) total, "
            "SUM(CASE WHEN scope='public' THEN 1 ELSE 0 END) public, "
            "SUM(CASE WHEN scope='project' THEN 1 ELSE 0 END) project "
            "FROM docs_knowledge"
        ).fetchone()

        snippets_count = conn.execute("SELECT COUNT(*) FROM snippets").fetchone()[0]
        dict_count = conn.execute("SELECT COUNT(*) FROM dict_items").fetchone()[0]
        prompt_count = conn.execute("SELECT COUNT(*) FROM prompt_items").fetchone()[0]
        memory_count = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
        log_count = conn.execute("SELECT COUNT(*) FROM event_log").fetchone()[0]
        progress_count = conn.execute("SELECT COUNT(*) FROM progress_items").fetchone()[0]
        todo_count = conn.execute("SELECT COUNT(*) FROM project_todos").fetchone()[0]
        env_count = conn.execute("SELECT COUNT(*) FROM project_env").fetchone()[0]

    lines = [
        f"notes: {notes_count}",
        f"tasks: {task_row[0]} (todo:{task_row[1] or 0} doing:{task_row[2] or 0} done:{task_row[3] or 0})",
        f"projects: {proj_row[0]} (active:{proj_row[1] or 0} paused:{proj_row[2] or 0} archived:{proj_row[3] or 0})",
        f"progress_items: {progress_count}",
        f"project_todos: {todo_count}",
        f"docs: {docs_row[0]} (public:{docs_row[1] or 0} project:{docs_row[2] or 0})",
        f"snippets: {snippets_count}",
        f"dict_items: {dict_count}",
        f"prompt_items: {prompt_count}",
        f"memories: {memory_count}",
        f"env_vars: {env_count}",
        f"event_logs: {log_count}",
    ]
    return "\n".join(lines)


def cleanup_expired(db_path: Path) -> str:
    with open_conn(db_path) as conn:
        cursor = conn.execute(
            """
            DELETE FROM memories
            WHERE ttl_seconds IS NOT NULL
              AND datetime(created_at, '+' || ttl_seconds || ' seconds') < datetime('now')
            """
        )
    return f"OK deleted={cursor.rowcount}"


def dispatch_stats_tool(name: str, arguments: dict, db_path: Path) -> str | None:
    if name == "stats/all":
        return stats_all(db_path)
    if name == "cleanup/expired":
        return cleanup_expired(db_path)
    return None
