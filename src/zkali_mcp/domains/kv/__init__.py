"""语义字典模块：同义词、分类词、触发词归一化。"""

from .service import add_dict, get_dict, get_dict_by_name, list_dict, update_dict, delete_dict

__all__ = ["add_dict", "get_dict", "get_dict_by_name", "list_dict", "update_dict", "delete_dict"]
