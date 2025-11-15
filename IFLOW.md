# ShareNovel 项目概览

ShareNovel 是一个基于 Python 的小说信息提取和处理系统，使用 LangChain 框架和大型语言模型（LLM）来分析小说内容、提取关键信息和角色数据。

## 开发环境
使用conda activate langchain激活，不需要额外安装依赖。

## 项目架构

- **技术栈**: Python 3+, LangChain, OpenAI API, Playwright
- **核心功能**: 小说信息提取、角色识别、网络爬虫
- **处理模式**: 支持单文件和批量异步处理
- **输出格式**: JSON 格式的结构化数据

## 项目结构

```
sharebook2/
├── main.py                 # 项目入口脚本
├── src/                    # 源代码目录
│   ├── api/               # API 接口层
│   │   └── cli/           # 命令行接口
│   ├── core/              # 核心功能模块
│   │   └── agents/        # AI 代理实现
│   ├── services/          # 业务服务层
│   │   ├── extraction/    # 信息提取服务
│   │   ├── extraction_character/  # 角色提取服务
│   │   └── crawling/      # 网络爬虫服务
│   └── utils/             # 工具函数
├── config/                # 配置文件
├── data/                  # 数据目录
│   ├── raw/              # 原始小说文件
│   ├── cleaned_novel/    # 清理后的小说
│   ├── output/           # 提取结果输出
│   └── characters/       # 角色数据
├── docs/                  # 文档
├── tests/                 # 测试文件
└── requirements.txt       # 项目依赖
```

## 主要功能模块

### 1. 小说信息提取 (`src/services/extraction/`)
- 从小说文本中提取关键信息（情节、人物、场景等）
- 支持单文件和批量处理
- 使用异步IO提高处理效率
- 输出结构化的JSON数据

### 2. 角色提取系统 (`src/services/extraction_character/`)
- 专门用于提取和识别小说中的角色信息
- 支持进度跟踪和断点续传
- 输出CSV格式的角色数据表

### 3. 网络爬虫 (`src/services/crawling/`)
- 使用 Playwright 进行网页爬取
- 支持从网站获取小说内容
- 自动处理分页和内容提取

## 安装和设置

1. **安装依赖**:
   ```bash
   pip install -r requirements.txt
   ```

2. **配置LLM**:
   - 编辑 `config/llm_config.py` 文件
   - 设置API_BASE、MODEL_NAME和API_KEY
   - 支持本地部署的LLM服务和云端API

## 使用方法

### 基础信息提取

```bash
# 单文件提取
python main.py extract -f path/to/novel.txt -o data/output

# 批量提取目录中的所有小说
python main.py extract -d data/raw -o data/output

# 直接使用模块
python -m src.services.extraction.main data/raw --processes 2 --output data/output
```

### 角色提取系统

```bash
# 查看角色提取进度
python src/services/extraction_character/main.py --progress

# 运行完整角色提取
python src/services/extraction_character/main.py

# 重置进度并重新开始
python src/services/extraction_character/main.py --reset

# 自定义路径
python src/services/extraction_character/main.py --novel-path path/to/novels --csv-path path/to/output.csv
```

### 网络爬虫

```bash
# 爬取小说内容
python main.py crawl https://example.com/novel -o data/raw
```

## 开发指南

### 代码规范
- 使用 Black 进行代码格式化
- 使用 Flake8 进行代码检查
- 使用 MyPy 进行类型检查

### 测试
```bash
# 运行测试
pytest

# 运行特定测试
pytest tests/unit/
```

### 日志系统
- 日志文件位于 `logs/` 目录
- 按模块分类：agent、api、data、error、general、performance、security、system
- 配置文件：`config/logging_config.py` 和 `config/logging_config.json`

## 配置说明

### LLM配置 (`config/llm_config.py`)
- 支持本地和云端LLM服务
- 可配置超时时间、重试次数、温度参数等
- 默认使用本地部署的vLLM服务

### 日志配置 (`config/logging_config.py`)
- 支持多级别日志记录
- 可配置输出格式和存储位置
- 按模块和日期自动分割日志文件

## 性能优化

1. **异步处理**: 使用异步IO和信号量控制并发数量
2. **批量处理**: 支持多文件并行处理
3. **断点续传**: 角色提取支持进度跟踪和恢复
4. **资源控制**: 通过信号量限制最大并发数，避免资源耗尽

## 故障排除

1. **文件路径问题**: 确保使用绝对路径或正确的相对路径
2. **权限问题**: 检查输出目录的读写权限
3. **API连接问题**: 验证LLM服务的连接状态和配置
4. **内存问题**: 调整并发处理数量，避免内存溢出

## 扩展开发

- 新增提取功能：在 `src/services/extraction/` 下创建新模块
- 新增Agent：在 `src/core/agents/` 下实现新的代理
- 新增CLI命令：在 `src/api/cli/main.py` 中添加新的子命令

## 注意事项

- 确保有足够的磁盘空间存储输出文件
- 大文件处理时注意内存使用情况
- 定期清理日志文件避免占用过多空间
- 使用本地LLM服务时确保硬件配置满足要求