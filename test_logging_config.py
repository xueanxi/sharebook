"""
测试日志记录器是否正确配置
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.logging_manager import get_agent_logger, log_manager

# 获取Agent日志记录器
logger = get_agent_logger("test_logging")

# 检查日志记录器的处理器
print(f"日志记录器名称: {logger.name}")
print(f"日志记录器级别: {logger.level}")
print(f"日志记录器处理器数量: {len(logger.handlers)}")

for i, handler in enumerate(logger.handlers):
    print(f"处理器 {i+1}: {type(handler).__name__}")
    print(f"  级别: {handler.level}")
    print(f"  格式化器: {type(handler.formatter).__name__}")

# 测试日志输出
print("\n测试日志输出:")
logger.debug("这是一条DEBUG级别的消息")
logger.info("这是一条INFO级别的消息")
logger.warning("这是一条WARNING级别的消息")
logger.error("这是一条ERROR级别的消息")

# 检查日志管理器的配置
print("\n日志管理器配置:")
print(f"console_output: {log_manager._config['console_output']}")
print(f"file_output: {log_manager._config['file_output']}")

# 检查agent分类配置
from src.utils.logging_manager import LogCategory
agent_config = log_manager._get_category_config(LogCategory.AGENT)
print(f"\nAgent分类配置:")
print(f"level: {agent_config['level']}")
print(f"console_level: {agent_config.get('console_level', 'Not set')}")
print(f"file_level: {agent_config.get('file_level', 'Not set')}")