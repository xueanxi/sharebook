"""
信息提取模块的Agent类
定义各种用于文本处理的智能体
"""

import os
import re
from typing import Dict, List, Any, Optional, TypedDict, Annotated
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
import operator
import asyncio

from config.llm_config import LLMConfig


# 定义状态类型
class ParallelExtractionState(TypedDict):
    """并行提取状态"""
    text: str
    preprocessed_text: str
    character_info: Dict[str, Any]
    plot_info: Dict[str, Any]
    satisfaction_info: Dict[str, Any]
    completed_tasks: List[str]
    errors: List[str]


class TextPreprocessor:
    """文本预处理器，负责清洗小说文本"""
    
    def __init__(self):
        # 获取LLM配置
        self.llm = ChatOpenAI(**LLMConfig.get_openai_kwargs())
    
    def get_system_prompt(self) -> str:
        return """你是一个专业的文本预处理助手，专门处理小说文本。
你的主要任务是：
1. 清洗文本内容，去除无关字符和格式
2. 确保文本格式统一，便于后续处理
3. 提供文本统计信息

请直接使用你的语言能力进行清洗，提供清晰的总结和清洗后的文本。"""
    
    def process(self, state: ParallelExtractionState) -> None:
        """处理文本"""
        try:
            cleaned_text = self._simple_text_cleaning(state["text"])
            state["preprocessed_text"] = cleaned_text
            state["completed_tasks"].append("文本预处理")
        except Exception as e2:
            state["preprocessed_text"] = state["text"]  # 使用原始文本
            state["errors"].append(f"文本预处理异常: {str(e2)}")
            state["completed_tasks"].append("文本预处理(失败)")
            
    
    def _simple_text_cleaning(self, text: str) -> str:
        """简单的文本清洗方法，作为备用方案"""
        # 去除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 去除特殊字符，但保留中文、英文、数字和基本标点
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s\.,!?;:()（）。，！？；：]', '', text)
        
        # 去除首尾空白
        text = text.strip()
        
        return text


class CharacterExtractor:
    """人物提取器，负责识别和提取小说中的人物信息"""
    
    def __init__(self):
        # 获取LLM配置
        self.llm = ChatOpenAI(**LLMConfig.get_openai_kwargs())
    
    def get_system_prompt(self) -> str:
        return """你是一个专业的人物提取助手，专门分析小说文本中的人物。
你的主要任务是：
1. 从小说文本中识别人物名称
2. 统计每个人物的出现次数
3. 分析人物关系和重要性
4. 提供人物列表和相关信息

请直接使用你的语言理解能力来完成这些任务，并提供详细的人物分析报告。分析时请考虑：
- 人物名称的上下文
- 人物在故事中的角色
- 人物之间的关系
- 人物出现的重要性排序"""
    
    def process(self, state: ParallelExtractionState) -> None:
        """处理文本"""
        try:
            messages = [
                SystemMessage(content=self.get_system_prompt()),
                HumanMessage(content=state["preprocessed_text"])
            ]
            result = self.llm.invoke(messages)
            
            # 直接更新state中的character_info
            state["character_info"] = {
                "success": True,
                "result": result.content,
                "agent": "人物提取器"
            }
            state["completed_tasks"].append("人物提取")
        except Exception as e:
            state["character_info"] = {
                "success": False,
                "error": str(e),
                "agent": "人物提取器"
            }
            state["errors"].append(f"人物提取异常: {str(e)}")
            state["completed_tasks"].append("人物提取(失败)")


