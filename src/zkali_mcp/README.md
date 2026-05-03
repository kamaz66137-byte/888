# zkali_mcp 使用说明

这是一个基于 Python + sqlite3 的 MCP Server，当前支持：

- 笔记管理
- 任务管理
- 项目管理（含描述、位置、环境、语言、三方库）
- 项目进度管理
- 项目执行步骤（todo）
- 知识库（公共知识 + 项目知识）
- 词典（公共词典 + 项目词典）
- 提示词模板（公共模板 + 项目模板 + 渲染）
- 项目隔离记忆
- 代码片段（公共片段 + 项目片段）
- 项目环境变量
- 事件日志
- 全局统计与过期清理
- 全局跨模块搜索
- 批量操作（笔记、任务）
- 项目数据导出 / 导入
- 标签管理（列出、重命名、合并）
- 数据库备份
- 热点事件查询（Google News / HN）

## 项目结构

```
src/zkali_mcp/
├── main.py              # 入口
├── runner.py            # 启动辅助
├── requirements.txt
├── adapters/            # 适配层（工具路由、Schema 契约）
│   ├── dispatcher.py    # O(1) 工具路由分发
│   ├── _contract.py
│   ├── schemas/         # 各模块 JSON Schema
│   └── tools/           # 各模块工具实现
├── domains/             # 业务域服务层
│   ├── docs/
│   ├── elog/
│   ├── envvar/
│   ├── kv/
│   ├── memory/
│   ├── note/
│   ├── project/
│   ├── prompt/
│   ├── snippet/
│   └── task/
├── db/                  # 数据库连接与 Schema 初始化
│   ├── connection.py
│   └── schema.py
├── protocol/            # 统一响应格式
│   └── response.py
└── server/              # HTTP 服务入口
    ├── app.py
    └── selftest.py
```

## 启动方式

```powershell
# 安装依赖
.\.venv\Scripts\python.exe -m pip install -r src\zkali_mcp\requirements.txt

# 本地自检（不启动 MCP）
.\.venv\Scripts\python.exe src\zkali_mcp\main.py --self-test

# 启动 MCP Server（stdio）
.\.venv\Scripts\python.exe src\zkali_mcp\main.py

# 启动 MCP Server（Streamable HTTP）
.\.venv\Scripts\python.exe src\zkali_mcp\main.py --transport streamable-http --host 127.0.0.1 --port 8000

# 启动 MCP Server（SSE）
.\.venv\Scripts\python.exe src\zkali_mcp\main.py --transport sse --host 127.0.0.1 --port 8000
```

默认数据库文件：`src/zkali_mcp/db/zkali.db`

HTTP 端点说明：
- `--transport streamable-http`：`/mcp`
- `--transport sse`：`/sse`（建立 SSE）+ `/messages`（POST 消息）

## 工具总览

你也可以直接在 MCP 里调用 `tool_help` 获取同样说明。

