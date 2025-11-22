"""
爬虫模块的主入口文件
提供简单的接口来使用爬虫功能
"""

import sys
import os
import argparse

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
# 从src/services/crawling/main.py回退三级到项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.services.crawling.fetch_novel import get_clipboard_after_click


def crawl_command(args):
    """处理爬虫命令"""
    print(f"启动小说爬虫，URL: {args.url}")
    try:
        # 获取最大章节数，如果没有提供则使用默认值50
        max_chapters = args.chapters if args.chapters else 50
        get_clipboard_after_click(args.url, max_chapters)
        print("✅ 爬取完成!")
    except Exception as e:
        print(f"❌ 爬取失败: {str(e)}")


def main():
    """主函数，处理命令行参数"""
    parser = argparse.ArgumentParser(description="ShareNovel 小说爬虫工具")
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 爬虫命令
    crawl_parser = subparsers.add_parser('crawl', help='爬取小说内容')
    crawl_parser.add_argument("url", help="小说的URL")
    crawl_parser.add_argument('-o', '--output', help='输出目录', default='.')
    crawl_parser.add_argument('-c', '--chapters', type=int, help='要爬取的章节数量')
    
    args = parser.parse_args()
    
    if args.command == 'crawl':
        crawl_command(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()