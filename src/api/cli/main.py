"""
ShareNovel 命令行接口
提供简单的命令行界面来使用ShareNovel的功能
"""

import argparse
import os
import sys
from typing import List, Optional

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.services.extraction.main import extract_novel_information, batch_extract_novel_info
from src.services.crawling.fetch_novel import get_clipboard_after_click


def extract_command(args):
    """处理信息提取命令"""
    if args.file:
        # 单文件提取
        result = extract_novel_information(
            args.file, 
            args.output, 
            parallel=args.parallel, 
            parallel_method=args.parallel_method
        )
        if result.get("success", False):
            print("✅ 信息提取成功!")
            if "output_file" in result:
                print(f"结果已保存到: {result['output_file']}")
            if args.parallel:
                print(f"使用 {args.parallel_method} 并行处理模式")
        else:
            print("❌ 信息提取失败:")
            print(result.get("error", "未知错误"))
    elif args.directory:
        # 批量提取
        txt_files = [os.path.join(args.directory, f) for f in os.listdir(args.directory) 
                     if f.endswith('.txt')]
        if not txt_files:
            print(f"在目录 {args.directory} 中没有找到.txt文件")
            return
        
        result = batch_extract_novel_info(txt_files, args.output, args.parallel, args.parallel_method)
        print(f"处理完成: {result['successful_extractions']}/{result['total_files']} 个文件成功")
        if result.get("failed_extractions", 0) > 0:
            print(f"有 {result['failed_extractions']} 个文件处理失败")
        if args.parallel:
            print(f"使用 {args.parallel_method} 并行处理模式")
    else:
        print("请指定要处理的文件或目录")


def crawl_command(args):
    """处理爬虫命令"""
    print("启动小说爬虫...")
    try:
        get_clipboard_after_click()
        print("✅ 爬取完成!")
    except Exception as e:
        print(f"❌ 爬取失败: {str(e)}")


def main():
    """主函数，处理命令行参数"""
    parser = argparse.ArgumentParser(description="ShareNovel - 小说处理和分析工具")
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 信息提取命令
    extract_parser = subparsers.add_parser('extract', help='从小说文件中提取信息')
    extract_group = extract_parser.add_mutually_exclusive_group(required=True)
    extract_group.add_argument('-f', '--file', help='要处理的小说文件路径')
    extract_group.add_argument('-d', '--directory', help='包含小说文件的目录路径')
    extract_parser.add_argument('-o', '--output', help='输出目录', default='data/output')
    
    # 并行处理选项
    extract_parser.add_argument('--parallel', action='store_true', help='启用并行处理')
    extract_parser.add_argument('--parallel-method', choices=['langgraph', 'threadpool'], 
                               default='langgraph', help='并行处理方法 (默认: langgraph)')
    
    # 爬虫命令
    crawl_parser = subparsers.add_parser('crawl', help='爬取小说内容')
    
    args = parser.parse_args()
    
    if args.command == 'extract':
        extract_command(args)
    elif args.command == 'crawl':
        crawl_command(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()