"""
角色图片生成命令行接口

提供命令行工具来生成角色图片.
"""

import argparse
import sys
import os
from typing import List

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.insert(0, project_root)

from src.services.character_image_generation.character_image_generator import CharacterImageGenerator
from config.logging_config import get_logger

logger = get_logger(__name__)


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="角色图片生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成所有角色图片
  python main.py --all
  
  # 生成指定角色图片
  python main.py --name "搬山宗宗主"
  
  # 批量生成多个角色图片
  python main.py --names "搬山宗宗主,叶师弟,灵儿"
  
  # 指定输出目录
  python main.py --all --output "custom_output"
  
  # 设置批处理大小
  python main.py --all --batch-size 2
  
  # 强制重新生成已有图片的角色
  python main.py --all --force
  
  # 列出所有角色
  python main.py --list
  
  # 测试ComfyUI连接
  python main.py --test
        """
    )
    
    # 角色选择参数
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--all", 
        action="store_true",
        help="生成所有角色图片"
    )
    group.add_argument(
        "--name", 
        type=str,
        help="生成指定角色图片"
    )
    group.add_argument(
        "--names", 
        type=str,
        help="批量生成多个角色图片, 用逗号分隔"
    )
    group.add_argument(
        "--list", 
        action="store_true",
        help="列出所有角色名称"
    )
    group.add_argument(
        "--test", 
        action="store_true",
        help="测试ComfyUI连接"
    )
    
    # 可选参数
    parser.add_argument(
        "--output", 
        type=str,
        default="data/characters/image",
        help="图片输出目录 (默认: data/characters/image)"
    )
    
    parser.add_argument(
        "--csv", 
        type=str,
        default="data/characters/characters.csv",
        help="角色数据CSV文件路径 (默认: data/characters/characters.csv)"
    )
    
    parser.add_argument(
        "--workflow", 
        type=str,
        default="comfyui/novel_t2I_flux.json",
        help="ComfyUI工作流模板文件路径 (默认: comfyui/novel_t2I_flux.json)"
    )
    
    parser.add_argument(
        "--batch-size", 
        type=int,
        default=1,
        help="批处理大小 (默认: 1)"
    )
    
    parser.add_argument(
        "--force", 
        action="store_true",
        help="强制重新生成已有图片的角色"
    )
    
    return parser.parse_args()


def list_characters(generator: CharacterImageGenerator):
    """列出所有角色"""
    characters = generator.get_character_list()
    print("可用角色列表:")
    for i, name in enumerate(characters, 1):
        print(f"{i:2d}. {name}")
    print(f"\n共 {len(characters)} 个角色")


def test_connection(generator: CharacterImageGenerator):
    """测试ComfyUI连接"""
    print("正在测试ComfyUI连接...")
    if generator.test_connection():
        print("✓ ComfyUI连接成功")
        return True
    else:
        print("✗ ComfyUI连接失败")
        return False


def generate_all_characters(generator: CharacterImageGenerator, batch_size: int, force: bool):
    """生成所有角色图片"""
    print(f"开始生成所有角色图片 (批处理大小: {batch_size})")
    if force:
        print("注意: 将强制重新生成已有图片的角色")
    
    results = generator.generate_all_characters(batch_size=batch_size, skip_existing=not force)
    
    print("\n生成结果:")
    success_count = 0
    for name, paths in results.items():
        if paths:
            print(f"✓ {name}: {len(paths)} 张图片")
            success_count += 1
        else:
            print(f"✗ {name}: 生成失败")
    
    print(f"\n完成! 成功生成 {success_count} 个角色的图片")


def generate_single_character(generator: CharacterImageGenerator, name: str, batch_size: int):
    """生成单个角色图片"""
    print(f"正在生成角色 '{name}' 的图片 (批处理大小: {batch_size})")
    
    try:
        paths = generator.generate_single_character(name, batch_size)
        print(f"✓ 成功生成 {len(paths)} 张图片:")
        for path in paths:
            print(f"  - {path}")
    except Exception as e:
        print(f"✗ 生成失败: {str(e)}")


def generate_multiple_characters(generator: CharacterImageGenerator, names: List[str], batch_size: int):
    """批量生成多个角色图片"""
    print(f"正在批量生成 {len(names)} 个角色的图片 (批处理大小: {batch_size})")
    
    results = generator.batch_generate(names, batch_size)
    
    print("\n生成结果:")
    success_count = 0
    for name, paths in results.items():
        if paths:
            print(f"✓ {name}: {len(paths)} 张图片")
            success_count += 1
        else:
            print(f"✗ {name}: 生成失败")
    
    print(f"\n完成! 成功生成 {success_count}/{len(names)} 个角色的图片")


def main():
    """主函数"""
    args = parse_arguments()
    
    # 创建生成器实例
    try:
        generator = CharacterImageGenerator(
            csv_file_path=args.csv,
            output_base_dir=args.output,
            workflow_template=args.workflow
        )
    except Exception as e:
        print(f"初始化失败: {str(e)}")
        sys.exit(1)
    
    # 根据参数执行相应操作
    if args.list:
        list_characters(generator)
    elif args.test:
        success = test_connection(generator)
        sys.exit(0 if success else 1)
    elif args.all:
        generate_all_characters(generator, args.batch_size, args.force)
    elif args.name:
        generate_single_character(generator, args.name, args.batch_size)
    elif args.names:
        names = [name.strip().strip('"\'') for name in args.names.split(",")]
        generate_multiple_characters(generator, names, args.batch_size)


if __name__ == "__main__":
    main()