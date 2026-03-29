"""
待办导出和备份模块。

支持 JSON、CSV 和备份功能。
"""

import json
import csv
from typing import List
from datetime import datetime
from pathlib import Path
from todo_model import TodoItem
import logging

logger = logging.getLogger(__name__)


class TodoExporter:
    """待办导出器。"""

    @staticmethod
    def export_to_json(todos: List[TodoItem], filepath: str) -> bool:
        """
        导出待办为 JSON 格式。

        Args:
            todos: 待办列表
            filepath: 导出文件路径

        Returns:
            是否成功
        """
        try:
            data = [todo.to_dict() for todo in todos]
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"已导出 {len(todos)} 个待办到 {filepath}")
            return True
        except Exception as e:
            logger.error(f"导出 JSON 失败: {e}")
            return False

    @staticmethod
    def export_to_csv(todos: List[TodoItem], filepath: str) -> bool:
        """
        导出待办为 CSV 格式。

        Args:
            todos: 待办列表
            filepath: 导出文件路径

        Returns:
            是否成功
        """
        try:
            if not todos:
                logger.warning("没有待办可导出")
                return False

            with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
                fieldnames = [
                    "ID",
                    "文本",
                    "优先级",
                    "分类",
                    "标签",
                    "截止日期",
                    "状态",
                    "完成时间",
                    "创建时间",
                    "备注",
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for todo in todos:
                    writer.writerow(
                        {
                            "ID": todo.id,
                            "文本": todo.text,
                            "优先级": todo.priority,
                            "分类": todo.category,
                            "标签": ",".join(todo.tags),
                            "截止日期": todo.due_date or "",
                            "状态": todo.status,
                            "完成时间": todo.completed_at or "",
                            "创建时间": todo.created_at,
                            "备注": todo.notes,
                        }
                    )
            logger.info(f"已导出 {len(todos)} 个待办到 {filepath}")
            return True
        except Exception as e:
            logger.error(f"导出 CSV 失败: {e}")
            return False

    @staticmethod
    def export_to_markdown(todos: List[TodoItem], filepath: str) -> bool:
        """
        导出待办为 Markdown 格式。

        Args:
            todos: 待办列表
            filepath: 导出文件路径

        Returns:
            是否成功
        """
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("# 待办事项导出\n\n")
                f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"总数: {len(todos)}\n\n")

                # 按分类分组
                categories = {}
                for todo in todos:
                    if todo.category not in categories:
                        categories[todo.category] = []
                    categories[todo.category].append(todo)

                for category, items in sorted(categories.items()):
                    f.write(f"## {category}\n\n")
                    for todo in items:
                        status = "✅" if todo.is_completed else "⬜"
                        priority = {
                            "low": "🟢",
                            "medium": "🟡",
                            "high": "🔴",
                        }.get(todo.priority, "⭕")

                        f.write(f"{status} {priority} **{todo.text}**\n")
                        if todo.tags:
                            f.write(f"  标签: {', '.join(todo.tags)}\n")
                        if todo.due_date:
                            f.write(f"  截止: {todo.due_date}\n")
                        if todo.notes:
                            f.write(f"  备注: {todo.notes}\n")
                        f.write("\n")

            logger.info(f"已导出 {len(todos)} 个待办到 {filepath}")
            return True
        except Exception as e:
            logger.error(f"导出 Markdown 失败: {e}")
            return False

    @staticmethod
    def create_backup(todos: List[TodoItem], backup_dir: str = "./backups") -> str:
        """
        创建备份。

        Args:
            todos: 待办列表
            backup_dir: 备份目录

        Returns:
            备份文件路径
        """
        try:
            Path(backup_dir).mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"{backup_dir}/todos_backup_{timestamp}.json"

            TodoExporter.export_to_json(todos, backup_file)
            logger.info(f"已创建备份: {backup_file}")
            return backup_file
        except Exception as e:
            logger.error(f"创建备份失败: {e}")
            return ""

    @staticmethod
    def import_from_json(filepath: str) -> List[TodoItem]:
        """
        从 JSON 文件导入。

        Args:
            filepath: 文件路径

        Returns:
            导入的待办列表
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            todos = [TodoItem.from_dict(item) for item in data]
            logger.info(f"已从 {filepath} 导入 {len(todos)} 个待办")
            return todos
        except Exception as e:
            logger.error(f"导入 JSON 失败: {e}")
            return []

    @staticmethod
    def list_backups(backup_dir: str = "./backups") -> List[str]:
        """
        列出所有备份文件。

        Args:
            backup_dir: 备份目录

        Returns:
            备份文件列表
        """
        try:
            backup_path = Path(backup_dir)
            if not backup_path.exists():
                return []
            backups = sorted(
                backup_path.glob("todos_backup_*.json"), key=lambda x: x.stat().st_mtime, reverse=True
            )
            return [str(b) for b in backups]
        except Exception as e:
            logger.error(f"列出备份失败: {e}")
            return []
