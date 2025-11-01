"""
并行化提取性能测试脚本
用于测试和比较串行与并行处理的性能和正确性
"""

import os
import sys
import time
import json
from typing import Dict, Any, List

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.services.extraction.main import extract_novel_information, batch_extract_novel_info


def test_single_file_performance(file_path: str, output_dir: str = "test_output") -> Dict[str, Any]:
    """
    测试单文件的串行与并行处理性能
    
    Args:
        file_path: 测试文件路径
        output_dir: 输出目录
        
    Returns:
        性能测试结果
    """
    print(f"测试文件: {file_path}")
    results = {}
    
    # 测试串行处理
    print("  运行串行处理...")
    start_time = time.time()
    serial_result = extract_novel_information(file_path, output_dir, parallel=False)
    serial_time = time.time() - start_time
    results["serial"] = {
        "time": serial_time,
        "success": serial_result.get("success", False),
        "result": serial_result
    }
    print(f"    串行处理耗时: {serial_time:.2f}秒")
    
    # 测试LangGraph并行处理
    print("  运行LangGraph并行处理...")
    start_time = time.time()
    langgraph_result = extract_novel_information(file_path, output_dir, parallel=True, parallel_method="langgraph")
    langgraph_time = time.time() - start_time
    results["langgraph_parallel"] = {
        "time": langgraph_time,
        "success": langgraph_result.get("success", False),
        "result": langgraph_result
    }
    print(f"    LangGraph并行处理耗时: {langgraph_time:.2f}秒")
    
    # 测试ThreadPool并行处理
    print("  运行ThreadPool并行处理...")
    start_time = time.time()
    threadpool_result = extract_novel_information(file_path, output_dir, parallel=True, parallel_method="threadpool")
    threadpool_time = time.time() - start_time
    results["threadpool_parallel"] = {
        "time": threadpool_time,
        "success": threadpool_result.get("success", False),
        "result": threadpool_result
    }
    print(f"    ThreadPool并行处理耗时: {threadpool_time:.2f}秒")
    
    # 计算性能提升
    if serial_time > 0:
        results["langgraph_speedup"] = serial_time / langgraph_time if langgraph_time > 0 else 0
        results["threadpool_speedup"] = serial_time / threadpool_time if threadpool_time > 0 else 0
        print(f"    LangGraph加速比: {results['langgraph_speedup']:.2f}x")
        print(f"    ThreadPool加速比: {results['threadpool_speedup']:.2f}x")
    
    # 验证结果一致性
    results["consistency_check"] = verify_result_consistency(
        serial_result, langgraph_result, threadpool_result
    )
    
    return results


def verify_result_consistency(serial_result: Dict, langgraph_result: Dict, threadpool_result: Dict) -> Dict[str, Any]:
    """
    验证不同处理方式的结果一致性
    
    Args:
        serial_result: 串行处理结果
        langgraph_result: LangGraph并行处理结果
        threadpool_result: ThreadPool并行处理结果
        
    Returns:
        一致性检查结果
    """
    check_result = {
        "all_successful": True,
        "data_consistency": True,
        "differences": []
    }
    
    # 检查所有处理是否成功
    for name, result in [("serial", serial_result), ("langgraph", langgraph_result), ("threadpool", threadpool_result)]:
        if not result.get("success", False):
            check_result["all_successful"] = False
            check_result["differences"].append(f"{name}处理失败")
    
    # 如果所有处理都成功，检查数据一致性
    if check_result["all_successful"]:
        # 比较关键数据字段
        serial_data = serial_result.get("data", {})
        langgraph_data = langgraph_result.get("data", {})
        threadpool_data = threadpool_result.get("data", {})
        
        # 检查人物信息
        if serial_data.get("character_info") != langgraph_data.get("character_info"):
            check_result["data_consistency"] = False
            check_result["differences"].append("人物信息不一致: serial vs langgraph")
            
        if serial_data.get("character_info") != threadpool_data.get("character_info"):
            check_result["data_consistency"] = False
            check_result["differences"].append("人物信息不一致: serial vs threadpool")
        
        # 检查剧情分析
        if serial_data.get("plot_info") != langgraph_data.get("plot_info"):
            check_result["data_consistency"] = False
            check_result["differences"].append("剧情分析不一致: serial vs langgraph")
            
        if serial_data.get("plot_info") != threadpool_data.get("plot_info"):
            check_result["data_consistency"] = False
            check_result["differences"].append("剧情分析不一致: serial vs threadpool")
        
        # 检查爽点识别
        if serial_data.get("satisfaction_info") != langgraph_data.get("satisfaction_info"):
            check_result["data_consistency"] = False
            check_result["differences"].append("爽点识别不一致: serial vs langgraph")
            
        if serial_data.get("satisfaction_info") != threadpool_data.get("satisfaction_info"):
            check_result["data_consistency"] = False
            check_result["differences"].append("爽点识别不一致: serial vs threadpool")
    
    return check_result


