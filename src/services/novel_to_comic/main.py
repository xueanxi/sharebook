"""
小说转漫画故事板生成主入口
"""

import os
import sys
import argparse
from typing import Optional

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from src.services.novel_to_comic.core.workflow import NovelToComicWorkflow
from src.services.novel_to_comic.models.data_models import ProcessingResult, ProcessingSummary
from src.services.novel_to_comic.utils.file_handler import FileHandler
from src.services.novel_to_comic.config.processing_config import OUTPUT_DIR
from src.utils.logging_manager import get_logger, LogCategory

logger = get_logger(__name__, LogCategory.GENERAL)


class NovelToComicProcessor:
    """小说转漫画处理器"""
    
    def __init__(self):
        self.logger = logger
        self.workflow = NovelToComicWorkflow()
        self.file_handler = FileHandler()
    
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
            
            # 处理所有文件
            total_segments = 0
            total_scenes = 0
            total_storyboards = 0
            total_errors = []
            processed_files = []
            
            for txt_file in txt_files:
                self.logger.info(f"处理文件: {txt_file}")
                result = self.process_chapter(txt_file, novel_type=novel_type)
                
                if result.success:
                    processed_files.append(result.output_path)
                    if result.processing_summary:
                        total_segments += result.processing_summary.total_segments
                        total_scenes += result.processing_summary.total_scenes
                        total_storyboards += result.processing_summary.total_storyboards
                        total_errors.extend(result.errors)
                else:
                    total_errors.extend(result.errors)
            
            # 创建总体摘要
            summary = ProcessingSummary(
                success=len(total_errors) == 0,
                total_segments=total_segments,
                total_scenes=total_scenes,
                total_storyboards=total_storyboards,
                processing_time=f"批量处理完成",
                error_count=len(total_errors)
            )
            
            return ProcessingResult(
                success=len(total_errors) == 0,
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


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="小说转漫画故事板生成工具")
    parser.add_argument("-f", "--file", help="单个章节文件路径")
    parser.add_argument("-d", "--directory", help="章节目录路径")
    parser.add_argument("-t", "--title", help="章节标题（仅在使用-f时有效）")
    parser.add_argument("-n", "--novel-type", default="玄幻", help="小说类型（默认：玄幻）")
    
    args = parser.parse_args()
    
    # 创建处理器
    processor = NovelToComicProcessor()
    
    # 确保输出目录存在
    processor.file_handler.ensure_directory_exists(OUTPUT_DIR)
    
    if args.file:
        # 处理单个文件
        result = processor.process_chapter(args.file, args.title, args.novel_type)
    elif args.directory:
        # 处理目录
        result = processor.process_directory(args.directory, args.novel_type)
    else:
        print("请指定要处理的文件或目录")
        print("使用 -h 查看帮助信息")
        return
    
    # 输出结果
    if result.success:
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