"""adapters._contract — 工具契约定义（从 tool/_contract.py 迁移）。"""
from __future__ import annotations


def ok_id(n: int) -> str:
    return f"OK id={n}"


def ok_updated() -> str:
    return "OK updated"


def ok_deleted() -> str:
    return "OK deleted"


def err_not_found() -> str:
    return "ERR not_found"


def err_validation(msg: str) -> str:
    return f"ERR {msg}"


def list_empty() -> str:
    return "(empty)"
