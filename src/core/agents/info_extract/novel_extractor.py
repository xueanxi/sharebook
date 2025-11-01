"""
小说信息提取器，使用LangGraph实现并行处理
"""

from typing import Dict, Any
from langgraph.graph import StateGraph, START, END

from .base import ParallelExtractionState
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
    
    def _preprocess_text(self, state: ParallelExtractionState) -> Dict[str, Any]:
        """预处理文本节点"""
        # 调用文本预处理器
        preprocessed_text = ""
        completed_tasks = []
        errors = []
        
        try:
            # 使用LCEL链处理文本
            result = self.text_preprocessor.chain.invoke({"text": state["text"]})
            preprocessed_text = result
            completed_tasks.append("文本预处理")
        except Exception as e:
            # 如果LLM处理失败，使用简单的文本清洗作为备用方案
            cleaned_text = self.text_preprocessor._simple_text_cleaning(state["text"])
            preprocessed_text = cleaned_text
            errors.append(f"文本预处理异常: {str(e)}")
            completed_tasks.append("文本预处理(失败)")
        
        # 返回状态更新
        return {
            "preprocessed_text": preprocessed_text,
            "completed_tasks": completed_tasks,
            "errors": errors,
            "preprocess_done": True
        }
    
    def _extract_character_info(self, state: ParallelExtractionState) -> Dict[str, Any]:
        """提取人物信息节点"""
        # 确保预处理已完成
        if not state.get("preprocess_done", False):
            return {
                "errors": ["人物提取: 预处理未完成"],
                "completed_tasks": ["人物提取(失败)"],
                "character_done": True
            }
        
        # 调用人物提取器
        character_info = {}
        completed_tasks = []
        errors = []
        
        try:
            # 使用LCEL链处理文本
            result = self.character_extractor.chain.invoke({"text": state["preprocessed_text"]})
            
            # 更新character_info
            character_info = {
                "success": True,
                "result": result,
                "agent": "人物提取器"
            }
            completed_tasks.append("人物提取")
        except Exception as e:
            character_info = {
                "success": False,
                "error": str(e),
                "agent": "人物提取器"
            }
            errors.append(f"人物提取异常: {str(e)}")
            completed_tasks.append("人物提取(失败)")
        
        # 返回状态更新
        return {
            "character_info": character_info,
            "completed_tasks": completed_tasks,
            "errors": errors,
            "character_done": True
        }
    
    def _analyze_plot(self, state: ParallelExtractionState) -> Dict[str, Any]:
        """分析剧情节点"""
        # 确保预处理已完成
        if not state.get("preprocess_done", False):
            return {
                "errors": ["剧情分析: 预处理未完成"],
                "completed_tasks": ["剧情分析(失败)"],
                "plot_done": True
            }
        
        # 调用剧情分析器
        plot_info = {}
        completed_tasks = []
        errors = []
        
        try:
            # 使用LCEL链处理文本
            result = self.plot_analyzer.chain.invoke({"text": state["preprocessed_text"]})
            
            # 更新plot_info
            plot_info = {
                "success": True,
                "result": result,
                "agent": "剧情分析器"
            }
            completed_tasks.append("剧情分析")
        except Exception as e:
            plot_info = {
                "success": False,
                "error": str(e),
                "agent": "剧情分析器"
            }
            errors.append(f"剧情分析异常: {str(e)}")
            completed_tasks.append("剧情分析(失败)")
        
        # 返回状态更新
        return {
            "plot_info": plot_info,
            "completed_tasks": completed_tasks,
            "errors": errors,
            "plot_done": True
        }
    
    def _identify_satisfaction_points(self, state: ParallelExtractionState) -> Dict[str, Any]:
        """识别爽点节点"""
        # 确保预处理已完成
        if not state.get("preprocess_done", False):
            return {
                "errors": ["爽点识别: 预处理未完成"],
                "completed_tasks": ["爽点识别(失败)"],
                "satisfaction_done": True
            }
        
        # 调用爽点识别器
        satisfaction_info = {}
        completed_tasks = []
        errors = []
        
        try:
            # 使用LCEL链处理文本
            result = self.satisfaction_identifier.chain.invoke({"text": state["preprocessed_text"]})
            
            # 更新satisfaction_info
            satisfaction_info = {
                "success": True,
                "result": result,
                "agent": "爽点识别器"
            }
            completed_tasks.append("爽点识别")
        except Exception as e:
            satisfaction_info = {
                "success": False,
                "error": str(e),
                "agent": "爽点识别器"
            }
            errors.append(f"爽点识别异常: {str(e)}")
            completed_tasks.append("爽点识别(失败)")
        
        # 返回状态更新
        return {
            "satisfaction_info": satisfaction_info,
            "completed_tasks": completed_tasks,
            "errors": errors,
            "satisfaction_done": True
        }
    
    def _merge_results(self, state: ParallelExtractionState) -> Dict[str, Any]:
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
    
    def _should_merge(self, state: ParallelExtractionState) -> str:
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