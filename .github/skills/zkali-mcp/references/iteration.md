# iteration.md — 迭代新模块方案 + 代码注释规范

## 1. 新增模块：标准四步法

### 步骤 1：新建 `tool/{module}.py`

```python
"""zkmcp.tool.{module} — {module} 模块工具实现（{module}_add/get/...）。"""
from __future__ import annotations

from pathlib import Path

from ..db import open_conn
from ._contract import (
    err_not_found, err_validation, list_empty,
    ok_deleted, ok_id, ok_updated,
)


def dispatch_{module}_tool(name: str, arguments: dict, db_path: Path) -> str | None:
    if name == "{module}_add":
        title = str(arguments["title"]).strip()
        with open_conn(db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO {module}s (title) VALUES (?)", (title,)
            )
        return ok_id(cursor.lastrowid)

    if name == "{module}_get":
        target_id = int(arguments["id"])
        with open_conn(db_path) as conn:
            row = conn.execute(
                "SELECT id, title, created_at FROM {module}s WHERE id = ?",
                (target_id,),
            ).fetchone()
        if row is None:
            return err_not_found()
        return f"id: {row['id']}\ntitle: {row['title']}\ncreated_at: {row['created_at']}"

    if name == "{module}_delete":
        target_id = int(arguments["id"])
        with open_conn(db_path) as conn:
            cursor = conn.execute("DELETE FROM {module}s WHERE id = ?", (target_id,))
        if cursor.rowcount == 0:
            return err_not_found()
        return ok_deleted()

    # ... 其他工具

    return None  # 不处理的工具名返回 None，交给 dispatcher 下一个模块
```

### 步骤 2：在 `_schemas.py` 中注册

在 `HELP_MAP` 中追加（按模块分组）：

```python
    # ── {module} module ──────────────────────────────────────────────────────
    "{module}_add": (
        "{module}_add(title, ...) -> "
        "新增...，返回 'OK id={N}'。title 必填。"
    ),
    "{module}_get": (
        "{module}_get(id) -> "
        "返回详情，每行 'field: value'；不存在返回 'ERR not_found'。"
    ),
```

在 `TOOL_ORDER` 中追加（按模块分组）：

```python
    # ── {module} module
    "{module}_add",
    "{module}_get",
    "{module}_delete",
```

在 `build_tools()` 中追加 Tool 定义：

```python
        # ── {module} module ──────────────────────────────────────────────────
        Tool(
            name="{module}_add",
            description=(
                "新增一条...并持久化到 sqlite3。"
                "【触发词】...中文触发词...，...英文触发词...。"
                "【返回】OK id={N}。"
            ),
            inputSchema={
                "type": "object",
                "x-tags": ["{module}", "add", "create"],
                "properties": {
                    "title": {"type": "string", "minLength": 1, "description": "标题（必填）"},
                },
                "required": ["title"],
                "additionalProperties": False,
            },
        ),
```

### 步骤 3：在 `dispatcher.py` 中注册

```python
from .{module} import dispatch_{module}_tool   # 追加 import

def dispatch_tool(name: str, arguments: dict, db_path: Path) -> str:
    if name not in ALLOWED_TOOLS:
        raise ValueError(f"Unknown tool: {name}")

    if name == "tool_help":
        return handle_help(arguments)

    note_result = dispatch_note_tool(name, arguments, db_path)
    if note_result is not None:
        return note_result

    task_result = dispatch_task_tool(name, arguments, db_path)
    if task_result is not None:
        return task_result

    # ── 新模块追加在此 ─────────────────────────────────────────────────────
    {module}_result = dispatch_{module}_tool(name, arguments, db_path)
    if {module}_result is not None:
        return {module}_result

    raise ValueError(f"Unhandled tool: {name}")
```

### 步骤 4：在 `db/schema.py` 中追加表

