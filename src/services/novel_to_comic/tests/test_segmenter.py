"""
段落分割器测试
"""

import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))

from src.services.novel_to_comic.core.segmenter import IntelligentSegmenter
from src.services.novel_to_comic.utils.character_manager import CharacterManager


def test_segmenter():
    """测试段落分割器功能"""
    print("开始测试段落分割器...")
    
    # 创建角色管理器
    character_manager = CharacterManager()
    
    # 创建分割器
    segmenter = IntelligentSegmenter(character_manager)
    
    # 测试文本
    test_text = """
    第一章 遇强则强
    
    叶君临站在山巅，感受着体内奔腾的力量。"这就是强者的感觉吗？"他喃喃自语。
    
    山风吹过，卷起他的衣袍。远处的云海翻腾，仿佛在回应他的心声。
    
    突然，一股强大的气息从山下传来。叶君临眉头一皱，"有人来了！"
    
    他纵身一跃，如雄鹰般掠向山间小径。
    
    山路上，一个黑衣人缓缓走来，每一步都带着沉重的压迫感。
    """
    
    # 执行分割
    segments = segmenter.split_chapter_to_segments(test_text)
    
    # 打印结果
    print(f"分割结果：共 {len(segments)} 个段落")
    for i, segment in enumerate(segments):
        print(f"\n段落 {i + 1}:")
        print(f"ID: {segment.segment_id}")
        print(f"长度: {len(segment.text)}")
        print(f"内容: {segment.text[:100]}...")
        print(f"元数据: {segment.metadata}")


if __name__ == "__main__":
    test_segmenter()
