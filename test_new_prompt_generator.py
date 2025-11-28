#!/usr/bin/env python3
"""
测试新的提示词生成功能
"""

import os
import sys
import json
from pathlib import Path

# 获取项目根目录
current_file = os.path.abspath(__file__)
root_path = os.path.dirname(current_file)
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from src.services.storyboard_to_prompt.prompt_generator import PromptGenerator
from src.utils.logging_manager import LogModule, get_module_logger

logger = get_module_logger(LogModule.STORYBOARD_TO_PROMPT)

from config.llm_config import LLMConfig
from openai import OpenAI


def main():
    
    
    print("测试完成！")

if __name__ == "__main__":
    main()