"""
角色提取工作流编排（简化版，不依赖LangGraph）
"""

from typing import Dict, Any, List
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
            state = self._initialize_state(reset_progress)
            
            # 运行工作流
            print("开始角色提取工作流...")
            
            while True:
                # 章节选择
                state = self.chapter_selector.select_next_chapter(state)
                if not self._should_continue_processing(state):
                    break
                
                # 文件读取
                state = self.file_reader.read_chapter(state)
                if not self._should_continue_processing(state):
                    break
                
                # 角色提取
                state = self.character_extractor.extract_characters(state)
                if not self._should_continue_processing(state):
                    break
                
                # 验证提取结果
                if self.character_extractor.validate_extracted_characters(state):
                    # 预处理角色信息
                    state = self.character_extractor.preprocess_characters(state)
                else:
                    state["error"] = "角色提取结果验证失败"
                    break
                
                # 并行角色分析
                state = self.parallel_analyzer.analyze_characters_parallel(state)
                if not self._should_continue_processing(state):
                    break
                
                # 验证分析结果
                if not self.parallel_analyzer.validate_analyzed_characters(state):
                    state["error"] = "角色分析结果验证失败"
                    break
                
                # 并行CSV更新
                state = self.parallel_csv_updater.update_csv_parallel(state)
                if not self._should_continue_processing(state):
                    break
                
                # 验证更新结果
                if not self.parallel_csv_updater.validate_csv_update(state):
                    state["error"] = "CSV更新结果验证失败"
                    break
                
                # 更新已处理章节
                state = self.progress_checker.update_processed_chapters(state)
                
                # 检查进度
                state = self.progress_checker.check_progress(state)
                
                # 更新配置文件
                if not state.get("error"):
                    current_chapter = state.get("current_chapter", "")
                    processed_chapters = state.get("processed_chapters", [])
                    self.config_manager.update_progress(current_chapter, processed_chapters)
                
                # 检查是否应该继续
                if not self._should_continue_processing(state):
                    break
            
            # 输出结果
            if state.get("error"):
                print(f"工作流执行失败: {state['error']}")
                return {"success": False, "error": state["error"]}
            else:
                processed_count = len(state.get("processed_chapters", []))
                print(f"工作流执行成功，共处理 {processed_count} 个章节")
                return {
                    "success": True,
                    "processed_chapters": state.get("processed_chapters", []),
                    "csv_path": self.config_manager.get_csv_path()
                }
        except Exception as e:
            print(f"工作流执行异常: {e}")
            return {"success": False, "error": str(e)}
    
    def _should_continue_processing(self, state: CharacterExtractionState) -> bool:
        """
        判断是否应该继续处理
        
        Args:
            state: 当前状态
            
        Returns:
            是否应该继续
        """
        # 检查是否有错误
        if state.get("error"):
            print(f"处理出错: {state['error']}")
            return False
        
        # 检查是否已完成
        if state.get("is_completed", False):
            print("所有章节处理完成")
            return False
        
        # 检查是否有当前章节
        if not state.get("current_chapter"):
            print("没有更多章节需要处理")
            return False
        
        return True
    
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