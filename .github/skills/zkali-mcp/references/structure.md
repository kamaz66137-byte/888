# structure.md — 项目结构与模块化分层（v2）

## 1. 标准目录树（必须包含）

```text
src/zkali-mcp/
  main.py
  zkmcp/
    __init__.py
    runner.py
    db/         # sqlite 相关模块（含性能优化）
    tool/       # 工具实现模块
    prompt/     # 提示词模块
    docs/       # 知识库模块
    dict/       # 语义字典模块
    memory/     # 记忆模块（支持项目隔离）
    protocol/   # 统一错误处理、响应、契约协议
    project/    # 项目管理与进度模块
```

---

## 2. 各模块职责

### 2.1 db/

- sqlite3 连接、事务、schema、迁移
- 性能优化：WAL、索引、批量写入、分页策略
- 只提供数据访问能力，不拼接面向用户响应

### 2.2 tool/

- MCP Tool 具体实现
- 输入校验后调用 db/prompt/docs/dict/memory 能力
- 所有输出统一走 protocol/ 的响应构造器
- 工具能力默认公共可用，不以 project_id 作为全局前置条件

### 2.3 prompt/

- 管理系统提示词、任务提示词、工具提示词模板
- 统一模板变量（如 `{project_id}`、`{lang}`）
- 按场景分文件，不在代码中硬编码长提示词

### 2.4 docs/

- 维护知识库片段、FAQ、规范条目
- 提供检索接口供 tool/ 调用
- 与 prompt/ 解耦，docs 负责内容，prompt 负责组织
- 支持双模式：公共知识（不绑定项目）和项目知识（绑定 project_id）

### 2.5 dict/

- 语义同义词词典、分类词典、触发词词典
- 为工具自动发现（name/describe/tags）提供归一化支持

### 2.6 memory/

- 统一记忆读写（会话级、项目级）
- 必须支持项目隔离：任何记忆记录都绑定 `project_id`
- 禁止跨项目默认共享记忆
- `memory` 相关工具必须强制携带 `project_id`

### 2.7 protocol/

- 统一错误码、错误消息、成功响应
- 统一输出契约（文本或 JSON）
- 统一参数校验错误映射与异常降级

### 2.8 project/

- 项目注册、项目配置、项目状态
- 项目进度管理（todo/doing/done、里程碑、更新时间）
- 为 memory/ 提供 `project_id` 生命周期管理

---

## 3. 依赖方向（单向）

```text
main.py
  -> runner.py
      -> tool/
          -> protocol/
          -> db/
          -> prompt/
          -> docs/
          -> dict/
          -> memory/
          -> project/
```

硬性约束：

- db/ 不依赖 tool/
- protocol/ 不依赖具体业务模块
- memory/ 不绕过 project/ 写入隔离键
- tool/ 之外模块不得直接对外暴露 MCP Tool

---

## 4. 统一协议模块（protocol/）最小能力

- `ok(data=None, message="OK")`
- `err(code, message, detail=None)`
- `validate_error(field, reason)`
- `not_found(entity, key)`
- `conflict(entity, key)`

推荐错误码：

- `ERR_VALIDATION`
- `ERR_NOT_FOUND`
- `ERR_CONFLICT`
- `ERR_FORBIDDEN`
- `ERR_INTERNAL`

---

## 5. 项目隔离记忆标准

每条记忆最小字段：

```json
{
  "id": 1,
  "project_id": "proj-xxx",
  "scope": "session|project",
  "key": "string",
  "value": "string/json",
  "updated_at": "2026-05-03 12:00:00"
}
```

隔离规则：

- 查询必须带 `project_id`
- 写入必须带 `project_id`
- 删除必须限定 `project_id`

---

## 6. 模块扩展规范

新增模块（例如 `tool_registry`）最小步骤：

