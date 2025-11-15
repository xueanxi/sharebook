"""
测试章节排序功能
"""

import os
from pathlib import Path
import sys

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from nodes.chapter_selector import ChapterSelector


def test_chapter_sorting():
    """
    测试章节排序功能
    """
    # 从配置文件中获取小说路径
    config_path = "src/services/extraction_character/config.yaml"
    try:
        # 尝试导入ConfigManager获取正确的小说路径
        from config_manager import ConfigManager
        config_manager = ConfigManager(config_path)
        novel_path = config_manager.get_novel_path()
        print(f"使用小说路径: {novel_path}")
    except Exception:
        # 如果无法导入ConfigManager，使用默认路径
        novel_path = "../../../data/cleaned_novel"
        print(f"使用默认小说路径: {novel_path}")
    
    # 确保路径存在
    if not os.path.exists(novel_path):
        print(f"小说路径不存在: {novel_path}")
        print("请检查配置或小说文件路径")
        return False
    
    # 创建章节选择器
    selector = ChapterSelector(novel_path)
    
    # 获取所有章节并排序
    all_chapters = selector._get_all_chapters()
    
    print("排序后的章节列表:")
    for i, chapter in enumerate(all_chapters, 1):
        print(f"{i}. {chapter}")
    
    # 验证是否正确排序
    # 检查前几个章节是否是第一章、第二章等
    is_correct_order = True
    if len(all_chapters) > 0:
        # 检查第一个章节是否包含"第一章"
        if "第一章" not in all_chapters[0]:
            print("警告: 第一个章节不包含'第一章'")
            is_correct_order = False
        
        # 检查是否有明显的顺序错误
        for i in range(len(all_chapters) - 1):
            current_num = selector._extract_chapter_number(all_chapters[i])
            next_num = selector._extract_chapter_number(all_chapters[i + 1])
            if current_num > next_num:
                print(f"发现顺序错误: {all_chapters[i]} (章节号{current_num}) 在 {all_chapters[i + 1]} (章节号{next_num}) 之后")
                is_correct_order = False
    
    if is_correct_order:
        print("\n测试通过: 章节正确排序")
    else:
        print("\n测试失败: 章节排序不正确")
    
    return is_correct_order


if __name__ == "__main__":
    test_chapter_sorting()