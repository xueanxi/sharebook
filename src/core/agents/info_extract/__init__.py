"""
信息提取模块
包含所有用于小说信息提取的Agent类
"""

# 导入基础类
from .base import BaseAgent, BaseExtractor, ParallelExtractionState

# 导入各个Agent类
from .text_preprocessor import TextPreprocessor
from .character_extractor import CharacterExtractor
from .plot_analyzer import PlotAnalyzer
from .satisfaction_identifier import SatisfactionPointIdentifier
from .novel_extractor import NovelInformationExtractor

# 定义__all__列表，明确导出的类
__all__ = [
    # 基础类
    "BaseAgent",
    "BaseExtractor", 
    "ParallelExtractionState",
    
    # Agent类
    "TextPreprocessor",
    "CharacterExtractor",
    "PlotAnalyzer",
    "SatisfactionPointIdentifier",
    "NovelInformationExtractor"
]