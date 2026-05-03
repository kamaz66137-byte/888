"""adapters.tools.kv — MCP 工具分发层（薄层）。"""
from __future__ import annotations
from pathlib import Path
from domains.kv import service as kv_svc


def dispatch_kv_tool(name: str, arguments: dict, db_path: Path) -> str | None:
    if name == "add/dict":
        return kv_svc.add_dict(
            db_path,
            name=str(arguments["name"]).strip(),
            value=str(arguments.get("value", "")),
            tags=arguments.get("tags"),
            project_id=str(arguments.get("project_id", "")),
        )
    if name == "get/dict":
        return kv_svc.get_dict(db_path, int(arguments["id"]))
    if name == "get/dict/by-name":
        return kv_svc.get_dict_by_name(
            db_path,
            name=str(arguments["name"]).strip(),
            scope=str(arguments.get("scope", "auto")),
            project_id=str(arguments.get("project_id", "")),
        )
    if name == "list/dict":
        return kv_svc.list_dict(
            db_path,
            scope=str(arguments.get("scope", "all")),
            project_id=str(arguments.get("project_id", "")),
            query=str(arguments.get("query", "")),
            limit=int(arguments.get("limit", 20)),
            offset=int(arguments.get("offset", 0)),
        )
    if name == "update/dict":
        return kv_svc.update_dict(
            db_path,
            dict_id=int(arguments["id"]),
            fields={k: v for k, v in arguments.items() if k != "id"},
        )
    if name == "delete/dict":
        return kv_svc.delete_dict(db_path, int(arguments["id"]))
    return None
