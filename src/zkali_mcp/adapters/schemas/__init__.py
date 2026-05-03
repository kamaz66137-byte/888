"""adapters.schemas — MCP Tool Schema 汇总层。

各模块 schema 定义在子模块中，此处负责组装最终的
HELP_MAP、TOOL_ORDER、ALLOWED_TOOLS 和 build_tools()。
"""
from __future__ import annotations

from mcp.types import Tool
from ._base import _tool
from . import note, task, project, docs, kv, prompt, memory, snippet, envvar, elog, system

# ── 组装 HELP_MAP ──────────────────────────────────────────────────────────────

HELP_MAP: dict[str, str] = {
    "tool_help": "tool_help(name?) -> 查看工具说明。name 为空则返回全部工具。",
}
for _mod in [note, task, project, docs, kv, prompt, memory, snippet, envvar, elog, system]:
    HELP_MAP.update(_mod.HELP_MAP)

# ── 组装 TOOL_ORDER ────────────────────────────────────────────────────────────

TOOL_ORDER: list[str] = ["tool_help"]
for _mod in [note, task, project, docs, kv, prompt, memory, snippet, envvar, elog, system]:
    TOOL_ORDER.extend(_mod.TOOL_ORDER)

ALLOWED_TOOLS: set[str] = set(TOOL_ORDER)


def build_tools() -> list[Tool]:
    """组装所有模块的 Tool 列表，tool_help 排在最前并引用完整 TOOL_ORDER。"""
    tools: list[Tool] = [
        _tool(
            name="tool_help",
            description="查看工具说明；不传 name 返回全部工具概览",
            x_tags=["system", "help"],
            properties={"name": {"type": "string", "enum": TOOL_ORDER}},
        ),
    ]
    for _mod in [note, task, project, docs, kv, prompt, memory, snippet, envvar, elog, system]:
        tools.extend(_mod.build_tools())
    return tools
