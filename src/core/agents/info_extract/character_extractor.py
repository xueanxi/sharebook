"""
人物提取器，负责识别和提取小说中的人物信息
"""

from typing import Dict, Any
from .base import BaseExtractor, NovelExtractionState, log_process


class CharacterExtractor(BaseExtractor):
    """人物提取器，负责识别和提取小说中的人物信息"""
    
    def __init__(self, model_name=None, temperature=0.7):
        super().__init__(model_name, temperature)
        
        # 使用LCEL创建处理链
        prompt_template = """
        你是一个专业的人物提取助手，专门分析小说文本中的人物。
        你的主要任务是：
        1. 从小说文本中识别人物名称
        2. 统计每个人物的出现次数
        3. 分析人物关系和重要性
        4. 提供人物列表和相关信息
        
        请直接使用你的语言理解能力来完成这些任务，并提供详细的人物分析报告。分析时请考虑：
        - 人物名称的上下文
        - 人物在故事中的角色
        - 人物之间的关系
        - 人物出现的重要性排序
        
        小说文本：
        {text}
        """
        
        # 创建处理链
        self.chain = self._create_chain(prompt_template)
    
    @log_process
    def process(self, state: NovelExtractionState) -> None:
        """处理文本
        
        Args:
            state: 并行提取状态
        """
        try:
            # 使用LCEL链处理文本
            result = self.chain.invoke({"text": state["preprocessed_text"]})
            
            # 直接更新state中的character_info
            state["character_info"] = {
                "success": True,
                "result": result,
                "agent": "人物提取器"
            }
            state["completed_tasks"].append("人物提取")
        except Exception as e:
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