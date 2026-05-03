"""server.app — MCP 服务器入口：日志配置、服务器构建与启动。"""
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
from adapters import dispatch_tool, build_tools

logger = logging.getLogger("zkali_mcp")


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


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

    import json as json_module
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
        body = json_module.dumps(data, ensure_ascii=False).encode("utf-8")
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
        import sqlite3
        try:
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
