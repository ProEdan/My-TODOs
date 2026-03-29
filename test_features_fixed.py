"""
综合单元测试文件。

测试所有新功能模块。
"""

import unittest
from datetime import datetime, timedelta
from todo_model import TodoItem, Priority, TodoStatus
from search_engine import TodoSearchEngine
from statistics import TodoStatistics
from exporter import TodoExporter
from pomodoro_timer import PomodoroTimer
from reminder_system import ReminderSystem
from keyboard_shortcuts import KeyboardShortcutManager, KeyModifier, ShortcutAction
from recycle_bin import RecycleBin
from todo_manager import EnhancedTodoManager


class TestTodoModel(unittest.TestCase):
    """测试待办项模型。"""

    def setUp(self) -> None:
        """设置测试前置条件。"""
        self.todo = TodoItem(
            text="测试任务",
            priority=Priority.HIGH.value,
            category="工作",
            tags=["重要", "紧急"],
            notes="这是一个测试备注",
        )

    def test_todo_creation(self) -> None:
        """测试任务创建。"""
        self.assertEqual(self.todo.text, "测试任务")
        self.assertEqual(self.todo.priority, Priority.HIGH.value)
        self.assertEqual(self.todo.status, TodoStatus.ACTIVE.value)
        self.assertIsNotNone(self.todo.id)

    def test_todo_completion(self) -> None:
        """测试任务完成。"""
        self.todo.mark_completed()
        self.assertEqual(self.todo.status, TodoStatus.COMPLETED.value)
        self.assertIsNotNone(self.todo.completed_at)

    def test_todo_serialization(self) -> None:
        """测试任务序列化。"""
        todo_dict = self.todo.to_dict()
        self.assertIn("id", todo_dict)
        self.assertIn("text", todo_dict)
        self.assertEqual(todo_dict["text"], "测试任务")

    def test_todo_deserialization(self) -> None:
        """测试任务反序列化。"""
        todo_dict = self.todo.to_dict()
        restored = TodoItem.from_dict(todo_dict)
        self.assertEqual(restored.id, self.todo.id)
        self.assertEqual(restored.text, self.todo.text)


class TestSearchEngine(unittest.TestCase):
    """测试搜索引擎。"""

    def setUp(self) -> None:
        """设置测试前置条件。"""
        self.todos = [
            TodoItem(text="完成项目", priority=Priority.HIGH.value, category="工作"),
            TodoItem(text="购买用品", priority=Priority.LOW.value, category="生活"),
            TodoItem(text="修复缺陷", priority=Priority.HIGH.value, category="工作"),
        ]
        self.engine = TodoSearchEngine()
        self.engine.set_todos(self.todos)

    def test_search_by_text(self) -> None:
        """测试文本搜索。"""
        results = self.engine.search_by_text("项目")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].text, "完成项目")

    def test_filter_by_priority(self) -> None:
        """测试优先级过滤。"""
        results = self.engine.filter_by_priority(Priority.HIGH.value)
        self.assertEqual(len(results), 2)

    def test_filter_by_category(self) -> None:
        """测试分类过滤。"""
        results = self.engine.filter_by_category("工作")
        self.assertEqual(len(results), 2)

    def test_sort_by_priority(self) -> None:
        """测试优先级排序。"""
        results = self.engine.sort_by("priority")
        self.assertEqual(results[0].priority, Priority.HIGH.value)


class TestStatistics(unittest.TestCase):
    """测试统计模块。"""

    def setUp(self) -> None:
        """设置测试前置条件。"""
        self.todos = [
            TodoItem(text="任务1", priority=Priority.HIGH.value),
            TodoItem(text="任务2", priority=Priority.MEDIUM.value),
            TodoItem(text="任务3", priority=Priority.LOW.value),
        ]
        # 标记一个为完成
        self.todos[0].mark_completed()
        self.stats = TodoStatistics(self.todos)

    def test_total_count(self) -> None:
        """测试总计数。"""
        self.assertEqual(self.stats.get_total_count(), 3)

    def test_completed_count(self) -> None:
        """测试完成计数。"""
        self.assertEqual(self.stats.get_completed_count(), 1)

    def test_completion_rate(self) -> None:
        """测试完成率。"""
        rate = self.stats.get_completion_rate()
        self.assertAlmostEqual(rate, 1/3, places=2)

    def test_priority_distribution(self) -> None:
        """测试优先级分布。"""
        dist = self.stats.get_priority_distribution()
        self.assertEqual(dist.get("high", 0), 1)
        self.assertEqual(dist.get("medium", 0), 1)
        self.assertEqual(dist.get("low", 0), 1)


class TestExporter(unittest.TestCase):
    """测试导出器。"""

    def setUp(self) -> None:
        """设置测试前置条件。"""
        self.todos = [
            TodoItem(text="任务1", category="工作"),
            TodoItem(text="任务2", category="生活"),
        ]
        self.exporter = TodoExporter()

    def test_export_to_json(self) -> None:
        """测试导出为JSON。"""
        result = self.exporter.export_to_json(self.todos)
        self.assertIsNotNone(result)
        self.assertIn("任务1", result)


