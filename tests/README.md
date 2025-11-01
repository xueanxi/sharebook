# 测试文档

## 测试结构

本项目采用分层测试结构，将测试分为单元测试和集成测试，便于维护和扩展。

```
tests/
├── __init__.py                 # 测试模块初始化，提供便捷的测试运行接口
├── test_utils.py               # 测试工具模块，共享测试数据和工具函数
├── unit/                       # 单元测试目录
│   ├── __init__.py
│   ├── test_extraction.py      # 原有的提取测试
│   └── test_individual_agents.py  # 单个Agent功能测试
└── integration/                # 集成测试目录
    ├── __init__.py
    └── test_complete_extraction.py  # 完整信息提取功能测试
```

## 测试文件说明

### 1. test_utils.py
测试工具模块，提供以下功能：
- 获取测试数据路径和内容
- 保存测试结果到JSON文件
- 打印测试结果
- 检查Agent结果是否有效

### 2. test_individual_agents.py
单个Agent功能测试，包含以下测试类：
- `TestSingleAgent`: 测试各个Agent的基本功能
  - `test_text_preprocessor`: 测试文本预处理Agent
  - `test_character_extractor`: 测试人物提取Agent
  - `test_plot_analyzer`: 测试剧情分析Agent
  - `test_satisfaction_identifier`: 测试爽点识别Agent

### 3. test_complete_extraction.py
完整信息提取功能测试，包含以下测试类：
- `TestCompleteExtraction`: 测试完整信息提取功能
  - `test_parallel_extraction`: 测试并行信息提取功能
  - `test_sequential_extraction`: 测试顺序信息提取功能
  - `test_performance_comparison`: 测试并行与顺序提取的性能对比

## 运行测试

### 方法1: 使用测试运行脚本
```bash
# 运行所有测试
python run_tests.py

# 运行单个Agent测试
python run_tests.py --type individual

# 运行完整信息提取测试
python run_tests.py --type complete
```

### 方法2: 直接运行测试文件
```bash
# 运行单个Agent测试
python tests/unit/test_individual_agents.py

# 运行完整信息提取测试
python tests/integration/test_complete_extraction.py
```

### 方法3: 使用tests模块接口
```bash
# 运行所有测试
python -m tests

# 或者
python tests/__init__.py
```

### 方法4: 使用pytest
```bash
# 运行所有测试
pytest tests/

# 运行单个Agent测试
pytest tests/unit/test_individual_agents.py

# 运行完整信息提取测试
pytest tests/integration/test_complete_extraction.py
```

## 测试结果

测试结果将保存在 `test_results/` 目录下：
- `parallel_extraction_result.json`: 并行提取结果
- `sequential_extraction_result.json`: 顺序提取结果
- `performance_comparison.json`: 性能对比结果

## 注意事项

1. 确保测试数据文件 `data/raw/第一章 遇强则强.txt` 存在
2. 测试过程中会创建 `test_results/` 目录用于保存结果
3. 测试可能会花费较长时间，特别是性能对比测试
4. 如果测试失败，请检查错误信息并确保所有依赖项正确安装