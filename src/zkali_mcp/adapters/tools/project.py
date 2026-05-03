"""adapters.tools.project — MCP 工具分发层（薄层）。"""
from __future__ import annotations
from pathlib import Path
import domains.project.service as svc


def dispatch_project_tool(name: str, arguments: dict, db_path: Path) -> str | None:
    if name == "add/project":
        return svc.add_project(
            db_path,
            project_id=str(arguments["id"]).strip(),
            name=str(arguments["name"]).strip(),
            describe=str(arguments.get("describe", "")),
            location=str(arguments.get("location", "")),
            environment=str(arguments.get("environment", "")),
            languages=arguments.get("languages"),
            libraries=arguments.get("libraries"),
            status=str(arguments.get("status", "active")),
            owner=str(arguments.get("owner", "")),
        )
    if name == "update/project":
        return svc.update_project(
            db_path,
            project_id=str(arguments["id"]).strip(),
            fields={k: v for k, v in arguments.items() if k != "id"},
        )
    if name == "list/project":
        return svc.list_projects(
            db_path,
            status=str(arguments.get("status", "all")),
            limit=int(arguments.get("limit", 20)),
            offset=int(arguments.get("offset", 0)),
        )
    if name == "get/project":
        return svc.get_project_detail(db_path, str(arguments["id"]).strip())
    if name == "delete/project":
        return svc.delete_project(db_path, str(arguments["id"]).strip())
    if name == "add/progress":
        return svc.add_progress(
            db_path,
            project_id=str(arguments["project_id"]).strip(),
            name=str(arguments["name"]).strip(),
            feature=str(arguments.get("feature", "")),
            context=str(arguments.get("context", "")),
            status=str(arguments.get("status", "todo")),
            priority=str(arguments.get("priority", "medium")),
            progress=int(arguments.get("progress", 0)),
            milestone=str(arguments.get("milestone", "")),
        )
    if name == "update/progress":
        return svc.update_progress(
            db_path,
            project_id=str(arguments["project_id"]).strip(),
            task_id=int(arguments["task_id"]),
            fields={k: v for k, v in arguments.items() if k not in ("project_id", "task_id")},
        )
    if name == "list/progress":
        return svc.list_progress(
            db_path,
            project_id=str(arguments["project_id"]).strip(),
            status=str(arguments.get("status", "all")),
            limit=int(arguments.get("limit", 20)),
            offset=int(arguments.get("offset", 0)),
        )
    if name == "stats/progress":
        return svc.stats_progress(db_path, str(arguments["project_id"]).strip())
    if name == "add/todo":
        return svc.add_todo(
            db_path,
            project_id=str(arguments["project_id"]).strip(),
            name=str(arguments["name"]).strip(),
            feature=str(arguments.get("feature", "")),
            context=str(arguments.get("context", "")),
            step_order=int(arguments.get("step_order", 1)),
            status=str(arguments.get("status", "todo")),
        )
    if name == "update/todo":
        return svc.update_todo(
            db_path,
            project_id=str(arguments["project_id"]).strip(),
            todo_id=int(arguments["id"]),
            fields={k: v for k, v in arguments.items() if k not in ("project_id", "id")},
        )
    if name == "done/todo":
        return svc.done_todo(
            db_path,
            project_id=str(arguments["project_id"]).strip(),
            todo_id=int(arguments["id"]),
        )
    if name == "list/todo":
        return svc.list_todos(
            db_path,
            project_id=str(arguments["project_id"]).strip(),
            status=str(arguments.get("status", "all")),
            limit=int(arguments.get("limit", 20)),
            offset=int(arguments.get("offset", 0)),
        )
    if name == "delete/todo":
        return svc.delete_todo(
            db_path,
            project_id=str(arguments["project_id"]).strip(),
            todo_id=int(arguments["id"]),
        )
    return None
