"""
信息提取模块的测试文件
用于验证信息提取功能是否正常工作
"""

import os
import sys
import json
from langchain_core.messages import BaseMessage

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.services.extraction.main import extract_novel_information


def custom_json_serializer(obj):
    """自定义JSON序列化函数，处理不可序列化的对象"""
    if isinstance(obj, BaseMessage):
        return {
            "type": obj.__class__.__name__,
            "content": obj.content
        }
    elif hasattr(obj, 'dict'):
        return obj.dict()
    elif hasattr(obj, '__dict__'):
        return obj.__dict__
    else:
        return str(obj)


def test_information_extraction():
    """测试信息提取功能"""
    
    # 测试文件路径
    test_file = "data/raw/第一章 遇强则强.txt"
    
    # 检查测试文件是否存在
    if not os.path.exists(test_file):
        print(f"测试文件不存在: {test_file}")
        return False
    
    # 输出目录
    output_dir = "data/output"
    
    print(f"开始测试文件: {test_file}")
    print("=" * 50)
    
    # 执行信息提取
    result = extract_novel_information(test_file, output_dir)
    
    # 打印结果
    print("\n提取结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2, default=custom_json_serializer))
    
    # 检查是否成功
    if result.get("success", False):
        print("\n✅ 测试成功!")
        if "output_file" in result:
            print(f"结果已保存到: {result['output_file']}")
        return True
    else:
        print("\n❌ 测试失败!")
        print(f"错误信息: {result.get('error', '未知错误')}")
        return False


if __name__ == "__main__":
    test_information_extraction()