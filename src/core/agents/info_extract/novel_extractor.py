"""
小说信息提取器，使用LangGraph实现并行处理
"""

from typing import Dict, Any
from langgraph.graph import StateGraph, START, END

from .base import NovelExtractionState
from .text_preprocessor import TextPreprocessor
from .character_extractor import CharacterExtractor
from .plot_analyzer import PlotAnalyzer
from .satisfaction_identifier import SatisfactionPointIdentifier


class NovelInformationExtractor:
    """小说信息提取器，使用LangGraph实现并行处理"""
    
    def __init__(self, model_name=None, temperature=0.7):
        # 初始化各个处理器
        self.text_preprocessor = TextPreprocessor(model_name, temperature)
        self.character_extractor = CharacterExtractor(model_name, temperature)
        self.plot_analyzer = PlotAnalyzer(model_name, temperature)
        self.satisfaction_identifier = SatisfactionPointIdentifier(model_name, temperature)
        
        # 构建并行处理图
        self.parallel_app = self._build_parallel_graph()
    
    def _preprocess_text(self, state: NovelExtractionState) -> Dict[str, Any]:
        """预处理文本节点"""
        # 调用文本预处理器的process方法
        self.text_preprocessor.process(state)
        
        # 返回状态更新，确保包含所有必要的字段
        return {
            "preprocess_done": True,
            "preprocessed_text": state.get("preprocessed_text", ""),
            "completed_tasks": state.get("completed_tasks", []),
            "errors": state.get("errors", [])
        }
    
    def _extract_character_info(self, state: NovelExtractionState) -> Dict[str, Any]:
        """提取人物信息节点"""
        # 调用人物提取器的process方法
        self.character_extractor.process(state)
        
        # 返回状态更新，确保包含所有必要的字段
        return {
            "character_done": True,
            "character_info": state.get("character_info", {}),
            "completed_tasks": state.get("completed_tasks", []),
            "errors": state.get("errors", [])
        }
    
    def _analyze_plot(self, state: NovelExtractionState) -> Dict[str, Any]:
        """分析剧情节点"""
        # 调用剧情分析器的process方法
        self.plot_analyzer.process(state)
        
        # 返回状态更新，确保包含所有必要的字段
        return {
            "plot_done": True,
            "plot_info": state.get("plot_info", {}),
            "completed_tasks": state.get("completed_tasks", []),
            "errors": state.get("errors", [])
        }
    
    def _identify_satisfaction_points(self, state: NovelExtractionState) -> Dict[str, Any]:
        """识别爽点节点"""
        # 调用爽点识别器的process方法
        self.satisfaction_identifier.process(state)
        
        # 返回状态更新，确保包含所有必要的字段
        return {
            "satisfaction_done": True,
            "satisfaction_info": state.get("satisfaction_info", {}),
            "completed_tasks": state.get("completed_tasks", []),
            "errors": state.get("errors", [])
        }
    
    def _merge_results(self, state: NovelExtractionState) -> Dict[str, Any]:
        """合并所有提取结果"""
        # 记录任务完成状态
        completed_tasks = ["结果合并"]
        
        # 添加调试信息
        print(f"合并结果时，preprocessed_text长度: {len(state['preprocessed_text'])}")
        print(f"人物信息: {state['character_info']}")
        print(f"剧情信息: {state['plot_info']}")
        print(f"爽点信息: {state['satisfaction_info']}")
        
        # 返回状态更新
        return {
            "completed_tasks": completed_tasks
        }
    
    def _should_merge(self, state: NovelExtractionState) -> str:
        """判断是否所有并行任务都已完成，可以进行合并"""
        if (state.get("preprocess_done", False) and 
            state.get("character_done", False) and 
            state.get("plot_done", False) and 
            state.get("satisfaction_done", False)):
            return "merge_results"
        else:
            return "continue"
    
    def _build_parallel_graph(self) -> StateGraph:
        """构建并行处理的状态图"""
        # 创建状态图
        workflow = StateGraph(NovelExtractionState)
        
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
        
        # 添加条件边：所有提取任务完成后合并结果
        workflow.add_conditional_edges(
            "extract_character",
            self._should_merge,
            {
                "merge_results": "merge_results",
                "continue": END
            }
        )
        
        workflow.add_conditional_edges(
            "analyze_plot",
            self._should_merge,
            {
                "merge_results": "merge_results",
                "continue": END
            }
        )
        
        workflow.add_conditional_edges(
            "identify_satisfaction",
            self._should_merge,
            {
                "merge_results": "merge_results",
                "continue": END
            }
        )
        
        # 设置结束点
        workflow.set_finish_point("merge_results")
        
        # 编译并返回工作流
        return workflow.compile()
    
    def extract_novel_information_parallel(self, novel_text: str) -> Dict[str, Any]:
        """提取小说的综合信息（并行化版本）
        
        Args:
            novel_text: 小说文本
            
        Returns:
            提取结果
        """
        # 初始状态
        initial_state = {
            "text": novel_text,
            "preprocessed_text": "",
            "character_info": {},
            "plot_info": {},
            "satisfaction_info": {},
            "errors": [],
            "completed_tasks": [],
            "preprocess_done": False,
            "character_done": False,
            "plot_done": False,
            "satisfaction_done": False
        }
        
        # 执行工作流
        result = self.parallel_app.invoke(initial_state)
        
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