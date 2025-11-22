"""
文本预处理器，负责清洗小说文本
"""

from typing import Dict, Any
import time
from .base import BaseAgent, NovelExtractionState
from src.utils.logging_manager import get_module_logger, LogModule
from pathlib import Path


class TextPreprocessor(BaseAgent):
    """文本预处理器，负责清洗小说文本"""
    
    def __init__(self, model_name=None, temperature=0.7):
        super().__init__(model_name, temperature)
        self.logger = get_module_logger(LogModule.CORE)
        self.cleaned_novel_dir = Path('data/cleaned_novel')
        self.cleaned_novel_dir.mkdir(parents=True)
        
        # 使用LCEL创建处理链
        prompt_template = """
        作为文本预处理专家，清洗小说文本。

        任务：
        1. 去除无关字符和格式
        2. 统一文本格式
        3. 提供基本统计信息

        要求：
        - 保持原文内容和顺序
        - 只做必要清洗，不改变语义
        - 输出清洗后的文本，不要额外解释
        - 最多返回原文本长度的95%

        文本：{text}
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
        input_text_length = len(state.get("text", ""))
        self.logger.info(f"process 开始处理，输入文本长度: {input_text_length} 字符")
        self.novel_file_name = state["novel_file_name"]
        self.logger.info(f"process 开始处理，小说文件名: {self.novel_file_name} 文本长度: {input_text_length} 字符")
        
        try:
            # 使用LCEL链处理文本，添加回调处理器
            from langchain_core.callbacks import CallbackManager
            callback_manager = CallbackManager([self._llm_callback_handler])
            result = self.chain.invoke({"text": state["text"]}, config={"callbacks": [self._llm_callback_handler]})
            state["preprocessed_text"] = result
            state["completed_tasks"].append("文本预处理")
            state["preprocess_done"] = True  # 设置预处理完成标志

            
            cleaned_novel_file = self.cleaned_novel_dir / self.novel_file_name
            with open(cleaned_novel_file, "w", encoding="utf-8") as f:
                f.write(result)
                self.logger.info(f"preprocess_text 清理小说完成，已保存到: {cleaned_novel_file}")
            
            # 记录处理完成
            end_time = time.time()
            duration = end_time - start_time
            self.logger.info(f"process 处理完成，文本长度:{len(result)}，耗时: {duration:.2f}秒")
            
        except Exception as e:
            # 记录异常
            end_time = time.time()
            duration = end_time - start_time
            self.logger.error(f"process 处理失败，耗时: {duration:.2f}秒，错误: {str(e)}")
            
            # 如果LLM处理失败，使用简单的文本清洗作为备用方案
            cleaned_text = self._simple_text_cleaning(state["text"])
            state["preprocessed_text"] = cleaned_text
            state["preprocess_done"] = True  # 即使失败也设置标志，表示已尝试处理
            # 确保errors键存在
            if "errors" not in state:
                state["errors"] = []
            state["errors"].append(f"文本预处理异常: {str(e)}")
            state["completed_tasks"].append("文本预处理(失败)")
    