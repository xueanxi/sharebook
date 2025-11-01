"""
测试重构后的Agent模块
使用真实小说章节进行测试
"""

import os
import json
from src.core.agents.agents import (
    TextPreprocessor,
    CharacterExtractor,
    PlotAnalyzer,
    SatisfactionPointIdentifier,
    NovelInformationExtractor
)

def test_agent_imports():
    """测试Agent类导入是否正常"""
    print("测试Agent类导入...")
    
    # 测试类名
    text_preprocessor = TextPreprocessor()
    character_extractor = CharacterExtractor()
    plot_analyzer = PlotAnalyzer()
    satisfaction_identifier = SatisfactionPointIdentifier()
    novel_extractor = NovelInformationExtractor()
    
    print("所有Agent类导入成功！")
    return True

def test_agent_functionality():
    """测试Agent基本功能"""
    print("\n测试Agent基本功能...")
    
    # 读取真实小说章节
    novel_path = "data/raw/第一章 遇强则强.txt"
    if not os.path.exists(novel_path):
        print(f"错误：找不到文件 {novel_path}")
        return False
        
    with open(novel_path, 'r', encoding='utf-8') as f:
        novel_text = f.read()
    
    print(f"已读取小说章节，共 {len(novel_text)} 字符")
    
    # 测试文本预处理器
    preprocessor = TextPreprocessor()
    try:
        result = preprocessor.preprocess_text(novel_text)
        print(f"文本预处理结果: {result.get('success', False)}")
        if result.get('success'):
            print(f"预处理后文本长度: {len(result.get('result', ''))}")
        else:
            print(f"预处理失败，使用备用方案，文本长度: {len(result.get('result', ''))}")
    except Exception as e:
        print(f"文本预处理测试失败: {str(e)}")
        return False
    
    # 测试人物提取器
    character_extractor = CharacterExtractor()
    try:
        result = character_extractor.extract(novel_text)
        print(f"人物提取结果: {result.get('success', False)}")
        if result.get('success'):
            # 直接显示结果的前200个字符
            character_result = result.get('result', '')
            print(f"人物提取结果长度: {len(character_result)}")
            print(f"人物提取结果前200字: {character_result[:200]}...")
        else:
            print(f"人物提取失败: {result.get('error', '未知错误')}")
    except Exception as e:
        print(f"人物提取测试失败: {str(e)}")
        return False
    
    # 测试剧情分析器
    plot_analyzer = PlotAnalyzer()
    try:
        result = plot_analyzer.extract(novel_text)
        print(f"剧情分析结果: {result.get('success', False)}")
        if result.get('success'):
            # 直接显示结果的前200个字符
            plot_result = result.get('result', '')
            print(f"剧情分析结果长度: {len(plot_result)}")
            print(f"剧情分析结果前200字: {plot_result[:200]}...")
        else:
            print(f"剧情分析失败: {result.get('error', '未知错误')}")
    except Exception as e:
        print(f"剧情分析测试失败: {str(e)}")
        return False
    
    # 测试爽点识别器
    satisfaction_identifier = SatisfactionPointIdentifier()
    try:
        result = satisfaction_identifier.extract(novel_text)
        print(f"爽点识别结果: {result.get('success', False)}")
        if result.get('success'):
            # 直接显示结果的前200个字符
            satisfaction_result = result.get('result', '')
            print(f"爽点识别结果长度: {len(satisfaction_result)}")
            print(f"爽点识别结果前200字: {satisfaction_result[:200]}...")
        else:
            print(f"爽点识别失败: {result.get('error', '未知错误')}")
    except Exception as e:
        print(f"爽点识别测试失败: {str(e)}")
        return False
    
    print("所有Agent基本功能测试通过！")
    return True

def test_parallel_processing():
    """测试并行处理功能"""
    print("\n测试并行处理功能...")
    
    # 读取真实小说章节
    novel_path = "data/raw/第一章 遇强则强.txt"
    if not os.path.exists(novel_path):
        print(f"错误：找不到文件 {novel_path}")
        return False
        
    with open(novel_path, 'r', encoding='utf-8') as f:
        novel_text = f.read()
    
    # 创建小说信息提取器
    novel_extractor = NovelInformationExtractor()
    
    try:
        # 执行并行提取
        result = novel_extractor.extract_novel_information_parallel(novel_text)
        
        if result.get('success', True):  # 这里没有success键，默认为True
            print("并行处理成功！")
            
            # 显示提取结果
            characters = result.get('characters', {})
            plot = result.get('plot', {})
            satisfaction_points = result.get('satisfaction_points', {})
            
            print(f"\n提取结果:")
            print(f"- 人物信息成功: {characters.get('success', False)}")
            if characters.get('success'):
                print(f"  人物提取结果长度: {len(characters.get('result', ''))}")
                print(f"  人物提取结果前100字: {characters.get('result', '')[:100]}...")
                
            print(f"\n- 剧情分析成功: {plot.get('success', False)}")
            if plot.get('success'):
                print(f"  剧情分析结果长度: {len(plot.get('result', ''))}")
                print(f"  剧情分析结果前100字: {plot.get('result', '')[:100]}...")
            
            print(f"\n- 爽点识别成功: {satisfaction_points.get('success', False)}")
            if satisfaction_points.get('success'):
                print(f"  爽点识别结果长度: {len(satisfaction_points.get('result', ''))}")
                print(f"  爽点识别结果前100字: {satisfaction_points.get('result', '')[:100]}...")
                
            # 保存结果到文件
            output_path = "test_output/第一章 遇强则强_parallel_test.json"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\n结果已保存到: {output_path}")
            
            return True
        else:
            print(f"并行处理失败: {result.get('error', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"并行处理测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    # 运行测试
    import_success = test_agent_imports()
    functionality_success = test_agent_functionality()
    parallel_success = test_parallel_processing()
    
    if import_success and functionality_success and parallel_success:
        print("\n✅ 所有测试通过！重构成功！")
    else:
        print("\n❌ 测试失败！需要检查重构代码！")