"""adapters.schemas.project — 项目/进度/待办工具 Schema。"""
from __future__ import annotations

from mcp.types import Tool
from ._base import _tool

HELP_MAP: dict[str, str] = {
    "add/project": "add/project(id, name, describe?, location?, environment?, languages?, libraries?, status='active', owner?) -> 新增项目。",
    "update/project": "update/project(id, name?, describe?, location?, environment?, languages?, libraries?, status?, owner?) -> 更新项目。",
    "list/project": "list/project(status='all', limit=20, offset=0) -> 列出项目。",
    "get/project": "get/project(id) -> 获取项目详情。",
    "delete/project": "delete/project(id) -> 删除项目。",
    "add/progress": "add/progress(project_id, name, feature?, context?, status?, priority?, progress?, milestone?) -> 新增进度项。",
    "update/progress": "update/progress(project_id, task_id, name?, feature?, context?, status?, priority?, progress?, milestone?) -> 更新进度项。",
    "list/progress": "list/progress(project_id, status='all', limit=20, offset=0) -> 列出进度项。",
    "stats/progress": "stats/progress(project_id) -> 输出项目进度统计。",
    "add/todo": "add/todo(project_id, name, feature?, context?, step_order?, status?) -> 为项目新增执行步骤。",
    "update/todo": "update/todo(project_id, id, name?, feature?, context?, step_order?, status?) -> 更新执行步骤。",
    "done/todo": "done/todo(project_id, id) -> 将执行步骤标记为 done。",
    "list/todo": "list/todo(project_id, status='all', limit=20, offset=0) -> 列出项目执行步骤。",
    "delete/todo": "delete/todo(project_id, id) -> 删除项目执行步骤。",
    "export/project": "export/project(id) -> 导出项目完整数据为 JSON。",
    "import/project": "import/project(data, overwrite=false) -> 从 JSON 导入项目数据（支持迁移/恢复）。",
}

TOOL_ORDER: list[str] = [
    "add/project", "update/project", "list/project", "get/project", "delete/project",
    "add/progress", "update/progress", "list/progress", "stats/progress",
    "add/todo", "update/todo", "done/todo", "list/todo", "delete/todo",
    "export/project", "import/project",
]

_LANG_LIBS_SCHEMA = {
    "anyOf": [
        {"type": "string"},
        {"type": "array", "items": {"type": "string"}},
    ]
}


