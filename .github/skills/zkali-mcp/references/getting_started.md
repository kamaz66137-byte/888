# MCP Server 入门指南

## MCP 协议概念

**MCP（Model Context Protocol）** 是让 AI 模型调用外部工具/服务的标准协议。

核心角色：
- **Server**：提供工具的进程（你要写的部分）
- **Client**：调用工具的 AI（Claude Code、VS Code Copilot）
- **Host**：运行 Client 的应用

三类能力：
| 能力 | 描述 | 本技能覆盖 |
|:--|:--|:--:|
| **Tools** | AI 可调用的函数 | ✅ |
| **Resources** | AI 可读取的数据（文件/DB 记录） | 部分 |
| **Prompts** | 预定义提示模板 | ❌ |

本技能约束：所有示例与产出必须使用 sqlite3 作为唯一储存层。

---

## 安装

```bash
# 基础（stdio 传输）
pip install mcp

# 含 SSE 支持（网络传输）
pip install "mcp[sse]"

# 完整（含调试工具）
pip install "mcp[cli]"
```

验证安装：
```bash
python -c "from mcp.server import Server; print('OK')"
mcp version   # 若安装了 cli extras
```

---

## 首个 MCP Server（5 分钟，sqlite3 持久化）

**步骤 1**：创建 `server.py`

```python
#!/usr/bin/env python3
import asyncio
import sqlite3
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

app = Server("hello-sqlite-server")
DB = Path(__file__).parent / "hello.db"


def init_db() -> None:
    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("CREATE TABLE IF NOT EXISTS kv (k TEXT PRIMARY KEY, v TEXT NOT NULL)")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="kv_put",
            description="写入键值对到 sqlite3",
            inputSchema={
                "type": "object",
                "properties": {
                    "key": {"type": "string"},
                    "value": {"type": "string"}
                },
                "required": ["key", "value"],
            },
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "kv_put":
        with sqlite3.connect(DB) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO kv (k, v) VALUES (?, ?)",
                (arguments["key"], arguments["value"]),
            )
        return [TextContent(type="text", text="OK")]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    init_db()
    async with stdio_server() as (r, w):
        await app.run(r, w, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
```

**步骤 2**：本地调试

```bash
# 方式 A：mcp dev（内置 Inspector UI，推荐）
mcp dev server.py

# 方式 B：MCP Inspector（npx）
npx @modelcontextprotocol/inspector python server.py
```

**步骤 3**：注册到 VS Code Copilot

`.vscode/mcp.json`：
```json
{
  "servers": {
        "hello-sqlite-server": {
      "type": "stdio",
      "command": "python",
      "args": ["${workspaceFolder}/server.py"]
    }
  }
}
```

重启 VS Code 后，Copilot 可自动发现并调用 `kv_put` 工具，数据会落盘到 `hello.db`。

---

## sqlite3 基础集成

```python
import sqlite3
from pathlib import Path

DB = Path(__file__).parent / "app.db"

def init_db():
    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                ts   TEXT DEFAULT (datetime('now'))
            )
        """)

def get_item(item_id: int) -> dict | None:
    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
        return dict(row) if row else None
```

---

## 传输方式选择

| 场景 | 传输 | 包 |
|:--|:--|:--|
| Claude Code / VS Code Copilot 本地 | `stdio` | `mcp.server.stdio` |
| 网络服务（长连接推送） | `sse` | `mcp[sse]` + starlette |
| 网络服务（新版标准） | `streamable_http` | `mcp[sse]` + starlette |
| 开发调试 | `stdio` + `mcp dev` | `mcp[cli]` |
