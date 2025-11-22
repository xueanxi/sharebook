"""
人物提取器，负责识别和提取小说中的人物信息
"""

from typing import Dict, Any
import time
from .base import BaseExtractor, NovelExtractionState
from src.utils.logging_manager import get_module_logger, LogModule


class CharacterExtractor(BaseExtractor):
    """人物提取器，负责识别和提取小说中的人物信息"""
    
    def __init__(self, model_name=None, temperature=0.7):
        super().__init__(model_name, temperature)
        self.logger = get_module_logger(LogModule.EXTRACTION_CHARACTER)
        
        # 使用LCEL创建处理链
        prompt_template = """
        作为人物提取专家，从小说中提取人物信息。

        任务：
        1. 识别人物名称
        2. 统计出现次数
        3. 标记主要角色(>5次出现)
        4. 简述人物关系

        要求：
        - 输出JSON格式
        - 只列出有名字的角色
        - 按出现次数降序排列
        - 总字数控制在500字内

        输出格式：
        {{
            "characters": [
                {{"name": "人物名", "count": 次数, "role": "主角/配角/次要", "relations": ["关系1", "关系2"]}}
            ]
        }}

        文本：{text}
        """
        
        # 创建提示模板和处理链
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import JsonOutputParser
        
        self.prompt = ChatPromptTemplate.from_template(prompt_template)
        self.chain = self.prompt | self.llm | JsonOutputParser()
    
    def process(self, state: NovelExtractionState) -> None:
        """处理文本
        
        Args:
            state: 并行提取状态
        """
        # 记录开始处理
        start_time = time.time()
        input_text_length = len(state.get("preprocessed_text", ""))
        self.logger.info(f"process 开始处理，输入文本长度: {input_text_length} 字符")
        
        try:
            # 使用LCEL链处理文本，添加回调处理器
            result = self.chain.invoke({"text": state["preprocessed_text"]}, config={"callbacks": [self._llm_callback_handler]})
            
            # 直接更新state中的character_info
            state["character_info"] = {
                "success": True,
                "result": result,
                "agent": "人物提取器"
            }
            state["completed_tasks"].append("人物提取")
            
            # 记录处理完成
            end_time = time.time()
            duration = end_time - start_time
            self.logger.info(f"process 处理完成，文本长度:{len(result)} 耗时: {duration:.2f}秒")
            
        except Exception as e:
            # 记录异常
            end_time = time.time()
            duration = end_time - start_time
            self.logger.error(f"process 处理失败，耗时: {duration:.2f}秒，错误: {str(e)}")
            
            # 确保errors键存在
            if "errors" not in state:
                state["errors"] = []
            state["character_info"] = {
                "success": False,
                "error": str(e),
                "agent": "人物提取器"
            }
            state["errors"].append(f"人物提取异常: {str(e)}")
            state["completed_tasks"].append("人物提取(失败)")
    
    def extract(self, text: str) -> Dict[str, Any]:
        """提取人物信息
        
        Args:
            text: 输入文本
            
        Returns:
            人物信息提取结果
        """
        try:
            # 使用LCEL链处理文本
            result = self.chain.invoke({"text": text})
            
            return {
                "success": True,
                "result": result,
                "agent": "人物提取器"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent": "人物提取器"
            }