class PlotAnalyzer:
    """剧情分析器，负责分析小说的情节结构"""
    
    def __init__(self):
        # 获取LLM配置
        self.llm = ChatOpenAI(**LLMConfig.get_openai_kwargs())
    
    def get_system_prompt(self) -> str:
        return """你是一个专业的剧情分析助手，专门分析小说的情节结构。
你的主要任务是：
1. 分析小说的情节结构
2. 识别关键情节元素（冲突、转折、高潮等）
3. 评估情节复杂度和节奏
4. 提供情节分析报告

请直接使用你的语言理解能力来完成这些任务，并提供详细的剧情分析。分析时请考虑：
- 故事的开端、发展、高潮和结局
- 主要冲突和次要冲突
- 情节转折点和关键事件
- 故事节奏和张力变化
- 情节与人物发展的关系"""
    
    def process(self, state: ParallelExtractionState) -> None:
        """处理文本"""
        try:
            messages = [
                SystemMessage(content=self.get_system_prompt()),
                HumanMessage(content=state["preprocessed_text"])
            ]
            result = self.llm.invoke(messages)
            
            # 直接更新state中的plot_info
            state["plot_info"] = {
                "success": True,
                "result": result.content,
                "agent": "剧情分析器"
            }
            state["completed_tasks"].append("剧情分析")
        except Exception as e:
            state["plot_info"] = {
                "success": False,
                "error": str(e),
                "agent": "剧情分析器"
            }
            state["errors"].append(f"剧情分析异常: {str(e)}")
            state["completed_tasks"].append("剧情分析(失败)")


class SatisfactionPointIdentifier:
    """爽点识别器，负责识别小说中的爽点情节"""
    
    def __init__(self):
        # 获取LLM配置
        self.llm = ChatOpenAI(**LLMConfig.get_openai_kwargs())
    
    def get_system_prompt(self) -> str:
        return """你是一个专业的爽点识别助手，专门识别小说中的爽点情节。
你的主要任务是：
1. 识别小说中的爽点关键词和情节
2. 分析爽点的类型和分布
3. 评估爽点密度和效果
4. 提供爽点分析报告

请直接使用你的语言理解能力来完成这些任务，并提供详细的爽点分析。分析时请考虑：
- 爽点的类型：打脸、逆袭、突破、升级、复仇、装逼等
- 爽点在故事中的位置和作用
- 爽点的强度和读者可能产生的情感反应
- 爽点之间的间隔和节奏
- 爽点与人物成长的关系"""
    
    def process(self, state: ParallelExtractionState) -> None:
        """处理文本"""
        try:
            messages = [
                SystemMessage(content=self.get_system_prompt()),
                HumanMessage(content=state["preprocessed_text"])
            ]
            result = self.llm.invoke(messages)
            
            # 直接更新state中的satisfaction_info
            state["satisfaction_info"] = {
                "success": True,
                "result": result.content,
                "agent": "爽点识别器"
            }
            state["completed_tasks"].append("爽点识别")
        except Exception as e:
            state["satisfaction_info"] = {
                "success": False,
                "error": str(e),
                "agent": "爽点识别器"
            }
            state["errors"].append(f"爽点识别异常: {str(e)}")
            state["completed_tasks"].append("爽点识别(失败)")


