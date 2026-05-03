"""adapters.dispatcher — O(1) 路由分发中心。"""
from __future__ import annotations

from pathlib import Path
from typing import Callable

from .tools.docs import dispatch_docs_tool
from .tools.kv import dispatch_kv_tool
from .tools.envvar import dispatch_envvar_tool
from .tools.help import handle_help
from .tools.hot_events import dispatch_hot_events_tool
from .tools.elog import dispatch_elog_tool
from .tools.memory import dispatch_memory_tool
from .tools.note import dispatch_note_tool
from .tools.project import dispatch_project_tool
from .tools.prompt import dispatch_prompt_tool
from .tools.snippet import dispatch_snippet_tool
from .schemas import ALLOWED_TOOLS
from .tools.task import dispatch_task_tool
from .tools.stats import dispatch_stats_tool
from .tools.search_all import dispatch_search_all_tool
from .tools.bulk import dispatch_bulk_tool
from .tools.export_import import dispatch_export_import_tool
from .tools.tags import dispatch_tags_tool
from .tools.backup import dispatch_backup_tool

_NOTE_TOOLS = {"note_add", "note_get", "note_update", "note_list", "note_search", "note_delete"}
_TASK_TOOLS = {"task_add", "task_list", "task_update", "task_done", "task_delete", "task_stats"}
_PROJECT_TOOLS = {
    "add/project", "update/project", "list/project", "get/project", "delete/project",
    "add/progress", "update/progress", "list/progress", "stats/progress",
    "add/todo", "update/todo", "done/todo", "list/todo", "delete/todo",
}
_DOCS_TOOLS = {"add/docs", "get/docs", "list/docs", "search/docs", "update/docs", "delete/docs"}
_MEMORY_TOOLS = {"add/memory", "get/memory", "list/memory", "update/memory", "delete/memory", "clear/memory"}
_KV_TOOLS = {"add/dict", "get/dict", "get/dict/by-name", "list/dict", "update/dict", "delete/dict"}
_PROMPT_TOOLS = {"add/prompt", "get/prompt", "get/prompt/by-name", "list/prompt", "update/prompt", "render/prompt", "delete/prompt"}
_SNIPPET_TOOLS = {"add/snippet", "get/snippet", "list/snippet", "search/snippet", "update/snippet", "delete/snippet"}
_ENV_TOOLS = {"set/env", "get/env", "list/env", "delete/env"}
_LOG_TOOLS = {"add/log", "get/log", "list/log", "clear/log"}
_HOT_TOOLS = {"query/hot-events"}
_STATS_TOOLS = {"stats/all", "cleanup/expired"}
_SEARCH_ALL_TOOLS = {"search/all"}
_BULK_TOOLS = {"bulk/note_add", "bulk/task_add"}
_EXPORT_IMPORT_TOOLS = {"export/project", "import/project"}
_TAGS_TOOLS = {"list/tags", "rename/tag", "merge/tags"}
_BACKUP_TOOLS = {"backup/db"}


def _make_module_registry() -> dict[str, Callable[[str, dict, Path], str | None]]:
    registry: dict[str, Callable[[str, dict, Path], str | None]] = {}

    def _reg(tool_names: set[str], fn: Callable) -> None:
        for n in tool_names:
            registry[n] = fn

    _reg(_NOTE_TOOLS, dispatch_note_tool)
    _reg(_TASK_TOOLS, dispatch_task_tool)
    _reg(_PROJECT_TOOLS, dispatch_project_tool)
    _reg(_DOCS_TOOLS, dispatch_docs_tool)
    _reg(_MEMORY_TOOLS, dispatch_memory_tool)
    _reg(_KV_TOOLS, dispatch_kv_tool)
    _reg(_PROMPT_TOOLS, dispatch_prompt_tool)
    _reg(_SNIPPET_TOOLS, dispatch_snippet_tool)
    _reg(_ENV_TOOLS, dispatch_envvar_tool)
    _reg(_LOG_TOOLS, dispatch_elog_tool)
    _reg(_HOT_TOOLS, lambda n, a, db: dispatch_hot_events_tool(n, a))
    _reg(_STATS_TOOLS, dispatch_stats_tool)
    _reg(_SEARCH_ALL_TOOLS, dispatch_search_all_tool)
    _reg(_BULK_TOOLS, dispatch_bulk_tool)
    _reg(_EXPORT_IMPORT_TOOLS, dispatch_export_import_tool)
    _reg(_TAGS_TOOLS, dispatch_tags_tool)
    _reg(_BACKUP_TOOLS, dispatch_backup_tool)
    return registry


_TOOL_REGISTRY: dict[str, Callable[[str, dict, Path], str | None]] = _make_module_registry()


def dispatch_tool(name: str, arguments: dict, db_path: Path) -> str:
    if name not in ALLOWED_TOOLS:
        raise ValueError(f"Unknown tool: {name}")

    if name == "tool_help":
        return handle_help(arguments)

    handler = _TOOL_REGISTRY.get(name)
    if handler is None:
        raise ValueError(f"Unknown tool: {name}")

    result = handler(name, arguments, db_path)
    if result is None:
        raise ValueError(f"Tool handler returned None for: {name}")
    return result
