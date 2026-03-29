"""
单元测试模块。

测试应用程序的核心功能和 parser。

运行测试: python -m unittest test_app -v
或: python -m pytest test_app.py -v
"""

import unittest
import tempfile
import os
from pathlib import Path

from todos_parser import TODOParser
from settings_parser import SettingsParser
from config_validator import ConfigValidator


class TestTODOParser(unittest.TestCase):
    """测试 TODOParser 类。"""

    def setUp(self):
        """设置测试前的环境。"""
        # 创建临时文件
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ini')
        self.temp_path = self.temp_file.name
        self.temp_file.close()

    def tearDown(self):
        """清理测试环境。"""
        if os.path.exists(self.temp_path):
            os.remove(self.temp_path)

    def test_add_todo(self):
        """测试添加待办事项。"""
        parser = TODOParser(self.temp_path)
        parser.add("测试待办")
        self.assertEqual(len(parser.todos), 1)
        self.assertEqual(parser.todos[0], "测试待办")

    def test_add_multiple_todos(self):
        """测试添加多个待办事项。"""
        parser = TODOParser(self.temp_path)
        todos = ["待办1", "待办2", "待办3"]
        for todo in todos:
            parser.add(todo)
        self.assertEqual(len(parser.todos), 3)

    def test_write_and_read(self):
        """测试写入和读取待办事项。"""
        # 写入
        parser1 = TODOParser(self.temp_path)
        parser1.add("待办1")
        parser1.add("待办2")
        parser1.write()

        # 读取
        parser2 = TODOParser(self.temp_path)
        self.assertEqual(len(parser2.todos), 2)
        self.assertEqual(parser2.todos[0], "待办1")
        self.assertEqual(parser2.todos[1], "待办2")

    def test_remove_todo(self):
        """测试删除待办事项。"""
        parser = TODOParser(self.temp_path)
        parser.add("待办1")
        parser.add("待办2")
        parser.remove(0)
        self.assertEqual(len(parser.todos), 1)
        self.assertEqual(parser.todos[0], "待办2")

    def test_remove_index_out_of_range(self):
        """测试删除不存在的待办事项。"""
        parser = TODOParser(self.temp_path)
        parser.add("待办1")
        with self.assertRaises(IndexError):
            parser.remove(10)

    def test_get_all(self):
        """测试获取所有待办事项。"""
        parser = TODOParser(self.temp_path)
        parser.add("待办1")
        parser.add("待办2")
        
        all_todos = parser.get_all()
        self.assertEqual(len(all_todos), 2)
        # 验证是副本而不是引用
        all_todos.append("待办3")
        self.assertEqual(len(parser.todos), 2)

    def test_clear_todos(self):
        """测试清空所有待办事项。"""
        parser = TODOParser(self.temp_path)
        parser.add("待办1")
        parser.add("待办2")
        parser.clear()
        self.assertEqual(len(parser.todos), 0)

    def test_add_empty_string(self):
        """测试添加空字符串。"""
        parser = TODOParser(self.temp_path)
        with self.assertRaises(ValueError):
            parser.add("")

    def test_add_non_string(self):
        """测试添加非字符串类型。"""
        parser = TODOParser(self.temp_path)
        with self.assertRaises(ValueError):
            parser.add(123)


