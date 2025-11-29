"""
data_helper 使用示例

展示如何在项目中使用 data_helper 来统一管理数据访问
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from sharebook.utils.data_helper import data_helper


def example_novel_processing():
    """示例：小说处理流程中使用 data_helper"""
    print("=== 小说处理示例 ===")
    
    # 1. 读取原始小说文件
    raw_files = data_helper.list_raw_files("*.txt")
    if raw_files:
        first_file = raw_files[0]
        print(f"读取原始文件: {first_file.name}")
        
        # 使用 data_helper 读取文件内容
        content = data_helper.read_text_file(first_file)
        print(f"文件内容长度: {len(content)} 字符")
        
        # 2. 处理后的文件保存到 cleaned_novel 目录
        cleaned_path = data_helper.get_cleaned_novel_path(first_file.name)
        # 假设这里进行了某些清理操作
        cleaned_content = content.strip()  # 简单示例
        data_helper.write_text_file(cleaned_content, cleaned_path)
        print(f"清理后文件保存到: {cleaned_path}")
    
    print()


def example_character_extraction():
    """示例：角色提取流程中使用 data_helper"""
    print("=== 角色提取示例 ===")
    
    # 1. 检查角色数据文件是否存在
    characters_file = data_helper.get_characters_path()
    if data_helper.file_exists(characters_file):
        # 读取角色数据
        import pandas as pd
        characters_df = data_helper.read_csv_file(characters_file)
        print(f"读取到 {len(characters_df)} 个角色")
        
        # 2. 为每个角色生成图片目录路径
        for _, character in characters_df.head(3).iterrows():
            character_name = character.get('name', '未知角色')
            image_path = data_helper.get_character_image_path(character_name, 'image_001.png')
            print(f"角色 {character_name} 的图片路径: {image_path}")
    
    print()


def example_storyboard_generation():
    """示例：故事板生成流程中使用 data_helper"""
    print("=== 故事板生成示例 ===")
    
    # 1. 读取清理后的小说章节
    novel_files = data_helper.list_cleaned_novel_files("*.txt")
    if novel_files:
        chapter_file = novel_files[0]
        print(f"处理章节: {chapter_file.name}")
        
        # 2. 生成故事板数据
        storyboard_data = {
            "chapter_title": chapter_file.stem,
            "scenes": [
                {
                    "scene_id": 1,
                    "description": "场景描述1",
                    "characters": ["角色A", "角色B"]
                },
                {
                    "scene_id": 2,
                    "description": "场景描述2",
                    "characters": ["角色A"]
                }
            ]
        }
        
        # 3. 保存故事板数据
        storyboard_file = data_helper.get_storyboards_path(f"{chapter_file.stem}_storyboards.json")
        data_helper.write_json_file(storyboard_data, storyboard_file)
        print(f"故事板数据保存到: {storyboard_file}")
        
        # 4. 生成提示词数据
        prompt_data = {
            "chapter_title": chapter_file.stem,
            "prompts": [
                {
                    "scene_id": 1,
                    "prompt": "一个美丽的场景，角色A和角色B在一起",
                    "negative_prompt": "模糊, 低质量"
                },
                {
                    "scene_id": 2,
                    "prompt": "角色A独自一人的场景",
                    "negative_prompt": "多个人物, 混乱"
                }
            ]
        }
        
        prompt_file = data_helper.get_storyboards_prompt_path(f"{chapter_file.stem}_prompts.json")
        data_helper.write_json_file(prompt_data, prompt_file)
        print(f"提示词数据保存到: {prompt_file}")
    
    print()


def example_batch_processing():
    """示例：批量处理中使用 data_helper"""
    print("=== 批量处理示例 ===")
    
    # 1. 获取所有需要处理的章节
    novel_files = data_helper.list_cleaned_novel_files("*.txt")
    print(f"找到 {len(novel_files)} 个章节文件")
    
    # 2. 批量处理每个章节
    processed_count = 0
    for novel_file in novel_files[:3]:  # 只处理前3个作为示例
        try:
            # 读取文件
            content = data_helper.read_text_file(novel_file)
            
            # 模拟处理过程
            processed_data = {
                "file": novel_file.name,
                "length": len(content),
                "processed": True
            }
            
            # 保存处理结果
            output_file = data_helper.get_output_path(f"{novel_file.stem}_processed.json")
            data_helper.write_json_file(processed_data, output_file)
            
            processed_count += 1
            print(f"✓ 处理完成: {novel_file.name}")
            
        except Exception as e:
            print(f"✗ 处理失败: {novel_file.name}, 错误: {e}")
    
    print(f"批量处理完成，成功处理 {processed_count} 个文件")
    print()


def main():
    """主函数，运行所有示例"""
    print("DataHelper 使用示例")
    print("=" * 50)
    
    example_novel_processing()
    example_character_extraction()
    example_storyboard_generation()
    example_batch_processing()
    
    print("=" * 50)
    print("示例运行完成！")


if __name__ == "__main__":
    main()