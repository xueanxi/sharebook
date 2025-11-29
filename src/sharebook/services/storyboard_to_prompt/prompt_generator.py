"""
提示词生成器
负责根据故事板场景生成AI绘画提示词
"""
from typing import Dict, List, Optional, Tuple, Any
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import os
import sys
from sharebook.utils.logging_manager import LogModule,get_module_logger

# 获取项目根目录的绝对路径
current_file = os.path.abspath(__file__)
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
print(f"prompt_generator#项目根目录: {root_path}")
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from sharebook.config.llm_config import LLMConfig
from .config.prompts import (
    SINGLE_SCENE_TO_PROMPT_CONVERTER,
    SINGLE_CHARACTER_PROMPT_TEMPLATE,
    DOUBLE_CHARACTER_PROMPT_TEMPLATE,
    MULTIPLE_CHARACTER_PROMPT_TEMPLATE,
    CHARACTER_FEATURE_ANALYSIS_TEMPLATE
)
from sharebook.utils.common_config import get_common_config


novel_type = get_common_config().get_novel_type()
logger = get_module_logger(LogModule.STORYBOARD_TO_PROMPT)

# 提示词生成器配置
PROMPT_GENERATOR_CONFIG = {
    "temperature": 0.5,  # 中等温度，平衡创造性和一致性
    "max_tokens": 3000,
}

# 角色分析配置
CHARACTER_ANALYSIS_CONFIG = {
    "temperature": 0.3,  # 较低温度，确保分析准确性
    "max_tokens": 2000,
}

# 多角色筛选配置
MULTIPLE_CHARACTER_CONFIG = {
    "temperature": 0.3,  # 较低温度，确保选择合理性
    "max_tokens": 2000,
}


