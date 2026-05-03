# DeepSeek API 完整参数参考

## 端点

| 兼容协议 | Base URL |
|---------|---------|
| OpenAI  | `https://api.deepseek.com` |
| Anthropic | `https://api.deepseek.com/anthropic` |

## 模型

| 模型名 | 特点 | 适用场景 |
|--------|------|---------|
| `deepseek-v4-flash` | 低延迟、低成本 | 单轮问答、代码补全、快速 Agent |
| `deepseek-v4-pro` | 强推理、支持 1M 上下文 | 复杂推理、多步 Agent、长文档分析 |
| `deepseek-v4-pro[1m]` | 同 pro，1M 上下文窗口 | 超长文档、大型代码库 |

> ⚠️ `deepseek-chat` / `deepseek-reasoner` 已弃用（2026-07-24），会报 400 错误。

## Chat Completions 参数

```
POST /chat/completions
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `model` | string | 必填 | 模型名 |
| `messages` | array | 必填 | 对话历史，含 system/user/assistant/tool |
| `tools` | array | 可选 | 工具列表（function calling） |
| `tool_choice` | string/object | `"auto"` | `"auto"` / `"none"` / `{"type":"function","function":{"name":"..."}}` |
| `stream` | bool | `false` | 是否流式输出 |
| `temperature` | float | `1.0` | 0-2，越高越随机 |
| `max_tokens` | int | 模型上限 | 最大输出 token 数 |
| `top_p` | float | `1.0` | nucleus sampling |
| `response_format` | object | 可选 | `{"type": "json_object"}` 强制 JSON 输出 |

## 消息角色

| role | 用途 |
|------|------|
| `system` | 系统指令（人格、规则） |
| `user` | 用户输入 |
| `assistant` | 模型回复（含 tool_calls） |
| `tool` | 工具执行结果（需含 `tool_call_id`） |

## 工具调用完整流程

```python
# 1. 定义工具
tools = [{
    "type": "function",
    "function": {
        "name": "search",
        "description": "搜索互联网",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "搜索词"}
            },
            "required": ["query"]
        }
    }
}]

# 2. 第一次调用
resp = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

# 3. 检查是否需要工具
msg = resp.choices[0].message
if resp.choices[0].finish_reason == "tool_calls":
    # 4. 执行工具
    for tc in msg.tool_calls:
        args = json.loads(tc.function.arguments)
        result = do_search(args["query"])  # 你的实现
        messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

    # 5. 再次调用获取最终答案
    final = client.chat.completions.create(model="deepseek-v4-pro", messages=messages)
    print(final.choices[0].message.content)
```

## 错误码

| HTTP 状态 | 含义 | 处理方式 |
|-----------|------|---------|
| 400 | 参数错误 / 模型已弃用 | 检查模型名和请求体 |
| 401 | API Key 无效 | 检查 `DEEPSEEK_API_KEY` 环境变量 |
| 429 | 限流 | 指数退避重试（1s → 2s → 4s，最多 3 次） |
| 500/503 | 服务端错误 | 重试，持续失败则上报 |
�?
## 端点

| 兼容协议 | Base URL |
|---------|---------|
| OpenAI  | `https://api.deepseek.com` |
| Anthropic | `https://api.deepseek.com/anthropic` |

## 模型

| 模型�?| 特点 | 适用场景 |
|--------|------|---------|
| `deepseek-v4-flash` | 低延迟、低成本 | 单轮问答、代码补全、快�?Agent |
| `deepseek-v4-pro` | 强推理、支�?1M 上下�?| 复杂推理、多�?Agent、长文档分析 |
| `deepseek-v4-pro[1m]` | �?pro�?M 上下文窗�?| 超长文档、大型代码库 |

> ⚠️ `deepseek-chat` / `deepseek-reasoner` 已弃用（2026-07-24），会报 400 错误�?
## Chat Completions 参数

```
POST /v1/chat/completions
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `model` | string | 必填 | 模型�?|
| `messages` | array | 必填 | 对话历史，含 system/user/assistant/tool |
| `tools` | array | 可�?| 工具列表（function calling�?|
| `tool_choice` | string/object | `"auto"` | `"auto"` / `"none"` / `{"type":"function","function":{"name":"..."}}` |
| `stream` | bool | `false` | 是否流式输出 |
| `temperature` | float | `1.0` | 0-2，越高越随机 |
| `max_tokens` | int | 模型上限 | 最大输�?token �?|
| `top_p` | float | `1.0` | nucleus sampling |
| `response_format` | object | 可�?| `{"type": "json_object"}` 强制 JSON 输出 |

## 消息角色

| role | 用�?|
|------|------|
| `system` | 系统指令（人格、规则） |
| `user` | 用户输入 |
| `assistant` | 模型回复（含 tool_calls�?|
| `tool` | 工具执行结果（需�?`tool_call_id`�?|

## 工具调用完整流程

```python
# 1. 定义工具
tools = [{
    "type": "function",
    "function": {
        "name": "search",
        "description": "搜索互联�?,
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "搜索�?}
            },
            "required": ["query"]
        }
    }
}]

# 2. 第一次调�?resp = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

# 3. 检查是否需要工�?msg = resp.choices[0].message
if resp.choices[0].finish_reason == "tool_calls":
    # 4. 执行工具
    for tc in msg.tool_calls:
        args = json.loads(tc.function.arguments)
        result = do_search(args["query"])  # 你的实现
        messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

    # 5. 再次调用获取最终答�?    final = client.chat.completions.create(model="deepseek-v4-pro", messages=messages)
    print(final.choices[0].message.content)
```

## 错误�?
| HTTP 状�?| 含义 | 处理方式 |
|-----------|------|---------|
| 400 | 参数错误 / 模型已弃�?| 检查模型名和请求体 |
| 401 | API Key 无效 | 检�?`DEEPSEEK_API_KEY` 环境变量 |
| 429 | 限流 | 指数退避重试（1s �?2s �?4s，最�?3 次） |
| 500/503 | 服务端错�?| 重试，持续失败则上报 |
