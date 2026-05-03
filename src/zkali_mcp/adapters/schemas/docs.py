"""adapters.schemas.docs — 知识文档工具 Schema。"""
from __future__ import annotations

from mcp.types import Tool
from ._base import _tool

HELP_MAP: dict[str, str] = {
    "add/docs": "add/docs(name, content?, tags?, project_id?) -> 新增知识文档；project_id 为空写入公共知识。",
    "get/docs": "get/docs(id) -> 获取知识文档详情。",
    "list/docs": "list/docs(scope='all', project_id?, query?, limit=20, offset=0) -> 列出知识文档。",
    "search/docs": "search/docs(query, scope='all', project_id?, limit=20, offset=0) -> 搜索知识文档。",
    "update/docs": "update/docs(id, name?, content?, tags?, project_id?) -> 更新知识文档；project_id 传空可转为公共知识。",
    "delete/docs": "delete/docs(id) -> 删除知识文档。",
}

TOOL_ORDER: list[str] = [
    "add/docs", "get/docs", "list/docs", "search/docs", "update/docs", "delete/docs",
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
            name="add/docs",
            description="新增知识文档（支持公共知识和项目知识）",
            x_tags=["docs", "add", "create", "knowledge"],
            properties={
                "name": {"type": "string", "minLength": 1},
                "content": {"type": "string"},
                "tags": _TAGS_SCHEMA,
                "project_id": {"type": "string", "minLength": 1},
            },
            required=["name"],
        ),
        _tool(
            name="get/docs",
            description="按 id 获取知识文档详情",
            x_tags=["docs", "get", "detail"],
            properties={"id": {"type": "integer", "minimum": 1}},
            required=["id"],
        ),
        _tool(
            name="list/docs",
            description="列出知识文档（支持公共与项目过滤）",
            x_tags=["docs", "list", "browse"],
            properties={
                "scope": {"type": "string", "enum": ["all", "public", "project"]},
                "project_id": {"type": "string", "minLength": 1},
                "query": {"type": "string", "minLength": 1},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                "offset": {"type": "integer", "minimum": 0},
            },
        ),
        _tool(
            name="search/docs",
            description="搜索知识文档（支持公共与项目过滤）",
            x_tags=["docs", "search", "find", "knowledge"],
            properties={
                "query": {"type": "string", "minLength": 1},
                "scope": {"type": "string", "enum": ["all", "public", "project"]},
                "project_id": {"type": "string", "minLength": 1},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                "offset": {"type": "integer", "minimum": 0},
            },
            required=["query"],
        ),
        _tool(
            name="update/docs",
            description="更新知识文档（可切换公共/项目绑定）",
            x_tags=["docs", "update", "edit"],
            properties={
                "id": {"type": "integer", "minimum": 1},
                "name": {"type": "string", "minLength": 1},
                "content": {"type": "string"},
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
            name="delete/docs",
            description="删除知识文档",
            x_tags=["docs", "delete", "remove"],
            properties={"id": {"type": "integer", "minimum": 1}},
            required=["id"],
        ),
    ]
