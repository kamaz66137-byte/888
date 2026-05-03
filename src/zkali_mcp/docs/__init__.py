"""知识库模块：管理文档片段与检索入口。"""

from .service import add_docs, get_docs, list_docs, update_docs, delete_docs

__all__ = ["add_docs", "get_docs", "list_docs", "update_docs", "delete_docs"]
