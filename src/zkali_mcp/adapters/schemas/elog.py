"""adapters.schemas.elog — 事件日志工具 Schema（对应 domains/elog）。"""
from __future__ import annotations

from mcp.types import Tool
from ._base import _tool

HELP_MAP: dict[str, str] = {
    "add/log": "add/log(summary, event_type='info', detail?, project_id?) -> 写入事件日志。",
    "get/log": "get/log(id) -> 获取日志详情。",
    "list/log": "list/log(project_id?, event_type?, limit=30, offset=0) -> 列出事件日志。",
    "clear/log": "clear/log(project_id?, event_type?) -> 清除日志（project_id/event_type 至少传一个）。",
}

TOOL_ORDER: list[str] = ["add/log", "get/log", "list/log", "clear/log"]


def build_tools() -> list[Tool]:
    return [
        _tool(
            name="add/log",
            description="写入事件/活动日志（可绑定项目）",
            x_tags=["log", "add", "event", "record"],
            properties={
                "summary": {"type": "string", "minLength": 1},
                "event_type": {"type": "string"},
                "detail": {"type": "string"},
                "project_id": {"type": "string", "minLength": 1},
            },
            required=["summary"],
        ),
        _tool(
            name="get/log",
            description="按 id 获取日志详情",
            x_tags=["log", "get", "detail"],
            properties={"id": {"type": "integer", "minimum": 1}},
            required=["id"],
        ),
        _tool(
            name="list/log",
            description="列出事件日志（可按 project_id/event_type 过滤）",
            x_tags=["log", "list", "browse", "event"],
            properties={
                "project_id": {"type": "string", "minLength": 1},
                "event_type": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 200},
                "offset": {"type": "integer", "minimum": 0},
            },
        ),
        _tool(
            name="clear/log",
            description="清除事件日志（project_id/event_type 至少传一个）",
            x_tags=["log", "clear", "delete"],
            properties={
                "project_id": {"type": "string", "minLength": 1},
                "event_type": {"type": "string"},
            },
        ),
    ]
