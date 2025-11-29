"""
漫画图片生成功能使用示例
展示单角色、多角色图片生成和章节处理功能的使用方法
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from sharebook.services.comic_image_generation import ComicImageGeneration
from sharebook.utils.logging_manager import get_module_logger, LogModule

logger = get_logger(LogModule.COMIC_IMAGE_GENERATION)


def example_single_character():
    """单角色图片生成示例"""
    print("=== 单角色图片生成示例 ===")
    
    # 创建接口实例
    comic_gen = ComicImageGeneration()
    
    # 生成单角色图片
    prompt = "一个英俊的年轻男子，黑发，穿着现代服装，站在城市街道上，动漫风格"
    reference_image = "data/characters/image/搬山宗宗主/image_001.png"  # 可选
    
    try:
        image_paths = comic_gen.generate_image(
            prompt=prompt,
            save_dir="output/single_character",
            reference_image=reference_image,
            batch_size=1
        )
        print(f"单角色图片生成成功，保存路径: {image_paths}")
    except Exception as e:
        print(f"单角色图片生成失败: {str(e)}")


def example_multi_character():
    """多角色图片生成示例"""
    print("=== 多角色图片生成示例 ===")
    
    # 创建接口实例
    comic_gen = ComicImageGeneration()
    
    # 生成多角色图片
    prompt = "男女主角背靠背站立，男性持盾，女性握剑，气氛严肃，背景为海洋"
    ref_image_1 = "data/characters/image/搬山宗宗主/image_001.png"  # 可选
    ref_image_2 = "data/characters/image/搬山宗宗主/image_001.png"  # 可选
    
    try:
        image_paths = comic_gen.generate_multi_character_image(
            prompt=prompt,
            ref_image_1=ref_image_1,
            ref_image_2=ref_image_2,
            save_dir="output/multi_character",
            batch_size=1
        )
        print(f"多角色图片生成成功，保存路径: {image_paths}")
    except Exception as e:
        print(f"多角色图片生成失败: {str(e)}")


def example_chapter_processing():
    """章节处理示例"""
    print("=== 章节处理示例 ===")
    
    # 创建接口实例
    comic_gen = ComicImageGeneration()
    
    # 处理单个章节
    chapter_json_path = "data/storyboards_prompt/第一章.json"
    
    try:
        chapter_results = comic_gen.process_chapter(
            chapter_json_path=chapter_json_path,
            save_dir="output/chapters"
        )
        print(f"章节处理成功，结果: {chapter_results}")
    except Exception as e:
        print(f"章节处理失败: {str(e)}")


def example_all_chapters_processing():
    """所有章节处理示例"""
    print("=== 所有章节处理示例 ===")
    
    # 创建接口实例
    comic_gen = ComicImageGeneration()
    
    try:
        # 处理所有章节
        all_results = comic_gen.process_all_chapters(
            storyboards_prompt_dir="data/storyboards_prompt/",
            save_dir="output/all_chapters"
        )
        print(f"所有章节处理成功，结果: {all_results}")
    except Exception as e:
        print(f"所有章节处理失败: {str(e)}")


def example_batch_generation():
    """批量生成示例"""
    print("=== 批量生成示例 ===")
    
    # 创建接口实例
    comic_gen = ComicImageGeneration()
    
    # 批量提示词
    prompts = [
        "主角站在山巅，俯瞰下方云海，白袍飘飘",
        "主角与神秘人对峙，气氛紧张",
        "激烈的战斗场面，剑光闪烁"
    ]
    
    try:
        image_paths = comic_gen.generate_multiple_images(
            prompts=prompts,
            save_dir="output/batch",
            reference_image="data/characters/image/搬山宗宗主/image_001.png",
            batch_size=1
        )
        print(f"批量生成成功，保存路径: {image_paths}")
    except Exception as e:
        print(f"批量生成失败: {str(e)}")


def main():
    """主函数"""
    print("漫画图片生成功能使用示例")
    print("请确保ComfyUI服务器正在运行，并根据需要修改示例中的参考图片路径")
    print()
    
    # 取消注释以运行不同的示例
    # example_single_character()
    # example_multi_character()
    # example_chapter_processing()
    # example_all_chapters_processing()
    # example_batch_generation()
    
    print("使用示例已准备就绪，请取消注释相应的示例函数来运行")


if __name__ == "__main__":
    main()