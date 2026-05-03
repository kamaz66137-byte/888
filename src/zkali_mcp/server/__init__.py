"""server — MCP 服务器层：包含 selftest 和 app。"""
from .selftest import run_self_test
from .app import run_server

__all__ = ["run_self_test", "run_server"]
