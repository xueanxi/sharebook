# LangChain v1.0.0 核心使用指南

## 1. 安装与环境配置

### 1.1 系统要求
- Python 3.10 或更高版本

### 1.2 安装命令
```bash
# 核心包
pip install langchain

# 社区集成包（如文档加载器、向量数据库等）
pip install langchain-community

# 特定提供商包
pip install langchain-openai  # OpenAI
pip install langchain-anthropic  # Anthropic

# 兼容旧版本
pip install langchain-classic
```

### 1.3 API密钥配置
```bash
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

## 2. v1.0.0 核心特性

### 2.1 统一的智能体构建：`create_agent`
```python
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

# 初始化模型
model = ChatOpenAI(model="gpt-4o", temperature=0)

# 定义工具
tools = [...]  # 工具列表

# 创建智能体
agent = create_agent(
    model=model,
    tools=tools,
    system_prompt="你是一个强大的助手，能够调用工具来回答问题。"
)

# 调用智能体
response = agent.invoke({"input": "你的问题"})
```

### 2.2 标准内容块（Standard Content Blocks）
```python
# 访问模型返回的标准化内容
response = model.invoke("你的问题")

for block in response.content_blocks:
    if block["type"] == "text":
        print(f"文本内容: {block['text']}")
    elif block["type"] == "tool_call":
        print(f"调用工具: {block['tool_name']}")
        print(f"工具参数: {block['args']}")
```

### 2.3 精简的包结构
- `langchain`: 核心功能
- `langchain-community`: 第三方集成
- `langchain-openai`: OpenAI集成
- `langchain-classic`: 旧版API兼容

### 2.4 中间件架构（Middleware）
```python
from langchain.agents.middleware import PIIMiddleware, HumanInTheLoopMiddleware

agent = create_agent(
    model=model,
    tools=tools,
    system_prompt="...",
    middleware=[
        PIIMiddleware(),  # 自动脱敏
        HumanInTheLoopMiddleware(approve_tool="transfer_funds")  # 敏感工具需审批
    ]
)
```

## 3. 核心概念

### 3.1 智能体（Agent）
- 核心循环：推理-行动-观察-重复
- v1.0.0使用LangGraph实现，更加透明、可控和可靠

### 3.2 工具（Tools）
```python
from langchain_core.tools import tool

@tool
def search_weather(city: str) -> str:
    """查询指定城市的当前天气。"""
    # 实际的天气查询逻辑...
    return f"{city}现在是晴天，25摄氏度。"
```

### 3.3 链（Chains）
- v0.x的核心，v1.0.0中地位被智能体取代
- 简单线性任务仍可使用
- 旧版链API已移至`langchain-classic`

### 3.4 提示模板（Prompt Templates）
```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_template("给我一个关于{topic}的笑话。")
```

### 3.5 模型（Models）
```python
# v1.0.0推荐使用统一初始化函数
from langchain.chat_models import init_chat_model

model = init_chat_model(model="gpt-4o", temperature=0)
```

## 4. API变更对照表

| 功能 | v0.x | v1.0.0 |
|------|------|--------|
| 模型导入 | `from langchain.chat_models import ChatOpenAI` | `from langchain_openai import ChatOpenAI` |
| 文档加载器 | `from langchain.document_loaders import PyPDFLoader` | `from langchain_community.document_loaders import PyPDFLoader` |
| 向量数据库 | `from langchain.vectorstores import FAISS` | `from langchain_community.vectorstores import FAISS` |
| 旧版链 | `from langchain.chains import LLMChain` | `from langchain_classic.chains import LLMChain` |
| 智能体创建 | `AgentExecutor` | `create_agent` |

## 5. LCEL（LangChain Expression Language）
```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_template("给我一个关于{topic}的笑话。")
chain = prompt | model | StrOutputParser()  # 使用管道符 | 组装链

