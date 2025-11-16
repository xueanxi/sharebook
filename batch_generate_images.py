"""
批量生成角色图片脚本
用于批量处理多个角色的图片生成任务
"""

import os
import sys
import logging
import time

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ""))
sys.path.insert(0, project_root)

from src.services.character_image_generation.character_image_generator import CharacterImageGenerator

# 设置日志级别
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def batch_generate_characters(batch_size=1, skip_existing=True):
    """批量生成所有角色图片"""
    print("开始批量生成角色图片...")
    
    try:
        generator = CharacterImageGenerator()
        
        # 测试连接
        if not generator.test_connection():
            print("ComfyUI连接失败，请确保ComfyUI服务器正在运行")
            return False
        
        # 获取角色列表
        characters = generator.get_character_list()
        if not characters:
            print("没有找到角色数据")
            return False
        
        print(f"找到 {len(characters)} 个角色，开始批量生成...")
        
        # 生成所有角色图片
        results = generator.generate_all_characters(batch_size=batch_size, skip_existing=skip_existing)
        
        # 统计结果
        success_count = 0
        total_images = 0
        
        print("\n生成结果:")
        for name, paths in results.items():
            if paths:
                print(f"✓ {name}: {len(paths)} 张图片")
                success_count += 1
                total_images += len(paths)
            else:
                print(f"✗ {name}: 生成失败")
        
        print(f"\n完成! 成功生成 {success_count}/{len(characters)} 个角色的图片，共 {total_images} 张图片")
        return True
        
    except Exception as e:
        print(f"批量生成失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="批量生成角色图片")
    parser.add_argument("--batch-size", type=int, default=1, help="批处理大小 (默认: 1)")
    parser.add_argument("--force", action="store_true", help="强制重新生成已有图片的角色")
    
    args = parser.parse_args()
    
    skip_existing = not args.force
    success = batch_generate_characters(batch_size=args.batch_size, skip_existing=skip_existing)
    sys.exit(0 if success else 1)