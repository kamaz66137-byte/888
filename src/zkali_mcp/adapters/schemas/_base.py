"""adapters.schemas._base — _tool() 构建帮助函数，供各模块 schema 文件共享。"""
from __future__ import annotations

from mcp.types import Tool


def _tool(
    *,
    name: str,
    description: str,
    x_tags: list[str],
    properties: dict,
    required: list[str] | None = None,
) -> Tool:
    schema: dict = {
        "type": "object",
        "x-tags": x_tags,
        "properties": properties,
        "additionalProperties": False,
    }
    if required:
        schema["required"] = required
    return Tool(name=name, description=description, inputSchema=schema)
