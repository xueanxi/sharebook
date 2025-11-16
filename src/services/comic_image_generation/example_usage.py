"""
漫画图片生成接口使用示例
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from src.services.comic_image_generation import ComicImageGeneration
from config.logging_config import get_logger

logger = get_logger(__name__)


def example_basic_usage():
    """基本使用示例"""
    # 创建接口实例
    comic_gen = ComicImageGeneration()
    
    # 基本参数
    prompt = "一个美丽的年轻女子，长发，穿着传统服装，站在樱花树下，动漫风格"
    reference_image = "path/to/your/reference/image.jpg"  # 替换为您的参考图片路径
    save_dir = "output/comic_images"
    
    # 生成图片
    image_paths = comic_gen.generate_image(
        prompt=prompt,
        save_dir=save_dir,
        reference_image=reference_image,
        batch_size=2,  # 生成2张图片
    )
    
    print(f"生成的图片保存在: {image_paths}")



if __name__ == "__main__":
    print("漫画图片生成接口使用示例")
    print("请根据需要修改示例中的参考图片路径和保存目录")
    
    # 取消注释以运行不同的示例
    # example_basic_usage()
    # example_character_variations()
    # example_batch_generation()