| 工具名 | 参数 | 作用 |
|:--|:--|:--|
| `tool_help` | `name?` | 查看工具说明（不传返回全部） |
| `note_add` | `name`, `body?` | 新增笔记 |
| `note_get` | `id` | 查看笔记详情 |
| `note_update` | `id`, `name?`, `body?` | 更新笔记 |
| `note_list` | `limit?`, `offset?` | 分页列出笔记 |
| `note_search` | `query`, `limit?`, `offset?` | 搜索笔记 |
| `note_delete` | `id` | 删除笔记 |
| `task_add` | `name`, `description?`, `priority?`, `due_date?` | 新增任务 |
| `task_list` | `status?`, `priority?`, `limit?`, `offset?` | 分页筛选任务 |
| `task_update` | `id`, `name?`, `description?`, `status?`, `priority?`, `due_date?` | 更新任务 |
| `task_done` | `id` | 标记任务完成 |
| `task_delete` | `id` | 删除任务 |
| `task_stats` | 无 | 任务统计 |
| `add/project` | `id`, `name`, `describe?`, `location?`, `environment?`, `languages?`, `libraries?`, `status?`, `owner?` | 新增项目 |
| `update/project` | `id`, `name?`, `describe?`, `location?`, `environment?`, `languages?`, `libraries?`, `status?`, `owner?` | 更新项目 |
| `list/project` | `status?`, `limit?`, `offset?` | 列出项目 |
| `get/project` | `id` | 项目详情（含进度与 todo 汇总） |
| `delete/project` | `id` | 删除项目 |
| `add/progress` | `project_id`, `name`, `feature?`, `context?`, `status?`, `priority?`, `progress?`, `milestone?` | 新增项目进度 |
| `update/progress` | `project_id`, `task_id`, `name?`, `feature?`, `context?`, `status?`, `priority?`, `progress?`, `milestone?` | 更新项目进度 |
| `list/progress` | `project_id`, `status?`, `limit?`, `offset?` | 列出项目进度 |
| `stats/progress` | `project_id` | 项目进度统计 |
| `add/todo` | `project_id`, `name`, `feature?`, `context?`, `step_order?`, `status?` | 新增项目执行步骤 |
| `update/todo` | `project_id`, `id`, `name?`, `feature?`, `context?`, `step_order?`, `status?` | 更新项目执行步骤 |
| `done/todo` | `project_id`, `id` | 标记执行步骤完成 |
| `list/todo` | `project_id`, `status?`, `limit?`, `offset?` | 列出项目执行步骤 |
| `delete/todo` | `project_id`, `id` | 删除项目执行步骤 |
| `add/docs` | `name`, `content?`, `tags?`, `project_id?` | 新增知识文档（不传 `project_id` 即公共知识） |
| `get/docs` | `id` | 查看知识文档详情 |
| `list/docs` | `scope?`, `project_id?`, `query?`, `limit?`, `offset?` | 列出知识文档 |
| `search/docs` | `query`, `scope?`, `project_id?`, `limit?`, `offset?` | 搜索知识文档 |
| `update/docs` | `id`, `name?`, `content?`, `tags?`, `project_id?` | 更新知识文档（可切换公共/项目） |
| `delete/docs` | `id` | 删除知识文档 |
| `add/dict` | `name`, `value?`, `tags?`, `project_id?` | 新增词典项（不传 `project_id` 即公共词典） |
| `get/dict` | `id` | 查看词典项详情 |
| `get/dict/by-name` | `name`, `scope?`, `project_id?` | 按名称读取词典项（支持 auto/public/project） |
| `list/dict` | `scope?`, `project_id?`, `query?`, `limit?`, `offset?` | 列出词典项 |
| `update/dict` | `id`, `name?`, `value?`, `tags?`, `project_id?` | 更新词典项（可切换公共/项目） |
| `delete/dict` | `id` | 删除词典项 |
| `add/prompt` | `name`, `content?`, `tags?`, `project_id?` | 新增提示词模板（不传 `project_id` 即公共模板） |
| `get/prompt` | `id` | 查看提示词模板详情 |
| `get/prompt/by-name` | `name`, `scope?`, `project_id?` | 按名称读取提示词模板（支持 auto/public/project） |
| `list/prompt` | `scope?`, `project_id?`, `query?`, `limit?`, `offset?` | 列出提示词模板 |
| `update/prompt` | `id`, `name?`, `content?`, `tags?`, `project_id?` | 更新提示词模板（可切换公共/项目） |
| `render/prompt` | `id`, `variables?`, `mode?` | 渲染提示词模板（`strict`/`loose`） |
| `delete/prompt` | `id` | 删除提示词模板 |
| `add/memory` | `project_id`, `key`, `value`, `scope?`, `namespace?`, `ttl_seconds?` | 写入项目记忆 |
| `get/memory` | `project_id`, `key`, `scope?`, `namespace?` | 获取单条项目记忆 |
| `list/memory` | `project_id`, `scope?`, `namespace?`, `limit?`, `offset?` | 列出项目记忆 |
| `update/memory` | `project_id`, `key`, `value`, `scope?`, `namespace?`, `ttl_seconds?` | 更新项目记忆 |
| `delete/memory` | `project_id`, `key`, `scope?`, `namespace?` | 删除项目记忆 |
| `clear/memory` | `project_id`, `scope?` | 清理项目记忆（默认 session） |
| `add/snippet` | `name`, `language?`, `content?`, `tags?`, `project_id?` | 新增代码片段（不传 `project_id` 即公共片段） |
| `get/snippet` | `id` | 查看代码片段详情 |
| `list/snippet` | `scope?`, `project_id?`, `language?`, `limit?`, `offset?` | 列出代码片段 |
| `search/snippet` | `query`, `limit?`, `offset?` | 搜索代码片段 |
| `update/snippet` | `id`, `name?`, `language?`, `content?`, `tags?` | 更新代码片段 |
| `delete/snippet` | `id` | 删除代码片段 |
| `set/env` | `project_id`, `key`, `value?`, `description?` | 设置项目环境变量（存在则覆盖） |
| `get/env` | `project_id`, `key` | 获取项目环境变量 |
| `list/env` | `project_id`, `limit?`, `offset?` | 列出项目所有环境变量 |
| `delete/env` | `project_id`, `key` | 删除项目环境变量 |
| `add/log` | `summary`, `event_type?`, `project_id?`, `detail?` | 新增事件日志 |
| `get/log` | `id` | 查看事件日志详情 |
| `list/log` | `project_id?`, `event_type?`, `limit?`, `offset?` | 列出事件日志 |
| `clear/log` | `project_id?`, `event_type?` | 清理事件日志（需至少传一个条件） |
| `stats/all` | 无 | 全库数据量统计（笔记/任务/项目/文档等各模块计数） |
| `cleanup/expired` | 无 | 清理已过期的记忆条目 |
| `search/all` | `query`, `modules?`, `limit?` | 跨模块全局搜索（notes/tasks/docs/snippets/dict/prompt） |
| `bulk/note_add` | `items` | 批量新增笔记，`items` 为 `[{name, body?}]` 数组 |
| `bulk/task_add` | `items` | 批量新增任务，`items` 为 `[{name, description?, priority?, due_date?}]` 数组 |
| `export/project` | `project_id` | 导出项目完整数据（含 todos/progress/memory/docs/env/snippets 等）为 JSON |
| `import/project` | `data` | 导入项目数据（`export/project` 产出的 JSON） |
| `list/tags` | `module?` | 列出所有标签及引用次数（module 可选：docs/dict/prompt/snippet） |
| `rename/tag` | `old_name`, `new_name`, `module?` | 重命名标签 |
| `merge/tags` | `tags`, `target`, `module?` | 将多个标签合并为一个目标标签 |
| `backup/db` | `dest?` | 备份数据库文件（不传 `dest` 则自动生成时间戳文件名） |
| `query/hot-events` | `topic`, `date?`, `limit?`, `sources?`, `timezone?` | 查询热点事件（Google News / Hacker News） |

