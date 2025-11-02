# Agents工作流文档

## 概述

本文档详细描述了小说转漫画视频项目中的Agent工作流架构，包括整体工作流设计、各个Agent的功能定义、输入输出标准以及Agent之间的连接方式。

## 整体架构

### 工作流设计原则

1. **模块化设计**：每个Agent专注于特定任务，降低耦合度
2. **并行处理**：利用LangGraph实现任务并行执行，提高处理效率
3. **状态管理**：通过统一的状态对象管理Agent间的数据传递
4. **错误处理**：每个Agent都有独立的错误处理机制，确保系统稳定性

### 技术栈

- **核心框架**：LangChain v1.0.0 + LangGraph
- **语言模型**：OpenAI GPT系列（通过config/llm_config.py配置）
- **状态管理**：TypedDict + operator.add
- **并行处理**：multiprocessing + LangGraph并行节点

## Agent详细说明

### 基础组件

#### BaseAgent

**位置**：`src/core/agents/info_extract/base.py`

**功能**：所有Agent的基类，提供通用功能

**主要方法**：
- `__init__(model_name, temperature)`: 初始化LLM实例
- `_create_chain(prompt_template)`: 创建LCEL处理链
- `_simple_text_cleaning(text)`: 简单文本清洗备用方案

**配置参数**：
- `model_name`: 模型名称，可选，默认使用配置文件中的模型
- `temperature`: 温度参数，控制输出随机性，默认0.7

#### BaseExtractor

**位置**：`src/core/agents/info_extract/base.py`

**功能**：提取器基类，继承自BaseAgent，为信息提取类Agent提供基础功能

**主要方法**：
- `extract(text)`: 提取信息的抽象方法
- `process(state)`: 处理状态的抽象方法

#### NovelExtractionState

**位置**：`src/core/agents/info_extract/base.py`

**功能**：统一的状态管理对象，用于Agent间的数据传递

**状态字段**：
```python
class NovelExtractionState(TypedDict):
    text: str                           # 原始文本
    preprocessed_text: str              # 预处理后的文本
    character_info: Dict[str, Any]      # 人物信息
    plot_info: Dict[str, Any]           # 剧情信息
    satisfaction_info: Dict[str, Any]   # 爽点信息
    completed_tasks: Annotated[List[str], operator.add]  # 已完成任务列表
    errors: Annotated[List[str], operator.add]           # 错误信息列表
    preprocess_done: bool               # 预处理完成标记
    character_done: bool                # 人物提取完成标记
    plot_done: bool                     # 剧情分析完成标记
    satisfaction_done: bool             # 爽点识别完成标记
```

### 信息提取阶段Agents

#### 1. TextPreprocessor（文本预处理器）

**位置**：`src/core/agents/info_extract/text_preprocessor.py`

**功能**：清洗和预处理小说文本，为后续分析做准备

**输入**：
- 原始小说文本（字符串）

**处理流程**：
1. 接收原始文本
2. 使用LLM进行智能文本清洗
3. 如果LLM处理失败，回退到简单清洗方案
4. 返回清洗后的文本

**输出**：
```python
{
    "success": bool,           # 处理是否成功
    "result": str,             # 清洗后的文本
    "error": str,              # 错误信息（如果有）
    "agent": "文本预处理器"    # Agent标识
}
```

**提示词模板**：
```
你是一个专业的文本预处理助手，专门处理小说文本。
你的主要任务是：
1. 清洗文本内容，去除无关字符和格式
2. 确保文本格式统一，便于后续处理
3. 提供文本统计信息

请直接使用你的语言能力进行清洗，提供清晰的总结和清洗后的文本。
```

#### 2. CharacterExtractor（人物提取器）

**位置**：`src/core/agents/info_extract/character_extractor.py`

**功能**：识别和提取小说中的人物信息，包括人物名称、关系和重要性

**输入**：
- 预处理后的文本（字符串）

**处理流程**：
1. 分析文本中的人物名称
2. 统计人物出现频率
3. 分析人物关系和重要性
4. 生成人物分析报告

**输出**：
```python
{
    "success": bool,           # 处理是否成功
    "result": str,             # 人物分析报告
    "error": str,              # 错误信息（如果有）
    "agent": "人物提取器"      # Agent标识
}
```

