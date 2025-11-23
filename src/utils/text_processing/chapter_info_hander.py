import re
import os
from typing import Optional


def extract_chapter_info(file_path: str) -> Optional[str]:
    """
    从文件路径或文件名中提取章节信息
    
    Args:
        file_path: 文件路径或文件名
        
    Returns:
        章节信息，如"第一章"、"第二章"等，如果无法提取则返回None
        
    Examples:
        >>> extract_chapter_info("data\\storyboards_prompt\\第一章 遇强则强_prompts.json")
        '第一章'
        >>> extract_chapter_info("第一章 遇强则强_prompts.json")
        '第一章'
        >>> extract_chapter_info("第四章修为又升！送上门的经验包！.txt")
        '第四章'
    """
    # 获取文件名（去除路径和扩展名）
    file_name = os.path.basename(file_path)
    name_without_ext = os.path.splitext(file_name)[0]
    
    # 匹配章节信息的正则表达式模式
    # 匹配"第X章"格式，其中X可以是数字、中文数字等
    chapter_pattern = r'第([0-9一二三四五六七八九十百千万零]+)章'
    
    # 搜索章节信息
    match = re.search(chapter_pattern, name_without_ext)
    
    if match:
        # 返回完整的章节信息，如"第一章"
        chapter_num = match.group(1)
        return f"第{chapter_num}章"
    
    return None


def extract_chapter_number(file_path: str) -> Optional[int]:
    """
    从文件路径或文件名中提取章节号
    
    Args:
        file_path: 文件路径或文件名
        
    Returns:
        章节号（整数），如果无法提取则返回None
        
    Examples:
        >>> extract_chapter_number("data\\storyboards_prompt\\第一章 遇强则强_prompts.json")
        1
        >>> extract_chapter_number("第四章修为又升！送上门的经验包！.txt")
        4
    """
    chapter_info = extract_chapter_info(file_path)
    
    if not chapter_info:
        return None
    
    # 提取章节号
    chapter_num_str = chapter_info[1:-1]  # 去掉"第"和"章"
    
    # 处理中文数字
    chinese_num_map = {
        '零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
        '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
        '百': 100, '千': 1000, '万': 10000
    }
    
    # 如果是纯阿拉伯数字，直接转换
    if chapter_num_str.isdigit():
        return int(chapter_num_str)
    
    # 处理中文数字
    result = 0
    temp = 0
    
    for char in chapter_num_str:
        if char in chinese_num_map:
            num = chinese_num_map[char]
            if num < 10:  # 个位数
                temp = temp * 10 + num if temp > 10 else num
            else:  # 十、百、千、万等
                if temp == 0:
                    temp = 1
                result += temp * num
                temp = 0
    
    result += temp
    
    return result if result > 0 else None


def extract_chapter_title(file_path: str) -> Optional[str]:
    """
    从文件路径或文件名中提取章节标题（章节名称）
    
    Args:
        file_path: 文件路径或文件名
        
    Returns:
        章节标题，如果无法提取则返回None
        
    Examples:
        >>> extract_chapter_title("data\\storyboards_prompt\\第一章 遇强则强_prompts.json")
        '遇强则强'
        >>> extract_chapter_title("第四章修为又升！送上门的经验包！.txt")
        '修为又升！送上门的经验包！'
    """
    # 获取文件名（去除路径和扩展名）
    file_name = os.path.basename(file_path)
    name_without_ext = os.path.splitext(file_name)[0]
    
    # 匹配章节信息的正则表达式模式
    chapter_pattern = r'第([0-9一二三四五六七八九十百千万零]+)章'
    
    # 搜索章节信息
    match = re.search(chapter_pattern, name_without_ext)
    
    if match:
        # 提取章节标题（章节名）
        chapter_end = match.end()
        title = name_without_ext[chapter_end:].strip()
        
        # 去除可能的后缀，如"_prompts"
        title = re.sub(r'_prompts.*$', '', title)
        
        return title if title else None
    
    return None


def get_full_chapter_info(file_path: str) -> dict:
    """
    获取完整的章节信息，包括章节号、章节名称等
    
    Args:
        file_path: 文件路径或文件名
        
    Returns:
        包含章节信息的字典，包括:
        - chapter_info: 章节信息，如"第一章"
        - chapter_number: 章节号（整数）
        - chapter_title: 章节标题
        - file_name: 文件名
        - file_path: 原始文件路径
    """
    return {
        'chapter_info': extract_chapter_info(file_path),
        'chapter_number': extract_chapter_number(file_path),
        'chapter_title': extract_chapter_title(file_path),
        'file_name': os.path.basename(file_path),
        'file_path': file_path
    }


if __name__ == "__main__":
    # 测试用例
    test_cases = [
        "data\\storyboards_prompt\\第一章 遇强则强_prompts.json",
        "第一章 遇强则强_prompts.json",
        "第四章修为又升！送上门的经验包！.txt",
        "data\\cleaned_novel\\第七章 绝望的魔教教主.txt",
        "第三十一章 不要吃鼠鼠！.txt"
    ]
    
    for test_case in test_cases:
        print(f"测试文件: {test_case}")
        print(f"章节信息: {extract_chapter_info(test_case)}")
        print(f"章节号: {extract_chapter_number(test_case)}")
        print(f"章节标题: {extract_chapter_title(test_case)}")
        print("-" * 50)