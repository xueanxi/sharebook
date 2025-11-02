# 统一日志管理系统

本项目已实现统一的日志管理系统，支持日志分类功能，可以根据不同的程序模块选择不同的日志类型。

## 功能特点

1. **日志分类**：支持通用日志、Agent日志、API日志、数据处理日志、系统日志、错误日志、性能日志和安全日志等多种分类
2. **自动文件管理**：自动创建日志目录和文件，按日期和分类组织
3. **日志轮转**：支持日志文件大小限制和自动轮转
4. **灵活配置**：支持通过JSON配置文件自定义日志格式和级别
5. **装饰器支持**：提供便捷的装饰器用于记录函数执行时间和Agent处理过程
6. **向后兼容**：保持与原有日志系统的兼容性

## 日志分类

| 分类 | 描述 | 适用场景 |
|------|------|----------|
| GENERAL | 通用日志 | 一般程序信息 |
| AGENT | Agent日志 | Agent处理过程记录 |
| API | API日志 | API请求和响应 |
| DATA | 数据处理日志 | 数据预处理、转换等 |
| SYSTEM | 系统日志 | 系统状态、资源使用等 |
| ERROR | 错误日志 | 错误和异常信息 |
| PERFORMANCE | 性能日志 | 性能指标、执行时间等 |
| SECURITY | 安全日志 | 安全相关事件 |

## 使用方法

### 1. 获取不同类型的日志记录器

```python
from src.utils.logging_manager import (
    get_logger,
    get_agent_logger,
    get_api_logger,
    get_data_logger,
    get_system_logger,
    get_error_logger,
    get_performance_logger,
    get_security_logger
)

# 获取通用日志记录器
general_logger = get_logger("my_module")

# 获取Agent日志记录器
agent_logger = get_agent_logger("character_extractor")

# 获取API日志记录器
api_logger = get_api_logger("novel_api")

# 获取数据处理日志记录器
data_logger = get_data_logger("text_preprocessor")

# 获取系统日志记录器
system_logger = get_system_logger("system_monitor")

# 获取错误日志记录器
error_logger = get_error_logger("error_handler")

# 获取性能日志记录器
performance_logger = get_performance_logger("performance_monitor")

# 获取安全日志记录器
security_logger = get_security_logger("security_manager")
```

### 2. 记录日志

```python
# 记录不同级别的日志
logger.info("信息日志")
logger.warning("警告日志")
logger.error("错误日志")
logger.debug("调试日志")

# 记录异常信息
try:
    # 可能出错的代码
    result = 1 / 0
except Exception as e:
    logger.error(f"发生错误: {str(e)}", exc_info=True)
```

### 3. 使用装饰器

```python
from src.utils.logging_manager import log_execution_time, log_agent_process

# 记录函数执行时间
@log_execution_time()
def slow_function():
    time.sleep(1)
    return "函数执行完成"

# 记录Agent处理过程
class MyAgent:
    @log_agent_process
    def process(self, state):
        # 处理逻辑
        return {"result": "处理完成"}
```

### 4. 配置日志系统

```python
from src.utils.logging_manager import log_manager

# 设置日志级别
log_manager.set_level(logging.INFO)

# 更新配置
log_manager.configure(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    console_output=True,
    file_output=True
)
```

### 5. 获取日志文件列表

```python
# 获取所有日志文件列表
all_log_files = log_manager.get_log_files()

# 获取特定分类的日志文件列表
agent_log_files = log_manager.get_log_files(LogCategory.AGENT)
```

## 配置文件

日志系统支持通过JSON配置文件进行自定义配置。配置文件位于 `config/logging_config.json`。

```json
{
  "level": 20,
  "format": "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
  "date_format": "%Y-%m-%d %H:%M:%S",
  "console_output": true,
  "file_output": true,
  "max_file_size": 10485760,
  "backup_count": 5,
  "encoding": "utf-8",
  "categories": {
    "general": {
      "level": 20,
      "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    },
    "agent": {
      "level": 10,
      "format": "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
    }
  }
}
```

## 日志文件结构

日志文件按以下结构组织：

```
logs/
├── general/          # 通用日志
├── agent/            # Agent日志
├── api/              # API日志
├── data/             # 数据处理日志
├── system/           # 系统日志
├── error/            # 错误日志
├── performance/      # 性能日志
└── security/         # 安全日志
```

每个分类下的日志文件按日期命名，例如：`my_module_20231201.log`

## 向后兼容

为了保持与原有代码的兼容性，原有的 `config/logging_config.py` 文件仍然可用，但内部已重定向到新的日志管理系统。

```python
# 原有代码仍然可以正常工作
from config.logging_config import get_logger
logger = get_logger("my_module")
logger.info("这是一条日志")
```

## 最佳实践

1. **选择合适的日志分类**：根据代码功能选择对应的日志分类，便于后续分析和排查问题
2. **使用装饰器**：对于需要记录执行时间的函数，使用 `@log_execution_time` 装饰器
3. **Agent处理日志**：对于Agent的process方法，使用 `@log_agent_process` 装饰器
4. **异常记录**：记录异常时使用 `exc_info=True` 参数，包含完整的堆栈信息
5. **日志级别**：合理使用不同的日志级别，避免在生产环境中输出过多调试信息

## 示例代码

完整的使用示例请参考 `examples/logging_example.py` 文件。