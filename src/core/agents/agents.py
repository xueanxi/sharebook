"""
信息提取模块的Agent类
定义各种用于文本处理的智能体
"""

import os
from typing import Dict, List, Any, Optional, TypedDict, Annotated
from langchain.agents import create_agent
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
import operator
import asyncio
from concurrent.futures import ThreadPoolExecutor

from src.utils.text_processing.tools import (
    load_text_from_file
)

from config.llm_config import LLMConfig


# 定义并行提取状态
class ParallelExtractionState(TypedDict):
    text: str  # 待处理的文本
    preprocessed_text: str  # 预处理后的文本
    character_info: Dict[str, Any]  # 人物信息
    plot_info: Dict[str, Any]  # 剧情信息
    satisfaction_info: Dict[str, Any]  # 爽点信息
    errors: Annotated[List[str], operator.add]  # 错误信息列表
    completed_tasks: Annotated[List[str], operator.add]  # 已完成任务列表


class BaseAgent:
    """基础Agent类，提供通用功能"""
    
    def __init__(self, name: str, description: str, tools: List[Any]):
        self.name = name
        self.description = description
        self.tools = tools
        
        # 获取LLM配置
        llm_config = LLMConfig.get_config()
        self.llm = ChatOpenAI(
            model=llm_config["model_name"],
            api_key=llm_config["api_key"],
            base_url=llm_config["api_base"],
            temperature=llm_config["temperature"],
            max_tokens=llm_config["max_tokens"],
            timeout=llm_config["timeout"]
        )
        
        # 创建Agent
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=self._get_system_prompt()
        )
    
    def _get_system_prompt(self) -> str:
        """获取系统提示，子类可以重写此方法"""
        return f"你是一个名为{self.name}的AI助手。{self.description}"
    
    def run(self, input_text: str) -> Dict[str, Any]:
        """运行Agent"""
        try:
            # 在LangChain v1.0.0中，Agent的调用方式可能有所不同
            # 可能需要使用AgentExecutor或其他方式来执行
            result = self.agent.invoke({"messages": [HumanMessage(content=input_text)]})
            return {
                "success": True,
                "result": result,
                "agent": self.name
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent": self.name
            }
    
    def process(self, text: str) -> Dict[str, Any]:
        """直接处理文本，不使用Agent框架"""
        try:
            # 直接使用LLM处理文本
            messages = [
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=text)
            ]
            result = self.llm.invoke(messages)
            
            return {
                "success": True,
                "result": result.content,
                "agent": self.name
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent": self.name
            }


class TextPreprocessorAgent(BaseAgent):
    """文本预处理Agent，负责加载和清洗小说文本"""
    
    def __init__(self):
        name = "文本预处理助手"
        description = "专门负责加载和清洗小说文本，包括去除无关内容、格式化文本等。"
        tools = [load_text_from_file]
        super().__init__(name, description, tools)
    
    def _get_system_prompt(self) -> str:
        return """你是一个专业的文本预处理助手，专门处理小说文本。
你的主要任务是：
1. 从指定路径加载小说文件
2. 清洗文本内容，去除无关字符和格式
3. 确保文本格式统一，便于后续处理
4. 提供文本统计信息

请始终使用提供的工具完成这些任务，并在处理完成后提供清晰的总结。当你需要清洗文本时，请直接使用你的语言能力进行清洗，而不是依赖特定的工具。"""


class CharacterExtractionAgent(BaseAgent):
    """人物提取Agent，负责识别和提取小说中的人物信息"""
    
    def __init__(self):
        name = "人物提取助手"
        description = "专门负责从小说文本中识别和提取人物信息，包括人物名称、出现次数等。"
        tools = []  # 不再使用特定工具，直接使用LLM能力
        super().__init__(name, description, tools)
    
    def _get_system_prompt(self) -> str:
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


class PlotAnalysisAgent(BaseAgent):
    """剧情分析Agent，负责分析小说的情节结构"""
    
    def __init__(self):
        name = "剧情分析助手"
        description = "专门负责分析小说的情节结构，包括冲突、转折、高潮等元素。"
        tools = []  # 不再使用特定工具，直接使用LLM能力
        super().__init__(name, description, tools)
    
    def _get_system_prompt(self) -> str:
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


class SatisfactionPointAgent(BaseAgent):
    """爽点识别Agent，负责识别小说中的爽点情节"""
    
    def __init__(self):
        name = "爽点识别助手"
        description = "专门负责识别小说中的爽点情节，如打脸、逆袭、突破等。"
        tools = []  # 不再使用特定工具，直接使用LLM能力
        super().__init__(name, description, tools)
    
    def _get_system_prompt(self) -> str:
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


