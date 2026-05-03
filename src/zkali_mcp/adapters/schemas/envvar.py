"""adapters.schemas.envvar — 环境变量工具 Schema（对应 domains/envvar）。"""
from __future__ import annotations

from mcp.types import Tool
from ._base import _tool

HELP_MAP: dict[str, str] = {
    "set/env": "set/env(project_id, key, value?, description?) -> 写入/覆盖项目环境变量。",
    "get/env": "get/env(project_id, key) -> 获取单个项目环境变量。",
    "list/env": "list/env(project_id, limit=50, offset=0) -> 列出项目所有环境变量。",
    "delete/env": "delete/env(project_id, key) -> 删除项目环境变量。",
}

TOOL_ORDER: list[str] = ["set/env", "get/env", "list/env", "delete/env"]


def build_tools() -> list[Tool]:
    return [
        _tool(
            name="set/env",
            description="写入/覆盖项目环境变量（同 key 自动覆盖）",
            x_tags=["env", "set", "config", "project"],
            properties={
                "project_id": {"type": "string", "minLength": 1},
                "key": {"type": "string", "minLength": 1},
                "value": {"type": "string"},
                "description": {"type": "string"},
            },
            required=["project_id", "key"],
        ),
        _tool(
            name="get/env",
            description="获取单个项目环境变量",
            x_tags=["env", "get", "config"],
            properties={
                "project_id": {"type": "string", "minLength": 1},
                "key": {"type": "string", "minLength": 1},
            },
            required=["project_id", "key"],
        ),
        _tool(
            name="list/env",
            description="列出项目所有环境变量",
            x_tags=["env", "list", "config"],
            properties={
                "project_id": {"type": "string", "minLength": 1},
                "limit": {"type": "integer", "minimum": 1, "maximum": 200},
                "offset": {"type": "integer", "minimum": 0},
            },
            required=["project_id"],
        ),
        _tool(
            name="delete/env",
            description="删除项目环境变量",
            x_tags=["env", "delete", "config"],
            properties={
                "project_id": {"type": "string", "minLength": 1},
                "key": {"type": "string", "minLength": 1},
            },
            required=["project_id", "key"],
        ),
    ]
