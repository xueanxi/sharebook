# ShareNovel 项目概览

ShareNovel 是一个基于 Python 的小说信息提取和处理系统，使用 LangChain 框架和大型语言模型（LLM）来分析小说内容、提取关键信息和角色数据，并支持将小说转换为漫画故事板和生成角色图片。

## 开发环境
使用conda activate langchain激活，不需要额外安装依赖。

## 项目架构

- **技术栈**: Python 3+, LangChain, OpenAI API, Playwright, ComfyUI
- **核心功能**: 小说信息提取、角色识别、网络爬虫、角色图片生成、小说转漫画故事板
- **处理模式**: 支持单文件和批量异步处理
- **输出格式**: JSON 格式的结构化数据、CSV格式角色数据、图片文件

## 项目结构

```
sharebook2/
├── main.py                 # 项目入口脚本
├── batch_generate_images.py # 批量生成角色图片脚本
├── src/                    # 源代码目录
│   ├── api/               # API 接口层
│   │   └── cli/           # 命令行接口
│   ├── core/              # 核心功能模块
│   │   └── agents/        # AI 代理实现
│   │       ├── info_extract/    # 信息提取代理
│   │       └── content_creation/ # 内容创建代理
│   ├── services/          # 业务服务层
│   │   ├── extraction/    # 信息提取服务
│   │   ├── extraction_character/  # 角色提取服务
│   │   ├── crawling/      # 网络爬虫服务
│   │   ├── character_image_generation/  # 角色图片生成服务
│   │   ├── comic_image_generation/     # 漫画图片生成服务
│   │   ├── novel_to_comic/             # 小说转漫画服务
│   │   └── storyboard_to_prompt/       # 故事板到提示词转换服务
│   └── utils/             # 工具函数
├── config/                # 配置文件
│   ├── embeddings_config.py  # 嵌入模型配置
│   ├── llm_config.py         # LLM配置
│   ├── logging_config.py     # 日志配置
│   └── logging_config.json   # 日志配置JSON
├── data/                  # 数据目录
│   ├── raw/              # 原始小说文件
│   ├── cleaned_novel/    # 清理后的小说
│   ├── output/           # 提取结果输出
│   ├── characters/       # 角色数据和图片
│   ├── storyboards/      # 故事板数据
│   ├── storyboards_image/ # 故事板图片
│   └── storyboards_prompt/ # 故事板提示词
├── comfyui/              # ComfyUI工作流配置
├── docs/                 # 文档
├── tests/                # 测试文件
└── requirements.txt      # 项目依赖
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

### 4. 角色图片生成 (`src/services/character_image_generation/`)
- 基于ComfyUI的角色图片生成
- 支持批量生成和单个角色生成
- 支持断点续传和跳过已生成图片
- 提供多种Flux模型工作流

### 5. 小说转漫画故事板 (`src/services/novel_to_comic/`)
- 将小说章节转换为漫画故事板
- 支持场景分割和画面描述生成
- 提供并行处理能力
- 输出结构化故事板数据和提示词

### 6. 故事板到提示词转换 (`src/services/storyboard_to_prompt/`)
- 将故事板数据转换为图像生成提示词
- 支持多种风格和参数配置
- 优化提示词质量

## 安装和设置

1. **安装依赖**:
   ```bash
   pip install -r requirements.txt
   ```

2. **配置LLM**:
   - 编辑 `config/llm_config.py` 文件
   - 设置API_BASE、MODEL_NAME和API_KEY
   - 支持本地部署的LLM服务和云端API

3. **配置ComfyUI** (用于图片生成):
   - 确保ComfyUI服务器正在运行
   - 根据需要修改 `comfyui/` 目录下的工作流配置文件

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

### 角色图片生成

```bash
# 批量生成所有角色图片
python -m src.services.character_image_generation.main --all

# 生成指定角色图片
python -m src.services.character_image_generation.main --name "搬山宗宗主"

# 批量生成多个角色
python -m src.services.character_image_generation.main --names "搬山宗宗主,叶师弟,灵儿"

# 使用项目根目录的批量脚本
python batch_generate_images.py --batch-size 2

# 测试ComfyUI连接
python -m src.services.character_image_generation.main --test
```

### 小说转漫画故事板

```bash
# 处理单个章节
python -m src.services.novel_to_comic.main -f path/to/chapter.txt -t "章节标题"

# 批量处理目录中的所有章节
python -m src.services.novel_to_comic.main -d data/cleaned_novel

# 自动模式（处理默认目录）
python -m src.services.novel_to_comic.main --auto

# 启用并行处理
python -m src.services.novel_to_comic.main --auto --parallel
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
- 支持ModelScope等云端API

### 日志配置 (`config/logging_config.py`)
- 支持多级别日志记录
- 可配置输出格式和存储位置
- 按模块和日期自动分割日志文件

### ComfyUI配置
- 工作流模板位于 `comfyui/` 目录
- 支持Flux和Flux+PuLID模型
- 可自定义工作流参数

## 性能优化

1. **异步处理**: 使用异步IO和信号量控制并发数量
2. **批量处理**: 支持多文件并行处理
3. **断点续传**: 角色提取和图片生成支持进度跟踪和恢复
4. **资源控制**: 通过信号量限制最大并发数，避免资源耗尽
5. **并行场景分割**: 小说转漫画支持并行场景分割（最多5个并发）

## 故障排除

1. **文件路径问题**: 确保使用绝对路径或正确的相对路径
2. **权限问题**: 检查输出目录的读写权限
3. **API连接问题**: 验证LLM服务的连接状态和配置
4. **ComfyUI连接问题**: 确保ComfyUI服务器正在运行并可访问
5. **内存问题**: 调整并发处理数量，避免内存溢出

## 扩展开发

- 新增提取功能：在 `src/services/extraction/` 下创建新模块
- 新增Agent：在 `src/core/agents/` 下实现新的代理
- 新增CLI命令：在 `src/api/cli/main.py` 中添加新的子命令
- 新增图片生成服务：在 `src/services/` 下创建新的生成模块

## 注意事项

- 确保有足够的磁盘空间存储输出文件和生成的图片
- 大文件处理时注意内存使用情况
- 定期清理日志文件避免占用过多空间
- 使用本地LLM服务时确保硬件配置满足要求
- 图片生成需要ComfyUI服务器支持，确保相关依赖已安装
- 并行处理功能会提高处理速度但也会增加资源消耗