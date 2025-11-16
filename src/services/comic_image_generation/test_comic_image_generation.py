"""
测试漫画图片生成接口
"""

import os
import sys
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from src.services.comic_image_generation import ComicImageGeneration
from config.logging_config import get_logger

logger = get_logger(__name__)


def test_comic_image_generation():
    """测试漫画图片生成功能"""
    try:
        # 创建接口实例
        comic_gen = ComicImageGeneration()
        
        # 测试连接
        if not comic_gen.test_connection():
            logger.error("无法连接到ComfyUI服务器，请确保ComfyUI正在运行")
            return False
        
        # 测试参数
        prompt = "Ye Jun stood in the center of a deep and mysterious primeval forest. His white hair was as white as snow, gently swaying in the invisible air current. His eyebrows and eyes were as deep as ancient abyss, and golden runes that flashed in an instant reflected in his eyes. He was dressed in a long black robe, with silver patterns flowing like a starry river on his sleeves and shoulder lines. A jade belt was draped around his waist, and his cape fluttered like a battle flag. On his shoulder was an ancient sword, with thunder patterns faintly visible on its spine. He slightly raised his head, his expression solemn and shocked. The corners of his mouth were slightly parted, neither startled nor delighted, as if he were receiving some ancient gift from heaven and earth. The background is a hazy ancient forest shadow. The Outlines of towering ancient trees are faintly visible in the mist. The moss on the ground gives off a faint green glow, and in the air, there are fine fragments of spiritual energy floating like stardust. The overall light radiated from the inside out, as if golden rays were seeping through his body, forming a sharp contrast with the surrounding darkness, highlighting his solitary and majestic aura."
        reference_image = "data/characters/image/搬山宗宗主/image_001.png"  # 使用角色参考图片
        save_dir = "test_output/"
        
        # 检查参考图片是否存在
        if not os.path.exists(reference_image):
            logger.warning(f"参考图片不存在: {reference_image}，将使用工作流中的默认参考图片")
            reference_image = None
        
        # 生成图片
        logger.info("开始生成漫画图片...")
        image_paths = comic_gen.generate_image(
            prompt=prompt,
            save_dir=save_dir,
            reference_image=reference_image,
            batch_size=4,
        )
        
        logger.info(f"图片生成完成，保存路径: {image_paths}")
        return True
        
    except Exception as e:
        logger.error(f"测试过程中出错: {str(e)}")
        return False


if __name__ == "__main__":
    success = test_comic_image_generation()
    if success:
        logger.info("测试成功完成")
    else:
        logger.error("测试失败")