# 故障排查与边界情况

## 常见错误

### 需求要求使用 MySQL/PostgreSQL/Redis/MongoDB
- 原因：与本技能边界冲突（本技能仅支持 sqlite3）
- 修复：将需求收敛为 sqlite3 实现；若必须使用其它数据库，应切换到非本技能方案

### `ModuleNotFoundError: No module named 'mcp'`
- 原因：未安装 mcp 包，或 Python 环境不对
- 修复：
  ```bash
  pip install mcp
  # 确认用的是同一 Python
  python -c "import mcp; print(mcp.__file__)"
  ```

### `ModuleNotFoundError: No module named 'mcp.server.stdio'`
- 原因：mcp 版本过旧（< 1.0）
- 修复：`pip install --upgrade mcp`

### `TypeError: object NoneType can't be used in 'await' expression`
- 原因：`@app.list_tools()` 装饰的函数未声明为 `async def`
- 修复：所有注册函数必须是 `async def`

### `sqlite3.OperationalError: database is locked`
- 原因：多进程同时写入，或长事务未提交
- 修复：
  ```python
  conn.execute("PRAGMA journal_mode=WAL")
  conn.execute("PRAGMA busy_timeout=5000")  # 等待 5s 再报错
  ```

### `sqlite3.IntegrityError: UNIQUE constraint failed`
- 原因：插入了重复的唯一字段值
- 修复：
  ```python
  # INSERT OR IGNORE（忽略重复）
  conn.execute("INSERT OR IGNORE INTO t (name) VALUES (?)", (name,))
  # INSERT OR REPLACE（覆盖重复）
  conn.execute("INSERT OR REPLACE INTO t (name, val) VALUES (?,?)", (name, val))
  ```

### 工具不出现在 Claude / Copilot 中
- 诊断步骤：
  1. `python main.py` 直接运行，确认无 Python 报错
  2. 检查 `.vscode/mcp.json` 的 `command`/`args` 路径是否正确
  3. 用 `mcp dev main.py` 或 MCP Inspector 验证工具列表
  4. 重启 VS Code 或 Claude Code

### 工具调用超时
- 原因：handler 中有同步阻塞操作（大量 I/O、网络请求）
- 修复：
  ```python
  result = await asyncio.to_thread(blocking_function, arg1, arg2)
  ```

### `ValueError: Unknown tool: xxx`
- 原因：`call_tool` 中缺少对该工具名的处理分支
- 修复：确认 `list_tools` 返回的 `name` 与 `call_tool` 中的判断字符串一致

---

## sqlite3 安全边界

### SQL 注入（必须参数化）

```python
# ❌ 危险 - 字符串拼接
conn.execute(f"SELECT * FROM t WHERE name = '{user_input}'")

# ✅ 安全 - 参数化
conn.execute("SELECT * FROM t WHERE name = ?", (user_input,))
```

### DB 文件路径

```python
# ✅ 推荐 - 相对脚本位置
DB = Path(__file__).parent / "app.db"

# ❌ 避免 - 相对 cwd（cwd 依赖调用方式）
DB = Path("app.db")
```

### DB 文件加入 .gitignore

```gitignore
# MCP Server 数据库
*.db
*.sqlite
*.sqlite3
```

---

## 协议边界

- MCP 客户端不强制执行 `inputSchema` 的 `additionalProperties` 和 `enum` 约束，handler 内需自行验证
- `list_tools` 在每次连接时调用，**不会缓存**（可动态更新工具列表）
- `stdio` 传输：stdout 只能用于 MCP 协议数据，**不能** `print()` 到 stdout（会污染协议）；调试日志必须写 stderr
  ```python
  import sys
  print("DEBUG: ...", file=sys.stderr)
  ```
- Server 崩溃后客户端会断开连接，需保证 handler 内所有异常都被捕获并返回错误 TextContent，而非抛出到顶层
