"""
快捷键系统模块。

实现键盘快捷键映射和处理。
"""

from typing import Callable, Dict, List, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class KeyModifier(Enum):
    """按键修饰符。"""

    NONE = 0
    CTRL = 1
    SHIFT = 2
    ALT = 4
    CTRL_SHIFT = 3
    CTRL_ALT = 5
    SHIFT_ALT = 6
    CTRL_SHIFT_ALT = 7


class ShortcutAction(Enum):
    """快捷键动作枚举。"""

    ADD_TODO = "add_todo"
    DELETE_TODO = "delete_todo"
    COMPLETE_TODO = "complete_todo"
    SEARCH = "search"
    EXPORT = "export"
    SETTINGS = "settings"
    UNDO = "undo"
    REDO = "redo"
    REFRESH = "refresh"
    QUIT = "quit"
    NEXT_TODO = "next_todo"
    PREV_TODO = "prev_todo"
    EDIT_TODO = "edit_todo"
    CLEAR_SEARCH = "clear_search"


class Shortcut:
    """快捷键类。"""

    def __init__(
        self,
        key: str,
        modifier: KeyModifier,
        action: ShortcutAction,
        description: str,
        callback: Optional[Callable] = None,
    ):
        """
        初始化快捷键。

        Args:
            key: 主键（如 'n', 'k', 'f'）
            modifier: 修饰符
            action: 动作
            description: 描述
            callback: 执行回调
        """
        self.key = key.lower()
        self.modifier = modifier
        self.action = action
        self.description = description
        self.callback = callback
        self.enabled = True

    def __repr__(self) -> str:
        """返回快捷键的字符串表示。"""
        mod_str = self._modifier_to_string()
        return f"<Shortcut {mod_str}+{self.key.upper()} -> {self.action.value}>"

    def _modifier_to_string(self) -> str:
        """将修饰符转为字符串。"""
        if self.modifier == KeyModifier.NONE:
            return ""
        elif self.modifier == KeyModifier.CTRL:
            return "Ctrl"
        elif self.modifier == KeyModifier.SHIFT:
            return "Shift"
        elif self.modifier == KeyModifier.ALT:
            return "Alt"
        elif self.modifier == KeyModifier.CTRL_SHIFT:
            return "Ctrl+Shift"
        elif self.modifier == KeyModifier.CTRL_ALT:
            return "Ctrl+Alt"
        elif self.modifier == KeyModifier.SHIFT_ALT:
            return "Shift+Alt"
        elif self.modifier == KeyModifier.CTRL_SHIFT_ALT:
            return "Ctrl+Shift+Alt"
        return ""

    def get_display_text(self) -> str:
        """
        获取显示文本。

        Returns:
            快捷键显示文本
        """
        mod_str = self._modifier_to_string()
        if mod_str:
            return f"{mod_str}+{self.key.upper()}"
        return self.key.upper()


