from __future__ import annotations

from pathlib import Path

from .docs import dispatch_docs_tool
from .dict_tool import dispatch_dict_tool
from .env import dispatch_env_tool
from .help import handle_help
from .hot_events import dispatch_hot_events_tool
from .log import dispatch_log_tool
from .memory import dispatch_memory_tool
from .note import dispatch_note_tool
from .project import dispatch_project_tool
from .prompt_tool import dispatch_prompt_tool
from .snippet import dispatch_snippet_tool
from ._schemas import ALLOWED_TOOLS
from .task import dispatch_task_tool


def dispatch_tool(name: str, arguments: dict, db_path: Path) -> str:
    if name not in ALLOWED_TOOLS:
        raise ValueError(f"Unknown tool: {name}")

    if name == "tool_help":
        return handle_help(arguments)

    note_result = dispatch_note_tool(name, arguments, db_path)
    if note_result is not None:
        return note_result

    task_result = dispatch_task_tool(name, arguments, db_path)
    if task_result is not None:
        return task_result

    project_result = dispatch_project_tool(name, arguments, db_path)
    if project_result is not None:
        return project_result

    docs_result = dispatch_docs_tool(name, arguments, db_path)
    if docs_result is not None:
        return docs_result

    memory_result = dispatch_memory_tool(name, arguments, db_path)
    if memory_result is not None:
        return memory_result

    dict_result = dispatch_dict_tool(name, arguments, db_path)
    if dict_result is not None:
        return dict_result

    prompt_result = dispatch_prompt_tool(name, arguments, db_path)
    if prompt_result is not None:
        return prompt_result

    snippet_result = dispatch_snippet_tool(name, arguments, db_path)
    if snippet_result is not None:
        return snippet_result

    env_result = dispatch_env_tool(name, arguments, db_path)
    if env_result is not None:
        return env_result

    log_result = dispatch_log_tool(name, arguments, db_path)
    if log_result is not None:
        return log_result

    hot_result = dispatch_hot_events_tool(name, arguments)
    if hot_result is not None:
        return hot_result


    raise ValueError(f"Unknown tool: {name}")
