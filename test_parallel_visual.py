"""
测试并行视觉生成功能
"""

import os
import sys
import time

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.services.novel_to_comic.core.workflow import NovelToComicWorkflow
from src.services.novel_to_comic.core.segmenter import IntelligentSegmenter
from src.services.novel_to_comic.utils.character_manager import CharacterManager
from src.utils.logging_manager import get_logger, LogCategory

logger = get_logger(__name__, LogCategory.PERFORMANCE)


def test_parallel_visual():
    """测试并行视觉生成功能"""
    # 测试文件
    test_file = "data/cleaned_novel/第一章 遇强则强.txt"
    
    if not os.path.exists(test_file):
        print(f"测试文件不存在: {test_file}")
        return
    
    print("="*60)
    print("测试并行视觉生成功能")
    print("="*60)
    
    # 读取文件
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 初始化组件
    character_manager = CharacterManager()
    segmenter = IntelligentSegmenter(character_manager)
    
    # 分割段落
    print("1. 分割段落...")
    segments = segmenter.split_chapter_to_segments(content)
    print(f"   生成了 {len(segments)} 个段落")
    
    # 测试完整的并行处理流程（场景分割 + 视觉生成）
    print("\n2. 测试完整的并行处理流程...")
    workflow_parallel = NovelToComicWorkflow(enable_parallel=True)
    
    start_time = time.time()
    context = {
        "novel_type": "玄幻",
        "chapter_title": "第一章 遇强则强"
    }
    
    # 先进行场景分割
    all_scenes = workflow_parallel.parallel_scene_splitter.process_segments_parallel(segments, context)
    print(f"   场景分割完成，生成 {len(all_scenes)} 个场景")
    
    # 再进行视觉生成
    visual_narratives = workflow_parallel.parallel_visual_workflow.process_scenes_parallel(all_scenes, context)
    parallel_time = time.time() - start_time
    
    print(f"\n完整并行处理完成，耗时: {parallel_time:.2f}秒")
    print(f"总场景数: {len(all_scenes)}")
    print(f"总视觉叙述数: {len(visual_narratives)}")
    
    # 显示视觉叙述的基本信息
    if visual_narratives:
        print("\n3. 视觉叙述信息预览:")
        for i, vn in enumerate(visual_narratives[:3]):  # 只显示前3个
            print(f"   视觉叙述 {i+1}:")
            print(f"     - 视觉描述: {vn.visual_description[:50]}...")
            print(f"     - 构图: {vn.composition.shot_type}, {vn.composition.angle}")
            print(f"     - 角色: {len(vn.characters)} 个")
    
    print("\n" + "="*60)
    print("并行视觉生成功能测试完成")
    print("="*60)


if __name__ == "__main__":
    test_parallel_visual()