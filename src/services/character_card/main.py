"""
角色卡提取服务的主入口文件
提供简单的接口来使用角色卡生成功能
"""

import os
import json
import asyncio
import aiofiles
from typing import Dict, Any, Optional, List

from src.core.agents.content_creation import CharacterCardGenerator
from src.utils.logging_manager import get_agent_logger

logger = get_agent_logger(__name__)


def custom_json_serializer(obj):
    """自定义JSON序列化函数，处理不可序列化的对象"""
    try:
        if hasattr(obj, 'dict'):
            return obj.dict()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return str(obj)
    except Exception as e:
        # 如果序列化失败，返回错误信息
        return f"<序列化失败: {str(e)}>"


async def extract_character_cards(character_info_file: str, text_file: str, 
                                 output_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    从角色信息文件和文本文件中提取角色卡片的便捷函数（异步版本）
    
    Args:
        character_info_file: 角色信息文件路径
        text_file: 原文文本文件路径
        output_dir: 输出目录，如果提供，结果将保存为JSON文件，同时也会读取该目录中的已存在角色卡片
        
    Returns:
        包含角色卡片的字典
    """
    # 检查文件是否存在
    if not os.path.exists(character_info_file):
        return {
            "success": False,
            "error": f"角色信息文件不存在: {character_info_file}"
        }
    
    if not os.path.exists(text_file):
        return {
            "success": False,
            "error": f"文本文件不存在: {text_file}"
        }
    
    # 异步读取文件内容
    try:
        async with aiofiles.open(character_info_file, 'r', encoding='utf-8') as f:
            character_info = json.loads(await f.read())
        
        async with aiofiles.open(text_file, 'r', encoding='utf-8') as f:
            original_text = await f.read()
        
        # 读取已存在的角色卡片
        existing_cards = {}
        if output_dir and os.path.exists(output_dir):
            # 扫描输出目录中的所有角色卡片文件
            for file_name in os.listdir(output_dir):
                if file_name.endswith('.json'):
                    file_path = os.path.join(output_dir, file_name)
                    try:
                        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                            character_card = json.loads(await f.read())
                            # 使用角色名作为键
                            character_name = character_card.get('name', os.path.splitext(file_name)[0])
                            existing_cards[character_name] = character_card
                    except Exception as e:
                        logger.warning(f"读取角色卡片文件 {file_path} 失败: {str(e)}")
        
    except Exception as e:
        return {
            "success": False,
            "error": f"读取文件失败: {str(e)}"
        }
    
    # 创建主控Agent并执行角色卡生成
    main_agent = CharacterCardGenerator()
    
    # 使用异步方式执行角色卡生成
    result = await asyncio.to_thread(
        main_agent.extract,
        character_info,
        original_text,
        existing_cards
    )
    
    # 添加文件路径和成功状态
    result["character_info_file"] = character_info_file
    result["text_file"] = text_file
    
    # 如果指定了输出目录，异步保存结果
    if output_dir:
        try:
            os.makedirs(output_dir, exist_ok=True)
            logger.info(f"输出目录已创建: {output_dir}")
            
            # 检查目录是否可写
            if not os.access(output_dir, os.W_OK):
                raise PermissionError(f"输出目录 {output_dir} 不可写")
        except Exception as e:
            result["save_error"] = f"创建输出目录失败: {str(e)}"
            logger.error(f"创建输出目录失败: {str(e)}")
            return result
        
        # 按角色名保存角色卡片
        saved_files = []
        if result.get("success") and "final_cards" in result:
            for character_name, character_card in result["final_cards"].items():
                # 清理角色名，确保文件名安全
                safe_character_name = character_name.replace("/", "_").replace("\\", "_").replace(":", "_").replace("*", "_").replace("?", "_").replace("\"", "_").replace("<", "_").replace(">", "_").replace("|", "_")
                output_file = os.path.join(output_dir, f"{safe_character_name}.json")
                output_file = output_file.replace(" ", "")
                
                try:
                    async with aiofiles.open(output_file, 'w', encoding='utf-8') as f:
                        content = json.dumps(character_card, ensure_ascii=False, indent=2, default=custom_json_serializer)
                        await f.write(content)
                    saved_files.append(output_file)
                    logger.info(f"角色卡片 {character_name} 已保存到: {output_file}")
                except Exception as e:
                    logger.error(f"保存角色卡片 {character_name} 失败: {str(e)}")
        
        result["saved_character_files"] = saved_files
        if saved_files:
            result["output_directory"] = output_dir
            logger.info(f"共保存 {len(saved_files)} 个角色卡片文件到: {output_dir}")
    
    return result


async def process_single_chapter(character_info_file: str, text_file: str, 
                                output_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    处理单个章节的辅助函数，用于异步处理
    
    Args:
        character_info_file: 角色信息文件路径
        text_file: 原文文本文件路径
        output_dir: 输出目录，如果提供，结果将保存为JSON文件
        
    Returns:
        包含角色卡片的字典
    """
    return await extract_character_cards(character_info_file, text_file, output_dir)


def fuzzy_match_files(pattern: str, directories: List[str], file_extensions: List[str] = None) -> List[str]:
    """
    在指定目录中基于章节前缀匹配文件
    
    Args:
        pattern: 章节前缀模式（如"第三章"）
        directories: 要搜索的目录列表
        file_extensions: 文件扩展名过滤列表，如['.txt', '.json']
        
    Returns:
        匹配到的文件路径列表
    """
    if file_extensions is None:
        file_extensions = ['.txt', '.json']
    
    matched_files = []
    
    for directory in directories:
        if not os.path.exists(directory):
            continue
            
        for root, dirs, files in os.walk(directory):
            for file in files:
                # 检查文件扩展名
                if not any(file.lower().endswith(ext.lower()) for ext in file_extensions):
                    continue
                
                file_path = os.path.join(root, file)
                base_name = os.path.splitext(file)[0]
                
                # 检查文件名是否以模式开头
                if base_name.startswith(pattern):
                    matched_files.append(file_path)
    
    return matched_files


def find_chapter_files(chapter_name: str, base_dir: str = "data") -> Dict[str, str]:
    """
    根据章节名称自动查找对应的文件，支持基于章节前缀的匹配
    
    Args:
        chapter_name: 章节名称（如"第一章"）
        base_dir: 基础目录，默认为data
        
    Returns:
        包含character_info_file和text_file的字典
    """
    # 首先尝试精确匹配
    # 定义可能的文件路径
    possible_paths = [
        # raw目录
        f"{base_dir}/raw/{chapter_name}.txt",
        # raw_bak目录
        f"{base_dir}/raw_bak/{chapter_name}.txt",
        # data_crawl_novel目录
        f"data_crawl_novel/{chapter_name}.txt",
    ]
    
    # 查找文本文件
    text_file = None
    for path in possible_paths:
        if os.path.exists(path):
            text_file = path
            break
    
    if text_file:
        # 找到精确匹配的文本文件，查找对应的角色信息文件
        base_name = os.path.splitext(os.path.basename(text_file))[0]
        info_file = f"{base_dir}/output/{base_name}_info.json"
        
        # 如果output目录没有，尝试output_bak目录
        if not os.path.exists(info_file):
            info_file = f"{base_dir}/output_bak/{base_name}_info.json"
        
        if os.path.exists(info_file):
            return {
                "character_info_file": info_file,
                "text_file": text_file
            }
    
    # 如果精确匹配失败，尝试基于章节前缀的匹配
    # 搜索文本文件
    text_files = fuzzy_match_files(
        chapter_name, 
        [f"{base_dir}/raw", f"{base_dir}/raw_bak", "data_crawl_novel"],
        ['.txt']
    )
    
    if not text_files:
        raise ValueError(f"未找到以 '{chapter_name}' 开头的文本文件")
    
    # 使用第一个匹配的文本文件
    text_file = text_files[0]
    logger.info(f"匹配到文本文件: {text_file}")
    
    # 获取文本文件的基础名称
    base_name = os.path.splitext(os.path.basename(text_file))[0]
    
    # 搜索对应的角色信息文件
    info_files = fuzzy_match_files(
        base_name,
        [f"{base_dir}/output", f"{base_dir}/output_bak"],
        ['_info_async.json']
    )
    
    if not info_files:
        # 如果找不到_info_async.json，尝试_info.json
        info_files = fuzzy_match_files(
            base_name,
            [f"{base_dir}/output", f"{base_dir}/output_bak"],
            ['_info.json']
        )
    
    if not info_files:
        # 如果还是找不到，尝试直接搜索章节前缀
        info_files = fuzzy_match_files(
            chapter_name,
            [f"{base_dir}/output", f"{base_dir}/output_bak"],
            ['_info_async.json', '_info.json']
        )
    
    if not info_files:
        raise ValueError(f"未找到以 '{chapter_name}' 开头的角色信息文件")
    
    character_info_file = info_files[0]
    logger.info(f"匹配到角色信息文件: {character_info_file}")
    
    return {
        "character_info_file": character_info_file,
        "text_file": text_file
    }


def scan_chapter_files(input_path: str) -> List[Dict[str, str]]:
    """
    扫描输入路径，获取所有章节文件对
    
    Args:
        input_path: 输入路径，可以是文件或文件夹
        
    Returns:
        章节文件对列表，每个元素包含character_info_file和text_file
    """
    chapter_files = []
    
    if os.path.isfile(input_path):
        # 如果是文件，假设是文本文件，尝试查找对应的角色信息文件
        base_name, _ = os.path.splitext(input_path)
        # 先尝试查找_info_async.json，再尝试查找_info.json
        character_info_file = f"{base_name}_info_async.json"
        if not os.path.exists(character_info_file):
            character_info_file = f"{base_name}_info.json"
        
        if os.path.exists(character_info_file):
            chapter_files.append({
                "character_info_file": character_info_file,
                "text_file": input_path
            })
    elif os.path.isdir(input_path):
        # 如果是目录，扫描所有.txt文件和对应的_info_async.json或_info.json文件
        # 需要在多个目录中查找匹配的文件
        search_dirs = [input_path]
        # 如果是data/raw，也搜索data/output
        if input_path.endswith("data/raw"):
            search_dirs.append("data/output")
        elif input_path.endswith("data/raw_bak"):
            search_dirs.append("data/output")
        
        for root, dirs, files in os.walk(input_path):
            for file in files:
                if file.endswith('.txt'):
                    text_file = os.path.join(root, file)
                    base_name, _ = os.path.splitext(file)
                    
                    # 在搜索目录中查找对应的角色信息文件
                    character_info_file = None
                    for search_dir in search_dirs:
                        # 先尝试查找_info_async.json，再尝试查找_info.json
                        potential_file = os.path.join(search_dir, f"{base_name}_info_async.json")
                        if os.path.exists(potential_file):
                            character_info_file = potential_file
                            break
                        potential_file = os.path.join(search_dir, f"{base_name}_info.json")
                        if os.path.exists(potential_file):
                            character_info_file = potential_file
                            break
                    
                    if character_info_file:
                        chapter_files.append({
                            "character_info_file": character_info_file,
                            "text_file": text_file
                        })
    else:
        raise ValueError(f"无效的输入路径: {input_path}")
    
    return chapter_files


async def batch_extract_character_cards(chapter_files: List[Dict[str, str]], 
                                      output_dir: Optional[str] = None, 
                                      max_concurrent: int = 4) -> Dict[str, Any]:
    """
    批量处理多个章节的角色卡片（异步IO版本）
    
    Args:
        chapter_files: 章节文件对列表
        output_dir: 输出目录，如果提供，结果将保存为JSON文件
        max_concurrent: 最大并发处理数量，默认为4
        
    Returns:
        包含所有角色卡片的字典
    """
    results = {
        "success": True,
        "total_chapters": len(chapter_files),
        "successful_extractions": 0,
        "failed_extractions": 0,
        "results": {},
        "all_character_cards": {},
        "async_execution": True,
        "max_concurrent": max_concurrent
    }
    
    # 始终使用信号量控制并发数量
    logger.info(f"使用异步IO处理 {len(chapter_files)} 个章节，最大并发数: {max_concurrent}")
    
    # 创建信号量控制并发数量
    semaphore = asyncio.Semaphore(max_concurrent)
    
    # 用于跟踪已存在的角色卡片
    existing_cards = {}
    
    async def process_and_save_immediately(chapter_data):
        """处理章节并立即保存结果"""
        async with semaphore:
            # 处理单个章节
            result = await process_single_chapter(
                chapter_data["character_info_file"],
                chapter_data["text_file"],
                output_dir
            )
            
            # 立即保存结果到汇总字典中
            chapter_name = os.path.basename(chapter_data["text_file"])
            results["results"][chapter_name] = result
            
            # 更新统计信息
            if result.get("success", False):
                results["successful_extractions"] += 1
                
                # 合并角色卡片到全局集合
                if "final_cards" in result:
                    results["all_character_cards"].update(result["final_cards"])
                    # 更新已存在的卡片，供下一章节使用
                    existing_cards.update(result["final_cards"])
                
                if "output_file" in result:
                    logger.info(f"章节 {chapter_name} 处理成功，结果已保存到: {result['output_file']}")
                else:
                    logger.info(f"章节 {chapter_name} 处理成功，但未保存文件")
            else:
                results["failed_extractions"] += 1
                error_msg = result.get("error", "未知错误")
                save_error = result.get("save_error", None)
                if save_error:
                    error_msg += f", 保存错误: {save_error}"
                logger.error(f"章节 {chapter_name} 处理失败: {error_msg}")
            
            return result
    
    # 创建任务列表
    tasks = [process_and_save_immediately(chapter_data) for chapter_data in chapter_files]
    
    # 等待所有任务完成
    await asyncio.gather(*tasks, return_exceptions=True)
    
    # 如果有失败的提取，将整体成功标志设为False
    if results["failed_extractions"] > 0:
        results["success"] = False
        results["error"] = f"有{results['failed_extractions']}个章节提取失败"
    
    # 按角色名保存最终的角色卡片
    if output_dir and results["all_character_cards"]:
        try:
            os.makedirs(output_dir, exist_ok=True)
            saved_files = []
            
            for character_name, character_card in results["all_character_cards"].items():
                # 清理角色名，确保文件名安全
                safe_character_name = character_name.replace("/", "_").replace("\\", "_").replace(":", "_").replace("*", "_").replace("?", "_").replace("\"", "_").replace("<", "_").replace(">", "_").replace("|", "_")
                output_file = os.path.join(output_dir, f"{safe_character_name}.json")
                output_file = output_file.replace(" ", "")
                
                try:
                    async with aiofiles.open(output_file, 'w', encoding='utf-8') as f:
                        content = json.dumps(character_card, ensure_ascii=False, indent=2, default=custom_json_serializer)
                        await f.write(content)
                    saved_files.append(output_file)
                    logger.info(f"角色卡片 {character_name} 已保存到: {output_file}")
                except Exception as e:
                    logger.error(f"保存角色卡片 {character_name} 失败: {str(e)}")
            
            results["saved_character_files"] = saved_files
            if saved_files:
                results["output_directory"] = output_dir
                logger.info(f"批量处理完成，共保存 {len(saved_files)} 个角色卡片文件到: {output_dir}")
                
        except Exception as e:
            results["save_error"] = f"保存角色卡片文件失败: {str(e)}"
            logger.error(f"保存角色卡片文件失败: {str(e)}")
    
    return results


if __name__ == "__main__":
    # 示例用法
    import argparse
    
    parser = argparse.ArgumentParser(description="角色卡提取工具")
    parser.add_argument("input", help="章节名称（如'第一章'）或文件路径")
    
    parser.add_argument("--output", "-o", help="输出目录", default="data/character_card")
    parser.add_argument("--processes", "-p", type=int, default=4, help="最大并发处理数量，默认为4")
    parser.add_argument("--batch", "-b", action="store_true", help="批量处理模式，input为目录路径")
    
    args = parser.parse_args()
    
    async def main():
        try:
            # 设置默认输出目录
            if not args.output:
                args.output = "data/character_card"
            
            if args.batch:
                # 批量处理模式
                chapter_files = scan_chapter_files(args.input)
                
                if not chapter_files:
                    print(f"在路径 {args.input} 中未找到章节文件对")
                    exit(1)
                
                print(f"找到 {len(chapter_files)} 个章节文件对")
                
                # 使用异步IO处理
                print(f"使用异步IO处理 {len(chapter_files)} 个章节 (最大并发数: {args.processes})")
                result = await batch_extract_character_cards(chapter_files, args.output, args.processes)
                
                # 输出结果
                if result.get("success", False):
                    print(f"批量处理成功! 成功处理 {result['successful_extractions']} 个章节")
                    print(f"共生成 {len(result['all_character_cards'])} 个角色卡片")
                    if "saved_character_files" in result:
                        print(f"角色卡片文件已保存到: {result['output_directory']}")
                        for file_path in result["saved_character_files"]:
                            print(f"  - {file_path}")
                else:
                    print(f"批量处理部分失败! 成功: {result['successful_extractions']}, 失败: {result['failed_extractions']}")
                    if "error" in result:
                        print(f"错误信息: {result['error']}")
            else:
                # 单章节处理模式
                if os.path.isfile(args.input) or os.path.isdir(args.input):
                    # 如果是文件路径，使用原有的扫描逻辑
                    chapter_files = scan_chapter_files(args.input)
                    
                    if not chapter_files:
                        print(f"在路径 {args.input} 中未找到章节文件对")
                        exit(1)
                    
                    # 使用第一个章节文件
                    chapter_data = chapter_files[0]
                    print(f"处理文件: {chapter_data['text_file']}")
                else:
                    # 如果是章节名称，自动查找文件（支持基于章节前缀的匹配）
                    try:
                        chapter_data = find_chapter_files(args.input)
                        print(f"找到章节文件: {args.input}")
                    except ValueError as e:
                        print(f"错误: {str(e)}")
                        exit(1)
                
                # 处理单个章节
                result = await extract_character_cards(
                    chapter_data["character_info_file"], 
                    chapter_data["text_file"], 
                    args.output
                )
                
                # 输出结果
                if result.get("success", False):
                    print("角色卡提取成功!")
                    if "saved_character_files" in result:
                        print(f"角色卡片文件已保存到: {result['output_directory']}")
                        for file_path in result["saved_character_files"]:
                            print(f"  - {file_path}")
                    print(f"共生成 {result.get('total_characters', 0)} 个角色卡片")
                else:
                    print("角色卡提取失败:")
                    print(result.get("error", "未知错误"))
                        
        except ValueError as e:
            print(f"错误: {str(e)}")
            exit(1)
        except Exception as e:
            print(f"处理过程中发生异常: {str(e)}")
            exit(1)
    
    # 运行主函数
    asyncio.run(main())