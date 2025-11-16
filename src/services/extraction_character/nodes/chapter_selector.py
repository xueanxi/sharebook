"""
章节选择节点
"""

import os
import re
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
            chapters.sort(key=self._extract_chapter_number)
            
            return chapters
        except Exception as e:
            print(f"获取章节列表失败: {e}")
            return []
    
    def _extract_chapter_number(self, filename: str) -> int:
        """
        从文件名中提取章节号
        
        Args:
            filename: 文件名
            
        Returns:
            章节号，如果无法提取则返回一个大数字
        """
        try:
            # 使用正则表达式匹配章节号
            # 匹配模式：第X章、第X章、第X章等
            match = re.search(r'第([一二三四五六七八九十百千万\d]+)章', filename)
            if match:
                chapter_str = match.group(1)
                # 将中文数字转换为阿拉伯数字
                return self._chinese_number_to_int(chapter_str)
            else:
                # 如果没有匹配到章节号，尝试匹配纯数字
                match = re.search(r'(\d+)', filename)
                if match:
                    return int(match.group(1))
                else:
                    # 如果都匹配不到，返回一个大数字，确保这些文件排在最后
                    return 999999
        except Exception:
            # 出错时返回大数字
            return 999999
    
    def _chinese_number_to_int(self, chinese_num: str) -> int:
        """
        将中文数字转换为阿拉伯数字
        
        Args:
            chinese_num: 中文数字字符串
            
        Returns:
            对应的阿拉伯数字
        """
        # 中文数字到阿拉伯数字的映射
        chinese_digits = {
            '零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
            '百': 100, '千': 1000, '万': 10000
        }
        
        # 如果是纯数字，直接返回
        if chinese_num.isdigit():
            return int(chinese_num)
        
        # 处理特殊情况
        if chinese_num == '十':
            return 10
        
        # 处理中文数字
        result = 0
        temp = 0
        
        for char in chinese_num:
            if char in chinese_digits:
                digit = chinese_digits[char]
                if digit < 10:  # 个位数
                    temp = temp * 10 + digit
                else:  # 十、百、千、万等
                    if temp == 0:
                        temp = 1
                    result += temp * digit
                    temp = 0
        
        result += temp
        return result
    
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