#!/usr/bin/env python3
"""
测试多进程小说信息提取功能
"""

import os
import sys
import time
import glob
from typing import List

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.services.extraction.main import batch_extract_novel_info


def test_multiprocessing():
    """测试多进程处理功能"""
    
    # 获取小说文件列表
    novel_files = glob.glob(os.path.join("data", "raw", "*.txt"))
    
    if not novel_files:
        print("未找到小说文件，请检查 data/raw 目录")
        return
    
    # 限制测试文件数量，避免测试时间过长
    test_files = novel_files[:5]
    output_dir = "data/output"
    
    print(f"测试文件数量: {len(test_files)}")
    print(f"测试文件: {[os.path.basename(f) for f in test_files]}")
    
    # 测试不同进程数的处理时间
    process_counts = [1, 2, 4]
    
    for num_processes in process_counts:
        print(f"\n===== 测试 {num_processes} 个进程 =====")
        start_time = time.time()
        
        result = batch_extract_novel_info(test_files, output_dir, num_processes)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print(f"处理时间: {elapsed_time:.2f} 秒")
        print(f"成功处理: {result['successful_extractions']} 个文件")
        print(f"失败处理: {result['failed_extractions']} 个文件")
        
        if result.get("success", False):
            print("✅ 批量处理成功!")
        else:
            print("❌ 批量处理部分失败!")
            if "error" in result:
                print(f"错误信息: {result['error']}")


if __name__ == "__main__":
    test_multiprocessing()