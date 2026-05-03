"""项目模块：项目实体、进度状态与生命周期管理。"""

from .queries import get_project, get_project_status, list_projects, project_exists, project_is_active
from .service import (
    add_project, update_project, get_project_detail, list_projects as list_projects_str,
    delete_project, add_progress, update_progress, list_progress, stats_progress,
    add_todo, update_todo, done_todo, list_todos, delete_todo,
)

__all__ = [
    "get_project", "get_project_status", "list_projects", "project_exists", "project_is_active",
    "add_project", "update_project", "get_project_detail", "list_projects_str",
    "delete_project", "add_progress", "update_progress", "list_progress", "stats_progress",
    "add_todo", "update_todo", "done_todo", "list_todos", "delete_todo",
]