**提示词模板**：
```
你是一个专业的人物提取助手，专门分析小说文本中的人物。
你的主要任务是：
1. 从小说文本中识别人物名称
2. 统计每个人物的出现次数
3. 分析人物关系和重要性
4. 提供人物列表和相关信息

请直接使用你的语言理解能力来完成这些任务，并提供详细的人物分析报告。
```

#### 3. PlotAnalyzer（剧情分析器）

**位置**：`src/core/agents/info_extract/plot_analyzer.py`

**功能**：分析小说的情节结构，识别关键情节元素

**输入**：
- 预处理后的文本（字符串）

**处理流程**：
1. 分析情节结构
2. 识别关键情节元素（冲突、转折、高潮等）
3. 评估情节复杂度和节奏
4. 生成剧情分析报告

**输出**：
```python
{
    "success": bool,           # 处理是否成功
    "result": str,             # 剧情分析报告
    "error": str,              # 错误信息（如果有）
    "agent": "剧情分析器"      # Agent标识
}
```

**提示词模板**：
```
你是一个专业的剧情分析助手，专门分析小说的情节结构。
你的主要任务是：
1. 分析小说的情节结构
2. 识别关键情节元素（冲突、转折、高潮等）
3. 评估情节复杂度和节奏
4. 提供情节分析报告

请直接使用你的语言理解能力来完成这些任务，并提供详细的剧情分析。
```

#### 4. SatisfactionPointIdentifier（爽点识别器）

**位置**：`src/core/agents/info_extract/satisfaction_identifier.py`

**功能**：识别小说中的爽点情节，如打脸、逆袭等

**输入**：
- 预处理后的文本（字符串）

**处理流程**：
1. 识别爽点关键词和情节
2. 分析爽点类型和分布
3. 评估爽点密度和效果
4. 生成爽点分析报告

**输出**：
```python
{
    "success": bool,           # 处理是否成功
    "result": str,             # 爽点分析报告
    "error": str,              # 错误信息（如果有）
    "agent": "爽点识别器"      # Agent标识
}
```

**提示词模板**：
```
你是一个专业的爽点识别助手，专门识别小说中的爽点情节。
你的主要任务是：
1. 识别小说中的爽点关键词和情节
2. 分析爽点的类型和分布
3. 评估爽点密度和效果
4. 提供爽点分析报告

请直接使用你的语言理解能力来完成这些任务，并提供详细的爽点分析。
```

### 主控Agent

#### NovelInformationExtractor（小说信息提取器）

**位置**：`src/core/agents/info_extract/novel_extractor.py`

**功能**：协调各个信息提取Agent的工作，实现并行处理

**组件关系**：
- 管理TextPreprocessor实例
- 管理CharacterExtractor实例
- 管理PlotAnalyzer实例
- 管理SatisfactionPointIdentifier实例

**工作流程**：
1. 初始化所有子Agent
2. 构建LangGraph并行处理图
3. 执行并行提取任务
4. 合并所有提取结果

**主要方法**：
- `extract_novel_information_parallel(novel_text)`: 执行并行信息提取

**并行处理图结构**：
```
START → preprocess → extract_character ↘
                      → analyze_plot → merge_results → END
                      → identify_satisfaction ↗
```

**输出格式**：
```python
{
    "characters": Dict[str, Any],      # 人物信息
    "plot": Dict[str, Any],           # 剧情信息
    "satisfaction_points": Dict[str, Any],  # 爽点信息
    "original_text_length": int,      # 原始文本长度
    "cleaned_text_length": int,       # 清洗后文本长度
    "errors": List[str],              # 错误信息列表
    "completed_tasks": List[str],     # 已完成任务列表
    "parallel_execution": bool        # 并行执行标记
}
```

## Agent连接方式

### 状态传递机制

1. **初始化状态**：创建NovelExtractionState实例，包含原始文本
2. **预处理阶段**：TextPreprocessor处理文本，更新preprocessed_text字段
3. **并行提取阶段**：
   - CharacterExtractor读取preprocessed_text，更新character_info字段
   - PlotAnalyzer读取preprocessed_text，更新plot_info字段
   - SatisfactionPointIdentifier读取preprocessed_text，更新satisfaction_info字段
