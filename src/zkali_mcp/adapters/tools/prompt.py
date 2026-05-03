"""adapters.tools.prompt — MCP 工具分发层（薄层）。"""
from __future__ import annotations
from pathlib import Path
import domains.prompt.service as prompt_svc


def dispatch_prompt_tool(name: str, arguments: dict, db_path: Path) -> str | None:
    if name == "add/prompt":
        return prompt_svc.add_prompt(
            db_path,
            name=str(arguments["name"]).strip(),
            content=str(arguments.get("content", "")),
            tags=arguments.get("tags"),
            project_id=str(arguments.get("project_id", "")),
        )
    if name == "get/prompt":
        return prompt_svc.get_prompt(db_path, int(arguments["id"]))
    if name == "get/prompt/by-name":
        return prompt_svc.get_prompt_by_name(
            db_path,
            name=str(arguments["name"]).strip(),
            scope=str(arguments.get("scope", "auto")),
            project_id=str(arguments.get("project_id", "")),
        )
    if name == "list/prompt":
        return prompt_svc.list_prompt(
            db_path,
            scope=str(arguments.get("scope", "all")),
            project_id=str(arguments.get("project_id", "")),
            query=str(arguments.get("query", "")),
            limit=int(arguments.get("limit", 20)),
            offset=int(arguments.get("offset", 0)),
        )
    if name == "update/prompt":
        return prompt_svc.update_prompt(
            db_path,
            prompt_id=int(arguments["id"]),
            fields={k: v for k, v in arguments.items() if k != "id"},
        )
    if name == "render/prompt":
        return prompt_svc.render_prompt(
            db_path,
            prompt_id=int(arguments["id"]),
            variables=arguments.get("variables"),
            mode=str(arguments.get("mode", "loose")),
        )
    if name == "delete/prompt":
        return prompt_svc.delete_prompt(db_path, int(arguments["id"]))
    return None
