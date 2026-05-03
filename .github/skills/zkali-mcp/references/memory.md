# memory.md — 记忆模块与项目隔离标准

## 1. 隔离目标

- 支持多项目并行
- 避免跨项目污染
- 支持会话级和项目级记忆

---

## 2. 记忆分层

- session：当前会话临时记忆
- project：项目持久记忆
- global：全局只读参考（可选，默认不写）

默认读取顺序：session -> project -> global

---

## 3. 存储模型

```json
{
  "id": 1,
  "project_id": "proj-001",
  "scope": "project",
  "namespace": "tool-discovery",
  "key": "preferred_tags",
  "value": ["search", "docs"],
  "created_at": "2026-05-03 10:00:00",
  "updated_at": "2026-05-03 12:00:00"
}
```

必填字段：

- `project_id`
- `scope`
- `key`
- `value`

---

## 4. 隔离规则（必须）

- 所有写入接口必须要求 `project_id`
- 所有查询接口必须按 `project_id` 过滤
- 所有删除接口必须按 `project_id + key` 限定
- 禁止默认查询全项目数据

---

## 5. 推荐工具

- `add/memory`
- `get/memory`
- `list/memory`
- `update/memory`
- `delete/memory`
- `clear/memory`（仅 session）

---

## 6. 安全与清理

- 不写入密钥、token、密码
- 支持 TTL 字段（可选）
- 定期清理过期 session 记忆