class KeyboardShortcutManager:
    """快捷键管理器类。"""

    def __init__(self):
        """初始化快捷键管理器。"""
        self.shortcuts: Dict[str, Shortcut] = {}
        self._setup_default_shortcuts()

    def _setup_default_shortcuts(self) -> None:
        """设置默认快捷键。"""
        defaults = [
            # 基础操作
            Shortcut("n", KeyModifier.CTRL, ShortcutAction.ADD_TODO, "新建任务"),
            Shortcut("k", KeyModifier.CTRL, ShortcutAction.DELETE_TODO, "删除任务"),
            Shortcut("d", KeyModifier.CTRL, ShortcutAction.COMPLETE_TODO, "完成任务"),
            Shortcut("f", KeyModifier.CTRL, ShortcutAction.SEARCH, "搜索"),
            Shortcut("e", KeyModifier.CTRL, ShortcutAction.EXPORT, "导出"),
            # 编辑操作
            Shortcut("z", KeyModifier.CTRL, ShortcutAction.UNDO, "撤销"),
            Shortcut("y", KeyModifier.CTRL, ShortcutAction.REDO, "重做"),
            Shortcut("r", KeyModifier.CTRL, ShortcutAction.REFRESH, "刷新"),
            # 导航
            Shortcut("j", KeyModifier.CTRL, ShortcutAction.NEXT_TODO, "下一个任务"),
            Shortcut("k", KeyModifier.CTRL_SHIFT, ShortcutAction.PREV_TODO, "上一个任务"),
            # 其他
            Shortcut("q", KeyModifier.CTRL, ShortcutAction.QUIT, "退出"),
            Shortcut("Escape", KeyModifier.NONE, ShortcutAction.CLEAR_SEARCH, "清除搜索"),
        ]

        for shortcut in defaults:
            self.register_shortcut(shortcut)

    def register_shortcut(self, shortcut: Shortcut) -> None:
        """
        注册快捷键。

        Args:
            shortcut: 快捷键对象
        """
        key = self._get_shortcut_key(shortcut.key, shortcut.modifier)
        self.shortcuts[key] = shortcut
        logger.info(f"注册快捷键: {shortcut.get_display_text()} -> {shortcut.action.value}")

    def unregister_shortcut(self, key: str, modifier: KeyModifier) -> None:
        """
        注销快捷键。

        Args:
            key: 主键
            modifier: 修饰符
        """
        shortcut_key = self._get_shortcut_key(key, modifier)
        if shortcut_key in self.shortcuts:
            del self.shortcuts[shortcut_key]
            logger.info(f"注销快捷键: {shortcut_key}")

    def trigger_shortcut(self, key: str, modifier: KeyModifier = KeyModifier.NONE) -> Optional[ShortcutAction]:
        """
        触发快捷键。

        Args:
            key: 主键
            modifier: 修饰符

        Returns:
            对应的动作
        """
        shortcut_key = self._get_shortcut_key(key, modifier)

        if shortcut_key not in self.shortcuts:
            logger.warning(f"快捷键未注册: {shortcut_key}")
            return None

        shortcut = self.shortcuts[shortcut_key]

        if not shortcut.enabled:
            logger.debug(f"快捷键已禁用: {shortcut_key}")
            return None

        # 执行回调
        if shortcut.callback:
            try:
                shortcut.callback()
                logger.debug(f"执行快捷键回调: {shortcut_key}")
            except Exception as e:
                logger.error(f"执行快捷键回调失败: {e}")

        logger.info(f"触发快捷键: {shortcut.get_display_text()} ({shortcut.action.value})")
        return shortcut.action

    def get_shortcut(self, key: str, modifier: KeyModifier) -> Optional[Shortcut]:
        """
        获取快捷键。

        Args:
            key: 主键
            modifier: 修饰符

        Returns:
            快捷键对象或 None
        """
        shortcut_key = self._get_shortcut_key(key, modifier)
        return self.shortcuts.get(shortcut_key)

    def set_shortcut_callback(
        self, key: str, modifier: KeyModifier, callback: Callable
    ) -> None:
        """
        设置快捷键回调。

        Args:
            key: 主键
            modifier: 修饰符
            callback: 回调函数
        """
        shortcut = self.get_shortcut(key, modifier)
        if shortcut:
            shortcut.callback = callback
            logger.debug(f"设置快捷键回调: {shortcut.get_display_text()}")

    def enable_shortcut(self, key: str, modifier: KeyModifier) -> None:
        """
        启用快捷键。

        Args:
            key: 主键
            modifier: 修饰符
        """
        shortcut = self.get_shortcut(key, modifier)
        if shortcut:
            shortcut.enabled = True
            logger.debug(f"启用快捷键: {shortcut.get_display_text()}")

    def disable_shortcut(self, key: str, modifier: KeyModifier) -> None:
        """
        禁用快捷键。

        Args:
            key: 主键
            modifier: 修饰符
        """
        shortcut = self.get_shortcut(key, modifier)
        if shortcut:
            shortcut.enabled = False
            logger.debug(f"禁用快捷键: {shortcut.get_display_text()}")

    def get_all_shortcuts(self) -> List[Shortcut]:
        """
        获取所有快捷键。

        Returns:
            快捷键列表
        """
        return list(self.shortcuts.values())

    def get_shortcuts_by_action(self, action: ShortcutAction) -> List[Shortcut]:
        """
        按动作获取快捷键。

        Args:
            action: 动作

        Returns:
            快捷键列表
        """
        return [s for s in self.shortcuts.values() if s.action == action]

    def format_shortcuts(self) -> str:
        """
        格式化快捷键。

        Returns:
            人类可读的快捷键字符串
        """
        lines = ["⌨️ 快捷键列表:"]

        # 按动作分组
        action_groups: Dict[str, List[Shortcut]] = {}
        for shortcut in self.get_all_shortcuts():
            action_name = shortcut.action.value
            if action_name not in action_groups:
                action_groups[action_name] = []
            action_groups[action_name].append(shortcut)

        for action_name, shortcuts in action_groups.items():
            lines.append(f"  {action_name}:")
            for shortcut in shortcuts:
                status = "✓" if shortcut.enabled else "✗"
                lines.append(
                    f"    {status} {shortcut.get_display_text()}: {shortcut.description}"
                )

        return "\n".join(lines)

    @staticmethod
    def _get_shortcut_key(key: str, modifier: KeyModifier) -> str:
        """
        生成快捷键的唯一键。

        Args:
            key: 主键
            modifier: 修饰符

        Returns:
            唯一键字符串
        """
        return f"{modifier.name}:{key.lower()}"
