"""
待办事项解析器模块。

用于读取、写入和管理待办事项列表。
"""

from pathlib import Path
from typing import List
import logging

logger = logging.getLogger(__name__)

# 待办事项文件的标记
TODO_MARK = "<TODO-START-MARK>"


class TODOParser:
    """解析和管理待办事项列表。"""

    def __init__(self, path: str) -> None:
        """
        初始化待办事项解析器。

        Args:
            path: 待办事项配置文件的路径

        Raises:
            FileNotFoundError: 如果文件不存在且无法创建
        """
        self.path = Path(path)
        self.todos: List[str] = []
        
        # 确保文件存在，如果不存在则创建
        if not self.path.exists():
            try:
                self.path.touch(exist_ok=True)
                logger.info(f"创建新的待办事项文件: {self.path}")
            except IOError as e:
                logger.error(f"无法创建待办事项文件: {e}")
                raise

        self.read()

    def read(self) -> None:
        """
        从待办事项文件读取所有待办事项。

        Raises:
            IOError: 如果文件读取失败
        """
        try:
            with open(self.path, "r", encoding="utf-8") as file:
                content = file.read()
                self.todos = content.split(TODO_MARK)[1:] if TODO_MARK in content else []
            logger.debug(f"成功读取 {len(self.todos)} 个待办事项")
        except IOError as e:
            logger.error(f"读取待办事项文件失败: {e}")
            self.todos = []

    def write(self) -> None:
        """
        将所有待办事项写入文件。

        Raises:
            IOError: 如果文件写入失败
        """
        try:
            with open(self.path, "w", encoding="utf-8") as file:
                for item in self.todos:
                    file.write(f"{TODO_MARK}{item}")
            logger.debug(f"成功保存 {len(self.todos)} 个待办事项")
        except IOError as e:
            logger.error(f"保存待办事项文件失败: {e}")
            raise

    def add(self, text: str) -> None:
        """
        添加新的待办事项。

        Args:
            text: 待办事项的文本内容

        Raises:
            ValueError: 如果文本为空
        """
        if not text or not isinstance(text, str):
            raise ValueError("待办事项文本不能为空或不是字符串类型")
        
        self.todos.append(text)
        logger.debug(f"已添加待办事项: {text[:50]}...")

    def remove(self, index: int) -> None:
        """
        删除指定索引的待办事项。

        Args:
            index: 待办事项的索引

        Raises:
            IndexError: 如果索引超出范围
        """
        if 0 <= index < len(self.todos):
            removed = self.todos.pop(index)
            logger.debug(f"已删除待办事项: {removed[:50]}...")
        else:
            raise IndexError(f"待办事项索引 {index} 超出范围")

    def get_all(self) -> List[str]:
        """
        获取所有待办事项。

        Returns:
            包含所有待办事项的列表
        """
        return self.todos.copy()

    def clear(self) -> None:
        """清空所有待办事项。"""
        count = len(self.todos)
        self.todos.clear()
        logger.info(f"已清空 {count} 个待办事项")
