import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from langchain_openai import ChatOpenAI
from typing import List, Dict, Any, TypedDict
from src.config.llm_config import LLMConfig
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

class CharacterInfo(TypedDict):
    """并行提取状态"""
    name: str
    age:int
    occupation: str
    skills: List[str]
    description: str

# 发送消息，请求返回结构化数据
prompt_template = """
请创建一个名为'张三'的虚构角色信息，并严格按照以下JSON格式返回：

{{
  "name": "角色名称（字符串）",
  "age": 角色年龄（整数）,
  "occupation": "角色职业（字符串）",
  "skills": ["技能1", "技能2", "技能3"],
  "description": "角色描述（字符串，50-100字）"
}}

请确保：
1. name字段为字符串类型
2. age字段为整数类型
3. occupation字段为字符串类型
4. skills字段为字符串数组
5. description字段为字符串类型，长度在50-100字之间
"""

# 创建ChatOpenAI实例，使用本地LLM配置
llm = ChatOpenAI(
    **LLMConfig.get_openai_kwargs()
)

# 非思维链模型
# prompt = ChatPromptTemplate.from_template(prompt_template)
# chain = prompt | llm | JsonOutputParser()
# result = chain.invoke({})
# print(result)


# 思维链的模型
structured_model = llm.with_structured_output(CharacterInfo)
result = structured_model.invoke(prompt_template)
print(result)
