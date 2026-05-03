"""adapters.schemas.prompt — 提示词模板工具 Schema。"""
from __future__ import annotations

from mcp.types import Tool
from ._base import _tool

HELP_MAP: dict[str, str] = {
    "add/prompt": "add/prompt(name, content?, tags?, project_id?) -> 新增提示词模板。",
    "get/prompt": "get/prompt(id) -> 获取提示词模板详情。",
    "get/prompt/by-name": "get/prompt/by-name(name, scope='auto', project_id?) -> 按名称获取提示词模板。",
    "list/prompt": "list/prompt(scope='all', project_id?, query?, limit=20, offset=0) -> 列出提示词模板。",
    "update/prompt": "update/prompt(id, name?, content?, tags?, project_id?) -> 更新提示词模板。",
    "render/prompt": "render/prompt(id, variables?, mode='loose') -> 渲染提示词模板。",
    "delete/prompt": "delete/prompt(id) -> 删除提示词模板。",
}

TOOL_ORDER: list[str] = [
    "add/prompt", "get/prompt", "get/prompt/by-name", "list/prompt",
    "update/prompt", "render/prompt", "delete/prompt",
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
            name="add/prompt",
            description="新增提示词模板（支持公共和项目绑定）",
            x_tags=["prompt", "add", "create", "template"],
            properties={
                "name": {"type": "string", "minLength": 1},
                "content": {"type": "string"},
                "tags": _TAGS_SCHEMA,
                "project_id": {"type": "string", "minLength": 1},
            },
            required=["name"],
        ),
        _tool(
            name="get/prompt",
            description="按 id 获取提示词模板详情",
            x_tags=["prompt", "get", "detail"],
            properties={"id": {"type": "integer", "minimum": 1}},
            required=["id"],
        ),
        _tool(
            name="get/prompt/by-name",
            description="按名称获取提示词模板（支持 public/project/auto）",
            x_tags=["prompt", "get", "name"],
            properties={
                "name": {"type": "string", "minLength": 1},
                "scope": {"type": "string", "enum": ["auto", "public", "project"]},
                "project_id": {"type": "string", "minLength": 1},
            },
            required=["name"],
        ),
        _tool(
            name="list/prompt",
            description="列出提示词模板（支持公共与项目过滤）",
            x_tags=["prompt", "list", "browse"],
            properties={
                "scope": {"type": "string", "enum": ["all", "public", "project"]},
                "project_id": {"type": "string", "minLength": 1},
                "query": {"type": "string", "minLength": 1},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                "offset": {"type": "integer", "minimum": 0},
            },
        ),
        _tool(
            name="update/prompt",
            description="更新提示词模板（可切换公共/项目绑定）",
            x_tags=["prompt", "update", "edit"],
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
            name="render/prompt",
            description="按变量渲染提示词模板（strict/loose）",
            x_tags=["prompt", "render", "template"],
            properties={
                "id": {"type": "integer", "minimum": 1},
                "variables": {"type": "object"},
                "mode": {"type": "string", "enum": ["strict", "loose"]},
            },
            required=["id"],
        ),
        _tool(
            name="delete/prompt",
            description="删除提示词模板",
            x_tags=["prompt", "delete", "remove"],
            properties={"id": {"type": "integer", "minimum": 1}},
            required=["id"],
        ),
    ]
