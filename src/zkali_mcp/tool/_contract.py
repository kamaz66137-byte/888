"""
zkali-mcp 工具契约 (Tool Contract)
====================================

命名规范
--------
格式：{module}_{action}

- module  = 领域名词（单数小写，如 note / task / user / doc）
- action  ∈ { add | get | list | search | update | delete | stats }
            + 领域专用动词（如 task_done）
- 系统保留前缀：tool_*

Action 语义
-----------
  add     → 新增一条记录，返回 OK id={N}
  get     → 按 id 获取详情，返回结构化文本或 ERR not_found
  list    → 分页列表，返回行集合或 (empty)
  search  → 关键词检索，返回行集合或 (empty)
  update  → 按 id 更新字段，返回 OK updated 或 ERR not_found
  delete  → 按 id 删除，返回 OK deleted 或 ERR not_found
  stats   → 聚合统计，返回 key: value 多行

输出格式标准 (Output Contract)
------------------------------
1. Mutation add       → "OK id={N}"
2. Mutation update    → "OK updated"  | "ERR not_found"
3. Mutation delete    → "OK deleted"  | "ERR not_found"
4. Mutation done      → "OK updated"  | "ERR not_found"
5. List / Search      → "(empty)"  或  "[id] field1 | field2 (timestamp)" 每行一条
6. Get (detail)       → "ERR not_found"  或  "field: value" 每行一字段
7. Stats              → "total: {N}\\nstatus: {N}\\n..." key: value 每行
8. Validation Error   → "ERR {message}"

description 字段规范 (用于 LLM 自动路由)
-----------------------------------------
每个 Tool.description 必须包含：
  1. 功能描述（1 句）
  2. 【触发词】覆盖自然语言同义词，逗号分隔
  3. 【返回】输出格式说明
  示例：
    "新增一条笔记并持久化到 sqlite3。【触发词】写笔记、记录、新建笔记、保存笔记、添加笔记。【返回】OK id={N}。"

x-tags 规范
-----------
每个 Tool.inputSchema 顶层包含 "x-tags": [module, action, ...domain_keywords]
- AI 客户端可读取 tags 做工具分类和自动路由
- 第一个 tag 固定为 module 名，第二个为 action 名

迭代新模块方案 (Iteration Guide)
---------------------------------
1. 新建 tool/{module}.py
   - 实现 dispatch_{module}_tool(name, args, db_path) -> str | None
   - 遵循命名规范与输出格式标准
   - 导入 _contract 的 helper 函数

2. 在 tool/_schemas.py 补充
   - HELP_MAP 条目："{name}({params}) -> {output_format}"
   - TOOL_ORDER 条目（按模块分组追加）
   - build_tools() 中的 Tool 定义（含 description 规范 + x-tags）

3. 在 tool/dispatcher.py 注册
   - from .{module} import dispatch_{module}_tool
   - 在 dispatch_tool() 中追加调用链

4. 如需新表 → 在 db/schema.py 的 init_db() 中追加
   CREATE TABLE IF NOT EXISTS {module}s (...)

5. 如有新依赖 → 追加到 requirements.txt
"""

from __future__ import annotations

# ── 输出格式 helpers ───────────────────────────────────────────────────────


def ok_id(n: int) -> str:
    """Mutation add 成功：返回新记录 id。"""
    return f"OK id={n}"


def ok_updated() -> str:
    """Mutation update/done 成功。"""
    return "OK updated"


def ok_deleted() -> str:
    """Mutation delete 成功。"""
    return "OK deleted"


def err_not_found() -> str:
    """记录不存在。"""
    return "ERR not_found"


def err_validation(msg: str) -> str:
    """输入校验失败。"""
    return f"ERR {msg}"


def list_empty() -> str:
    """list/search 无结果。"""
    return "(empty)"
