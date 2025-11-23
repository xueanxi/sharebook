"""
漫画图片生成主入口
"""

import os
import sys
import argparse
from typing import Optional, List

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from src.services.comic_image_generation import ComicImageGeneration
from src.utils.logging_manager import get_module_logger, LogModule
from src.utils.text_processing.chapter_sorter import ChapterSorter

logger = get_module_logger(LogModule.MAIN)
logger.setLevel('DEBUG')


class ComicImageProcessor:
    """漫画图片生成处理器"""
    
    def __init__(self):
        self.logger = logger
        self.comic_gen = ComicImageGeneration()
        
    def generate_single_image(
        self, 
        prompt: str, 
        reference_image: Optional[str] = None,
        save_dir: Optional[str] = None,
        batch_size: Optional[int] = None
    ) -> bool:
        """
        生成单角色图片
        
        Args:
            prompt: 提示词
            reference_image: 参考图片路径
            save_dir: 保存目录
            batch_size: 批处理大小
            
        Returns:
            是否成功
        """
        try:
            self.logger.info("开始生成单角色图片...")
            
            # 测试连接
            if not self.comic_gen.test_connection():
                self.logger.error("无法连接到ComfyUI服务器，请确保ComfyUI正在运行")
                return False
            
            # 从配置文件获取默认值
            generation_config = self.comic_gen.config.get("comic_image_generation", {}).get("generation", {})
            default_batch_size = generation_config.get("default_batch_size", 1)
            
            # 使用传入参数或默认值
            batch_size = batch_size if batch_size is not None else default_batch_size
            
            # 生成图片
            image_paths = self.comic_gen.generate_image(
                prompt=prompt,
                save_dir=save_dir,
                reference_image=reference_image,
                batch_size=batch_size
            )
            
            self.logger.info(f"单角色图片生成成功，生成 {len(image_paths)} 张图片")
            for i, path in enumerate(image_paths, 1):
                self.logger.info(f"  图片 {i}: {path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"生成单角色图片失败: {str(e)}")
            return False
    
    def generate_multi_character_image(
        self, 
        prompt: str, 
        ref_image_1: Optional[str] = None,
        ref_image_2: Optional[str] = None,
        save_dir: Optional[str] = None,
        batch_size: Optional[int] = None
    ) -> bool:
        """
        生成多角色图片
        
        Args:
            prompt: 提示词
            ref_image_1: 参考图片1路径
            ref_image_2: 参考图片2路径
            save_dir: 保存目录
            batch_size: 批处理大小
            
        Returns:
            是否成功
        """
        try:
            self.logger.info("开始生成多角色图片...")
            
            # 测试连接
            if not self.comic_gen.test_connection():
                self.logger.error("无法连接到ComfyUI服务器，请确保ComfyUI正在运行")
                return False
            
            # 从配置文件获取默认值
            generation_config = self.comic_gen.config.get("comic_image_generation", {}).get("generation", {})
            default_batch_size = generation_config.get("default_batch_size", 1)
            
            # 使用传入参数或默认值
            batch_size = batch_size if batch_size is not None else default_batch_size
            
            # 生成图片
            image_paths = self.comic_gen.generate_multi_character_image(
                prompt=prompt,
                ref_image_1=ref_image_1,
                ref_image_2=ref_image_2,
                save_dir=save_dir,
                batch_size=batch_size
            )
            
            self.logger.info(f"多角色图片生成成功，生成 {len(image_paths)} 张图片")
            for i, path in enumerate(image_paths, 1):
                self.logger.info(f"  图片 {i}: {path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"生成多角色图片失败: {str(e)}")
            return False
    
    def process_chapter(
        self, 
        chapter_file: str, 
        save_dir: Optional[str] = None
    ) -> bool:
        """
        处理单个章节
        
        Args:
            chapter_file: 章节JSON文件路径
            save_dir: 保存目录
            
        Returns:
            是否成功
        """
        try:
            self.logger.info(f"开始处理章节: {chapter_file}")
            
            # 去掉可能的引号
            chapter_file = chapter_file.strip('"\'')
            
            # 处理相对路径，转换为绝对路径
            if not os.path.isabs(chapter_file):
                chapter_file = os.path.abspath(chapter_file)
            
            # 标准化路径
            chapter_file = os.path.normpath(chapter_file)
            
            if not os.path.exists(chapter_file):
                self.logger.error(f"章节文件不存在: {chapter_file}")
                return False
            
            # 测试连接
            if not self.comic_gen.test_connection():
                self.logger.error("无法连接到ComfyUI服务器，请确保ComfyUI正在运行")
                return False
            
            # 处理章节
            chapter_results = self.comic_gen.process_chapter(
                chapter_json_path=chapter_file,
                save_dir=save_dir
            )
            
            # 统计结果
            total_scenes = len(chapter_results)
            total_images = sum(len(images) for images in chapter_results.values())
            
            self.logger.info(f"章节处理完成:")
            self.logger.info(f"  总场景数: {total_scenes}")
            self.logger.info(f"  总图片数: {total_images}")
            
            for scene_id, image_paths in chapter_results.items():
                self.logger.info(f"  {scene_id}: {len(image_paths)} 张图片")
                for path in image_paths:
                    self.logger.info(f"    - {path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"处理章节失败: {str(e)}")
            return False
    
    def process_all_chapters(
        self, 
        storyboards_prompt_dir: Optional[str] = None,
        save_dir: Optional[str] = None
    ) -> bool:
        """
        处理所有章节
        
        Args:
            storyboards_prompt_dir: 故事板提示词目录
            save_dir: 保存目录
            
        Returns:
            是否成功
        """
        try:
            # 使用传入的目录或配置文件中的默认值
            if storyboards_prompt_dir is None:
                storyboards_prompt_dir = self.comic_gen.storyboards_prompt_dir
            
            # 处理相对路径，转换为绝对路径
            if not os.path.isabs(storyboards_prompt_dir):
                storyboards_prompt_dir = os.path.abspath(storyboards_prompt_dir)
            
            # 标准化路径
            storyboards_prompt_dir = os.path.normpath(storyboards_prompt_dir)
            
            self.logger.info(f"开始处理所有章节，目录: {storyboards_prompt_dir}")
            
            # 检查目录是否存在
            if not os.path.exists(storyboards_prompt_dir):
                self.logger.error(f"故事板提示词目录不存在: {storyboards_prompt_dir}")
                return False
            
            # 测试连接
            if not self.comic_gen.test_connection():
                self.logger.error("无法连接到ComfyUI服务器，请确保ComfyUI正在运行")
                return False
            
            # 处理所有章节
            all_results = self.comic_gen.process_all_chapters(
                storyboards_prompt_dir=storyboards_prompt_dir,
                save_dir=save_dir
            )
            
            # 统计结果
            total_chapters = len(all_results)
            total_scenes = sum(len(chapter_results) for chapter_results in all_results.values())
            total_images = sum(
                len(images) 
                for chapter_results in all_results.values() 
                for images in chapter_results.values()
            )
            
            self.logger.info(f"所有章节处理完成:")
            self.logger.info(f"  总章节数: {total_chapters}")
            self.logger.info(f"  总场景数: {total_scenes}")
            self.logger.info(f"  总图片数: {total_images}")
            
            for chapter_title, chapter_results in all_results.items():
                chapter_scenes = len(chapter_results)
                chapter_images = sum(len(images) for images in chapter_results.values())
                self.logger.info(f"  {chapter_title}: {chapter_scenes} 场景, {chapter_images} 张图片")
            
            return True
            
        except Exception as e:
            self.logger.error(f"处理所有章节失败: {str(e)}")
            return False
    
    def test_connection(self) -> bool:
        """
        测试ComfyUI连接
        
        Returns:
            连接是否成功
        """
        try:
            self.logger.info("测试ComfyUI连接...")
            result = self.comic_gen.test_connection()
            
            if result:
                self.logger.info("ComfyUI连接测试成功")
            else:
                self.logger.error("ComfyUI连接测试失败，请确保ComfyUI服务器正在运行")
            
            return result
            
        except Exception as e:
            self.logger.error(f"连接测试失败: {str(e)}")
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="漫画图片生成工具")
    
    # 单图片生成参数
    parser.add_argument("--single", help="生成单角色图片的提示词")
    parser.add_argument("--multi", help="生成多角色图片的提示词")
    parser.add_argument("--ref-image", help="单角色参考图片路径")
    parser.add_argument("--ref-image-1", help="多角色参考图片1路径")
    parser.add_argument("--ref-image-2", help="多角色参考图片2路径")
    
    # 章节处理参数
    parser.add_argument("-f", "--file", help="单个章节JSON文件路径")
    parser.add_argument("-d", "--directory", help="故事板提示词目录路径")
    parser.add_argument("--auto", action="store_true", help="自动模式：处理配置文件中的默认目录")
    
    # 通用参数
    parser.add_argument("-s", "--save-dir", help="保存目录")
    parser.add_argument("-b", "--batch-size", type=int, help="批处理大小（从配置文件读取默认值）")
    parser.add_argument("--test", action="store_true", help="测试ComfyUI连接")
    
    args = parser.parse_args()
    
    # 创建处理器
    processor = ComicImageProcessor()
    
    # 从配置文件获取默认值
    generation_config = processor.comic_gen.config.get("comic_image_generation", {}).get("generation", {})
    default_batch_size = generation_config.get("default_batch_size", 1)
    
    # 如果未指定批处理大小，使用配置文件中的默认值
    if args.batch_size is None:
        args.batch_size = default_batch_size
    
    # 去掉保存目录的引号并处理路径
    if args.save_dir:
        args.save_dir = args.save_dir.strip('"\'')
        if not os.path.isabs(args.save_dir):
            args.save_dir = os.path.abspath(args.save_dir)
        args.save_dir = os.path.normpath(args.save_dir)
    
    # 处理参考图片路径
    if args.ref_image:
        args.ref_image = args.ref_image.strip('"\'')
        if not os.path.isabs(args.ref_image):
            args.ref_image = os.path.abspath(args.ref_image)
        args.ref_image = os.path.normpath(args.ref_image)
    
    if args.ref_image_1:
        args.ref_image_1 = args.ref_image_1.strip('"\'')
        if not os.path.isabs(args.ref_image_1):
            args.ref_image_1 = os.path.abspath(args.ref_image_1)
        args.ref_image_1 = os.path.normpath(args.ref_image_1)
    
    if args.ref_image_2:
        args.ref_image_2 = args.ref_image_2.strip('"\'')
        if not os.path.isabs(args.ref_image_2):
            args.ref_image_2 = os.path.abspath(args.ref_image_2)
        args.ref_image_2 = os.path.normpath(args.ref_image_2)
    
    if args.test:
        # 测试连接
        success = processor.test_connection()
        sys.exit(0 if success else 1)
    
    elif args.single:
        # 生成单角色图片
        success = processor.generate_single_image(
            prompt=args.single,
            reference_image=args.ref_image,
            save_dir=args.save_dir,
            batch_size=args.batch_size
        )
        sys.exit(0 if success else 1)
    
    elif args.multi:
        # 生成多角色图片
        success = processor.generate_multi_character_image(
            prompt=args.multi,
            ref_image_1=args.ref_image_1,
            ref_image_2=args.ref_image_2,
            save_dir=args.save_dir,
            batch_size=args.batch_size
        )
        sys.exit(0 if success else 1)
    
    elif args.file:
        # 处理单个章节
        chapter_file = args.file.strip('\"\'')
        success = processor.process_chapter(
            chapter_file=chapter_file,
            save_dir=args.save_dir
        )
        sys.exit(0 if success else 1)
    
    elif args.directory:
        # 处理目录中的所有章节
        directory = args.directory.strip('"\'')
        success = processor.process_all_chapters(
            storyboards_prompt_dir=directory,
            save_dir=args.save_dir
        )
        sys.exit(0 if success else 1)
    
    elif args.auto:
        # 自动模式：处理默认目录
        success = processor.process_all_chapters(
            storyboards_prompt_dir=None,
            save_dir=args.save_dir
        )
        sys.exit(0 if success else 1)
    
    else:
        # 显示使用说明
        print("漫画图片生成工具使用说明:")
        print()
        print("1. 测试连接:")
        print("   python -m src.services.comic_image_generation.main --test")
        print()
        print("2. 生成单角色图片:")
        print("   python -m src.services.comic_image_generation.main --single \"提示词\" --ref-image \"参考图片路径\"")
        print()
        print("3. 生成多角色图片:")
        print("   python -m src.services.comic_image_generation.main --multi \"提示词\" --ref-image-1 \"参考图片1\" --ref-image-2 \"参考图片2\"")
        print()
        print("4. 处理单个章节:")
        print("   python -m src.services.comic_image_generation.main -f <章节JSON文件路径>")
        print()
        print("5. 处理目录中的所有章节:")
        print("   python -m src.services.comic_image_generation.main -d <故事板提示词目录>")
        print()
        print("6. 自动模式（处理默认目录）:")
        print("   python -m src.services.comic_image_generation.main --auto")
        print()
        # 获取配置文件中的默认值用于显示
    generation_config = processor.comic_gen.config.get("comic_image_generation", {}).get("generation", {})
    default_batch_size = generation_config.get("default_batch_size", 1)
    default_output_dir = processor.comic_gen.config.get("comic_image_generation", {}).get("paths", {}).get("output_root_dir", "data/storyboards_image/")
    default_storyboards_dir = processor.comic_gen.config.get("comic_image_generation", {}).get("paths", {}).get("storyboards_prompt_dir", "data/storyboards_prompt/")
    
    print("通用参数:")
    print("  -s, --save-dir     保存目录")
    print(f"  -b, --batch-size   批处理大小（默认：{default_batch_size}，从配置文件读取）")
    print("  --test             测试ComfyUI连接")
    print()
    print("配置文件默认值:")
    print(f"  默认输出目录: {default_output_dir}")
    print(f"  默认故事板目录: {default_storyboards_dir}")
    print(f"  默认批处理大小: {default_batch_size}")
    print()
    print("使用 -h 查看更多参数信息")


if __name__ == "__main__":
    main()