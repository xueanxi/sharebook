"""
集成测试
"""

import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))

from src.services.novel_to_comic.main import NovelToComicProcessor


def test_integration():
    """测试整个系统的集成功能"""
    print("开始集成测试...")
    
    # 创建处理器
    processor = NovelToComicProcessor()
    
    # 测试文件路径
    test_file = "data/cleaned_novel/第一章 遇强则强.txt"
    
    # 检查测试文件是否存在
    if not os.path.exists(test_file):
        print(f"测试文件不存在: {test_file}")
        print("使用内置测试文本...")
        
        # 创建临时测试文件
        test_text = """
第一章 遇强则强

叶君临站在山巅，感受着体内奔腾的力量。"这就是强者的感觉吗？"他喃喃自语。

山风吹过，卷起他的衣袍。远处的云海翻腾，仿佛在回应他的心声。

突然，一股强大的气息从山下传来。叶君临眉头一皱，"有人来了！"

他纵身一跃，如雄鹰般掠向山间小径。

山路上，一个黑衣人缓缓走来，每一步都带着沉重的压迫感。
        """
        
        # 创建临时目录和文件
        os.makedirs("temp_test", exist_ok=True)
        test_file = "temp_test/test_chapter.txt"
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_text)
    
    try:
        # 处理章节
        result = processor.process_chapter(
            chapter_file=test_file,
            chapter_title="第一章 遇强则强",
            novel_type="玄幻"
        )
        
        # 输出结果
        print("\n" + "="*50)
        print("集成测试结果:")
        print("="*50)
        
        if result.success:
            print("✓ 处理成功!")
            print(f"输出路径: {result.output_path}")
            
            if result.processing_summary:
                summary = result.processing_summary
                print(f"总段落数: {summary.total_segments}")
                print(f"总场景数: {summary.total_scenes}")
                print(f"总故事板数: {summary.total_storyboards}")
                print(f"处理时间: {summary.processing_time}")
                print(f"错误数量: {summary.error_count}")
            
            if result.errors:
                print("\n警告信息:")
                for error in result.errors:
                    print(f"  - {error}")
            
            # 尝试读取并显示部分输出内容
            if result.output_path and os.path.exists(result.output_path):
                print(f"\n输出文件内容预览:")
                print("-"*30)
                
                import json
                with open(result.output_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 显示章节信息
                if "chapter_info" in data:
                    chapter_info = data["chapter_info"]
                    print(f"章节标题: {chapter_info.get('chapter_title', '未知')}")
                    print(f"小说类型: {chapter_info.get('novel_type', '未知')}")
                    print(f"处理时间: {chapter_info.get('processing_time', '未知')}")
                
                # 显示段落和场景统计
                if "basic_stats" in data:
                    stats = data["basic_stats"]
                    print(f"段落统计: {stats.get('total_segments', 0)}")
                    print(f"场景统计: {stats.get('total_scenes', 0)}")
                    print(f"故事板统计: {stats.get('total_storyboards', 0)}")
                
                # 显示第一个场景的视觉叙述
                if "segments" in data and data["segments"]:
                    first_segment = data["segments"][0]
                    if "scenes" in first_segment and first_segment["scenes"]:
                        first_scene = first_segment["scenes"][0]
                        if "visual_narrative" in first_scene:
                            visual = first_scene["visual_narrative"]
                            print(f"\n第一个场景的视觉描述:")
                            print(f"  {visual.get('visual_description', '无')[:100]}...")
                            
                            if "narration" in visual:
                                narration = visual["narration"]
                                scene_desc = narration.get('scene_description', '')
                                if scene_desc:
                                    print(f"\n场景旁白:")
                                    print(f"  {scene_desc}")
        else:
            print("✗ 处理失败!")
            for error in result.errors:
                print(f"错误: {error}")
        
    except Exception as e:
        print(f"集成测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理临时文件
        if test_file.startswith("temp_test/"):
            try:
                os.remove(test_file)
                os.rmdir("temp_test")
                print("\n临时文件已清理")
            except:
                pass


if __name__ == "__main__":
    test_integration()