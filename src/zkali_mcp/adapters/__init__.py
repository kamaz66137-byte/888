"""adapters — MCP 适配器层，对外暴露 dispatch_tool 和 build_tools。"""
from .dispatcher import dispatch_tool
from .schemas import build_tools

__all__ = ["dispatch_tool", "build_tools"]
