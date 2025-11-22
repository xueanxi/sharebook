"""
信息提取模块的主入口文件
提供简单的接口来使用信息提取功能
"""

import os
import sys

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, project_root)

import json
import asyncio
import aiofiles
import argparse
from typing import Dict, Any, Optional, List
from langchain_core.messages import BaseMessage
from pathlib import Path
from src.core.agents.info_extract import NovelInformationExtractor


def custom_json_serializer(obj):
    """自定义JSON序列化函数，处理不可序列化的对象"""
    try:
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
    except Exception as e:
        # 如果序列化失败，返回错误信息
        return f"<序列化失败: {str(e)}>"


async def extract_novel_information(file_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    从小说文件中提取信息的便捷函数（异步版本）
    
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
    
    # 异步读取文件内容
    try:
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            novel_text = await f.read()
    except Exception as e:
        return {
            "success": False,
            "error": f"读取文件失败: {str(e)}"
        }
    
    # 使用Path，提取文件名
    file_name = Path(file_path).name
    print(f'extract_novel_information# filename:{file_name}')
    
    # 创建主控Agent并执行信息提取
    main_agent = NovelInformationExtractor()
    
    # 使用异步方式执行信息提取，避免阻塞
    result = await asyncio.to_thread(
        main_agent.extract_novel_information_parallel,
        novel_text,
        file_name
    )
    
    # 添加文件路径和成功状态
    result["file_path"] = file_path
    result["success"] = True
    
    # 如果指定了输出目录，异步保存结果
    if output_dir:
        try:
            os.makedirs(output_dir, exist_ok=True)
            print(f"输出目录已创建: {output_dir}")  # 添加输出目录创建的日志
            
            # 检查目录是否可写
            if not os.access(output_dir, os.W_OK):
                raise PermissionError(f"输出目录 {output_dir} 不可写")
        except Exception as e:
            result["save_error"] = f"创建输出目录失败: {str(e)}"
            print(f"创建输出目录失败: {str(e)}")
            return result
        
        # 生成输出文件名
        file_name = os.path.basename(file_path)
        base_name, _ = os.path.splitext(file_name)
        
        # 所有处理都是并行的
        output_file = os.path.join(output_dir, f"{base_name}_info.json")
        output_file = output_file.replace(" ", "")
        print(f"准备保存文件到: {output_file}")  # 添加文件保存路径的日志
        
        # 异步保存结果
        try:
            async with aiofiles.open(output_file, 'w', encoding='utf-8') as f:
                content = json.dumps(result, ensure_ascii=False, indent=2, default=custom_json_serializer)
                await f.write(content)
            result["output_file"] = output_file
            print(f"文件已成功保存到: {output_file}")  # 添加保存成功的日志
        except Exception as e:
            result["save_error"] = f"保存文件失败: {str(e)}"
            print(f"保存文件失败: {str(e)}")  # 添加保存失败的日志
    
    return result


async def process_single_file(file_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    处理单个小说文件的辅助函数，用于异步处理
    
    Args:
        file_path: 小说文件路径
        output_dir: 输出目录，如果提供，结果将保存为JSON文件
        
    Returns:
        包含提取信息的字典
    """
    return await extract_novel_information(file_path, output_dir)


def scan_novel_files(input_path: str) -> list:
    """
    扫描输入路径，获取所有小说文件
    
    Args:
        input_path: 输入路径，可以是文件或文件夹
        
    Returns:
        小说文件路径列表
    """
    file_paths = []
    
    if os.path.isfile(input_path):
        # 如果是文件，直接添加到列表
        file_paths.append(input_path)
    elif os.path.isdir(input_path):
        # 如果是目录，扫描所有.txt文件
        for root, dirs, files in os.walk(input_path):
            for file in files:
                if file.endswith('.txt'):
                    file_paths.append(os.path.join(root, file))
    else:
        raise ValueError(f"无效的输入路径: {input_path}")
    
    return file_paths


async def batch_extract_novel_info(file_paths: list, output_dir: Optional[str] = None, max_concurrent: int = 4) -> Dict[str, Any]:
    """
    批量处理多个小说文件（异步IO版本）
    
    Args:
        file_paths: 小说文件路径列表
        output_dir: 输出目录，如果提供，结果将保存为JSON文件
        max_concurrent: 最大并发处理数量，默认为4
        
    Returns:
        包含所有提取信息的字典
    """
    results = {
        "success": True,
        "total_files": len(file_paths),
        "successful_extractions": 0,
        "failed_extractions": 0,
        "results": {},
        "async_execution": True,
        "max_concurrent": max_concurrent
    }
    
    # 始终使用信号量控制并发数量，即使只有一个文件
    print(f"使用异步IO处理 {len(file_paths)} 个文件，最大并发数: {max_concurrent}")
    
    # 创建信号量控制并发数量
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_and_save_immediately(file_path):
        """处理文件并立即保存结果"""
        async with semaphore:
            # 处理单个文件
            result = await process_single_file(file_path, output_dir)
            
            # 立即保存结果到汇总字典中
            file_name = os.path.basename(file_path)
            results["results"][file_name] = result
            
            # 更新统计信息
            if result.get("success", False):
                results["successful_extractions"] += 1
                if "output_file" in result:
                    print(f"文件 {file_name} 处理成功，结果已保存到: {result['output_file']}")
                else:
                    print(f"文件 {file_name} 处理成功，但未保存文件")
            else:
                results["failed_extractions"] += 1
                error_msg = result.get("error", "未知错误")
                save_error = result.get("save_error", None)
                if save_error:
                    error_msg += f", 保存错误: {save_error}"
                print(f"文件 {file_name} 处理失败: {error_msg}")
                # 记录详细错误信息
                if "errors" in result and result["errors"]:
                    print(f"详细错误: {result['errors']}")
            
            return result
    
    # 创建任务列表
    tasks = [process_and_save_immediately(file_path) for file_path in file_paths]
    
    # 等待所有任务完成，但每个文件处理完成后会立即保存结果
    await asyncio.gather(*tasks, return_exceptions=True)
    
    # 如果有失败的提取，将整体成功标志设为False
    if results["failed_extractions"] > 0:
        results["success"] = False
        results["error"] = f"有{results['failed_extractions']}个文件提取失败"
    
    return results


def main():
    """主函数，处理命令行参数"""
    parser = argparse.ArgumentParser(description="ShareNovel 小说信息提取工具")
    
    # 信息提取命令参数
    extract_group = parser.add_mutually_exclusive_group(required=True)
    extract_group.add_argument('-f', '--file', help='要处理的小说文件路径')
    extract_group.add_argument('-d', '--directory', help='包含小说文件的目录路径')
    parser.add_argument('-o', '--output', help='输出目录', default='data/output')
    
    # 直接解析所有命令行参数
    args = parser.parse_args()
    
    # 处理新的命令行参数格式
    if args.file:
        # 单文件提取 - 需要异步处理
        async def process_single():
            result = await extract_novel_information(args.file, args.output)
            if result.get("success", False):
                print("✅ 信息提取成功!")
                if "output_file" in result:
                    print(f"结果已保存到: {result['output_file']}")
                print("使用langgraph处理模式")
            else:
                print("❌ 信息提取失败:")
                print(result.get("error", "未知错误"))
        
        asyncio.run(process_single())
    elif args.directory:
        # 批量提取
        txt_files = [os.path.join(args.directory, f) for f in os.listdir(args.directory) 
                     if f.endswith('.txt')]
        if not txt_files:
            print(f"在目录 {args.directory} 中没有找到.txt文件")
            return
        
        async def process_batch():
            result = await batch_extract_novel_info(txt_files, args.output)
            print(f"处理完成: {result['successful_extractions']}/{result['total_files']} 个文件成功")
            if result.get("failed_extractions", 0) > 0:
                print(f"有 {result['failed_extractions']} 个文件处理失败")
            print("使用 langgraph 并行处理模式")
        
        asyncio.run(process_batch())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()