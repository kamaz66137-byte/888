"""提示词模块：管理系统/任务/工具提示词模板。"""

from .service import add_prompt, get_prompt, get_prompt_by_name, list_prompt, update_prompt, render_prompt, delete_prompt

__all__ = ["add_prompt", "get_prompt", "get_prompt_by_name", "list_prompt", "update_prompt", "render_prompt", "delete_prompt"]
