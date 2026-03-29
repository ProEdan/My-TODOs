"""
待办统计和仪表板模块。

提供实时的统计信息和分析功能。
"""

from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from collections import Counter
from todo_model import TodoItem, Priority, TodoStatus
import logging

logger = logging.getLogger(__name__)


class TodoStatistics:
    """待办统计类。"""

    def __init__(self, todos: List[TodoItem]):
        """
        初始化统计器。

        Args:
            todos: 待办列表
        """
        self.todos = todos

    def get_total_count(self) -> int:
        """获取待办总数。"""
        return len(self.todos)

    def get_completed_count(self) -> int:
        """获取已完成的待办数。"""
        return sum(1 for todo in self.todos if todo.is_completed)

    def get_active_count(self) -> int:
        """获取活跃的待办数。"""
        return sum(1 for todo in self.todos if not todo.is_completed)

    def get_completion_rate(self) -> float:
        """
        获取完成率（百分比）。

        Returns:
            完成率 0-100
        """
        if self.get_total_count() == 0:
            return 0.0
        return (self.get_completed_count() / self.get_total_count()) * 100

    def get_priority_distribution(self) -> Dict[str, int]:
        """
        获取优先级分布。

        Returns:
            {'low': 数量, 'medium': 数量, 'high': 数量}
        """
        distribution = Counter(todo.priority for todo in self.todos if not todo.is_completed)
        return {
            Priority.LOW.value: distribution.get(Priority.LOW.value, 0),
            Priority.MEDIUM.value: distribution.get(Priority.MEDIUM.value, 0),
            Priority.HIGH.value: distribution.get(Priority.HIGH.value, 0),
        }

    def get_priority_distribution_completed(self) -> Dict[str, int]:
        """获取已完成待办的优先级分布。"""
        distribution = Counter(todo.priority for todo in self.todos if todo.is_completed)
        return {
            Priority.LOW.value: distribution.get(Priority.LOW.value, 0),
            Priority.MEDIUM.value: distribution.get(Priority.MEDIUM.value, 0),
            Priority.HIGH.value: distribution.get(Priority.HIGH.value, 0),
        }

    def get_category_distribution(self) -> Dict[str, int]:
        """
        获取分类分布。

        Returns:
            {'分类名': 数量, ...}
        """
        distribution = Counter(
            todo.category for todo in self.todos if not todo.is_completed
        )
        return dict(distribution.most_common())

    def get_category_completion(self) -> Dict[str, float]:
        """
        获取每个分类的完成率。

        Returns:
            {'分类名': 完成率, ...}
        """
        categories = {}
        for category in set(todo.category for todo in self.todos):
            todos_in_category = [
                todo for todo in self.todos if todo.category == category
            ]
            if todos_in_category:
                completed = sum(1 for todo in todos_in_category if todo.is_completed)
                rate = (completed / len(todos_in_category)) * 100
                categories[category] = rate
        return categories

    def get_overdue_count(self) -> int:
        """获取逾期的待办数。"""
        return sum(1 for todo in self.todos if todo.is_overdue())

    def get_due_today_count(self) -> int:
        """获取今天截止的待办数。"""
        today = datetime.now().date().isoformat()
        return sum(
            1
            for todo in self.todos
            if todo.due_date
            and todo.due_date.startswith(today)
            and not todo.is_completed
        )

    def get_due_this_week_count(self) -> int:
        """获取本周截止的待办数。"""
        now = datetime.now()
        week_end = (now + timedelta(days=7)).date()
        return sum(
            1
            for todo in self.todos
            if todo.due_date
            and not todo.is_completed
            and datetime.fromisoformat(todo.due_date).date() <= week_end
        )

    def get_average_priority(self) -> float:
        """
        获取平均优先级（不含已完成）。

        Returns:
            1-3 之间的平均值
        """
        active_todos = [todo for todo in self.todos if not todo.is_completed]
        if not active_todos:
            return 0.0
        total_priority = sum(todo.get_priority_level() for todo in active_todos)
        return total_priority / len(active_todos)

    def get_creation_trend(self, days: int = 7) -> Dict[str, int]:
        """
        获取创建趋势（最近 N 天）。

        Args:
            days: 天数

        Returns:
            {'日期': 创建数, ...}
        """
        trend = {}
        for i in range(days, -1, -1):
            date = (datetime.now() - timedelta(days=i)).date().isoformat()
            count = sum(
                1
                for todo in self.todos
                if todo.created_at.startswith(date)
            )
            trend[date] = count
        return trend

    def get_completion_trend(self, days: int = 7) -> Dict[str, int]:
        """
        获取完成趋势（最近 N 天）。

        Args:
            days: 天数

        Returns:
            {'日期': 完成数, ...}
        """
        trend = {}
        for i in range(days, -1, -1):
            date = (datetime.now() - timedelta(days=i)).date().isoformat()
            count = sum(
                1
                for todo in self.todos
                if todo.completed_at and todo.completed_at.startswith(date)
            )
            trend[date] = count
        return trend

    def get_pomodoro_stats(self) -> Dict[str, int]:
        """
        获取番茄计时统计。

        Returns:
            {'estimated': 总计划, 'completed': 已完成}
        """
        estimated = sum(todo.estimated_pomodoros for todo in self.todos)
        completed = sum(todo.completed_pomodoros for todo in self.todos)
        return {"estimated": estimated, "completed": completed}

    def get_most_used_tags(self, top_n: int = 10) -> List[Tuple[str, int]]:
        """
        获取最常用的标签。

        Args:
            top_n: 返回前 N 个

        Returns:
            [(标签, 使用次数), ...]
        """
        tag_counter = Counter()
        for todo in self.todos:
            tag_counter.update(todo.tags)
        return tag_counter.most_common(top_n)

    def get_dashboard(self) -> Dict[str, any]:
        """
        获取完整的仪表板数据。

        Returns:
            包含所有统计信息的字典
        """
        return {
            "基本统计": {
                "总数": self.get_total_count(),
                "活跃": self.get_active_count(),
                "已完成": self.get_completed_count(),
                "完成率%": round(self.get_completion_rate(), 2),
            },
            "优先级": self.get_priority_distribution(),
            "分类分布": self.get_category_distribution(),
            "分类完成率": {
                cat: round(rate, 2)
                for cat, rate in self.get_category_completion().items()
            },
            "时间相关": {
                "逾期": self.get_overdue_count(),
                "今天截止": self.get_due_today_count(),
                "本周截止": self.get_due_this_week_count(),
            },
            "番茄计时": self.get_pomodoro_stats(),
            "最常用标签": self.get_most_used_tags(5),
        }

    def print_dashboard(self) -> None:
        """打印仪表板到控制台。"""
        dashboard = self.get_dashboard()
        logger.info("=" * 50)
        logger.info("📊 待办事项仪表板")
        logger.info("=" * 50)

        for section, data in dashboard.items():
            logger.info(f"\n【{section}】")
            if isinstance(data, dict):
                for key, value in data.items():
                    logger.info(f"  {key}: {value}")
            elif isinstance(data, list):
                for item in data:
                    logger.info(f"  {item}")
            else:
                logger.info(f"  {data}")
