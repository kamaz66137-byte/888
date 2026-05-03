"""adapters.schemas.kv — 词典工具 Schema（对应 domains/kv）。"""
from __future__ import annotations

from mcp.types import Tool
from ._base import _tool

HELP_MAP: dict[str, str] = {
    "add/dict": "add/dict(name, value?, tags?, project_id?) -> 新增词典项；project_id 为空写入公共词典。",
    "get/dict": "get/dict(id) -> 获取词典项详情。",
    "get/dict/by-name": "get/dict/by-name(name, scope='auto', project_id?) -> 按名称获取词典项。",
    "list/dict": "list/dict(scope='all', project_id?, query?, limit=20, offset=0) -> 列出词典项。",
    "update/dict": "update/dict(id, name?, value?, tags?, project_id?) -> 更新词典项。",
    "delete/dict": "delete/dict(id) -> 删除词典项。",
}

TOOL_ORDER: list[str] = [
    "add/dict", "get/dict", "get/dict/by-name", "list/dict", "update/dict", "delete/dict",
]

_TAGS_SCHEMA = {
    "anyOf": [
        {"type": "string"},
        {"type": "array", "items": {"type": "string"}},
    ]
}


def build_tools() -> list[Tool]:
    return [
        _tool(
            name="add/dict",
            description="新增词典项（支持公共和项目绑定）",
            x_tags=["dict", "add", "create", "knowledge"],
            properties={
                "name": {"type": "string", "minLength": 1},
                "value": {"type": "string"},
                "tags": _TAGS_SCHEMA,
                "project_id": {"type": "string", "minLength": 1},
            },
            required=["name"],
        ),
        _tool(
            name="get/dict",
            description="按 id 获取词典项详情",
            x_tags=["dict", "get", "detail"],
            properties={"id": {"type": "integer", "minimum": 1}},
            required=["id"],
        ),
        _tool(
            name="get/dict/by-name",
            description="按名称获取词典项（支持 public/project/auto）",
            x_tags=["dict", "get", "name"],
            properties={
                "name": {"type": "string", "minLength": 1},
                "scope": {"type": "string", "enum": ["auto", "public", "project"]},
                "project_id": {"type": "string", "minLength": 1},
            },
            required=["name"],
        ),
        _tool(
            name="list/dict",
            description="列出词典项（支持公共与项目过滤）",
            x_tags=["dict", "list", "browse"],
            properties={
                "scope": {"type": "string", "enum": ["all", "public", "project"]},
                "project_id": {"type": "string", "minLength": 1},
                "query": {"type": "string", "minLength": 1},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                "offset": {"type": "integer", "minimum": 0},
            },
        ),
        _tool(
            name="update/dict",
            description="更新词典项（可切换公共/项目绑定）",
            x_tags=["dict", "update", "edit"],
            properties={
                "id": {"type": "integer", "minimum": 1},
                "name": {"type": "string", "minLength": 1},
                "value": {"type": "string"},
                "tags": _TAGS_SCHEMA,
                "project_id": {
                    "anyOf": [
                        {"type": "string", "minLength": 1},
                        {"type": "null"},
                    ]
                },
            },
            required=["id"],
        ),
        _tool(
            name="delete/dict",
            description="删除词典项",
            x_tags=["dict", "delete", "remove"],
            properties={"id": {"type": "integer", "minimum": 1}},
            required=["id"],
        ),
    ]
