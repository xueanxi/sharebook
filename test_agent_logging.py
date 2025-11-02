"""
测试Agent日志输出
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.agents.info_extract.text_preprocessor import TextPreprocessor
from src.core.agents.info_extract.base import NovelExtractionState

# 创建TextPreprocessor实例
preprocessor = TextPreprocessor()

# 创建测试状态
test_state = NovelExtractionState(
    text="这是一个测试文本，用于验证Agent日志输出是否正常。",
    preprocessed_text="",
    character_info={},
    plot_info={},
    satisfaction_info={},
    completed_tasks=[],
    errors=[],
    preprocess_done=False,
    character_done=False,
    plot_done=False,
    satisfaction_done=False
)

# 处理文本
print("开始处理文本...")
preprocessor.process(test_state)
print("处理完成。")

# 检查结果
print(f"预处理后的文本: {test_state['preprocessed_text']}")
print(f"完成的任务: {test_state['completed_tasks']}")