"""
统一日志管理系统
提供分类日志管理功能，支持通用日志、agent日志等不同类型的日志
"""

import os
import logging

import logging.handlers
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
import json
import threading
from pathlib import Path

class LogModule(Enum):
    """日志模块枚举"""
    NOVEL_TO_COMIC = "novel_to_comic"          # 小说转漫画模块
    CHARACTER_IMAGE_GENERATION = "character_image_generation"  # 角色图片生成模块
    COMIC_IMAGE_GENERATION = "comic_image_generation"          # 漫画图片生成模块
    EXTRACTION = "extraction"                  # 信息提取模块
    EXTRACTION_CHARACTER = "extraction_character"  # 角色提取模块
    STORYBOARD_TO_PROMPT = "storyboard_to_prompt"  # 故事板到提示词转换模块
    CHARACTER_CARD = "character_card"          # 角色卡片模块
    CORE = "core"                              # 核心模块
    UTILS = "utils"                            # 工具模块
    API = "api"                                # API模块
    MAIN = "main"                              # 主程序模块


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
            "encoding": "utf-8",
            "use_module_based_logging": True
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
        
        # 为每个日志模块创建子目录
        for module in LogModule:
            module_dir = self.log_dir / module.value
            module_dir.mkdir(exist_ok=True)
    
    def _get_module_from_name(self, name: str) -> LogModule:
        """根据名称获取对应的模块
        
        注意：现在不再支持字符串映射，只能通过get_module_logger使用LogModule枚举
        
        Args:
            name: 日志记录器名称
            
        Returns:
            对应的日志模块
        """
        # 创建名称到模块的映射
        name_to_module = {
            # 直接映射
            "novel_to_comic": LogModule.NOVEL_TO_COMIC,
            "character_image_generation": LogModule.CHARACTER_IMAGE_GENERATION,
            "comic_image_generation": LogModule.COMIC_IMAGE_GENERATION,
            "extraction": LogModule.EXTRACTION,
            "extraction_character": LogModule.EXTRACTION_CHARACTER,
            "storyboard_to_prompt": LogModule.STORYBOARD_TO_PROMPT,
            "character_card": LogModule.CHARACTER_CARD,
            "core": LogModule.CORE,
            "utils": LogModule.UTILS,
            "api": LogModule.API,
            "main": LogModule.MAIN,
        }
        
        # 如果名称直接匹配，返回对应的模块
        if name in name_to_module:
            return name_to_module[name]
        # 默认返回通用模块
        return LogModule.MAIN
    
    def _get_module_config(self, module: LogModule) -> Dict[str, Any]:
        """获取模块特定配置
        
        Args:
            module: 日志模块
            
        Returns:
            模块配置字典
        """
        # 默认使用全局配置
        module_config = {
            "level": self._config["level"],
            "format": self._config["format"],
            "date_format": self._config["date_format"]
        }
        
        # 如果配置文件中有模块特定配置，则覆盖默认配置
        if "modules" in self._config and module.value in self._config["modules"]:
            mod_config = self._config["modules"][module.value]
            module_config.update(mod_config)
        
        return module_config
    
    def _get_log_file_path(self, name: str) -> str:
        """获取日志文件路径
        
        Args:
            name: 日志记录器名称
            
        Returns:
            日志文件路径
        """
        current_date = datetime.now().strftime("%Y%m%d")
        
        # 获取模块名
        module = self._get_module_from_name(name)
        
        # 使用模块名和日期作为文件名，格式为：模块名-日期.log
        file_name = f"{module.value}-{current_date}.log"
        return str(self.log_dir / module.value / file_name)
    
    def _create_formatter(self, module_config: Optional[Dict[str, Any]] = None) -> logging.Formatter:
        """创建日志格式化器
        
        Args:
            module_config: 模块特定配置，如果为None则使用全局配置
        """
        if module_config is None:
            format_str = self._config["format"]
            date_format = self._config["date_format"]
        else:
            format_str = module_config.get("format", self._config["format"])
            date_format = module_config.get("date_format", self._config["date_format"])
            
        return logging.Formatter(format_str, datefmt=date_format)
    
    def _create_console_handler(self, module_config: Optional[Dict[str, Any]] = None) -> logging.StreamHandler:
        """创建控制台处理器
        
        Args:
            module_config: 模块特定配置，如果为None则使用全局配置
        """
        if module_config is None:
            level = self._config["level"]
        else:
            # 优先使用模块特定的控制台级别，否则使用通用级别
            level = module_config.get("console_level", module_config.get("level", self._config["level"]))
            
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(self._create_formatter(module_config))
        return console_handler
    
    def _create_file_handler(self, file_path: str, module_config: Optional[Dict[str, Any]] = None) -> logging.Handler:
        """创建文件处理器
        
        Args:
            file_path: 日志文件路径
            module_config: 模块特定配置，如果为None则使用全局配置
        """
        from logging.handlers import RotatingFileHandler
        
        # 确保日志目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        if module_config is None:
            level = self._config["level"]
        else:
            # 优先使用模块特定的文件级别，否则使用通用级别
            level = module_config.get("file_level", module_config.get("level", self._config["level"]))
            
        file_handler = RotatingFileHandler(
            file_path,
            maxBytes=self._config["max_file_size"],
            backupCount=self._config["backup_count"],
            encoding=self._config["encoding"]
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(self._create_formatter(module_config))
        return file_handler
    
    def get_logger(self, name: str) -> logging.Logger:
        """获取指定名称的日志记录器
        
        Args:
            name: 日志记录器名称
            
        Returns:
            配置好的日志记录器
        """
        # 获取模块信息
        module = self._get_module_from_name(name)
        
        # 创建唯一的logger_id，包含模块信息
        logger_id = name
        
        # 如果logger已存在，直接返回
        if logger_id in self._loggers:
            return self._loggers[logger_id]
        
        # 创建新的logger
        logger = logging.getLogger(logger_id)
        logger.setLevel(logging.DEBUG)  # 设置最低级别，由handler控制
        
        # 清除已有的处理器
        logger.handlers.clear()
        
        # 获取模块特定配置
        module_config = self._get_module_config(module)
        
        # 合并配置优先级：模块全局 > 全局
        level = module_config.get("level", self._config.get("level", logging.INFO))
        format_str = module_config.get("format", self._config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        
        # 创建格式化器
        formatter = logging.Formatter(
            format_str,
            datefmt=self._config.get("date_format", "%Y-%m-%d %H:%M:%S")
        )
        
        # 添加控制台处理器
        if self._config.get("console_output", True):
            console_handler = logging.StreamHandler()
            console_level = module_config.get("console_level", level)
            console_handler.setLevel(console_level)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # 添加文件处理器
        if self._config.get("file_output", True):
            # 获取日志文件路径
            log_file_path = self._get_log_file_path(name)
            file_level = module_config.get("file_level", level)
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_file_path,
                maxBytes=self._config.get("max_file_size", 10 * 1024 * 1024),
                backupCount=self._config.get("backup_count", 5),
                encoding=self._config.get("encoding", "utf-8")
            )
            file_handler.setLevel(file_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        # 缓存logger
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
    
    def get_log_files(self, module: Optional[LogModule] = None) -> Dict[str, list]:
        """获取日志文件列表
        
        Args:
            module: 日志模块，如果为None则返回所有模块的日志文件
            
        Returns:
            日志文件列表字典
        """
        result = {}
        
        modules = [module] if module else list(LogModule)
        
        for mod in modules:
            mod_dir = self.log_dir / mod.value
            if mod_dir.exists():
                result[mod.value] = [str(f) for f in mod_dir.glob("*.log")]
            else:
                result[mod.value] = []
        
        return result


# 创建全局日志管理器实例
log_manager = LogManager()


def get_logger(name: str) -> logging.Logger:
    """获取日志记录器的便捷函数
    
    Args:
        name: 日志记录器名称
        
    Returns:
        配置好的日志记录器
    """
    return log_manager.get_logger(name)


def get_module_logger(module: LogModule) -> logging.Logger:
    """获取模块级别的日志记录器
    
    Args:
        module: 日志模块
        
    Returns:
        配置好的模块日志记录器
    """
    # 使用模块值作为日志记录器名称
    name = module.value
    return get_logger(name)


# 装饰器函数，用于记录函数执行时间
def log_execution_time(module: LogModule = LogModule.CORE, include_args: bool = False):
    """记录函数执行时间的装饰器
    
    Args:
        module: 日志模块
        include_args: 是否在日志中包含函数参数
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            import functools
            
            # 获取日志记录器
            logger = get_module_logger(module)
            
            # 记录开始时间
            start_time = time.time()
            
            # 记录函数调用开始
            if include_args:
                logger.debug(f"开始执行函数 {func.__name__}，参数: args={args}, kwargs={kwargs}")
            else:
                logger.debug(f"开始执行函数 {func.__name__}")
            
            try:
                # 执行函数
                result = func(*args, **kwargs)
                
                # 计算执行时间
                execution_time = time.time() - start_time
                logger.info(f"函数 {func.__name__} 执行完成，耗时: {execution_time:.4f}秒")
                return result
            except Exception as e:
                # 计算执行时间
                execution_time = time.time() - start_time
                logger.error(f"函数 {func.__name__} 执行失败，耗时: {execution_time:.4f}秒，错误: {str(e)}")
                raise
        
        return wrapper
    return decorator


# 装饰器函数，用于记录Agent处理过程
def log_agent_process(module: LogModule = LogModule.NOVEL_TO_COMIC, include_args: bool = False):
    """记录Agent处理过程的装饰器
    
    Args:
        module: 日志模块
        include_args: 是否在日志中包含函数参数
    """
    def decorator(func):
        def wrapper(self, state, *args, **kwargs):
            import time
            import functools
            
            # 获取Agent日志记录器
            logger = get_module_logger(module)
            
            class_name = self.__class__.__name__
            func_name = func.__name__
            
            # 获取输入文本信息（如果有）
            input_info = ""
            if isinstance(state, dict) and "text" in state:
                text = state["text"]
                if isinstance(text, str):
                    input_info = f"，输入文本长度: {len(text)} 字符"
            
            # 记录Agent处理开始
            if include_args:
                logger.info(f"@{class_name}.{func_name} - 开始处理:{input_info}，参数: args={args}, kwargs={kwargs}")
            else:
                logger.info(f"@{class_name}.{func_name} - 开始处理:{input_info}")
            
            start_time = time.time()
            
            try:
                result = func(self, state, *args, **kwargs)
                execution_time = time.time() - start_time
                
                # 获取输出信息（如果有）
                output_info = ""
                if isinstance(result, dict):
                    output_keys = list(result.keys())
                    output_info = f"，输出键: {output_keys}"
                
                logger.info(f"@{class_name}.{func_name} - 处理完成，耗时: {execution_time:.4f}秒{output_info}")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"@{class_name}.{func_name} - 处理失败，耗时: {execution_time:.4f}秒，错误: {str(e)}", exc_info=True)
                raise
        
        return wrapper
    return decorator