"""
完整信息提取功能测试
测试NovelInformationExtractor的完整信息提取功能，包括并行处理
"""

import os
import sys
import pytest
import json
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.agents.info_extract.novel_extractor import NovelInformationExtractor
from src.core.agents.info_extract.base import ParallelExtractionState

from tests.test_utils import (
    get_test_novel_content, 
    save_test_results,
    print_test_result, 
    check_agent_result
)


class TestCompleteExtraction:
    """完整信息提取功能测试类"""
    
    @pytest.fixture
    def novel_content(self):
        """测试小说内容夹具"""
        return get_test_novel_content()
    
    @pytest.fixture
    def extractor(self):
        """提取器夹具"""
        return NovelInformationExtractor()
    
    def test_parallel_extraction_success(self, extractor, novel_content):
        """测试并行信息提取功能 - 成功情况"""
        print("\n=== 测试并行信息提取功能 ===")
        
        # 执行并行提取
        result = extractor.extract_novel_information_parallel(novel_content)
        
        # 验证结果结构
        assert isinstance(result, dict), "结果应该是字典类型"
        assert 'characters' in result, "结果应包含characters字段"
        assert 'plot' in result, "结果应包含plot字段"
        assert 'satisfaction_points' in result, "结果应包含satisfaction_points字段"
        assert 'original_text_length' in result, "结果应包含original_text_length字段"
        assert 'cleaned_text_length' in result, "结果应包含cleaned_text_length字段"
        assert 'parallel_execution' in result, "结果应包含parallel_execution字段"
        assert result['parallel_execution'] is True, "parallel_execution应为True"
        assert result['original_text_length'] > 0, "原始文本长度应大于0"
        
        # 检查各个部分的结果结构
        for key in ['characters', 'plot', 'satisfaction_points']:
            assert isinstance(result[key], dict), f"{key}应该是字典类型"
            assert 'success' in result[key], f"{key}应包含success字段"
            if result[key]['success']:
                assert 'result' in result[key], f"{key}成功时应包含result字段"
                assert isinstance(result[key]['result'], str), f"{key}的result应该是字符串"
                assert len(result[key]['result']) > 0, f"{key}的result不应为空"
            else:
                # 如果处理失败，应该有错误信息
                assert 'error' in result[key], f"{key}失败时应包含error字段"
                print(f"警告: {key}处理失败: {result[key]['error']}")
        
        print("并行提取测试通过!")
        print(f"原始文本长度: {result['original_text_length']}")
        print(f"清洗后文本长度: {result['cleaned_text_length']}")
        
        # 保存测试结果
        output_path = save_test_results(result, "parallel_extraction_result.json")
        print(f"测试结果已保存到: {output_path}")
    

    @patch('src.core.agents.info_extract.novel_extractor.TextPreprocessor')
    @patch('src.core.agents.info_extract.novel_extractor.CharacterExtractor')
    @patch('src.core.agents.info_extract.novel_extractor.PlotAnalyzer')
    @patch('src.core.agents.info_extract.novel_extractor.SatisfactionPointIdentifier')
    def test_parallel_extraction_with_llm_failure(self, mock_satisfaction, mock_plot, 
                                                  mock_character, mock_preprocessor, novel_content):
        """测试并行信息提取功能 - LLM失败情况"""
        print("\n=== 测试并行信息提取功能 - LLM失败情况 ===")
        
        # 模拟LLM调用失败
        mock_preprocessor.return_value.chain.invoke.side_effect = Exception("LLM调用失败")
        mock_character.return_value.chain.invoke.side_effect = Exception("LLM调用失败")
        mock_plot.return_value.chain.invoke.side_effect = Exception("LLM调用失败")
        mock_satisfaction.return_value.chain.invoke.side_effect = Exception("LLM调用失败")
        
        # 创建提取器
        extractor = NovelInformationExtractor()
        
        # 执行并行提取
        result = extractor.extract_novel_information_parallel(novel_content)
        
        # 验证结果
        assert isinstance(result, dict), "结果应该是字典类型"
        assert 'characters' in result, "结果应包含characters字段"
        assert 'plot' in result, "结果应包含plot字段"
        assert 'satisfaction_points' in result, "结果应包含satisfaction_points字段"
        assert 'errors' in result, "结果应包含errors字段"
        assert len(result['errors']) > 0, "应该有错误信息"
        
        # 验证各个部分都标记为失败
        for key in ['characters', 'plot', 'satisfaction_points']:
            assert isinstance(result[key], dict), f"{key}应该是字典类型"
            assert result[key]['success'] is False, f"{key}应该标记为失败"
            assert 'error' in result[key], f"{key}应包含error字段"
        
        print("LLM失败情况下的并行提取测试通过!")
    
    def test_parallel_extraction_with_empty_text(self, extractor):
        """测试并行信息提取功能 - 空文本情况"""
        print("\n=== 测试并行信息提取功能 - 空文本情况 ===")
        
        # 执行并行提取
        result = extractor.extract_novel_information_parallel("")
        
        # 验证结果
        assert isinstance(result, dict), "结果应该是字典类型"
        assert 'original_text_length' in result, "结果应包含original_text_length字段"
        assert result['original_text_length'] == 0, "原始文本长度应为0"
        
        print("空文本情况下的并行提取测试通过!")
    
    def test_parallel_extraction_with_short_text(self, extractor):
        """测试并行信息提取功能 - 短文本情况"""
        print("\n=== 测试并行信息提取功能 - 短文本情况 ===")
        
        # 使用短文本
        short_text = "这是一个简短的测试文本。"
        
        # 执行并行提取
        result = extractor.extract_novel_information_parallel(short_text)
        
        # 验证结果
        assert isinstance(result, dict), "结果应该是字典类型"
        assert 'original_text_length' in result, "结果应包含original_text_length字段"
        assert result['original_text_length'] == len(short_text), "原始文本长度应匹配"
        
        print("短文本情况下的并行提取测试通过!")
    
    def test_parallel_extraction_result_structure(self, extractor, novel_content):
        """测试并行信息提取功能 - 结果结构验证"""
        print("\n=== 测试并行信息提取功能 - 结果结构验证 ===")
        
        # 执行并行提取
        result = extractor.extract_novel_information_parallel(novel_content)
        
        # 验证结果结构
        required_fields = [
            'characters', 'plot', 'satisfaction_points', 
            'original_text_length', 'cleaned_text_length', 
            'errors', 'completed_tasks', 'parallel_execution'
        ]
        
        for field in required_fields:
            assert field in result, f"结果应包含{field}字段"
        
        # 验证characters字段结构
        assert isinstance(result['characters'], dict), "characters应该是字典类型"
        assert 'success' in result['characters'], "characters应包含success字段"
        if result['characters']['success']:
            assert 'result' in result['characters'], "characters成功时应包含result字段"
            assert 'agent' in result['characters'], "characters应包含agent字段"
        
        # 验证plot字段结构
        assert isinstance(result['plot'], dict), "plot应该是字典类型"
        assert 'success' in result['plot'], "plot应包含success字段"
        if result['plot']['success']:
            assert 'result' in result['plot'], "plot成功时应包含result字段"
            assert 'agent' in result['plot'], "plot应包含agent字段"
        
        # 验证satisfaction_points字段结构
        assert isinstance(result['satisfaction_points'], dict), "satisfaction_points应该是字典类型"
        assert 'success' in result['satisfaction_points'], "satisfaction_points应包含success字段"
        if result['satisfaction_points']['success']:
            assert 'result' in result['satisfaction_points'], "satisfaction_points成功时应包含result字段"
            assert 'agent' in result['satisfaction_points'], "satisfaction_points应包含agent字段"
        
        # 验证其他字段
        assert isinstance(result['original_text_length'], int), "original_text_length应该是整数"
        assert isinstance(result['cleaned_text_length'], int), "cleaned_text_length应该是整数"
        assert isinstance(result['errors'], list), "errors应该是列表"
        assert isinstance(result['completed_tasks'], list), "completed_tasks应该是列表"
        assert isinstance(result['parallel_execution'], bool), "parallel_execution应该是布尔值"
        
        print("结果结构验证测试通过!")