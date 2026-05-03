"""adapters.schemas.task — 任务工具 Schema。"""
from __future__ import annotations

from mcp.types import Tool
from ._base import _tool

HELP_MAP: dict[str, str] = {
    "task_add": "task_add(name, description?, priority?, due_date?) -> 新增任务。",
    "task_list": "task_list(status='all', priority='all', limit=20, offset=0) -> 分页筛选任务。",
    "task_update": "task_update(id, name?, description?, status?, priority?, due_date?) -> 更新任务。",
    "task_done": "task_done(id) -> 快速标记任务为 done。",
    "task_delete": "task_delete(id) -> 删除任务。",
    "task_stats": "task_stats() -> 输出 total/todo/doing/done 统计。",
}

TOOL_ORDER: list[str] = [
    "task_add", "task_list", "task_update", "task_done", "task_delete", "task_stats",
]


def build_tools() -> list[Tool]:
    return [
        _tool(
            name="task_add",
            description="新增任务",
            x_tags=["task", "add", "create", "todo"],
            properties={
                "name": {"type": "string", "minLength": 1},
                "description": {"type": "string"},
                "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                "due_date": {"type": "string", "description": "截止日期，建议格式 YYYY-MM-DD"},
            },
            required=["name"],
        ),
        _tool(
            name="task_list",
            description="列出任务，可按状态和优先级过滤",
            x_tags=["task", "list", "browse", "filter"],
            properties={
                "status": {"type": "string", "enum": ["all", "todo", "doing", "done"]},
                "priority": {"type": "string", "enum": ["all", "low", "medium", "high"]},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                "offset": {"type": "integer", "minimum": 0},
            },
        ),
        _tool(
            name="task_update",
            description="更新任务（名称/描述/状态/优先级/截止日期）",
            x_tags=["task", "update", "edit", "modify"],
            properties={
                "id": {"type": "integer", "minimum": 1},
                "name": {"type": "string", "minLength": 1},
                "description": {"type": "string"},
                "status": {"type": "string", "enum": ["todo", "doing", "done"]},
                "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                "due_date": {"type": ["string", "null"], "description": "传 null 可清空截止日期"},
            },
            required=["id"],
        ),
        _tool(
            name="task_done",
            description="将任务标记为 done",
            x_tags=["task", "done", "complete", "finish"],
            properties={"id": {"type": "integer", "minimum": 1}},
            required=["id"],
        ),
        _tool(
            name="task_delete",
            description="删除任务",
            x_tags=["task", "delete", "remove"],
            properties={"id": {"type": "integer", "minimum": 1}},
            required=["id"],
        ),
        _tool(
            name="task_stats",
            description="统计任务总数与各状态数量",
            x_tags=["task", "stats", "summary", "count"],
            properties={},
        ),
    ]
