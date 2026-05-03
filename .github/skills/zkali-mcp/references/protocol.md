# protocol.md — 统一错误处理、响应、契约协议

## 1. 目标

- 所有工具输出统一格式
- 所有错误统一编码和可读消息
- 所有异常统一降级为协议错误

---

## 2. 响应标准

### 2.1 文本模式（兼容现有工具）

- 成功：`OK ...`
- 失败：`ERR <CODE> <message>`

示例：

```text
OK id=12
ERR ERR_NOT_FOUND tool not found: search/docs
```

### 2.2 JSON 模式（推荐）

```json
{
  "ok": true,
  "code": "OK",
  "message": "updated",
  "data": {}
}
```

```json
{
  "ok": false,
  "code": "ERR_VALIDATION",
  "message": "name is required",
  "detail": {"field": "name"}
}
```

---

## 3. 错误码标准

| code | 语义 | HTTP 对齐参考 |
|------|------|---------------|
| ERR_VALIDATION | 参数校验失败 | 400 |
| ERR_NOT_FOUND | 资源不存在 | 404 |
| ERR_CONFLICT | 资源冲突（重复 name） | 409 |
| ERR_FORBIDDEN | 禁止访问 | 403 |
| ERR_INTERNAL | 内部错误 | 500 |

---

## 4. 协议构造器建议

```python
def ok(message: str = "OK", data: dict | None = None) -> dict: ...
def err(code: str, message: str, detail: dict | None = None) -> dict: ...
def validate_error(field: str, reason: str) -> dict: ...
def not_found(entity: str, key: str) -> dict: ...
```

---

## 5. 工具契约映射

- input_schema：请求参数契约
- output_schema：返回参数契约
- content.returns：返回说明示例
- protocol.err：统一错误口径

当 `content` 与 `output_schema` 冲突时，以 `output_schema` 为准。

---

## 6. 与现有 _contract.py 的关系

- `_contract.py` 负责工具文本输出约束
- `protocol.md` 负责跨模块统一协议模型
- 演进路径：文本模式 -> 文本+JSON 双模式 -> JSON 主模式
