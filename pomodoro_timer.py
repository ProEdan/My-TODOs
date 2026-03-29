"""
番茄计时器模块。

实现 Pomodoro 时间管理技术。
"""

from typing import Callable, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class PomodoroTimer:
    """番茄计时器类。"""

    def __init__(
        self,
        work_duration: int = 25,  # 25 分钟
        break_duration: int = 5,  # 5 分钟
        long_break_duration: int = 15,  # 15 分钟
    ):
        """
        初始化计时器。

        Args:
            work_duration: 工作时长（分钟）
            break_duration: 短暂休息时长（分钟）
            long_break_duration: 长休息时长（分钟）
        """
        self.work_duration = work_duration
        self.break_duration = break_duration
        self.long_break_duration = long_break_duration

        self.is_running = False
        self.is_work_time = True
        self.completed_pomodoros = 0
        self.start_time: Optional[datetime] = None
        self.on_tick: Optional[Callable[[int], None]] = None
        self.on_session_complete: Optional[Callable[[], None]] = None

    def start(self) -> None:
        """开始计时。"""
        if not self.is_running:
            self.is_running = True
            self.start_time = datetime.now()
            logger.info("番茄计时开始")

    def pause(self) -> None:
        """暂停计时。"""
        if self.is_running:
            self.is_running = False
            logger.info("番茄计时已暂停")

    def resume(self) -> None:
        """恢复计时。"""
        if not self.is_running and self.start_time:
            self.is_running = True
            logger.info("番茄计时已恢复")

    def stop(self) -> None:
        """停止计时。"""
        self.is_running = False
        self.start_time = None
        logger.info("番茄计时已停止")

    def reset(self) -> None:
        """重置计时。"""
        self.is_running = False
        self.start_time = None
        self.is_work_time = True
        self.completed_pomodoros = 0
        logger.info("番茄计时已重置")

    def get_elapsed_time(self) -> int:
        """
        获取已用时间（秒）。

        Returns:
            已用时间（秒）
        """
        if not self.start_time:
            return 0
        elapsed = (datetime.now() - self.start_time).total_seconds()
        return int(elapsed)

    def get_remaining_time(self) -> int:
        """
        获取剩余时间（秒）。

        Returns:
            剩余时间（秒）
        """
        if not self.is_running:
            return 0

        elapsed = self.get_elapsed_time()
        duration = (
            self.work_duration * 60 if self.is_work_time else self.break_duration * 60
        )
        remaining = max(0, duration - elapsed)
        return remaining

    def check_session_complete(self) -> bool:
        """
        检查当前会话是否完成。

        Returns:
            是否完成
        """
        if not self.is_running or not self.start_time:
            return False

        elapsed = self.get_elapsed_time()
        duration = (
            self.work_duration * 60 if self.is_work_time else self.break_duration * 60
        )

        if elapsed >= duration:
            self.handle_session_complete()
            return True
        return False

    def handle_session_complete(self) -> None:
        """处理会话完成。"""
        if self.is_work_time:
            self.completed_pomodoros += 1
            logger.info(f"完成一个番茄！总数: {self.completed_pomodoros}")

            # 判断是否需要长休息
            if self.completed_pomodoros % 4 == 0:
                self.is_work_time = False
                logger.info(f"进入长休息({self.long_break_duration} 分钟)")
            else:
                self.is_work_time = False
                logger.info(f"进入短休息({self.break_duration} 分钟)")
        else:
            self.is_work_time = True
            logger.info("休息结束，准备开始新一个番茄")

        # 重置计时
        self.start_time = datetime.now()

        # 触发完成回调
        if self.on_session_complete:
            self.on_session_complete()

    def get_status(self) -> dict:
        """
        获取计时器状态。

        Returns:
            状态字典
        """
        return {
            "is_running": self.is_running,
            "is_work_time": self.is_work_time,
            "elapsed_seconds": self.get_elapsed_time(),
            "remaining_seconds": self.get_remaining_time(),
            "completed_pomodoros": self.completed_pomodoros,
            "session_type": "工作" if self.is_work_time else "休息",
        }

    def get_formatted_time(self, seconds: Optional[int] = None) -> str:
        """
        获取格式化的时间字符串。

        Args:
            seconds: 秒数，如果为 None 则使用剩余时间

        Returns:
            格式化字符串 "MM:SS"
        """
        if seconds is None:
            seconds = self.get_remaining_time()

        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"

    def format_status(self) -> str:
        """
        格式化状态字符串。

        Returns:
            人类可读的状态字符串
        """
        status = self.get_status()
        running_icon = "▶️" if status["is_running"] else "⏸️"
        session_icon = "🍅" if status["is_work_time"] else "☕"

        return (
            f"{running_icon} {session_icon} "
            f"{status['session_type']}: {self.get_formatted_time(status['remaining_seconds'])} "
            f"(完成: {status['completed_pomodoros']}个)"
        )
