"""
章节选择节点
"""

import os
import sys
from typing import Dict, Any, List
from state import CharacterExtractionState

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))
from src.utils.text_processing import ChapterSorter


class ChapterSelector:
    """章节选择节点"""
    
    def __init__(self, novel_path: str):
        """
        初始化章节选择节点
        
        Args:
            novel_path: 小说文件目录路径
        """
        self.novel_path = novel_path
    
    def select_next_chapter(self, state: CharacterExtractionState) -> CharacterExtractionState:
        """
        选择下一个未处理的章节
        
        Args:
            state: 当前状态
            
        Returns:
            更新后的状态
        """
        try:
            # 获取所有章节文件
            all_chapters = self._get_all_chapters()
            
            if not all_chapters:
                state["error"] = "没有找到章节文件"
                state["is_completed"] = True
                return state
            
            # 直接返回第一个章节
            state["current_chapter"] = all_chapters[0]
            state["is_completed"] = False
            
            # 清除错误信息
            state["error"] = None
            
            return state
        except Exception as e:
            state["error"] = f"章节选择失败: {str(e)}"
            state["is_completed"] = True
            return state
    
    def _get_all_chapters(self) -> List[str]:
        """
        获取所有章节文件列表
        
        Returns:
            章节文件名列表
        """
        try:
            if not os.path.exists(self.novel_path):
                print(f"小说目录不存在: {self.novel_path}")
                return []
            
            # 获取目录中的所有.txt文件
            chapters = []
            for file_name in os.listdir(self.novel_path):
                if file_name.endswith('.txt'):
                    chapters.append(file_name)
            
            # 按章节号排序
            chapters = ChapterSorter.sort_chapter_files(chapters)
            
            return chapters
        except Exception as e:
            print(f"获取章节列表失败: {e}")
            return []
    
    def reset_progress(self, state: CharacterExtractionState) -> CharacterExtractionState:
        """
        重置处理进度
        
        Args:
            state: 当前状态
            
        Returns:
            重置后的状态
        """
        state["processed_chapters"] = []
        state["current_chapter"] = ""
        state["is_completed"] = False
        state["error"] = None
        
        return state