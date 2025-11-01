"""
并行化提取性能测试脚本
用于测试单个文件的并行处理性能
"""

import os
import sys
import time
import json
from typing import Dict, Any

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.services.extraction.main import extract_novel_information


def test_single_file_performance(file_path: str, output_dir: str = "test_output") -> Dict[str, Any]:
    """
    测试单文件的并行处理性能
    
    Args:
        file_path: 测试文件路径
        output_dir: 输出目录
        
    Returns:
        性能测试结果
    """
    print(f"测试文件: {file_path}")
    results = {}
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"错误: 文件不存在 - {file_path}")
        return {"error": f"文件不存在: {file_path}"}
    
    # 读取文件内容并打印长度
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"  文件内容长度: {len(content)} 字符")
        print(f"  文件内容预览: {content[:100]}...")
    except Exception as e:
        print(f"错误: 读取文件失败 - {str(e)}")
        return {"error": f"读取文件失败: {str(e)}"}
    
    # 测试LangGraph并行处理
    print("  运行LangGraph并行处理...")
    start_time = time.time()
    langgraph_result = extract_novel_information(file_path, output_dir)
    langgraph_time = time.time() - start_time
    
    print(f"    LangGraph并行处理耗时: {langgraph_time:.2f}秒")
    print(f"    处理结果: {langgraph_result}")
    
    results["langgraph_parallel"] = {
        "time": langgraph_time,
        "success": langgraph_result.get("success", False),
        "result": langgraph_result
    }
    
    return results


def main():
    """主函数，运行性能测试"""
    # 确保输出目录存在
    os.makedirs("test_output", exist_ok=True)
    
    # 查找测试文件
    test_files = []
    data_dir = "data/raw"  # 修改为正确的目录
    if os.path.exists(data_dir):
        test_files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) 
                     if f.endswith('.txt')]
    
    if not test_files:
        print("未找到测试文件，请确保data/raw目录中有.txt文件")
        return
    
    # 只测试第一个文件
    test_file = test_files[0]
    
    # 运行单文件测试
    print(f"开始测试文件: {os.path.basename(test_file)}")
    result = test_single_file_performance(test_file)
    
    # 汇总结果
    summary = {
        "test_file": os.path.basename(test_file),
        "test_result": result,
        "test_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # 保存测试结果
    output_file = os.path.join("test_output", f"{os.path.basename(test_file)}_info_parallel.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"\n测试完成！结果已保存到 {output_file}")
    
    # 打印简要总结
    print("\n=== 性能测试总结 ===")
    print(f"文件: {os.path.basename(test_file)}")
    if "langgraph_parallel" in result:
        print(f"  LangGraph并行耗时: {result['langgraph_parallel']['time']:.2f}秒")
        print(f"  处理状态: {'成功' if result['langgraph_parallel']['success'] else '失败'}")
        
        # 打印更多详细信息
        langgraph_result = result['langgraph_parallel']['result']
        if isinstance(langgraph_result, dict):
            print(f"  原始文本长度: {langgraph_result.get('original_text_length', '未知')}")
            print(f"  清洗后文本长度: {langgraph_result.get('cleaned_text_length', '未知')}")
            print(f"  完成的任务: {langgraph_result.get('completed_tasks', [])}")
            print(f"  错误信息: {langgraph_result.get('errors', [])}")
            
            # 检查各个提取结果
            characters = langgraph_result.get('characters', {})
            plot = langgraph_result.get('plot', {})
            satisfaction_points = langgraph_result.get('satisfaction_points', {})
            
            print(f"  人物提取结果: {characters}")
            print(f"  剧情分析结果: {plot}")
            print(f"  爽点识别结果: {satisfaction_points}")


if __name__ == "__main__":
    main()