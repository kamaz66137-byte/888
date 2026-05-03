"""笔记模块：轻量笔记读写。"""

from .service import add_note, get_note, update_note, list_notes, search_notes, delete_note

__all__ = ["add_note", "get_note", "update_note", "list_notes", "search_notes", "delete_note"]
