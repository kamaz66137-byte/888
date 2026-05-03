---
name: headless-cli
description: "DeepSeek CLI 无头模式调用技能：支持通过 Invoke-RestMethod 直接调用 DeepSeek API 及通过 Claude Code 接入 DeepSeek，包含 YOLO 模式和安全模式。适用于 Windows 10 PowerShell 环境。"
---

# DeepSeek Headless CLI 技能

在 Windows 10 PowerShell 中无交互批量调用 DeepSeek，支持直接 API 调用和通过 Claude Code 接入两种方式。

> 运行环境：**Windows 10 / PowerShell 5.1+**

## When to Use This Skill

触发条件：
- 需要批量处理文件（翻译、审查、格式化）
- 需要在脚本中调用 AI 模型
- 需要多模型串联/并联处理
- 需要无人值守的 AI 任务执行

## Not For / Boundaries

不适用于：
- 需要交互式对话的场景
- 需要实时反馈的任务
- 敏感操作（YOLO 模式需谨慎）

必需输入：
- `$env:DEEPSEEK_API_KEY` 已设置
- Node.js 18+ 和 Git for Windows（仅 Claude Code 接入方式需要）
- 网络代理配置（如需）


## Quick Reference

### 🔴 YOLO 模式（通过 Claude Code 接入，全权限）

```powershell
# 1. 配置环境变量（临时，当前会话）
$env:ANTHROPIC_BASE_URL="https://api.deepseek.com/anthropic"
$env:ANTHROPIC_AUTH_TOKEN="<你的 DeepSeek API Key>"
$env:ANTHROPIC_MODEL="deepseek-v4-pro[1m]"
$env:ANTHROPIC_DEFAULT_OPUS_MODEL="deepseek-v4-pro[1m]"
$env:ANTHROPIC_DEFAULT_SONNET_MODEL="deepseek-v4-pro[1m]"
$env:ANTHROPIC_DEFAULT_HAIKU_MODEL="deepseek-v4-flash"
$env:CLAUDE_CODE_SUBAGENT_MODEL="deepseek-v4-flash"
$env:CLAUDE_CODE_EFFORT_LEVEL="max"

# 2. 定义快捷函数
function ds { claude --dangerously-skip-permissions @args }
```

> 持久化（写入用户级，重启后生效）：
> ```powershell
> [System.Environment]::SetEnvironmentVariable("ANTHROPIC_BASE_URL",            "https://api.deepseek.com/anthropic", "User")
> [System.Environment]::SetEnvironmentVariable("ANTHROPIC_AUTH_TOKEN",           "<你的 DeepSeek API Key>",            "User")
> [System.Environment]::SetEnvironmentVariable("ANTHROPIC_MODEL",                "deepseek-v4-pro[1m]",                "User")
> [System.Environment]::SetEnvironmentVariable("ANTHROPIC_DEFAULT_OPUS_MODEL",   "deepseek-v4-pro[1m]",                "User")
> [System.Environment]::SetEnvironmentVariable("ANTHROPIC_DEFAULT_SONNET_MODEL", "deepseek-v4-pro[1m]",                "User")
> [System.Environment]::SetEnvironmentVariable("ANTHROPIC_DEFAULT_HAIKU_MODEL",  "deepseek-v4-flash",                  "User")
> [System.Environment]::SetEnvironmentVariable("CLAUDE_CODE_SUBAGENT_MODEL",     "deepseek-v4-flash",                  "User")
> [System.Environment]::SetEnvironmentVariable("CLAUDE_CODE_EFFORT_LEVEL",       "max",                                "User")
> ```

### 🟢 安全模式（无头但有限制）

**直接调用 API（无需 Claude Code）**
```powershell
$prompt = Get-Content input.md -Raw
$body = @{
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

**通过 Claude Code Print 模式（需配置 ANTHROPIC_* 环境变量）**
```powershell
Get-Content input.md | claude -p "prompt" --output-format text | Set-Content output.md
```

### 📋 常用命令模板

**批量代码审查**
```powershell
# 确保已配置 ANTHROPIC_* 环境变量
Get-ChildItem src\*.ts | ForEach-Object {
    Get-Content $_.FullName | claude -p `
        "Review for bugs, security issues and best practices. Output markdown." `
        --output-format text | Set-Content "review_$($_.BaseName).md"
}
```

**推理模式（复杂分析）**
```powershell
$body = @{
    model            = "deepseek-v4-pro[1m]"
    messages         = @(@{ role = "user"; content = (Get-Content input.md -Raw) })
    thinking         = @{ type = "enabled" }
    reasoning_effort = "high"
    stream           = $false
} | ConvertTo-Json -Depth 5

