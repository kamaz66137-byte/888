"""adapters.tools.help — MCP 工具帮助处理。"""
from __future__ import annotations

from ..schemas import HELP_MAP, TOOL_ORDER


def handle_help(arguments: dict) -> str:
    target = str(arguments.get("name", "")).strip()
    if target:
        return HELP_MAP.get(target, "Error: 未找到该工具")
    return "\n".join(f"- {HELP_MAP[key]}" for key in TOOL_ORDER)
