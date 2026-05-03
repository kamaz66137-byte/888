"""adapters.tools.envvar — MCP 工具分发层（薄层）。"""
from __future__ import annotations
from pathlib import Path
import domains.envvar.service as svc


def dispatch_envvar_tool(name: str, arguments: dict, db_path: Path) -> str | None:
    if name == "set/env":
        return svc.set_env(
            db_path,
            project_id=str(arguments["project_id"]).strip(),
            key=str(arguments["key"]).strip(),
            value=str(arguments.get("value", "")),
            description=str(arguments.get("description", "")),
        )
    if name == "get/env":
        return svc.get_env(
            db_path,
            project_id=str(arguments["project_id"]).strip(),
            key=str(arguments["key"]).strip(),
        )
    if name == "list/env":
        return svc.list_env(
            db_path,
            project_id=str(arguments["project_id"]).strip(),
            limit=int(arguments.get("limit", 50)),
            offset=int(arguments.get("offset", 0)),
        )
    if name == "delete/env":
        return svc.delete_env(
            db_path,
            project_id=str(arguments["project_id"]).strip(),
            key=str(arguments["key"]).strip(),
        )
    return None
