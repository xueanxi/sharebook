"""
单个Agent功能测试
测试各个Agent的基本功能，包括文本预处理、人物提取、剧情分析和爽点识别
"""

import os
import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.agents.info_extract.text_preprocessor import TextPreprocessor
from src.core.agents.info_extract.character_extractor import CharacterExtractor
from src.core.agents.info_extract.plot_analyzer import PlotAnalyzer
from src.core.agents.info_extract.satisfaction_identifier import SatisfactionPointIdentifier
from src.core.agents.info_extract.base import NovelExtractionState

from tests.test_utils import (
    get_test_novel_content, 
    print_test_result, 
    check_agent_result
)


class TestSingleAgent:
    """单个Agent功能测试类"""
    
    @pytest.fixture
    def novel_content(self):
        """测试小说内容夹具"""
        return get_test_novel_content()
    
    @pytest.fixture
    def state(self, novel_content):
        """测试状态夹具"""
        return NovelExtractionState(
            text=novel_content,
            preprocessed_text="",
            character_info={},
            plot_info={},
            satisfaction_info={},
            completed_tasks=[],
            errors=[],
            preprocess_done=False,
            character_done=False,
            plot_done=False,
            satisfaction_done=False
        )
    
    def test_text_preprocessor(self, state):
        """测试文本预处理Agent"""
        # 创建文本预处理器
        preprocessor = TextPreprocessor()
        
        # 测试预处理方法
        result = preprocessor.preprocess_text(state["text"])
        
        # 验证结果
        assert result is not None, "预处理结果不能为None"
        assert "success" in result, "结果应包含success字段"
        assert "result" in result, "结果应包含result字段"
        assert "agent" in result, "结果应包含agent字段"
        assert result["agent"] == "文本预处理器", "agent字段应为'文本预处理器'"
        
        # 验证预处理后的文本不为空
        if result["success"]:
            assert len(result["result"]) > 0, "预处理后文本不能为空"
        else:
            # 即使失败，也应该有备用方案处理文本
            assert len(result["result"]) > 0, "即使失败，预处理后文本也不能为空"
            assert "error" in result, "失败结果应包含error字段"
        
        # 测试process方法
        preprocessor.process(state)
        assert len(state["preprocessed_text"]) > 0, "state中预处理后文本不能为空"
        assert "文本预处理" in state["completed_tasks"], "completed_tasks应包含文本预处理"
    
    def test_character_extractor(self, state):
        """测试人物提取Agent"""
        # 确保已预处理文本
        if not state["preprocessed_text"]:
            preprocessor = TextPreprocessor()
            preprocessor.process(state)
        
        # 创建人物提取器
        extractor = CharacterExtractor()
        
        # 测试提取方法
        result = extractor.extract(state["preprocessed_text"])
        
        # 验证结果
        assert result is not None, "人物提取结果不能为None"
        assert "success" in result, "结果应包含success字段"
        assert "result" in result, "结果应包含result字段"
        assert "agent" in result, "结果应包含agent字段"
        assert result["agent"] == "人物提取器", "agent字段应为'人物提取器'"
        
        if result["success"]:
            assert len(result["result"]) > 0, "人物提取结果不能为空"
        else:
            assert "error" in result, "失败结果应包含error字段"
        
        # 测试process方法
        extractor.process(state)
        assert "character_info" in state, "state应包含character_info"
        assert "success" in state["character_info"], "character_info应包含success字段"
        assert "人物提取" in state["completed_tasks"], "completed_tasks应包含人物提取"
    
    def test_plot_analyzer(self, state):
        """测试剧情分析Agent"""
        # 确保已预处理文本
        if not state["preprocessed_text"]:
            preprocessor = TextPreprocessor()
            preprocessor.process(state)
        
        # 创建剧情分析器
        analyzer = PlotAnalyzer()
        
        # 测试分析方法
        result = analyzer.extract(state["preprocessed_text"])
        
        # 验证结果
        assert result is not None, "剧情分析结果不能为None"
        assert "success" in result, "结果应包含success字段"
        assert "result" in result, "结果应包含result字段"
        assert "agent" in result, "结果应包含agent字段"
        assert result["agent"] == "剧情分析器", "agent字段应为'剧情分析器'"
        
        if result["success"]:
            assert len(result["result"]) > 0, "剧情分析结果不能为空"
        else:
            assert "error" in result, "失败结果应包含error字段"
        
        # 测试process方法
        analyzer.process(state)
        assert "plot_info" in state, "state应包含plot_info"
        assert "success" in state["plot_info"], "plot_info应包含success字段"
        assert "剧情分析" in state["completed_tasks"], "completed_tasks应包含剧情分析"
    
    def test_satisfaction_identifier(self, state):
        """测试爽点识别Agent"""
        # 确保已预处理文本
        if not state["preprocessed_text"]:
            preprocessor = TextPreprocessor()
            preprocessor.process(state)
        
        # 创建爽点识别器
        identifier = SatisfactionPointIdentifier()
        
        # 测试识别方法
        result = identifier.extract(state["preprocessed_text"])
        
        # 验证结果
        assert result is not None, "爽点识别结果不能为None"
        assert "success" in result, "结果应包含success字段"
        assert "result" in result, "结果应包含result字段"
        assert "agent" in result, "结果应包含agent字段"
        assert result["agent"] == "爽点识别器", "agent字段应为'爽点识别器'"
        
        if result["success"]:
            assert len(result["result"]) > 0, "爽点识别结果不能为空"
        else:
            assert "error" in result, "失败结果应包含error字段"
        
        # 测试process方法
        identifier.process(state)
        assert "satisfaction_info" in state, "state应包含satisfaction_info"
        assert "success" in state["satisfaction_info"], "satisfaction_info应包含success字段"
        assert "爽点识别" in state["completed_tasks"], "completed_tasks应包含爽点识别"


    @patch('src.core.agents.info_extract.base.ChatOpenAI')
    def test_agents_with_llm_failure(self, mock_llm, state):
        """测试LLM失败时的备用方案"""
        # 模拟LLM调用失败
        mock_llm_instance = Mock()
        mock_llm_instance.invoke.side_effect = Exception("LLM调用失败")
        mock_llm.return_value = mock_llm_instance
        
        # 测试文本预处理器的备用方案
        preprocessor = TextPreprocessor()
        result = preprocessor.preprocess_text(state["text"])
        assert not result["success"], "LLM失败时success应为False"
        assert "error" in result, "LLM失败时应包含error字段"
        assert len(result["result"]) > 0, "LLM失败时备用方案应返回处理后的文本"
        
        # 测试其他Agent的备用方案
        extractor = CharacterExtractor()
        result = extractor.extract(state["text"])
        assert not result["success"], "LLM失败时success应为False"
        assert "error" in result, "LLM失败时应包含error字段"
        
        analyzer = PlotAnalyzer()
        result = analyzer.extract(state["text"])
        assert not result["success"], "LLM失败时success应为False"
        assert "error" in result, "LLM失败时应包含error字段"
        
        identifier = SatisfactionPointIdentifier()
        result = identifier.extract(state["text"])
        assert not result["success"], "LLM失败时success应为False"
        assert "error" in result, "LLM失败时应包含error字段"