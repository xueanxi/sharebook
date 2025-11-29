"""
章节排序器模块
"""

from typing import List, Dict, Any
import re

class ChapterSorter:
    """章节排序器"""
    
    def __init__(self):
        """初始化章节排序器"""
        pass
    
    def sort_chapters(self, chapters: List[str]) -> List[str]:
        """
        对章节进行排序
        
        Args:
            chapters: 章节文件名列表
            
        Returns:
            排序后的章节列表
        """
        def extract_chapter_number(filename: str) -> int:
            """从文件名中提取章节号"""
            # 匹配各种章节编号格式
            patterns = [
                r'第(\d+)章',  # 第X章
                r'(\d+)章',   # X章
                r'chapter(\d+)',  # chapterX
                r'ch(\d+)',   # chX
                r'^(\d+)',    # 开头数字
            ]
            
            for pattern in patterns:
                match = re.search(pattern, filename, re.IGNORECASE)
                if match:
                    return int(match.group(1))
            
            # 如果没有找到数字，返回一个大数字，排在最后
            return 999999
        
        try:
            return sorted(chapters, key=extract_chapter_number)
        except Exception:
            # 如果排序失败，返回原列表
            return chapters
    
    def get_chapter_info(self, filename: str) -> Dict[str, Any]:
        """
        获取章节信息
        
        Args:
            filename: 章节文件名
            
        Returns:
            章节信息字典
        """
        return {
            'filename': filename,
            'title': filename.replace('.txt', ''),
            'number': self._extract_number(filename)
        }
    
    def _extract_number(self, filename: str) -> int:
        """提取章节号"""
        patterns = [
            r'第(\d+)章',
            r'(\d+)章',
            r'chapter(\d+)',
            r'ch(\d+)',
            r'^(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return 0