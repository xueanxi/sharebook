"""
剧情分析器，负责分析小说的情节结构
"""

from typing import Dict, Any
import time
from .base import BaseExtractor, NovelExtractionState
from src.utils.logging_manager import get_agent_logger


class PlotAnalyzer(BaseExtractor):
    """剧情分析器，负责分析小说的情节结构"""
    
    def __init__(self, model_name=None, temperature=0.7):
        super().__init__(model_name, temperature)
        self.logger = get_agent_logger(self.__class__.__module__ + "." + self.__class__.__name__)
        
        # 使用LCEL创建处理链
        prompt_template = """
        你是一个专业的剧情分析助手，专门分析小说的情节结构。
        你的主要任务是：
        1. 分析小说的情节结构
        2. 识别关键情节元素（冲突、转折、高潮等）
        3. 评估情节复杂度和节奏
        4. 提供情节分析报告
        
        请直接使用你的语言理解能力来完成这些任务，并提供详细的剧情分析。分析时请考虑：
        - 故事的开端、发展、高潮和结局
        - 主要冲突和次要冲突
        - 情节转折点和关键事件
        - 故事节奏和张力变化
        - 情节与人物发展的关系
        
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
            self.logger.warning(f"@{self.__class__.__name__}.process - 预处理未完成，跳过剧情分析")
            # 确保errors键存在
            if "errors" not in state:
                state["errors"] = []
            state["errors"].append("剧情分析: 预处理未完成")
            state["completed_tasks"].append("剧情分析(失败)")
            state["plot_info"] = {
                "success": False,
                "error": "预处理未完成",
                "agent": "剧情分析器"
            }
            return
        
        try:
            # 使用LCEL链处理文本
            result = self.chain.invoke({"text": state["preprocessed_text"]})
            
            # 直接更新state中的plot_info
            state["plot_info"] = {
                "success": True,
                "result": result,
                "agent": "剧情分析器"
            }
            state["completed_tasks"].append("剧情分析")
            
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
            state["plot_info"] = {
                "success": False,
                "error": str(e),
                "agent": "剧情分析器"
            }
            state["errors"].append(f"剧情分析异常: {str(e)}")
            state["completed_tasks"].append("剧情分析(失败)")
    
    def extract(self, text: str) -> Dict[str, Any]:
        """分析剧情
        
        Args:
            text: 输入文本
            
        Returns:
            剧情分析结果
        """
        try:
            # 使用LCEL链处理文本
            result = self.chain.invoke({"text": text})
            
            return {
                "success": True,
                "result": result,
                "agent": "剧情分析器"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent": "剧情分析器"
            }