"""事件日志模块：结构化事件日志读写。"""

from .service import add_log, get_log, list_logs, clear_logs

__all__ = ["add_log", "get_log", "list_logs", "clear_logs"]
