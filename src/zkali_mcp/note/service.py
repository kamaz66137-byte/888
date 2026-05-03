"""note.service — 笔记业务逻辑层。"""
from __future__ import annotations

from pathlib import Path

from db import open_conn


def add_note(db_path: Path, name: str, body: str = "") -> str:
    with open_conn(db_path) as conn:
        cursor = conn.execute(
            "INSERT INTO notes (name, body) VALUES (?, ?)",
            (name, body),
        )
    return f"OK: note id={cursor.lastrowid}"


def get_note(db_path: Path, note_id: int) -> str:
    with open_conn(db_path) as conn:
        row = conn.execute(
            "SELECT id, name, body, created_at, updated_at FROM notes WHERE id = ?",
            (note_id,),
        ).fetchone()
    if row is None:
        return "(无结果)"
    return (
        f"id={row['id']}\n"
        f"name={row['name']}\n"
        f"body={row['body']}\n"
        f"created_at={row['created_at']}\n"
        f"updated_at={row['updated_at']}"
    )


def update_note(db_path: Path, note_id: int, fields: dict) -> str:
    updates: list[str] = []
    params: list[object] = []
    if "name" in fields:
        updates.append("name = ?")
        params.append(str(fields["name"]).strip())
    if "body" in fields:
        updates.append("body = ?")
        params.append(str(fields["body"]))
    if not updates:
        return "Error: 至少提供 name 或 body"
    updates.append("updated_at = datetime('now')")
    params.append(note_id)
    with open_conn(db_path) as conn:
        cursor = conn.execute(
            f"UPDATE notes SET {', '.join(updates)} WHERE id = ?", params
        )
    return "OK: updated" if cursor.rowcount else "OK: not found"


def list_notes(db_path: Path, limit: int = 20, offset: int = 0) -> str:
    with open_conn(db_path) as conn:
        rows = conn.execute(
            "SELECT id, name, created_at FROM notes ORDER BY id DESC LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
    if not rows:
        return "(空)"
    return "\n".join(f"[{r['id']}] {r['name']} ({r['created_at']})" for r in rows)


def search_notes(db_path: Path, query: str, limit: int = 20, offset: int = 0) -> str:
    like = f"%{query}%"
    with open_conn(db_path) as conn:
        rows = conn.execute(
            "SELECT id, name, created_at FROM notes WHERE name LIKE ? OR body LIKE ? ORDER BY id DESC LIMIT ? OFFSET ?",
            (like, like, limit, offset),
        ).fetchall()
    if not rows:
        return "(无结果)"
    return "\n".join(f"[{r['id']}] {r['name']} ({r['created_at']})" for r in rows)


def delete_note(db_path: Path, note_id: int) -> str:
    with open_conn(db_path) as conn:
        cursor = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    return "OK: deleted" if cursor.rowcount else "OK: not found"
