"""
应用程序全局状态管理模块。

集中管理所有全局变量，避免在多个地方分散定义。
"""

from typing import List, Optional, Any
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class AppState:
    """应用程序全局状态容器。"""

    # 待办事项相关
    delete_pile: List[Any] = field(default_factory=list)
    """被标记为完成的待办事项列表（待删除）"""

    position_locked: bool = False
    """窗口位置是否被锁定"""

    todo_list_unfold_state: bool = True
    """待办列表是否展开显示"""

    add_todo_unfold_state: bool = False
    """添加待办面板是否展开显示"""

    # UI 组件引用
    settings_parser: Optional[Any] = None
    """设置解析器实例"""

    todos_parser: Optional[Any] = None
    """待办事项解析器实例"""

    todo_list_unfold_button: Optional[Any] = None
    """待办列表展开/隐藏按钮"""

    add_todo_unfold_button: Optional[Any] = None
    """添加待办展开/隐藏按钮"""

    settings_unfold_button: Optional[Any] = None
    """设置展开/隐藏按钮"""

    addTODO: Optional[callable] = None
    """添加待办的方法引用"""

    def reset(self) -> None:
        """重置所有状态为默认值。"""
        self.delete_pile = []
        self.position_locked = False
        self.todo_list_unfold_state = True
        self.add_todo_unfold_state = False
        logger.info("应用状态已重置")

    def get_stats(self) -> dict:
        """
        获取应用统计信息。

        Returns:
            包含应用状态统计的字典
        """
        return {
            "delete_pile_size": len(self.delete_pile),
            "position_locked": self.position_locked,
            "todo_list_visible": self.todo_list_unfold_state,
            "add_todo_visible": self.add_todo_unfold_state,
        }


# 全局应用状态实例
_app_state = AppState()


def get_app_state() -> AppState:
    """
    获取全局应用状态实例。

    Returns:
        应用程序全局状态对象
    """
    return _app_state


def reset_app_state() -> None:
    """重置应用程序全局状态。"""
    _app_state.reset()
