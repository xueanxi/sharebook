"""
测试Agent日志输出
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path

ddd = "D:\work\code\python\sharebook\data\raw\第四十二章 无敌碾压！.txt"


a = Path(ddd)
print(f'a={a}')
print(f'a.stem={a.stem}')
print(f'a.name={a.name}')
