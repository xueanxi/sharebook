#!/usr/bin/env python3
"""
简单验证 data_helper 功能
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def main():
    print("=== 简单验证 data_helper 功能 ===")
    
    try:
        # 测试data_helper导入
        from sharebook.utils.data_helper import data_helper
        print("✓ data_helper 导入成功")
        
        # 测试基本路径功能
        raw_path = data_helper.get_raw_path("test.txt")
        print(f"✓ Raw路径: {raw_path}")
        
        characters_path = data_helper.get_characters_path()
        print(f"✓ Characters路径: {characters_path}")
        
        # 测试文件操作
        test_content = "测试内容"
        test_file = data_helper.get_processed_path("simple_test.txt")
        
        # 写入文件
        data_helper.write_text_file(test_content, test_file)
        print(f"✓ 文件写入成功: {test_file}")
        
        # 读取文件
        read_content = data_helper.read_text_file(test_file)
        print(f"✓ 文件读取成功: {read_content}")
        
        # 清理测试文件
        test_file.unlink()
        print("✓ 测试文件清理完成")
        
        print("\n=== 验证主要模块导入 ===")
        
        # 测试核心模块导入
        from sharebook.core.agents.info_extract.text_preprocessor import TextPreprocessor
        print("✓ TextPreprocessor 导入成功")
        
        # 检查cleaned_novel_dir是否正确设置
        preprocessor = TextPreprocessor()
        print(f"✓ TextPreprocessor.cleaned_novel_dir: {preprocessor.cleaned_novel_dir}")
        
        # 测试character_manager
        from sharebook.services.novel_to_comic.utils.character_manager import CharacterManager
        print("✓ CharacterManager 导入成功")
        
        character_manager = CharacterManager()
        print(f"✓ CharacterManager.character_csv_path: {character_manager.character_csv_path}")
        
        print("\n✓ 所有验证通过！data_helper替换成功！")
        return True
        
    except Exception as e:
        print(f"✗ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)