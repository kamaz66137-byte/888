"""adapters.schemas.note — 笔记工具 Schema。"""
from __future__ import annotations

from mcp.types import Tool
from ._base import _tool

HELP_MAP: dict[str, str] = {
    "note_add": "note_add(name, body?) -> 新增笔记，返回 note id。",
    "note_get": "note_get(id) -> 查看单条笔记详情。",
    "note_update": "note_update(id, name?, body?) -> 更新笔记，至少传 name/body 之一。",
    "note_list": "note_list(limit=20, offset=0) -> 分页列出笔记。",
    "note_search": "note_search(query, limit=20, offset=0) -> 关键词搜索笔记。",
    "note_delete": "note_delete(id) -> 删除指定笔记。",
}

TOOL_ORDER: list[str] = [
    "note_add", "note_get", "note_update", "note_list", "note_search", "note_delete",
]


def build_tools() -> list[Tool]:
    return [
        _tool(
            name="note_add",
            description="新增一条笔记",
            x_tags=["note", "add", "create", "write"],
            properties={
                "name": {"type": "string", "minLength": 1},
                "body": {"type": "string"},
            },
            required=["name"],
        ),
        _tool(
            name="note_get",
            description="按 id 获取一条笔记详情",
            x_tags=["note", "get", "detail", "read"],
            properties={"id": {"type": "integer", "minimum": 1}},
            required=["id"],
        ),
        _tool(
            name="note_update",
            description="更新笔记名称和正文（至少提供一个字段）",
            x_tags=["note", "update", "edit", "modify"],
            properties={
                "id": {"type": "integer", "minimum": 1},
                "name": {"type": "string", "minLength": 1},
                "body": {"type": "string"},
            },
            required=["id"],
        ),
        _tool(
            name="note_list",
            description="列出最近笔记",
            x_tags=["note", "list", "browse", "paginate"],
            properties={
                "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                "offset": {"type": "integer", "minimum": 0},
            },
        ),
        _tool(
            name="note_search",
            description="按关键词搜索名称和正文",
            x_tags=["note", "search", "find", "query", "fulltext"],
            properties={
                "query": {"type": "string", "minLength": 1},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                "offset": {"type": "integer", "minimum": 0},
            },
            required=["query"],
        ),
        _tool(
            name="note_delete",
            description="删除指定 id 的笔记",
            x_tags=["note", "delete", "remove"],
            properties={"id": {"type": "integer", "minimum": 1}},
            required=["id"],
        ),
    ]
