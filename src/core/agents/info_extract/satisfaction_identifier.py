"""
爽点识别器，负责识别小说中的爽点情节
"""

from typing import Dict, Any
import time
from .base import BaseExtractor, NovelExtractionState
from src.utils.logging_manager import get_agent_logger


class SatisfactionPointIdentifier(BaseExtractor):
    """爽点识别器，负责识别小说中的爽点情节"""
    
    def __init__(self, model_name=None, temperature=0.7):
        super().__init__(model_name, temperature)
        self.logger = get_agent_logger(self.__class__.__module__ + "." + self.__class__.__name__)
        
        # 使用LCEL创建处理链
        prompt_template = """
        你是一个专业的爽点识别助手，专门识别小说中的爽点情节。
        你的主要任务是：
        1. 识别小说中的爽点关键词和情节
        2. 分析爽点的类型和分布
        3. 评估爽点密度和效果
        4. 提供爽点分析报告
        
        请直接使用你的语言理解能力来完成这些任务，并提供详细的爽点分析。分析时请考虑：
        - 爽点的类型：打脸、逆袭、突破、升级、复仇、装逼等
        - 爽点在故事中的位置和作用
        - 爽点的强度和读者可能产生的情感反应
        - 爽点之间的间隔和节奏
        - 爽点与人物成长的关系
        
        小说文本：
        {text}
        """
        
        # 创建处理链
        self.chain = self._create_chain(prompt_template)
    
    def process(self, state: NovelExtractionState) -> None:
        """处理文本
        
        Args:
            state: 并行提取状态
        """
        # 记录开始处理
        start_time = time.time()
        input_text_length = len(state.get("preprocessed_text", ""))
        self.logger.info(f"@{self.__class__.__name__}.process - 开始处理，输入文本长度: {input_text_length} 字符")
        
        # 检查依赖关系
        if not state.get("preprocess_done", False):
            self.logger.warning(f"@{self.__class__.__name__}.process - 预处理未完成，跳过爽点识别")
            # 确保errors键存在
            if "errors" not in state:
                state["errors"] = []
            state["errors"].append("爽点识别: 预处理未完成")
            state["completed_tasks"].append("爽点识别(失败)")
            state["satisfaction_info"] = {
                "success": False,
                "error": "预处理未完成",
                "agent": "爽点识别器"
            }
            return
        
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
            self.logger.info(f"@{self.__class__.__name__}.process - 处理完成，耗时: {duration:.2f}秒")
            
        except Exception as e:
            # 记录异常
            end_time = time.time()
            duration = end_time - start_time
            self.logger.error(f"@{self.__class__.__name__}.process - 处理失败，耗时: {duration:.2f}秒，错误: {str(e)}")
            
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