## 项目字段与查询规则（重点）

### 1) 项目主实体字段（projects）

| 字段 | 类型 | 必填 | 默认值 | 说明 | 可更新 |
|:--|:--|:--:|:--|:--|:--:|
| `id` | string | 是 | - | 项目唯一 ID（主键） | 否 |
| `name` | string | 是 | - | 项目名称 | 是 |
| `describe` | string | 否 | `""` | 项目描述 | 是 |
| `location` | string | 否 | `""` | 项目路径/位置 | 是 |
| `environment` | string | 否 | `""` | 运行环境描述 | 是 |
| `languages` | string / string[] | 否 | `[]` | 语言列表，存储为 JSON 字符串 | 是 |
| `libraries` | string / string[] | 否 | `[]` | 依赖库列表，存储为 JSON 字符串 | 是 |
| `status` | enum | 否 | `active` | 仅允许 `active` / `paused` / `archived` | 是 |
| `owner` | string | 否 | `""` | 负责人 | 是 |
| `created_at` | datetime | 自动 | `now` | 创建时间 | 否 |
| `updated_at` | datetime | 自动 | `now` | 更新时间 | 自动维护 |

### 2) 项目相关工具入参字段

| 工具 | 必填参数 | 可选参数 |
|:--|:--|:--|
| `add/project` | `id`, `name` | `describe`, `location`, `environment`, `languages`, `libraries`, `status`, `owner` |
| `update/project` | `id` | `name`, `describe`, `location`, `environment`, `languages`, `libraries`, `status`, `owner` |
| `list/project` | 无 | `status`, `limit`, `offset` |
| `get/project` | `id` | 无 |
| `delete/project` | `id` | 无 |

### 3) list/project 的过滤、分页、排序

| 能力 | 规则 |
|:--|:--|
| 可过滤字段 | `status` |
| status 取值 | `all` / `active` / `paused` / `archived` |
| 分页 | `limit`（默认 20）+ `offset`（默认 0） |
| 排序 | 固定 `ORDER BY p.id DESC` |
| 自定义排序 | 当前不支持 |

### 4) list/project 返回内容（摘要）

| 返回项 | 来源 |
|:--|:--|
| `id` | `projects.id` |
| `status` | `projects.status` |
| `name` | `projects.name` |
| `location` | `projects.location` |
| `todo_done/todo_total` | `project_todos` 聚合统计 |

格式示例：

```text
[proj-001] [active] Planner loc=C:/work/planner todo=3/5
```

### 5) get/project 返回内容（详情）

