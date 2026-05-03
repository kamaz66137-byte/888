#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from runner import run_self_test, run_server

DEFAULT_DB = Path(__file__).resolve().parent / "db" / "zkali.db"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="zkali_mcp sqlite3 server")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="sqlite3 数据库路径")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="执行本地数据库自检后退出（不启动 MCP）",
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http", "sse"],
        default="stdio",
        help="MCP 传输方式：stdio / streamable-http / sse",
    )
    parser.add_argument("--host", default="127.0.0.1", help="HTTP 监听地址（HTTP 传输时生效）")
    parser.add_argument("--port", type=int, default=8000, help="HTTP 监听端口（HTTP 传输时生效）")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    db_path = Path(args.db).resolve()

    if args.self_test:
        return run_self_test(db_path)

    asyncio.run(
        run_server(
            db_path,
            transport=args.transport,
            host=args.host,
            port=args.port,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
