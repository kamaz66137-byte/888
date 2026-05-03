"""project.queries — 项目层可复用查询函数。

供 tool/ 各模块调用，避免内联重复 SQL。
"""
from __future__ import annotations

import json
from pathlib import Path

from db import open_conn


def project_exists(db_path: Path, project_id: str) -> bool:
    """检查 project_id 是否存在。"""
    with open_conn(db_path) as conn:
        return conn.execute(
            "SELECT 1 FROM projects WHERE id = ?", (project_id,)
        ).fetchone() is not None


def get_project_status(db_path: Path, project_id: str) -> str | None:
    """返回项目 status，不存在时返回 None。"""
    with open_conn(db_path) as conn:
        row = conn.execute(
            "SELECT status FROM projects WHERE id = ?", (project_id,)
        ).fetchone()
    return row["status"] if row else None


def project_is_active(db_path: Path, project_id: str) -> tuple[bool, str]:
    """
    检查项目是否 active。
    返回 (True, '') 或 (False, 错误描述)。
    """
    status = get_project_status(db_path, project_id)
    if status is None:
        return False, f"ERR: project not found: {project_id}"
    if status != "active":
        return False, f"ERR: project 非 active 状态 (status={status})"
    return True, ""


def get_project(db_path: Path, project_id: str) -> dict | None:
    """获取项目完整字段字典，不存在返回 None。"""
    with open_conn(db_path) as conn:
        row = conn.execute(
            """
            SELECT id, name, describe, location, environment,
                   languages, libraries, status, owner, created_at, updated_at
            FROM projects WHERE id = ?
            """,
            (project_id,),
        ).fetchone()
    if row is None:
        return None
    result = dict(row)
    for field in ("languages", "libraries"):
        try:
            result[field] = json.loads(result[field] or "[]")
        except (ValueError, TypeError):
            result[field] = []
    return result


def list_projects(
    db_path: Path,
    *,
    status: str = "all",
    limit: int = 20,
    offset: int = 0,
) -> list[dict]:
    """返回项目列表（含 todo 统计）。"""
    where_sql = ""
    params: list[object] = []
    if status != "all":
        where_sql = "WHERE p.status = ?"
        params.append(status)
    params.extend([limit, offset])

    with open_conn(db_path) as conn:
        rows = conn.execute(
            f"""
            SELECT p.id, p.name, p.status, p.location,
                   COUNT(t.id) AS todo_total,
                   SUM(CASE WHEN t.status = 'done' THEN 1 ELSE 0 END) AS todo_done
            FROM projects p
            LEFT JOIN project_todos t ON p.id = t.project_id
            {where_sql}
            GROUP BY p.id, p.name, p.status, p.location
            ORDER BY p.id DESC
            LIMIT ? OFFSET ?
            """,
            params,
        ).fetchall()
    return [dict(r) for r in rows]
