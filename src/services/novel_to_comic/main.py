"""
小说转漫画故事板生成主入口
"""

import os
import sys
import argparse
import re
from typing import Optional, List

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from src.services.novel_to_comic.core.workflow import NovelToComicWorkflow
from src.services.novel_to_comic.models.data_models import ProcessingResult, ProcessingSummary
from src.services.novel_to_comic.utils.file_handler import FileHandler
from src.services.novel_to_comic.config.processing_config import (
    OUTPUT_DIR, ENABLE_PARALLEL_SCENE_SPLITTING, 
    MAX_SCENE_SPLITTING_CONCURRENT
)
from src.utils.logging_manager import get_logger, LogCategory

logger = get_logger(__name__, LogCategory.GENERAL)


class NovelToComicProcessor:
    """小说转漫画处理器"""
    
    def __init__(self, enable_parallel: Optional[bool] = None):
        self.logger = logger
        self.workflow = NovelToComicWorkflow(enable_parallel)
        self.file_handler = FileHandler()
        
        # 记录并行处理状态
        if enable_parallel is None:
            parallel_status = "启用" if ENABLE_PARALLEL_SCENE_SPLITTING else "禁用"
        else:
            parallel_status = "启用" if enable_parallel else "禁用"
        
        self.logger.info(f"并行场景分割: {parallel_status}")
        if self.workflow.enable_parallel:
            self.logger.info(f"最大并发数: {MAX_SCENE_SPLITTING_CONCURRENT}")
    
    def process_chapter(
        self, 
        chapter_file: str, 
        chapter_title: Optional[str] = None, 
        novel_type: str = "玄幻"
    ) -> ProcessingResult:
        """
        处理单个章节
        
        Args:
            chapter_file: 章节文件路径
            chapter_title: 章节标题，如果为None则从文件名提取
            novel_type: 小说类型
            
        Returns:
            处理结果
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(chapter_file):
                return ProcessingResult(
                    success=False,
                    errors=[f"文件不存在: {chapter_file}"]
                )
            
            # 提取章节标题
            if chapter_title is None:
                chapter_title = self.file_handler.get_file_name_without_extension(chapter_file)
            
            # 处理章节
            result = self.workflow.process_chapter(chapter_file, chapter_title, novel_type)
            
            # 保存结果
            output_path = self.workflow.save_result(result)
            
            # 创建处理摘要
            summary = ProcessingSummary(
                success=len(result.errors) == 0,
                total_segments=result.basic_stats.total_segments,
                total_scenes=result.basic_stats.total_scenes,
                total_storyboards=result.basic_stats.total_storyboards,
                processing_time=result.chapter_info.processing_time,
                error_count=len(result.errors)
            )
            
            return ProcessingResult(
                success=True,
                output_path=output_path,
                processing_summary=summary,
                errors=[error.error_message for error in result.errors]
            )
            
        except Exception as e:
            self.logger.error(f"处理章节失败: {e}")
            return ProcessingResult(
                success=False,
                errors=[str(e)]
            )
    
    def process_directory(
        self, 
        directory: str, 
        novel_type: str = "玄幻"
    ) -> ProcessingResult:
        """
        处理目录中的所有章节
        
        Args:
            directory: 章节目录路径
            novel_type: 小说类型
            
        Returns:
            处理结果
        """
        try:
            # 检查目录是否存在
            if not os.path.exists(directory):
                return ProcessingResult(
                    success=False,
                    errors=[f"目录不存在: {directory}"]
                )
            
            # 获取所有txt文件
            txt_files = self.file_handler.list_files_in_directory(directory, "*.txt")
            
            if not txt_files:
                return ProcessingResult(
                    success=False,
                    errors=[f"目录中没有找到txt文件: {directory}"]
                )
            
            # 智能排序：按章节顺序排序
            txt_files = self._sort_chapter_files(txt_files)
            
            print(f"发现 {len(txt_files)} 个章节文件，按顺序处理...")
            
            # 处理所有文件
            total_segments = 0
            total_scenes = 0
            total_storyboards = 0
            total_errors = []
            processed_files = []
            failed_files = []
            
            for i, txt_file in enumerate(txt_files, 1):
                # 提取章节标题
                chapter_title = self.file_handler.get_file_name_without_extension(txt_file)
                
                print(f"\n[{i}/{len(txt_files)}] 正在处理: {chapter_title}")
                print(f"文件路径: {txt_file}")
                
                result = self.process_chapter(txt_file, chapter_title, novel_type)
                
                if result.success:
                    processed_files.append(result.output_path)
                    if result.processing_summary:
                        total_segments += result.processing_summary.total_segments
                        total_scenes += result.processing_summary.total_scenes
                        total_storyboards += result.processing_summary.total_storyboards
                        total_errors.extend(result.errors)
                    
                    print(f"✓ 处理成功: {result.output_path}")
                    if result.processing_summary:
                        summary = result.processing_summary
                        print(f"  - 段落数: {summary.total_segments}")
                        print(f"  - 场景数: {summary.total_scenes}")
                        print(f"  - 故事板数: {summary.total_storyboards}")
                else:
                    failed_files.append(txt_file)
                    total_errors.extend(result.errors)
                    print(f"✗ 处理失败: {txt_file}")
                    for error in result.errors:
                        print(f"  错误: {error}")
            
            # 创建总体摘要
            summary = ProcessingSummary(
                success=len(failed_files) == 0,
                total_segments=total_segments,
                total_scenes=total_scenes,
                total_storyboards=total_storyboards,
                processing_time=f"批量处理完成",
                error_count=len(total_errors)
            )
            
            # 输出处理结果摘要
            print(f"\n{'='*50}")
            print("批量处理完成!")
            print(f"{'='*50}")
            print(f"总文件数: {len(txt_files)}")
            print(f"成功处理: {len(processed_files)}")
            print(f"处理失败: {len(failed_files)}")
            print(f"总段落数: {total_segments}")
            print(f"总场景数: {total_scenes}")
            print(f"总故事板数: {total_storyboards}")
            print(f"错误数量: {len(total_errors)}")
            
            if failed_files:
                print(f"\n失败的文件:")
                for failed_file in failed_files:
                    print(f"  - {failed_file}")
            
            return ProcessingResult(
                success=len(failed_files) == 0,
                output_path=f"已处理 {len(processed_files)} 个文件",
                processing_summary=summary,
                errors=total_errors
            )
            
        except Exception as e:
            self.logger.error(f"处理目录失败: {e}")
            return ProcessingResult(
                success=False,
                errors=[str(e)]
            )
    
    def _sort_chapter_files(self, files: List[str]) -> List[str]:
        """
        智能排序章节文件
        
        Args:
            files: 文件路径列表
            
        Returns:
            排序后的文件列表
        """
        try:
            # 按章节号排序
            sorted_files = sorted(files, key=self._extract_chapter_number)
            return sorted_files
        except:
            # 如果排序失败，返回原始顺序
            return files
    
    def _extract_chapter_number(self, filepath: str) -> int:
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
                return self._chinese_number_to_int(chapter_str)
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


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="小说转漫画故事板生成工具")
    parser.add_argument("-f", "--file", help="单个章节文件路径")
    parser.add_argument("-d", "--directory", help="章节目录路径")
    parser.add_argument("-t", "--title", help="章节标题（仅在使用-f时有效）")
    parser.add_argument("-n", "--novel-type", default="玄幻", help="小说类型（默认：玄幻）")
    parser.add_argument("--auto", action="store_true", help="自动模式：处理data/cleaned_novel目录中的所有章节")
    parser.add_argument("--parallel", action="store_true", help="启用并行场景分割")
    parser.add_argument("--no-parallel", action="store_true", help="禁用并行场景分割")
    
    args = parser.parse_args()
    
    # 确定是否启用并行处理
    enable_parallel = None
    if args.parallel and args.no_parallel:
        print("错误：不能同时指定 --parallel 和 --no-parallel")
        return
    elif args.parallel:
        enable_parallel = True
    elif args.no_parallel:
        enable_parallel = False
    
    # 创建处理器
    processor = NovelToComicProcessor(enable_parallel)
    
    # 确保输出目录存在
    processor.file_handler.ensure_directory_exists(OUTPUT_DIR)
    
    if args.auto:
        # 自动模式：处理默认目录
        default_dir = "data/cleaned_novel"
        print(f"自动模式：处理目录 {default_dir} 中的所有章节")
        result = processor.process_directory(default_dir, args.novel_type)
    elif args.file:
        # 处理单个文件
        result = processor.process_chapter(args.file, args.title, args.novel_type)
    elif args.directory:
        # 处理目录
        result = processor.process_directory(args.directory, args.novel_type)
    else:
        print("使用方法:")
        print("1. 处理单个章节:")
        print("   python -m src.services.novel_to_comic.main -f <章节文件路径> -t <章节标题>")
        print("2. 批量处理目录:")
        print("   python -m src.services.novel_to_comic.main -d <章节目录路径>")
        print("3. 自动模式（处理data/cleaned_novel目录）:")
        print("   python -m src.services.novel_to_comic.main --auto")
        print("\n并行处理选项:")
        print("  --parallel     启用并行场景分割（最多5个并发）")
        print("  --no-parallel  禁用并行场景分割")
        print("\n使用 -h 查看更多参数信息")
        return
    
    # 输出结果
    if result.success:
        if not args.auto and not args.directory:  # 单文件处理
            print("处理成功!")
            print(f"输出路径: {result.output_path}")
            
            if result.processing_summary:
                summary = result.processing_summary
                print(f"总段落数: {summary.total_segments}")
                print(f"总场景数: {summary.total_scenes}")
                print(f"总故事板数: {summary.total_storyboards}")
                print(f"错误数量: {summary.error_count}")
            
            if result.errors:
                print("警告信息:")
                for error in result.errors:
                    print(f"  - {error}")
    else:
        print("处理失败!")
        for error in result.errors:
            print(f"错误: {error}")


if __name__ == "__main__":
    main()
