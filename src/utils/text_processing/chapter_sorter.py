"""
章节排序工具模块

提供章节文件排序和章节号提取的功能
"""

import os
import re
from typing import List


class ChapterSorter:
    """章节排序工具类"""
    
    @staticmethod
    def sort_chapter_files(files: List[str]) -> List[str]:
        """
        按章节号智能排序章节文件
        
        Args:
            files: 文件路径列表
            
        Returns:
            排序后的文件列表
        """
        try:
            # 按章节号排序
            sorted_files = sorted(files, key=ChapterSorter.extract_chapter_number)
            return sorted_files
        except:
            # 如果排序失败，返回原始顺序
            return files
    
    @staticmethod
    def extract_chapter_number(filepath: str) -> int:
        """
        从文件名中提取章节号
        
        Args:
            filepath: 文件路径
            
        Returns:
            章节号，如果无法提取则返回一个大数字
        """
        try:
            filename = os.path.basename(filepath)
            
            # 使用正则表达式匹配章节号
            # 匹配模式：第X章、第X章、第X章等
            match = re.search(r'第([一二三四五六七八九十百千万\d]+)章', filename)
            if match:
                chapter_str = match.group(1)
                # 将中文数字转换为阿拉伯数字
                return ChapterSorter.chinese_number_to_int(chapter_str)
            else:
                # 如果没有匹配到章节号，尝试匹配各种数字模式
                patterns = [
                    r'chapter[^\d]*(\d+)',  # chapter1, chapter_1
                    r'^(\d+)',  # 以数字开头
                    r'(\d+)[^\d]*$',  # 以数字结尾
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, filename, re.IGNORECASE)
                    if match:
                        return int(match.group(1))
                
                # 如果都匹配不到，返回一个大数字，确保这些文件排在最后
                return 999999
        except Exception:
            # 出错时返回大数字
            return 999999
    
    @staticmethod
    def chinese_number_to_int(chinese_num: str) -> int:
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