class PromptGenerator:
    """提示词生成器类"""
    
    def __init__(self, llm=None, character_manager=None, image_manager=None):
        """
        初始化提示词生成器
        
        Args:
            llm: 语言模型实例，如果为None则使用默认配置
            character_manager: 角色数据管理器实例
            image_manager: 参考图片管理器实例
        """
        # 初始化LLM
        self.llm_kwargs = LLMConfig.get_openai_kwargs()
        self.llm_kwargs.update(PROMPT_GENERATOR_CONFIG)
        self.llm = ChatOpenAI(**self.llm_kwargs)
        self.scene_converter_prompt = SINGLE_SCENE_TO_PROMPT_CONVERTER
        self.single_character_prompt = SINGLE_CHARACTER_PROMPT_TEMPLATE
        self.double_character_prompt = DOUBLE_CHARACTER_PROMPT_TEMPLATE
        self.multiple_character_prompt = MULTIPLE_CHARACTER_PROMPT_TEMPLATE
        self.character_analysis_prompt = CHARACTER_FEATURE_ANALYSIS_TEMPLATE
        
        # 初始化管理器
        self.character_manager = character_manager
        self.image_manager = image_manager
    
    
    def generate_prompt(self, scene: Dict[str, Any], reference_images: Optional[List[str]] = None) -> str:
        """
        根据场景信息和参考图片生成英文提示词
        
        Args:
            scene: 场景信息字典
            reference_images: 参考图片路径列表（可选）
            
        Returns:
            英文提示词字符串
        """
        try:
            # 分析场景中的角色
            character_analysis = self._analyze_characters(scene)
            character_count = len(character_analysis['characters'])
            
            # 根据角色数量选择生成策略
            if character_count == 1:
                prompt = self._generate_single_character_prompt(scene)
            elif character_count == 2:
                prompt = self._generate_double_character_prompt(scene, character_analysis)
            else:
                prompt = self._generate_multiple_character_prompt(scene, character_analysis)
            
            logger.info(f"成功生成场景 {scene.get('scene_id')} 的英文提示词（角色数量：{character_count}）")
            return prompt
            
        except Exception as e:
            logger.error(f"生成提示词失败: {str(e)}")
            raise Exception(f"生成提示词失败: {str(e)}")
    
    def generate_prompt_with_characters(self, scene: Dict[str, Any], reference_images: Optional[List[str]] = None) -> tuple[str, List[Dict[str, Any]]]:
        """
        根据场景信息和参考图片生成英文提示词，并返回角色信息
        
        Args:
            scene: 场景信息字典
            reference_images: 参考图片路径列表（可选）
            
        Returns:
            (英文提示词字符串, 角色信息列表)
        """
        try:
            # 分析场景中的角色
            character_analysis = self._analyze_characters(scene)
            character_count = len(character_analysis['characters'])
            
            # 根据角色数量选择生成策略
            if character_count == 1:
                prompt = self._generate_single_character_prompt(scene)
            elif character_count == 2:
                prompt = self._generate_double_character_prompt(scene, character_analysis)
            else:
                prompt = self._generate_multiple_character_prompt(scene, character_analysis)
            
            # 获取角色详细信息
            scene_characters = self._get_scene_characters_info(character_analysis['characters'])
            
            logger.info(f"成功生成场景 {scene.get('scene_id')} 的英文提示词（角色数量：{character_count}）")
            return prompt, scene_characters
            
        except Exception as e:
            logger.error(f"生成提示词失败: {str(e)}")
            raise Exception(f"生成提示词失败: {str(e)}")
    
    def _get_scene_characters_info(self, characters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        获取场景中角色的详细信息
        
        Args:
            characters: 角色信息列表
            
        Returns:
            角色详细信息列表
        """
        scene_characters = []
        
        for char in characters:
            char_name = char.get('name', '')
            if not char_name:
                continue
            
            # 从角色数据管理器获取角色信息
            character_info = {}
            if self.character_manager:
                character_info = self.character_manager.get_character_reference_info(char_name)
            
            # 如果没有找到角色信息，使用基本信息
            if not character_info:
                character_info = {
                    'name': char_name,
                    'aliases': [],
                    'gender': 'unknown',
                    'character_type': 'unknown',
                    'reference_image_path': None,
                    'character_prompt': char.get('appearance', ''),  # 使用外貌作为提示词
                    'appearance': char.get('appearance', ''),
                    'clothing': ''
                }
            
            # 获取参考图片信息
            if self.image_manager and character_info['name']:
                best_image = self.image_manager.get_best_reference_image(character_info['name'])
                if best_image:
                    character_info['reference_image_path'] = best_image['path']
                    character_info['image_validation'] = best_image['validation']
            
            scene_characters.append(character_info)
        
        return scene_characters
    
    def _analyze_characters(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析场景中的角色
        
        Args:
            scene: 场景信息字典
            
        Returns:
            角色分析结果
        """
        try:
            characters = scene.get('characters', [])
            
            # 提取角色基本信息
            character_info = []
            for char in characters:
                char_info = {
                    'name': char.get('name', ''),
                    'appearance': char.get('appearance', ''),
                    'expression': char.get('expression', ''),
                    'action': char.get('action', ''),
                    'emotion': char.get('emotion', ''),
                    'features': self._extract_character_features(char)
                }
                character_info.append(char_info)
            
            return {
                'characters': character_info,
                'count': len(character_info)
            }
            
        except Exception as e:
            logger.error(f"角色分析失败: {str(e)}")
            return {'characters': [], 'count': 0}
    
    def _extract_character_features(self, character: Dict[str, Any]) -> Dict[str, str]:
        """
        提取角色特征用于差异化描述
        
        Args:
            character: 角色信息字典
            
        Returns:
            角色特征字典
        """
        try:
            appearance = character.get('appearance', '')
            
            # 提取性别特征
            gender = 'unknown'
            if any(word in appearance for word in ['男', '公子', '君', '他']):
                gender = 'male'
            elif any(word in appearance for word in ['女', '姑娘', '小姐', '她']):
                gender = 'female'
            
            # 提取发色特征
            hair_color = 'unknown'
            if '银发' in appearance or '白发' in appearance:
                hair_color = 'silver'
            elif '黑发' in appearance:
                hair_color = 'black'
            elif '金发' in appearance:
                hair_color = 'golden'
            elif '红发' in appearance:
                hair_color = 'red'
            
            # 提取服装颜色
            clothing_color = 'unknown'
            if '玄色' in appearance or '黑色' in appearance:
                clothing_color = 'black'
            elif '红色' in appearance or '红衣' in appearance:
                clothing_color = 'red'
            elif '蓝色' in appearance or '蓝衣' in appearance:
                clothing_color = 'blue'
            elif '白色' in appearance or '白衣' in appearance:
                clothing_color = 'white'
            
            # 提取特殊标记
            special_marks = []
            if '疤痕' in appearance or '伤疤' in appearance:
                special_marks.append('scar')
            if '纹身' in appearance or '符文' in appearance:
                special_marks.append('tattoo')
            if '银纹' in appearance:
                special_marks.append('silver_pattern')
            
            return {
                'gender': gender,
                'hair_color': hair_color,
                'clothing_color': clothing_color,
                'special_marks': special_marks
            }
            
        except Exception as e:
            logger.error(f"角色特征提取失败: {str(e)}")
            return {
                'gender': 'unknown',
                'hair_color': 'unknown',
                'clothing_color': 'unknown',
                'special_marks': []
            }
    
    def _generate_single_character_prompt(self, scene: Dict[str, Any]) -> str:
        """
        生成单角色场景的提示词
        
        Args:
            scene: 场景信息字典
            
        Returns:
            英文提示词字符串
        """
        try:
            # 提取场景信息
            scene_info = self._extract_scene_info(scene)
            
            # 生成单角色提示词
            formatted_prompt = self.single_character_prompt.format(
                novel_type=novel_type,
                scene_info=scene_info
            )
            
            # 调用LLM生成提示词
            prompt_text = self.llm.invoke(formatted_prompt).content
            
            # 解析提示词
            positive_prompt = self._parse_english_prompt(prompt_text)
            
            return positive_prompt
            
        except Exception as e:
            logger.error(f"单角色提示词生成失败: {str(e)}")
            raise Exception(f"单角色提示词生成失败: {str(e)}")
    
    def _generate_double_character_prompt(self, scene: Dict[str, Any], character_analysis: Dict[str, Any]) -> str:
        """
        生成双角色场景的提示词
        
        Args:
            scene: 场景信息字典
            character_analysis: 角色分析结果
            
        Returns:
            英文提示词字符串
        """
        try:
            # 提取场景信息
            scene_info = self._extract_scene_info(scene)
            
            # 生成角色特征分析
            character_analysis_text = self._generate_character_analysis(character_analysis['characters'])
            
            # 生成双角色提示词
            formatted_prompt = self.double_character_prompt.format(
                novel_type=novel_type,
                scene_info=scene_info,
                character_analysis=character_analysis_text
            )
            
            # 调用LLM生成提示词
            prompt_text = self.llm.invoke(formatted_prompt).content
            
            # 解析提示词
            positive_prompt = self._parse_english_prompt(prompt_text)
            
            return positive_prompt
            
        except Exception as e:
            logger.error(f"双角色提示词生成失败: {str(e)}")
            raise Exception(f"双角色提示词生成失败: {str(e)}")
    
    def _generate_multiple_character_prompt(self, scene: Dict[str, Any], character_analysis: Dict[str, Any]) -> str:
        """
        生成多角色场景的提示词
        
        Args:
            scene: 场景信息字典
            character_analysis: 角色分析结果
            
        Returns:
            英文提示词字符串
        """
        try:
            # 提取场景信息
            scene_info = self._extract_scene_info(scene)
            
            # 筛选关键角色
            key_characters = self._select_key_characters(character_analysis['characters'], scene)
            
            # 如果筛选失败，使用前两个角色
            if len(key_characters) < 2:
                key_characters = character_analysis['characters'][:2]
            
            # 生成角色信息文本
            all_characters_text = self._format_characters_info(character_analysis['characters'])
            
            # 生成多角色提示词
            formatted_prompt = self.multiple_character_prompt.format(
                novel_type=novel_type,
                scene_info=scene_info,
                all_characters=all_characters_text
            )
            
            # 调用LLM生成提示词
            prompt_text = self.llm.invoke(formatted_prompt).content
            
            # 解析提示词
            positive_prompt = self._parse_english_prompt(prompt_text)
            
            return positive_prompt
            
        except Exception as e:
            logger.error(f"多角色提示词生成失败: {str(e)}")
            raise Exception(f"多角色提示词生成失败: {str(e)}")
    
    def _generate_character_analysis(self, characters: List[Dict[str, Any]]) -> str:
        """
        生成角色特征分析文本
        
        Args:
            characters: 角色信息列表
            
        Returns:
            角色分析文本
        """
        try:
            # 格式化角色信息
            characters_text = ""
            for i, char in enumerate(characters, 1):
                characters_text += f"角色{i}: {char.get('name', '')}\n"
                characters_text += f"外貌: {char.get('appearance', '')}\n"
                characters_text += f"表情: {char.get('expression', '')}\n"
                characters_text += f"动作: {char.get('action', '')}\n"
                characters_text += f"特征: {char.get('features', {})}\n\n"
            
            # 使用LLM进行特征分析
            formatted_prompt = self.character_analysis_prompt.format(
                characters=characters_text
            )
            
            # 使用较低温度调用LLM
            analysis_config = self.llm_kwargs.copy()
            analysis_config.update(CHARACTER_ANALYSIS_CONFIG)
            analysis_llm = ChatOpenAI(**analysis_config)
            
            analysis_result = analysis_llm.invoke(formatted_prompt).content
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"角色特征分析失败: {str(e)}")
            return "角色特征分析失败"
    
    def _select_key_characters(self, characters: List[Dict[str, Any]], scene: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        筛选关键角色
        
        Args:
            characters: 角色信息列表
            scene: 场景信息字典
            
        Returns:
            关键角色列表
        """
        try:
            # 简单的筛选逻辑：选择有动作和表情的角色
            key_characters = []
            for char in characters:
                action = char.get('action', '')
                emotion = char.get('emotion', '')
                
                # 如果角色有明显的动作或情感，认为是关键角色
                if action and emotion:
                    key_characters.append(char)
                    if len(key_characters) >= 2:
                        break
            
            # 如果没有找到关键角色，返回前两个角色
            if len(key_characters) < 2:
                return characters[:2]
            
            return key_characters
            
        except Exception as e:
            logger.error(f"关键角色筛选失败: {str(e)}")
            return characters[:2]
    
    def _format_characters_info(self, characters: List[Dict[str, Any]]) -> str:
        """
        格式化角色信息为文本
        
        Args:
            characters: 角色信息列表
            
        Returns:
            格式化的角色信息文本
        """
        try:
            characters_text = ""
            for i, char in enumerate(characters, 1):
                characters_text += f"角色{i} - {char.get('name', '')}:\n"
                characters_text += f"  外貌: {char.get('appearance', '')}\n"
                characters_text += f"  表情: {char.get('expression', '')}\n"
                characters_text += f"  动作: {char.get('action', '')}\n"
                characters_text += f"  情感: {char.get('emotion', '')}\n"
                characters_text += f"  特征: {char.get('features', {})}\n\n"
            
            return characters_text
            
        except Exception as e:
            logger.error(f"角色信息格式化失败: {str(e)}")
            return "角色信息格式化失败"
    
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
         