"""
增强型待办项管理器。

集成所有功能的核心管理器类。
"""

import json
from typing import List, Optional, Dict, Callable
from datetime import datetime
import logging

from todo_model import TodoItem, Priority, TodoStatus
from search_engine import TodoSearchEngine
from statistics import TodoStatistics
from exporter import TodoExporter
from pomodoro_timer import PomodoroTimer
from reminder_system import ReminderSystem
from keyboard_shortcuts import KeyboardShortcutManager, KeyModifier, ShortcutAction
from recycle_bin import RecycleBin

logger = logging.getLogger(__name__)


class EnhancedTodoManager:
    """增强型待办项管理器。"""

    def __init__(self, storage_file: str = "todos.json"):
        """
        初始化管理器。

        Args:
            storage_file: 存储文件路径
        """
        self.storage_file = storage_file
        self.todos: List[TodoItem] = []

        # 初始化各个子系统
        self.search_engine = TodoSearchEngine()
        self.statistics = TodoStatistics(self.todos)
        self.exporter = TodoExporter()
        self.pomodoro = PomodoroTimer()
        self.reminders = ReminderSystem()
        self.shortcuts = KeyboardShortcutManager()
        self.recycle_bin = RecycleBin()

        # 加载已有数据
        self.load_todos()
        self._sync_views()

        logger.info("增强型待办项管理器已初始化")

    def _sync_views(self) -> None:
        """同步各子系统持有的待办列表引用。"""
        self.search_engine.set_todos(self.todos)
        self.statistics.todos = self.todos

    def add_todo(
        self,
        text: str,
        priority: Priority = Priority.MEDIUM,
        category: str = "默认",
        tags: Optional[List[str]] = None,
        due_date: Optional[datetime] = None,
        estimated_pomodoros: int = 1,
        notes: str = "",
    ) -> TodoItem:
        """
        添加新任务。

        Args:
            text: 任务文本
            priority: 优先级
            category: 分类
            tags: 标签
            due_date: 截止日期
            estimated_pomodoros: 估计番茄数
            notes: 备注

        Returns:
            新创建的 TodoItem
        """
        due_date_value = due_date.isoformat() if isinstance(due_date, datetime) else due_date

        todo = TodoItem(
            text=text,
            priority=priority,
            category=category,
            tags=tags or [],
            due_date=due_date_value,
            estimated_pomodoros=estimated_pomodoros,
            notes=notes,
        )

        self.todos.append(todo)
        self._sync_views()
        logger.info(f"添加任务: {text}")

        # 如果设置了截止日期，添加提醒
        if isinstance(due_date, datetime):
            self.reminders.add_reminder(
                todo.id, text, due_date, remind_before_days=1
            )

        self.save_todos()
        return todo

    def delete_todo(self, todo_id: str, permanently: bool = False) -> bool:
        """
        删除任务。

        Args:
            todo_id: 任务ID
            permanently: 是否永久删除（True）或移至回收站（False）

        Returns:
            是否成功删除
        """
        todo = self.get_todo_by_id(todo_id)
        if not todo:
            logger.warning(f"任务未找到: {todo_id}")
            return False

        if permanently:
            self.todos = [t for t in self.todos if t.id != todo_id]
            self._sync_views()
            logger.info(f"永久删除任务: {todo.text}")
        else:
            # 移至回收站
            todo.status = TodoStatus.ARCHIVED
            self.todos = [t for t in self.todos if t.id != todo_id]
            self._sync_views()
            self.recycle_bin.move_to_recycle(todo.to_dict())
            logger.info(f"删除任务（移至回收站）: {todo.text}")

        self.save_todos()
        return True

    def update_todo(
        self,
        todo_id: str,
        text: Optional[str] = None,
        priority: Optional[Priority] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        due_date: Optional[datetime] = None,
        notes: Optional[str] = None,
    ) -> Optional[TodoItem]:
        """
        更新任务。

        Args:
            todo_id: 任务ID
            text: 新文本
            priority: 新优先级
            category: 新分类
            tags: 新标签
            due_date: 新截止日期
            notes: 新备注

        Returns:
            更新后的 TodoItem 或 None
        """
        todo = self.get_todo_by_id(todo_id)
        if not todo:
            logger.warning(f"任务未找到: {todo_id}")
            return None

        if text:
            todo.text = text
        if priority:
            todo.priority = priority
        if category:
            todo.category = category
        if tags is not None:
            todo.tags = tags
        if due_date:
            todo.due_date = due_date.isoformat() if isinstance(due_date, datetime) else due_date
        if notes is not None:
            todo.notes = notes

        logger.info(f"更新任务: {todo.text}")
        self.save_todos()
        return todo

    def complete_todo(self, todo_id: str) -> Optional[TodoItem]:
        """
        完成任务。

        Args:
            todo_id: 任务ID

        Returns:
            完成的 TodoItem 或 None
        """
        todo = self.get_todo_by_id(todo_id)
        if not todo:
            logger.warning(f"任务未找到: {todo_id}")
            return None

        todo.mark_completed()
        logger.info(f"任务已完成: {todo.text}")
        self.save_todos()
        return todo

    def get_todo_by_id(self, todo_id: str) -> Optional[TodoItem]:
        """
        通过ID获取任务。

        Args:
            todo_id: 任务ID

        Returns:
            TodoItem 或 None
        """
        for todo in self.todos:
            if todo.id == todo_id:
                return todo
        return None

    def get_all_todos(self) -> List[TodoItem]:
        """
        获取所有任务。

        Returns:
            所有任务列表
        """
        return self.todos.copy()

    def search_todos(self, query: str) -> List[TodoItem]:
        """
        搜索任务。

        Args:
            query: 搜索查询

        Returns:
            匹配的任务列表
        """
        results = self.search_engine.search_by_text(query)
        logger.info(f"搜索 '{query}'，找到 {len(results)} 个结果")
        return results

    def filter_todos(
        self,
        priority: Optional[Priority] = None,
        category: Optional[str] = None,
        status: Optional[TodoStatus] = None,
        tag: Optional[str] = None,
    ) -> List[TodoItem]:
        """
        按条件过滤任务。

        Args:
            priority: 优先级
            category: 分类
            status: 状态
            tag: 标签

        Returns:
            过滤后的任务列表
        """
        results = self.todos.copy()

        priority_value = priority.value if isinstance(priority, Priority) else priority
        status_value = status.value if isinstance(status, TodoStatus) else status

        if priority_value:
            results = [todo for todo in results if todo.priority == priority_value]
        if category:
            results = [todo for todo in results if todo.category == category]
        if status_value:
            results = [todo for todo in results if todo.status == status_value]
        if tag:
            results = [todo for todo in results if tag in todo.tags]

        logger.debug(f"过滤任务，得到 {len(results)} 个结果")
        return results

    def get_overdue_todos(self) -> List[TodoItem]:
        """
        获取逾期任务。

        Returns:
            逾期任务列表
        """
        return self.search_engine.get_overdue()

    def get_today_todos(self) -> List[TodoItem]:
        """
        获取今日任务。

        Returns:
            今日任务列表
        """
        return self.search_engine.get_due_today()

    def get_upcoming_todos(self, days: int = 7) -> List[TodoItem]:
        """
        获取即将到期的任务。

        Args:
            days: 天数范围

        Returns:
            即将到期的任务列表
        """
        return self.search_engine.get_upcoming(days)

    def get_dashboard(self) -> Dict:
        """
        获取仪表板信息。

        Returns:
            仪表板字典
        """
        return {
            "statistics": self.statistics.get_dashboard(),
            "reminders": self.reminders.get_reminder_statistics(),
            "recycle_bin": self.recycle_bin.get_statistics(),
            "pomodoro": self.pomodoro.get_status(),
        }

    def export_todos(self, format: str = "json", filepath: Optional[str] = None) -> bool:
        """
        导出任务。

        Args:
            format: 导出格式（json/csv/markdown）
            filepath: 导出文件路径

        Returns:
            导出内容或文件路径
        """
        if format == "json":
            return self.exporter.export_to_json(self.todos, filepath)
        elif format == "csv":
            return self.exporter.export_to_csv(self.todos, filepath)
        elif format == "markdown":
            return self.exporter.export_to_markdown(self.todos, filepath)
        else:
            logger.warning(f"不支持的导出格式: {format}")
            return False

    def create_backup(self) -> str:
        """
        创建备份。

        Returns:
            备份文件路径
        """
        return self.exporter.create_backup(self.todos)

    def restore_backup(self, backup_file: str) -> bool:
        """
        恢复备份。

        Args:
            backup_file: 备份文件路径

        Returns:
            是否成功恢复
        """
        try:
            todos_data = self.exporter.import_from_json(backup_file)
            self.todos = todos_data
            self._sync_views()
            self.save_todos()
            logger.info(f"从备份恢复: {backup_file}")
            return True
        except Exception as e:
            logger.error(f"恢复备份失败: {e}")
            return False

    def save_todos(self) -> None:
        """保存任务到文件。"""
        try:
            self._sync_views()
            todos_data = [todo.to_dict() for todo in self.todos]
            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump(todos_data, f, ensure_ascii=False, indent=2)
            logger.debug(f"保存了 {len(self.todos)} 个任务")
        except Exception as e:
            logger.error(f"保存任务失败: {e}")

    def load_todos(self) -> None:
        """从文件加载任务。"""
        try:
            with open(self.storage_file, "r", encoding="utf-8") as f:
                todos_data = json.load(f)
                self.todos = [TodoItem.from_dict(data) for data in todos_data]
            self._sync_views()
            logger.info(f"加载了 {len(self.todos)} 个任务")
        except FileNotFoundError:
            logger.info("任务文件不存在，创建新文件")
            self.todos = []
            self._sync_views()
        except Exception as e:
            logger.error(f"加载任务失败: {e}")
            self.todos = []
            self._sync_views()

    def register_shortcut_callback(
        self, action: ShortcutAction, callback: Callable
    ) -> None:
        """
        注册快捷键回调。

        Args:
            action: 动作
            callback: 回调函数
        """
        for shortcut in self.shortcuts.get_shortcuts_by_action(action):
            shortcut.callback = callback

    def format_summary(self) -> str:
        """
        格式化摘要信息。

        Returns:
            人类可读的摘要字符串
        """
        stats = self.statistics.get_dashboard()
        basic = stats.get("基本统计", {})
        priority_dist = stats.get("优先级", {})
        lines = [
            "📊 待办项目摘要",
            f"  总数: {basic.get('总数', 0)}",
            f"  已完成: {basic.get('已完成', 0)}",
            f"  进行中: {basic.get('活跃', 0)}",
            f"  完成率: {basic.get('完成率%', 0):.1f}%",
            "",
            "🎯 优先级分布:",
            f"  高: {priority_dist.get('high', 0)}",
            f"  中: {priority_dist.get('medium', 0)}",
            f"  低: {priority_dist.get('low', 0)}",
        ]

        overdue = self.get_overdue_todos()
        if overdue:
            lines.append(f"\n⚠️ 逾期任务: {len(overdue)} 个")

        today = self.get_today_todos()
        if today:
            lines.append(f"📅 今日任务: {len(today)} 个")

        return "\n".join(lines)