| 分类 | 字段 |
|:--|:--|
| 项目基础字段 | `id`, `name`, `describe`, `location`, `environment`, `languages`, `libraries`, `status`, `owner`, `created_at`, `updated_at` |
| 进度统计 | `progress_total`, `progress_todo`, `progress_doing`, `progress_done` |
| 执行步骤统计 | `todo_total`, `todo_todo`, `todo_doing`, `todo_done` |

## 参数约束

- `id` 必须是正整数。
- `priority` 只允许：`low` / `medium` / `high`。
- `status` 只允许：`todo` / `doing` / `done`（`task_list` 支持 `all`）。
- `project_id`：
	- `memory` 工具必须传。
	- `docs` 工具可不传（公共知识）或传（项目知识）。
- `languages` / `libraries` 支持字符串（逗号分隔）或字符串数组。
- `event_type` 常用值：`info` / `warn` / `error`（自由字符串，不强制枚举）。
- `clear/log` 必须至少传 `project_id` 或 `event_type`，防止误删全表。
- 所有查询均使用参数化 SQL，避免注入。

## 常用调用示例

### 笔记

```json
{"name":"周会纪要","body":"本周完成接口联调"}
```
对应工具：`note_add`

```json
{"query":"接口","limit":10,"offset":0}
```
对应工具：`note_search`

### 任务

```json
{"name":"发布 v1.0","priority":"high","due_date":"2026-05-10"}
```
对应工具：`task_add`

```json
{"status":"todo","priority":"high","limit":20}
```
对应工具：`task_list`

```json
{"id":3,"status":"doing"}
```
对应工具：`task_update`

### 项目

```json
{
	"id":"proj-plan-demo",
	"name":"Planner",
	"describe":"项目规划与执行",
	"location":"C:/work/planner",
	"environment":"python3.12 windows",
	"languages":["python","sql"],
	"libraries":["mcp","sqlite3"]
}
```
对应工具：`add/project`

```json
{"project_id":"proj-plan-demo","name":"初始化schema","feature":"db","context":"先建表再写工具","step_order":1}
```
对应工具：`add/todo`

### 知识库与记忆

```json
{"name":"MCP契约约定","content":"统一ERR_*错误码","tags":"protocol,contract"}
```
对应工具：`add/docs`（公共知识）

```json
{"project_id":"proj-plan-demo","name":"项目部署说明","content":"仅当前项目使用"}
```
对应工具：`add/docs`（项目知识）

```json
{"project_id":"proj-plan-demo","key":"preferred_tags","value":"docs,project"}
```
对应工具：`add/memory`

### 词典与提示词模板

```json
{"name":"api_base","value":"https://example.local","tags":"config,endpoint"}
```
对应工具：`add/dict`

```json
{"name":"rewrite-mail","content":"请将以下内容改写为正式邮件：{{content}}","tags":"rewrite,mail"}
```
对应工具：`add/prompt`

```json
{"name":"api_base","scope":"auto","project_id":"proj-plan-demo"}
```
对应工具：`get/dict/by-name`

```json
{"name":"rewrite-mail","scope":"auto","project_id":"proj-plan-demo"}
```
对应工具：`get/prompt/by-name`

```json
{"id":1,"variables":{"content":"明天讨论需求变更"},"mode":"strict"}
```
对应工具：`render/prompt`

### 代码片段

```json
{"name":"db-connect","language":"python","content":"conn = sqlite3.connect(db_path)\nconn.row_factory = sqlite3.Row","tags":"db,sqlite"}
```
对应工具：`add/snippet`（公共片段）

```json
{"project_id":"proj-plan-demo","name":"init-schema","language":"sql","content":"CREATE TABLE IF NOT EXISTS ...","tags":"db,init"}
```
对应工具：`add/snippet`（项目片段）

### 环境变量

```json
{"project_id":"proj-plan-demo","key":"DB_PATH","value":"./db/zkali.db","description":"数据库文件路径"}
```
对应工具：`set/env`

```json
{"project_id":"proj-plan-demo"}
```
对应工具：`list/env`

### 事件日志

```json
{"summary":"schema 初始化完成","event_type":"info","project_id":"proj-plan-demo"}
```
对应工具：`add/log`

```json
{"project_id":"proj-plan-demo","event_type":"error","limit":10}
```
对应工具：`list/log`

## 在 VS Code 中注册

已配置文件：[.vscode/mcp.json](.vscode/mcp.json)

如果你调整了 Python 路径，请同步更新该文件中的 `command` 字段。
