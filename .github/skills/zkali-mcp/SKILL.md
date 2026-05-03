---
name: zkali-mcp
description: "Python MCP Server 端到端能力：命名规范、项目结构、模块化、工具契约（输入/输出/错误处理）、AI 协议（description/x-tags 自动路由）、技术文档标准、迭代方案。以 sqlite3 为唯一持久化后端。适用于为 Claude Code/VS Code Copilot 构建生产可用的本地工具服务。"
---

# zkali-mcp 技能

用 Python + sqlite3 构建**生产可用**的 MCP Server。

详细规范见 `references/`，本文件只做激活入口与快速参考。

---

## 何时触发

满足以下任意条件时激活：

- 为 Claude Code / VS Code Copilot 构建自定义 MCP 工具
- 设计带有 JSON Schema 的工具协议
- MCP Server 需要持久化数据（仅 sqlite3）
- 新增/修改工具模块或数据表
- 调试工具的输入输出格式
- 对现有 MCP Server 进行模块化重构

---

## 禁止使用 / 边界

- 不覆盖 MCP 客户端开发（只涉及 Server 端）
- 不涉及 LLM 推理逻辑
- **仅** sqlite3 作为存储层，不提供其他数据库方案
- 缺少关键信息时先提问：工具功能？传输方式（stdio/sse）？表结构？

---

## references/ 导航

| 文件 | 内容 |
|------|------|
| [index.md](references/index.md) | 全目录导航 + 快速定位表 |
| [structure.md](references/structure.md) | 项目结构 / 模块化分层 / 各层职责 / 依赖方向 |
| [naming.md](references/naming.md) | 工具命名 / Python 标识符 / 数据库命名规范 |
| [contract.md](references/contract.md) | 工具契约：输入参数标准 / 输出格式 / 错误处理 |
| [ai-protocol.md](references/ai-protocol.md) | AI 协议：description 规范 / 触发词 / x-tags / HELP_MAP |
| [db.md](references/db.md) | 数据库层规范：connection / schema / SQL 最佳实践 |
| [protocol.md](references/protocol.md) | 统一错误处理 / 响应 / 契约协议模块 |
| [project.md](references/project.md) | 项目模块与进度管理标准 |
| [memory.md](references/memory.md) | 记忆模块标准（支持项目隔离） |
| [iteration.md](references/iteration.md) | 迭代新模块四步法 / 验证命令 / 代码注释规范 |
| [getting_started.md](references/getting_started.md) | 快速启动 / 安装 / VS Code 注册 |
| [examples.md](references/examples.md) | 完整代码模板（main/runner/dispatcher/tool） |
| [api.md](references/api.md) | MCP SDK API 速查 |
| [troubleshooting.md](references/troubleshooting.md) | 常见问题排查 |

---

## 规则约束速查

### MUST

- sqlite3 是**唯一**存储层
- 目录结构必须包含：`db/` `tool/` `prompt/` `docs/` `dict/` `memory/`
- 必须有 `protocol/` 统一错误处理、响应和契约
- 必须有 `project/` 项目与进度模块
- 记忆读写必须携带 `project_id`（项目隔离）
- 所有 SQL 使用参数化查询（`?`），禁止字符串拼接
- 每个 Tool 必须有 `description`（含触发词）+ 完整 `inputSchema`（含 x-tags）
- `inputSchema` 包含 `"additionalProperties": False`
- 未知工具名抛出 `ValueError`
- 工具输出使用 `_contract.py` helpers，不硬编码字符串
- 新增工具后必须运行 `--self-test`
- `main.py` 只做参数解析，不含业务逻辑
- 文件编码统一 UTF-8（无 BOM）

### NEVER

- 引入 MySQL / PostgreSQL / Redis / MongoDB
- 省略 `inputSchema` 中的 `required` 字段
- 在 `description` 中省略【触发词】和【返回】段
- 把 `.db` 文件提交到 git
- 跨层调用（`db/` 导入 `tool/`，`main.py` 直接调用 SQL）

---

## 快速启动

```bash
pip install mcp
python main.py --self-test    # 验证环境
```

`.vscode/mcp.json` 注册：

```json
{
  "servers": {
    "zkali-mcp": {
      "type": "stdio",
      "command": "${workspaceFolder}/.venv/Scripts/python.exe",
      "args": ["${workspaceFolder}/src/zkali-mcp/main.py"]
    }
  }
}
```

完整模板见 [references/examples.md](references/examples.md)。