```python
def init_db(db_path: Path) -> None:
    with open_conn(db_path) as conn:
        # ... 已有表 ...

        # ── {module}s 表 ────────────────────────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS {module}s (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      TEXT    NOT NULL,
                created_at TEXT    NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT    NOT NULL DEFAULT (datetime('now'))
            )
        """)
```

---

## 2. 验证新模块（必做）

```powershell
# 1. 语法检查
.\.venv\Scripts\python.exe -m py_compile src\zkali-mcp\zkmcp\tool\{module}.py

# 2. 自检（在 runner.py 的 run_self_test 中添加新模块测试后运行）
.\.venv\Scripts\python.exe src\zkali-mcp\main.py --self-test

# 3. 冒烟测试（快速验证 add + get + delete 链路）
.\.venv\Scripts\python.exe -c "
from pathlib import Path
from zkmcp.db import init_db
from zkmcp.tool import dispatch_tool
db = Path('test.db')
init_db(db)
r = dispatch_tool('{module}_add', {'title': 'smoke-test'}, db)
print('add:', r)
assert r.startswith('OK id='), r
"
```

---

## 3. 代码注释规范

### 3.1 文件头注释（每个 .py 文件必须有）

```python
"""zkmcp.tool.note — note 模块工具实现（note_add/get/update/list/search/delete）。"""
from __future__ import annotations
```

**格式**：`"""{package}.{module} — {一句话功能描述}。"""`

### 3.2 函数 docstring（仅在需要时添加）

**需要 docstring 的情况**：
- 公开 API 函数（其他模块会调用）
- 逻辑复杂、参数含义不明

```python
def open_conn(db_path: Path):
    """返回开启 WAL 模式和外键约束的 sqlite3 连接（上下文管理器）。"""
```

**不需要 docstring 的情况**（命名自解释）：

```python
def ok_id(n: int) -> str:        return f"OK id={n}"      # 无需
def err_not_found() -> str:      return "ERR not_found"   # 无需
```

### 3.3 行内注释（仅用于非显而易见的逻辑）

```python
# WAL 模式提升写入并发性能（Read 不阻塞 Write）
conn.execute("PRAGMA journal_mode=WAL")

# 每次连接都必须显式开启外键约束（sqlite3 默认关闭）
conn.execute("PRAGMA foreign_keys=ON")

# LIKE 两侧加 % 实现全文包含匹配
like = f"%{query}%"
```

**禁止**：
```python
# ❌ 废话注释
i = i + 1  # i 加 1

# ❌ 注释掉的代码（用 git 管理历史）
# result = old_function(x)
```

### 3.4 模块分组分隔符

在多模块汇聚文件（`_schemas.py`、`dispatcher.py`）中，用分隔线标识模块边界：

```python
# ── system ──────────────────────────────────────────────────────────────────
Tool(name="tool_help", ...)

# ── note module ─────────────────────────────────────────────────────────────
Tool(name="note_add", ...)
Tool(name="note_get", ...)

# ── task module ─────────────────────────────────────────────────────────────
Tool(name="task_add", ...)
```

---

## 4. run_self_test 维护规范

每次新增模块，必须在 `runner.py` 的 `run_self_test()` 中追加验证：

```python
def run_self_test(db_path: Path) -> int:
    init_db(db_path)

    # ── system ────────────────────────────────────────────────────────────
    out = dispatch_tool("tool_help", {}, db_path)
    assert "note_add" in out, "help 缺少 note_add"
    assert "{module}_add" in out, "help 缺少 {module}_add"   # 新模块加这一行

    # ── note ──────────────────────────────────────────────────────────────
    r = dispatch_tool("note_add", {"title": "self-test"}, db_path)
    assert r.startswith("OK id="), f"note_add 失败: {r}"

    # ── {module} ─────────────────────────────────────────────────────────
    r = dispatch_tool("{module}_add", {"title": "self-test"}, db_path)
    assert r.startswith("OK id="), f"{module}_add 失败: {r}"

    print("SELF-TEST OK")
    return 0
```