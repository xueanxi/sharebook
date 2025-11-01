"""
测试TextPreprocessorAgent的简单清洗功能
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.agents.agents import TextPreprocessorAgent

def test_text_cleaning():
    """测试文本清洗功能"""
    # 读取测试文件
    file_path = "data/raw/第一章 遇强则强.txt"
    
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        original_text = f.read()
    
    print(f"原始文本长度: {len(original_text)}")
    print(f"原始文本预览: {original_text[:100]}...")
    
    # 创建TextPreprocessorAgent实例
    preprocessor = TextPreprocessorAgent()
    
    # 测试_simple_text_cleaning方法
    cleaned_text = preprocessor._simple_text_cleaning(original_text)
    
    print(f"\n清洗后文本长度: {len(cleaned_text)}")
    print(f"清洗后文本预览: {cleaned_text[:100]}...")
    
    # 测试process方法
    result = preprocessor.process(original_text)
    
    print(f"\nprocess方法结果:")
    print(f"  成功: {result.get('success', False)}")
    print(f"  结果长度: {len(result.get('result', ''))}")
    print(f"  错误: {result.get('error', 'None')}")
    print(f"  结果预览: {result.get('result', '')[:100]}...")

if __name__ == "__main__":
    test_text_cleaning()