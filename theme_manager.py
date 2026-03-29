"""
主题和颜色管理模块。

集中管理所有颜色配置和主题定义，提高代码复用性和可维护性。
"""

from typing import Dict
from dataclasses import dataclass
from siui.core.color import Color
import logging

logger = logging.getLogger(__name__)


@dataclass
class ColorScheme:
    """颜色方案定义。"""

    theme: str
    panel_theme: str
    background_color: str
    background_dark_color: str
    border_color: str
    tooltip_bg: str
    svg_a: str
    theme_transition_a: str
    theme_transition_b: str
    text_a: str
    text_b: str
    text_c: str
    text_d: str
    text_e: str
    switch_deactivate: str
    switch_activate: str
    button_hover: str
    button_flash: str
    simple_button_bg: str
    toggle_button_off_bg: str
    toggle_button_on_bg: str


# 深色主题配置
DARK_THEME = ColorScheme(
    theme="#e1d9e8",
    panel_theme="#0F85D3",
    background_color="#252229",
    background_dark_color=None,  # 将从 SiGlobal 动态获取
    border_color="#3b373f",
    tooltip_bg="ef413a47",
    svg_a="#e1d9e8",
    theme_transition_a="#52389a",
    theme_transition_b="#9c4e8b",
    text_a="#FFFFFF",
    text_b="#e1d9e8",
    text_c=None,  # 将计算为 THEME 的透明度变体
    text_d=None,  # 将计算为 THEME 的透明度变体
    text_e=None,  # 将计算为 THEME 的透明度变体
    switch_deactivate="#D2D2D2",
    switch_activate="#100912",
    button_hover="#10FFFFFF",
    button_flash="#20FFFFFF",
    simple_button_bg=None,  # 将计算
    toggle_button_off_bg=None,  # 将计算
    toggle_button_on_bg=None,  # 将计算
)

# 亮色主题配置
LIGHT_THEME = ColorScheme(
    theme="#0F85D3",
    panel_theme="#0F85D3",
    background_color="#F3F3F3",
    background_dark_color="#e8e8e8",
    border_color="#d0d0d0",
    tooltip_bg="#F3F3F3",
    svg_a="#0F85D3",
    theme_transition_a="#2abed8",
    theme_transition_b="#2ad98e",
    text_a="#1f1f2f",
    text_b=None,  # 将计算
    text_c=None,  # 将计算
    text_d=None,  # 将计算
    text_e=None,  # 将计算
    switch_deactivate="#bec1c7",
    switch_activate="#F3F3F3",
    button_hover=None,  # 将计算
    button_flash=None,  # 将计算
    simple_button_bg=None,  # 将计算
    toggle_button_off_bg=None,  # 将计算
    toggle_button_on_bg=None,  # 将计算
)


class ThemeManager:
    """管理应用程序主题和颜色。"""

    def __init__(self):
        """初始化主题管理器。"""
        self.is_dark_mode: bool = True
        self.current_scheme: ColorScheme = DARK_THEME
        logger.debug("主题管理器初始化成功")

    def apply_theme(self, colors_dict: Dict, is_dark: bool = True) -> None:
        """
        应用指定的主题到颜色字典。

        Args:
            colors_dict: SiGlobal.siui.colors 字典
            is_dark: 是否应用深色主题，False 为亮色主题
        """
        self.is_dark_mode = is_dark
        scheme = DARK_THEME if is_dark else LIGHT_THEME

        # 设置基础颜色
        colors_dict["THEME"] = scheme.theme
        colors_dict["PANEL_THEME"] = scheme.panel_theme
        colors_dict["BACKGROUND_COLOR"] = scheme.background_color
        colors_dict["BACKGROUND_DARK_COLOR"] = scheme.background_dark_color or colors_dict.get("INTERFACE_BG_A", "#000000")
        colors_dict["BORDER_COLOR"] = scheme.border_color
        colors_dict["TOOLTIP_BG"] = scheme.tooltip_bg
        colors_dict["SVG_A"] = scheme.svg_a

        # 过渡颜色
        colors_dict["THEME_TRANSITION_A"] = scheme.theme_transition_a
        colors_dict["THEME_TRANSITION_B"] = scheme.theme_transition_b

        # 文本颜色
        colors_dict["TEXT_A"] = scheme.text_a
        colors_dict["TEXT_B"] = scheme.text_b or colors_dict["THEME"]

        if is_dark:
            colors_dict["TEXT_C"] = Color.transparency(colors_dict["THEME"], 0.75)
            colors_dict["TEXT_D"] = Color.transparency(colors_dict["THEME"], 0.6)
            colors_dict["TEXT_E"] = Color.transparency(colors_dict["THEME"], 0.5)
        else:
            colors_dict["TEXT_C"] = Color.transparency(colors_dict["TEXT_A"], 0.75)
            colors_dict["TEXT_D"] = Color.transparency(colors_dict["TEXT_A"], 0.6)
            colors_dict["TEXT_E"] = Color.transparency(colors_dict["TEXT_A"], 0.5)

        # 开关颜色
        colors_dict["SWITCH_DEACTIVATE"] = scheme.switch_deactivate
        colors_dict["SWITCH_ACTIVATE"] = scheme.switch_activate

        # 按钮颜色
        if is_dark:
            colors_dict["BUTTON_HOVER"] = scheme.button_hover
            colors_dict["BUTTON_FLASH"] = scheme.button_flash
        else:
            colors_dict["BUTTON_HOVER"] = Color.transparency(colors_dict["THEME"], 0.0625)
            colors_dict["BUTTON_FLASH"] = Color.transparency(colors_dict["THEME"], 0.43)

        # 简单按钮背景
        if is_dark:
            colors_dict["SIMPLE_BUTTON_BG"] = Color.transparency(colors_dict["THEME"], 0.1)
        else:
            colors_dict["SIMPLE_BUTTON_BG"] = Color.transparency(colors_dict["THEME"], 0.6)

        # 切换按钮背景
        colors_dict["TOGGLE_BUTTON_OFF_BG"] = Color.transparency(colors_dict["THEME"], 0)
        colors_dict["TOGGLE_BUTTON_ON_BG"] = Color.transparency(colors_dict["THEME"], 0.1)

        logger.info(f"已应用 {'深色' if is_dark else '亮色'} 主题")

    def get_current_theme_name(self) -> str:
        """
        获取当前主题名称。

        Returns:
            '深色主题' 或 '亮色主题'
        """
        return "深色主题" if self.is_dark_mode else "亮色主题"


# 全局主题管理器实例
_theme_manager = ThemeManager()


def get_theme_manager() -> ThemeManager:
    """
    获取全局主题管理器实例。

    Returns:
        主题管理器对象
    """
    return _theme_manager
