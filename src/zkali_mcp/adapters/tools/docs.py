"""adapters.tools.docs — MCP 工具分发层（薄层）。"""
from __future__ import annotations
from pathlib import Path
import domains.docs.service as svc


def dispatch_docs_tool(name: str, arguments: dict, db_path: Path) -> str | None:
    if name == "add/docs":
        return svc.add_docs(
            db_path,
            name=str(arguments.get("name", "") or arguments.get("title", "")).strip(),
            content=str(arguments.get("content", "")),
            tags=arguments.get("tags"),
            project_id=str(arguments.get("project_id", "")),
        )
    if name == "get/docs":
        return svc.get_docs(db_path, int(arguments["id"]))
    if name == "list/docs":
        return svc.list_docs(
            db_path,
            scope=str(arguments.get("scope", "all")),
            project_id=str(arguments.get("project_id", "")),
            query=str(arguments.get("query", "")),
            limit=int(arguments.get("limit", 20)),
            offset=int(arguments.get("offset", 0)),
        )
    if name == "search/docs":
        return svc.list_docs(
            db_path,
            scope=str(arguments.get("scope", "all")),
            project_id=str(arguments.get("project_id", "")),
            query=str(arguments.get("query", "")),
            limit=int(arguments.get("limit", 20)),
            offset=int(arguments.get("offset", 0)),
        )
    if name == "update/docs":
        return svc.update_docs(
            db_path,
            doc_id=int(arguments["id"]),
            fields={k: v for k, v in arguments.items() if k != "id"},
        )
    if name == "delete/docs":
        return svc.delete_docs(db_path, int(arguments["id"]))
    return None
