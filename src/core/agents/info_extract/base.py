"""
信息提取模块的基础类和共享组件
"""

import re
import logging
import time
import functools
from typing import Dict, List, Any, Optional, TypedDict, Annotated
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
import operator

from config.llm_config import LLMConfig
from config.logging_config import get_logger

# 初始化日志记录器
logger = get_logger(__name__)

def log_process(func):
    """装饰器，用于记录process方法的开始和结束，同时输出到控制台和日志文件"""
    @functools.wraps(func)
    def wrapper(self, state, *args, **kwargs):
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


# 定义状态类型
class NovelExtractionState(TypedDict):
    """并行提取状态"""
    text: str
    preprocessed_text: str
    character_info: Dict[str, Any]
    plot_info: Dict[str, Any]
    satisfaction_info: Dict[str, Any]
    completed_tasks: Annotated[List[str], operator.add]
    errors: Annotated[List[str], operator.add]
    # 添加状态标记，用于跟踪哪些节点已完成
    preprocess_done: bool
    character_done: bool
    plot_done: bool
    satisfaction_done: bool


class BaseAgent:
    """Agent基类，提供通用功能"""
    
    def __init__(self, model_name: Optional[str] = None, temperature: float = 0.7):
        """初始化Agent
        
        Args:
            model_name: 模型名称，如果为None则使用配置文件中的默认模型
            temperature: 温度参数，控制输出的随机性
        """
        # 获取LLM配置
        self.llm_kwargs = LLMConfig.get_openai_kwargs()
        
        # 如果指定了模型名称，覆盖配置
        if model_name:
            self.llm_kwargs["model_name"] = model_name
            
        # 设置温度参数
        self.llm_kwargs["temperature"] = temperature
        
        # 创建LLM实例
        self.llm = ChatOpenAI(**self.llm_kwargs)
    
    def _create_chain(self, prompt_template: str):
        """创建处理链
        
        Args:
            prompt_template: 提示模板
            
        Returns:
            处理链
        """
        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = prompt | self.llm | StrOutputParser()
        return chain
    
    def _simple_text_cleaning(self, text: str) -> str:
        """简单的文本清洗方法，作为备用方案
        
        Args:
            text: 原始文本
            
        Returns:
            清洗后的文本
        """
        # 去除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 去除特殊字符，但保留中文、英文、数字和基本标点
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s\.,!?;:()（）。，！？；：]', '', text)
        
        # 去除首尾空白
        text = text.strip()
        
        return text


class BaseExtractor(BaseAgent):
    """提取器基类，继承自BaseAgent，提供提取功能"""
    
    def __init__(self, model_name: Optional[str] = None, temperature: float = 0.7):
        super().__init__(model_name, temperature)
    
    def extract(self, text: str) -> Dict[str, Any]:
        """提取信息的抽象方法，子类需要实现
        
        Args:
            text: 输入文本
            
        Returns:
            提取结果
        """
        raise NotImplementedError("子类必须实现extract方法")
    
    @log_process
    def process(self, state: NovelExtractionState) -> None:
        """处理状态的抽象方法，子类需要实现
        
        Args:
            state: 并行提取状态
        """
        raise NotImplementedError("子类必须实现process方法")