# db.md — 数据库规范（含工具注册表）

## 1. 存储边界

- 唯一持久化后端：sqlite3
- 工具目录元数据统一落到 `tools` 表
- JSON 结构字段统一存 `TEXT`（JSON 字符串）

---

## 2. tools 表标准字段

```sql
CREATE TABLE IF NOT EXISTS tools (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  name           TEXT    NOT NULL UNIQUE,
  version        TEXT    NOT NULL,
  describe       TEXT    NOT NULL,
  classification TEXT    NOT NULL,
  enable         INTEGER NOT NULL DEFAULT 1 CHECK (enable IN (0,1)),
  input_schema   TEXT    NOT NULL,
  output_schema  TEXT    NOT NULL,
  tags           TEXT    NOT NULL,
  content        TEXT    NOT NULL,
  created_at     TEXT    NOT NULL DEFAULT (datetime('now')),
  updated_at     TEXT    NOT NULL DEFAULT (datetime('now'))
);
```

字段说明：

- `id`：主键
- `name`：工具名，遵循 `scope/target` 或 `todo`
- `version`：工具版本（推荐 semver）
- `describe`：详细描述（语义检索源）
- `classification`：分类字段
- `enable`：是否启用，`1` 启用，`0` 禁用
- `input_schema`：输入参数 JSON Schema
- `output_schema`：输出参数 JSON Schema
- `tags`：JSON 数组字符串
- `content`：JSON 详情，详情接口直接返回该字段

---

## 3. 索引建议

```sql
CREATE INDEX IF NOT EXISTS idx_tools_classification ON tools (classification);
CREATE INDEX IF NOT EXISTS idx_tools_enable ON tools (enable);
CREATE INDEX IF NOT EXISTS idx_tools_name ON tools (name);
```

> `describe` 的语义检索可先用 `LIKE`，后续如需高性能可接 FTS5 虚表。

---

## 4. 入库标准化

### 4.1 tags

- 若输入是逗号分隔字符串：`"mcp,search,docs"`
- 入库前标准化为 JSON：`["mcp","search","docs"]`

### 4.2 content

`content` 至少包含：

```json
{
  "summary": "工具概要",
  "usage": "调用方式",
  "examples": [{"input": {}, "output": {}}],
  "returns": {"ok": "...", "error": "..."}
}
```

---

## 5. 查询范式

### 5.1 通过 name 获取详情

```sql
SELECT id, name, version, classification, enable, content
FROM tools
WHERE name = ?;
```

### 5.2 通过 describe 语义扫描（基础版）

```sql
SELECT id, name, version, classification, enable
FROM tools
WHERE enable = 1
  AND describe LIKE ?
ORDER BY id DESC
LIMIT ? OFFSET ?;
```

### 5.3 通过 tags 过滤

> 若未启用 JSON1 函数，可先用 `LIKE` 粗过滤；启用后推荐 JSON 精确匹配。

```sql
SELECT id, name, version, classification, enable
FROM tools
WHERE enable = 1
  AND tags LIKE ?
ORDER BY id DESC
LIMIT ? OFFSET ?;
```
