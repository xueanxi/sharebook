"""
单章节角色提取工作流
每个章节使用独立的LangGraph工作流处理
"""

from typing import Dict, Any
from langgraph.graph import StateGraph, END

from state import CharacterExtractionState
from config_manager import ConfigManager
from nodes.file_reader import FileReader
from nodes.character_extractor import CharacterExtractor
from nodes.parallel_analyzer import ParallelCharacterAnalyzer
from nodes.parallel_csv_updater import ParallelCSVUpdater


class SingleChapterWorkflow:
    """单章节角色提取工作流"""
    
    def __init__(self, config_path: str, chapter_name: str):
        """
        初始化单章节工作流
        
        Args:
            config_path: 配置文件路径
            chapter_name: 章节名称
        """
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_config()
        self.chapter_name = chapter_name
        
        # 初始化各个节点
        self.file_reader = FileReader(self.config_manager.get_novel_path())
        self.character_extractor = CharacterExtractor(
            self.config_manager.get_llm_config()['config_path'],
            self.config_manager.config_path
        )
        self.parallel_analyzer = ParallelCharacterAnalyzer(
            self.config_manager.get_llm_config()['config_path'],
            self.config_manager.config_path,
            self.config_manager.get_max_analyzer_agents()
        )
        self.parallel_csv_updater = ParallelCSVUpdater(
            self.config_manager.get_csv_path(),
            self.config_manager.get_llm_config()['config_path'],
            self.config_manager.config_path,
            self.config_manager.get_max_csv_agents()
        )
        
        # 构建工作流图
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """
        构建单章节工作流图
        
        Returns:
            工作流图
        """
        # 创建工作流图
        workflow = StateGraph(CharacterExtractionState)
        
        # 添加节点
        workflow.add_node("read_chapter", self._read_chapter_node)
        workflow.add_node("extract_characters", self._extract_characters_node)
        workflow.add_node("analyze_characters", self._analyze_characters_node)
        workflow.add_node("update_csv", self._update_csv_node)
        
        # 设置入口点
        workflow.set_entry_point("read_chapter")
        
        # 添加边（线性流程，无循环）
        workflow.add_edge("read_chapter", "extract_characters")
        workflow.add_edge("extract_characters", "analyze_characters")
        workflow.add_edge("analyze_characters", "update_csv")
        workflow.add_edge("update_csv", END)
        
        return workflow.compile()
    
    def _read_chapter_node(self, state: CharacterExtractionState) -> CharacterExtractionState:
        """文件读取节点"""
        # 设置当前章节
        state["current_chapter"] = self.chapter_name
        
        # 读取章节内容
        state = self.file_reader.read_chapter(state)
        
        # 验证章节内容
        if not self.file_reader.validate_chapter_content(state):
            state["error"] = "章节内容验证失败"
        
        return state
    
    def _extract_characters_node(self, state: CharacterExtractionState) -> CharacterExtractionState:
        """角色提取节点"""
        # 提取角色
        state = self.character_extractor.extract_characters(state)
        
        # 验证提取结果
        if self.character_extractor.validate_extracted_characters(state):
            # 预处理角色信息
            state = self.character_extractor.preprocess_characters(state)
        else:
            state["error"] = "角色提取结果验证失败"
        
        return state
    
    def _analyze_characters_node(self, state: CharacterExtractionState) -> CharacterExtractionState:
        """并行角色分析节点"""
        state = self.parallel_analyzer.analyze_characters_parallel(state)
        
        # 验证分析结果
        if not self.parallel_analyzer.validate_analyzed_characters(state):
            state["error"] = "角色分析结果验证失败"
        
        return state
    
    def _update_csv_node(self, state: CharacterExtractionState) -> CharacterExtractionState:
        """并行CSV更新节点"""
        state = self.parallel_csv_updater.update_csv_parallel(state)
        
        # 验证更新结果
        if not self.parallel_csv_updater.validate_csv_update(state):
            state["error"] = "CSV更新结果验证失败"
        
        return state
    
    def run(self) -> Dict[str, Any]:
        """
        运行单章节工作流
        
        Returns:
            处理结果
        """
        try:
            # 初始化状态
            initial_state = self._initialize_state()
            
            # 运行工作流
            result = self.workflow.invoke(initial_state)
            
            # 输出结果
            if result.get("error"):
                return {"success": False, "error": result["error"]}
            else:
                return {
                    "success": True,
                    "chapter": self.chapter_name,
                    "extracted_characters": result.get("extracted_characters", []),
                    "analyzed_characters": result.get("all_characters", {})
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _initialize_state(self) -> CharacterExtractionState:
        """
        初始化单章节状态
        
        Returns:
            初始状态
        """
        return {
            "current_chapter": self.chapter_name,
            "chapter_content": "",
            "extracted_characters": [],
            "all_characters": {},
            "processed_chapters": [],  # 单章节工作流不需要这个
            "csv_path": self.config_manager.get_csv_path(),
            "error": None,
            "config_path": self.config_manager.config_path,
            "character_aliases": {},
            "is_completed": False
        }