# 扩展示例

约束说明：本页所有示例都以 sqlite3 为唯一持久化后端，不包含其它数据库实现。

## 示例1：完整 CRUD 任务管理器

```python
#!/usr/bin/env python3
"""任务管理 MCP Server：增删查改 + 状态筛选"""
import asyncio
import sqlite3
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

DB = Path(__file__).parent / "tasks.db"

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init():
    with db() as c:
        c.execute("""
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

app = Server("zkali-tasks")

TOOLS = [
    Tool(name="create_task", description="创建新任务",
         inputSchema={"type":"object","properties":{
             "title":{"type":"string"},
             "priority":{"type":"string","enum":["low","medium","high"]}
         },"required":["title"]}),
    Tool(name="list_tasks", description="列出任务（可按状态筛选）",
         inputSchema={"type":"object","properties":{
             "status":{"type":"string","enum":["todo","doing","done","all"]}
         }}),
    Tool(name="update_status", description="更新任务状态",
         inputSchema={"type":"object","properties":{
             "id":{"type":"integer"},
             "status":{"type":"string","enum":["todo","doing","done"]}
         },"required":["id","status"]}),
    Tool(name="delete_task", description="删除任务",
         inputSchema={"type":"object","properties":{
             "id":{"type":"integer"}
         },"required":["id"]}),
]

@app.list_tools()
async def list_tools(): return TOOLS

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "create_task":
        with db() as c:
            cur = c.execute(
                "INSERT INTO tasks (title, priority) VALUES (?,?)",
                (arguments["title"], arguments.get("priority","medium"))
            )
        return [TextContent(type="text", text=f"OK: task id={cur.lastrowid}")]

    if name == "list_tasks":
        status = arguments.get("status", "all")
        with db() as c:
            if status == "all":
                rows = c.execute("SELECT id,title,status,priority FROM tasks ORDER BY id").fetchall()
            else:
                rows = c.execute(
                    "SELECT id,title,status,priority FROM tasks WHERE status=? ORDER BY id",
                    (status,)
                ).fetchall()
        lines = [f"[{r['id']}] [{r['priority']}] [{r['status']}] {r['title']}" for r in rows]
        return [TextContent(type="text", text="\n".join(lines) or "(空)")]

    if name == "update_status":
        with db() as c:
            c.execute("UPDATE tasks SET status=? WHERE id=?",
                      (arguments["status"], arguments["id"]))
        return [TextContent(type="text", text="OK")]

    if name == "delete_task":
        with db() as c:
            c.execute("DELETE FROM tasks WHERE id=?", (arguments["id"],))
        return [TextContent(type="text", text="OK")]

    raise ValueError(f"Unknown tool: {name}")

async def main():
    init()
    async with stdio_server() as (r, w):
        await app.run(r, w, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 示例2：MCP Resources（暴露数据库表作为资源）

```python
from mcp.types import Resource, TextResourceContents
from mcp.server.models import InitializationOptions
from pydantic import AnyUrl

@app.list_resources()
async def list_resources() -> list[Resource]:
    return [
        Resource(
            uri=AnyUrl("db://tasks/all"),
            name="所有任务",
            description="任务数据库完整内容",
            mimeType="application/json",
        )
    ]

@app.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    import json
    if str(uri) == "db://tasks/all":
        with db() as c:
            rows = c.execute("SELECT * FROM tasks").fetchall()
        return json.dumps([dict(r) for r in rows], ensure_ascii=False, indent=2)
    raise ValueError(f"Unknown resource: {uri}")
```

---

## 示例3：自定义验证层（handler 内部校验）

```python
ALLOWED_PRIORITIES = {"low", "medium", "high"}

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "create_task":
        priority = arguments.get("priority", "medium")
        if priority not in ALLOWED_PRIORITIES:
            return [TextContent(type="text",
                text=f"Error: priority 必须为 {ALLOWED_PRIORITIES}，收到 '{priority}'")]
        # ... 正常逻辑
```

---

## 示例4：多 DB 表 Server（模块化工具注册）

```python
def register_note_tools(app: Server) -> None:
    @app.list_tools()
    async def list_tools():
        return NOTE_TOOLS + TASK_TOOLS

    @app.call_tool()
    async def call_tool(name: str, arguments: dict):
        if name.startswith("note_"):
            return await handle_note(name, arguments)
        if name.startswith("task_"):
            return await handle_task(name, arguments)
        raise ValueError(f"Unknown: {name}")
```

---

## 示例5：.vscode/mcp.json 多 Server 配置

```json
{
  "servers": {
    "zkali-tasks": {
      "type": "stdio",
      "command": "python",
      "args": ["${workspaceFolder}/.github/skills/zkali-mcp/scripts/main.py"]
    },
    "zkali-notes": {
      "type": "stdio",
      "command": "python",
      "args": ["${workspaceFolder}/tools/notes-server.py"]
    },
    "remote-api": {
      "type": "sse",
      "url": "http://localhost:8000/sse"
    }
  }
}
```
