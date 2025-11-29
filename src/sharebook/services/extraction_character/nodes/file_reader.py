"""
文件读取节点
"""

import os
from typing import Dict, Any
from state import CharacterExtractionState


class FileReader:
    """文件读取节点"""
    
    def __init__(self, novel_path: str):
        """
        初始化文件读取节点
        
        Args:
            novel_path: 小说文件目录路径
        """
        self.novel_path = novel_path
    
    def read_chapter(self, state: CharacterExtractionState) -> CharacterExtractionState:
        """
        读取当前章节内容
        
        Args:
            state: 当前状态
            
        Returns:
            更新后的状态
        """
        try:
            current_chapter = state.get("current_chapter", "")
            
            if not current_chapter:
                state["error"] = "没有指定当前章节"
                return state
            
            # 构建文件完整路径
            file_path = os.path.join(self.novel_path, current_chapter)
            
            if not os.path.exists(file_path):
                state["error"] = f"章节文件不存在: {file_path}"
                return state
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                chapter_content = f.read()
            
            # 更新状态
            state["chapter_content"] = chapter_content
            state["error"] = None
            
            return state
        except Exception as e:
            state["error"] = f"读取章节失败: {str(e)}"
            return state
    
    def validate_chapter_content(self, state: CharacterExtractionState) -> bool:
        """
        验证章节内容是否有效
        
        Args:
            state: 当前状态
            
        Returns:
            内容是否有效
        """
        chapter_content = state.get("chapter_content", "")
        
        # 检查内容是否为空
        if not chapter_content.strip():
            return False
        
        # 检查内容长度（至少10个字符）
        if len(chapter_content.strip()) < 10:
            return False
        
        return True