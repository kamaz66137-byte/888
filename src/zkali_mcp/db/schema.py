from __future__ import annotations

from pathlib import Path
import sqlite3

from .connection import open_conn


def _has_column(conn: sqlite3.Connection, table: str, column: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(row[1] == column for row in rows)


def _ensure_column(conn: sqlite3.Connection, table: str, column: str, definition: str) -> None:
    if not _has_column(conn, table, column):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def _name_expr(conn: sqlite3.Connection, table: str) -> str:
    has_name = _has_column(conn, table, "name")
    has_title = _has_column(conn, table, "title")
    if has_name and has_title:
        return "CASE WHEN TRIM(name) = '' THEN title ELSE name END"
    if has_name:
        return "name"
    if has_title:
        return "title"
    return "''"


def _col_expr(conn: sqlite3.Connection, table: str, column: str, fallback: str) -> str:
    if _has_column(conn, table, column):
        return column
    return fallback


def _migrate_legacy_title_columns(conn: sqlite3.Connection) -> None:
    if _has_column(conn, "notes", "title"):
        name_expr = _name_expr(conn, "notes")
        created_expr = _col_expr(conn, "notes", "created_at", "datetime('now')")
        updated_expr = _col_expr(conn, "notes", "updated_at", created_expr)
        conn.execute("DROP TABLE IF EXISTS notes_new")
        conn.execute(
            """
            CREATE TABLE notes_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                body TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.execute(
            f"""
            INSERT INTO notes_new (id, name, body, created_at, updated_at)
            SELECT id, {name_expr}, body, {created_expr}, {updated_expr}
            FROM notes
            """
        )
        conn.execute("DROP TABLE notes")
        conn.execute("ALTER TABLE notes_new RENAME TO notes")

    if _has_column(conn, "tasks", "title"):
        name_expr = _name_expr(conn, "tasks")
        due_expr = _col_expr(conn, "tasks", "due_date", "NULL")
        created_expr = _col_expr(conn, "tasks", "created_at", "datetime('now')")
        updated_expr = _col_expr(conn, "tasks", "updated_at", created_expr)
        conn.execute("DROP TABLE IF EXISTS tasks_new")
        conn.execute(
            """
            CREATE TABLE tasks_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'todo'
                    CHECK(status IN ('todo', 'doing', 'done')),
                priority TEXT NOT NULL DEFAULT 'medium'
                    CHECK(priority IN ('low', 'medium', 'high')),
                due_date TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.execute(
            f"""
            INSERT INTO tasks_new (id, name, description, status, priority, due_date, created_at, updated_at)
            SELECT id, {name_expr}, description, status, priority, {due_expr}, {created_expr}, {updated_expr}
            FROM tasks
            """
        )
        conn.execute("DROP TABLE tasks")
        conn.execute("ALTER TABLE tasks_new RENAME TO tasks")

    if _has_column(conn, "progress_items", "title"):
        name_expr = _name_expr(conn, "progress_items")
        feature_expr = _col_expr(conn, "progress_items", "feature", "''")
        context_expr = _col_expr(conn, "progress_items", "context", "''")
        status_expr = _col_expr(conn, "progress_items", "status", "'todo'")
        priority_expr = _col_expr(conn, "progress_items", "priority", "'medium'")
        progress_expr = _col_expr(conn, "progress_items", "progress", "0")
        milestone_expr = _col_expr(conn, "progress_items", "milestone", "''")
        created_expr = _col_expr(conn, "progress_items", "created_at", "datetime('now')")
        updated_expr = _col_expr(conn, "progress_items", "updated_at", created_expr)
        conn.execute("DROP TABLE IF EXISTS progress_items_new")
        conn.execute(
            """
            CREATE TABLE progress_items_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                name TEXT NOT NULL,
                feature TEXT NOT NULL DEFAULT '',
                context TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'todo'
                    CHECK(status IN ('todo', 'doing', 'done')),
                priority TEXT NOT NULL DEFAULT 'medium'
                    CHECK(priority IN ('low', 'medium', 'high')),
                progress INTEGER NOT NULL DEFAULT 0
                    CHECK(progress >= 0 AND progress <= 100),
                milestone TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            f"""
            INSERT INTO progress_items_new (
                id, project_id, name, feature, context, status, priority, progress, milestone, created_at, updated_at
            )
            SELECT
                id, project_id, {name_expr}, {feature_expr}, {context_expr}, {status_expr}, {priority_expr}, {progress_expr}, {milestone_expr}, {created_expr}, {updated_expr}
            FROM progress_items
            """
        )
        conn.execute("DROP TABLE progress_items")
        conn.execute("ALTER TABLE progress_items_new RENAME TO progress_items")

    if _has_column(conn, "docs_knowledge", "title"):
        name_expr = _name_expr(conn, "docs_knowledge")
        content_expr = _col_expr(conn, "docs_knowledge", "content", "''")
        tags_expr = _col_expr(conn, "docs_knowledge", "tags", "'[]'")
        created_expr = _col_expr(conn, "docs_knowledge", "created_at", "datetime('now')")
        updated_expr = _col_expr(conn, "docs_knowledge", "updated_at", created_expr)
        conn.execute("DROP TABLE IF EXISTS docs_knowledge_new")
        conn.execute(
            """
            CREATE TABLE docs_knowledge_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT,
                scope TEXT NOT NULL
                    CHECK(scope IN ('public', 'project')),
                name TEXT NOT NULL,
                content TEXT NOT NULL DEFAULT '',
                tags TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
                CHECK (
                    (scope = 'public' AND project_id IS NULL)
                    OR (scope = 'project' AND project_id IS NOT NULL)
                )
            )
            """
        )
        conn.execute(
            f"""
            INSERT INTO docs_knowledge_new (
                id, project_id, scope, name, content, tags, created_at, updated_at
            )
            SELECT
                id, project_id, scope, {name_expr}, {content_expr}, {tags_expr}, {created_expr}, {updated_expr}
            FROM docs_knowledge
            """
        )
        conn.execute("DROP TABLE docs_knowledge")
        conn.execute("ALTER TABLE docs_knowledge_new RENAME TO docs_knowledge")

    if _has_column(conn, "project_todos", "title"):
        name_expr = _name_expr(conn, "project_todos")
        feature_expr = _col_expr(conn, "project_todos", "feature", "''")
        context_expr = _col_expr(conn, "project_todos", "context", "''")
        step_order_expr = _col_expr(conn, "project_todos", "step_order", "1")
        status_expr = _col_expr(conn, "project_todos", "status", "'todo'")
        created_expr = _col_expr(conn, "project_todos", "created_at", "datetime('now')")
        updated_expr = _col_expr(conn, "project_todos", "updated_at", created_expr)
        conn.execute("DROP TABLE IF EXISTS project_todos_new")
        conn.execute(
            """
            CREATE TABLE project_todos_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                name TEXT NOT NULL,
                feature TEXT NOT NULL DEFAULT '',
                context TEXT NOT NULL DEFAULT '',
                step_order INTEGER NOT NULL DEFAULT 1,
                status TEXT NOT NULL DEFAULT 'todo'
                    CHECK(status IN ('todo', 'doing', 'done')),
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            f"""
            INSERT INTO project_todos_new (
                id, project_id, name, feature, context, step_order, status, created_at, updated_at
            )
            SELECT
                id, project_id, {name_expr}, {feature_expr}, {context_expr}, {step_order_expr}, {status_expr}, {created_expr}, {updated_expr}
            FROM project_todos
            """
        )
        conn.execute("DROP TABLE project_todos")
        conn.execute("ALTER TABLE project_todos_new RENAME TO project_todos")


def init_db(db_path: Path) -> None:
    with open_conn(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                body TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'todo'
                    CHECK(status IN ('todo', 'doing', 'done')),
                priority TEXT NOT NULL DEFAULT 'medium'
                    CHECK(priority IN ('low', 'medium', 'high')),
                due_date TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                describe TEXT NOT NULL DEFAULT '',
                location TEXT NOT NULL DEFAULT '',
                environment TEXT NOT NULL DEFAULT '',
                languages TEXT NOT NULL DEFAULT '[]',
                libraries TEXT NOT NULL DEFAULT '[]',
                status TEXT NOT NULL DEFAULT 'active'
                    CHECK(status IN ('active', 'paused', 'archived')),
                owner TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS progress_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                name TEXT NOT NULL,
                feature TEXT NOT NULL DEFAULT '',
                context TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'todo'
                    CHECK(status IN ('todo', 'doing', 'done')),
                priority TEXT NOT NULL DEFAULT 'medium'
                    CHECK(priority IN ('low', 'medium', 'high')),
                progress INTEGER NOT NULL DEFAULT 0
                    CHECK(progress >= 0 AND progress <= 100),
                milestone TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                scope TEXT NOT NULL
                    CHECK(scope IN ('session', 'project', 'global')),
                namespace TEXT NOT NULL DEFAULT 'default',
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                ttl_seconds INTEGER,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                UNIQUE(project_id, scope, namespace, key),
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS docs_knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT,
                scope TEXT NOT NULL
                    CHECK(scope IN ('public', 'project')),
                name TEXT NOT NULL,
                content TEXT NOT NULL DEFAULT '',
                tags TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
                CHECK (
                    (scope = 'public' AND project_id IS NULL)
                    OR (scope = 'project' AND project_id IS NOT NULL)
                )
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS dict_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT,
                scope TEXT NOT NULL
                    CHECK(scope IN ('public', 'project')),
                name TEXT NOT NULL,
                value TEXT NOT NULL DEFAULT '',
                tags TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
                CHECK (
                    (scope = 'public' AND project_id IS NULL)
                    OR (scope = 'project' AND project_id IS NOT NULL)
                ),
                UNIQUE(scope, project_id, name)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS prompt_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT,
                scope TEXT NOT NULL
                    CHECK(scope IN ('public', 'project')),
                name TEXT NOT NULL,
                content TEXT NOT NULL DEFAULT '',
                tags TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
                CHECK (
                    (scope = 'public' AND project_id IS NULL)
                    OR (scope = 'project' AND project_id IS NOT NULL)
                ),
                UNIQUE(scope, project_id, name)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS project_todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                name TEXT NOT NULL,
                feature TEXT NOT NULL DEFAULT '',
                context TEXT NOT NULL DEFAULT '',
                step_order INTEGER NOT NULL DEFAULT 1,
                status TEXT NOT NULL DEFAULT 'todo'
                    CHECK(status IN ('todo', 'doing', 'done')),
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
            """
        )

        _ensure_column(conn, "projects", "describe", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "notes", "name", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "tasks", "name", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "projects", "location", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "projects", "environment", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "projects", "languages", "TEXT NOT NULL DEFAULT '[]'")
        _ensure_column(conn, "projects", "libraries", "TEXT NOT NULL DEFAULT '[]'")
        _ensure_column(conn, "progress_items", "name", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "progress_items", "feature", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "progress_items", "context", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "docs_knowledge", "name", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "project_todos", "name", "TEXT NOT NULL DEFAULT ''")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS snippets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT,
                scope TEXT NOT NULL DEFAULT 'public'
                    CHECK(scope IN ('public', 'project')),
                name TEXT NOT NULL,
                language TEXT NOT NULL DEFAULT '',
                content TEXT NOT NULL DEFAULT '',
                tags TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS project_env (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL DEFAULT '',
                description TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                UNIQUE(project_id, key),
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS event_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT,
                event_type TEXT NOT NULL DEFAULT 'info',
                summary TEXT NOT NULL,
                detail TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
            """
        )

        _migrate_legacy_title_columns(conn)

        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_projects_location ON projects(location)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_progress_project ON progress_items(project_id)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_progress_feature ON progress_items(feature)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_project_todos_project ON project_todos(project_id)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_project_todos_status ON project_todos(status)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_memories_project ON memories(project_id)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_docs_scope ON docs_knowledge(scope)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_docs_project ON docs_knowledge(project_id)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_dict_scope ON dict_items(scope)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_dict_project ON dict_items(project_id)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_prompt_scope ON prompt_items(scope)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_prompt_project ON prompt_items(project_id)"
        )

        # 统一对外命名：project / project_todos / project_detail
        # 说明：底层仍保留 projects 物理表，避免破坏已有工具和历史数据。
        conn.execute("DROP VIEW IF EXISTS project")
        conn.execute(
            """
            CREATE VIEW project AS
            SELECT
                id,
                name,
                status,
                owner,
                created_at,
                updated_at
            FROM projects
            """
        )
        conn.execute("DROP VIEW IF EXISTS project_detail")
        conn.execute(
            """
            CREATE VIEW project_detail AS
            SELECT
                id AS project_id,
                name,
                describe,
                location,
                environment,
                languages,
                libraries,
                status,
                owner,
                created_at,
                updated_at
            FROM projects
            """
        )
