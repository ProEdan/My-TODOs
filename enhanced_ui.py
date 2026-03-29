"""Production-ready desktop UI powered by EnhancedTodoManager."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from PyQt5.QtCore import QDate, QTimer, Qt
from PyQt5.QtGui import QGuiApplication, QKeySequence
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QDateEdit,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QShortcut,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from todo_manager import EnhancedTodoManager
from todo_model import Priority, TodoItem, TodoStatus


PRIORITY_ORDER = {
    "high": 0,
    "medium": 1,
    "low": 2,
}


class TODOApplication(QMainWindow):
    """Main application window for the enhanced todo product."""

    def __init__(self) -> None:
        super().__init__()
        self.manager = EnhancedTodoManager("todos.json")
        self._dragging = False
        self._drag_offset = None
        self._is_pinned = True
        self._is_minimal = False
        self._is_transparent = False

        self.setWindowTitle("桌面待办插件")
        self.resize(420, 640)
        self.setMinimumSize(360, 520)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)

        self._pomodoro_timer = QTimer(self)
        self._pomodoro_timer.timeout.connect(self._tick_pomodoro)

        self._build_ui()
        self._bind_shortcuts()
        self._apply_widget_style()
        self._refresh_all()

    def _build_ui(self) -> None:
        root = QWidget(self)
        self.setCentralWidget(root)

        main = QVBoxLayout(root)
        main.setContentsMargins(10, 10, 10, 10)
        main.setSpacing(8)

        main.addWidget(self._build_title_bar())

        main.addWidget(self._build_add_panel())
        main.addWidget(self._build_toolbar_panel())
        main.addWidget(self._build_list_panel(), 1)
        main.addWidget(self._build_right_panel())

    def _build_title_bar(self) -> QGroupBox:
        box = QGroupBox()
        row = QHBoxLayout(box)
        row.setContentsMargins(8, 4, 8, 4)

        title = QLabel("桌面待办")
        title.setObjectName("WidgetTitle")

        self.pin_btn = QPushButton("置顶")
        self.pin_btn.setCheckable(True)
        self.pin_btn.setChecked(True)
        self.pin_btn.clicked.connect(self._toggle_pin)

        self.compact_btn = QPushButton("极简")
        self.compact_btn.setCheckable(True)
        self.compact_btn.setChecked(False)
        self.compact_btn.clicked.connect(self._toggle_minimal)

        self.transparent_btn = QPushButton("半透")
        self.transparent_btn.setCheckable(True)
        self.transparent_btn.setChecked(False)
        self.transparent_btn.clicked.connect(self._toggle_transparent)

        close_btn = QPushButton("×")
        close_btn.clicked.connect(self.close)

        row.addWidget(title)
        row.addStretch(1)
        row.addWidget(self.pin_btn)
        row.addWidget(self.compact_btn)
        row.addWidget(self.transparent_btn)
        row.addWidget(close_btn)
        return box

    def _build_add_panel(self) -> QGroupBox:
        box = QGroupBox("新建任务")
        self.add_panel = box
        layout = QGridLayout(box)
        layout.setHorizontalSpacing(6)
        layout.setVerticalSpacing(6)

        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("输入待办内容...")

        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["高", "中", "低"])
        self.priority_combo.setCurrentText("中")

        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("分类")

        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("标签，逗号分隔")

        self.due_date = QDateEdit()
        self.due_date.setDisplayFormat("yyyy-MM-dd")
        self.due_date.setCalendarPopup(True)
        self.due_date.setDate(QDate.currentDate())

        self.enable_due = QComboBox()
        self.enable_due.addItems(["不设置日期", "设置截止日期"])

        self.pomo_spin = QSpinBox()
        self.pomo_spin.setRange(1, 16)
        self.pomo_spin.setValue(1)

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("备注")
        self.notes_input.setFixedHeight(46)

        self.add_button = QPushButton("添加")
        self.add_button.clicked.connect(self._add_task)

        layout.addWidget(QLabel("任务"), 0, 0)
        layout.addWidget(self.task_input, 0, 1, 1, 3)

        layout.addWidget(QLabel("优先级"), 1, 0)
        layout.addWidget(self.priority_combo, 1, 1)
        layout.addWidget(QLabel("分类"), 1, 2)
        layout.addWidget(self.category_input, 1, 3)

        layout.addWidget(QLabel("标签"), 2, 0)
        layout.addWidget(self.tags_input, 2, 1, 1, 3)

        layout.addWidget(self.enable_due, 3, 0)
        layout.addWidget(self.due_date, 3, 1)
        layout.addWidget(QLabel("番茄"), 3, 2)
        layout.addWidget(self.pomo_spin, 3, 3)

        layout.addWidget(QLabel("备注"), 4, 0)
        layout.addWidget(self.notes_input, 4, 1, 1, 2)
        layout.addWidget(self.add_button, 4, 3)

        return box

    def _build_toolbar_panel(self) -> QGroupBox:
        box = QGroupBox("搜索与操作")
        self.action_panel = box
        outer = QVBoxLayout(box)
        outer.setSpacing(5)

        row_top = QHBoxLayout()
        row_top.setSpacing(5)
        row_bottom = QHBoxLayout()
        row_bottom.setSpacing(5)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索任务/备注/标签")
        self.search_input.textChanged.connect(self._refresh_list)

        self.filter_priority = QComboBox()
        self.filter_priority.addItems(["全部", "高", "中", "低"])
        self.filter_priority.currentTextChanged.connect(self._refresh_list)

        self.filter_status = QComboBox()
        self.filter_status.addItems(["全部", "进行中", "已完成"])
        self.filter_status.currentTextChanged.connect(self._refresh_list)

        self.complete_btn = QPushButton("完成")
        self.complete_btn.clicked.connect(self._complete_selected)

        self.delete_btn = QPushButton("删除")
        self.delete_btn.clicked.connect(self._delete_selected)

        self.restore_btn = QPushButton("恢复最近")
        self.restore_btn.clicked.connect(self._restore_last_deleted)

        self.quick_add_today_btn = QPushButton("今天")
        self.quick_add_today_btn.clicked.connect(self._quick_due_today)

        row_top.addWidget(self.search_input, 1)
        row_top.addWidget(QLabel("优先级"))
        row_top.addWidget(self.filter_priority)
        row_top.addWidget(QLabel("状态"))
        row_top.addWidget(self.filter_status)

        row_bottom.addWidget(self.complete_btn)
        row_bottom.addWidget(self.delete_btn)
        row_bottom.addWidget(self.restore_btn)
        row_bottom.addWidget(self.quick_add_today_btn)
        row_bottom.addStretch(1)

        outer.addLayout(row_top)
        outer.addLayout(row_bottom)

        return box

    def _build_list_panel(self) -> QGroupBox:
        box = QGroupBox("任务列表")
        col = QVBoxLayout(box)

        self.todo_list = QListWidget()
        self.todo_list.itemSelectionChanged.connect(self._show_current_item_details)
        self.todo_list.itemDoubleClicked.connect(lambda _: self._complete_selected())

        col.addWidget(self.todo_list)
        return box

    def _build_right_panel(self) -> QGroupBox:
        box = QGroupBox("信息面板")
        col = QVBoxLayout(box)

        self.stats_label = QLabel("-")
        self.stats_label.setWordWrap(True)
        self.stats_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.reminder_label = QLabel("-")
        self.reminder_label.setWordWrap(True)

        self.detail_label = QLabel("选择任务后查看详情")
        self.detail_label.setWordWrap(True)

        export_row = QHBoxLayout()
        export_json = QPushButton("导出JSON")
        export_csv = QPushButton("导出CSV")
        export_md = QPushButton("导出MD")
        export_json.clicked.connect(lambda: self._export("json"))
        export_csv.clicked.connect(lambda: self._export("csv"))
        export_md.clicked.connect(lambda: self._export("markdown"))
        export_row.addWidget(export_json)
        export_row.addWidget(export_csv)
        export_row.addWidget(export_md)

        backup_row = QHBoxLayout()
        backup_btn = QPushButton("创建备份")
        backup_btn.clicked.connect(self._create_backup)
        backup_row.addWidget(backup_btn)

        pomo_box = QGroupBox("番茄时钟")
        pomo_layout = QVBoxLayout(pomo_box)
        self.pomo_status = QLabel("00:00")
        self.pomo_status.setAlignment(Qt.AlignCenter)
        start_btn = QPushButton("开始")
        pause_btn = QPushButton("暂停")
        reset_btn = QPushButton("重置")
        start_btn.clicked.connect(self._start_pomodoro)
        pause_btn.clicked.connect(self._pause_pomodoro)
        reset_btn.clicked.connect(self._reset_pomodoro)
        btn_row = QHBoxLayout()
        btn_row.addWidget(start_btn)
        btn_row.addWidget(pause_btn)
        btn_row.addWidget(reset_btn)
        pomo_layout.addWidget(self.pomo_status)
        pomo_layout.addLayout(btn_row)

        col.addWidget(self.stats_label)
        col.addWidget(self.reminder_label)
        col.addLayout(export_row)
        col.addLayout(backup_row)
        col.addWidget(pomo_box)
        col.addWidget(self.detail_label)

        self.dashboard_panel = box
        return box

    def _bind_shortcuts(self) -> None:
        QShortcut(QKeySequence("Ctrl+N"), self, activated=self.task_input.setFocus)
        QShortcut(QKeySequence("Ctrl+F"), self, activated=self.search_input.setFocus)
        QShortcut(QKeySequence("Ctrl+D"), self, activated=self._complete_selected)
        QShortcut(QKeySequence("Delete"), self, activated=self._delete_selected)
        QShortcut(QKeySequence("Escape"), self, activated=self._clear_search)
        QShortcut(QKeySequence("Ctrl+M"), self, activated=self._toggle_minimal)

    def _apply_widget_style(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow { background: #f4f7fb; }
            QGroupBox {
                border: 1px solid #d7e0ec;
                border-radius: 10px;
                margin-top: 8px;
                background: #ffffff;
                font-weight: 600;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; color: #355070; }
            QLabel#WidgetTitle { font-size: 16px; font-weight: 700; color: #1f3552; }
            QPushButton {
                border: 1px solid #b4c6dc;
                border-radius: 8px;
                padding: 3px 7px;
                background: #eef3fa;
                color: #24415f;
            }
            QPushButton:hover { background: #e3edf9; }
            QPushButton:checked { background: #cbe1ff; border-color: #7aa8df; }
            QLineEdit, QTextEdit, QComboBox, QDateEdit, QSpinBox, QListWidget {
                border: 1px solid #c9d7e7;
                border-radius: 8px;
                background: #fbfdff;
                padding: 3px;
            }
            QListWidget { padding: 2px; }
            """
        )

    def _toggle_pin(self) -> None:
        self._is_pinned = self.pin_btn.isChecked()
        flags = Qt.FramelessWindowHint | Qt.Tool
        if self._is_pinned:
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show()

    def _toggle_minimal(self) -> None:
        self._is_minimal = not self._is_minimal
        self.compact_btn.setChecked(self._is_minimal)
        self.add_panel.setVisible(not self._is_minimal)
        self.action_panel.setVisible(True)
        self.dashboard_panel.setVisible(not self._is_minimal)
        self.resize(400, 460 if self._is_minimal else 640)

    def _toggle_transparent(self) -> None:
        self._is_transparent = self.transparent_btn.isChecked()
        self.setWindowOpacity(0.9 if self._is_transparent else 1.0)

    def _clear_search(self) -> None:
        self.search_input.clear()

    def _priority_from_text(self, text: str) -> Priority:
        if text == "高":
            return Priority.HIGH
        if text == "低":
            return Priority.LOW
        return Priority.MEDIUM

    def _priority_to_cn(self, value: str) -> str:
        return {"high": "高", "medium": "中", "low": "低"}.get(value, value)

    def _quick_due_today(self) -> None:
        self.enable_due.setCurrentIndex(1)
        self.due_date.setDate(QDate.currentDate())

    def _maybe_due_datetime(self) -> Optional[datetime]:
        if self.enable_due.currentIndex() == 0:
            return None
        qdate = self.due_date.date()
        return datetime(qdate.year(), qdate.month(), qdate.day(), 23, 59, 0)

    def _add_task(self) -> None:
        text = self.task_input.text().strip()
        if not text:
            QMessageBox.warning(self, "提示", "任务内容不能为空")
            return

        tags = [t.strip() for t in self.tags_input.text().split(",") if t.strip()]
        category = self.category_input.text().strip() or "默认"

        self.manager.add_todo(
            text=text,
            priority=self._priority_from_text(self.priority_combo.currentText()),
            category=category,
            tags=tags,
            due_date=self._maybe_due_datetime(),
            estimated_pomodoros=self.pomo_spin.value(),
            notes=self.notes_input.toPlainText().strip(),
        )

        self.task_input.clear()
        self.tags_input.clear()
        self.notes_input.clear()
        self._refresh_all()

    def _filtered_todos(self) -> List:
        search = self.search_input.text().strip()
        p_filter = self.filter_priority.currentText()
        s_filter = self.filter_status.currentText()

        todos = self.manager.search_todos(search) if search else self.manager.get_all_todos()

        if p_filter != "全部":
            mapping = {"高": "high", "中": "medium", "低": "low"}
            todos = [t for t in todos if t.priority == mapping.get(p_filter, t.priority)]

        if s_filter == "进行中":
            todos = [t for t in todos if not t.is_completed and t.status != TodoStatus.ARCHIVED.value]
        elif s_filter == "已完成":
            todos = [t for t in todos if t.is_completed]

        todos.sort(key=lambda t: (PRIORITY_ORDER.get(t.priority, 3), t.created_at), reverse=False)
        return todos

    def _item_title(self, todo) -> str:
        done = "✓" if todo.is_completed else "○"
        priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(todo.priority, "⚪")
        due = f" 截止:{todo.due_date[:10]}" if todo.due_date else ""
        return f"{done} {priority_icon} {todo.text} · {todo.category}{due}"

    def _refresh_list(self) -> None:
        self.todo_list.clear()
        for todo in self._filtered_todos():
            item = QListWidgetItem(self._item_title(todo))
            item.setData(Qt.UserRole, todo.id)
            self.todo_list.addItem(item)

    def _refresh_stats(self) -> None:
        dashboard = self.manager.get_dashboard()
        basic = dashboard.get("statistics", {}).get("基本统计", {})
        time_stats = dashboard.get("statistics", {}).get("时间相关", {})

        self.stats_label.setText(
            "\n".join(
                [
                    "Overview",
                    f"总任务: {basic.get('总数', 0)}",
                    f"进行中: {basic.get('活跃', 0)}",
                    f"已完成: {basic.get('已完成', 0)}",
                    f"完成率: {basic.get('完成率%', 0)}%",
                    f"逾期: {time_stats.get('逾期', 0)}",
                    f"今天截止: {time_stats.get('今天截止', 0)}",
                ]
            )
        )

        reminder_stats = dashboard.get("reminders", {})
        self.reminder_label.setText(
            "\n".join(
                [
                    "Reminders",
                    f"今日提醒: {reminder_stats.get('today_reminders', 0)}",
                    f"即将到期: {reminder_stats.get('upcoming_reminders', 0)}",
                    f"提醒逾期: {reminder_stats.get('overdue_reminders', 0)}",
                ]
            )
        )

    def _refresh_pomodoro(self) -> None:
        self.pomo_status.setText(self.manager.pomodoro.format_status())

    def _refresh_all(self) -> None:
        self._refresh_list()
        self._refresh_stats()
        self._refresh_pomodoro()

    def _selected_todo_id(self) -> Optional[str]:
        item = self.todo_list.currentItem()
        return item.data(Qt.UserRole) if item else None

    def _complete_selected(self) -> None:
        todo_id = self._selected_todo_id()
        if not todo_id:
            return
        self.manager.complete_todo(todo_id)
        self._refresh_all()

    def _delete_selected(self) -> None:
        todo_id = self._selected_todo_id()
        if not todo_id:
            return
        self.manager.delete_todo(todo_id, permanently=False)
        self._refresh_all()

    def _restore_last_deleted(self) -> None:
        details = self.manager.recycle_bin.get_recycle_bin_details()
        if not details:
            QMessageBox.information(self, "回收站", "回收站为空")
            return

        latest = details[0]
        restored = self.manager.recycle_bin.restore_item(latest.get("id", ""))
        if restored:
            self.manager.todos.append(TodoItem.from_dict(restored))
            self.manager.save_todos()
            self._refresh_all()

    def _show_current_item_details(self) -> None:
        todo_id = self._selected_todo_id()
        if not todo_id:
            self.detail_label.setText("选择任务后查看详情")
            return

        todo = self.manager.get_todo_by_id(todo_id)
        if not todo:
            self.detail_label.setText("该任务已不存在")
            return

        self.detail_label.setText(
            "\n".join(
                [
                    f"ID: {todo.id}",
                    f"内容: {todo.text}",
                    f"优先级: {self._priority_to_cn(todo.priority)}",
                    f"分类: {todo.category}",
                    f"状态: {todo.status}",
                    f"创建时间: {todo.created_at}",
                    f"截止日期: {todo.due_date or '-'}",
                    f"标签: {', '.join(todo.tags) if todo.tags else '-'}",
                    f"备注: {todo.notes or '-'}",
                ]
            )
        )

    def _export(self, fmt: str) -> None:
        ext = {"json": "json", "csv": "csv", "markdown": "md"}[fmt]
        default_name = f"todos_export.{ext}"
        path, _ = QFileDialog.getSaveFileName(self, "导出文件", default_name)
        if not path:
            return

        ok = self.manager.export_todos(fmt, path)
        if ok:
            QMessageBox.information(self, "导出", f"已导出到:\n{path}")
        else:
            QMessageBox.critical(self, "导出", "导出失败")

    def _create_backup(self) -> None:
        backup = self.manager.create_backup()
        if backup:
            QMessageBox.information(self, "备份", f"备份已创建:\n{backup}")
        else:
            QMessageBox.critical(self, "备份", "备份失败")

    def _start_pomodoro(self) -> None:
        self.manager.pomodoro.start()
        self._pomodoro_timer.start(1000)
        self._refresh_pomodoro()

    def _pause_pomodoro(self) -> None:
        self.manager.pomodoro.pause()
        self._pomodoro_timer.stop()
        self._refresh_pomodoro()

    def _reset_pomodoro(self) -> None:
        self.manager.pomodoro.reset()
        self._pomodoro_timer.stop()
        self._refresh_pomodoro()

    def _tick_pomodoro(self) -> None:
        self.manager.pomodoro.check_session_complete()
        self._refresh_pomodoro()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._drag_offset = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event) -> None:
        if self._dragging and self._drag_offset is not None:
            self.move(event.globalPos() - self._drag_offset)
            event.accept()

    def mouseReleaseEvent(self, event) -> None:
        self._dragging = False
        self._drag_offset = None
        self._snap_to_edges()
        super().mouseReleaseEvent(event)

    def _snap_to_edges(self) -> None:
        """在桌面边缘附近自动吸附，增强插件体验。"""
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            return

        area = screen.availableGeometry()
        geo = self.frameGeometry()
        threshold = 24

        x = geo.x()
        y = geo.y()

        if abs(geo.left() - area.left()) <= threshold:
            x = area.left()
        elif abs(geo.right() - area.right()) <= threshold:
            x = area.right() - geo.width()

        if abs(geo.top() - area.top()) <= threshold:
            y = area.top()
        elif abs(geo.bottom() - area.bottom()) <= threshold:
            y = area.bottom() - geo.height()

        self.move(x, y)


def main() -> None:
    app = QApplication.instance() or QApplication([])
    win = TODOApplication()
    win.show()
    app.exec_()


if __name__ == "__main__":
    main()
