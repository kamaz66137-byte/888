# index.md — zkali-mcp references 导航索引

## 核心规范

| 文件 | 主题 | 关键内容 |
|------|------|---------|
| [naming.md](naming.md) | 命名规范 | 工具命名格式表、Python 标识符、数据库命名、dispatch 函数命名 |
| [contract.md](contract.md) | 工具契约 | inputSchema 约束速查、输出格式契约表、错误处理层级、rowcount 检查 |
| [ai-protocol.md](ai-protocol.md) | AI 协议 | description 三段式规范、触发词覆盖要求、x-tags 参考表、HELP_MAP 格式 |
| [structure.md](structure.md) | 项目结构 | 标准目录树、各层职责、依赖方向、tool/ 可迭代性 |
| [db.md](db.md) | 数据库层 | tools 表字段标准、索引建议、name/describe/tags 查询范式 |
| [protocol.md](protocol.md) | 协议层 | 统一错误处理、响应模型、契约映射 |
| [project.md](project.md) | 项目层 | 项目模型、进度模型、项目状态管理 |
| [memory.md](memory.md) | 记忆层 | 记忆分层、项目隔离、读写安全规则 |
| [iteration.md](iteration.md) | 迭代方案 | 新增模块四步法、验证命令、代码注释规范、run_self_test 维护 |

## 快速入门

| 文件 | 主题 | 关键内容 |
|------|------|---------|
| [getting_started.md](getting_started.md) | 快速启动 | 安装依赖、VS Code 注册、自检命令 |
| [examples.md](examples.md) | 完整代码模板 | main.py / runner.py / dispatcher.py / tool 模板 |

## 参考资料

| 文件 | 主题 | 关键内容 |
|------|------|---------|
| [api.md](api.md) | MCP SDK API | Server / Tool / TextContent / stdio_server 用法 |
| [troubleshooting.md](troubleshooting.md) | 问题排查 | 常见错误、调试方法、环境问题 |

---

## 快速定位

| 我要... | 去哪里 |
|---------|--------|
| 给工具起名 | [naming.md §1](naming.md#1-工具命名) |
| 给工具目录命名（crawl/search/add/list 等） | [naming.md §6](naming.md#6-工具注册名标准面向工具市场自动发现) |
| 知道工具输出格式 | [contract.md §2](contract.md#2-输出格式标准output-contract) |
| 定义 tools 字段契约（id/name/version/describe/tags/content） | [contract.md §4](contract.md#4-工具注册元数据契约tools) |
| 设计 name/describe/tags 发现机制 | [ai-protocol.md §5](ai-protocol.md#5-自动发现协议name--describe--tags) |
| 处理工具错误 | [contract.md §3](contract.md#3-错误处理规范) |
| 统一错误处理与响应协议 | [protocol.md §2](protocol.md#2-响应标准) |
| 让 LLM 自动路由工具 | [ai-protocol.md §1](ai-protocol.md#1-description-字段规范) |
| 添加 x-tags | [ai-protocol.md §2](ai-protocol.md#2-x-tags-规范) |
| 写 HELP_MAP | [ai-protocol.md §3](ai-protocol.md#3-help_map-规范) |
| 了解目录结构 | [structure.md §1](structure.md#1-标准目录树) |
| 配置六大模块（db/tool/prompt/docs/dict/memory） | [structure.md §2](structure.md#2-各模块职责) |
| 定义模块边界（IN/OUT） | [structure.md §8](structure.md#8-模块边界矩阵谁负责谁不负责) |
| 规划模块主题方向 | [structure.md §9](structure.md#9-模块主题方向roadmap) |
| 设计模块如何结合 | [structure.md §10](structure.md#10-如何结合端到端编排) |
| 管理项目与进度 | [project.md §3](project.md#3-进度模型) |
| 实现项目隔离记忆 | [memory.md §4](memory.md#4-隔离规则必须) |
| 新增一个模块 | [iteration.md §1](iteration.md#1-新增模块标准四步法) |
| 了解数据库存储边界 | [db.md §1](db.md#1-存储边界) |
| 添加 tools 数据表 | [db.md §2](db.md#2-tools-表标准字段) |
| 写工具发现 SQL | [db.md §5](db.md#5-查询范式) |
| 写代码注释 | [iteration.md §3](iteration.md#3-代码注释规范) |