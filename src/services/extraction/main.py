"""
信息提取模块的主入口文件
提供简单的接口来使用信息提取功能
"""

import os
import json
import asyncio
import aiofiles
from typing import Dict, Any, Optional
from langchain_core.messages import BaseMessage

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
    
    # 创建主控Agent并执行信息提取
    main_agent = NovelInformationExtractor()
    
    # 使用异步方式执行信息提取，避免阻塞
    result = await asyncio.to_thread(
        main_agent.extract_novel_information_parallel,
        novel_text
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


if __name__ == "__main__":
    # 示例用法
    import argparse
    
    parser = argparse.ArgumentParser(description="小说信息提取工具")
    parser.add_argument("input_path", help="小说文件路径或包含小说文件的目录")
    parser.add_argument("--output", "-o", help="输出目录", default=None)
    parser.add_argument("--processes", "-p", type=int, default=4, help="最大并发处理数量，默认为4")
    parser.add_argument("--single", "-s", action="store_true", help="强制使用单线程处理，即使输入是目录")
    
    args = parser.parse_args()
    
    async def main():
        try:
            # 扫描输入路径，获取所有小说文件
            file_paths = scan_novel_files(args.input_path)
            
            if not file_paths:
                print(f"在路径 {args.input_path} 中未找到小说文件")
                exit(1)
            
            print(f"找到 {len(file_paths)} 个小说文件")
            
            # 如果输入是目录且没有强制指定单进程，则使用异步IO
            is_directory = os.path.isdir(args.input_path)
            use_async = is_directory and not args.single
            
            if use_async:
                print(f"检测到目录输入，使用异步IO处理 (最大并发数: {args.processes})")
                result = await batch_extract_novel_info(file_paths, args.output, args.processes)
            else:
                # 所有情况都使用批量处理函数，确保信号量控制生效
                print(f"使用异步IO处理 {len(file_paths)} 个文件 (最大并发数: {args.processes})")
                result = await batch_extract_novel_info(file_paths, args.output, args.processes)
            
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
    
    # 运行主函数
    asyncio.run(main())