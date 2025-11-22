"""
工具模块初始化

此模块在导入时会自动初始化CommonConfig全局实例，确保配置在整个应用程序中可用。
使用方式:
1. 直接导入utils模块: from src import utils
   然后通过 utils._common_config 访问配置实例

2. 或者使用get_common_config函数: from src.utils.common_config import get_common_config
   然后通过 get_common_config() 获取配置实例

注意: 建议使用第二种方式，因为它更加明确且符合Python的最佳实践。
"""

# 初始化通用配置实例
from .common_config import get_common_config

# 在模块导入时自动创建全局配置实例
# 这样可以确保配置在应用程序启动时就被加载
_common_config = get_common_config()

# 导出常用工具
__all__ = [
    'get_common_config',
    '_common_config'
]