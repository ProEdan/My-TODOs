"""
提醒/通知系统模块。

实现任务提醒和通知功能。
"""

from datetime import datetime, timedelta
from typing import Callable, Optional, List, Dict
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class Reminder:
    """提醒项类。"""

    todo_id: str
    todo_text: str
    due_date: datetime
    remind_before_days: int
    created_at: datetime


class ReminderSystem:
    """提醒系统类。"""

    def __init__(self):
        """初始化提醒系统。"""
        self.reminders: List[Reminder] = []
        self.notification_history: List[Dict] = []
        self.on_reminder: Optional[Callable[[Reminder], None]] = None

    def add_reminder(
        self,
        todo_id: str,
        todo_text: str,
        due_date: datetime,
        remind_before_days: int,
    ) -> None:
        """
        添加提醒。

        Args:
            todo_id: 任务ID
            todo_text: 任务文本
            due_date: 截止日期
            remind_before_days: 提前几天提醒
        """
        reminder = Reminder(
            todo_id=todo_id,
            todo_text=todo_text,
            due_date=due_date,
            remind_before_days=remind_before_days,
            created_at=datetime.now(),
        )
        self.reminders.append(reminder)
        logger.info(f"添加提醒: {todo_text} (在 {due_date.strftime('%Y-%m-%d')} 之前 {remind_before_days} 天)")

    def remove_reminder(self, todo_id: str) -> None:
        """
        移除提醒。

        Args:
            todo_id: 任务ID
        """
        self.reminders = [r for r in self.reminders if r.todo_id != todo_id]
        logger.info(f"移除提醒: {todo_id}")

    def check_reminders(self) -> List[Reminder]:
        """
        检查需要提醒的任务。

        Returns:
            需要提醒的任务列表
        """
        now = datetime.now()
        pending_reminders = []

        for reminder in self.reminders:
            reminder_time = reminder.due_date - timedelta(days=reminder.remind_before_days)

            # 检查是否应该提醒
            if now >= reminder_time and now < reminder.due_date:
                pending_reminders.append(reminder)
                self._record_notification(reminder)

                # 触发回调
                if self.on_reminder:
                    self.on_reminder(reminder)

        return pending_reminders

    def get_upcoming_reminders(self, days: int = 7) -> List[Dict]:
        """
        获取即将到来的提醒。

        Args:
            days: 查看几天内的提醒

        Returns:
            提醒列表
        """
        now = datetime.now()
        upcoming = []

        for reminder in self.reminders:
            days_until = (reminder.due_date - now).days
            if 0 < days_until <= days:
                upcoming.append({
                    "todo_id": reminder.todo_id,
                    "todo_text": reminder.todo_text,
                    "due_date": reminder.due_date,
                    "days_until": days_until,
                    "remind_before_days": reminder.remind_before_days,
                })

        # 按距离排序
        upcoming.sort(key=lambda x: x["days_until"])
        return upcoming

    def get_overdue_reminders(self) -> List[Dict]:
        """
        获取逾期的提醒。

        Returns:
            逾期提醒列表
        """
        now = datetime.now()
        overdue = []

        for reminder in self.reminders:
            if reminder.due_date < now:
                days_overdue = (now - reminder.due_date).days
                overdue.append({
                    "todo_id": reminder.todo_id,
                    "todo_text": reminder.todo_text,
                    "due_date": reminder.due_date,
                    "days_overdue": days_overdue,
                })

        # 按逾期时间排序（最长逾期在前）
        overdue.sort(key=lambda x: x["days_overdue"], reverse=True)
        return overdue

    def get_today_reminders(self) -> List[Dict]:
        """
        获取今天的提醒。

        Returns:
            今天的提醒列表
        """
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        today_reminders = []
        for reminder in self.reminders:
            if today_start <= reminder.due_date < today_end:
                today_reminders.append({
                    "todo_id": reminder.todo_id,
                    "todo_text": reminder.todo_text,
                    "due_date": reminder.due_date,
                    "hours_until": (reminder.due_date - now).total_seconds() / 3600,
                })

        today_reminders.sort(key=lambda x: x["hours_until"])
        return today_reminders

    def clear_old_reminders(self, days: int = 30) -> int:
        """
        清理旧提醒（超期 30 天以上）。

        Args:
            days: 清理超过 N 天的提醒

        Returns:
            清理的提醒数量
        """
        now = datetime.now()
        original_count = len(self.reminders)

        self.reminders = [
            r for r in self.reminders if (now - r.due_date).days <= days
        ]

        removed_count = original_count - len(self.reminders)
        logger.info(f"清理了 {removed_count} 个旧提醒")
        return removed_count

    def _record_notification(self, reminder: Reminder) -> None:
        """
        记录通知。

        Args:
            reminder: 提醒对象
        """
        self.notification_history.append({
            "todo_id": reminder.todo_id,
            "todo_text": reminder.todo_text,
            "due_date": reminder.due_date,
            "notification_time": datetime.now(),
            "message": f"提醒: 任务 '{reminder.todo_text}' 将在 {reminder.due_date.strftime('%Y-%m-%d')} 截止",
        })

    def get_notification_history(self, limit: int = 50) -> List[Dict]:
        """
        获取通知历史。

        Args:
            limit: 返回最近多少条通知

        Returns:
            通知历史列表
        """
        return self.notification_history[-limit:]

    def get_reminder_statistics(self) -> Dict:
        """
        获取提醒统计信息。

        Returns:
            统计信息字典
        """
        now = datetime.now()
        today_reminders = self.get_today_reminders()
        upcoming = self.get_upcoming_reminders(7)
        overdue = self.get_overdue_reminders()

        return {
            "total_reminders": len(self.reminders),
            "today_reminders": len(today_reminders),
            "upcoming_reminders": len(upcoming),
            "overdue_reminders": len(overdue),
            "notification_count": len(self.notification_history),
            "last_notification": (
                self.notification_history[-1]["notification_time"]
                if self.notification_history
                else None
            ),
        }

    def format_reminders(self) -> str:
        """
        格式化提醒信息。

        Returns:
            人类可读的提醒字符串
        """
        stats = self.get_reminder_statistics()
        lines = [
            "🔔 提醒统计",
            f"  总提醒数: {stats['total_reminders']}",
            f"  今日提醒: {stats['today_reminders']}",
            f"  即将到期: {stats['upcoming_reminders']}",
            f"  已逾期: {stats['overdue_reminders']}",
        ]

        today = self.get_today_reminders()
        if today:
            lines.append("\n📌 今日提醒:")
            for reminder in today[:5]:  # 最多显示 5 个
                hours = int(reminder["hours_until"])
                lines.append(f"  • {reminder['todo_text']} (还有 {hours}h)")

        return "\n".join(lines)
