"""
视觉叙述生成器测试
"""

import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))

from src.services.novel_to_comic.core.visual_narrative import VisualNarrativeAgent
from src.services.novel_to_comic.core.scene_splitter import SceneSplitterAgent
from src.services.novel_to_comic.core.segmenter import IntelligentSegmenter
from src.services.novel_to_comic.utils.character_manager import CharacterManager


def test_visual_narrative():
    """测试视觉叙述生成器功能"""
    print("开始测试视觉叙述生成器...")
    
    # 创建角色管理器
    character_manager = CharacterManager()
    
    # 创建分割器
    segmenter = IntelligentSegmenter(character_manager)
    scene_splitter = SceneSplitterAgent(character_manager)
    visual_agent = VisualNarrativeAgent(character_manager)
    
    # 测试文本
    test_text = """
    第一章 遇强则强
    
    叶君临站在山巅，感受着体内奔腾的力量。"这就是强者的感觉吗？"他喃喃自语。
    
    山风吹过，卷起他的衣袍。远处的云海翻腾，仿佛在回应他的心声。
    
    突然，一股强大的气息从山下传来。叶君临眉头一皱，"有人来了！"
    
    他纵身一跃，如雄鹰般掠向山间小径。
    
    山路上，一个黑衣人缓缓走来，每一步都带着沉重的压迫感。
    """
    
    # 准备上下文
    context = {
        "novel_type": "玄幻",
        "chapter_title": "第一章 遇强则强",
        "previous_scene_summary": "无"
    }
    
    try:
        # 先进行段落分割
        segments = segmenter.split_chapter_to_segments(test_text)
        
        if not segments:
            print("段落分割失败，无法继续测试")
            return
        
        # 取第一个段落进行场景分割
        segment = segments[0]
        scenes = scene_splitter.split_segment_to_scenes(segment, context)
        
        if not scenes:
            print("场景分割失败，无法继续测试")
            return
        
        # 取第一个场景进行视觉叙述生成
        scene = scenes[0]
        visual_narrative = visual_agent.generate_visual_narrative(scene, context)
        
        # 打印结果
        print(f"\n视觉叙述生成结果:")
        print(f"场景ID: {visual_narrative.scene_id}")
        print(f"视觉描述: {visual_narrative.visual_description}")
        print(f"构图类型: {visual_narrative.composition.shot_type}")
        print(f"拍摄角度: {visual_narrative.composition.angle}")
        print(f"环境背景: {visual_narrative.environment.background}")
        print(f"艺术风格: {visual_narrative.style.art_style}")
        print(f"场景描述旁白: {visual_narrative.narration.scene_description}")
        print(f"分镜类型: {visual_narrative.storyboard_suggestions.panel_type}")
        print(f"角色数量: {len(visual_narrative.characters)}")
        
    except Exception as e:
        print(f"视觉叙述生成测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_visual_narrative()
