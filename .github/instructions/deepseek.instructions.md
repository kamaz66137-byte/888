---
name: 'deepseek'
description: 'DeepSeek Agents项目工程结构,契约优先,搭建高质量Agents工程'
applyTo: '**'
---
# DeepSeek Agents 必须遵守的规则

- [MUST] 关于模型、方法、工具等，必须查阅 [官方文档](https://api-docs.deepseek.com/zh-cn/) 后才可开发，不允许随意使用，必须遵守契约优先原则：先定义好契约，再进行开发。
- [MUST] Python 虚拟环境路径：必须按照 `.vscode/settings.json` 中的路径为基准。

## 本地环境

- Windows 10
- Python 3.12

---

## 模型选型规范

| 场景 | 模型 |
|:---|:---|
| 简单问答、代码补全、快速响应 | `deepseek-v4-flash` |
| 复杂推理、多步 Agent、深度分析 | `deepseek-v4-pro` |
| 推理增强模式 | `deepseek-v4-pro[1m]`（需开启 `thinking`） |

- [MUSTNOT] 使用已弃用模型：`deepseek-chat`、`deepseek-reasoner`（2026-07-24 起弃用）。
- [MUST] 模型名称必须为字符串常量，不允许动态拼接。

---

## API Key 与凭据规范

- [MUST] API Key 从环境变量 `DEEPSEEK_API_KEY` 读取，禁止硬编码到源码或配置文件。
- [MUSTNOT] 在日志、异常消息、注释或代码中输出完整 API Key。
- [MUST] 联调前运行健康检查脚本，确认 Key 有效：
  ```bash
  python .github/skills/deepseek-api/scripts/deepseek-healthcheck.py --preflight-only
  ```

---

## 工具调用（Function Calling）契约规范

- [MUST] 每个工具必须包含 `name`（snake_case 命名）、`description`（含【触发词】与【返回】描述）、`parameters`（完整 JSON Schema）。
- [MUST] `parameters` 必须包含 `required` 字段，不允许省略。
- [MUST] 收到响应后必须检查 `finish_reason`：
  - `tool_calls`：执行工具，将结果以 `role: tool` + `tool_call_id` 追加到 messages，再次调用 API。
  - `stop`：模型直接回答，无需执行工具。
- [MUSTNOT] 不检查 `finish_reason` 直接解析工具调用结果。
- [MUST] `tool` 消息的 `tool_call_id` 必须与请求中一致，否则模型无法引用结果。

---

## 错误处理规范

- [MUST] 捕获并处理以下 HTTP 错误：
  - `401 Unauthorized`：Key 无效，立即停止重试，抛出明确错误。
  - `429 Too Many Requests`：指数退避重试，最多 3 次（1s → 2s → 4s）。
  - `400 Bad Request`：检查模型名称、参数格式，不重试。
  - `5xx`：可重试，最多 2 次。
- [MUSTNOT] 忽略 HTTP 429，无限循环重试。
- [MUST] 流式输出（`stream=True`）必须处理 `delta.content is None` 的情况（跳过空 chunk）。

---

## 命名规范

- [MUST] 工具函数名使用 `snake_case`（如 `get_weather`、`search_document`）。
- [MUST] 工具 `description` 必须以动词开头，描述工具的功能与适用场景。
- [MUSTNOT] 工具名与标准库函数名冲突（如不使用 `print`、`input`）。

---

## 验收标准

- [ ] 所有模型名称符合当前可用模型列表（非弃用）。
- [ ] API Key 从环境变量读取，未硬编码。
- [ ] 工具调用契约完整（name/description/parameters/required）。
- [ ] 错误处理覆盖 401 / 429 / 400 / 5xx。
- [ ] 流式输出处理 `delta.content is None`。
- [ ] 项目方法符合 [官方文档](https://api-docs.deepseek.com/zh-cn/) 项目标准。