result = chain.invoke({"topic": "程序员"})
```

## 6. LangGraph：LangChain v1.0.0的底层编排引擎

### 6.1 什么是LangGraph？

LangGraph是LangChain v1.0.0的底层编排引擎，它是一个低级编排框架和运行时，专为构建、管理和部署长时间运行的状态化智能体而设计。

与传统的线性链式结构不同，LangGraph通过有向图(Directed Graph)的方式组织智能体的工作流程，能够处理复杂的循环、分支和人机交互场景。

### 6.2 LangGraph的核心优势

1. **持久化执行(Durable Execution)**：构建能够抵御故障并持续长时间运行的智能体，可从中断点精确自动恢复执行。

2. **人在回路(Human-in-the-Loop)**：无缝整合人工监督，支持在任何点检查和修改智能体状态。

3. **全面记忆(Comprehensive Memory)**：创建具有短期工作记忆和跨会话长期记忆的状态化智能体。

4. **流式传输(Streaming)**：内置流式传输支持，适配实时数据交互场景。

5. **生产就绪部署**：为处理状态化、长时间运行工作流的独特挑战而设计的可扩展基础设施。

### 6.3 LangGraph与LangChain的关系

LangGraph和LangChain是同一个生态里的两个工具，但定位和用途不同：

- **LangChain**：一个通用的LLM应用开发框架，核心目标是将大语言模型(LLM)和外部工具、数据连接起来。

- **LangGraph**：一个基于LangChain的工作流编排框架，专注于处理复杂的工作流和状态管理。

LangChain v1.0.0中的`create_agent`函数在底层使用了LangGraph作为执行引擎，这使得所有通过`create_agent`创建的代理都天然具备了持久化状态、流式输出和时间旅行等能力。

### 6.4 LangGraph生态系统

虽然LangGraph可以独立使用，但它也与任何LangChain产品无缝集成，为开发者提供构建智能体的完整工具套件：

- **LangSmith**：用于智能体评估和可观测性，帮助调试性能不佳的LLM应用运行，评估智能体轨迹，在生产中获得可见性，并随时间推移改进性能。

- **LangSmith部署平台**：轻松部署和扩展智能体，专为长时间运行、状态化的工作流而构建。

- **LangChain**：提供集成和可组合组件，简化LLM应用开发，包含基于LangGraph构建的智能体抽象。

### 6.5 LangGraph基础示例

```python
from langgraph.graph import StateGraph, MessagesState, START, END

def mock_llm(state: MessagesState):
    return {"messages": [{"role": "ai", "content": "hello world"}]}

# 创建状态图
graph = StateGraph(MessagesState)
graph.add_node(mock_llm)
graph.add_edge(START, "mock_llm")
graph.add_edge("mock_llm", END)
graph = graph.compile()

# 调用图
result = graph.invoke({"messages": [{"role": "user", "content": "hi!"}]})
```

### 6.6 LangGraph工作流模式

LangGraph支持多种工作流模式，每种模式适用于不同的应用场景：

#### 6.6.1 提示链(Prompt Chaining)
提示链是每个LLM调用处理前一个调用的输出，常用于可分解为更小、可验证步骤的明确定义任务，如：
- 将文档翻译成不同语言
- 验证生成内容的一致性

#### 6.6.2 并行化(Parallelization)
并行化使LLM同时处理任务，可以通过以下方式实现：
- 同时运行多个独立子任务，提高速度
- 多次运行相同任务检查不同输出，提高置信度

应用示例：
- 一个子任务处理文档关键词，另一个子任务检查格式错误
- 基于不同标准（引用数量、来源数量、来源质量）多次运行任务对文档进行准确性评分

#### 6.6.3 路由(Routing)
路由工作流处理输入并将其定向到特定任务，允许为复杂任务定义专门流程。例如，回答产品相关问题的工作流可能先处理问题类型，然后将请求路由到定价、退款、退货等特定流程。

#### 6.6.4 编排器-工作者(Orchestrator-Worker)
在编排器-工作者配置中，编排器：
- 将任务分解为子任务
- 将子任务委托给工作者
- 将工作者输出合成为最终结果

这种模式提供更大灵活性，常用于子任务无法预定义的情况，如编写代码或需要跨多个文件更新内容的工作流。

##### LangGraph中的工作者创建
LangGraph对编排器-工作者工作流提供内置支持。Send API允许动态创建工作者节点并向它们发送特定输入。每个工作者有自己的状态，所有工作者输出写入共享状态键，可供编排器图访问。

```python
from langgraph.types import Send
from typing import TypedDict, Annotated, list
import operator

# 图状态
class State(TypedDict):
    topic: str  # 报告主题
    sections: list[Section]  # 报告章节列表
    completed_sections: Annotated[list, operator.add]  # 所有工作者并行写入此键
    final_report: str  # 最终报告

# 工作者状态
class WorkerState(TypedDict):
    section: Section
    completed_sections: Annotated[list, operator.add]

# 节点
def orchestrator(state: State):
    """生成报告计划的编排器"""
    # 生成查询
    report_sections = planner.invoke([...])
    
    # 返回Send对象列表，每个对象包含工作者节点和输入
    return [Send("worker", {"section": s}) for s in report_sections]
```

## 7. 常见问题

**Q: 为什么我的import找不到了？**
A: 检查是否已移至`langchain-community`、`langchain-openai`等新包中。

**Q: LLMChain去哪了？**
A: 已移至`langchain-classic`包中，建议使用LCEL替代。

**Q: AgentExecutor不存在了，如何运行代理？**
A: 使用`create_agent`创建代理，它返回可运行对象，直接调用`.invoke()`或`.stream()`。

**Q: 如何处理不同LLM返回的不同格式？**
A: 使用标准内容块`message.content_blocks`。

**Q: 如何在代理执行过程中添加日志或自定义逻辑？**
A: 使用中间件（Middleware），实现钩子函数并应用到代理中。

**Q: LangGraph和LangChain是什么关系？**
A: LangGraph是LangChain v1.0.0的底层编排引擎，专注于状态化智能体的构建和管理，而LangChain提供更高级的抽象和组件集成。
