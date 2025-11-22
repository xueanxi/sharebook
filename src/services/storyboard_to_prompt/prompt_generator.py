"""
提示词生成器
负责根据故事板场景生成AI绘画提示词
"""
from typing import Dict, List, Optional, Tuple, Any
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import os
import sys
from src.utils.logging_manager import LogModule,get_module_logger

# 获取项目根目录的绝对路径
current_file = os.path.abspath(__file__)
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
print(f"prompt_generator#项目根目录: {root_path}")
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from config.llm_config import LLMConfig
from .config.prompts import (
    SINGLE_SCENE_TO_PROMPT_CONVERTER
)
from src.utils.common_config import get_common_config


novel_type = get_common_config().get_novel_type()
logger = get_module_logger(LogModule.STORYBOARD_TO_PROMPT)

# 提示词生成器配置
PROMPT_GENERATOR_CONFIG = {
    "temperature": 0.5,  # 中等温度，平衡创造性和一致性
    "max_tokens": 3000,
}


class PromptGenerator:
    """提示词生成器类"""
    
    def __init__(self, llm=None):
        """
        初始化提示词生成器
        
        Args:
            llm: 语言模型实例，如果为None则使用默认配置
        """
        # 初始化LLM
        self.llm_kwargs = LLMConfig.get_openai_kwargs()
        self.llm_kwargs.update(PROMPT_GENERATOR_CONFIG)
        self.llm = ChatOpenAI(**self.llm_kwargs)
        self.scene_converter_prompt = SINGLE_SCENE_TO_PROMPT_CONVERTER
    
    
    def generate_prompt(self, scene: Dict[str, Any]) -> str:
        """
        根据场景信息生成英文提示词
        
        Args:
            scene: 场景信息字典
            
        Returns:
            英文提示词字符串
        """
        try:
            # 提取场景信息
            scene_info = self._extract_scene_info(scene)
            
            # 生成基础提示词
            formatted_prompt = self.scene_converter_prompt.format(novel_type=novel_type,scene_info=scene_info)
            prompt_text = self.llm.invoke(formatted_prompt).content
            
            # 解析提示词，只获取正面提示词部分
            positive_prompt = self._parse_english_prompt(prompt_text)
            
            logger.info(f"成功生成场景 {scene.get('scene_id')} 的英文提示词")
            return positive_prompt
            
        except Exception as e:
            logger.error(f"生成提示词失败: {str(e)}")
            raise Exception(f"生成提示词失败: {str(e)}")
    
    def _extract_scene_info(self, scene: Dict[str, Any]) -> Dict[str, str]:
        """提取场景信息供LLM使用"""
        visual_narrative = scene.get('visual_narrative', {})
        composition = visual_narrative.get('composition', {})
        environment = visual_narrative.get('environment', {})
        style = visual_narrative.get('style', {})
        
        # 处理角色信息
        characters = scene.get('characters', [])
        character_descriptions = []
        for char in characters:
            char_desc = f"{char.get('name', '')}: {char.get('appearance', '')}, {char.get('expression', '')}, {char.get('action', '')}, {char.get('emotion', '')}"
            character_descriptions.append(char_desc)
        
        return {
            'scene_description': scene.get('scene_description', ''),
            'environment': scene.get('environment', ''),
            'atmosphere': scene.get('atmosphere', ''),
            'time': scene.get('time', ''),
            'characters': '; '.join(character_descriptions),
            'main_action': scene.get('main_action', ''),
            'emotional_tone': scene.get('emotional_tone', ''),
            'shot_type': composition.get('shot_type', '中景'),
            'angle': composition.get('angle', '平视'),
            'layout': composition.get('layout', ''),
            'lighting': environment.get('lighting', '自然光'),
            'color_scheme': environment.get('color_scheme', ''),
            'art_style': style.get('art_style', '漫画风格'),
            'quality_tags': ', '.join(style.get('quality_tags', []))
        }
    
    def _parse_english_prompt(self, result: str) -> str:
        """解析LLM生成的英文提示词结果"""
        try:
            lines = result.strip().split('\n')
            english_prompt = ""
            
            # 查找Visual Prompt部分
            found_visual_prompt = False
            for line in lines:
                line = line.strip()
                if line.startswith('Visual Prompt:'):
                    found_visual_prompt = True
                    # 提取Visual Prompt后的内容
                    prompt_start = line.replace('Visual Prompt:', '').strip()
                    if prompt_start:
                        english_prompt = prompt_start
                    continue
                elif found_visual_prompt and line:
                    # 继续收集Visual Prompt的内容，直到遇到下一个标题
                    if line.startswith(('Art Style Guidance:', 'Character Focus:')):
                        break
                    english_prompt += ' ' + line
            
            # 如果没有找到Visual Prompt，尝试提取所有英文内容
            if not english_prompt:
                for line in lines:
                    line = line.strip()
                    # 简单的英文检测：检查是否包含英文字母
                    if any(char.isalpha() and char.isascii() for char in line):
                        if english_prompt:
                            english_prompt += ' '
                        english_prompt += line
            
            return english_prompt.strip()
        except Exception as e:
            logger.error(f"解析英文提示词结果失败: {str(e)}")
            return result
         