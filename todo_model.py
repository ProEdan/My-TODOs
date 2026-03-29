"""
增强型待办事项模型。

支持优先级、分类、截止日期、完成状态、标签等高级功能。
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from enum import Enum
import json
import logging
import uuid

logger = logging.getLogger(__name__)


class Priority(Enum):
    """优先级枚举。"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TodoStatus(Enum):
    """待办状态枚举。"""
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


@dataclass
class TodoItem:
    """增强型待办事项数据类。"""

    text: str

    # 基本信息
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    # 优先级和分类
    priority: str = Priority.MEDIUM.value
    category: str = "默认"
    tags: List[str] = field(default_factory=list)

    # 时间相关
    due_date: Optional[str] = None  # ISO 格式日期
    completed_at: Optional[str] = None

    # 状态
    status: str = TodoStatus.ACTIVE.value
    is_completed: bool = False

    # 提醒
    remind_before_days: int = 0  # 截止日期前多少天提醒

    # 番茄计时
    estimated_pomodoros: int = 0  # 预计番茄数
    completed_pomodoros: int = 0  # 已完成番茄数

    # 备注
    notes: str = ""

    def __post_init__(self) -> None:
        """标准化可能传入的 Enum 值，避免后续序列化失败。"""
        if isinstance(self.priority, Priority):
            self.priority = self.priority.value
        if isinstance(self.status, TodoStatus):
            self.status = self.status.value

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典。"""
        data = asdict(self)
        # 双保险：即便对象被外部直接改成 Enum，也可稳定序列化。
        if isinstance(data.get("priority"), Priority):
            data["priority"] = data["priority"].value
        if isinstance(data.get("status"), TodoStatus):
            data["status"] = data["status"].value
        return data

    def to_json(self) -> str:
        """转换为 JSON 字符串。"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "TodoItem":
        """从字典创建。"""
        return TodoItem(**data)

    @staticmethod
    def from_json(json_str: str) -> "TodoItem":
        """从 JSON 字符串创建。"""
        data = json.loads(json_str)
        return TodoItem.from_dict(data)

    def is_overdue(self) -> bool:
        """检查是否逾期。"""
        if not self.due_date or self.is_completed:
            return False
        due = datetime.fromisoformat(self.due_date)
        return datetime.now() > due

    def days_until_due(self) -> Optional[int]:
        """获取距离截止日期的天数。"""
        if not self.due_date:
            return None
        due = datetime.fromisoformat(self.due_date)
        delta = (due.date() - datetime.now().date()).days
        return delta

    def should_remind(self) -> bool:
        """是否应该提醒。"""
        if not self.due_date or self.is_completed:
            return False
        days_until = self.days_until_due()
        return days_until is not None and 0 <= days_until <= self.remind_before_days

    def get_priority_level(self) -> int:
        """获取优先级数值（用于排序）。"""
        priority_map = {
            Priority.LOW.value: 1,
            Priority.MEDIUM.value: 2,
            Priority.HIGH.value: 3,
        }
        return priority_map.get(self.priority, 2)

    def mark_completed(self) -> None:
        """标记为完成。"""
        self.is_completed = True
        self.status = TodoStatus.COMPLETED.value
        self.completed_at = datetime.now().isoformat()
        logger.debug(f"待办已标记为完成: {self.text[:50]}")

    def mark_active(self) -> None:
        """标记为活跃。"""
        self.is_completed = False
        self.status = TodoStatus.ACTIVE.value
        self.completed_at = None
        logger.debug(f"待办已标记为活跃: {self.text[:50]}")

    def add_tag(self, tag: str) -> None:
        """添加标签。"""
        if tag not in self.tags:
            self.tags.append(tag)
            logger.debug(f"已添加标签: {tag} 到 {self.text[:50]}")

    def remove_tag(self, tag: str) -> None:
        """删除标签。"""
        if tag in self.tags:
            self.tags.remove(tag)
            logger.debug(f"已移除标签: {tag} 从 {self.text[:50]}")

    def add_pomodoro(self, count: int = 1) -> None:
        """增加完成的番茄数。"""
        self.completed_pomodoros = min(
            self.completed_pomodoros + count, self.estimated_pomodoros
        )

    def __str__(self) -> str:
        """字符串表示。"""
        priority_emoji = {
            Priority.LOW.value: "🟢",
            Priority.MEDIUM.value: "🟡",
            Priority.HIGH.value: "🔴",
        }
        status_emoji = "✅" if self.is_completed else "📝"
        return (
            f"{status_emoji} [{priority_emoji.get(self.priority, '📝')}] "
            f"{self.text} "
            f"(#{self.category})"
        )

    def __lt__(self, other: "TodoItem") -> bool:
        """用于排序的比较。"""
        # 优先按优先级排序（高优先级在前）
        if self.get_priority_level() != other.get_priority_level():
            return self.get_priority_level() > other.get_priority_level()
        # 然后按创建时间排序（新的在前）
        return self.created_at > other.created_at
