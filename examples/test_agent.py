import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from langchain_openai import ChatOpenAI
from config.llm_config import LLMConfig

    
# 创建ChatOpenAI实例，使用本地LLM配置
chat = ChatOpenAI(
    **LLMConfig.get_openai_kwargs()
)

# 发送消息
response = chat.invoke("你好")
print(f"助手: {response.content}")
print()