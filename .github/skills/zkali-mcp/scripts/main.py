#!/usr/bin/env python3
"""zkali-mcp 示例 MCP Server

功能：笔记 + 任务双模块，sqlite3 持久化，stdio 传输。
用法：
    python main.py                          # 启动（等待 stdio MCP 连接）
    mcp dev main.py                         # 调试模式（Inspector UI）
    python main.py --db /path/to/data.db   # 自定义 DB 路径

注册到 VS Code (.vscode/mcp.json):
    {
      "servers": {
        "zkali-mcp": {
          "type": "stdio",
          "command": "python",
          "args": ["${workspaceFolder}/.github/skills/zkali-mcp/scripts/main.py"]
        }
      }
    }
"""

from __future__ import annotations

import argparse
import asyncio
import sqlite3
import sys
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# ---------------------------------------------------------------------------
# CLI 参数
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="zkali-mcp MCP Server (sqlite3)")
    parser.add_argument(
        "--db",
        default=str(Path(__file__).parent / "zkali.db"),
        help="sqlite3 数据库路径（默认：scripts/zkali.db）",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# 数据库初始化
# ---------------------------------------------------------------------------

_DB_PATH: Path = Path(__file__).parent / "zkali.db"


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def _init_db() -> None:
    with _conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT    NOT NULL,
                body  TEXT    NOT NULL DEFAULT '',
                ts    TEXT    DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                title    TEXT NOT NULL,
                status   TEXT NOT NULL DEFAULT 'todo'
                         CHECK(status IN ('todo','doing','done')),
                priority TEXT NOT NULL DEFAULT 'medium'
                         CHECK(priority IN ('low','medium','high')),
                created  TEXT DEFAULT (datetime('now'))
            )
        """)


# ---------------------------------------------------------------------------
# 工具定义
# ---------------------------------------------------------------------------

_TOOLS: list[Tool] = [
    # ---- 笔记 ----
    Tool(
        name="note_add",
        description="添加一条笔记（title + body）",
        inputSchema={
            "type": "object",
            "properties": {
                "title": {"type": "string", "minLength": 1},
                "body":  {"type": "string"},
            },
            "required": ["title"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="note_search",
        description="全文搜索笔记（按 title 或 body 模糊匹配）",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "minLength": 1},
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="note_list",
        description="列出最近 N 条笔记（默认 20）",
        inputSchema={
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "minimum": 1, "maximum": 200},
            },
            "additionalProperties": False,
        },
    ),
    Tool(
        name="note_delete",
        description="按 ID 删除笔记",
        inputSchema={
            "type": "object",
            "properties": {
                "id": {"type": "integer", "minimum": 1},
            },
            "required": ["id"],
            "additionalProperties": False,
        },
    ),
    # ---- 任务 ----
    Tool(
        name="task_create",
        description="创建任务（可指定优先级）",
        inputSchema={
            "type": "object",
            "properties": {
                "title":    {"type": "string", "minLength": 1},
                "priority": {"type": "string", "enum": ["low", "medium", "high"]},
            },
            "required": ["title"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="task_list",
        description="列出任务，可按状态筛选",
        inputSchema={
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["all", "todo", "doing", "done"],
                },
            },
            "additionalProperties": False,
        },
    ),
    Tool(
        name="task_update",
        description="更新任务状态",
        inputSchema={
            "type": "object",
            "properties": {
                "id":     {"type": "integer", "minimum": 1},
                "status": {"type": "string", "enum": ["todo", "doing", "done"]},
            },
            "required": ["id", "status"],
            "additionalProperties": False,
        },
    ),
    Tool(
        name="task_delete",
        description="按 ID 删除任务",
        inputSchema={
            "type": "object",
            "properties": {
                "id": {"type": "integer", "minimum": 1},
            },
            "required": ["id"],
            "additionalProperties": False,
        },
    ),
]

# ---------------------------------------------------------------------------
# Server 与 handler
# ---------------------------------------------------------------------------

app = Server("zkali-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return _TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:  # noqa: C901
    # 使用 asyncio.to_thread 包装所有同步 DB 操作，避免阻塞事件循环
    result = await asyncio.to_thread(_handle_sync, name, arguments)
    return [TextContent(type="text", text=result)]


def _handle_sync(name: str, arguments: dict) -> str:
    """同步 handler，在 thread 中运行"""
    # ---- notes ----
    if name == "note_add":
        with _conn() as conn:
            cur = conn.execute(
                "INSERT INTO notes (title, body) VALUES (?, ?)",
                (arguments["title"], arguments.get("body", "")),
            )
        return f"OK: note id={cur.lastrowid}"

    if name == "note_search":
        q = f"%{arguments['query']}%"
        with _conn() as conn:
            rows = conn.execute(
                "SELECT id, title, ts FROM notes WHERE title LIKE ? OR body LIKE ? ORDER BY id DESC",
                (q, q),
            ).fetchall()
        if not rows:
            return "(无匹配笔记)"
        return "\n".join(f"[{r['id']}] {r['title']}  ({r['ts']})" for r in rows)

    if name == "note_list":
        limit = arguments.get("limit", 20)
        with _conn() as conn:
            rows = conn.execute(
                "SELECT id, title, ts FROM notes ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        if not rows:
            return "(暂无笔记)"
        return "\n".join(f"[{r['id']}] {r['title']}  ({r['ts']})" for r in rows)

    if name == "note_delete":
        with _conn() as conn:
            conn.execute("DELETE FROM notes WHERE id=?", (arguments["id"],))
        return "OK"

    # ---- tasks ----
    if name == "task_create":
        priority = arguments.get("priority", "medium")
        if priority not in ("low", "medium", "high"):
            return f"Error: 非法 priority '{priority}'，允许: low/medium/high"
        with _conn() as conn:
            cur = conn.execute(
                "INSERT INTO tasks (title, priority) VALUES (?, ?)",
                (arguments["title"], priority),
            )
        return f"OK: task id={cur.lastrowid}"

    if name == "task_list":
        status = arguments.get("status", "all")
        with _conn() as conn:
            if status == "all":
                rows = conn.execute(
                    "SELECT id, title, status, priority FROM tasks ORDER BY id"
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT id, title, status, priority FROM tasks WHERE status=? ORDER BY id",
                    (status,),
                ).fetchall()
        if not rows:
            return "(暂无任务)"
        return "\n".join(
            f"[{r['id']}] [{r['priority']:6}] [{r['status']:5}] {r['title']}"
            for r in rows
        )

    if name == "task_update":
        with _conn() as conn:
            conn.execute(
                "UPDATE tasks SET status=? WHERE id=?",
                (arguments["status"], arguments["id"]),
            )
        return "OK"

    if name == "task_delete":
        with _conn() as conn:
            conn.execute("DELETE FROM tasks WHERE id=?", (arguments["id"],))
        return "OK"

    raise ValueError(f"Unknown tool: {name}")


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------

async def _amain() -> None:
    _init_db()
    print(f"zkali-mcp started  db={_DB_PATH}", file=sys.stderr)
    async with stdio_server() as (r, w):
        await app.run(r, w, app.create_initialization_options())


def main() -> int:
    global _DB_PATH
    args = parse_args()
    _DB_PATH = Path(args.db).resolve()
    asyncio.run(_amain())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
