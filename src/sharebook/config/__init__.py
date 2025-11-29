"""
配置管理模块

提供项目配置的统一管理，包括LLM配置、日志配置、嵌入模型配置等。
"""

from .llm_config import LLMConfig
from ..utils.logging_manager import get_logger
from .embeddings_config import get_embeddings_config

__all__ = [
    "LLMConfig",
    "get_logger", 
    "get_embeddings_config",
]