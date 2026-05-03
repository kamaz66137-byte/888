# naming.md — 命名规范

## 1. 工具命名

**格式**：`{module}_{action}`

```
module  = 领域名词（单数小写英文，如 note / task / user / doc / file）
action  ∈ 标准动词集合（见下表）
```

| action | 语义 | 示例 |
|--------|------|------|
| `add` | 新增记录 | `note_add` `task_add` |
| `get` | 按 id 获取详情 | `note_get` `task_get` |
| `list` | 分页列出 | `note_list` `task_list` |
| `search` | 关键词检索 | `note_search` `doc_search` |
| `update` | 更新字段 | `note_update` `task_update` |
| `delete` | 删除记录 | `note_delete` `task_delete` |
| `stats` | 聚合统计 | `task_stats` `user_stats` |
| 领域动词 | 特殊业务操作 | `task_done` `task_assign` |

**系统保留前缀**：`tool_*`（如 `tool_help`）

**禁止**：

```
❌ addNote       — 驼峰
❌ create_note   — create 不在标准动词集
❌ notes_add     — module 应单数
❌ note          — 缺少 action
```

---

## 2. Python 标识符命名

| 类型 | 规则 | 示例 |
|------|------|------|
| 包 / 模块 | 小写下划线 | `zkmcp`, `note.py` |
| 函数 / 方法 | 小写下划线 | `dispatch_note_tool()` |
| 常量 | 大写下划线 | `HELP_MAP`, `TOOL_ORDER` |
| 内部模块文件 | 下划线前缀 | `_contract.py`, `_schemas.py` |
| 类（极少用） | 大驼峰 | `NoteRepository` |

下划线前缀文件（`_contract.py`、`_schemas.py`）是**包内部文件**，不对外暴露，不在 `__init__.py` 中导出。

---

## 3. 数据库命名

| 类型 | 规则 | 示例 |
|------|------|------|
| 表名 | 小写复数 | `notes`, `tasks`, `users` |
| 列名 | 小写下划线 | `created_at`, `due_date` |
| 主键 | `id INTEGER PRIMARY KEY AUTOINCREMENT` | 固定格式 |
| 时间戳列 | `created_at` / `updated_at` | `DEFAULT (datetime('now'))` |
| 外键列 | `{ref_singular}_id` | `user_id`, `note_id` |

---

## 4. 文件命名

| 位置 | 命名规则 | 示例 |
|------|----------|------|
| `tool/{module}.py` | module 单数小写 | `note.py`, `task.py` |
| `tool/_*.py` | 下划线前缀=内部 | `_contract.py`, `_schemas.py` |
| `db/connection.py` | 固定名称 | — |
| `db/schema.py` | 固定名称 | — |
| `.db` 文件 | `{project-name}.db` | `zkali.db` |

---

## 5. dispatch 函数命名

每个模块文件必须暴露固定命名的分发函数：

```python
def dispatch_{module}_tool(name: str, arguments: dict, db_path: Path) -> str | None:
    ...
```

示例：`dispatch_note_tool`, `dispatch_task_tool`, `dispatch_user_tool`

---

## 6. 工具注册名标准（面向工具市场/自动发现）

本节用于约束数据库中 `tools.name` 的命名，不替代 `module_action` 的 Python 函数命名。

### 6.1 基础格式

```text
{scope}/{target}
```

- `scope`：功能域或动作域（小写英文）
- `target`：对象名（小写英文，支持 `-` 和 `_`）

### 6.2 功能域命名

| 前缀 | 语义 | 示例 |
|------|------|------|
| `crawl/xxx` | 抓取站点或数据源 | `crawl/github` `crawl/arxiv` |
| `search/xxx` | 搜索指定域内容 | `search/issues` `search/docs` |
| `todo` | 代办事项工具集合根能力 | `todo` |

> `todo` 允许单段名称，表示系统内置代办能力入口；其子能力可用 `todo/add`、`todo/list`。

### 6.3 操作层命名

| 前缀 | 语义 | 示例 |
|------|------|------|
| `add/xxx` | 添加 xxx | `add/tool` `add/task` |
| `update/xxx` | 更新 xxx | `update/tool` |
| `delete/xxx` | 删除 xxx | `delete/tool` |
| `list/xxx` | 列出 xxx | `list/tool` |
| `get/xxx` | 获取 xxx 详情 | `get/tool` |
| `discover/xxx` | 发现/检索 xxx | `discover/tool` |

### 6.4 校验建议

```text
允许：^[a-z][a-z0-9-]*(/[a-z0-9][a-z0-9_-]*)?$
特例：todo
```

### 6.5 禁止项

- `Crawl/Github`（禁止大写）
- `search//docs`（禁止空段）
- `add tool`（禁止空格）
- `tool.add`（禁止点号分隔）