def test_batch_performance(file_paths: List[str], output_dir: str = "test_output") -> Dict[str, Any]:
    """
    测试批量文件的串行与并行处理性能
    
    Args:
        file_paths: 测试文件路径列表
        output_dir: 输出目录
        
    Returns:
        批量性能测试结果
    """
    print(f"测试批量处理: {len(file_paths)}个文件")
    results = {}
    
    # 测试串行批量处理
    print("  运行串行批量处理...")
    start_time = time.time()
    serial_result = batch_extract_novel_info(file_paths, output_dir, parallel=False)
    serial_time = time.time() - start_time
    results["serial"] = {
        "time": serial_time,
        "successful": serial_result.get("successful_extractions", 0),
        "failed": serial_result.get("failed_extractions", 0),
        "result": serial_result
    }
    print(f"    串行批量处理耗时: {serial_time:.2f}秒")
    
    # 测试并行批量处理
    print("  运行并行批量处理...")
    start_time = time.time()
    parallel_result = batch_extract_novel_info(file_paths, output_dir, parallel=True, parallel_method="langgraph")
    parallel_time = time.time() - start_time
    results["parallel"] = {
        "time": parallel_time,
        "successful": parallel_result.get("successful_extractions", 0),
        "failed": parallel_result.get("failed_extractions", 0),
        "result": parallel_result
    }
    print(f"    并行批量处理耗时: {parallel_time:.2f}秒")
    
    # 计算性能提升
    if serial_time > 0:
        results["speedup"] = serial_time / parallel_time if parallel_time > 0 else 0
        print(f"    并行批量处理加速比: {results['speedup']:.2f}x")
    
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
        print("未找到测试文件，请确保data/novels目录中有.txt文件")
        return
    
    # 限制测试文件数量
    test_files = test_files[:3]  # 最多测试3个文件
    
    # 运行单文件测试
    single_file_results = {}
    for file_path in test_files:
        single_file_results[os.path.basename(file_path)] = test_single_file_performance(file_path)
        print()
    
    # 运行批量测试
    batch_results = test_batch_performance(test_files)
    
    # 汇总结果
    summary = {
        "single_file_tests": single_file_results,
        "batch_test": batch_results,
        "test_files": [os.path.basename(f) for f in test_files],
        "test_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # 保存测试结果
    with open("test_output/performance_test_results.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print("测试完成！结果已保存到 test_output/performance_test_results.json")
    
    # 打印简要总结
    print("\n=== 性能测试总结 ===")
    for filename, result in single_file_results.items():
        print(f"\n文件: {filename}")
        print(f"  串行耗时: {result['serial']['time']:.2f}秒")
        print(f"  LangGraph并行耗时: {result['langgraph_parallel']['time']:.2f}秒")
        print(f"  ThreadPool并行耗时: {result['threadpool_parallel']['time']:.2f}秒")
        print(f"  LangGraph加速比: {result.get('langgraph_speedup', 0):.2f}x")
        print(f"  ThreadPool加速比: {result.get('threadpool_speedup', 0):.2f}x")
        print(f"  结果一致性: {'通过' if result['consistency_check']['data_consistency'] else '未通过'}")
    
    print(f"\n批量处理:")
    print(f"  串行耗时: {batch_results['serial']['time']:.2f}秒")
    print(f"  并行耗时: {batch_results['parallel']['time']:.2f}秒")
    print(f"  并行加速比: {batch_results.get('speedup', 0):.2f}x")


if __name__ == "__main__":
    main()