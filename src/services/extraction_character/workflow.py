"""
角色提取工作流编排
"""

from typing import Dict, Any, Callable
from langgraph.graph import StateGraph, END

# 使用绝对导入而不是相对导入
try:
    from .state import CharacterExtractionState
    from .config_manager import ConfigManager
    from .nodes.chapter_selector import ChapterSelector
    from .nodes.file_reader import FileReader
    from .nodes.character_extractor import CharacterExtractor
    from .nodes.parallel_analyzer import ParallelCharacterAnalyzer
    from .nodes.parallel_csv_updater import ParallelCSVUpdater
    from .nodes.progress_checker import ProgressChecker
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    from state import CharacterExtractionState
    from config_manager import ConfigManager
    from nodes.chapter_selector import ChapterSelector
    from nodes.file_reader import FileReader
    from nodes.character_extractor import CharacterExtractor
    from nodes.parallel_analyzer import ParallelCharacterAnalyzer
    from nodes.parallel_csv_updater import ParallelCSVUpdater
    from nodes.progress_checker import ProgressChecker


class CharacterExtractionWorkflow:
    """角色提取工作流"""
    
    def __init__(self, config_path: str):
        """
        初始化工作流
        
        Args:
            config_path: 配置文件路径
        """
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_config()
        
        # 初始化各个节点
        self.chapter_selector = ChapterSelector(self.config_manager.get_novel_path())
        self.file_reader = FileReader(self.config_manager.get_novel_path())
        self.character_extractor = CharacterExtractor(self.config_manager.get_llm_config()['config_path'])
        self.parallel_analyzer = ParallelCharacterAnalyzer(
            self.config_manager.get_llm_config()['config_path'],
            self.config_manager.get_max_analyzer_agents()
        )
        self.parallel_csv_updater = ParallelCSVUpdater(
            self.config_manager.get_csv_path(),
            self.config_manager.get_llm_config()['config_path'],
            self.config_manager.get_max_csv_agents()
        )
        self.progress_checker = ProgressChecker(self.config_manager.get_novel_path())
        
        # 构建工作流图
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """
        构建工作流图
        
        Returns:
            工作流图
        """
        # 创建工作流图
        workflow = StateGraph(CharacterExtractionState)
        
        # 添加节点
        workflow.add_node("select_chapter", self._select_chapter_node)
        workflow.add_node("read_chapter", self._read_chapter_node)
        workflow.add_node("extract_characters", self._extract_characters_node)
        workflow.add_node("analyze_characters", self._analyze_characters_node)
        workflow.add_node("update_csv", self._update_csv_node)
        workflow.add_node("check_progress", self._check_progress_node)
        
        # 设置入口点
        workflow.set_entry_point("select_chapter")
        
        # 添加边
        workflow.add_edge("select_chapter", "read_chapter")
        workflow.add_edge("read_chapter", "extract_characters")
        workflow.add_edge("extract_characters", "analyze_characters")
        workflow.add_edge("analyze_characters", "update_csv")
        workflow.add_edge("update_csv", "check_progress")
        
        # 添加条件边
        workflow.add_conditional_edges(
            "select_chapter",
            self._should_continue_processing,
            {
                "continue": "read_chapter",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "check_progress",
            self._should_continue_processing,
            {
                "continue": "select_chapter",
                "end": END
            }
        )
        
        return workflow.compile()
    
    def _select_chapter_node(self, state: CharacterExtractionState) -> CharacterExtractionState:
        """章节选择节点"""
        return self.chapter_selector.select_next_chapter(state)
    
    def _read_chapter_node(self, state: CharacterExtractionState) -> CharacterExtractionState:
        """文件读取节点"""
        return self.file_reader.read_chapter(state)
    
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
    
    def _check_progress_node(self, state: CharacterExtractionState) -> CharacterExtractionState:
        """进度检查节点"""
        # 更新已处理章节
        state = self.progress_checker.update_processed_chapters(state)
        
        # 检查进度
        state = self.progress_checker.check_progress(state)
        
        # 更新配置文件
        if not state.get("error"):
            current_chapter = state.get("current_chapter", "")
            processed_chapters = state.get("processed_chapters", [])
            self.config_manager.update_progress(current_chapter, processed_chapters)
        
        return state
    
    def _should_continue_processing(self, state: CharacterExtractionState) -> str:
        """
        判断是否应该继续处理
        
        Args:
            state: 当前状态
            
        Returns:
            "continue" 或 "end"
        """
        # 检查是否有错误
        if state.get("error"):
            print(f"处理出错: {state['error']}")
            return "end"
        
        # 检查是否已完成
        if state.get("is_completed", False):
            print("所有章节处理完成")
            return "end"
        
        # 检查是否有当前章节
        if not state.get("current_chapter"):
            print("没有更多章节需要处理")
            return "end"
        
        return "continue"
    
    def run(self, reset_progress: bool = False) -> Dict[str, Any]:
        """
        运行工作流
        
        Args:
            reset_progress: 是否重置进度
            
        Returns:
            处理结果
        """
        try:
            # 初始化状态
            initial_state = self._initialize_state(reset_progress)
            
            # 运行工作流
            print("开始角色提取工作流...")
            result = self.workflow.invoke(initial_state)
            
            # 输出结果
            if result.get("error"):
                print(f"工作流执行失败: {result['error']}")
                return {"success": False, "error": result["error"]}
            else:
                processed_count = len(result.get("processed_chapters", []))
                print(f"工作流执行成功，共处理 {processed_count} 个章节")
                return {
                    "success": True,
                    "processed_chapters": result.get("processed_chapters", []),
                    "csv_path": self.config_manager.get_csv_path()
                }
        except Exception as e:
            print(f"工作流执行异常: {e}")
            return {"success": False, "error": str(e)}
    
    def _initialize_state(self, reset_progress: bool) -> CharacterExtractionState:
        """
        初始化状态
        
        Args:
            reset_progress: 是否重置进度
            
        Returns:
            初始状态
        """
        if reset_progress:
            # 重置进度
            self.config_manager.reset_progress()
            processed_chapters = []
        else:
            # 从配置文件读取进度
            processed_chapters = self.config_manager.get_processed_chapters()
        
        return {
            "current_chapter": "",
            "chapter_content": "",
            "extracted_characters": [],
            "all_characters": {},
            "processed_chapters": processed_chapters,
            "csv_path": self.config_manager.get_csv_path(),
            "error": None,
            "config_path": self.config_manager.config_path,
            "character_aliases": {},
            "is_completed": False
        }
    
    def get_progress(self) -> Dict[str, Any]:
        """
        获取当前进度
        
        Returns:
            进度信息
        """
        try:
            # 获取所有章节
            all_chapters = self.chapter_selector._get_all_chapters()
            total_chapters = len(all_chapters)
            
            # 获取已处理章节
            processed_chapters = self.config_manager.get_processed_chapters()
            processed_count = len(processed_chapters)
            
            # 计算进度百分比
            progress_percentage = (processed_count / total_chapters) * 100 if total_chapters > 0 else 0
            
            return {
                "total_chapters": total_chapters,
                "processed_chapters": processed_count,
                "progress_percentage": progress_percentage,
                "current_chapter": self.config_manager.get_current_chapter(),
                "processed_chapters_list": processed_chapters
            }
        except Exception as e:
            print(f"获取进度失败: {e}")
            return {
                "total_chapters": 0,
                "processed_chapters": 0,
                "progress_percentage": 0,
                "current_chapter": "",
                "processed_chapters_list": []
            }