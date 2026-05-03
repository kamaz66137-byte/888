"""tool.tags — 标签管理工具（list/tags, rename/tag, merge/tags）。"""
from __future__ import annotations

import json
from pathlib import Path

from db import open_conn

# Tables that store tags as JSON arrays
_TAG_TABLES: dict[str, str] = {
    "docs": "docs_knowledge",
    "dict": "dict_items",
    "prompt": "prompt_items",
    "snippet": "snippets",
}


def _resolve_tables(module: str) -> dict[str, str]:
    if module and module in _TAG_TABLES:
        return {module: _TAG_TABLES[module]}
    return dict(_TAG_TABLES)


def _parse_tags(raw: str) -> list[str]:
    try:
        result = json.loads(raw)
        if isinstance(result, list):
            return [str(t) for t in result]
    except Exception:
        pass
    if raw:
        return [t.strip() for t in raw.split(",") if t.strip()]
    return []


def list_tags(db_path: Path, module: str = "") -> str:
    tables = _resolve_tables(module)
    tag_counts: dict[str, int] = {}

    with open_conn(db_path) as conn:
        for mod_name, table in tables.items():
            rows = conn.execute(f"SELECT tags FROM {table} WHERE tags IS NOT NULL AND tags != '[]'").fetchall()
            for row in rows:
                for tag in _parse_tags(row["tags"]):
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1

    if not tag_counts:
        return "(empty)"
    sorted_tags = sorted(tag_counts.items(), key=lambda x: (-x[1], x[0]))
    return "\n".join(f"{tag}: {count}" for tag, count in sorted_tags)


def rename_tag(db_path: Path, old_name: str, new_name: str, module: str = "") -> str:
    tables = _resolve_tables(module)
    total = 0

    with open_conn(db_path) as conn:
        for table in tables.values():
            rows = conn.execute(f"SELECT id, tags FROM {table}").fetchall()
            for row in rows:
                tags = _parse_tags(row["tags"])
                if old_name in tags:
                    new_tags = [new_name if t == old_name else t for t in tags]
                    # Deduplicate while preserving order
                    seen: set[str] = set()
                    deduped: list[str] = []
                    for t in new_tags:
                        if t not in seen:
                            seen.add(t)
                            deduped.append(t)
                    conn.execute(
                        f"UPDATE {table} SET tags = ? WHERE id = ?",
                        (json.dumps(deduped, ensure_ascii=False), row["id"]),
                    )
                    total += 1

    return f"OK updated={total}"


def merge_tags(db_path: Path, source: str, target: str, module: str = "") -> str:
    """Merge source tag into target (replaces source with target, deduplicates)."""
    return rename_tag(db_path, old_name=source, new_name=target, module=module)


def dispatch_tags_tool(name: str, arguments: dict, db_path: Path) -> str | None:
    if name == "list/tags":
        module = str(arguments.get("module", "")).strip()
        return list_tags(db_path, module=module)
    if name == "rename/tag":
        old_name = str(arguments.get("old", "")).strip()
        new_name = str(arguments.get("new", "")).strip()
        if not old_name or not new_name:
            return "ERR: old 和 new 都是必填参数"
        module = str(arguments.get("module", "")).strip()
        return rename_tag(db_path, old_name=old_name, new_name=new_name, module=module)
    if name == "merge/tags":
        source = str(arguments.get("source", "")).strip()
        target = str(arguments.get("target", "")).strip()
        if not source or not target:
            return "ERR: source 和 target 都是必填参数"
        module = str(arguments.get("module", "")).strip()
        return merge_tags(db_path, source=source, target=target, module=module)
    return None