def build_tools() -> list[Tool]:
    return [
        _tool(
            name="add/project",
            description="新增项目",
            x_tags=["project", "add", "create"],
            properties={
                "id": {"type": "string", "minLength": 1},
                "name": {"type": "string", "minLength": 1},
                "describe": {"type": "string"},
                "location": {"type": "string"},
                "environment": {"type": "string"},
                "languages": _LANG_LIBS_SCHEMA,
                "libraries": _LANG_LIBS_SCHEMA,
                "status": {"type": "string", "enum": ["active", "paused", "archived"]},
                "owner": {"type": "string"},
            },
            required=["id", "name"],
        ),
        _tool(
            name="update/project",
            description="更新项目",
            x_tags=["project", "update", "edit"],
            properties={
                "id": {"type": "string", "minLength": 1},
                "name": {"type": "string", "minLength": 1},
                "describe": {"type": "string"},
                "location": {"type": "string"},
                "environment": {"type": "string"},
                "languages": _LANG_LIBS_SCHEMA,
                "libraries": _LANG_LIBS_SCHEMA,
                "status": {"type": "string", "enum": ["active", "paused", "archived"]},
                "owner": {"type": "string"},
            },
            required=["id"],
        ),
        _tool(
            name="list/project",
            description="列出项目",
            x_tags=["project", "list", "browse"],
            properties={
                "status": {"type": "string", "enum": ["all", "active", "paused", "archived"]},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                "offset": {"type": "integer", "minimum": 0},
            },
        ),
        _tool(
            name="get/project",
            description="获取项目详情",
            x_tags=["project", "get", "detail"],
            properties={"id": {"type": "string", "minLength": 1}},
            required=["id"],
        ),
        _tool(
            name="delete/project",
            description="删除项目",
            x_tags=["project", "delete", "remove"],
            properties={"id": {"type": "string", "minLength": 1}},
            required=["id"],
        ),
        _tool(
            name="add/progress",
            description="新增项目进度项",
            x_tags=["progress", "add", "create"],
            properties={
                "project_id": {"type": "string", "minLength": 1},
                "name": {"type": "string", "minLength": 1},
                "feature": {"type": "string"},
                "context": {"type": "string"},
                "status": {"type": "string", "enum": ["todo", "doing", "done"]},
                "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                "progress": {"type": "integer", "minimum": 0, "maximum": 100},
                "milestone": {"type": "string"},
            },
            required=["project_id", "name"],
        ),
        _tool(
            name="update/progress",
            description="更新项目进度项",
            x_tags=["progress", "update", "edit"],
            properties={
                "project_id": {"type": "string", "minLength": 1},
                "task_id": {"type": "integer", "minimum": 1},
                "name": {"type": "string", "minLength": 1},
                "feature": {"type": "string"},
                "context": {"type": "string"},
                "status": {"type": "string", "enum": ["todo", "doing", "done"]},
                "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                "progress": {"type": "integer", "minimum": 0, "maximum": 100},
                "milestone": {"type": "string"},
            },
            required=["project_id", "task_id"],
        ),
        _tool(
            name="list/progress",
            description="列出项目进度项",
            x_tags=["progress", "list", "browse"],
            properties={
                "project_id": {"type": "string", "minLength": 1},
                "status": {"type": "string", "enum": ["all", "todo", "doing", "done"]},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                "offset": {"type": "integer", "minimum": 0},
            },
            required=["project_id"],
        ),
        _tool(
            name="stats/progress",
            description="统计项目进度项数量",
            x_tags=["progress", "stats", "summary"],
            properties={"project_id": {"type": "string", "minLength": 1}},
            required=["project_id"],
        ),
        _tool(
            name="add/todo",
            description="为项目新增执行步骤",
            x_tags=["todo", "add", "project"],
            properties={
                "project_id": {"type": "string", "minLength": 1},
                "name": {"type": "string", "minLength": 1},
                "feature": {"type": "string"},
                "context": {"type": "string"},
                "step_order": {"type": "integer", "minimum": 1},
                "status": {"type": "string", "enum": ["todo", "doing", "done"]},
            },
            required=["project_id", "name"],
        ),
        _tool(
            name="update/todo",
            description="更新项目执行步骤",
            x_tags=["todo", "update", "project"],
            properties={
                "project_id": {"type": "string", "minLength": 1},
                "id": {"type": "integer", "minimum": 1},
                "name": {"type": "string", "minLength": 1},
                "feature": {"type": "string"},
                "context": {"type": "string"},
                "step_order": {"type": "integer", "minimum": 1},
                "status": {"type": "string", "enum": ["todo", "doing", "done"]},
            },
            required=["project_id", "id"],
        ),
        _tool(
            name="done/todo",
            description="将项目执行步骤标记为完成",
            x_tags=["todo", "done", "project"],
            properties={
                "project_id": {"type": "string", "minLength": 1},
                "id": {"type": "integer", "minimum": 1},
            },
            required=["project_id", "id"],
        ),
        _tool(
            name="list/todo",
            description="列出项目执行步骤",
            x_tags=["todo", "list", "project"],
            properties={
                "project_id": {"type": "string", "minLength": 1},
                "status": {"type": "string", "enum": ["all", "todo", "doing", "done"]},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                "offset": {"type": "integer", "minimum": 0},
            },
            required=["project_id"],
        ),
        _tool(
            name="delete/todo",
            description="删除项目执行步骤",
            x_tags=["todo", "delete", "project"],
            properties={
                "project_id": {"type": "string", "minLength": 1},
                "id": {"type": "integer", "minimum": 1},
            },
            required=["project_id", "id"],
        ),
        _tool(
            name="export/project",
            description="导出项目完整数据（todos/progress/memory/docs/env/snippets/dict/prompts）为 JSON",
            x_tags=["project", "export", "backup", "migrate"],
            properties={"id": {"type": "string", "minLength": 1}},
            required=["id"],
        ),
        _tool(
            name="import/project",
            description="从 JSON 导入项目数据，支持迁移与备份恢复；传 overwrite=true 允许覆盖已有项目",
            x_tags=["project", "import", "restore", "migrate"],
            properties={
                "data": {"type": "string", "minLength": 1, "description": "export/project 返回的 JSON 字符串"},
                "overwrite": {"type": "boolean", "description": "是否覆盖同 id 的已有项目", "default": False},
            },
            required=["data"],
        ),
    ]