4. **结果合并**：NovelInformationExtractor收集所有结果，返回统一格式

### 依赖关系

```
TextPreprocessor
    ↓ (提供preprocessed_text)
┌─────────────────┬─────────────────┬─────────────────┐
│                 │                 │                 │
CharacterExtractor  PlotAnalyzer  SatisfactionPointIdentifier
│                 │                 │                 │
└─────────────────┴─────────────────┴─────────────────┘
    ↓ (提供各自的提取结果)
NovelInformationExtractor (合并结果)
```

### 并行执行控制

1. **条件检查**：每个提取节点检查preprocess_done标记
2. **并行启动**：预处理完成后，三个提取节点并行执行
3. **完成检测**：通过_should_merge方法检测所有任务是否完成
4. **结果合并**：所有任务完成后，调用merge_results节点

## 使用方式

### 单文件处理

```python
from src.services.extraction.main import extract_novel_information

# 处理单个文件
result = extract_novel_information("path/to/novel.txt", "output/dir")
```

### 批量处理

```python
from src.services.extraction.main import batch_extract_novel_info

# 批量处理多个文件
file_paths = ["novel1.txt", "novel2.txt", "novel3.txt"]
result = batch_extract_novel_info(file_paths, "output/dir", num_processes=4)
```

### 直接使用Agent

```python
from src.core.agents.info_extract import NovelInformationExtractor

# 创建提取器实例
extractor = NovelInformationExtractor()

# 执行并行提取
result = extractor.extract_novel_information_parallel(novel_text)
```

## 错误处理机制

### 单Agent错误处理

每个Agent都有独立的try-catch块，错误发生时：
1. 记录错误信息到state["errors"]
2. 在结果中标记success为False
3. 提供错误详情

### 系统级错误处理

1. **预处理失败**：回退到简单文本清洗
2. **提取失败**：标记对应任务为失败，继续其他任务
3. **整体失败**：在最终结果中汇总所有错误信息

## 扩展指南

### 添加新Agent

1. 继承BaseExtractor或BaseAgent
2. 实现extract和process方法
3. 在NovelInformationExtractor中添加新节点
4. 更新状态定义和并行处理图

### 修改工作流

1. 修改NovelExtractionState定义
2. 更新NovelInformationExtractor中的图结构
3. 调整条件检查逻辑
4. 更新输出格式

## 性能优化

### 并行处理优化

1. 使用multiprocessing实现文件级并行
2. 使用LangGraph实现任务级并行
3. 可配置的进程数量

### 资源管理

1. LLM连接复用
2. 状态对象高效传递
3. 错误恢复机制

### 内容创作阶段Agents

#### 1. CharacterCardGenerator（角色卡片生成器）

**位置**：`src/core/agents/content_creation/character_card_generator.py`

**功能**：基于LangGraph工作流为小说中所有角色创建多阶段视觉档案

**工作流设计**：
```
分组Agent → 并行角色卡片提取Agent → 角色信息合并Agent → 角色卡片更新Agent
```

**处理流程**：
1. **分组Agent**：根据已有角色重要性（主角/配角/龙套）进行分组处理
   - 主角组：["叶君临"]
   - 重要配角组：按2-3个角色分组
   - 普通配角组：按3-4个角色分组
   - 龙套角色组：批量处理

2. **并行角色卡片提取Agent**：每组处理2-3个角色
   - 输入：角色信息 + 原文文本
   - 处理：提取当前章节视觉信息
   - 输出：临时角色卡片（仅包含当前章节信息）

3. **角色信息合并Agent**：
   - 检查该角色是否已有卡片
   - 如果存在，判断是否需要新增阶段（基于重大变化关键词）
   - 如果不存在，创建新角色卡片

4. **角色卡片更新Agent**：
   - 将新信息合并到现有角色卡片中
   - 确保时间线的连贯性
   - 输出最终的角色卡片

**输入**：
- 角色信息（包含角色名、重要性、出现章节等）
- 原文文本内容

**重大变化判断标准**：
- 实力突破：突破、晋级、飞升等
- 外貌变化：变身、恢复、重伤等
- 装备获得：获得法宝、装备等

