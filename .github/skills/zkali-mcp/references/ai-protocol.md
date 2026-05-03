# ai-protocol.md — AI 协议（description / x-tags / HELP_MAP）

MCP Server 的 `Tool.description` 和 `inputSchema["x-tags"]` 是 LLM **自动路由**的核心依据。

---

## 1. description 字段规范

每个工具的 `description` **必须**包含三段：

```
{功能描述（1 句话，准确描述操作和存储层）}
【触发词】{中英文自然语言同义词，逗号分隔}
【返回】{对应 contract.md 输出格式的说明}
```

**完整示例**：

```python
Tool(
    name="note_add",
    description=(
        "新增一条笔记并持久化到 sqlite3。"
        "【触发词】写笔记、记录、新建笔记、保存笔记、添加笔记、记一下、note add、create note。"
        "【返回】OK id={N}。"
    ),
)

Tool(
    name="note_list",
    description=(
        "分页列出所有笔记（按 id 倒序，最新在前）。"
        "【触发词】所有笔记、笔记列表、最近笔记、有哪些笔记、查看笔记、note list、show notes。"
        "【返回】每行 '[id] title (created_at)'；空返回 '(empty)'。"
    ),
)

Tool(
    name="task_stats",
    description=(
        "统计任务总数与各状态的数量。"
        "【触发词】任务统计、任务概况、有多少任务、完成了多少、task stats、task summary。"
        "【返回】每行 'key: N'，字段：total/todo/doing/done。"
    ),
)
```

### 触发词覆盖要求

- 至少 **3 个中文表达** + **2 个英文表达**
- 覆盖动词变体（新建/添加/创建/写）
- 覆盖名词变体（笔记/记录/note）
- CRUD 操作覆盖同义动词（删除/移除/取消/去掉）

| action | 中文触发词示例 | 英文触发词示例 |
|--------|--------------|--------------|
| `add` | 添加、新建、创建、写、记 | add、create、new |
| `get` | 查看、获取、查一下、详情 | get、fetch、show、read |
| `list` | 列出、所有、有哪些、最近 | list、show all、browse |
| `search` | 搜索、查找、找一下 | search、find、query |
| `update` | 修改、编辑、更新、改 | update、edit、modify |
| `delete` | 删除、移除、取消、去掉 | delete、remove、cancel |
| `stats` | 统计、概况、多少、汇总 | stats、summary、count |

---

## 2. x-tags 规范

每个 Tool 的 `inputSchema` 顶层包含 `x-tags` 数组：

```python
"x-tags": [module, action, ...domain_keywords]
```

**固定规则**：
- 第 1 个 tag：**module 名**（如 `"note"`）
- 第 2 个 tag：**action 名**（如 `"add"`）
- 后续 tag：语义同义词（供 AI 客户端分类和路由）

### 各模块 x-tags 参考

```python
# system
tool_help:   ["system", "help"]

# note 模块
note_add:    ["note", "add",    "create", "write"]
note_get:    ["note", "get",    "detail", "read"]
note_update: ["note", "update", "edit",   "modify"]
note_list:   ["note", "list",   "browse", "paginate"]
note_search: ["note", "search", "find",   "query", "fulltext"]
note_delete: ["note", "delete", "remove"]

# task 模块
task_add:    ["task", "add",    "create", "todo"]
task_list:   ["task", "list",   "browse", "filter"]
task_update: ["task", "update", "edit",   "modify"]
task_done:   ["task", "done",   "complete", "finish"]
task_delete: ["task", "delete", "remove", "cancel"]
task_stats:  ["task", "stats",  "summary", "count", "aggregate"]
```

---

## 3. HELP_MAP 规范

`HELP_MAP` 同时作为 **`tool_help` 的响应内容** 和 **机器可读文档**。

**格式固定**：

```python
"{name}": "{name}({params}) -> {output_contract}"
```

**参数标注规则**：
- 必填参数：直接写 `title`
- 可选参数：加问号 `body?`
- 默认值：写出 `limit=20`
- 枚举值：列出 `priority in {low,medium,high}`

**完整示例**：

```python
HELP_MAP: dict[str, str] = {
    "tool_help": (
        "tool_help(name?) -> "
        "不传 name：返回全部工具列表，每行 '- name(params) -> output'；"
        "传 name：返回该工具的完整说明。"
    ),
    "note_add": (
        "note_add(title, body?) -> "
        "新增笔记，返回 'OK id={N}'。title 必填。"
    ),
    "note_list": (
        "note_list(limit=20, offset=0) -> "
        "分页列笔记（id 倒序），每行 '[id] title (created_at)'；空返回 '(empty)'。"
    ),
    "task_add": (
        "task_add(title, description?, priority='medium', due_date?) -> "
        "新增任务，返回 'OK id={N}'。priority in {low,medium,high}。"
    ),
    "task_stats": (
        "task_stats() -> "
        "统计任务数量，每行 'key: N'（total/todo/doing/done）。"
    ),
}
```

---

## 4. _contract.py 作为规范锚点

`_contract.py` 是项目**技术规范的唯一真相来源（Single Source of Truth）**：
- 模块顶部文档字符串包含完整的命名规范、输出标准、迭代方案摘要
- helpers 函数本身即为规范的可执行验证
- 新成员阅读 `_contract.py` 即可快速了解全部约定
- 更新规范时**先改 `_contract.py`**，再改实现，再改文档

---

## 5. 自动发现协议（name / describe / tags）

为了让 AI 自动选对工具，工具目录必须同时暴露以下三类发现键：

- `name`：精确路由键（确定性最高）
- `describe`：语义路由键（自然语言意图匹配）
- `tags`：标签路由键（领域分类和二次过滤）

推荐执行顺序：

1. 先尝试 `name` 精确匹配。
2. 未命中则走 `describe` 语义检索。
3. 最后用 `tags` 做重排或过滤。

---

## 6. 操作层协议（工具目录管理）

对“工具目录”建议统一使用以下能力名：

- `add/tool`
- `update/tool`
- `delete/tool`
- `list/tool`
- `get/tool`（通过 name 获取详情）
- `discover/tool`（通过 describe/tags 发现工具）

`discover/tool` 描述模板建议：

```text
发现工具目录中的候选工具，支持语义扫描和标签过滤。
【触发词】找工具、发现工具、推荐工具、按标签找、按描述找、discover tool、find tool。
【返回】每行 '[name] v{version} [classification] enabled={0|1}'。
```