class TestPomodoro(unittest.TestCase):
    """测试番茄计时器。"""

    def setUp(self) -> None:
        """设置测试前置条件。"""
        self.timer = PomodoroTimer(work_duration=1, break_duration=1)

    def test_timer_start_stop(self) -> None:
        """测试计时器启动和停止。"""
        self.assertFalse(self.timer.is_running)
        self.timer.start()
        self.assertTrue(self.timer.is_running)
        self.timer.stop()
        self.assertFalse(self.timer.is_running)

    def test_timer_remaining_time(self) -> None:
        """测试剩余时间。"""
        self.timer.start()
        remaining = self.timer.get_remaining_time()
        self.assertTrue(0 <= remaining <= 60)

    def test_timer_status(self) -> None:
        """测试计时器状态。"""
        status = self.timer.get_status()
        self.assertIn("is_running", status)
        self.assertIn("is_work_time", status)
        self.assertIn("completed_pomodoros", status)


class TestReminderSystem(unittest.TestCase):
    """测试提醒系统。"""

    def setUp(self) -> None:
        """设置测试前置条件。"""
        self.system = ReminderSystem()

    def test_add_reminder(self) -> None:
        """测试添加提醒。"""
        due_date = datetime.now() + timedelta(days=3)
        self.system.add_reminder("1", "测试任务", due_date, 1)
        self.assertEqual(len(self.system.reminders), 1)

    def test_remove_reminder(self) -> None:
        """测试移除提醒。"""
        due_date = datetime.now() + timedelta(days=3)
        self.system.add_reminder("1", "测试任务", due_date, 1)
        self.system.remove_reminder("1")
        self.assertEqual(len(self.system.reminders), 0)

    def test_get_upcoming_reminders(self) -> None:
        """测试获取即将到来的提醒。"""
        due_date = datetime.now() + timedelta(days=3)
        self.system.add_reminder("1", "测试任务", due_date, 1)
        upcoming = self.system.get_upcoming_reminders(days=7)
        self.assertGreater(len(upcoming), 0)


class TestKeyboardShortcuts(unittest.TestCase):
    """测试快捷键系统。"""

    def setUp(self) -> None:
        """设置测试前置条件。"""
        self.manager = KeyboardShortcutManager()

    def test_shortcut_registration(self) -> None:
        """测试快捷键注册。"""
        shortcuts = self.manager.get_all_shortcuts()
        self.assertGreater(len(shortcuts), 0)

    def test_trigger_shortcut(self) -> None:
        """测试触发快捷键。"""
        action = self.manager.trigger_shortcut("n", KeyModifier.CTRL)
        self.assertEqual(action, ShortcutAction.ADD_TODO)

    def test_disable_shortcut(self) -> None:
        """测试禁用快捷键。"""
        self.manager.disable_shortcut("n", KeyModifier.CTRL)
        action = self.manager.trigger_shortcut("n", KeyModifier.CTRL)
        self.assertIsNone(action)


class TestRecycleBin(unittest.TestCase):
    """测试回收站。"""

    def setUp(self) -> None:
        """设置测试前置条件。"""
        self.bin = RecycleBin()
        self.item = {"id": "1", "text": "测试项目"}

    def test_move_to_recycle(self) -> None:
        """测试移至回收站。"""
        self.bin.move_to_recycle(self.item)
        self.assertEqual(len(self.bin.deleted_items), 1)

    def test_restore_item(self) -> None:
        """测试恢复项目。"""
        self.bin.move_to_recycle(self.item)
        restored = self.bin.restore_item("1")
        self.assertIsNotNone(restored)
        self.assertEqual(restored["text"], "测试项目")

    def test_permanently_delete(self) -> None:
        """测试永久删除。"""
        self.bin.move_to_recycle(self.item)
        success = self.bin.permanently_delete("1")
        self.assertTrue(success)
        self.assertEqual(len(self.bin.deleted_items), 0)

    def test_search_recycle(self) -> None:
        """测试在回收站中搜索。"""
        self.bin.move_to_recycle(self.item)
        results = self.bin.search("测试")
        self.assertEqual(len(results), 1)


class TestEnhancedTodoManager(unittest.TestCase):
    """测试增强型待办项管理器。"""

    def setUp(self) -> None:
        """设置测试前置条件。"""
        self.manager = EnhancedTodoManager("test_todos.json")

    def tearDown(self) -> None:
        """清理测试后置条件。"""
        import os
        if os.path.exists("test_todos.json"):
            os.remove("test_todos.json")

    def test_add_todo(self) -> None:
        """测试添加任务。"""
        todo = self.manager.add_todo("测试任务", priority=Priority.HIGH)
        self.assertIsNotNone(todo)
        self.assertEqual(todo.text, "测试任务")

    def test_delete_todo(self) -> None:
        """测试删除任务。"""
        todo = self.manager.add_todo("测试任务")
        success = self.manager.delete_todo(todo.id)
        self.assertTrue(success)

    def test_complete_todo(self) -> None:
        """测试完成任务。"""
        todo = self.manager.add_todo("测试任务")
        completed = self.manager.complete_todo(todo.id)
        self.assertEqual(completed.status, TodoStatus.COMPLETED.value)

    def test_search_todos(self) -> None:
        """测试搜索任务。"""
        self.manager.add_todo("测试任务1")
        self.manager.add_todo("测试任务2")
        results = self.manager.search_todos("任务")
        self.assertEqual(len(results), 2)

    def test_get_dashboard(self) -> None:
        """测试获取仪表板。"""
        self.manager.add_todo("测试任务")
        dashboard = self.manager.get_dashboard()
        self.assertIn("statistics", dashboard)
        self.assertIn("reminders", dashboard)


if __name__ == "__main__":
    unittest.main()
