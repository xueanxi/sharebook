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
    from src.utils.logging_manager import get_logger, log_manager
    
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
    from src.utils.logging_manager import get_logger
    
    # 使用新的日志管理系统
    return get_logger(name)