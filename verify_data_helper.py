#!/usr/bin/env python3
"""
验证 data_helper 替换后的功能
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def test_imports():
    """测试各个模块的导入"""
    print("=== 测试模块导入 ===")
    
    try:
        # 测试data_helper导入
        from sharebook.utils.data_helper import data_helper
        print("✓ data_helper 导入成功")
        
        # 测试主要模块导入
        from sharebook.utils.comfyui_wrapper import ComfyUIWrapper
        print("✓ ComfyUIWrapper 导入成功")
        
        from sharebook.services.storyboard_to_prompt.storyboard_to_prompt_processor import StoryboardToPromptProcessor
        print("✓ StoryboardToPromptProcessor 导入成功")
        
        from sharebook.core.agents.info_extract.text_preprocessor import TextPreprocessor
        print("✓ TextPreprocessor 导入成功")
        
        from sharebook.services.character_image_generation.character_image_generator import CharacterImageGenerator
        print("✓ CharacterImageGenerator 导入成功")
        
        from sharebook.services.comic_image_generation.comic_image_generation import ComicImageGeneration
        print("✓ ComicImageGeneration 导入成功")
        
        from sharebook.services.novel_to_comic.utils.character_manager import CharacterManager
        print("✓ CharacterManager 导入成功")
        
        return True
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return False

def test_data_helper_paths():
    """测试data_helper路径功能"""
    print("\n=== 测试 data_helper 路径功能 ===")
    
    try:
        from sharebook.utils.data_helper import data_helper
        
        # 测试各种路径获取
        raw_path = data_helper.get_raw_path("test.txt")
        print(f"✓ Raw路径: {raw_path}")
        
        cleaned_path = data_helper.get_cleaned_novel_path("chapter1.txt")
        print(f"✓ Cleaned novel路径: {cleaned_path}")
        
        output_path = data_helper.get_output_path("result.json")
        print(f"✓ Output路径: {output_path}")
        
        characters_path = data_helper.get_characters_path()
        print(f"✓ Characters路径: {characters_path}")
        
        character_image_path = data_helper.get_character_image_path("测试角色", "image_001.png")
        print(f"✓ 角色图片路径: {character_image_path}")
        
        storyboard_path = data_helper.get_storyboards_path("story.json")
        print(f"✓ Storyboard路径: {storyboard_path}")
        
        prompt_path = data_helper.get_storyboards_prompt_path("prompts.json")
        print(f"✓ Prompt路径: {prompt_path}")
        
        return True
    except Exception as e:
        print(f"✗ 路径测试失败: {e}")
        return False

def test_initialization():
    """测试各类初始化"""
    print("\n=== 测试类初始化 ===")
    
    try:
        from sharebook.utils.data_helper import data_helper
        from sharebook.core.agents.info_extract.text_preprocessor import TextPreprocessor
        from sharebook.services.novel_to_comic.utils.character_manager import CharacterManager
        
        # 测试TextPreprocessor初始化
        preprocessor = TextPreprocessor()
        print(f"✓ TextPreprocessor初始化成功，cleaned_novel_dir: {preprocessor.cleaned_novel_dir}")
        
        # 测试CharacterManager初始化
        character_manager = CharacterManager()
        print(f"✓ CharacterManager初始化成功，CSV路径: {character_manager.character_csv_path}")
        
        return True
    except Exception as e:
        print(f"✗ 初始化测试失败: {e}")
        return False

def test_file_operations():
    """测试文件操作"""
    print("\n=== 测试文件操作 ===")
    
    try:
        from sharebook.utils.data_helper import data_helper
        
        # 测试文件读写
        test_content = "测试内容"
        test_file = data_helper.get_processed_path("test_verify.txt")
        
        # 写入文件
        data_helper.write_text_file(test_content, test_file)
        print(f"✓ 文件写入成功: {test_file}")
        
        # 读取文件
        read_content = data_helper.read_text_file(test_file)
        print(f"✓ 文件读取成功: {read_content}")
        
        # 测试JSON操作
        test_data = {"test": "data", "number": 123}
        json_file = data_helper.get_prompts_path("test_verify.json")
        
        # 写入JSON
        data_helper.write_json_file(test_data, json_file)
        print(f"✓ JSON写入成功: {json_file}")
        
        # 读取JSON
        read_data = data_helper.read_json_file(json_file)
        print(f"✓ JSON读取成功: {read_data}")
        
        # 清理测试文件
        test_file.unlink()
        json_file.unlink()
        print("✓ 测试文件清理完成")
        
        return True
    except Exception as e:
        print(f"✗ 文件操作测试失败: {e}")
        return False

def main():
    """主验证函数"""
    print("DataHelper 替换验证")
    print("=" * 50)
    
    results = []
    
    # 运行各项测试
    results.append(test_imports())
    results.append(test_data_helper_paths())
    results.append(test_initialization())
    results.append(test_file_operations())
    
    # 统计结果
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 50)
    print(f"验证结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("✓ 所有测试通过！data_helper替换成功！")
        return True
    else:
        print("✗ 部分测试失败，需要检查")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)