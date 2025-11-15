"""
角色提取主入口脚本
"""

import argparse
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

# 尝试导入LangGraph版本，如果失败则使用简化版

from workflow import CharacterExtractionWorkflow
USE_LANGGRAPH = True



def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="小说角色提取工具")
    parser.add_argument(
        "--config",
        type=str,
        default="src/services/extraction_character/config.yaml",
        help="配置文件路径"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="重置处理进度"
    )
    parser.add_argument(
        "--progress",
        action="store_true",
        help="显示当前进度"
    )
    parser.add_argument(
        "--novel-path",
        type=str,
        help="小说文件目录路径（覆盖配置文件中的设置）"
    )
    parser.add_argument(
        "--csv-path",
        type=str,
        help="CSV文件输出路径（覆盖配置文件中的设置）"
    )
    
    args = parser.parse_args()
    
    try:
        # 检查配置文件是否存在
        if not os.path.exists(args.config):
            print(f"配置文件不存在: {args.config}")
            print("将创建默认配置文件...")
        
        # 创建工作流实例
        workflow = CharacterExtractionWorkflow(args.config)
        
        # 如果需要覆盖配置
        if args.novel_path or args.csv_path:
            config = workflow.config_manager.get_config()
            if args.novel_path:
                config['extraction']['paths']['novel_path'] = args.novel_path
            if args.csv_path:
                config['extraction']['paths']['csv_path'] = args.csv_path
            workflow.config_manager.config = config
        
        # 显示进度
        if args.progress:
            progress = workflow.get_progress()
            print(f"总章节数: {progress['total_chapters']}")
            print(f"已处理章节: {progress['processed_chapters']}")
            print(f"处理进度: {progress['progress_percentage']:.1f}%")
            if progress['current_chapter']:
                print(f"当前章节: {progress['current_chapter']}")
            return
        
        # 运行工作流
        print("开始角色提取...")
        result = workflow.run(reset_progress=args.reset)
        
        if result["success"]:
            print("角色提取完成!")
            print(f"处理的章节: {len(result['processed_chapters'])}")
            print(f"输出文件: {result['csv_path']}")
        else:
            print(f"角色提取失败: {result['error']}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"程序执行异常: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
