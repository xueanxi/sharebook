"""
日志配置模块
提供统一的日志配置管理，已迁移到新的统一日志管理系统
"""

import logging
from typing import Optional

# 为了向后兼容，保留原有的函数名
def setup_logger(name: str, log_file: Optional[str] = None, level=logging.INFO):
    """设置日志记录器，同时输出到控制台和文件
    
    Args:
        name: 日志记录器名称
        log_file: 日志文件路径（已弃用，新系统自动管理日志文件）
        level: 日志级别
        
    Returns:
        配置好的日志记录器
    """
    # 延迟导入以避免循环导入
    from sharebook.utils.logging_manager import get_logger, log_manager
    
    # 使用新的日志管理系统
    logger = get_logger(name)
    
    # 如果指定了日志级别，更新配置
    if level != logging.INFO:
        log_manager.set_level(level)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """获取日志记录器的便捷函数
    
    Args:
        name: 日志记录器名称
        
    Returns:
        配置好的日志记录器
    """
    # 延迟导入以避免循环导入
    from sharebook.utils.logging_manager import get_logger
    
    # 使用新的日志管理系统
    return get_logger(name)

def get_module_logger(module_name, log_level: Optional[str] = None) -> logging.Logger:
    """获取模块日志记录器的便捷函数
    
    Args:
        module_name: 模块名称（可以是字符串或LogModule枚举）
        log_level: 日志级别
        
    Returns:
        配置好的日志记录器
    """
    # 延迟导入以避免循环导入
    from sharebook.utils.logging_manager import get_logger, LogModule
    
    # 处理枚举类型
    if hasattr(module_name, 'value'):
        # 如果是枚举，获取其值
        name = module_name.value
    else:
        # 如果是字符串，直接使用
        name = str(module_name)
    
    # 使用新的日志管理系统
    logger = get_module_logger(name)
    
    # 如果指定了日志级别，更新配置
    if log_level:
        from sharebook.utils.logging_manager import log_manager
        log_manager.set_level(log_level)
    
    return logger

# 导入LogModule枚举
try:
    from sharebook.utils.logging_manager import LogModule
except ImportError:
    # 如果导入失败，创建一个简单的枚举
    from enum import Enum
    class LogModule(Enum):
        AGENT = "agent"
        API = "api"
        DATA = "data"
        ERROR = "error"
        GENERAL = "general"
        PERFORMANCE = "performance"
        SECURITY = "security"
        SYSTEM = "system"