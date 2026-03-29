"""
设置解析器模块。

用于读取、写入和管理应用配置设置。
"""

from pathlib import Path
from typing import Any, Dict, Union
import logging

logger = logging.getLogger(__name__)

# 默认配置值
DEFAULT_SETTINGS = {
    "USE_DARK_MODE": True,
    "FIXED_POSITION": False,
    "FIXED_POSITION_X": 100,
    "FIXED_POSITION_Y": 100,
}


class SettingsParser:
    """解析和管理应用程序设置。"""

    def __init__(self, path: str) -> None:
        """
        初始化设置解析器。

        Args:
            path: 设置配置文件的路径

        Raises:
            IOError: 如果无法访问或创建配置文件
        """
        self.ini_path = Path(path)
        self.options: Dict[str, Any] = DEFAULT_SETTINGS.copy()
        
        # 确保文件存在，如果不存在则创建
        if not self.ini_path.exists():
            try:
                self.ini_path.parent.mkdir(parents=True, exist_ok=True)
                self._write_defaults()
                logger.info(f"创建新的设置文件: {self.ini_path}")
            except IOError as e:
                logger.error(f"无法创建设置文件: {e}")
                raise

        self.load()

    def load(self) -> None:
        """
        从配置文件加载设置。

        Raises:
            IOError: 如果文件读取失败
        """
        try:
            with open(self.ini_path, "r", encoding="utf-8") as ini_file:
                options = {}
                for line in ini_file.readlines():
                    line = line.strip()
                    if self._is_valid_line(line):
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip()
                        options[key] = self._parse_value(value)
                
                # 使用验证器清理和验证配置
                from config_validator import ConfigValidator
                clean_options = ConfigValidator.sanitize_config(options)
                self.options.update(clean_options)
                
                # 验证配置
                is_valid, errors = ConfigValidator.validate_config(self.options)
                if not is_valid:
                    logger.warning(f"配置包含问题，但已使用默认值修复: {len(errors)} 个错误")
            
            logger.debug(f"成功加载设置，共 {len(self.options)} 个选项")
        except IOError as e:
            logger.error(f"读取设置文件失败: {e}，使用默认值")

    def modify(self, key: str, value: Any) -> None:
        """
        修改设置值。

        Args:
            key: 设置键
            value: 设置值
        """
        if not key or not isinstance(key, str):
            raise ValueError("键不能为空或不是字符串类型")
        
        self.options[key] = value
        logger.debug(f"已修改设置: {key} = {value}")

    def write(self) -> None:
        """
        将所有设置写入文件。

        Raises:
            IOError: 如果文件写入失败
        """
        try:
            with open(self.ini_path, "w", encoding="utf-8") as ini_file:
                for key, value in self.options.items():
                    ini_file.write(f"{key} = {value}\n")
            logger.debug(f"成功保存 {len(self.options)} 个设置")
        except IOError as e:
            logger.error(f"保存设置文件失败: {e}")
            raise

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取设置值。

        Args:
            key: 设置键
            default: 如果键不存在时的默认值

        Returns:
            设置值或默认值
        """
        return self.options.get(key, default)

    def get_all(self) -> Dict[str, Any]:
        """
        获取所有设置。

        Returns:
            包含所有设置的字典副本
        """
        return self.options.copy()

    def reset_to_defaults(self) -> None:
        """重置所有设置为默认值。"""
        self.options = DEFAULT_SETTINGS.copy()
        logger.info("已重置设置为默认值")
        self.write()

    def _write_defaults(self) -> None:
        """写入默认设置到文件。"""
        try:
            with open(self.ini_path, "w", encoding="utf-8") as ini_file:
                for key, value in DEFAULT_SETTINGS.items():
                    ini_file.write(f"{key} = {value}\n")
            logger.debug("已写入默认设置")
        except IOError as e:
            logger.error(f"写入默认设置失败: {e}")

    @staticmethod
    def _parse_value(string: str) -> Union[bool, int, float, str]:
        """
        尝试将字符串转换为相应的类型。

        示例:
            _parse_value("1.234") -> 1.234 (float)
            _parse_value("False") -> False (bool)
            _parse_value("42") -> 42 (int)
            _parse_value("name") -> "name" (str)

        Args:
            string: 要解析的字符串

        Returns:
            解析后的值
        """
        # 布尔值判断
        if string == "True":
            return True
        if string == "False":
            return False

        # 数字判断
        try:
            if "." in string:
                return float(string)
            else:
                return int(string)
        except ValueError:
            return string

    @staticmethod
    def _is_valid_line(line: str) -> bool:
        """
        检查该行是否为有效的配置行。

        Args:
            line: 要检查的行

        Returns:
            如果该行包含有效的键值对则返回True
        """
        if not line or line.startswith("#"):  # 忽略注释
            return False

        if line.count("=") != 1:
            return False

        key, value = line.split("=")
        key = key.strip()
        value = value.strip()

        return bool(key and value)
