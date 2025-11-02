"""
内容创作模块的基础类和共享组件
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
from src.utils.logging_manager import get_agent_logger, get_agent_file_logger, log_agent_process


# 定义角色卡状态类型
class CharacterCardState(TypedDict):
    """角色卡生成状态"""
    character_info: Dict[str, Any]      # 角色基本信息
    original_text: str                  # 原文文本
    existing_cards: Dict[str, Any]      # 已存在的角色卡片
    temp_cards: Dict[str, Any]          # 临时角色卡片
    final_cards: Dict[str, Any]         # 最终角色卡片
    grouped_characters: Dict[str, List] # 分组后的角色
    completed_tasks: Annotated[List[str], operator.add]  # 已完成任务列表
    errors: Annotated[List[str], operator.add]           # 错误信息列表
    # 添加状态标记，用于跟踪哪些节点已完成
    grouping_done: bool
    extraction_done: bool
    merging_done: bool
    updating_done: bool


class BaseContentAgent:
    """内容创作Agent基类，提供通用功能"""
    
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
        from langchain_core.callbacks import BaseCallbackHandler
        
        class LLMCallbackHandler(BaseCallbackHandler):
            """自定义回调处理器，用于记录LLM的详细输出"""
            
            def __init__(self):
                self.logger = get_agent_logger(__name__.__class__)
                self.file_logger = get_agent_file_logger(__name__.__class__)
            
            def on_llm_start(self, serialized, prompts, **kwargs):
                """LLM开始时的回调"""
                self.file_logger.debug(f"LLM开始处理，提示: {prompts[0][:100]}...")
            
            def on_llm_end(self, response, **kwargs):
                """LLM结束时的回调"""
                if hasattr(response, 'generations') and response.generations:
                    for gen_list in response.generations:
                        for gen in gen_list:
                            self.file_logger.info(f"LLM输出: {gen.text}")
            
            def on_llm_error(self, error, **kwargs):
                """LLM出错时的回调"""
                self.logger.error(f"LLM处理出错: {str(error)}")
        
        # 创建提示模板
        prompt = ChatPromptTemplate.from_template(prompt_template)
        
        # 创建处理链，不使用bind方式添加回调
        chain = prompt | self.llm | StrOutputParser()
        
        # 保存回调处理器供后续使用
        self._llm_callback_handler = LLMCallbackHandler()
        
        return chain
    
    def _create_json_chain(self, prompt_template: str):
        """创建JSON处理链
        
        Args:
            prompt_template: 提示模板
            
        Returns:
            处理链
        """
        from langchain_core.callbacks import BaseCallbackHandler
        
        class LLMCallbackHandler(BaseCallbackHandler):
            """自定义回调处理器，用于记录LLM的详细输出"""
            
            def __init__(self):
                self.logger = get_agent_logger(__name__.__class__)
                self.file_logger = get_agent_file_logger(__name__.__class__)
            
            def on_llm_start(self, serialized, prompts, **kwargs):
                """LLM开始时的回调"""
                self.file_logger.debug(f"LLM开始处理，提示: {prompts[0][:100]}...")
            
            def on_llm_end(self, response, **kwargs):
                """LLM结束时的回调"""
                if hasattr(response, 'generations') and response.generations:
                    for gen_list in response.generations:
                        for gen in gen_list:
                            self.file_logger.info(f"LLM输出: {gen.text}")
            
            def on_llm_error(self, error, **kwargs):
                """LLM出错时的回调"""
                self.logger.error(f"LLM处理出错: {str(error)}")
        
        # 创建提示模板
        prompt = ChatPromptTemplate.from_template(prompt_template)
        
        # 创建处理链
        chain = prompt | self.llm | JsonOutputParser()
        
        # 保存回调处理器供后续使用
        self._llm_callback_handler = LLMCallbackHandler()
        
        return chain


class BaseCharacterCardAgent(BaseContentAgent):
    """角色卡生成Agent基类，继承自BaseContentAgent"""
    
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
    
    @log_agent_process
    def process(self, state: CharacterCardState) -> None:
        """处理状态的抽象方法，子类需要实现
        
        Args:
            state: 角色卡生成状态
        """
        raise NotImplementedError("子类必须实现process方法")