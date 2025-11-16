"""
测试提示词生成功能
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.services.novel_to_comic.core.workflow import NovelToComicWorkflow
from src.services.novel_to_comic.prompt_generator import PromptGenerator


def test_prompt_generator():
    """测试提示词生成器"""
    print("=== 测试提示词生成器 ===")
    
    # 创建提示词生成器
    generator = PromptGenerator()
    
    # 处理所有章节
    generator.process_all_chapters()
    
    print("提示词生成完成!")


def test_workflow_integration():
    """测试工作流集成"""
    print("\n测试工作流集成...")
    
    # 创建工作流实例
    workflow = NovelToComicWorkflow(enable_parallel=False)
    
    # 测试文件路径
    test_file = "data/cleaned_novel/第一章 遇强则强.txt"
    chapter_title = "第一章 遇强则强"
    
    if not os.path.exists(test_file):
        print(f"测试文件不存在: {test_file}")
        return
    
    try:
        # 处理章节
        print(f"正在处理章节: {test_file}")
        result = workflow.process_chapter(test_file, chapter_title, "玄幻")
        
        # 保存结果
        output_path = workflow.save_result(result)
        print(f"故事板已保存到: {output_path}")
        
        # 生成提示词和旁白
        prompts = workflow.generate_prompts_for_chapter(output_path)
        print(f"成功生成 {len(prompts)} 个提示词和旁白")
        
        # 保存提示词和旁白
        prompts_output_path = workflow.save_prompts(prompts, chapter_title)
        print(f"提示词已保存到: {prompts_output_path}")
        
        # 显示前3个提示词
        if prompts:
            print("\n前3个提示词示例:")
            for i, prompt in enumerate(prompts[:3]):
                print(f"\n场景 {i+1}:")
                print(f"提示词: {prompt.get('prompt', 'N/A')}")
                print(f"旁白: {prompt.get('narration', 'N/A')}")
        
        print("\n✓ 工作流集成测试成功!")
        
    except Exception as e:
        print(f"✗ 工作流集成测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 可以选择测试模式
    test_mode = input("选择测试模式 (1: 直接测试提示词生成器, 2: 测试工作流中的提示词生成): ")
    
    if test_mode == "1":
        test_prompt_generator()
    elif test_mode == "2":
        test_workflow_integration()
    else:
        print("默认测试提示词生成器...")
        test_prompt_generator()