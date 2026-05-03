# mcp Python SDK API 参考

## 存储层硬约束

- 本技能所有 MCP Server 实现必须使用 sqlite3 作为唯一储存层。
- 不提供 MySQL、PostgreSQL、Redis、MongoDB 的实现、迁移或适配说明。
- 若需求指定非 sqlite3，请先回退需求并改为 sqlite3 方案再继续实现。

## Server 核心类

### `Server(name: str)`

```python
from mcp.server import Server
app = Server("my-server")
```

| 方法装饰器 | 用途 | 签名 |
|:--|:--|:--|
| `@app.list_tools()` | 声明工具列表 | `async def() -> list[Tool]` |
| `@app.call_tool()` | 处理工具调用 | `async def(name: str, arguments: dict) -> list[Content]` |
| `@app.list_resources()` | 声明资源列表 | `async def() -> list[Resource]` |
| `@app.read_resource()` | 读取资源内容 | `async def(uri: AnyUrl) -> str \| bytes` |
| `@app.list_prompts()` | 声明提示列表 | `async def() -> list[Prompt]` |
| `@app.get_prompt()` | 获取提示内容 | `async def(name: str, arguments: dict) -> GetPromptResult` |

---

## Tool 类型

```python
from mcp.types import Tool

Tool(
    name="tool_name",           # 工具名（snake_case 推荐）
    description="工具描述",      # 必须，AI 用于决策是否调用
    inputSchema={               # JSON Schema 对象
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "参数说明",
                "minLength": 1,
            },
            "param2": {
                "type": "integer",
                "minimum": 0,
                "maximum": 100,
            },
            "param3": {
                "type": "string",
                "enum": ["a", "b", "c"],    # 枚举约束
            },
            "param4": {
                "type": "array",
                "items": {"type": "string"},
            },
        },
        "required": ["param1"],             # 必填字段列表
        "additionalProperties": False,       # 禁止额外字段
    },
)
```

---

## 返回类型

```python
from mcp.types import TextContent, ImageContent, EmbeddedResource

# 文本（最常用）
TextContent(type="text", text="返回内容")

# 图片（base64）
ImageContent(type="image", data="base64...", mimeType="image/png")

# 嵌入资源
EmbeddedResource(type="resource", resource=TextResourceContents(...))
```

`call_tool` 必须返回 `list[TextContent | ImageContent | EmbeddedResource]`。

---

## 传输层

### stdio（本地，推荐）

```python
from mcp.server.stdio import stdio_server

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )

asyncio.run(main())
```

### SSE（网络，需 starlette）

```python
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route, Mount
import uvicorn

sse = SseServerTransport("/messages/")

async def handle_sse(request):
    async with sse.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await app.run(streams[0], streams[1], app.create_initialization_options())

starlette_app = Starlette(
    routes=[
        Route("/sse", endpoint=handle_sse),
        Mount("/messages/", app=sse.handle_post_message),
    ]
)

if __name__ == "__main__":
    uvicorn.run(starlette_app, host="0.0.0.0", port=8000)
```

SSE 对应的 mcp.json 注册：
```json
{
  "servers": {
    "my-sse-server": {
      "type": "sse",
      "url": "http://localhost:8000/sse"
    }
  }
}
```

---

## sqlite3 参数化查询速查

说明：以下查询模式为本技能唯一推荐与支持的持久化实现。

| 操作 | 代码 |
|:--|:--|
| 插入 | `conn.execute("INSERT INTO t (a,b) VALUES (?,?)", (a, b))` |
| 查询单行 | `conn.execute("SELECT * FROM t WHERE id=?", (id,)).fetchone()` |
| 查询多行 | `conn.execute("SELECT * FROM t WHERE a=?", (val,)).fetchall()` |
| 更新 | `conn.execute("UPDATE t SET a=? WHERE id=?", (a, id))` |
| 删除 | `conn.execute("DELETE FROM t WHERE id=?", (id,))` |
| LIKE 搜索 | `conn.execute("SELECT * FROM t WHERE col LIKE ?", (f"%{q}%",))` |
| lastrowid | `cur = conn.execute("INSERT ..."); cur.lastrowid` |

---

## asyncio.to_thread（阻塞 I/O 包装）

sqlite3 操作是同步的，在 async handler 中应包装：

```python
import asyncio

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    result = await asyncio.to_thread(_sync_db_query, arguments["id"])
    return [TextContent(type="text", text=str(result))]

def _sync_db_query(item_id: int) -> dict | None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM items WHERE id=?", (item_id,)).fetchone()
        return dict(row) if row else None
```

---

## 非支持范围

- 不提供 ORM（如 SQLAlchemy）作为默认路径。
- 不提供跨数据库抽象层（repository adapter）以切换到其它数据库。
- 不提供分布式数据库与外部缓存替代 sqlite3 的方案。
