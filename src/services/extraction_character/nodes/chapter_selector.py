"""
章节选择节点
"""

import os
from typing import Dict, Any, List
from state import CharacterExtractionState


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
            
            # 获取已处理的章节
            processed_chapters = state.get("processed_chapters", [])
            
            # 找出未处理的章节
            unprocessed_chapters = [
                chapter for chapter in all_chapters 
                if chapter not in processed_chapters
            ]
            
            if not unprocessed_chapters:
                # 所有章节都已处理
                state["is_completed"] = True
                state["current_chapter"] = ""
            else:
                # 选择下一个章节（按文件名排序）
                next_chapter = sorted(unprocessed_chapters)[0]
                state["current_chapter"] = next_chapter
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
            
            # 按文件名排序
            chapters.sort()
            
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