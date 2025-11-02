"""
日志系统使用示例
展示如何使用新的统一日志管理系统
"""

import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.logging_manager import (
    get_logger,
    get_agent_logger,
    get_api_logger,
    get_data_logger,
    get_system_logger,
    get_error_logger,
    get_performance_logger,
    get_security_logger,
    LogCategory,
    log_execution_time,
    log_agent_process,
    log_manager
)

# 示例1: 使用通用日志
general_logger = get_logger("example_module")
general_logger.info("这是一条通用日志信息")

# 示例2: 使用Agent日志
agent_logger = get_agent_logger("character_extractor")
agent_logger.info("Agent开始处理文本")

# 示例3: 使用API日志
api_logger = get_api_logger("novel_api")
api_logger.info("API请求开始")

# 示例4: 使用数据处理日志
data_logger = get_data_logger("text_preprocessor")
data_logger.info("开始预处理文本")

# 示例5: 使用系统日志
system_logger = get_system_logger("system_monitor")
system_logger.info("系统状态检查")

# 示例6: 使用错误日志
error_logger = get_error_logger("error_handler")
try:
    # 模拟一个错误
    result = 1 / 0
except Exception as e:
    error_logger.error(f"发生错误: {str(e)}", exc_info=True)

# 示例7: 使用性能日志
performance_logger = get_performance_logger("performance_monitor")
performance_logger.info("性能指标记录")

# 示例8: 使用安全日志
security_logger = get_security_logger("security_manager")
security_logger.info("安全事件记录")

# 示例9: 使用装饰器记录函数执行时间
@log_execution_time()
def slow_function():
    """模拟一个耗时函数"""
    time.sleep(1)
    return "函数执行完成"

result = slow_function()

# 示例10: 使用装饰器记录Agent处理过程
class ExampleAgent:
    """示例Agent类"""
    
    @log_agent_process
    def process(self, state):
        """处理状态的方法"""
        time.sleep(0.5)  # 模拟处理时间
        return {"result": "处理完成"}

# 创建Agent实例并调用处理方法
agent = ExampleAgent()
agent.process({"text": "示例文本"})

# 示例11: 配置日志级别
log_manager.set_level(20)  # 设置为INFO级别

# 示例12: 获取日志文件列表
log_files = log_manager.get_log_files()
print("日志文件列表:", log_files)

# 示例13: 获取特定分类的日志文件
agent_log_files = log_manager.get_log_files(LogCategory.AGENT)
print("Agent日志文件列表:", agent_log_files)

print("日志系统示例执行完成！")