$headers = @{
    "Content-Type"  = "application/json"
    "Authorization" = "Bearer $env:DEEPSEEK_API_KEY"
}

$resp = Invoke-RestMethod -Uri "https://api.deepseek.com/chat/completions" `
    -Method Post -Headers $headers -Body $body
$resp.choices[0].message.content | Set-Content output.md
```

### ⚙️ 关键参数对照表

| 功能 | DeepSeek (Invoke-RestMethod) | DeepSeek (via Claude Code) |
|:---|:---|:---|
| YOLO 模式 | N/A | `claude --dangerously-skip-permissions` |
| 指定模型 | `model = "deepseek-v4-pro"` | `$env:ANTHROPIC_MODEL="deepseek-v4-pro[1m]"` |
| 非交互输入 | `messages` 数组 | `claude -p "prompt"` |
| 输出捕获 | `$resp.choices[0].message.content` | `--output-format text \| Set-Content` |
| 推理增强 | `thinking=@{type="enabled"}` + `reasoning_effort="high"` | `$env:CLAUDE_CODE_EFFORT_LEVEL="max"` |
| 继续对话 | N/A（无状态） | `-c` / `--continue` |

## Examples

### Example 1: 批量处理文档

**输入**: 多个 Markdown 文件
**步骤**:
```powershell
Get-ChildItem docs\*.md | ForEach-Object {
  $prompt  = Get-Content $_.FullName -Raw
  $body    = @{
    model    = "deepseek-v4-pro"
    messages = @(@{ role = "user"; content = "Translate to English. Keep code fences unchanged.`n`n$prompt" })
    stream   = $false
  } | ConvertTo-Json -Depth 5
  $headers = @{ "Content-Type" = "application/json"; "Authorization" = "Bearer $env:DEEPSEEK_API_KEY" }
  $resp    = Invoke-RestMethod -Uri "https://api.deepseek.com/chat/completions" `
           -Method Post -Headers $headers -Body $body
  $resp.choices[0].message.content | Set-Content "en_$($_.Name)"
}
```
**预期输出**: 翻译后的英文文件

### Example 2: 代码审查（Claude Code + DeepSeek）

**输入**: 源代码文件
**步骤**:
```powershell
# 确保已配置 ANTHROPIC_* 环境变量
Get-ChildItem src\*.py | Get-Content | claude --dangerously-skip-permissions -p `
  "Review for: 1) Bugs 2) Security 3) Performance. Output markdown table." | Set-Content review.md
```
**预期输出**: Markdown 格式的审查报告

### Example 3: 推理模型深度分析

**输入**: 复杂技术问题
**步骤**:
```powershell
$body = @{
  model            = "deepseek-v4-pro[1m]"
  messages         = @(@{ role = "user"; content = (Get-Content question.md -Raw) })
  thinking         = @{ type = "enabled" }
  reasoning_effort = "high"
  stream           = $false
} | ConvertTo-Json -Depth 5

$headers = @{
    "Content-Type"  = "application/json"
    "Authorization" = "Bearer $env:DEEPSEEK_API_KEY"
}

$resp = Invoke-RestMethod -Uri "https://api.deepseek.com/chat/completions" `
    -Method Post -Headers $headers -Body $body
$resp.choices[0].message.content | Set-Content analysis.md
```
**预期输出**: 带推理链的深度分析结果

## References

- `references/deepseek-cli.md` - DeepSeek API 调用参数
- [DeepSeek API 官方文档](https://api-docs.deepseek.com/zh-cn/)
- [DeepSeek 接入 Claude Code 指南](https://api-docs.deepseek.com/zh-cn/quick_start/agent_integrations/claude_code)

## Maintenance

- 来源: DeepSeek 官方文档
- 更新: 2026-05-03
- 限制: 需要网络连接和有效 `DEEPSEEK_API_KEY`；YOLO 模式有安全风险；`deepseek-chat`/`deepseek-reasoner` 将于 2026/07/24 弃用
