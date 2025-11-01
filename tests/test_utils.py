"""
测试工具模块，提供共享的测试数据和工具函数
"""

import os
import sys
import json
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 测试数据路径
TEST_DATA_DIR = project_root / "data" / "raw"
TEST_RESULTS_DIR = project_root / "test_results"

# 确保测试结果目录存在
TEST_RESULTS_DIR.mkdir(exist_ok=True)

def get_test_novel_path():
    """获取测试小说文件路径"""
    novel_path = TEST_DATA_DIR / "第一章 遇强则强.txt"
    if not novel_path.exists():
        raise FileNotFoundError(f"测试小说文件不存在: {novel_path}")
    return novel_path

def get_test_novel_content():
    """获取测试小说内容"""
    with open(get_test_novel_path(), 'r', encoding='utf-8') as f:
        return f.read()

def save_test_results(results, filename):
    """保存测试结果到JSON文件"""
    output_path = TEST_RESULTS_DIR / filename
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    return output_path

def print_test_result(test_name, result, preview_length=100):
    """打印测试结果"""
    print(f"\n{test_name}结果:")
    if isinstance(result, str):
        print(f"长度: {len(result)} 字符")
        print(f"内容预览: {result[:preview_length]}...")
    elif isinstance(result, dict):
        for key, value in result.items():
            if isinstance(value, str):
                print(f"{key}: 长度 {len(value)} 字符")
                print(f"{key} 预览: {value[:preview_length]}...")
            else:
                print(f"{key}: {value}")
    else:
        print(f"结果: {result}")

def check_agent_result(result, agent_name):
    """检查Agent结果是否有效"""
    if not result:
        print(f"{agent_name}失败: 结果为空")
        return False
    
    if isinstance(result, dict):
        if 'success' in result and not result['success']:
            print(f"{agent_name}失败: {result.get('error', '未知错误')}")
            return False
        
        # 检查result字段
        if 'result' in result:
            content = result['result']
            if isinstance(content, str) and len(content) > 0:
                return True
            elif isinstance(content, dict):
                return True
            else:
                print(f"{agent_name}失败: result字段内容无效")
                return False
    
    print(f"{agent_name}失败: 结果格式不正确")
    return False