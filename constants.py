"""
应用程序常量和配置定义。

定义所有应用程序范围内的常量，避免硬编码的魔法数字和字符串。
"""

# ============ 窗口配置 ============
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 800
WINDOW_PADDING = 48
HEADER_HEIGHT = 48 + 12
SECTION_SPACING = 12
ADD_TODO_HEIGHT = 200
TEXT_EDIT_HEIGHT = 70
FOOTER_HEIGHT = 64
ICON_SIZE = 32
CHECKBOX_SIZE = 12

# ============ 文件路径配置 ============
SETTINGS_FILE = "./options.ini"
TODOS_FILE = "./todos.ini"
ICONS_FILE = "./icons/icons.dat"

# ============ UI 元素大小 ============
ICON_SVG_SIZE = 16
SMALL_BUTTON_SIZE = 32
CONTAINER_SPACING = 0
BODY_SPACING = 4
HEADER_SPACING = 4
BORDER_RADIUS = 8
BORDER_RADIUS_SMALL = 4
SHADOW_OFFSET = 0
SHADOW_BLUR_RADIUS = 48
SHADOW_COLOR_ALPHA = 80

# ============ 动画配置 ============
MOVE_ANIMATION_FACTOR = 1 / 4
MOVE_ANIMATION_BIAS = 1

# ============ 存储相关的标记 ============
TODO_MARK = "<TODO-START-MARK>"

# ============ 约束值 ============
MAX_TODO_ITEMS = 10000  # 最多可以存储的待办事项数
MIN_TEXT_LENGTH = 1     # 最小待办文本长度
MAX_TEXT_LENGTH = 1000  # 最大待办文本长度

# ============ UI 文本常量 ============
TEXT_NO_TODOS = "当前没有待办哦"
TEXT_NO_TODOS_ALT = "没有待办"
TEXT_TODO_COUNT = "个待办事项"
TEXT_ADD_TODO_PANEL = "添加新待办"
TEXT_TODO_LIST_PANEL = "全部待办"
TEXT_SETTINGS_PANEL = "设置"
TEXT_ENTER_TODO = "请输入待办内容"
TEXT_DARK_MODE = "深色模式"
TEXT_DARK_MODE_DESC = "在深色主题的计算机上提供更佳的视觉效果"
TEXT_LOCK_POSITION = "锁定位置"
TEXT_LOCK_POSITION_DESC = "阻止拖动窗口以保持位置不变"
TEXT_THIRD_PARTY = "第三方资源"
TEXT_THIRD_PARTY_DESC = "本项目使用了 FlatIcon 提供的图标"
TEXT_LICENSE = "开源许可证"
TEXT_LICENSE_DESC = "本项目采用 GNU General Public License v3.0"
TEXT_ABOUT = "关于此软件"
TEXT_ABOUT_DESC = "制作者 霏泠Ice 保留所有权利"
TEXT_DONATION = "赞助作者"
TEXT_DONATION_DESC = "为爱发电，您的支持是我最大的动力"
TEXT_COMPLETE_ALL = "全部完成"

# ============ 按钮提示 ============
HINT_CONFIRM = "确认并添加"
HINT_CANCEL = "取消"
HINT_SETTINGS = "设置"
HINT_ADD = "添加新待办"

# ============ URL 链接 ============
URL_FLATICON = "https://flaticon.com/"
URL_LICENSE = "https://github.com/ChinaIceF/My-TODOs/blob/main/LICENSE"
URL_GITHUB = "https://github.com/ChinaIceF"
URL_BILIBILI = "https://space.bilibili.com/390832893"
URL_DONATION = "https://github.com/ChinaIceF/My-TODOs?tab=readme-ov-file#%E8%B5%9E%E5%8A%A9"
URL_SILICON_UI = "https://github.com/ChinaIceF/PyQt-SiliconUI"
URL_REPO = "https://github.com/ChinaIceF/My-TODOs"

# ============ 按钮文本 ============
BUTTON_FLATICON = "前往 FlatIcon"
BUTTON_LICENSE_VIEW = "在 Github 上查看"
BUTTON_GITHUB = "Github 主页"
BUTTON_BILIBILI = "哔哩哔哩 主页"
BUTTON_DONATION = "在 Github 上扫码赞助"
BUTTON_SILICON_UI = "基于 PyQt-SiliconUI 编写"

# ============ 规则表达式和验证 ============
NEWLINE_CHARS = "\n"

# ============ 日志配置 ============
LOG_LEVEL = "DEBUG"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ============ 默认值 ============
DEFAULT_WINDOW_X = 100
DEFAULT_WINDOW_Y = 100
DEFAULT_DARK_MODE = True
DEFAULT_FIXED_POSITION = False
