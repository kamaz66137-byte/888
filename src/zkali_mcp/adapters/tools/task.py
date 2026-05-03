"""adapters.tools.task — MCP 工具分发层（薄层）。"""
from __future__ import annotations
from pathlib import Path
import domains.task.service as svc


def dispatch_task_tool(name: str, arguments: dict, db_path: Path) -> str | None:
    if name == "task_add":
        return svc.add_task(
            db_path,
            name=str(arguments["name"]).strip(),
            description=str(arguments.get("description", "")),
            priority=str(arguments.get("priority", "medium")),
            due_date=arguments.get("due_date"),
        )
    if name == "task_list":
        return svc.list_tasks(
            db_path,
            status=str(arguments.get("status", "all")),
            priority=str(arguments.get("priority", "all")),
            limit=int(arguments.get("limit", 20)),
            offset=int(arguments.get("offset", 0)),
        )
    if name == "task_update":
        return svc.update_task(
            db_path,
            task_id=int(arguments["id"]),
            fields={k: v for k, v in arguments.items() if k != "id"},
        )
    if name == "task_done":
        return svc.done_task(db_path, int(arguments["id"]))
    if name == "task_delete":
        return svc.delete_task(db_path, int(arguments["id"]))
    if name == "task_stats":
        return svc.stats_tasks(db_path)
    return None
