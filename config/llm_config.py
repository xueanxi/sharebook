"""
本地LLM配置文件
用于连接本地部署的LLM服务
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class LLMConfig:
    """本地LLM配置类"""

    # 本地vllm
    # API_BASE = "http://127.0.0.1:8000/v1"
    # MODEL_NAME = "local-llm"
    # API_KEY = "123"

    # 服务器vllm
    API_BASE = "http://192.168.3.46:8000/v1"
    MODEL_NAME = "local-llm"
    API_KEY = "123"
    # API_BASE = "https://api-inference.modelscope.cn/v1"
    # MODEL_NAME = "Qwen/Qwen3-30B-A3B-Instruct-2507"
    # API_KEY = "ms-09b6bc00-d301-4fbb-9578-01105875a874"
    
    # 请求配置
    TIMEOUT = 30  # 请求超时时间（秒）
    MAX_RETRIES = 3  # 最大重试次数
    TEMPERATURE = 0.4  # 默认温度参数
    
    # 模型参数
    MAX_TOKENS = 2000  # 最大生成token数
    TOP_P = 0.9  # 核采样参数
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """获取完整的配置字典"""
        return {
            "api_base": cls.API_BASE,
            "model_name": cls.MODEL_NAME,
            "api_key": cls.API_KEY,
            "timeout": cls.TIMEOUT,
            "max_retries": cls.MAX_RETRIES,
            "temperature": cls.TEMPERATURE,
            "max_tokens": cls.MAX_TOKENS,
            "top_p": cls.TOP_P,
        }
    
    @classmethod
    def validate_config(cls) -> bool:
        """验证配置是否有效"""
        if not cls.API_BASE:
            raise ValueError("API_BASE不能为空")
        if not cls.MODEL_NAME:
            raise ValueError("MODEL_NAME不能为空")
        if cls.TIMEOUT <= 0:
            raise ValueError("TIMEOUT必须大于0")
        if cls.MAX_RETRIES < 0:
            raise ValueError("MAX_RETRIES不能为负数")
        return True
    
    @classmethod
    def get_openai_kwargs(cls) -> Dict[str, Any]:
        """获取OpenAI兼容的参数"""
        return {
            "base_url": cls.API_BASE,
            "api_key": cls.API_KEY,
            "model": cls.MODEL_NAME,
            "timeout": cls.TIMEOUT,
            "max_retries": cls.MAX_RETRIES,
        }

# 验证配置
LLMConfig.validate_config()