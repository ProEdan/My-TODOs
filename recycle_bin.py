"""
回收站模块。

实现任务的软删除、回收站管理和恢复功能。
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dataclasses import asdict
import logging

logger = logging.getLogger(__name__)


class RecycleBin:
    """回收站类。"""

    def __init__(self, retention_days: int = 30):
        """
        初始化回收站。

        Args:
            retention_days: 回收站保留天数（超过此天数会自动删除）
        """
        self.retention_days = retention_days
        self.deleted_items: List[Dict] = []

    def move_to_recycle(self, todo_item: Dict, hard_delete_time: Optional[datetime] = None) -> None:
        """
        将任务移至回收站。

        Args:
            todo_item: 待办项（字典格式）
            hard_delete_time: 硬删除时间，默认为 retention_days 天后
        """
        if hard_delete_time is None:
            hard_delete_time = datetime.now() + timedelta(days=self.retention_days)

        deleted_record = {
            "todo_item": todo_item,
            "deleted_at": datetime.now(),
            "hard_delete_at": hard_delete_time,
        }

        self.deleted_items.append(deleted_record)
        logger.info(f"移至回收站: {todo_item.get('text', 'Unknown')} (ID: {todo_item.get('id')})")

    def restore_item(self, todo_id: str) -> Optional[Dict]:
        """
        从回收站恢复任务。

        Args:
            todo_id: 任务ID

        Returns:
            恢复的任务，找不到返回 None
        """
        for i, record in enumerate(self.deleted_items):
            if record["todo_item"].get("id") == todo_id:
                item = self.deleted_items.pop(i)
                logger.info(f"从回收站恢复: {item['todo_item'].get('text')} (ID: {todo_id})")
                return item["todo_item"]

        logger.warning(f"回收站中找不到任务: {todo_id}")
        return None

    def restore_all(self) -> List[Dict]:
        """
        恢复所有任务。

        Returns:
            恢复的所有任务
        """
        items = [record["todo_item"] for record in self.deleted_items]
        self.deleted_items.clear()
        logger.info(f"恢复了 {len(items)} 个任务")
        return items

    def permanently_delete(self, todo_id: str) -> bool:
        """
        永久删除任务。

        Args:
            todo_id: 任务ID

        Returns:
            是否成功删除
        """
        for i, record in enumerate(self.deleted_items):
            if record["todo_item"].get("id") == todo_id:
                item = self.deleted_items.pop(i)
                logger.warning(
                    f"永久删除: {item['todo_item'].get('text')} (ID: {todo_id})"
                )
                return True

        logger.warning(f"回收站中找不到任务: {todo_id}")
        return False

    def permanently_delete_all(self) -> int:
        """
        清空回收站。

        Returns:
            删除的任务数量
        """
        count = len(self.deleted_items)
        self.deleted_items.clear()
        logger.warning(f"清空回收站，删除 {count} 个任务")
        return count

    def clean_expired(self) -> int:
        """
        清理过期的任务（超过保留期限）。

        Returns:
            清理的任务数量
        """
        now = datetime.now()
        original_count = len(self.deleted_items)

        self.deleted_items = [
            record
            for record in self.deleted_items
            if record["hard_delete_at"] > now
        ]

        removed_count = original_count - len(self.deleted_items)
        if removed_count > 0:
            logger.info(f"清理了 {removed_count} 个过期任务")
        return removed_count

    def get_recycle_bin(self) -> List[Dict]:
        """
        获取回收站中的所有任务。

        Returns:
            任务列表
        """
        return [record["todo_item"] for record in self.deleted_items]

    def get_recycle_bin_details(self) -> List[Dict]:
        """
        获取回收站详细信息（包含删除时间等）。

        Returns:
            详细信息列表
        """
        details = []
        for record in self.deleted_items:
            item = record["todo_item"].copy()
            item["deleted_at"] = record["deleted_at"]
            item["hard_delete_at"] = record["hard_delete_at"]
            item["days_until_permanent_delete"] = (
                record["hard_delete_at"] - datetime.now()
            ).days
            details.append(item)

        # 按删除时间排序（最新的在前）
        details.sort(key=lambda x: x["deleted_at"], reverse=True)
        return details

    def get_item_by_id(self, todo_id: str) -> Optional[Dict]:
        """
        通过ID获取回收站中的任务。

        Args:
            todo_id: 任务ID

        Returns:
            任务信息或 None
        """
        for record in self.deleted_items:
            if record["todo_item"].get("id") == todo_id:
                return record["todo_item"]
        return None

    def get_statistics(self) -> Dict:
        """
        获取回收站统计信息。

        Returns:
            统计信息字典
        """
        now = datetime.now()
        expired_count = 0

        for record in self.deleted_items:
            if record["hard_delete_at"] < now:
                expired_count += 1

        total_items = len(self.deleted_items)
        will_expire_soon = sum(
            1 for record in self.deleted_items
            if now < record["hard_delete_at"] < now + timedelta(days=3)
        )

        return {
            "total_items": total_items,
            "will_expire_soon": will_expire_soon,
            "expired_items": expired_count,
            "retention_days": self.retention_days,
            "oldest_item": (
                self.deleted_items[0]["todo_item"].get("text", "Unknown")
                if self.deleted_items
                else None
            ),
        }

    def search(self, keyword: str) -> List[Dict]:
        """
        在回收站中搜索任务。

        Args:
            keyword: 搜索关键词

        Returns:
            匹配的任务列表
        """
        keyword_lower = keyword.lower()
        results = []

        for record in self.deleted_items:
            item = record["todo_item"]
            text = item.get("text", "").lower()
            notes = item.get("notes", "").lower()

            if keyword_lower in text or keyword_lower in notes:
                results.append(item)

        logger.debug(f"在回收站中搜索 '{keyword}'，找到 {len(results)} 个结果")
        return results

    def format_recycle_bin(self) -> str:
        """
        格式化回收站信息。

        Returns:
            人类可读的回收站字符串
        """
        stats = self.get_statistics()
        lines = [
            "🗑️ 回收站",
            f"  总项目: {stats['total_items']}",
            f"  即将过期: {stats['will_expire_soon']}",
            f"  已过期: {stats['expired_items']}",
            f"  保留期限: {stats['retention_days']} 天",
        ]

        if stats["total_items"] > 0:
            lines.append("\n📋 最近删除的项目:")
            details = self.get_recycle_bin_details()
            for item in details[:5]:  # 最多显示 5 个
                days_until = item["days_until_permanent_delete"]
                text = item["text"][:30]  # 截断过长的文本
                lines.append(f"  • {text} (还有 {days_until} 天)")

        return "\n".join(lines)

    def export_recycle_bin(self) -> Dict:
        """
        导出回收站为字典格式。

        Returns:
            回收站字典
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "total_items": len(self.deleted_items),
            "retention_days": self.retention_days,
            "items": self.get_recycle_bin_details(),
        }
