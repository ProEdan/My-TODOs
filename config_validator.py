"""
配置验证和校验模块。

验证应用程序配置的有效性和完整性。
"""

from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class ConfigValidator:
    """配置验证器类。"""

    # 支持的配置键和其验证规则
    VALID_CONFIGS = {
        "USE_DARK_MODE": {"type": bool, "required": True},
        "FIXED_POSITION": {"type": bool, "required": True},
        "FIXED_POSITION_X": {"type": int, "required": True, "min": -10000, "max": 10000},
        "FIXED_POSITION_Y": {"type": int, "required": True, "min": -10000, "max": 10000},
    }

    @staticmethod
    def validate_config(config: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        验证配置字典的完整性和有效性。

        Args:
            config: 配置字典

        Returns:
            (是否有效, 错误信息列表)
        """
        errors = []

        # 检查必需的配置
        for key, rules in ConfigValidator.VALID_CONFIGS.items():
            if rules.get("required", False) and key not in config:
                errors.append(f"缺少必需的配置项: {key}")
                continue

            if key in config:
                value = config[key]
                
                # 检查类型
                expected_type = rules.get("type")
                if expected_type and not isinstance(value, expected_type):
                    errors.append(
                        f"配置 '{key}' 的类型错误: 期望 {expected_type.__name__}，"
                        f"但得到 {type(value).__name__}"
                    )
                    continue

                # 检查数值范围
                if isinstance(value, (int, float)):
                    min_val = rules.get("min")
                    max_val = rules.get("max")
                    
                    if min_val is not None and value < min_val:
                        errors.append(f"配置 '{key}' 的值 {value} 小于最小值 {min_val}")
                    
                    if max_val is not None and value > max_val:
                        errors.append(f"配置 '{key}' 的值 {value} 大于最大值 {max_val}")

        if errors:
            logger.error(f"配置验证失败，发现 {len(errors)} 个错误:")
            for error in errors:
                logger.error(f"  - {error}")
            return False, errors

        logger.debug("配置验证通过")
        return True, []

    @staticmethod
    def validate_todo_text(text: str) -> tuple[bool, Optional[str]]:
        """
        验证待办事项文本的有效性。

        Args:
            text: 待办事项文本

        Returns:
            (是否有效, 错误信息)
        """
        from constants import MAX_TEXT_LENGTH, MIN_TEXT_LENGTH

        if not isinstance(text, str):
            msg = f"待办文本必须是字符串，但得到 {type(text).__name__}"
            logger.warning(msg)
            return False, msg

        text_length = len(text)
        
        if text_length < MIN_TEXT_LENGTH:
            msg = f"待办文本长度不能为空"
            logger.warning(msg)
            return False, msg

        if text_length > MAX_TEXT_LENGTH:
            msg = f"待办文本长度超过最大限制 {MAX_TEXT_LENGTH} 字符"
            logger.warning(msg)
            return False, msg

        return True, None

    @staticmethod
    def validate_position(x: int, y: int) -> tuple[bool, Optional[str]]:
        """
        验证窗口位置坐标的有效性。

        Args:
            x: X 坐标
            y: Y 坐标

        Returns:
            (是否有效, 错误信息)
        """
        if not isinstance(x, int) or not isinstance(y, int):
            msg = "窗口坐标必须是整数"
            logger.warning(msg)
            return False, msg

        # 允许的坐标范围（考虑到多显示器支持）
        if not (-10000 <= x <= 10000) or not (-10000 <= y <= 10000):
            msg = f"窗口坐标超出允许范围: ({x}, {y})"
            logger.warning(msg)
            return False, msg

        return True, None

    @staticmethod
    def sanitize_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        清理和修复配置字典，移除无效项并修复类型。

        Args:
            config: 原始配置字典

        Returns:
            清理后的配置字典
        """
        from constants import (
            DEFAULT_DARK_MODE,
            DEFAULT_FIXED_POSITION,
            DEFAULT_WINDOW_X,
            DEFAULT_WINDOW_Y,
        )

        sanitized = {}

        # 处理每个已知的配置键
        for key in ConfigValidator.VALID_CONFIGS.keys():
            if key in config:
                value = config[key]
                rule = ConfigValidator.VALID_CONFIGS[key]
                expected_type = rule.get("type")

                # 尝试转换类型
                if expected_type is bool and not isinstance(value, bool):
                    if isinstance(value, str):
                        sanitized[key] = value.lower() in ("true", "1", "yes")
                    else:
                        sanitized[key] = bool(value)
                elif expected_type in (int, float):
                    try:
                        sanitized[key] = expected_type(value)
                        # 应用范围限制
                        min_val = rule.get("min")
                        max_val = rule.get("max")
                        if min_val is not None:
                            sanitized[key] = max(sanitized[key], min_val)
                        if max_val is not None:
                            sanitized[key] = min(sanitized[key], max_val)
                    except (ValueError, TypeError):
                        logger.warning(f"无法将 '{key}' 转换为 {expected_type.__name__}")
                else:
                    sanitized[key] = value
            else:
                # 使用默认值
                if key == "USE_DARK_MODE":
                    sanitized[key] = DEFAULT_DARK_MODE
                elif key == "FIXED_POSITION":
                    sanitized[key] = DEFAULT_FIXED_POSITION
                elif key == "FIXED_POSITION_X":
                    sanitized[key] = DEFAULT_WINDOW_X
                elif key == "FIXED_POSITION_Y":
                    sanitized[key] = DEFAULT_WINDOW_Y

        logger.debug(f"配置已清理，共 {len(sanitized)} 项")
        return sanitized
