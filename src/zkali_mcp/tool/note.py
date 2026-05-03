"""tool.note — MCP 工具分发层（薄层）。"""
from __future__ import annotations
from pathlib import Path
import note.service as svc


def dispatch_note_tool(name: str, arguments: dict, db_path: Path) -> str | None:
    if name == "note_add":
        return svc.add_note(
            db_path,
            name=str(arguments["name"]).strip(),
            body=str(arguments.get("body", "")),
        )
    if name == "note_get":
        return svc.get_note(db_path, int(arguments["id"]))
    if name == "note_update":
        return svc.update_note(
            db_path,
            note_id=int(arguments["id"]),
            fields={k: v for k, v in arguments.items() if k != "id"},
        )
    if name == "note_list":
        return svc.list_notes(
            db_path,
            limit=int(arguments.get("limit", 20)),
            offset=int(arguments.get("offset", 0)),
        )
    if name == "note_search":
        return svc.search_notes(
            db_path,
            query=str(arguments["query"]).strip(),
            limit=int(arguments.get("limit", 20)),
            offset=int(arguments.get("offset", 0)),
        )
    if name == "note_delete":
        return svc.delete_note(db_path, int(arguments["id"]))
    return None
