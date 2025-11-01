#!/usr/bin/env python3
"""
测试文件夹输入功能
"""

import os
import sys
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.services.extraction.main import scan_novel_files, batch_extract_novel_info


def test_folder_input():
    """测试文件夹输入功能"""
    
    # 测试文件夹路径
    folder_path = "data/raw"
    output_dir = "data/output"
    
    if not os.path.exists(folder_path):
        print(f"测试文件夹 {folder_path} 不存在")
        return
    
    print(f"测试文件夹: {folder_path}")
    
    # 测试扫描文件夹功能
    try:
        file_paths = scan_novel_files(folder_path)
        print(f"扫描到 {len(file_paths)} 个小说文件")
        
        # 只显示前5个文件名
        for i, file_path in enumerate(file_paths[:5]):
            print(f"  {i+1}. {os.path.basename(file_path)}")
        
        if len(file_paths) > 5:
            print(f"  ... 还有 {len(file_paths) - 5} 个文件")
        
        # 测试多进程处理（限制文件数量以避免测试时间过长）
        test_files = file_paths[:3]
        print(f"\n使用多进程处理前 {len(test_files)} 个文件...")
        
        start_time = time.time()
        result = batch_extract_novel_info(test_files, output_dir, 2)
        end_time = time.time()
        
        print(f"处理完成，耗时: {end_time - start_time:.2f} 秒")
        print(f"成功处理: {result['successful_extractions']} 个文件")
        print(f"失败处理: {result['failed_extractions']} 个文件")
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")


if __name__ == "__main__":
    test_folder_input()