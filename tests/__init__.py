"""
测试模块初始化文件
提供便捷的测试运行接口
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("开始运行所有测试...")
    print("=" * 50)
    
    # 运行单个Agent测试
    from tests.unit.test_individual_agents import run_single_agent_tests
    single_agent_success = run_single_agent_tests()
    
    # 运行完整信息提取测试
    from tests.integration.test_complete_extraction import run_complete_extraction_tests
    complete_extraction_success = run_complete_extraction_tests()
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print(f"单个Agent测试: {'通过' if single_agent_success else '失败'}")
    print(f"完整信息提取测试: {'通过' if complete_extraction_success else '失败'}")
    
    if single_agent_success and complete_extraction_success:
        print("\n✅ 所有测试通过!")
        return True
    else:
        print("\n❌ 部分测试失败!")
        return False


def run_individual_agent_tests():
    """仅运行单个Agent测试"""
    from tests.unit.test_individual_agents import run_single_agent_tests
    return run_single_agent_tests()


def run_complete_extraction_tests():
    """仅运行完整信息提取测试"""
    from tests.integration.test_complete_extraction import run_complete_extraction_tests
    return run_complete_extraction_tests()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)