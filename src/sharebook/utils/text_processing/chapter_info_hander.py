"""
章节信息处理器模块
"""

from typing import Dict, Any, Optional
import re

def extract_chapter_info(text: str) -> Dict[str, Any]:
    """
    从文本中提取章节信息
    
    Args:
        text: 章节文本内容
        
    Returns:
        章节信息字典
    """
    # 简单的章节信息提取
    lines = text.split('\n')
    title = ""
    content = ""
    
    if lines:
        # 第一行通常是标题
        title = lines[0].strip()
        # 其余行是内容
        content = '\n'.join(lines[1:]).strip()
    
    return {
        'title': title,
        'content': content,
        'word_count': len(content),
        'line_count': len(lines) - 1
    }

def get_chapter_title(filename: str) -> str:
    """
    从文件名获取章节标题
    
    Args:
        filename: 文件名
        
    Returns:
        章节标题
    """
    # 移除扩展名
    title = filename.replace('.txt', '')
    
    # 移除章节编号前缀
    patterns = [
        r'^第\d+章\s*',
        r'^\d+章\s*',
        r'^chapter\d+\s*',
        r'^ch\d+\s*',
        r'^\d+\s*',
    ]
    
    for pattern in patterns:
        title = re.sub(pattern, '', title, flags=re.IGNORECASE)
    
    return title.strip()