"""tool.snippet — MCP 工具分发层（薄层）。"""
from __future__ import annotations
from pathlib import Path
import snippet.service as svc


def dispatch_snippet_tool(name: str, arguments: dict, db_path: Path) -> str | None:
    if name == "add/snippet":
        return svc.add_snippet(
            db_path,
            name=str(arguments["name"]).strip(),
            language=str(arguments.get("language", "")),
            content=str(arguments.get("content", "")),
            tags=str(arguments.get("tags", "[]")),
            project_id=str(arguments.get("project_id") or ""),
        )
    if name == "get/snippet":
        return svc.get_snippet(db_path, int(arguments["id"]))
    if name == "list/snippet":
        return svc.list_snippets(
            db_path,
            scope=str(arguments.get("scope", "all")),
            project_id=str(arguments.get("project_id") or ""),
            language=str(arguments.get("language") or ""),
            limit=int(arguments.get("limit", 20)),
            offset=int(arguments.get("offset", 0)),
        )
    if name == "search/snippet":
        return svc.search_snippets(
            db_path,
            query=str(arguments["query"]).strip(),
            limit=int(arguments.get("limit", 20)),
            offset=int(arguments.get("offset", 0)),
        )
    if name == "update/snippet":
        return svc.update_snippet(
            db_path,
            snippet_id=int(arguments["id"]),
            fields={k: v for k, v in arguments.items() if k != "id"},
        )
    if name == "delete/snippet":
        return svc.delete_snippet(db_path, int(arguments["id"]))
    return None
