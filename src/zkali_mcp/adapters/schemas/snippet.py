"""adapters.schemas.snippet — 代码/文本片段工具 Schema。"""
from __future__ import annotations

from mcp.types import Tool
from ._base import _tool

HELP_MAP: dict[str, str] = {
    "add/snippet": "add/snippet(name, language?, content?, tags?, project_id?) -> 新增代码片段；project_id 为空写入公共片段库。",
    "get/snippet": "get/snippet(id) -> 获取片段详情。",
    "list/snippet": "list/snippet(scope='all', project_id?, language?, limit=20, offset=0) -> 列出代码片段。",
    "search/snippet": "search/snippet(query, limit=20, offset=0) -> 搜索代码片段。",
    "update/snippet": "update/snippet(id, name?, language?, content?, tags?) -> 更新代码片段。",
    "delete/snippet": "delete/snippet(id) -> 删除代码片段。",
}

TOOL_ORDER: list[str] = [
    "add/snippet", "get/snippet", "list/snippet", "search/snippet",
    "update/snippet", "delete/snippet",
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
            name="add/snippet",
            description="新增代码/文本片段（支持公共和项目绑定）",
            x_tags=["snippet", "add", "create", "code"],
            properties={
                "name": {"type": "string", "minLength": 1},
                "language": {"type": "string"},
                "content": {"type": "string"},
                "tags": _TAGS_SCHEMA,
                "project_id": {"type": "string", "minLength": 1},
            },
            required=["name"],
        ),
        _tool(
            name="get/snippet",
            description="按 id 获取片段详情",
            x_tags=["snippet", "get", "detail"],
            properties={"id": {"type": "integer", "minimum": 1}},
            required=["id"],
        ),
        _tool(
            name="list/snippet",
            description="列出代码/文本片段（可按 scope/language 过滤）",
            x_tags=["snippet", "list", "browse"],
            properties={
                "scope": {"type": "string", "enum": ["all", "public", "project"]},
                "project_id": {"type": "string", "minLength": 1},
                "language": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                "offset": {"type": "integer", "minimum": 0},
            },
        ),
        _tool(
            name="search/snippet",
            description="搜索代码/文本片段",
            x_tags=["snippet", "search", "find"],
            properties={
                "query": {"type": "string", "minLength": 1},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                "offset": {"type": "integer", "minimum": 0},
            },
            required=["query"],
        ),
        _tool(
            name="update/snippet",
            description="更新代码/文本片段",
            x_tags=["snippet", "update", "edit"],
            properties={
                "id": {"type": "integer", "minimum": 1},
                "name": {"type": "string", "minLength": 1},
                "language": {"type": "string"},
                "content": {"type": "string"},
                "tags": _TAGS_SCHEMA,
            },
            required=["id"],
        ),
        _tool(
            name="delete/snippet",
            description="删除代码/文本片段",
            x_tags=["snippet", "delete", "remove"],
            properties={"id": {"type": "integer", "minimum": 1}},
            required=["id"],
        ),
    ]
