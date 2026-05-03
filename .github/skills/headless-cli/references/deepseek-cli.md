# DeepSeek API CLI 参考

> ⚠️ 以下参数基于官方文档，请以 [DeepSeek API 官方文档](https://api-docs.deepseek.com/zh-cn/) 为准
>
> 运行环境：**Windows 10 / PowerShell 5.1+**

## 接入方式

DeepSeek 提供两种兼容格式的 API 接入：

| 方式 | base_url | 说明 |
|:---|:---|:---|
| OpenAI 兼容格式 | `https://api.deepseek.com` | 使用 OpenAI SDK 或 curl |
| Anthropic 兼容格式 | `https://api.deepseek.com/anthropic` | 用于 Claude Code 等 Anthropic 工具 |

## 当前模型

> `deepseek-chat` / `deepseek-reasoner` 将于 **2026/07/24 弃用**，请使用以下新模型名：

| 模型 | 说明 | 推荐场景 |
|:---|:---|:---|
| `deepseek-v4-flash` | 快速响应，低成本 | 批量任务、子智能体 |
| `deepseek-v4-pro` | 高质量输出 | 代码审查、生成 |
| `deepseek-v4-pro[1m]` | 带推理（thinking）模式，100万 token 上下文 | 复杂分析、架构设计 |

## Invoke-RestMethod 调用（PowerShell 原生）

### 基础对话（非流式）
```powershell
$body = @{
    model    = "deepseek-v4-pro"
    messages = @(
        @{ role = "system"; content = "You are a helpful assistant." }
        @{ role = "user";   content = "Your prompt here" }
    )
    stream = $false
} | ConvertTo-Json -Depth 5

$headers = @{
    "Content-Type"  = "application/json"
    "Authorization" = "Bearer $env:DEEPSEEK_API_KEY"
}

$resp = Invoke-RestMethod -Uri "https://api.deepseek.com/chat/completions" `
    -Method Post -Headers $headers -Body $body
$resp.choices[0].message.content
```

### 推理模式（thinking，需使用 `[1m]` 后缀模型）
```powershell
$body = @{
    model    = "deepseek-v4-pro[1m]"
    messages = @(@{ role = "user"; content = "Your complex question" })
    thinking         = @{ type = "enabled" }
    reasoning_effort = "high"
    stream   = $false
} | ConvertTo-Json -Depth 5

$headers = @{
    "Content-Type"  = "application/json"
    "Authorization" = "Bearer $env:DEEPSEEK_API_KEY"
}

$resp = Invoke-RestMethod -Uri "https://api.deepseek.com/chat/completions" `
    -Method Post -Headers $headers -Body $body
$resp.choices[0].message.content | Set-Content output.md
```

### 从文件读取 Prompt 并输出
```powershell
$prompt  = Get-Content input.md -Raw
$body    = @{
    model    = "deepseek-v4-pro"
    messages = @(@{ role = "user"; content = $prompt })
    stream   = $false
} | ConvertTo-Json -Depth 5

$headers = @{
    "Content-Type"  = "application/json"
    "Authorization" = "Bearer $env:DEEPSEEK_API_KEY"
}

$resp = Invoke-RestMethod -Uri "https://api.deepseek.com/chat/completions" `
    -Method Post -Headers $headers -Body $body
$resp.choices[0].message.content | Set-Content output.md
```

## 通过 Claude Code 接入 DeepSeek

Claude Code 支持将 DeepSeek 作为后端模型（Anthropic 兼容格式）。

### 环境变量配置（PowerShell）

**当前会话（临时）**
```powershell
$env:ANTHROPIC_BASE_URL="https://api.deepseek.com/anthropic"
$env:ANTHROPIC_AUTH_TOKEN="<你的 DeepSeek API Key>"
$env:ANTHROPIC_MODEL="deepseek-v4-pro[1m]"
$env:ANTHROPIC_DEFAULT_OPUS_MODEL="deepseek-v4-pro[1m]"
$env:ANTHROPIC_DEFAULT_SONNET_MODEL="deepseek-v4-pro[1m]"
$env:ANTHROPIC_DEFAULT_HAIKU_MODEL="deepseek-v4-flash"
$env:CLAUDE_CODE_SUBAGENT_MODEL="deepseek-v4-flash"
$env:CLAUDE_CODE_EFFORT_LEVEL="max"
```

**持久化配置（用户级，重启后生效）**
```powershell
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_BASE_URL",      "https://api.deepseek.com/anthropic", "User")
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_AUTH_TOKEN",     "<你的 DeepSeek API Key>",            "User")
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_MODEL",          "deepseek-v4-pro[1m]",                "User")
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_DEFAULT_OPUS_MODEL",   "deepseek-v4-pro[1m]",   "User")
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_DEFAULT_SONNET_MODEL", "deepseek-v4-pro[1m]",   "User")
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_DEFAULT_HAIKU_MODEL",  "deepseek-v4-flash",     "User")
[System.Environment]::SetEnvironmentVariable("CLAUDE_CODE_SUBAGENT_MODEL",     "deepseek-v4-flash",     "User")
[System.Environment]::SetEnvironmentVariable("CLAUDE_CODE_EFFORT_LEVEL",       "max",                   "User")
```

### 无头模式调用（配置环境变量后）
```powershell
# Print 模式（安全，无工具权限）
Get-Content input.md | claude -p "prompt" --output-format text | Set-Content output.md

# YOLO 模式（全权限，跳过确认）
claude --dangerously-skip-permissions "prompt"
```

## 关键请求参数

| 参数 | 类型 | 说明 |
|:---|:---|:---|
| `model` | string | 必填，见模型列表 |
| `messages` | array | 必填，对话历史 |
| `stream` | boolean | `false` 为非流式输出，适合脚本 |
| `thinking.type` | string | `"enabled"` 启用推理（仅 `[1m]` 模型） |
| `reasoning_effort` | string | `"high"` / `"medium"` / `"low"` |
| `max_tokens` | integer | 最大输出 token 数 |
| `temperature` | float | 0-2，默认 1 |

## 官方文档链接

- [首次调用 API](https://api-docs.deepseek.com/zh-cn/)
- [接入 Claude Code](https://api-docs.deepseek.com/zh-cn/quick_start/agent_integrations/claude_code)
- [模型与价格](https://api-docs.deepseek.com/zh-cn/quick_start/pricing)
- [错误码](https://api-docs.deepseek.com/zh-cn/quick_start/error_codes)
