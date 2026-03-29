"""
待办事项搜索模块。

提供强大的搜索、过滤和排序功能。
"""

from typing import List, Optional, Callable
from datetime import datetime, timedelta
from todo_model import TodoItem, Priority, TodoStatus
import logging

logger = logging.getLogger(__name__)


class TodoSearchEngine:
    """待办事项搜索引擎。"""

    def __init__(self):
        """初始化搜索引擎。"""
        self.todos: List[TodoItem] = []

    def set_todos(self, todos: List[TodoItem]) -> None:
        """设置待办列表。"""
        self.todos = todos

    def search_by_text(self, keyword: str) -> List[TodoItem]:
        """
        按文本内容搜索。

        支持模糊搜索。

        Args:
            keyword: 搜索关键词

        Returns:
            匹配的待办列表
        """
        keyword = keyword.lower()
        results = []
        for todo in self.todos:
            if (
                keyword in todo.text.lower()
                or keyword in todo.notes.lower()
                or any(keyword in tag.lower() for tag in todo.tags)
            ):
                results.append(todo)
        logger.debug(f"文本搜索: '{keyword}' 找到 {len(results)} 个结果")
        return results

    def filter_by_priority(self, priority: str) -> List[TodoItem]:
        """
        按优先级过滤。

        Args:
            priority: 优先级 ('low', 'medium', 'high')

        Returns:
            指定优先级的待办列表
        """
        results = [todo for todo in self.todos if todo.priority == priority]
        logger.debug(f"优先级过滤: {priority} 找到 {len(results)} 个结果")
        return results

    def filter_by_category(self, category: str) -> List[TodoItem]:
        """
        按分类过滤。

        Args:
            category: 分类名称

        Returns:
            指定分类的待办列表
        """
        results = [todo for todo in self.todos if todo.category == category]
        logger.debug(f"分类过滤: {category} 找到 {len(results)} 个结果")
        return results

    def filter_by_status(self, status: str) -> List[TodoItem]:
        """
        按状态过滤。

        Args:
            status: 状态 ('active', 'completed', 'archived')

        Returns:
            指定状态的待办列表
        """
        results = [todo for todo in self.todos if todo.status == status]
        logger.debug(f"状态过滤: {status} 找到 {len(results)} 个结果")
        return results

    def filter_by_tag(self, tag: str) -> List[TodoItem]:
        """
        按标签过滤。

        Args:
            tag: 标签名称

        Returns:
            包含指定标签的待办列表
        """
        results = [todo for todo in self.todos if tag in todo.tags]
        logger.debug(f"标签过滤: {tag} 找到 {len(results)} 个结果")
        return results

    def filter_by_due_date_range(
        self, start_date: str, end_date: str
    ) -> List[TodoItem]:
        """
        按截止日期范围过滤。

        Args:
            start_date: 开始日期 (ISO 格式)
            end_date: 结束日期 (ISO 格式)

        Returns:
            在指定日期范围内的待办列表
        """
        start = datetime.fromisoformat(start_date).date()
        end = datetime.fromisoformat(end_date).date()

        results = []
        for todo in self.todos:
            if todo.due_date:
                due = datetime.fromisoformat(todo.due_date).date()
                if start <= due <= end:
                    results.append(todo)

        logger.debug(
            f"日期范围过滤: {start_date} 到 {end_date} 找到 {len(results)} 个结果"
        )
        return results

    def get_overdue(self) -> List[TodoItem]:
        """
        获取所有逾期的待办。

        Returns:
            逾期的待办列表
        """
        results = [todo for todo in self.todos if todo.is_overdue()]
        logger.debug(f"找到 {len(results)} 个逾期待办")
        return results

    def get_due_today(self) -> List[TodoItem]:
        """
        获取今天截止的待办。

        Returns:
            今天截止的待办列表
        """
        today = datetime.now().date().isoformat()
        results = [
            todo
            for todo in self.todos
            if todo.due_date and todo.due_date.startswith(today) and not todo.is_completed
        ]
        logger.debug(f"找到 {len(results)} 个今天截止的待办")
        return results

    def get_upcoming(self, days: int = 7) -> List[TodoItem]:
        """
        获取最近 N 天内截止的待办。

        Args:
            days: 天数

        Returns:
            未来 N 天内截止的待办列表
        """
        now = datetime.now()
        future = (now + timedelta(days=days)).date()

        results = []
        for todo in self.todos:
            if todo.due_date and not todo.is_completed:
                due = datetime.fromisoformat(todo.due_date).date()
                if now.date() <= due <= future:
                    results.append(todo)

        logger.debug(f"找到 {len(results)} 个即将截止的待办")
        return results

    def sort_by(
        self, todos: List[TodoItem], key: str = "priority", reverse: bool = True
    ) -> List[TodoItem]:
        """
        对待办进行排序。

        Args:
            todos: 待办列表
            key: 排序键 ('priority', 'due_date', 'created_at', 'category')
            reverse: 是否反向排序

        Returns:
            排序后的待办列表
        """
        if key == "priority":
            return sorted(todos, key=lambda x: x.get_priority_level(), reverse=reverse)
        elif key == "due_date":
            return sorted(
                todos,
                key=lambda x: x.due_date or "9999-12-31",
                reverse=reverse,
            )
        elif key == "created_at":
            return sorted(todos, key=lambda x: x.created_at, reverse=reverse)
        elif key == "category":
            return sorted(todos, key=lambda x: x.category, reverse=reverse)
        else:
            return todos

    def advanced_search(
        self,
        text: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> List[TodoItem]:
        """
        高级搜索（多条件组合）。

        Args:
            text: 文本搜索关键词
            priority: 优先级
            category: 分类
            status: 状态
            tag: 标签

        Returns:
            符合所有条件的待办列表
        """
        results = self.todos.copy()

        if text:
            text_lower = text.lower()
            results = [
                todo
                for todo in results
                if text_lower in todo.text.lower()
                or text_lower in todo.notes.lower()
                or any(text_lower in t.lower() for t in todo.tags)
            ]

        if priority:
            results = [todo for todo in results if todo.priority == priority]

        if category:
            results = [todo for todo in results if todo.category == category]

        if status:
            results = [todo for todo in results if todo.status == status]

        if tag:
            results = [todo for todo in results if tag in todo.tags]

        logger.debug(f"高级搜索找到 {len(results)} 个结果")
        return results

    def get_all_categories(self) -> List[str]:
        """获取所有分类。"""
        categories = set(todo.category for todo in self.todos)
        return sorted(list(categories))

    def get_all_tags(self) -> List[str]:
        """获取所有标签。"""
        tags = set()
        for todo in self.todos:
            tags.update(todo.tags)
        return sorted(list(tags))
