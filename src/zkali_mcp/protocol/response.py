from __future__ import annotations

from typing import Any


def _detail(detail: dict | None) -> dict:
    return detail or {}


def ok(message: str = "OK", data: dict | None = None) -> dict[str, Any]:
    return {
        "ok": True,
        "code": "OK",
        "message": message,
        "data": data or {},
    }


def err(code: str, message: str, detail: dict | None = None) -> dict[str, Any]:
    return {
        "ok": False,
        "code": code,
        "message": message,
        "detail": _detail(detail),
    }


def validate_error(field: str, reason: str) -> dict[str, Any]:
    return err("ERR_VALIDATION", f"{field}: {reason}", {"field": field})


def not_found(entity: str, key: str) -> dict[str, Any]:
    return err("ERR_NOT_FOUND", f"{entity} not found: {key}")


def conflict(entity: str, key: str) -> dict[str, Any]:
    return err("ERR_CONFLICT", f"{entity} already exists: {key}")


def forbidden(message: str = "forbidden") -> dict[str, Any]:
    return err("ERR_FORBIDDEN", message)


def internal_error(message: str = "internal error", detail: dict | None = None) -> dict[str, Any]:
    return err("ERR_INTERNAL", message, detail)
