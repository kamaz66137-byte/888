---
name: deepseek-api
description: "DeepSeek API 端到端能力：包含 Chat/Reasoner 调用、Agent 工具调用、Skill 构建。适用于需要接入 DeepSeek 模型实现 Agent、工具调用、技能封装等场景。"
---

# deepseek-api 技能

DeepSeek API 的生产级技能：基于实际情况构建 DeepSeek Agent、Tool、Skill 相关功能，覆盖模型选型、API 调用、工具调用、流式输出与错误处理。

## 何时使用本技能

满足以下任意条件时触发：
- 需要调用 DeepSeek API（Chat / Reasoner / 工具调用）
- 正在构建 DeepSeek Agent 或封装 Skill
- 需要为 DeepSeek 配置工具（function calling）
- 需要流式输出（stream）实现
- 调试 DeepSeek API 报错（4xx / 5xx / 超时）

## 禁止使用 / 边界

- **不涉及** OpenAI / Anthropic 原生 SDK（仅 DeepSeek OpenAI 兼容接口）
- **不包含** 模型训练、微调、部署
- **不生成** API Key 或账号凭据
- 缺失以下信息时先提问：模型名称（deepseek-v4-flash / deepseek-v4-pro）、是否需要工具调用、目标语言（Python / PowerShell / Node.js）

## 快速参考

### 端点与模型

| 用途 | 端点 | 推荐模型 |
|------|------|---------|
| Chat（OpenAI 兼容） | `https://api.deepseek.com` | `deepseek-v4-flash`（快速）/ `deepseek-v4-pro`（强推理）|
| Anthropic 兼容 | `https://api.deepseek.com/anthropic` | 同上 |

> ⚠️ `deepseek-chat` / `deepseek-reasoner` 已于 2026-07-24 弃用，请勿使用。

### Python：基础 Chat 调用

```python
from openai import OpenAI

client = OpenAI(
    api_key="your-deepseek-key",
    base_url="https://api.deepseek.com"
)

resp = client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=[{"role": "user", "content": "你好"}]
)
print(resp.choices[0].message.content)
```

### Python：工具调用（function calling）

```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "获取城市天气",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"]
        }
    }
}]

resp = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=[{"role": "user", "content": "上海今天天气如何？"}],
    tools=tools,
    tool_choice="auto"
)
```

### PowerShell：基础调用（Windows 10）

```powershell
$headers = @{
    "Authorization" = "Bearer $env:DEEPSEEK_API_KEY"
    "Content-Type"  = "application/json"
}
$body = @{
    model    = "deepseek-v4-flash"
    messages = @(@{ role = "user"; content = "你好" })
} | ConvertTo-Json -Depth 5

$resp = Invoke-RestMethod -Uri "https://api.deepseek.com/chat/completions" `
    -Method Post -Headers $headers -Body $body
$resp.choices[0].message.content
```

### 可用性检查（必须先跑）

```bash
python .github/skills/deepseek-api/scripts/deepseek-healthcheck.py --preflight-only
python .github/skills/deepseek-api/scripts/deepseek-healthcheck.py
```

说明：
- 第一个命令检查 `DEEPSEEK_API_KEY` 与 `.vscode/settings.json`。
- 第二个命令执行真实联网调用 `POST /chat/completions`，用于确认 DeepSeek 可用。

### 流式输出（Python）

```python
stream = client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=[{"role": "user", "content": "写一首诗"}],
    stream=True
)
for chunk in stream:
    print(chunk.choices[0].delta.content or "", end="", flush=True)
```

## 规则与约束

- **MUST**：API Key 从环境变量读取（`DEEPSEEK_API_KEY`），禁止硬编码
- **MUST**：使用 `deepseek-v4-flash` 或 `deepseek-v4-pro`，不使用已弃用模型
- **MUST**：联调前必须执行 `deepseek-healthcheck.py`，并确保 live call 成功
- **SHOULD**：工具调用后检查 `finish_reason == "tool_calls"` 再解析
- **SHOULD**：流式输出处理 `delta.content is None` 的情况
- **NEVER**：不在日志/代码中输出完整 API Key
- **NEVER**：不忽略 HTTP 429（限流）——应做指数退避重试

## 示例

### 示例1：构建单轮 Agent（Python）
- **输入**：用户问题 + 工具列表
- **步骤**：
  1. 发送含 `tools` 的 Chat 请求
  2. 检查 `finish_reason == "tool_calls"`
  3. 执行工具，将结果以 `role: tool` 追加到 messages
  4. 再次调用 API 获取最终回答
- **验收**：最终回答中包含工具执行结果，无幻觉

### 示例2：封装 DeepSeek Skill（PowerShell + SKILL.md）
- **输入**：业务场景描述
- **步骤**：
  1. 用 `create-skill.sh <name> --full` 生成骨架
  2. 在 `SKILL.md` 快速参考中放入 PowerShell 调用片段
  3. `validate-skill.sh <name> --strict` 验证结构
- **验收**：`EXIT:0`，中文章节标题全部通过

### 示例3：流式输出 + 错误处理（Python）
- **输入**：长文生成请求
- **步骤**：
  1. 设置 `stream=True`
  2. 逐 chunk 打印 `delta.content`（跳过 `None`）
  3. 捕获 `openai.RateLimitError` 做退避重试（最多 3 次）
- **验收**：输出完整，限流时自动重试后成功

## 常见问题

- **Q: 如何选择 flash 还是 pro？**
  - A: 简单问答/代码补全用 `flash`；复杂推理/多步 Agent 用 `pro`
- **Q: Anthropic 兼容接口和 OpenAI 兼容接口有何区别？**
  - A: 消息格式略有差异（如 `system` 字段位置）；优先用 OpenAI 兼容接口，Anthropic 兼容接口用于已有 Anthropic SDK 的项目迁移
- **Q: 工具调用返回 `finish_reason: stop` 而非 `tool_calls`？**
  - A: 模型判断不需要调用工具，直接回答了；检查工具描述是否足够清晰

## 故障排查

- **401 Unauthorized** → API Key 无效或未设置 `DEEPSEEK_API_KEY` 环境变量
- **429 Too Many Requests** → 触发限流，做指数退避（1s → 2s → 4s）重试
- **400 Bad Request / invalid model** → 使用了已弃用模型名，改为 `deepseek-v4-flash`
- **工具调用结果未被模型引用** → `tool` 消息的 `tool_call_id` 与请求中不匹配

## 参考资料

- `references/index.md`：导航索引
- `references/api.md`：完整 API 参数参考
- `references/examples.md`：多轮 Agent、RAG、批量调用扩展示例

## 维护说明

- 来源：DeepSeek 官方 API 文档、实际工程经验
- 最后更新：2026-05-03
- 已知限制：不包含 DeepSeek 私有化部署配置；多模态接口暂未覆盖

## 质量门控

发布前最低检查项（完整版见元技能 `skills-skills`）：

1. `description` 可判定（"做什么 + 何时用"）且包含触发关键词
2. 包含"何时使用本技能"且触发器可判定
3. 包含"禁止使用 / 边界"以减少误触发
4. 快速参考 <= 20 个模式且每个模式可直接使用
5. 包含 >= 3 个可复现示例（输入 -> 步骤 -> 验收）
6. 长篇内容在 `references/` 中，且有可导航的 `references/index.md`
7. 不确定的内容包含验证路径（禁止吹牛）
8. 快速参考中无文档堆砌
9. 读起来像操作手册，而非知识堆砌
