"""
进度检查节点
"""

from typing import Dict, Any, List
from state import CharacterExtractionState


class ProgressChecker:
    """进度检查节点"""
    
    def __init__(self, novel_path: str):
        """
        初始化进度检查节点
        
        Args:
            novel_path: 小说文件目录路径
        """
        self.novel_path = novel_path
    
    def check_progress(self, state: CharacterExtractionState) -> CharacterExtractionState:
        """
        检查处理进度
        
        Args:
            state: 当前状态
            
        Returns:
            更新后的状态
        """
        try:
            # 获取所有章节
            all_chapters = self._get_all_chapters()
            
            if not all_chapters:
                state["error"] = "没有找到章节文件"
                state["is_completed"] = True
                return state
            
            # 获取已处理的章节
            processed_chapters = state.get("processed_chapters", [])
            
            # 检查是否所有章节都已处理
            unprocessed_chapters = [
                chapter for chapter in all_chapters 
                if chapter not in processed_chapters
            ]
            
            if not unprocessed_chapters:
                # 所有章节都已处理
                state["is_completed"] = True
                state["current_chapter"] = ""
            else:
                # 还有未处理的章节
                state["is_completed"] = False
            
            # 更新处理进度
            total_chapters = len(all_chapters)
            processed_count = len(processed_chapters)
            progress_percentage = (processed_count / total_chapters) * 100 if total_chapters > 0 else 0
            
            print(f"处理进度: {processed_count}/{total_chapters} ({progress_percentage:.1f}%)")
            
            # 清除错误信息
            state["error"] = None
            
            return state
        except Exception as e:
            state["error"] = f"进度检查失败: {str(e)}"
            state["is_completed"] = True
            return state
    
    def _get_all_chapters(self) -> List[str]:
        """
        获取所有章节文件列表
        
        Returns:
            章节文件名列表
        """
        try:
            import os
            
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
    
    def should_continue(self, state: CharacterExtractionState) -> bool:
        """
        判断是否应该继续处理
        
        Args:
            state: 当前状态
            
        Returns:
            是否应该继续
        """
        # 检查是否有错误
        if state.get("error"):
            return False
        
        # 检查是否已完成
        if state.get("is_completed", False):
            return False
        
        # 检查是否有当前章节
        if not state.get("current_chapter"):
            return False
        
        return True
    
    def update_processed_chapters(self, state: CharacterExtractionState) -> CharacterExtractionState:
        """
        更新已处理章节列表
        
        Args:
            state: 当前状态
            
        Returns:
            更新后的状态
        """
        try:
            current_chapter = state.get("current_chapter", "")
            processed_chapters = state.get("processed_chapters", [])
            
            # 如果当前章节不在已处理列表中，添加它
            if current_chapter and current_chapter not in processed_chapters:
                processed_chapters.append(current_chapter)
                state["processed_chapters"] = processed_chapters
                print(f"章节处理完成: {current_chapter}")
            
            return state
        except Exception as e:
            state["error"] = f"更新已处理章节失败: {str(e)}"
            return state