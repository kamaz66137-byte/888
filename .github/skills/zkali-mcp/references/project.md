# project.md — 项目模块与进度标准

## 1. 目标

- 管理多项目上下文
- 统一项目状态和进度
- 为记忆隔离提供 project_id 主键

---

## 2. project 基础模型

```json
{
  "id": "proj-001",
  "name": "zkali-mcp-core",
  "status": "active",
  "owner": "team-a",
  "created_at": "2026-05-03 10:00:00",
  "updated_at": "2026-05-03 12:00:00"
}
```

状态枚举：`active` / `paused` / `archived`

---

## 3. 进度模型

```json
{
  "project_id": "proj-001",
  "task_id": 1001,
  "title": "实现 discover/tool",
  "status": "todo",
  "priority": "high",
  "progress": 0,
  "milestone": "M1",
  "updated_at": "2026-05-03 12:00:00"
}
```

约束：

- `status`：`todo` / `doing` / `done`
- `progress`：0~100
- `project_id` 必填

---

## 4. 工具建议

- `add/project`
- `update/project`
- `list/project`
- `get/project`
- `add/progress`
- `update/progress`
- `list/progress`
- `stats/progress`

---

## 5. 与 memory 的关系

- memory 写入前必须校验 project 是否存在且为 active
- project archived 后默认禁止新写入 memory
- 删除项目需要明确策略：软删除或归档，不建议物理删除
