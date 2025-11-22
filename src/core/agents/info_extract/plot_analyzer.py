"""
剧情分析器，负责分析小说的情节结构
"""

from typing import Dict, Any
import time
from .base import BaseExtractor, NovelExtractionState
from src.utils.logging_manager import get_module_logger, LogModule


class PlotAnalyzer(BaseExtractor):
    """剧情分析器，负责分析小说的情节结构"""
    
    def __init__(self, model_name=None, temperature=0.7):
        super().__init__(model_name, temperature)
        self.logger = get_module_logger(LogModule.EXTRACTION)
        
        # 使用LCEL创建处理链
        prompt_template = """
        作为剧情分析专家，分析小说情节结构。

        任务：
        1. 识别主要情节线
        2. 标记关键转折点
        3. 评估故事节奏
        4. 提取高潮部分

        要求：
        - 输出JSON格式
        - 只关注主要情节，忽略次要细节
        - 按时间顺序排列
        - 总字数控制在500字内

        输出格式：
        {{
            "plot_summary": "一句话概括",
            "key_events": [
                {{"event": "事件描述", "type": "开端/发展/高潮/结局", "importance": 1-10}}
            ],
            "pacing": "快/中/慢",
            "main_conflicts": ["冲突1", "冲突2"]
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
            self.logger.info(f"process 处理完成，文本长度:{len(result)}，耗时: {duration:.2f}秒")
            
        except Exception as e:
            # 记录异常
            end_time = time.time()
            duration = end_time - start_time
            self.logger.error(f"process 处理失败，耗时: {duration:.2f}秒，错误: {str(e)}")
            
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