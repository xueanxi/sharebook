"""
爽点识别器，负责识别小说中的爽点情节
"""

from typing import Dict, Any
import time
from .base import BaseExtractor, NovelExtractionState
from src.utils.logging_manager import get_module_logger, LogModule


class SatisfactionPointIdentifier(BaseExtractor):
    """爽点识别器，负责识别小说中的爽点情节"""
    
    def __init__(self, model_name=None, temperature=0.7):
        super().__init__(model_name, temperature)
        self.logger = get_module_logger(LogModule.EXTRACTION)
        
        # 使用LCEL创建处理链
        prompt_template = """
        作为爽点识别专家，识别小说中的爽点情节。

        任务：
        1. 识别爽点关键词和情节
        2. 分类爽点类型
        3. 评估爽点强度
        4. 统计爽点分布

        要求：
        - 输出JSON格式
        - 只标记明显的爽点(强度>5)
        - 按出现顺序排列
        - 总字数控制在500字内

        输出格式：
        {{
            "satisfaction_points": [
                {{"description": "爽点描述", "type": "打脸/逆袭/突破/升级/复仇/装逼", "intensity": 1-10, "location": "大致位置"}}
            ],
            "density": "高/中/低",
            "main_types": ["类型1", "类型2"]
        }}

        文本：{text}
        """
        
        # 创建处理链，使用JSON输出解析器
        from langchain_core.output_parsers import JsonOutputParser
        self.chain = self._create_chain(prompt_template) | JsonOutputParser()
    
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
            # 使用LCEL链处理文本
            result = self.chain.invoke({"text": state["preprocessed_text"]})
            
            # 直接更新state中的satisfaction_info
            state["satisfaction_info"] = {
                "success": True,
                "result": result,
                "agent": "爽点识别器"
            }
            state["completed_tasks"].append("爽点识别")
            
            # 记录处理完成
            end_time = time.time()
            duration = end_time - start_time
            self.logger.info(f"process 处理完成，文本长度:{len(result)}，耗时: {duration:.2f}秒")
            
        except Exception as e:
            # 记录异常
            end_time = time.time()
            duration = end_time - start_time
            self.logger.error(f"process 处理失败，耗时: {duration:.2f}秒，错误: {str(e)}")
            
            # 确保errors键存在
            if "errors" not in state:
                state["errors"] = []
            state["satisfaction_info"] = {
                "success": False,
                "error": str(e),
                "agent": "爽点识别器"
            }
            state["errors"].append(f"爽点识别异常: {str(e)}")
            state["completed_tasks"].append("爽点识别(失败)")
    
    def extract(self, text: str) -> Dict[str, Any]:
        """识别爽点
        
        Args:
            text: 输入文本
            
        Returns:
            爽点识别结果
        """
        try:
            # 使用LCEL链处理文本
            result = self.chain.invoke({"text": text})
            
            return {
                "success": True,
                "result": result,
                "agent": "爽点识别器"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent": "爽点识别器"
            }