**阶段划分策略**：
- 主要角色：多阶段分析（早期/中期/晚期）
- 重要配角：单阶段描述，核心特征提取
- 龙套角色：最简描述，1-2个视觉标签

**输出**：
```python
{
    "success": bool,                    # 处理是否成功
    "character_cards": Dict[str, Any],  # 角色卡片信息
    "updated_characters": List[str],    # 更新的角色列表
    "new_characters": List[str],        # 新增角色列表
    "error": str,                       # 错误信息（如果有）
    "agent": "角色卡片生成器"           # Agent标识
}
```

**状态管理**：
```python
class CharacterCardState(TypedDict):
    character_info: Dict[str, Any]      # 角色基本信息
    original_text: str                  # 原文文本
    existing_cards: Dict[str, Any]      # 已存在的角色卡片
    temp_cards: Dict[str, Any]          # 临时角色卡片
    final_cards: Dict[str, Any]         # 最终角色卡片
    grouped_characters: Dict[str, List] # 分组后的角色
    completed_tasks: Annotated[List[str], operator.add]  # 已完成任务列表
    errors: Annotated[List[str], operator.add]           # 错误信息列表
}
```

**并行处理图结构**：
```
START → group_characters → parallel_extract → merge_cards → update_cards → END
```

#### 2. StoryboardPlanner（分镜规划器）

**位置**：`src/core/agents/content_creation/storyboard_planner.py`

**功能**：将小说内容规划为视频分镜

**输入**：
- 剧情信息
- 爽点信息
- 角色卡片信息

**处理流程**：
1. 将50章内容划分为若干90秒视频片段
2. 为每个片段设计15-30个镜头(每镜头3-6秒)
3. 确保分镜节奏符合叙事需求
4. 平衡各视频片段的内容分布

**输出**：
```python
{
    "success": bool,           # 处理是否成功
    "storyboard": Dict[str, Any],  # 分镜规划方案
    "error": str,              # 错误信息（如果有）
    "agent": "分镜规划器"      # Agent标识
}
```

#### 3. SceneDesigner（场景设计器）

**位置**：`src/core/agents/content_creation/scene_designer.py`

**功能**：设计每个分镜的场景

**输入**：
- 分镜规划方案
- 角色卡片信息
- 剧情信息

**处理流程**：
1. 识别每个分镜的关键场景
2. 生成场景描述和氛围设定
3. 确保场景连贯性
4. 设计场景转换方式

**输出**：
```python
{
    "success": bool,           # 处理是否成功
    "scenes": Dict[str, Any],  # 场景设计方案
    "error": str,              # 错误信息（如果有）
    "agent": "场景设计器"      # Agent标识
}
```

### 输出准备阶段Agents

#### 1. PromptGenerator（提示词生成器）

**位置**：`src/core/agents/output_preparation/prompt_generator.py`

**功能**：为图像生成创建详细提示词

**输入**：
- 场景设计方案
- 角色卡片信息
- 分镜规划方案

**处理流程**：
1. 为每个分镜生成详细的图像生成提示词
2. 包含人物、场景、动作、风格等元素
3. 优化提示词以适应AI图像生成
4. 确保提示词的一致性和多样性

**输出**：
```python
{
    "success": bool,           # 处理是否成功
    "prompts": Dict[str, Any], # 图像生成提示词列表
    "error": str,              # 错误信息（如果有）
    "agent": "提示词生成器"    # Agent标识
}
```

#### 2. NarrationScriptGenerator（旁白脚本生成器）

**位置**：`src/core/agents/output_preparation/narration_generator.py`

**功能**：为每个分镜编写旁白

**输入**：
- 分镜规划方案
- 场景设计方案
- 剧情信息

**处理流程**：
1. 为每个分镜编写3-6秒的旁白
2. 确保旁白与画面同步
3. 控制旁白长度和节奏
4. 优化旁白的表达效果

**输出**：
```python
{
    "success": bool,           # 处理是否成功
    "narration": Dict[str, Any],  # 旁白脚本
    "error": str,              # 错误信息（如果有）
    "agent": "旁白脚本生成器"  # Agent标识
}
```

---

*本文档随项目发展持续更新，如有疑问请参考源代码或联系开发团队。*