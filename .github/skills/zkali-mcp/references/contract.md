# contract.md — 工具契约（输入 / 输出 / 错误处理）

## 1. 输入参数标准（inputSchema）

每个 Tool 的 `inputSchema` **必须**包含：

```python
{
    "type": "object",
    "x-tags": [module, action, ...keywords],   # 见 ai-protocol.md
    "properties": {
        "field": {
            "type": "...",
            "description": "字段说明（中文，必填字段注明'必填'）",
            # 约束：minLength / minimum / enum / format 等
        },
    },
    "required": ["必填字段列表"],
    "additionalProperties": False,             # 严格模式，拒绝未声明字段
}
```

### 常用字段约束速查

```python
# id 字段
"id": {"type": "integer", "minimum": 1, "description": "记录 id（必填）"}

# 非空字符串
"title": {"type": "string", "minLength": 1, "description": "标题（必填）"}

# 枚举
"priority": {"type": "string", "enum": ["low", "medium", "high"]}
"status":   {"type": "string", "enum": ["todo", "doing", "done"]}

# 可空字段（update 时清空传 null）
"due_date": {"type": ["string", "null"], "description": "传 null 可清空"}

# 分页
"limit":  {"type": "integer", "minimum": 1, "maximum": 100, "description": "每页数量（默认 20）"}
"offset": {"type": "integer", "minimum": 0, "description": "跳过条数（默认 0）"}

# 全文搜索关键词
"query": {"type": "string", "minLength": 1, "description": "搜索关键词（必填）"}
```

---

## 2. 输出格式标准（Output Contract）

所有工具输出为**纯文本字符串**，格式严格固定：

| 操作类型 | 成功输出 | 失败/空输出 |
|---------|----------|------------|
| `add` | `OK id={N}` | — |
| `update` / `done` | `OK updated` | `ERR not_found` |
| `delete` | `OK deleted` | `ERR not_found` |
| `list` / `search` | 每行一条（见格式） | `(empty)` |
| `get`（详情） | 每行 `field: value` | `ERR not_found` |
| `stats` | 每行 `key: N` | — |
| 输入校验失败 | — | `ERR {message}` |

### list / search 行格式

```
[{id}] {主字段} ({created_at})
```

示例（notes）：
```
[3] 我的笔记标题 (2026-05-03 12:00:00)
[2] 另一条笔记 (2026-05-03 11:00:00)
[1] 最早的笔记 (2026-05-03 10:00:00)
```

示例（tasks，含状态和优先级）：
```
[2] [todo] [high] 修复 BUG | due=2026-05-10
[1] [done] [medium] 写文档 | due=-
```

### get 详情格式

```
id: {N}
title: {value}
body: {value}
created_at: {value}
updated_at: {value}
```

### stats 格式

```
total: 10
todo: 4
doing: 3
done: 3
```

---

## 3. 错误处理规范

### 3.1 _contract.py helpers（禁止硬编码字符串）

所有工具输出**必须**使用 `_contract.py` 中的 helpers，不得直接拼接字符串：

```python
from ._contract import (
    ok_id, ok_updated, ok_deleted,
    err_not_found, err_validation, list_empty,
)

# 正确
return ok_id(cursor.lastrowid)      # → "OK id=3"
return ok_updated()                  # → "OK updated"
return ok_deleted()                  # → "OK deleted"
return err_not_found()               # → "ERR not_found"
return err_validation("至少提供 title 或 body")  # → "ERR 至少提供 title 或 body"
return list_empty()                  # → "(empty)"

# 禁止
return "OK: id=3"                    # ❌ 格式不符合契约
return "not found"                   # ❌ 未使用 helper
```

### 3.2 错误处理层级

| 层级 | 处理位置 | 方式 |
|------|----------|------|
| 1. 输入校验 | MCP 框架自动（inputSchema） | 协议级错误，无需手动处理 |
| 2. 业务校验 | tool 实现中 | `return err_validation("说明")` |
| 3. 记录不存在 | tool 实现中 | `return err_not_found()` |
| 4. 未知工具名 | dispatcher.py | `raise ValueError(f"Unknown tool: {name}")` |
| 5. DB 异常 | 不捕获，向上传播 | runner 层记录日志后返回协议错误 |

### 3.3 rowcount 和 fetchone 检查（必做）

```python
# delete / update 后必须检查 rowcount
cursor = conn.execute("DELETE FROM notes WHERE id = ?", (id,))
if cursor.rowcount == 0:
    return err_not_found()
return ok_deleted()

# get 后必须检查 None
row = conn.execute("SELECT ... WHERE id = ?", (id,)).fetchone()
if row is None:
    return err_not_found()
```

### 3.4 dispatcher 末尾兜底

```python
def dispatch_tool(name: str, arguments: dict, db_path: Path) -> str:
    if name not in ALLOWED_TOOLS:
        raise ValueError(f"Unknown tool: {name}")
    # ... 各模块调用链 ...
    raise ValueError(f"Unhandled tool: {name}")   # 调用链末尾兜底，不能用 return
```

---

## 4. 工具注册元数据契约（tools）

用于描述“工具目录”中的工具定义，支持按名称、语义和标签发现。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | integer | 是 | 主键，自增 |
| `name` | string | 是 | 工具名，遵循 naming.md 的 `scope/target` 规则 |
| `version` | string | 是 | 语义版本，如 `1.0.0` |
| `describe` | string | 是 | 工具详细说明（用于语义发现） |
| `classification` | string | 是 | 分类（如 `crawl`/`search`/`todo`/`ops`） |
| `enable` | boolean/integer | 是 | 是否启用（1 启用，0 禁用） |
| `input_schema` | json string | 是 | 输入参数 JSON Schema |
| `output_schema` | json string | 是 | 输出参数 JSON Schema |
| `tags` | json string | 是 | 标签数组，示例 `["mcp","search","docs"]` |
| `content` | json string | 是 | 工具完整详情与返回模板，详情接口直接返回该字段 |

### 4.1 tags 存储约束

- 存储形态必须是 JSON 数组字符串，不存裸逗号字符串。
- 入参可接受逗号分隔文本，落库前必须标准化为 JSON 数组。

示例：

```text
输入: "mcp,search,docs"
落库: ["mcp","search","docs"]
```

### 4.2 content 约束

`content` 建议至少包含：

```json
{
    "summary": "一句话功能描述",
    "usage": "如何调用",
    "examples": [{"input": {}, "output": {}}],
    "returns": {"ok": "...", "error": "..."}
}
```

---

## 5. 工具发现与读取契约

### 5.1 必备读取能力

- 按 `name` 精确获取工具详情（详情主体返回 `content`）
- 按 `describe` 语义检索发现工具
- 按 `tags` 标签过滤发现工具

### 5.2 操作层最小集合

- `add/tool`
- `update/tool`
- `delete/tool`
- `list/tool`
- `get/tool`
- `discover/tool`

`discover/tool` 负责统一语义检索和标签过滤，推荐参数：

```json
{
    "query": "string, 可选，describe 语义检索词",
    "tags": ["string"],
    "enable": true,
    "classification": "string",
    "limit": 20,
    "offset": 0
}
```