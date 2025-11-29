"""
ShareBook - 小说信息提取和处理系统

基于 LangChain 框架和大型语言模型（LLM）来分析小说内容、提取关键信息和角色数据，
并支持将小说转换为漫画故事板和生成角色图片。
"""

__version__ = "0.1.0"
__author__ = "simon"
__email__ = "simon@example.com"

# 导入核心模块
from . import config
from . import core
from . import services
from . import utils

__all__ = [
    "config",
    "core", 
    "services",
    "utils",
    "__version__",
    "__author__",
    "__email__",
]