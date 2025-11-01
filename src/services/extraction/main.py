"""
信息提取模块的主入口文件
提供简单的接口来使用信息提取功能
"""

import os
import json
from typing import Dict, Any, Optional
from langchain_core.messages import BaseMessage

from src.core.agents.info_extract import NovelInformationExtractor


def custom_json_serializer(obj):
    """自定义JSON序列化函数，处理不可序列化的对象"""
    if isinstance(obj, BaseMessage):
        return {
            "type": obj.__class__.__name__,
            "content": obj.content
        }
    elif hasattr(obj, 'dict'):
        return obj.dict()
    elif hasattr(obj, '__dict__'):
        return obj.__dict__
    else:
        return str(obj)


def extract_novel_information(file_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    从小说文件中提取信息的便捷函数
    
    Args:
        file_path: 小说文件路径
        output_dir: 输出目录，如果提供，结果将保存为JSON文件
        
    Returns:
        包含提取信息的字典
    """
    # 检查文件是否存在
    if not os.path.exists(file_path):
        return {
            "success": False,
            "error": f"文件不存在: {file_path}"
        }
    
    # 读取文件内容
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            novel_text = f.read()
    except Exception as e:
        return {
            "success": False,
            "error": f"读取文件失败: {str(e)}"
        }
    
    # 创建主控Agent并执行信息提取
    main_agent = NovelInformationExtractor()
    result = main_agent.extract_novel_information_parallel(novel_text)
    
    # 添加文件路径和成功状态
    result["file_path"] = file_path
    result["success"] = True
    
    # 如果指定了输出目录，保存结果
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成输出文件名
        file_name = os.path.basename(file_path)
        base_name, _ = os.path.splitext(file_name)
        
        # 所有处理都是并行的
        parallel_suffix = "_parallel"
        output_file = os.path.join(output_dir, f"{base_name}_info{parallel_suffix}.json")
        
        # 保存结果
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=custom_json_serializer)
        
        result["output_file"] = output_file
    
    return result


def batch_extract_novel_info(file_paths: list, output_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    批量处理多个小说文件
    
    Args:
        file_paths: 小说文件路径列表
        output_dir: 输出目录，如果提供，结果将保存为JSON文件
        
    Returns:
        包含所有提取信息的字典
    """
    results = {
        "success": True,
        "total_files": len(file_paths),
        "successful_extractions": 0,
        "failed_extractions": 0,
        "results": {}
    }
    
    for file_path in file_paths:
        print(f"处理文件: {file_path}")
        result = extract_novel_information(file_path, output_dir)
        
        file_name = os.path.basename(file_path)
        results["results"][file_name] = result
        
        if result.get("success", False):
            results["successful_extractions"] += 1
        else:
            results["failed_extractions"] += 1
    
    # 如果有失败的提取，将整体成功标志设为False
    if results["failed_extractions"] > 0:
        results["success"] = False
        results["error"] = f"有{results['failed_extractions']}个文件提取失败"
    
    # 添加并行处理信息
    results["parallel_execution"] = True
    
    return results


if __name__ == "__main__":
    # 示例用法
    import argparse
    
    parser = argparse.ArgumentParser(description="小说信息提取工具")
    parser.add_argument("file_path", help="小说文件路径")
    parser.add_argument("--output", "-o", help="输出目录", default=None)
    
    args = parser.parse_args()
    
    result = extract_novel_information(args.file_path, args.output)
    
    if result.get("success", False):
        print("信息提取成功!")
        if "output_file" in result:
            print(f"结果已保存到: {result['output_file']}")
    else:
        print("信息提取失败:")
        print(result.get("error", "未知错误"))