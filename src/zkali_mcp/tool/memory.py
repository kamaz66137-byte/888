"""tool.memory — MCP 工具分发层（薄层）。"""
from __future__ import annotations
from pathlib import Path
import memory.service as mem_svc


def dispatch_memory_tool(name: str, arguments: dict, db_path: Path) -> str | None:
    if name == "add/memory":
        return mem_svc.add_memory(
            db_path,
            project_id=str(arguments["project_id"]).strip(),
            scope=str(arguments.get("scope", "project")),
            namespace=str(arguments.get("namespace", "default")),
            key=str(arguments["key"]).strip(),
            value=str(arguments.get("value", "")),
            ttl_seconds=int(arguments["ttl"]) if arguments.get("ttl") is not None else None,
        )
    if name == "get/memory":
        return mem_svc.get_memory(
            db_path,
            project_id=str(arguments["project_id"]).strip(),
            key=str(arguments["key"]).strip(),
            scope=str(arguments.get("scope", "project")),
            namespace=str(arguments.get("namespace", "default")),
        )
    if name == "list/memory":
        return mem_svc.list_memory(
            db_path,
            project_id=str(arguments["project_id"]).strip(),
            namespace=str(arguments.get("namespace", "")),
            limit=int(arguments.get("limit", 20)),
            offset=int(arguments.get("offset", 0)),
        )
    if name == "update/memory":
        return mem_svc.update_memory(
            db_path,
            project_id=str(arguments["project_id"]).strip(),
            key=str(arguments["key"]).strip(),
            namespace=str(arguments.get("namespace", "default")),
            value=str(arguments["value"]),
            ttl_seconds=int(arguments["ttl"]) if arguments.get("ttl") is not None else None,
        )
    if name == "delete/memory":
        return mem_svc.delete_memory(
            db_path,
            project_id=str(arguments["project_id"]).strip(),
            key=str(arguments["key"]).strip(),
            scope=str(arguments.get("scope", "project")),
            namespace=str(arguments.get("namespace", "default")),
        )
    if name == "clear/memory":
        return mem_svc.clear_memory(
            db_path,
            project_id=str(arguments["project_id"]).strip(),
            scope=str(arguments.get("scope", "session")),
        )
    return None
