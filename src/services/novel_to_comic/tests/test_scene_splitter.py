"""
场景分割器测试
"""

import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))

from src.services.novel_to_comic.core.scene_splitter import SceneSplitterAgent
from src.services.novel_to_comic.core.segmenter import IntelligentSegmenter
from src.services.novel_to_comic.utils.character_manager import CharacterManager


def test_scene_splitter():
    """测试场景分割器功能"""
    print("开始测试场景分割器...")
    
    # 创建角色管理器
    character_manager = CharacterManager()
    
    # 创建分割器
    segmenter = IntelligentSegmenter(character_manager)
    scene_splitter = SceneSplitterAgent(character_manager)
    
    # 测试文本
    test_text = """
    第一章 遇强则强
    
    叶君临站在山巅，感受着体内奔腾的力量。"这就是强者的感觉吗？"他喃喃自语。
    
    山风吹过，卷起他的衣袍。远处的云海翻腾，仿佛在回应他的心声。
    
    突然，一股强大的气息从山下传来。叶君临眉头一皱，"有人来了！"
    
    他纵身一跃，如雄鹰般掠向山间小径。
    
    山路上，一个黑衣人缓缓走来，每一步都带着沉重的压迫感。
    """
    
    # 先进行段落分割
    segments = segmenter.split_chapter_to_segments(test_text)
    
    if not segments:
        print("段落分割失败，无法继续测试")
        return
    
    # 取第一个段落进行场景分割
    segment = segments[0]
    
    # 准备上下文
    context = {
        "novel_type": "玄幻",
        "chapter_title": "第一章 遇强则强",
        "previous_scene_summary": "无"
    }
    
    try:
        # 执行场景分割
        scenes = scene_splitter.split_segment_to_scenes(segment, context)
        
        # 打印结果
        print(f"场景分割结果：共 {len(scenes)} 个场景")
        for i, scene in enumerate(scenes):
            print(f"\n场景 {i + 1}:")
            print(f"ID: {scene.scene_id}")
            print(f"描述: {scene.scene_description}")
            print(f"环境: {scene.environment}")
            print(f"主要动作: {scene.main_action}")
            print(f"重要性评分: {scene.importance_score}")
            print(f"视觉适合度: {scene.visual_suitability}")
            print(f"角色数量: {len(scene.characters)}")
            
    except Exception as e:
        print(f"场景分割测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_scene_splitter()
