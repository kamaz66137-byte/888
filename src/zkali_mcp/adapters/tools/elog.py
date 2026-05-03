"""adapters.tools.elog — MCP 工具分发层（薄层）。"""
from __future__ import annotations
from pathlib import Path
import domains.elog.service as svc


def dispatch_elog_tool(name: str, arguments: dict, db_path: Path) -> str | None:
    if name == "add/log":
        return svc.add_log(
            db_path,
            summary=str(arguments["summary"]).strip(),
            event_type=str(arguments.get("event_type", "info")),
            project_id=arguments.get("project_id"),
            detail=str(arguments.get("detail", "")),
        )
    if name == "get/log":
        return svc.get_log(db_path, int(arguments["id"]))
    if name == "list/log":
        return svc.list_logs(
            db_path,
            project_id=arguments.get("project_id"),
            event_type=arguments.get("event_type"),
            limit=int(arguments.get("limit", 30)),
            offset=int(arguments.get("offset", 0)),
        )
    if name == "clear/log":
        return svc.clear_logs(
            db_path,
            project_id=arguments.get("project_id"),
            event_type=arguments.get("event_type"),
        )
    return None
