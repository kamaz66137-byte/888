from __future__ import annotations

import asyncio
import logging
import time
from pathlib import Path
from typing import Literal

from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.server.stdio import stdio_server
from mcp.server.streamable_http import StreamableHTTPServerTransport
from mcp.types import TextContent

from db import init_db
from tool import dispatch_tool, build_tools

logger = logging.getLogger("zkali_mcp")


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def run_self_test(db_path: Path) -> int:
    init_db(db_path)
    project_id = "self-test-proj"

    help_output = dispatch_tool("tool_help", {}, db_path)
    if (
        "note_add" not in help_output
        or "task_add" not in help_output
        or "add/project" not in help_output
        or "add/memory" not in help_output
    ):
        print("SELF-TEST FAIL")
        return 1

    note_result = dispatch_tool("note_add", {"name": "self-test", "body": "ok"}, db_path)
    if "OK: note id=" not in note_result:
        print("SELF-TEST FAIL")
        return 1

    note_output = dispatch_tool("note_search", {"query": "self-test"}, db_path)
    if "self-test" not in note_output:
        print("SELF-TEST FAIL")
        return 1

    task_result = dispatch_tool(
        "task_add",
        {"name": "task-self-test", "description": "ok", "priority": "high"},
        db_path,
    )
    if "OK: task id=" not in task_result:
        print("SELF-TEST FAIL")
        return 1

    stats_output = dispatch_tool("task_stats", {}, db_path)
    if "total=" not in stats_output:
        print("SELF-TEST FAIL")
        return 1

    dispatch_tool("delete/project", {"id": project_id}, db_path)

    project_result = dispatch_tool(
        "add/project",
        {
            "id": project_id,
            "name": "self-test",
            "describe": "mcp self test project",
            "location": "C:/Users/a1575/Desktop/888/src/zkali_mcp",
            "environment": "python3.12 + windows10",
            "languages": ["python"],
            "libraries": ["mcp", "sqlite3"],
            "owner": "system",
        },
        db_path,
    )
    if "OK id=" not in project_result:
        print("SELF-TEST FAIL")
        return 1

    progress_result = dispatch_tool(
        "add/progress",
        {
            "project_id": project_id,
            "name": "build mcp",
            "priority": "high",
        },
        db_path,
    )
    if "OK id=" not in progress_result:
        print("SELF-TEST FAIL")
        return 1

    memory_result = dispatch_tool(
        "add/memory",
        {
            "project_id": project_id,
            "scope": "project",
            "namespace": "self-test",
            "key": "boot",
            "value": "ok",
        },
        db_path,
    )
    if "OK id=" not in memory_result:
        print("SELF-TEST FAIL")
        return 1

    todo_result = dispatch_tool(
        "add/todo",
        {
            "project_id": project_id,
            "name": "定义工具契约",
            "feature": "contract",
            "context": "先定义输入输出再写实现",
            "step_order": 1,
        },
        db_path,
    )
    if "OK id=" not in todo_result:
        print("SELF-TEST FAIL")
        return 1

    todo_list = dispatch_tool("list/todo", {"project_id": project_id}, db_path)
    if "定义工具契约" not in todo_list:
        print("SELF-TEST FAIL")
        return 1

    progress_stats = dispatch_tool("stats/progress", {"project_id": project_id}, db_path)
    if "total:" not in progress_stats:
        print("SELF-TEST FAIL")
        return 1

    memory_list = dispatch_tool("list/memory", {"project_id": project_id}, db_path)
    if "boot" not in memory_list:
        print("SELF-TEST FAIL")
        return 1

    public_doc = dispatch_tool(
        "add/docs",
        {
            "name": "public-doc",
            "content": "global knowledge",
            "tags": ["public", "kb"],
        },
        db_path,
    )
    if "OK id=" not in public_doc:
        print("SELF-TEST FAIL")
        return 1

    project_doc = dispatch_tool(
        "add/docs",
        {
            "project_id": project_id,
            "name": "project-doc",
            "content": "project scoped knowledge",
            "tags": "project,kb",
        },
        db_path,
    )
    if "OK id=" not in project_doc:
        print("SELF-TEST FAIL")
        return 1

    docs_output = dispatch_tool("search/docs", {"query": "knowledge", "project_id": project_id}, db_path)
    if "public-doc" not in docs_output or "project-doc" not in docs_output:
        print("SELF-TEST FAIL")
        return 1

    dict_result = dispatch_tool(
        "add/dict",
        {
            "name": "api_base",
            "value": "https://example.local",
            "project_id": project_id,
            "tags": ["config", "endpoint"],
        },
        db_path,
    )
    if "OK id=" not in dict_result:
        print("SELF-TEST FAIL")
        return 1

    dict_list = dispatch_tool("list/dict", {"project_id": project_id, "query": "api_base"}, db_path)
    if "api_base" not in dict_list:
        print("SELF-TEST FAIL")
        return 1

    dict_get_by_name = dispatch_tool(
        "get/dict/by-name",
        {"name": "api_base", "scope": "auto", "project_id": project_id},
        db_path,
    )
    if "name: api_base" not in dict_get_by_name:
        print("SELF-TEST FAIL")
        return 1

    prompt_result = dispatch_tool(
        "add/prompt",
        {
            "name": "rewrite-mail",
            "content": "请将以下内容改写为正式邮件：{{content}}",
            "project_id": project_id,
            "tags": ["rewrite", "mail"],
        },
        db_path,
    )
    if "OK id=" not in prompt_result:
        print("SELF-TEST FAIL")
        return 1
    prompt_id = int(prompt_result.split("=")[-1])

    prompt_list = dispatch_tool("list/prompt", {"project_id": project_id, "query": "rewrite-mail"}, db_path)
    if "rewrite-mail" not in prompt_list:
        print("SELF-TEST FAIL")
        return 1

    prompt_get_by_name = dispatch_tool(
        "get/prompt/by-name",
        {"name": "rewrite-mail", "scope": "auto", "project_id": project_id},
        db_path,
    )
    if "name: rewrite-mail" not in prompt_get_by_name:
        print("SELF-TEST FAIL")
        return 1

    prompt_render_strict_fail = dispatch_tool(
        "render/prompt",
        {"id": prompt_id, "mode": "strict", "variables": {}},
        db_path,
    )
    if "ERR 缺少变量" not in prompt_render_strict_fail:
        print("SELF-TEST FAIL")
        return 1

    prompt_render_ok = dispatch_tool(
        "render/prompt",
        {"id": prompt_id, "mode": "strict", "variables": {"content": "今天完成联调"}},
        db_path,
    )
    if "mode: strict" not in prompt_render_ok:
        print("SELF-TEST FAIL")
        return 1

    project_detail = dispatch_tool("get/project", {"id": project_id}, db_path)
    if "location:" not in project_detail or "libraries:" not in project_detail:
        print("SELF-TEST FAIL")
        return 1

    snippet_result = dispatch_tool(
        "add/snippet",
        {
            "name": "hello-world",
            "language": "python",
            "content": "print('hello world')",
            "project_id": project_id,
        },
        db_path,
    )
    if "OK: snippet id=" not in snippet_result:
        print("SELF-TEST FAIL")
        return 1

    snippet_search = dispatch_tool("search/snippet", {"query": "hello"}, db_path)
    if "hello-world" not in snippet_search:
        print("SELF-TEST FAIL")
        return 1

    env_result = dispatch_tool(
        "set/env",
        {"project_id": project_id, "key": "DEBUG", "value": "true", "description": "debug mode"},
        db_path,
    )
    if "OK: env set" not in env_result:
        print("SELF-TEST FAIL")
        return 1

    env_get = dispatch_tool("get/env", {"project_id": project_id, "key": "DEBUG"}, db_path)
    if "DEBUG" not in env_get or "true" not in env_get:
        print("SELF-TEST FAIL")
        return 1

    log_result = dispatch_tool(
        "add/log",
        {"summary": "self-test started", "event_type": "info", "project_id": project_id},
        db_path,
    )
    if "OK: log id=" not in log_result:
        print("SELF-TEST FAIL")
        return 1

    log_list = dispatch_tool("list/log", {"project_id": project_id}, db_path)
    if "self-test started" not in log_list:
        print("SELF-TEST FAIL")
        return 1


    # ── Phase 2: CRUD 全覆盖 ──────────────────────────────────────────────

    # note: get / update / list / delete
    note_id = int(note_result.split("=")[-1])
    note_get = dispatch_tool("note_get", {"id": note_id}, db_path)
    if "self-test" not in note_get:
        print("SELF-TEST FAIL [note_get]")
        return 1
    note_update = dispatch_tool("note_update", {"id": note_id, "body": "updated-body"}, db_path)
    if "OK" not in note_update:
        print("SELF-TEST FAIL [note_update]")
        return 1
    note_list = dispatch_tool("note_list", {"limit": 10}, db_path)
    if "self-test" not in note_list:
        print("SELF-TEST FAIL [note_list]")
        return 1
    note_delete = dispatch_tool("note_delete", {"id": note_id}, db_path)
    if "OK" not in note_delete:
        print("SELF-TEST FAIL [note_delete]")
        return 1

    # task: list / update / done / delete
    task_id = int(task_result.split("=")[-1])
    task_list = dispatch_tool("task_list", {"status": "all", "priority": "high"}, db_path)
    if "task-self-test" not in task_list:
        print("SELF-TEST FAIL [task_list]")
        return 1
    task_update = dispatch_tool("task_update", {"id": task_id, "priority": "low"}, db_path)
    if "OK" not in task_update:
        print("SELF-TEST FAIL [task_update]")
        return 1
    task_done = dispatch_tool("task_done", {"id": task_id}, db_path)
    if "OK" not in task_done:
        print("SELF-TEST FAIL [task_done]")
        return 1
    task_delete = dispatch_tool("task_delete", {"id": task_id}, db_path)
    if "OK" not in task_delete:
        print("SELF-TEST FAIL [task_delete]")
        return 1

    # project: list / update
    proj_list = dispatch_tool("list/project", {"status": "active"}, db_path)
    if project_id not in proj_list:
        print("SELF-TEST FAIL [list/project]")
        return 1
    proj_update = dispatch_tool(
        "update/project",
        {"id": project_id, "describe": "updated desc"},
        db_path,
    )
    if "OK" not in proj_update:
        print("SELF-TEST FAIL [update/project]")
        return 1

    # todo: update / done / delete
    todo_id = int(todo_result.split("=")[-1])
    todo_update = dispatch_tool(
        "update/todo",
        {"project_id": project_id, "id": todo_id, "name": "updated-todo"},
        db_path,
    )
    if "OK" not in todo_update:
        print("SELF-TEST FAIL [update/todo]")
        return 1
    todo_done = dispatch_tool("done/todo", {"project_id": project_id, "id": todo_id}, db_path)
    if "OK" not in todo_done:
        print("SELF-TEST FAIL [done/todo]")
        return 1
    todo_delete = dispatch_tool("delete/todo", {"project_id": project_id, "id": todo_id}, db_path)
    if "OK" not in todo_delete:
        print("SELF-TEST FAIL [delete/todo]")
        return 1

    # progress: update
    progress_id = int(progress_result.split("=")[-1])
    progress_update = dispatch_tool(
        "update/progress",
        {"project_id": project_id, "task_id": progress_id, "name": "updated-prog", "progress": 50},
        db_path,
    )
    if "OK" not in progress_update:
        print("SELF-TEST FAIL [update/progress]")
        return 1

    # docs: get / update / delete
    doc_id = int(public_doc.split("=")[-1])
    docs_get = dispatch_tool("get/docs", {"id": doc_id}, db_path)
    if "public-doc" not in docs_get:
        print("SELF-TEST FAIL [get/docs]")
        return 1
    docs_update = dispatch_tool("update/docs", {"id": doc_id, "content": "updated content"}, db_path)
    if "OK" not in docs_update:
        print("SELF-TEST FAIL [update/docs]")
        return 1
    docs_delete = dispatch_tool("delete/docs", {"id": doc_id}, db_path)
    if "OK" not in docs_delete:
        print("SELF-TEST FAIL [delete/docs]")
        return 1

    # dict: get / update / delete
    dict_id = int(dict_result.split("=")[-1])
    dict_get = dispatch_tool("get/dict", {"id": dict_id}, db_path)
    if "api_base" not in dict_get:
        print("SELF-TEST FAIL [get/dict]")
        return 1
    dict_update = dispatch_tool("update/dict", {"id": dict_id, "value": "https://updated.local"}, db_path)
    if "OK" not in dict_update:
        print("SELF-TEST FAIL [update/dict]")
        return 1
    dict_delete = dispatch_tool("delete/dict", {"id": dict_id}, db_path)
    if "OK" not in dict_delete:
        print("SELF-TEST FAIL [delete/dict]")
        return 1

    # memory: update / delete / clear
    memory_update = dispatch_tool(
        "update/memory",
        {"project_id": project_id, "scope": "project", "namespace": "self-test", "key": "boot", "value": "updated"},
        db_path,
    )
    if "OK" not in memory_update:
        print("SELF-TEST FAIL [update/memory]")
        return 1
    memory_delete = dispatch_tool(
        "delete/memory",
        {"project_id": project_id, "scope": "project", "namespace": "self-test", "key": "boot"},
        db_path,
    )
    if "OK" not in memory_delete:
        print("SELF-TEST FAIL [delete/memory]")
        return 1
    memory_clear = dispatch_tool("clear/memory", {"project_id": project_id, "scope": "session"}, db_path)
    if "OK" not in memory_clear:
        print("SELF-TEST FAIL [clear/memory]")
        return 1

    # prompt: get / update / render(loose) / delete
    prompt_get = dispatch_tool("get/prompt", {"id": prompt_id}, db_path)
    if "rewrite-mail" not in prompt_get:
        print("SELF-TEST FAIL [get/prompt]")
        return 1
    prompt_update = dispatch_tool(
        "update/prompt",
        {"id": prompt_id, "content": "改写为邮件：{{content}}"},
        db_path,
    )
    if "OK" not in prompt_update:
        print("SELF-TEST FAIL [update/prompt]")
        return 1
    prompt_render_loose = dispatch_tool(
        "render/prompt",
        {"id": prompt_id, "mode": "loose", "variables": {}},
        db_path,
    )
    if "mode: loose" not in prompt_render_loose:
        print("SELF-TEST FAIL [render/prompt loose]")
        return 1
    prompt_delete = dispatch_tool("delete/prompt", {"id": prompt_id}, db_path)
    if "OK" not in prompt_delete:
        print("SELF-TEST FAIL [delete/prompt]")
        return 1

    # snippet: get / list / update / delete
    snippet_id = int(snippet_result.split("=")[-1])
    snippet_get = dispatch_tool("get/snippet", {"id": snippet_id}, db_path)
    if "hello-world" not in snippet_get:
        print("SELF-TEST FAIL [get/snippet]")
        return 1
    snippet_list = dispatch_tool("list/snippet", {"scope": "project", "project_id": project_id}, db_path)
    if "hello-world" not in snippet_list:
        print("SELF-TEST FAIL [list/snippet]")
        return 1
    snippet_update = dispatch_tool("update/snippet", {"id": snippet_id, "language": "python3"}, db_path)
    if "OK" not in snippet_update:
        print("SELF-TEST FAIL [update/snippet]")
        return 1
    snippet_delete = dispatch_tool("delete/snippet", {"id": snippet_id}, db_path)
    if "OK" not in snippet_delete:
        print("SELF-TEST FAIL [delete/snippet]")
        return 1

    # env: list / delete
    env_list = dispatch_tool("list/env", {"project_id": project_id}, db_path)
    if "DEBUG" not in env_list:
        print("SELF-TEST FAIL [list/env]")
        return 1
    env_delete = dispatch_tool("delete/env", {"project_id": project_id, "key": "DEBUG"}, db_path)
    if "OK" not in env_delete:
        print("SELF-TEST FAIL [delete/env]")
        return 1

    # log: get / clear
    log_id = int(log_result.split("=")[-1])
    log_get = dispatch_tool("get/log", {"id": log_id}, db_path)
    if "self-test started" not in log_get:
        print("SELF-TEST FAIL [get/log]")
        return 1
    log_clear = dispatch_tool("clear/log", {"project_id": project_id}, db_path)
    if "OK" not in log_clear:
        print("SELF-TEST FAIL [clear/log]")
        return 1

    print("SELF-TEST OK")
    return 0


