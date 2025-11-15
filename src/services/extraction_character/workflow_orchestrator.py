"""
角色提取工作流编排器
实现外部大循环遍历章节，每个章节使用独立的工作流处理
"""

from typing import Dict, Any, List
from state import CharacterExtractionState
from config_manager import ConfigManager
from nodes.chapter_selector import ChapterSelector
from nodes.progress_checker import ProgressChecker
from utils.backup_utils import BackupUtils


class CharacterExtractionOrchestrator:
    """角色提取工作流编排器"""
    
    def __init__(self, config_path: str):
        """
        初始化编排器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_config()
        
        # 初始化章节选择器和进度检查器
        self.chapter_selector = ChapterSelector(self.config_manager.get_novel_path())
        self.progress_checker = ProgressChecker(self.config_manager.get_novel_path())
    
    def run(self, reset_progress: bool = False) -> Dict[str, Any]:
        """
        运行编排器
        
        Args:
            reset_progress: 是否重置进度
            
        Returns:
            处理结果
        """
        try:
            # 初始化状态
            state = self._initialize_state(reset_progress)
            
            # 获取所有章节
            all_chapters = self.chapter_selector._get_all_chapters()
            total_chapters = len(all_chapters)
            
            if total_chapters == 0:
                return {"success": False, "error": "没有找到章节文件"}
            
            print(f"开始角色提取，共 {total_chapters} 个章节...")
            
            # 外部大循环遍历章节
            for i, chapter in enumerate(all_chapters, 1):
                # 检查是否已处理
                if chapter in state.get("processed_chapters", []):
                    print(f"章节 {chapter} 已处理，跳过")
                    continue
                
                print(f"处理章节 {i}/{total_chapters}: {chapter}")
                
                # 创建单章节工作流并运行
                chapter_result = self._process_single_chapter(chapter)
                
                if chapter_result["success"]:
                    # 更新已处理章节
                    state["processed_chapters"].append(chapter)
                    
                    # 保存进度
                    self.config_manager.update_progress(chapter, state["processed_chapters"])
                    
                    print(f"章节 {chapter} 处理完成")
                else:
                    print(f"章节 {chapter} 处理失败: {chapter_result.get('error', '未知错误')}")
                    # 可以选择继续或中断
                    # 这里选择继续处理下一章节
                    continue
            
            # 输出结果
            processed_count = len(state.get("processed_chapters", []))
            print(f"角色提取完成，共处理 {processed_count} 个章节")
            
            return {
                "success": True,
                "processed_chapters": state.get("processed_chapters", []),
                "csv_path": self.config_manager.get_csv_path()
            }
            
        except Exception as e:
            print(f"编排器执行异常: {e}")
            return {"success": False, "error": str(e)}
    
    def _process_single_chapter(self, chapter_name: str) -> Dict[str, Any]:
        """
        处理单个章节
        
        Args:
            chapter_name: 章节名称
            
        Returns:
            处理结果
        """
        try:
            # 创建单章节工作流
            from single_chapter_workflow import SingleChapterWorkflow
            workflow = SingleChapterWorkflow(
                self.config_manager.config_path,
                chapter_name
            )
            
            # 运行工作流
            return workflow.run()
            
        except Exception as e:
            print(f"单章节处理异常: {e}")
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