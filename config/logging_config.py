"""
日志配置模块
提供统一的日志配置管理
"""

import os
import logging
from datetime import datetime
from typing import Optional

def setup_logger(name: str, log_file: Optional[str] = None, level=logging.INFO):
    """设置日志记录器，同时输出到控制台和文件
    
    Args:
        name: 日志记录器名称
        log_file: 日志文件路径，如果为None则使用默认路径
        level: 日志级别
        
    Returns:
        配置好的日志记录器
    """
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 创建文件处理器
    if log_file is None:
        # 创建logs目录（如果不存在）
        # 从config目录向上两级到项目根目录
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # 使用当前日期作为日志文件名
        current_date = datetime.now().strftime("%Y%m%d")
        log_file = os.path.join(log_dir, f"sharebook_{current_date}.log")
    
    # 确保日志目录存在
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 记录日志文件创建信息
    logger.info(f"日志文件已创建: {log_file}")
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """获取日志记录器的便捷函数
    
    Args:
        name: 日志记录器名称
        
    Returns:
        配置好的日志记录器
    """
    return setup_logger(name)