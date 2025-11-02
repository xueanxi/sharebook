"""
统一日志管理系统
提供分类日志管理功能，支持通用日志、agent日志等不同类型的日志
"""

import os
import logging
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
import json
import threading
from pathlib import Path


class LogCategory(Enum):
    """日志分类枚举"""
    GENERAL = "general"      # 通用日志
    AGENT = "agent"          # Agent相关日志
    API = "api"              # API相关日志
    DATA = "data"            # 数据处理日志
    SYSTEM = "system"        # 系统日志
    ERROR = "error"          # 错误日志
    PERFORMANCE = "performance"  # 性能日志
    SECURITY = "security"    # 安全日志


class LogManager:
    """统一日志管理器"""
    
    _instance = None
    _lock = threading.Lock()
    _loggers: Dict[str, logging.Logger] = {}
    _config: Dict[str, Any] = {}
    
    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(LogManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化日志管理器"""
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        self._setup_default_config()
        self._setup_log_directory()
    
    def _setup_default_config(self):
        """设置默认配置"""
        # 获取项目根目录
        self.project_root = Path(__file__).parent.parent.parent
        self.log_dir = self.project_root / "logs"
        
        # 默认配置
        self._config = {
            "level": logging.INFO,
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "date_format": "%Y-%m-%d %H:%M:%S",
            "console_output": True,
            "file_output": True,
            "max_file_size": 10 * 1024 * 1024,  # 10MB
            "backup_count": 5,
            "encoding": "utf-8"
        }
        
        # 加载自定义配置（如果存在）
        config_file = self.project_root / "config" / "logging_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    custom_config = json.load(f)
                    self._config.update(custom_config)
            except Exception as e:
                print(f"加载日志配置文件失败: {e}")
    
    def _setup_log_directory(self):
        """设置日志目录结构"""
        # 创建主日志目录
        self.log_dir.mkdir(exist_ok=True)
        
        # 为每个日志分类创建子目录
        for category in LogCategory:
            category_dir = self.log_dir / category.value
            category_dir.mkdir(exist_ok=True)
    
    def _get_category_config(self, category: LogCategory) -> Dict[str, Any]:
        """获取分类特定配置
        
        Args:
            category: 日志分类
            
        Returns:
            分类配置字典
        """
        # 默认使用全局配置
        category_config = {
            "level": self._config["level"],
            "format": self._config["format"],
            "date_format": self._config["date_format"]
        }
        
        # 如果配置文件中有分类特定配置，则覆盖默认配置
        if "categories" in self._config and category.value in self._config["categories"]:
            cat_config = self._config["categories"][category.value]
            category_config.update(cat_config)
        
        return category_config
    
    def _get_log_file_path(self, category: LogCategory, name: str) -> str:
        """获取日志文件路径
        
        Args:
            category: 日志分类
            name: 日志记录器名称
            
        Returns:
            日志文件路径
        """
        current_date = datetime.now().strftime("%Y%m%d")
        # 使用分类目录和日期作为文件名
        file_name = f"{name}_{current_date}.log"
        return str(self.log_dir / category.value / file_name)
    
    def _create_formatter(self, category_config: Optional[Dict[str, Any]] = None) -> logging.Formatter:
        """创建日志格式化器
        
        Args:
            category_config: 分类特定配置，如果为None则使用全局配置
        """
        if category_config is None:
            format_str = self._config["format"]
            date_format = self._config["date_format"]
        else:
            format_str = category_config.get("format", self._config["format"])
            date_format = category_config.get("date_format", self._config["date_format"])
            
        return logging.Formatter(format_str, datefmt=date_format)
    
    def _create_console_handler(self, category_config: Optional[Dict[str, Any]] = None) -> logging.StreamHandler:
        """创建控制台处理器
        
        Args:
            category_config: 分类特定配置，如果为None则使用全局配置
        """
        if category_config is None:
            level = self._config["level"]
        else:
            # 优先使用分类特定的控制台级别，否则使用通用级别
            level = category_config.get("console_level", category_config.get("level", self._config["level"]))
            
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(self._create_formatter(category_config))
        return console_handler
    
    def _create_file_handler(self, file_path: str, category_config: Optional[Dict[str, Any]] = None) -> logging.Handler:
        """创建文件处理器
        
        Args:
            file_path: 日志文件路径
            category_config: 分类特定配置，如果为None则使用全局配置
        """
        from logging.handlers import RotatingFileHandler
        
        # 确保日志目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        if category_config is None:
            level = self._config["level"]
        else:
            # 优先使用分类特定的文件级别，否则使用通用级别
            level = category_config.get("file_level", category_config.get("level", self._config["level"]))
            
        file_handler = RotatingFileHandler(
            file_path,
            maxBytes=self._config["max_file_size"],
            backupCount=self._config["backup_count"],
            encoding=self._config["encoding"]
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(self._create_formatter(category_config))
        return file_handler
    
    def get_logger(self, name: str, category: LogCategory = LogCategory.GENERAL) -> logging.Logger:
        """获取指定分类的日志记录器
        
        Args:
            name: 日志记录器名称
            category: 日志分类
            
        Returns:
            配置好的日志记录器
        """
        # 创建唯一标识符
        logger_id = f"{category.value}.{name}"
        
        # 如果已存在，直接返回
        if logger_id in self._loggers:
            return self._loggers[logger_id]
        
        # 创建新的日志记录器
        logger = logging.getLogger(logger_id)
        
        # 获取分类特定配置
        category_config = self._get_category_config(category)
        logger.setLevel(category_config["level"])
        
        # 避免重复添加处理器
        if logger.handlers:
            return logger
        
        # 添加控制台处理器
        if self._config["console_output"]:
            console_handler = self._create_console_handler(category_config)
            logger.addHandler(console_handler)
        
        # 添加文件处理器
        if self._config["file_output"]:
            file_path = self._get_log_file_path(category, name)
            file_handler = self._create_file_handler(file_path, category_config)
            logger.addHandler(file_handler)
            logger.info(f"日志文件已创建: {file_path}")
        
        # 缓存日志记录器
        self._loggers[logger_id] = logger
        
        return logger
    
    def configure(self, **kwargs):
        """更新日志配置
        
        Args:
            **kwargs: 配置参数
        """
        self._config.update(kwargs)
        
        # 重新配置所有已存在的日志记录器
        for logger in self._loggers.values():
            logger.setLevel(self._config["level"])
            
            # 更新所有处理器的级别
            for handler in logger.handlers:
                handler.setLevel(self._config["level"])
    
    def set_level(self, level: int):
        """设置日志级别
        
        Args:
            level: 日志级别
        """
        self.configure(level=level)
    
    def get_log_files(self, category: Optional[LogCategory] = None) -> Dict[str, list]:
        """获取日志文件列表
        
        Args:
            category: 日志分类，如果为None则返回所有分类的日志文件
            
        Returns:
            日志文件列表字典
        """
        result = {}
        
        categories = [category] if category else list(LogCategory)
        
        for cat in categories:
            cat_dir = self.log_dir / cat.value
            if cat_dir.exists():
                result[cat.value] = [str(f) for f in cat_dir.glob("*.log")]
            else:
                result[cat.value] = []
        
        return result


# 创建全局日志管理器实例
log_manager = LogManager()


def get_logger(name: str, category: LogCategory = LogCategory.GENERAL) -> logging.Logger:
    """获取日志记录器的便捷函数
    
    Args:
        name: 日志记录器名称
        category: 日志分类
        
    Returns:
        配置好的日志记录器
    """
    return log_manager.get_logger(name, category)


def get_agent_logger(name: str) -> logging.Logger:
    """获取Agent日志记录器的便捷函数
    
    Args:
        name: 日志记录器名称
        
    Returns:
        配置好的Agent日志记录器
    """
    return get_logger(name, LogCategory.AGENT)


def get_agent_file_logger(name: str) -> logging.Logger:
    """获取仅写入文件的Agent日志记录器，用于记录详细输出（如LLM响应）
    
    Args:
        name: 日志记录器名称
        
    Returns:
        配置好的仅写入文件的Agent日志记录器
    """
    # 创建唯一标识符
    logger_id = f"{LogCategory.AGENT.value}.file_only.{name}"
    
    # 如果已存在，直接返回
    if logger_id in log_manager._loggers:
        return log_manager._loggers[logger_id]
    
    # 创建新的日志记录器
    logger = logging.getLogger(logger_id)
    
    # 获取分类特定配置
    category_config = log_manager._get_category_config(LogCategory.AGENT)
    logger.setLevel(category_config.get("file_level", category_config.get("level", log_manager._config["level"])))
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 只添加文件处理器，不添加控制台处理器
    if log_manager._config["file_output"]:
        file_path = log_manager._get_log_file_path(LogCategory.AGENT, f"{name}_detailed")
        file_handler = log_manager._create_file_handler(file_path, category_config)
        logger.addHandler(file_handler)
        logger.info(f"详细日志文件已创建: {file_path}")
    
    # 缓存日志记录器
    log_manager._loggers[logger_id] = logger
    
    return logger


def get_api_logger(name: str) -> logging.Logger:
    """获取API日志记录器的便捷函数
    
    Args:
        name: 日志记录器名称
        
    Returns:
        配置好的API日志记录器
    """
    return get_logger(name, LogCategory.API)


def get_data_logger(name: str) -> logging.Logger:
    """获取数据处理日志记录器的便捷函数
    
    Args:
        name: 日志记录器名称
        
    Returns:
        配置好的数据处理日志记录器
    """
    return get_logger(name, LogCategory.DATA)


def get_system_logger(name: str) -> logging.Logger:
    """获取系统日志记录器的便捷函数
    
    Args:
        name: 日志记录器名称
        
    Returns:
        配置好的系统日志记录器
    """
    return get_logger(name, LogCategory.SYSTEM)


def get_error_logger(name: str) -> logging.Logger:
    """获取错误日志记录器的便捷函数
    
    Args:
        name: 日志记录器名称
        
    Returns:
        配置好的错误日志记录器
    """
    return get_logger(name, LogCategory.ERROR)


def get_performance_logger(name: str) -> logging.Logger:
    """获取性能日志记录器的便捷函数
    
    Args:
        name: 日志记录器名称
        
    Returns:
        配置好的性能日志记录器
    """
    return get_logger(name, LogCategory.PERFORMANCE)


def get_security_logger(name: str) -> logging.Logger:
    """获取安全日志记录器的便捷函数
    
    Args:
        name: 日志记录器名称
        
    Returns:
        配置好的安全日志记录器
    """
    return get_logger(name, LogCategory.SECURITY)


# 装饰器函数，用于记录函数执行时间
def log_execution_time(logger: Optional[logging.Logger] = None):
    """记录函数执行时间的装饰器
    
    Args:
        logger: 日志记录器，如果为None则使用性能日志
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            
            # 获取日志记录器
            nonlocal logger
            if logger is None:
                logger = get_performance_logger(func.__module__)
            
            # 记录开始时间
            start_time = time.time()
            logger.info(f"开始执行函数: {func.__name__}")
            
            try:
                # 执行函数
                result = func(*args, **kwargs)
                
                # 计算执行时间
                end_time = time.time()
                duration = end_time - start_time
                
                logger.info(f"函数 {func.__name__} 执行完成，耗时: {duration:.2f}秒")
                return result
            except Exception as e:
                # 计算执行时间
                end_time = time.time()
                duration = end_time - start_time
                
                logger.error(f"函数 {func.__name__} 执行失败，耗时: {duration:.2f}秒，错误: {str(e)}")
                raise
        
        return wrapper
    return decorator


# 装饰器函数，用于记录Agent处理过程
def log_agent_process(func):
    """装饰器，用于记录Agent处理方法的开始和结束
    
    Args:
        func: 要装饰的函数
    """
    def wrapper(self, state, *args, **kwargs):
        import time
        import functools
        
        # 获取Agent日志记录器
        logger = get_agent_logger(self.__class__.__module__)
        
        class_name = self.__class__.__name__
        func_name = func.__name__
        
        # 获取输入文本信息（如果有）
        input_info = ""
        if isinstance(state, dict) and "text" in state:
            text = state["text"]
            if isinstance(text, str):
                input_info = f"，输入文本长度: {len(text)} 字符"
        
        logger.info(f"@{class_name}.{func_name} - 开始处理:{input_info}")
        start_time = time.time()
        
        try:
            result = func(self, state, *args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            
            # 获取输出信息（如果有）
            output_info = ""
            if isinstance(result, dict):
                output_keys = list(result.keys())
                output_info = f"，输出键: {output_keys}"
            
            logger.info(f"@{class_name}.{func_name} - 处理完成，耗时: {duration:.2f}秒{output_info}")
            return result
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            logger.error(f"@{class_name}.{func_name} - 处理失败，耗时: {duration:.2f}秒，错误: {str(e)}", exc_info=True)
            raise
    
    return wrapper