1. 在 `tool/` 增加实现文件
2. 在 `tool/dispatcher.py` 挂接分发
3. 在 `tool/_schemas.py` 注册 inputSchema 和 x-tags
4. 若涉及状态与进度，接入 `project/`
5. 若涉及记忆，接入 `memory/` 并强制 `project_id`
6. 运行 `python src/zkali-mcp/main.py --self-test`

---

## 7. 文档同步规则

- 结构变更后同步更新：
  - `references/index.md`
  - `references/contract.md`
  - `references/ai-protocol.md`
  - `references/examples.md`

---

## 8. 模块边界矩阵（谁负责，谁不负责）

| 模块 | 负责（IN） | 不负责（OUT） |
|------|------------|---------------|
| `db/` | SQL、事务、索引、迁移、性能优化 | MCP 协议响应、业务文案、提示词拼装 |
| `tool/` | 工具业务编排、调用其他模块、对外暴露能力 | 直接管理连接池细节、跨项目绕过隔离 |
| `prompt/` | 提示词模板、变量注入、版本化模板 | 存储业务状态、执行 SQL |
| `docs/` | 知识片段管理、检索接口 | 业务流程控制、协议错误映射 |
| `dict/` | 同义词归一化、标签映射、语义分类 | 直接执行工具动作 |
| `memory/` | 记忆存取、会话/项目分层、隔离约束 | 项目生命周期决策 |
| `protocol/` | 成功/失败响应、错误码、异常降级 | 业务规则判断、数据持久化 |
| `project/` | 项目实体、状态、进度、里程碑 | 工具路由、提示词渲染 |

边界铁律：

- 任何模块都不能绕过 `protocol/` 直接返回未约束错误。
- 任何模块都不能绕过 `project/` 在 `memory/` 写入无 `project_id` 数据。
- `tool/` 是唯一对外 MCP 暴露层，其他模块只提供内部能力。

---

## 9. 模块主题方向（Roadmap）

| 模块 | 主题方向 | 近期优先级 |
|------|----------|------------|
| `db/` | 稳定性与性能（WAL、索引命中、批量写） | 高 |
| `tool/` | 工具标准化（add/update/delete/list/get/discover） | 高 |
| `prompt/` | 模板可维护与可复用 | 中 |
| `docs/` | 知识检索质量（召回与排序） | 中 |
| `dict/` | 语义归一化准确率（同义词、标签） | 中 |
| `memory/` | 项目隔离与生命周期（TTL、清理） | 高 |
| `protocol/` | 响应一致性与可观测错误码 | 高 |
| `project/` | 多项目治理与进度看板化 | 高 |

---

## 10. 如何结合（端到端编排）

统一编排链路：

```text
tool/ 接收请求
  -> project/ 校验 project_id 与项目状态
  -> dict/ 归一化 name/describe/tags 语义
  -> docs/ + prompt/ 组装上下文（可选）
  -> db/ 与 memory/ 执行读写
  -> protocol/ 统一返回 ok/err
```

### 10.1 discover/tool 场景

1. `tool/` 接收 `query/tags/project_id`。
2. `project/` 校验项目可用。
3. `dict/` 将 query 同义词扩展。
4. `db/` 按 `name/describe/tags` 检索。
5. `memory/` 记录用户偏好标签（带 `project_id`）。
6. `protocol/` 输出统一响应。

### 10.2 进度驱动场景

1. `add/progress` 写入 `project/`。
2. 任务状态变更触发 `memory/` 写入上下文摘要。
3. `list/progress` 读取时可拼接 `docs/` 规范建议。
4. 全流程错误统一走 `protocol/`。

---

## 11. 实施检查清单

- 每个对外工具都能映射到一个 `project_id`。
- 每个失败路径都返回 `ERR_*` 标准码。
- 每个查询接口都声明是否读取 `memory/`。
- 每个写接口都声明是否更新进度（`project/`）。
- 每次新增模块后，更新 `references/index.md` 快速定位。
