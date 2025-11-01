# ShareNovel

一个用于小说内容爬取、处理和分析的工具集。

## 项目结构

```
sharenovel/
├── src/                     # 源代码
│   ├── core/               # 核心模块
│   │   └── agents/         # 智能体实现
│   ├── services/           # 服务模块
│   │   ├── extraction/     # 信息提取服务
│   │   └── crawling/       # 爬虫服务
│   ├── utils/              # 工具模块
│   │   ├── text_processing/ # 文本处理工具
│   │   └── file_handling/  # 文件处理工具
│   └── api/                # 接口模块
│       └── cli/            # 命令行接口
├── tests/                  # 测试代码
│   ├── unit/              # 单元测试
│   └── integration/       # 集成测试
├── docs/                   # 文档
│   ├── api/               # API文档
│   └── user_guide/        # 用户指南
├── data/                   # 数据目录
│   ├── raw/               # 原始数据
│   ├── processed/         # 处理后数据
│   └── output/            # 输出数据
├── scripts/               # 脚本目录
├── main.py                # 项目入口脚本
└── requirements.txt       # 项目依赖
```

## 功能特性

- **小说内容爬取**: 自动爬取指定网站的小说章节内容
- **信息提取**: 从小说文本中提取人物、情节、爽点等信息
- **智能分析**: 使用LLM进行深度文本分析
- **批量处理**: 支持批量处理多个小说文件
- **命令行接口**: 提供简洁的CLI界面

## 安装与使用

### 环境要求

- Python 3.8+
- pip

### 安装依赖

```bash
pip install -r requirements.txt
```

### 使用方法

#### 1. 爬取小说内容

```bash
python main.py crawl
```

#### 2. 提取单篇小说信息

```bash
python main.py extract -f data/raw/小说文件.txt
```

#### 3. 批量提取信息

```bash
python main.py extract -d data/raw
```

#### 4. 指定输出目录

```bash
python main.py extract -f data/raw/小说文件.txt -o data/output
```

## 开发指南

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/unit/test_extraction.py
```

### 代码格式化

```bash
black src/ tests/
```

### 类型检查

```bash
mypy src/
```

## 配置说明

项目配置文件位于 `config/` 目录下，主要包括：

- `llm_config.py`: LLM相关配置
- `crawl_config.py`: 爬虫相关配置

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。