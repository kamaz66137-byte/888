"""adapters.schemas.memory — 记忆工具 Schema。"""
from __future__ import annotations

from mcp.types import Tool
from ._base import _tool

HELP_MAP: dict[str, str] = {
    "add/memory": "add/memory(project_id, key, value, scope='project', namespace='default', ttl_seconds?) -> 写入记忆。",
    "get/memory": "get/memory(project_id, key, scope='project', namespace='default') -> 获取单条记忆。",
    "list/memory": "list/memory(project_id, scope='all', namespace?, limit=20, offset=0) -> 列出记忆。",
    "update/memory": "update/memory(project_id, key, value, scope='project', namespace='default', ttl_seconds?) -> 更新记忆。",
    "delete/memory": "delete/memory(project_id, key, scope='project', namespace='default') -> 删除记忆。",
    "clear/memory": "clear/memory(project_id, scope='session') -> 清理某 scope 的记忆。",
    "cleanup/expired": "cleanup/expired() -> 清理已过期的记忆（ttl_seconds 到期），返回删除数量。",
}

TOOL_ORDER: list[str] = [
    "add/memory", "get/memory", "list/memory", "update/memory",
    "delete/memory", "clear/memory", "cleanup/expired",
]


def build_tools() -> list[Tool]:
    return [
        _tool(
            name="add/memory",
            description="新增项目记忆",
            x_tags=["memory", "add", "create"],
            properties={
                "project_id": {"type": "string", "minLength": 1},
                "scope": {"type": "string", "enum": ["session", "project", "global"]},
                "namespace": {"type": "string"},
                "key": {"type": "string", "minLength": 1},
                "value": {"type": "string"},
                "ttl_seconds": {"type": "integer", "minimum": 1},
            },
            required=["project_id", "key", "value"],
        ),
        _tool(
            name="get/memory",
            description="获取单条项目记忆",
            x_tags=["memory", "get", "detail"],
            properties={
                "project_id": {"type": "string", "minLength": 1},
                "scope": {"type": "string", "enum": ["session", "project", "global"]},
                "namespace": {"type": "string"},
                "key": {"type": "string", "minLength": 1},
            },
            required=["project_id", "key"],
        ),
        _tool(
            name="list/memory",
            description="列出项目记忆",
            x_tags=["memory", "list", "browse"],
            properties={
                "project_id": {"type": "string", "minLength": 1},
                "scope": {"type": "string", "enum": ["all", "session", "project", "global"]},
                "namespace": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                "offset": {"type": "integer", "minimum": 0},
            },
            required=["project_id"],
        ),
        _tool(
            name="update/memory",
            description="更新项目记忆",
            x_tags=["memory", "update", "edit"],
            properties={
                "project_id": {"type": "string", "minLength": 1},
                "scope": {"type": "string", "enum": ["session", "project", "global"]},
                "namespace": {"type": "string"},
                "key": {"type": "string", "minLength": 1},
                "value": {"type": "string"},
                "ttl_seconds": {"type": "integer", "minimum": 1},
            },
            required=["project_id", "key", "value"],
        ),
        _tool(
            name="delete/memory",
            description="删除项目记忆",
            x_tags=["memory", "delete", "remove"],
            properties={
                "project_id": {"type": "string", "minLength": 1},
                "scope": {"type": "string", "enum": ["session", "project", "global"]},
                "namespace": {"type": "string"},
                "key": {"type": "string", "minLength": 1},
            },
            required=["project_id", "key"],
        ),
        _tool(
            name="clear/memory",
            description="清理某个 scope 的项目记忆",
            x_tags=["memory", "clear", "cleanup"],
            properties={
                "project_id": {"type": "string", "minLength": 1},
                "scope": {"type": "string", "enum": ["session", "project", "global"]},
            },
            required=["project_id"],
        ),
        _tool(
            name="cleanup/expired",
            description="清理已过期的记忆（ttl_seconds 到期），返回删除数量",
            x_tags=["memory", "cleanup", "expired", "ttl"],
            properties={},
        ),
    ]