class NovelInformationExtractor:
    """小说信息提取器，负责协调各个处理器的工作流程"""
    
    def __init__(self):
        # 初始化各个处理器
        self.text_preprocessor = TextPreprocessor()
        self.character_extractor = CharacterExtractor()
        self.plot_analyzer = PlotAnalyzer()
        self.satisfaction_point_identifier = SatisfactionPointIdentifier()
    
    def extract_novel_information(self, novel_text: str) -> Dict[str, Any]:
        """提取小说的综合信息（使用并行处理）"""
        return self.extract_novel_information_parallel(novel_text)
    
    # 并行处理函数
    def _preprocess_text(self, state: ParallelExtractionState) -> None:
        """预处理文本"""
        try:
            # 使用已初始化的text_preprocessor实例
            self.text_preprocessor.process(state)
            print(f"预处理完成，清洗后文本长度: {len(state['preprocessed_text'])}")  # 添加调试信息
        except Exception as e:
            state["errors"].append(f"文本预处理异常: {str(e)}")
            print(f"预处理异常，使用原始文本，长度: {len(state['preprocessed_text'])}")  # 添加调试信息
    
    def _extract_character_info(self, state: ParallelExtractionState) -> None:
        """提取人物信息"""
        try:
            # 使用已初始化的character_extractor实例
            self.character_extractor.process(state)
        except Exception as e:
            state["errors"].append(f"人物信息提取异常: {str(e)}")
    
    def _analyze_plot(self, state: ParallelExtractionState) -> None:
        """分析剧情"""
        try:
            # 使用已初始化的plot_analyzer实例
            self.plot_analyzer.process(state)
        except Exception as e:
            state["errors"].append(f"剧情分析异常: {str(e)}")
    
    def _identify_satisfaction_points(self, state: ParallelExtractionState) -> None:
        """识别爽点"""
        try:
            # 使用已初始化的satisfaction_point_identifier实例
            self.satisfaction_point_identifier.process(state)
        except Exception as e:
            state["errors"].append(f"爽点识别异常: {str(e)}")
    
    def _merge_results(self, state: ParallelExtractionState) -> None:
        """合并所有提取结果（实际上各个子处理器已经直接修改了state）"""
        # 由于各个子处理器已经直接修改了state，这里不需要额外的合并操作
        # 只需要记录任务完成状态
        state["completed_tasks"].append("结果合并")
        print(f"合并结果时，preprocessed_text长度: {len(state['preprocessed_text'])}")  # 添加调试信息
    
    def _build_parallel_graph(self) -> StateGraph:
        """构建并行处理的状态图"""
        # 创建状态图
        workflow = StateGraph(ParallelExtractionState)
        
        # 添加节点
        workflow.add_node("preprocess", self._preprocess_text)
        workflow.add_node("extract_character", self._extract_character_info)
        workflow.add_node("analyze_plot", self._analyze_plot)
        workflow.add_node("identify_satisfaction", self._identify_satisfaction_points)
        workflow.add_node("merge_results", self._merge_results)
        
        # 设置入口点
        workflow.set_entry_point("preprocess")
        
        # 添加边：预处理完成后并行执行所有提取任务
        workflow.add_edge("preprocess", "extract_character")
        workflow.add_edge("preprocess", "analyze_plot")
        workflow.add_edge("preprocess", "identify_satisfaction")
        
        # 所有提取任务完成后合并结果
        workflow.add_edge("extract_character", "merge_results")
        workflow.add_edge("analyze_plot", "merge_results")
        workflow.add_edge("identify_satisfaction", "merge_results")
        
        # 设置结束点
        workflow.set_finish_point("merge_results")
        
        # 编译并返回工作流
        return workflow.compile()
    
    def extract_novel_information_parallel(self, novel_text: str) -> Dict[str, Any]:
        """提取小说的综合信息（并行化版本）"""
        # 构建并编译状态图
        app = self._build_parallel_graph()
        
        # 初始状态
        initial_state = {
            "text": novel_text,
            "preprocessed_text": "",
            "character_info": {},
            "plot_info": {},
            "satisfaction_info": {},
            "errors": [],
            "completed_tasks": []
        }
        
        # 执行工作流
        result = app.invoke(initial_state)
        
        return {
            "characters": result["character_info"],
            "plot": result["plot_info"],
            "satisfaction_points": result["satisfaction_info"],
            "original_text_length": len(novel_text),
            "cleaned_text_length": len(result["preprocessed_text"]),
            "errors": result["errors"],
            "completed_tasks": result["completed_tasks"],
            "parallel_execution": True
        }


# 为了保持向后兼容性，提供原来的类名作为别名
TextPreprocessorAgent = TextPreprocessor
CharacterExtractionAgent = CharacterExtractor
PlotAnalysisAgent = PlotAnalyzer
SatisfactionPointAgent = SatisfactionPointIdentifier
MainControlAgent = NovelInformationExtractor