class TestSettingsParser(unittest.TestCase):
    """测试 SettingsParser 类。"""

    def setUp(self):
        """设置测试前的环境。"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ini')
        self.temp_path = self.temp_file.name
        self.temp_file.close()

    def tearDown(self):
        """清理测试环境。"""
        if os.path.exists(self.temp_path):
            os.remove(self.temp_path)

    def test_load_default_settings(self):
        """测试加载默认设置。"""
        parser = SettingsParser(self.temp_path)
        self.assertTrue(parser.options.get("USE_DARK_MODE"))
        self.assertFalse(parser.options.get("FIXED_POSITION"))

    def test_modify_settings(self):
        """测试修改设置。"""
        parser = SettingsParser(self.temp_path)
        parser.modify("USE_DARK_MODE", False)
        self.assertFalse(parser.options["USE_DARK_MODE"])

    def test_write_and_read_settings(self):
        """测试写入和读取设置。"""
        # 写入
        parser1 = SettingsParser(self.temp_path)
        parser1.modify("USE_DARK_MODE", False)
        parser1.modify("FIXED_POSITION", True)
        parser1.write()

        # 读取
        parser2 = SettingsParser(self.temp_path)
        self.assertFalse(parser2.options["USE_DARK_MODE"])
        self.assertTrue(parser2.options["FIXED_POSITION"])

    def test_get_with_default(self):
        """测试使用默认值获取设置。"""
        parser = SettingsParser(self.temp_path)
        value = parser.get("NOT_EXISTS", "default_value")
        self.assertEqual(value, "default_value")

    def test_get_all(self):
        """测试获取所有设置。"""
        parser = SettingsParser(self.temp_path)
        all_settings = parser.get_all()
        self.assertIsInstance(all_settings, dict)
        self.assertIn("USE_DARK_MODE", all_settings)

    def test_reset_to_defaults(self):
        """测试重置为默认设置。"""
        parser = SettingsParser(self.temp_path)
        parser.modify("USE_DARK_MODE", False)
        parser.reset_to_defaults()
        self.assertTrue(parser.options["USE_DARK_MODE"])


class TestConfigValidator(unittest.TestCase):
    """测试 ConfigValidator 类。"""

    def test_validate_valid_config(self):
        """测试验证有效的配置。"""
        config = {
            "USE_DARK_MODE": True,
            "FIXED_POSITION": False,
            "FIXED_POSITION_X": 100,
            "FIXED_POSITION_Y": 200,
        }
        is_valid, errors = ConfigValidator.validate_config(config)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_validate_invalid_type(self):
        """测试验证类型错误的配置。"""
        config = {
            "USE_DARK_MODE": "not_a_bool",
            "FIXED_POSITION": False,
            "FIXED_POSITION_X": 100,
            "FIXED_POSITION_Y": 200,
        }
        is_valid, errors = ConfigValidator.validate_config(config)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)

    def test_validate_out_of_range(self):
        """测试验证超出范围的值。"""
        config = {
            "USE_DARK_MODE": True,
            "FIXED_POSITION": False,
            "FIXED_POSITION_X": 50000,  # 超出范围
            "FIXED_POSITION_Y": 200,
        }
        is_valid, errors = ConfigValidator.validate_config(config)
        self.assertFalse(is_valid)

    def test_validate_todo_text_valid(self):
        """测试验证有效的待办文本。"""
        is_valid, error = ConfigValidator.validate_todo_text("这是一个有效的待办")
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_validate_todo_text_empty(self):
        """测试验证空待办文本。"""
        is_valid, error = ConfigValidator.validate_todo_text("")
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)

    def test_validate_todo_text_too_long(self):
        """测试验证过长的待办文本。"""
        long_text = "a" * 2000  # 超过最大长度
        is_valid, error = ConfigValidator.validate_todo_text(long_text)
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)

    def test_validate_position_valid(self):
        """测试验证有效的位置。"""
        is_valid, error = ConfigValidator.validate_position(100, 200)
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_validate_position_out_of_range(self):
        """测试验证超出范围的位置。"""
        is_valid, error = ConfigValidator.validate_position(50000, 50000)
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)

    def test_sanitize_config_auto_fix(self):
        """测试自动修复配置。"""
        config = {
            "USE_DARK_MODE": "true",  # 字符串而非布尔值
            "FIXED_POSITION_X": "100",  # 字符串而非整数
        }
        sanitized = ConfigValidator.sanitize_config(config)
        self.assertIsInstance(sanitized["USE_DARK_MODE"], bool)
        self.assertIsInstance(sanitized["FIXED_POSITION_X"], int)


class TestIntegration(unittest.TestCase):
    """集成测试。"""

    def setUp(self):
        """设置测试前的环境。"""
        self.temp_dir = tempfile.mkdtemp()
        self.todos_path = os.path.join(self.temp_dir, "todos.ini")
        self.settings_path = os.path.join(self.temp_dir, "options.ini")

    def tearDown(self):
        """清理测试环境。"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_full_workflow(self):
        """测试完整的工作流。"""
        # 创建解析器
        todos_parser = TODOParser(self.todos_path)
        settings_parser = SettingsParser(self.settings_path)

        # 添加待办
        todos_parser.add("完成项目优化")
        todos_parser.add("代码审查")
        todos_parser.write()

        # 修改设置
        settings_parser.modify("USE_DARK_MODE", False)
        settings_parser.write()

        # 重新加载
        todos_parser2 = TODOParser(self.todos_path)
        settings_parser2 = SettingsParser(self.settings_path)

        # 验证
        self.assertEqual(len(todos_parser2.todos), 2)
        self.assertFalse(settings_parser2.options["USE_DARK_MODE"])


if __name__ == "__main__":
    # 配置logging
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    # 运行测试
    unittest.main(verbosity=2)
