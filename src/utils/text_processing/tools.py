"""
信息提取模块的基础工具类
只保留必要的文件操作功能，其他文本处理任务交给AI代理处理
"""

import os
from typing import Dict, Any
from langchain_core.tools import tool
from pydantic import BaseModel, Field


class TextLoaderInput(BaseModel):
    """文本加载工具的输入参数"""
    file_path: str = Field(description="小说文件的路径")


@tool
def load_text_from_file(file_path: str) -> Dict[str, Any]:
    """
    从文件加载小说文本
    
    Args:
        file_path: 小说文件的路径
        
    Returns:
        包含文本内容和元数据的字典
    """
    if not os.path.exists(file_path):
        return {
            "success": False,
            "error": f"文件不存在: {file_path}",
            "content": "",
            "metadata": {}
        }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 获取文件基本信息
        file_stats = os.stat(file_path)
        metadata = {
            "file_size": file_stats.st_size,
            "line_count": len(content.splitlines()),
            "char_count": len(content),
            "file_name": os.path.basename(file_path)
        }
        
        return {
            "success": True,
            "content": content,
            "metadata": metadata
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"读取文件时出错: {str(e)}",
            "content": "",
            "metadata": {}
        }