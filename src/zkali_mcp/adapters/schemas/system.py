"""adapters.schemas.system — 系统/跨域工具 Schema（stats, search, backup, bulk, tags, hot-events）。"""
from __future__ import annotations

from mcp.types import Tool
from ._base import _tool

HELP_MAP: dict[str, str] = {
    "query/hot-events": "query/hot-events(topic, date='today', timezone='Asia/Shanghai', region='global', scope='hot', limit=10, lang='zh-CN', strict_mode=true) -> 统一参数查询 topic 热点资讯（支持 google/hacker-news/multi 多源）。",
    "stats/all": "stats/all() -> 返回所有模块的记录数量汇总。",
    "search/all": "search/all(query, modules?, limit=5) -> 全局搜索 notes/tasks/docs/snippets/dict/prompt，结果按模块分组。",
    "bulk/note_add": "bulk/note_add(items: [{name, body?}]) -> 批量新增笔记，返回 count 和 ids。",
    "bulk/task_add": "bulk/task_add(items: [{name, description?, priority?, due_date?}]) -> 批量新增任务，返回 count 和 ids。",
    "list/tags": "list/tags(module?) -> 列出全局或指定模块的 tag 及使用次数。",
    "rename/tag": "rename/tag(old, new, module?) -> 批量重命名 tag。",
    "merge/tags": "merge/tags(source, target, module?) -> 合并 tag（source → target，自动去重）。",
    "backup/db": "backup/db(dest?) -> 备份 SQLite 数据库，返回备份路径和大小。",
}

TOOL_ORDER: list[str] = [
    "query/hot-events",
    "stats/all",
    "search/all",
    "bulk/note_add",
    "bulk/task_add",
    "list/tags",
    "rename/tag",
    "merge/tags",
    "backup/db",
]


def build_tools() -> list[Tool]:
    return [
        _tool(
            name="query/hot-events",
            description="统一参数查询热点资讯（按 topic 聚合），支持 Google News / Hacker News 多源",
            x_tags=["query", "hot", "events", "news"],
            properties={
                "topic": {"type": "string", "minLength": 1},
                "date": {"type": "string", "description": "today 或 YYYY-MM-DD"},
                "timezone": {"type": "string", "default": "Asia/Shanghai"},
                "region": {
                    "type": "string",
                    "enum": ["global", "hacker-news", "hn", "multi"],
                    "default": "global",
                    "description": "global=Google News, hacker-news/hn=HN, multi=两者合并",
                },
                "scope": {"type": "string", "enum": ["hot", "all"], "default": "hot"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 50, "default": 10},
                "lang": {"type": "string", "default": "zh-CN"},
                "strict_mode": {"type": "boolean", "default": True},
            },
        ),
        _tool(
            name="stats/all",
            description="返回所有模块的记录数量汇总（notes/tasks/projects/docs/snippets/dict/prompt/memories/logs）",
            x_tags=["stats", "summary", "count", "all"],
            properties={},
        ),
        _tool(
            name="search/all",
            description="全局搜索：同时在 notes/tasks/docs/snippets/dict/prompt 中搜索，结果按模块分组",
            x_tags=["search", "find", "all", "global", "fulltext"],
            properties={
                "query": {"type": "string", "minLength": 1},
                "modules": {
                    "anyOf": [
                        {"type": "string", "description": "逗号分隔的模块名"},
                        {"type": "array", "items": {"type": "string", "enum": ["notes", "tasks", "docs", "snippets", "dict", "prompt"]}},
                    ],
                    "description": "指定搜索范围，不传则搜索全部模块",
                },
                "limit": {"type": "integer", "minimum": 1, "maximum": 20, "default": 5, "description": "每个模块最多返回条数"},
            },
            required=["query"],
        ),
        _tool(
            name="bulk/note_add",
            description="批量新增笔记，用单一事务写入，返回新增数量和 id 列表",
            x_tags=["note", "bulk", "add", "batch"],
            properties={
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "minLength": 1},
                            "body": {"type": "string"},
                        },
                        "required": ["name"],
                    },
                    "minItems": 1,
                }
            },
            required=["items"],
        ),
        _tool(
            name="bulk/task_add",
            description="批量新增任务，用单一事务写入，返回新增数量和 id 列表",
            x_tags=["task", "bulk", "add", "batch"],
            properties={
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "minLength": 1},
                            "description": {"type": "string"},
                            "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                            "due_date": {"type": "string"},
                        },
                        "required": ["name"],
                    },
                    "minItems": 1,
                }
            },
            required=["items"],
        ),
        _tool(
            name="list/tags",
            description="列出全局或指定模块的所有 tag 及使用次数（支持 docs/dict/prompt/snippet）",
            x_tags=["tags", "list", "browse"],
            properties={
                "module": {
                    "type": "string",
                    "enum": ["docs", "dict", "prompt", "snippet"],
                    "description": "不传则列出全部模块的 tag",
                }
            },
        ),
        _tool(
            name="rename/tag",
            description="批量重命名 tag（将所有 old 替换为 new，支持跨模块）",
            x_tags=["tags", "rename", "update"],
            properties={
                "old": {"type": "string", "minLength": 1},
                "new": {"type": "string", "minLength": 1},
                "module": {
                    "type": "string",
                    "enum": ["docs", "dict", "prompt", "snippet"],
                    "description": "不传则在全部模块中重命名",
                },
            },
            required=["old", "new"],
        ),
        _tool(
            name="merge/tags",
            description="合并 tag：将 source tag 替换为 target tag（等同于跨模块 rename，会自动去重）",
            x_tags=["tags", "merge", "update"],
            properties={
                "source": {"type": "string", "minLength": 1},
                "target": {"type": "string", "minLength": 1},
                "module": {
                    "type": "string",
                    "enum": ["docs", "dict", "prompt", "snippet"],
                    "description": "不传则在全部模块中合并",
                },
            },
            required=["source", "target"],
        ),
        _tool(
            name="backup/db",
            description="备份 sqlite3 数据库到指定路径（使用 SQLite 热备份 API），返回备份路径和文件大小",
            x_tags=["backup", "db", "admin"],
            properties={
                "dest": {
                    "type": "string",
                    "description": "目标文件路径，不传则自动生成 zkali_backup_YYYYMMDD_HHMMSS.db",
                }
            },
        ),
    ]