def _build_mcp_server(db_path: Path) -> Server:
    app = Server("zkali_mcp")

    @app.list_tools()
    async def list_tools():
        return build_tools()

    @app.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        t0 = time.monotonic()
        try:
            result = await asyncio.to_thread(dispatch_tool, name, arguments, db_path)
        except Exception as exc:
            logger.error("tool %s raised exception: %s", name, exc, exc_info=True)
            result = f"ERR INTERNAL: {exc}"
        elapsed_ms = int((time.monotonic() - t0) * 1000)
        preview = result[:80].replace("\n", " ") if result else ""
        logger.info("tool=%s elapsed=%dms result_preview=%r", name, elapsed_ms, preview)
        return [TextContent(type="text", text=result)]

    return app


async def run_server(
    db_path: Path,
    transport: Literal["stdio", "streamable-http", "sse"] = "stdio",
    host: str = "127.0.0.1",
    port: int = 8000,
) -> None:
    _configure_logging()
    init_db(db_path)
    app = _build_mcp_server(db_path)
    tools_count = len(build_tools())
    logger.info("zkali_mcp started transport=%s host=%s port=%s db=%s tools=%d", transport, host, port, db_path, tools_count)

    if transport == "stdio":
        async with stdio_server() as (reader, writer):
            await app.run(reader, writer, app.create_initialization_options())
        return

    import json as _json

    import uvicorn

    async def send_text_response(send, status_code: int, text: str) -> None:
        body = text.encode("utf-8")
        await send(
            {
                "type": "http.response.start",
                "status": status_code,
                "headers": [(b"content-type", b"text/plain; charset=utf-8")],
            }
        )
        await send({"type": "http.response.body", "body": body})

    async def send_json_response(send, status_code: int, data: dict) -> None:
        body = _json.dumps(data, ensure_ascii=False).encode("utf-8")
        await send(
            {
                "type": "http.response.start",
                "status": status_code,
                "headers": [
                    (b"content-type", b"application/json; charset=utf-8"),
                    (b"access-control-allow-origin", b"*"),
                ],
            }
        )
        await send({"type": "http.response.body", "body": body})

    async def handle_health(send) -> None:
        try:
            import sqlite3
            sqlite3.connect(db_path).close()
            db_status = "connected"
        except Exception:
            db_status = "error"
        await send_json_response(send, 200, {"status": "ok", "db": db_status, "tools": tools_count})

    if transport == "streamable-http":
        http_transport = StreamableHTTPServerTransport(mcp_session_id=None)

        async def streamable_http_asgi(scope, receive, send) -> None:
            if scope.get("type") != "http":
                return
            path = scope.get("path")
            if path == "/health":
                await handle_health(send)
                return
            if path != "/mcp":
                await send_text_response(send, 404, "Not Found")
                return
            await http_transport.handle_request(scope, receive, send)

        async def run_mcp_http() -> None:
            async with http_transport.connect() as (read_stream, write_stream):
                await app.run(read_stream, write_stream, app.create_initialization_options())

        config = uvicorn.Config(streamable_http_asgi, host=host, port=port, log_level="info")
        server = uvicorn.Server(config)

        mcp_task = asyncio.create_task(run_mcp_http())
        try:
            await server.serve()
        finally:
            mcp_task.cancel()
            await asyncio.gather(mcp_task, return_exceptions=True)
        return

    sse_transport = SseServerTransport("/messages")

    async def sse_asgi(scope, receive, send) -> None:
        if scope.get("type") != "http":
            return
        path = scope.get("path")
        method = scope.get("method")

        if path == "/health":
            await handle_health(send)
            return

        if path == "/sse" and method == "GET":
            async with sse_transport.connect_sse(scope, receive, send) as (read_stream, write_stream):
                await app.run(read_stream, write_stream, app.create_initialization_options())
            return

        if path == "/messages" and method == "POST":
            await sse_transport.handle_post_message(scope, receive, send)
            return

        await send_text_response(send, 404, "Not Found")

    config = uvicorn.Config(sse_asgi, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()
