"""
文本预处理器，负责清洗小说文本
"""

from typing import Dict, Any
from .base import BaseAgent, ParallelExtractionState


class TextPreprocessor(BaseAgent):
    """文本预处理器，负责清洗小说文本"""
    
    def __init__(self, model_name=None, temperature=0.7):
        super().__init__(model_name, temperature)
        
        # 使用LCEL创建处理链
        prompt_template = """
        你是一个专业的文本预处理助手，专门处理小说文本。
        你的主要任务是：
        1. 清洗文本内容，去除无关字符和格式
        2. 确保文本格式统一，便于后续处理
        3. 提供文本统计信息
        
        请直接使用你的语言能力进行清洗，提供清晰的总结和清洗后的文本。
        
        原始文本：
        {text}
        """
        
        # 创建处理链
        self.chain = self._create_chain(prompt_template)
    
    def process(self, state: ParallelExtractionState) -> None:
        """处理文本
        
        Args:
            state: 并行提取状态
        """
        try:
            # 使用LCEL链处理文本
            result = self.chain.invoke({"text": state["text"]})
            state["preprocessed_text"] = result
            state["completed_tasks"].append("文本预处理")
        except Exception as e:
            # 如果LLM处理失败，使用简单的文本清洗作为备用方案
            cleaned_text = self._simple_text_cleaning(state["text"])
            state["preprocessed_text"] = cleaned_text
            state["errors"].append(f"文本预处理异常: {str(e)}")
            state["completed_tasks"].append("文本预处理(失败)")
    
    def preprocess_text(self, text: str) -> Dict[str, Any]:
        """预处理文本
        
        Args:
            text: 原始文本
            
        Returns:
            预处理结果
        """
        try:
            # 使用LCEL链处理文本
            result = self.chain.invoke({"text": text})
            return {
                "success": True,
                "result": result,
                "agent": "文本预处理器"
            }
        except Exception as e:
            # 如果LLM处理失败，使用简单的文本清洗作为备用方案
            cleaned_text = self._simple_text_cleaning(text)
            return {
                "success": False,
                "result": cleaned_text,
                "error": str(e),
                "agent": "文本预处理器"
            }