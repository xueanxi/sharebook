#!/usr/bin/env python3
"""
ShareNovel 项目入口脚本
提供统一的入口点来访问项目功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.api.cli.main import main

if __name__ == "__main__":
    main()