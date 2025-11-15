"""
简化的并行处理测试
只测试并行功能是否正常工作
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


def test_parallel_only():
    """仅测试并行处理功能"""
    # 测试文件
    test_file = "data/cleaned_novel/第一章 遇强则强.txt"
    
    if not os.path.exists(test_file):
        print(f"测试文件不存在: {test_file}")
        return
    
    print("="*60)
    print("测试并行场景分割功能")
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
    
    # 测试并行处理
    print("\n2. 测试并行场景分割...")
    workflow_parallel = NovelToComicWorkflow(enable_parallel=True)
    
    start_time = time.time()
    context = {
        "novel_type": "玄幻",
        "chapter_title": "第一章 遇强则强"
    }
    parallel_scenes = workflow_parallel.parallel_scene_splitter.process_segments_parallel(segments, context)
    parallel_time = time.time() - start_time
    
    print(f"\n并行处理完成，耗时: {parallel_time:.2f}秒")
    print(f"总场景数: {len(parallel_scenes)}")
    
    # 显示每个场景的基本信息
    if parallel_scenes:
        print("\n3. 场景信息预览:")
        for i, scene in enumerate(parallel_scenes[:5]):  # 只显示前5个场景
            print(f"   场景 {i+1}: {scene.scene_description[:50]}...")
    
    print("\n" + "="*60)
    print("并行功能测试完成")
    print("="*60)


if __name__ == "__main__":
    test_parallel_only()
