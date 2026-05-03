"""tool.dict_tool — MCP 工具分发层（薄层）。"""
from __future__ import annotations
from pathlib import Path
from dict import service as dict_svc


def dispatch_dict_tool(name: str, arguments: dict, db_path: Path) -> str | None:
    if name == "add/dict":
        return dict_svc.add_dict(
            db_path,
            name=str(arguments["name"]).strip(),
            value=str(arguments.get("value", "")),
            tags=arguments.get("tags"),
            project_id=str(arguments.get("project_id", "")),
        )
    if name == "get/dict":
        return dict_svc.get_dict(db_path, int(arguments["id"]))
    if name == "get/dict/by-name":
        return dict_svc.get_dict_by_name(
            db_path,
            name=str(arguments["name"]).strip(),
            scope=str(arguments.get("scope", "auto")),
            project_id=str(arguments.get("project_id", "")),
        )
    if name == "list/dict":
        return dict_svc.list_dict(
            db_path,
            scope=str(arguments.get("scope", "all")),
            project_id=str(arguments.get("project_id", "")),
            query=str(arguments.get("query", "")),
            limit=int(arguments.get("limit", 20)),
            offset=int(arguments.get("offset", 0)),
        )
    if name == "update/dict":
        return dict_svc.update_dict(
            db_path,
            dict_id=int(arguments["id"]),
            fields={k: v for k, v in arguments.items() if k != "id"},
        )
    if name == "delete/dict":
        return dict_svc.delete_dict(db_path, int(arguments["id"]))
    return None
