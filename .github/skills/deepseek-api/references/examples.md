# 扩展示例

## 多轮 Agent（Python）

完整的多轮对话 + 工具循环：

```python
import json
from openai import OpenAI

client = OpenAI(api_key="...", base_url="https://api.deepseek.com")

def run_agent(user_input: str):
    messages = [{"role": "user", "content": user_input}]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "获取城市当前天气",
                "parameters": {
                    "type": "object",
                    "properties": {"city": {"type": "string"}},
                    "required": ["city"]
                }
            }
        }
    ]

    for _ in range(5):  # 最多 5 轮工具调用
        resp = client.chat.completions.create(
            model="deepseek-v4-pro",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        choice = resp.choices[0]
        messages.append(choice.message)

        if choice.finish_reason != "tool_calls":
            return choice.message.content

        for tc in choice.message.tool_calls:
            args = json.loads(tc.function.arguments)
            result = f"{args['city']}：晴，25°C"
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result
            })

    return "达到最大工具调用轮次"

print(run_agent("北京和上海今天哪里更热？"))
```

## 流式 + 指数退避重试（Python）

```python
import time
from openai import OpenAI, RateLimitError

client = OpenAI(api_key="...", base_url="https://api.deepseek.com")

def stream_with_retry(prompt: str, retries: int = 3):
    for attempt in range(retries):
        try:
            stream = client.chat.completions.create(
                model="deepseek-v4-flash",
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    print(content, end="", flush=True)
            print()
            return
        except RateLimitError:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # 1s, 2s, 4s
            else:
                raise

stream_with_retry("写一篇关于 AI 的短文")
```

## 强制 JSON 输出

```python
resp = client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=[
        {"role": "system", "content": "你只输出合法 JSON"},
        {"role": "user", "content": "返回包含 name 和 age 字段的 JSON"}
    ],
    response_format={"type": "json_object"}
)
import json
data = json.loads(resp.choices[0].message.content)
print(data)
```

## PowerShell：工具调用（Windows 10）

```powershell
$headers = @{
    "Authorization" = "Bearer $env:DEEPSEEK_API_KEY"
    "Content-Type"  = "application/json"
}

$tool = @{
    type     = "function"
    function = @{
        name        = "get_time"
        description = "获取当前时间"
        parameters  = @{ type = "object"; properties = @{}; required = @() }
    }
}

$body = @{
    model       = "deepseek-v4-flash"
    messages    = @(@{ role = "user"; content = "现在几点了？" })
    tools       = @($tool)
    tool_choice = "auto"
} | ConvertTo-Json -Depth 10

$resp = Invoke-RestMethod -Uri "https://api.deepseek.com/chat/completions" `
    -Method Post -Headers $headers -Body $body

$choice = $resp.choices[0]
if ($choice.finish_reason -eq "tool_calls") {
    Write-Host "需要调用工具：$($choice.message.tool_calls[0].function.name)"
} else {
    Write-Host $choice.message.content
}
```
�?
完整的多轮对�?+ 工具循环�?
```python
import json
from openai import OpenAI

client = OpenAI(api_key="...", base_url="https://api.deepseek.com")

def run_agent(user_input: str):
    messages = [{"role": "user", "content": user_input}]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "获取城市当前天气",
                "parameters": {
                    "type": "object",
                    "properties": {"city": {"type": "string"}},
                    "required": ["city"]
                }
            }
        }
    ]

    for _ in range(5):  # 最�?5 轮工具调�?        resp = client.chat.completions.create(
            model="deepseek-v4-pro",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        choice = resp.choices[0]
        messages.append(choice.message)

        if choice.finish_reason != "tool_calls":
            return choice.message.content

        for tc in choice.message.tool_calls:
            args = json.loads(tc.function.arguments)
            # 模拟工具执行
            result = f"{args['city']}：晴�?5°C"
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result
            })

    return "达到最大工具调用轮�?

print(run_agent("北京和上海今天哪里更热？"))
```

## 流式 + 指数退避重试（Python�?
```python
import time
from openai import OpenAI, RateLimitError

client = OpenAI(api_key="...", base_url="https://api.deepseek.com")

def stream_with_retry(prompt: str, retries: int = 3):
    for attempt in range(retries):
        try:
            stream = client.chat.completions.create(
                model="deepseek-v4-flash",
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    print(content, end="", flush=True)
            print()
            return
        except RateLimitError:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # 1s, 2s, 4s
            else:
                raise

stream_with_retry("写一篇关�?AI 的短�?)
```

## 强制 JSON 输出

```python
resp = client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=[
        {"role": "system", "content": "你只输出合法 JSON"},
        {"role": "user", "content": "返回包含 name �?age 字段�?JSON"}
    ],
    response_format={"type": "json_object"}
)
import json
data = json.loads(resp.choices[0].message.content)
print(data)
```

## PowerShell：工具调用（Windows 10�?
```powershell
$headers = @{
    "Authorization" = "Bearer $env:DEEPSEEK_API_KEY"
    "Content-Type"  = "application/json"
}

$tool = @{
    type     = "function"
    function = @{
        name        = "get_time"
        description = "获取当前时间"
        parameters  = @{ type = "object"; properties = @{}; required = @() }
    }
}

$body = @{
    model       = "deepseek-v4-flash"
    messages    = @(@{ role = "user"; content = "现在几点了？" })
    tools       = @($tool)
    tool_choice = "auto"
} | ConvertTo-Json -Depth 10

$resp = Invoke-RestMethod -Uri "https://api.deepseek.com/chat/completions" `
    -Method Post -Headers $headers -Body $body

$choice = $resp.choices[0]
if ($choice.finish_reason -eq "tool_calls") {
    Write-Host "需要调用工具：$($choice.message.tool_calls[0].function.name)"
} else {
    Write-Host $choice.message.content
}
```
