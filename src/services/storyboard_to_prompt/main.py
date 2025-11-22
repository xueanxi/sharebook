"""
故事板到提示词转换服务入口脚本
"""
import argparse
import logging
import sys,os
from pathlib import Path
from typing import Optional

# 添加项目根目录到路径
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
print(f"项目根目录: {root_path}")    
sys.path.append(root_path)

from config.logging_config import get_logger
from .storyboard_to_prompt_processor import StoryboardToPromptProcessor

# 设置日志
logger = get_logger(__name__)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='故事板到提示词转换服务',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 处理所有章节
  python main.py --all
  
  # 处理单个章节
  python main.py --chapter "data/storyboards/第一章 遇强则强_storyboards.json"
  
  # 列出所有章节
  python main.py --list
  
  # 验证故事板文件
  python main.py --validate "data/storyboards/第一章 遇强则强_storyboards.json"
  
  # 清理旧备份
  python main.py --clean-backups --keep 5
  
  # 导出处理报告
  python main.py --export-report
        """
    )
    
    # 基本参数
    parser.add_argument('--config', type=str, 
                       help='配置文件路径')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='详细输出')
    
    # 处理选项
    processing_group = parser.add_mutually_exclusive_group()
    processing_group.add_argument('--all', action='store_true',
                                 help='处理所有章节')
    processing_group.add_argument('--chapter', type=str,
                                 help='处理指定章节的故事板文件')
    processing_group.add_argument('--list', action='store_true',
                                 help='列出所有可用章节')
    processing_group.add_argument('--validate', type=str,
                                 help='验证故事板文件格式')
    
    # 维护选项
    parser.add_argument('--clean-backups', action='store_true',
                       help='清理旧备份文件')
    parser.add_argument('--keep', type=int, default=10,
                       help='保留备份文件数量 (默认: 10)')
    parser.add_argument('--export-report', action='store_true',
                       help='导出处理报告')
    
    # 处理选项
    parser.add_argument('--no-batch-optimize', action='store_true',
                       help='跳过批量优化')
    parser.add_argument('--output', type=str,
                       help='指定输出目录')
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # 创建处理器
        processor = StoryboardToPromptProcessor(args.config)
        
        # 处理命令
        if args.all:
            process_all_chapters(processor, not args.no_batch_optimize)
        elif args.chapter:
            process_single_chapter(processor, args.chapter)
        elif args.list:
            list_chapters(processor)
        elif args.validate:
            validate_file(processor, args.validate)
        elif args.clean_backups:
            clean_backups(processor, args.keep)
        elif args.export_report:
            export_report(processor)
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        logger.info("用户中断操作")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序执行失败: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def process_all_chapters(processor: StoryboardToPromptProcessor, optimize_batch: bool = True):
    """处理所有章节"""
    logger.info("开始处理所有章节...")
    
    # 获取章节列表
    chapters = processor.get_chapter_list()
    if not chapters:
        print("没有找到故事板文件")
        return
    
    print(f"找到 {len(chapters)} 个章节:")
    for chapter in chapters:
        status = "✓" if chapter['is_valid'] else "✗"
        print(f"  {status} {chapter['file_name']}")
    
    # 确认处理
    if not confirm_action("确定要处理所有章节吗？"):
        return
    
    # 处理所有章节
    result = processor.process_all_chapters(optimize_batch)
    
    # 显示结果
    print("\n处理结果:")
    print(f"  总章节数: {result['total_chapters']}")
    print(f"  成功处理: {result['successful_chapters']}")
    print(f"  处理失败: {result['failed_chapters']}")
    print(f"  生成提示词: {result['total_prompts']}")
    print(f"  处理时间: {result['processing_time']:.2f}秒")
    
    if result['errors']:
        print("\n错误信息:")
        for error in result['errors']:
            print(f"  - {error}")


def process_single_chapter(processor: StoryboardToPromptProcessor, chapter_path: str):
    """处理单个章节"""
    file_path = Path(chapter_path)
    
    if not file_path.exists():
        print(f"文件不存在: {chapter_path}")
        return
    
    logger.info(f"处理章节: {file_path}")
    
    # 验证文件
    is_valid, errors = processor.validate_storyboard_file(file_path)
    if not is_valid:
        print("文件验证失败:")
        for error in errors:
            print(f"  - {error}")
        return
    
    # 处理章节
    result = processor.process_chapter(file_path)
    
    if result['success']:
        print(f"处理成功:")
        print(f"  生成提示词: {result['prompt_count']}")
        print(f"  输出文件: {result.get('output_path', 'N/A')}")
    else:
        print(f"处理失败: {result.get('error', '未知错误')}")


def list_chapters(processor: StoryboardToPromptProcessor):
    """列出所有章节"""
    chapters = processor.get_chapter_list()
    
    if not chapters:
        print("没有找到故事板文件")
        return
    
    print(f"找到 {len(chapters)} 个章节:")
    print("-" * 80)
    print(f"{'状态':<4} {'文件名':<40} {'章节标题':<20} {'场景数':<8} {'文件大小':<10}")
    print("-" * 80)
    
    for chapter in chapters:
        status = "✓" if chapter['is_valid'] else "✗"
        file_name = chapter['file_name'][:38] + ".." if len(chapter['file_name']) > 40 else chapter['file_name']
        chapter_title = chapter.get('chapter_title', 'N/A')[:18] + ".." if len(chapter.get('chapter_title', '')) > 20 else chapter.get('chapter_title', 'N/A')
        total_scenes = chapter.get('total_scenes', 'N/A')
        file_size = format_file_size(chapter['file_size'])
        
        print(f"{status:<4} {file_name:<40} {chapter_title:<20} {total_scenes:<8} {file_size:<10}")
    
    print("-" * 80)


def validate_file(processor: StoryboardToPromptProcessor, file_path: str):
    """验证故事板文件"""
    path = Path(file_path)
    
    if not path.exists():
        print(f"文件不存在: {file_path}")
        return
    
    print(f"验证文件: {path}")
    
    is_valid, errors = processor.validate_storyboard_file(path)
    
    if is_valid:
        print("✓ 文件格式正确")
    else:
        print("✗ 文件格式有误:")
        for error in errors:
            print(f"  - {error}")


def clean_backups(processor: StoryboardToPromptProcessor, keep_count: int):
    """清理备份文件"""
    print(f"清理备份文件，保留最新 {keep_count} 个...")
    
    if not confirm_action(f"确定要清理旧备份文件吗？将保留最新 {keep_count} 个备份。"):
        return
    
    processor.clean_old_backups(keep_count)
    print("备份清理完成")


def export_report(processor: StoryboardToPromptProcessor):
    """导出处理报告"""
    print("导出处理报告...")
    
    success = processor.export_processing_report()
    
    if success:
        print("✓ 处理报告已导出")
    else:
        print("✗ 导出处理报告失败")


def confirm_action(message: str) -> bool:
    """确认操作"""
    try:
        response = input(f"{message} (y/N): ").strip().lower()
        return response in ['y', 'yes', '是']
    except KeyboardInterrupt:
        return False


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


if __name__ == '__main__':
    main()
