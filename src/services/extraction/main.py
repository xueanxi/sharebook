"""
信息提取模块的主入口文件
提供简单的接口来使用信息提取功能
"""

import os
import json
import multiprocessing
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


def process_single_file(file_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    处理单个小说文件的辅助函数，用于多进程处理
    
    Args:
        file_path: 小说文件路径
        output_dir: 输出目录，如果提供，结果将保存为JSON文件
        
    Returns:
        包含提取信息的字典
    """
    return extract_novel_information(file_path, output_dir)


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


def batch_extract_novel_info(file_paths: list, output_dir: Optional[str] = None, num_processes: int = 4) -> Dict[str, Any]:
    """
    批量处理多个小说文件（多进程版本）
    
    Args:
        file_paths: 小说文件路径列表
        output_dir: 输出目录，如果提供，结果将保存为JSON文件
        num_processes: 使用的进程数量，默认为4
        
    Returns:
        包含所有提取信息的字典
    """
    results = {
        "success": True,
        "total_files": len(file_paths),
        "successful_extractions": 0,
        "failed_extractions": 0,
        "results": {},
        "parallel_execution": True,
        "num_processes": num_processes
    }
    
    # 如果只有一个文件或进程数为1，使用单进程处理
    if len(file_paths) == 1 or num_processes <= 1:
        for file_path in file_paths:
            print(f"处理文件: {file_path}")
            result = extract_novel_information(file_path, output_dir)
            
            file_name = os.path.basename(file_path)
            results["results"][file_name] = result
            
            if result.get("success", False):
                results["successful_extractions"] += 1
            else:
                results["failed_extractions"] += 1
    else:
        # 使用多进程处理
        print(f"使用 {num_processes} 个进程并行处理 {len(file_paths)} 个文件")
        
        # 创建进程池
        pool = multiprocessing.Pool(processes=num_processes)
        
        # 准备参数，每个文件路径和输出目录组成一个元组
        args = [(file_path, output_dir) for file_path in file_paths]
        
        # 使用map_async异步处理所有文件
        async_results = pool.starmap_async(process_single_file, args)
        
        # 关闭进程池，等待所有任务完成
        pool.close()
        pool.join()
        
        # 获取所有结果
        file_results = async_results.get()
        
        # 整理结果
        for i, file_path in enumerate(file_paths):
            result = file_results[i]
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
    
    return results


if __name__ == "__main__":
    # 示例用法
    import argparse
    
    parser = argparse.ArgumentParser(description="小说信息提取工具")
    parser.add_argument("input_path", help="小说文件路径或包含小说文件的目录")
    parser.add_argument("--output", "-o", help="输出目录", default=None)
    parser.add_argument("--processes", "-p", type=int, default=4, help="使用的进程数量，默认为4")
    parser.add_argument("--single", "-s", action="store_true", help="强制使用单进程处理，即使输入是目录")
    
    args = parser.parse_args()
    
    try:
        # 扫描输入路径，获取所有小说文件
        file_paths = scan_novel_files(args.input_path)
        
        if not file_paths:
            print(f"在路径 {args.input_path} 中未找到小说文件")
            exit(1)
        
        print(f"找到 {len(file_paths)} 个小说文件")
        
        # 如果输入是目录且没有强制指定单进程，则使用多进程
        is_directory = os.path.isdir(args.input_path)
        use_multiprocessing = is_directory and not args.single
        
        if use_multiprocessing:
            print(f"检测到目录输入，使用多进程处理 ({args.processes} 个进程)")
            result = batch_extract_novel_info(file_paths, args.output, args.processes)
        elif len(file_paths) == 1:
            # 单文件处理模式
            print(f"处理单个文件: {file_paths[0]}")
            result = extract_novel_information(file_paths[0], args.output)
        else:
            # 多文件但使用单进程
            print(f"使用单进程处理 {len(file_paths)} 个文件")
            result = batch_extract_novel_info(file_paths, args.output, 1)
        
        # 输出结果
        if isinstance(result, dict) and "results" in result:
            # 批量处理结果
            if result.get("success", False):
                print(f"批量处理成功! 成功处理 {result['successful_extractions']} 个文件")
            else:
                print(f"批量处理部分失败! 成功: {result['successful_extractions']}, 失败: {result['failed_extractions']}")
                if "error" in result:
                    print(f"错误信息: {result['error']}")
        else:
            # 单文件处理结果
            if result.get("success", False):
                print("信息提取成功!")
                if "output_file" in result:
                    print(f"结果已保存到: {result['output_file']}")
            else:
                print("信息提取失败:")
                print(result.get("error", "未知错误"))
                
    except ValueError as e:
        print(f"错误: {str(e)}")
        exit(1)
    except Exception as e:
        print(f"处理过程中发生异常: {str(e)}")
        exit(1)