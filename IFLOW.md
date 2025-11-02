# ShareBook 项目说明

## 项目概述

ShareBook 是一个基于 Python 的小说处理和分析工具，主要功能是从小说文本中提取关键信息，包括人物信息、剧情分析和爽点识别。项目使用 LangChain 和 LangGraph 框架实现并行处理，支持单文件和批量文件处理。

## 核心技术栈

- **Python 3.x**: 主要编程语言
- **LangChain**: LLM 应用框架
- **LangGraph**: 用于构建并行处理工作流
- **OpenAI API**: 语言模型接口（兼容本地部署模型）
- **Playwright**: 网页爬虫工具
- **Pandas/NumPy**: 数据处理
- **Pydantic**: 数据验证和配置管理

## 项目结构

```
sharebook/
├── main.py                    # 项目入口脚本
├── src/                       # 源代码目录
│   ├── api/                   # API 接口
│   │   └── cli/               # 命令行接口
│   ├── core/                  # 核心功能
│   │   └── agents/            # 智能代理
│   │       └── info_extract/  # 信息提取模块
│   └── services/              # 服务层
│       ├── crawling/          # 爬虫服务
│       └── extraction/        # 提取服务
├── config/                    # 配置文件
│   ├── llm_config.py          # LLM 配置
│   ├── embeddings_config.py   # 嵌入配置
│   └── logging_config.py      # 日志配置
├── data/                      # 数据目录
│   ├── raw/                   # 原始数据
│   ├── processed/             # 处理后数据
│   └── output/                # 输出结果
└── tests/                     # 测试代码
```

## 安装和配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 LLM

编辑 `config/llm_config.py` 文件，配置您的 LLM 服务：

```python
# 本地vllm示例
API_BASE = "http://127.0.0.1:8000/v1"
MODEL_NAME = "local-llm"
API_KEY = "123"

# 或者使用远程服务
API_BASE = "http://192.168.3.46:8000/v1"
MODEL_NAME = "local-llm"
API_KEY = "123"
```

## 使用方法

### 命令行接口

#### 提取小说信息

**单文件处理:**
```bash
python main.py extract -f data/raw/小说文件.txt -o data/output
```

**批量处理:**
```bash
python main.py extract -d data/raw -o data/output
```

**使用模块直接调用:**
```bash
python -m src.services.extraction.main data/raw --processes 1 --output data/output
```

#### 爬取小说内容

```bash
python main.py crawl https://小说网站URL -o data_crawl_novel
```

### 编程接口

#### 单文件信息提取

```python
from src.services.extraction.main import extract_novel_information

result = extract_novel_information("data/raw/小说文件.txt", "data/output")
```

#### 批量处理

```python
from src.services.extraction.main import batch_extract_novel_info

file_paths = ["file1.txt", "file2.txt", "file3.txt"]
result = batch_extract_novel_info(file_paths, "data/output", num_processes=4)
```

## 核心功能

### 1. 信息提取

项目使用多个专门的 Agent 并行处理小说文本：

- **文本预处理器** (TextPreprocessor): 清洗和预处理文本
- **人物提取器** (CharacterExtractor): 识别人物信息
- **剧情分析器** (PlotAnalyzer): 分析剧情发展
- **爽点识别器** (SatisfactionPointIdentifier): 识别读者爽点

### 2. 并行处理架构

使用 LangGraph 实现并行处理工作流，提高处理效率：

1. 文本预处理完成后，并行启动人物提取、剧情分析和爽点识别
2. 所有任务完成后合并结果
3. 支持多进程批量处理多个文件

### 3. 爬虫功能

集成 Playwright 爬虫，可以从网站自动抓取小说内容。

## 输出格式

提取结果以 JSON 格式保存，包含以下信息：

```json
{
  "characters": {
    "success": true,
    "result": "人物信息",
    "agent": "人物提取器"
  },
  "plot": {
    "success": true,
    "result": "剧情分析",
    "agent": "剧情分析器"
  },
  "satisfaction_points": {
    "success": true,
    "result": "爽点识别",
    "agent": "爽点识别器"
  },
  "original_text_length": 字符数,
  "cleaned_text_length": 清洗后字符数,
  "errors": [],
  "completed_tasks": ["任务列表"],
  "parallel_execution": true
}
```

## 开发和测试

### 运行测试

```bash
pytest tests/
```

### 代码格式化

```bash
black src/
```

### 类型检查

```bash
mypy src/
```

## 配置说明

### LLM 配置

在 `config/llm_config.py` 中配置：

- `API_BASE`: LLM 服务的 API 地址
- `MODEL_NAME`: 使用的模型名称
- `API_KEY`: API 密钥
- `TIMEOUT`: 请求超时时间
- `MAX_RETRIES`: 最大重试次数
- `TEMPERATURE`: 温度参数

### 日志配置

在 `config/logging_config.py` 中配置日志级别和输出格式。

## 常见问题

1. **LLM 连接失败**: 检查 `config/llm_config.py` 中的 API 配置是否正确
2. **内存不足**: 减少并行处理的进程数或处理较小的文件
3. **编码问题**: 确保小说文件使用 UTF-8 编码

## 扩展开发

### 添加新的提取器

1. 继承 `BaseExtractor` 类
2. 实现 `extract` 和 `process` 方法
3. 在 `NovelInformationExtractor` 中集成新的提取器

### 修改处理流程

编辑 `src/core/agents/info_extract/novel_extractor.py` 中的工作流图。

## 许可证

本项目采用 MIT 许可证。