class MainControlAgent(BaseAgent):
    """主控Agent，负责协调各个子Agent的工作流程"""
    
    def __init__(self):
        name = "信息提取主控助手"
        description = "负责协调各个子Agent的工作流程，完成小说信息的全面提取。"
        tools = []  # 主控Agent不直接使用工具，而是协调其他Agent
        super().__init__(name, description, tools)
        
        # 初始化子Agent
        self.text_preprocessor = TextPreprocessorAgent()
        self.character_extractor = CharacterExtractionAgent()
        self.plot_analyzer = PlotAnalysisAgent()
        self.satisfaction_point_agent = SatisfactionPointAgent()
    
    def _get_system_prompt(self) -> str:
        return """你是一个信息提取主控助手，负责协调各个子Agent完成小说信息的全面提取。
你的主要任务是：
1. 协调文本预处理、人物提取、剧情分析和爽点识别等子Agent
2. 整合各个子Agent的分析结果
3. 提供综合的信息提取报告
4. 确保整个信息提取流程的顺利进行

请根据需要调用适当的子Agent，并整合他们的分析结果。"""
    
    def extract_novel_information(self, novel_text: str) -> Dict[str, Any]:
        """提取小说的综合信息（原始版本）"""
        # 直接使用文本预处理Agent清洗文本
        text_processor = TextPreprocessorAgent()
        preprocessor_result = text_processor.process(novel_text)
        
        # 获取清洗后的文本
        if preprocessor_result.get("success", False):
            cleaned_text = preprocessor_result["result"]
        else:
            # 如果预处理失败，使用原始文本
            cleaned_text = novel_text
        
        # 使用人物提取Agent识别人物
        character_agent = CharacterExtractionAgent()
        character_info = character_agent.process(cleaned_text)
        
        # 使用剧情分析Agent分析情节
        plot_agent = PlotAnalysisAgent()
        plot_info = plot_agent.process(cleaned_text)
        
        # 使用爽点识别Agent识别爽点
        satisfaction_agent = SatisfactionPointAgent()
        satisfaction_info = satisfaction_agent.process(cleaned_text)
        
        return {
            "characters": character_info,
            "plot": plot_info,
            "satisfaction_points": satisfaction_info,
            "original_text_length": len(novel_text),
            "cleaned_text_length": len(cleaned_text)
        }
    
    # 并行处理函数
    def _preprocess_text(self, state: ParallelExtractionState) -> ParallelExtractionState:
        """预处理文本"""
        try:
            text_processor = TextPreprocessorAgent()
            preprocessor_result = text_processor.process(state["text"])
            
            # 创建新状态而不是修改现有状态
            new_state = state.copy()
            new_state["completed_tasks"] = state["completed_tasks"].copy()
            new_state["errors"] = state["errors"].copy()
            
            if preprocessor_result.get("success", False):
                new_state["preprocessed_text"] = preprocessor_result["result"]
                new_state["completed_tasks"].append("文本预处理")
            else:
                new_state["preprocessed_text"] = state["text"]  # 使用原始文本
                new_state["errors"].append(f"文本预处理失败: {preprocessor_result.get('error', '未知错误')}")
                new_state["completed_tasks"].append("文本预处理(使用原始文本)")
            
            return new_state
        except Exception as e:
            # 创建新状态而不是修改现有状态
            new_state = state.copy()
            new_state["completed_tasks"] = state["completed_tasks"].copy()
            new_state["errors"] = state["errors"].copy()
            new_state["preprocessed_text"] = state["text"]  # 使用原始文本
            new_state["errors"].append(f"文本预处理异常: {str(e)}")
            new_state["completed_tasks"].append("文本预处理(使用原始文本)")
            
            return new_state
    
    def _extract_characters(self, state: ParallelExtractionState) -> ParallelExtractionState:
        """提取人物信息"""
        try:
            character_agent = CharacterExtractionAgent()
            character_info = character_agent.process(state["preprocessed_text"])
            
            # 创建新状态而不是修改现有状态
            new_state = state.copy()
            new_state["completed_tasks"] = state["completed_tasks"].copy()
            new_state["errors"] = state["errors"].copy()
            new_state["character_info"] = character_info
            new_state["completed_tasks"].append("人物提取")
            
            return new_state
        except Exception as e:
            # 创建新状态而不是修改现有状态
            new_state = state.copy()
            new_state["completed_tasks"] = state["completed_tasks"].copy()
            new_state["errors"] = state["errors"].copy()
            new_state["character_info"] = {"success": False, "error": str(e)}
            new_state["errors"].append(f"人物提取异常: {str(e)}")
            new_state["completed_tasks"].append("人物提取(失败)")
            
            return new_state
    
    def _analyze_plot(self, state: ParallelExtractionState) -> ParallelExtractionState:
        """分析剧情"""
        try:
            plot_agent = PlotAnalysisAgent()
            plot_info = plot_agent.process(state["preprocessed_text"])
            
            # 创建新状态而不是修改现有状态
            new_state = state.copy()
            new_state["completed_tasks"] = state["completed_tasks"].copy()
            new_state["errors"] = state["errors"].copy()
            new_state["plot_info"] = plot_info
            new_state["completed_tasks"].append("剧情分析")
            
            return new_state
        except Exception as e:
            # 创建新状态而不是修改现有状态
            new_state = state.copy()
            new_state["completed_tasks"] = state["completed_tasks"].copy()
            new_state["errors"] = state["errors"].copy()
            new_state["plot_info"] = {"success": False, "error": str(e)}
            new_state["errors"].append(f"剧情分析异常: {str(e)}")
            new_state["completed_tasks"].append("剧情分析(失败)")
            
            return new_state
    
    def _identify_satisfaction_points(self, state: ParallelExtractionState) -> ParallelExtractionState:
        """识别爽点"""
        try:
            satisfaction_agent = SatisfactionPointAgent()
            satisfaction_info = satisfaction_agent.process(state["preprocessed_text"])
            
            # 创建新状态而不是修改现有状态
            new_state = state.copy()
            new_state["completed_tasks"] = state["completed_tasks"].copy()
            new_state["errors"] = state["errors"].copy()
            new_state["satisfaction_info"] = satisfaction_info
            new_state["completed_tasks"].append("爽点识别")
            
            return new_state
        except Exception as e:
            # 创建新状态而不是修改现有状态
            new_state = state.copy()
            new_state["completed_tasks"] = state["completed_tasks"].copy()
            new_state["errors"] = state["errors"].copy()
            new_state["satisfaction_info"] = {"success": False, "error": str(e)}
            new_state["errors"].append(f"爽点识别异常: {str(e)}")
            new_state["completed_tasks"].append("爽点识别(失败)")
            
            return new_state
    
    def extract_novel_information_parallel(self, novel_text: str) -> Dict[str, Any]:
        """提取小说的综合信息（并行化版本）"""
        # 创建状态图
        workflow = StateGraph(ParallelExtractionState)
        
        # 添加节点
        workflow.add_node("preprocess", self._preprocess_text)
        workflow.add_node("extract_characters", self._extract_characters)
        workflow.add_node("analyze_plot", self._analyze_plot)
        workflow.add_node("identify_satisfaction", self._identify_satisfaction_points)
        
        # 设置边
        workflow.add_edge(START, "preprocess")
        # 预处理完成后，并行执行三个任务
        workflow.add_edge("preprocess", "extract_characters")
        workflow.add_edge("preprocess", "analyze_plot")
        workflow.add_edge("preprocess", "identify_satisfaction")
        # 所有任务完成后，结束
        workflow.add_edge("extract_characters", END)
        workflow.add_edge("analyze_plot", END)
        workflow.add_edge("identify_satisfaction", END)
        
        # 编译图
        app = workflow.compile()
        
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
    
    def extract_novel_information_threadpool(self, novel_text: str) -> Dict[str, Any]:
        """提取小说的综合信息（线程池并行版本）"""
        # 首先进行文本预处理
        text_processor = TextPreprocessorAgent()
        preprocessor_result = text_processor.process(novel_text)
        
        # 获取清洗后的文本
        if preprocessor_result.get("success", False):
            cleaned_text = preprocessor_result["result"]
        else:
            # 如果预处理失败，使用原始文本
            cleaned_text = novel_text
        
        # 使用线程池并行执行三个任务
        with ThreadPoolExecutor(max_workers=3) as executor:
            # 提交任务
            character_future = executor.submit(self._run_character_extraction, cleaned_text)
            plot_future = executor.submit(self._run_plot_analysis, cleaned_text)
            satisfaction_future = executor.submit(self._run_satisfaction_identification, cleaned_text)
            
            # 获取结果
            character_info = character_future.result()
            plot_info = plot_future.result()
            satisfaction_info = satisfaction_future.result()
        
        return {
            "characters": character_info,
            "plot": plot_info,
            "satisfaction_points": satisfaction_info,
            "original_text_length": len(novel_text),
            "cleaned_text_length": len(cleaned_text),
            "parallel_execution": True,
            "parallel_method": "ThreadPoolExecutor"
        }
    
    def _run_character_extraction(self, text: str) -> Dict[str, Any]:
        """运行人物提取"""
        character_agent = CharacterExtractionAgent()
        return character_agent.process(text)
    
    def _run_plot_analysis(self, text: str) -> Dict[str, Any]:
        """运行剧情分析"""
        plot_agent = PlotAnalysisAgent()
        return plot_agent.process(text)
    
    def _run_satisfaction_identification(self, text: str) -> Dict[str, Any]:
        """运行爽点识别"""
        satisfaction_agent = SatisfactionPointAgent()
        return satisfaction_agent.process(text)