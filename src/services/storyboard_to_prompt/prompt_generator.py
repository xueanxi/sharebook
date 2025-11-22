"""
提示词生成器类
负责根据场景信息生成图像生成提示词
"""
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from config.llm_config import LLMConfig
from .config.prompts import (
    SINGLE_SCENE_TO_PROMPT_CONVERTER
)

logger = logging.getLogger(__name__)

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
        
        self._init_chains()
    
    def _init_chains(self):
        """初始化LLM链"""
        # 新版本langchain使用不同的方式创建链
        self.scene_converter_prompt = SINGLE_SCENE_TO_PROMPT_CONVERTER
        # 其他提示词模板暂时留空，后续可以添加
        self.batch_optimizer_prompt = ""
        self.special_handler_prompt = ""
        self.quality_checker_prompt = ""
    
    def generate_prompt(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据场景信息生成提示词
        
        Args:
            scene: 场景信息字典
            
        Returns:
            包含提示词的字典
        """
        try:
            # 提取场景信息
            scene_info = self._extract_scene_info(scene)
            
            # 生成基础提示词
            formatted_prompt = self.scene_converter_prompt.format(**scene_info)
            prompt_text = self.llm.invoke(formatted_prompt).content
            
            # 解析提示词
            positive_prompt, negative_prompt = self._parse_prompt_result(prompt_text)
            
            # 应用优化规则
            optimized_prompt = self._apply_optimization_rules(positive_prompt, scene_info)
            
            # 生成最终提示词
            final_prompt = {
                'prompt_id': f"{scene.get('segment_index', 0)}-{scene.get('scene_id', 1)}",
                'segment_id': scene.get('segment_id', ''),
                'segment_index': scene.get('segment_index', 0),
                'scene_id': scene.get('scene_id', 1),
                'scene_index_in_segment': scene.get('scene_index_in_segment', 0),
                'text_content': scene.get('text', ''),
                'prompt_text': optimized_prompt,
                'negative_prompt': negative_prompt or self._generate_default_negative_prompt(),
                'metadata': {
                    'style': self._extract_style(scene),
                    'quality_tags': self._extract_quality_tags(scene),
                    'aspect_ratio': self._determine_aspect_ratio(scene),
                    'importance_score': scene.get('importance_score', 5),
                    'visual_suitability': scene.get('visual_suitability', 5)
                }
            }
            
            logger.info(f"成功生成场景 {scene.get('scene_id')} 的提示词")
            return final_prompt
            
        except Exception as e:
            logger.error(f"生成提示词失败: {str(e)}")
            return self._generate_fallback_prompt(scene)
    
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
    
    def _parse_prompt_result(self, result: str) -> Tuple[str, Optional[str]]:
        """解析LLM生成的提示词结果"""
        try:
            lines = result.strip().split('\n')
            positive_prompt = ""
            negative_prompt = ""
            
            current_section = None
            for line in lines:
                line = line.strip()
                if line.startswith('正面提示词：'):
                    current_section = 'positive'
                    positive_prompt = line.replace('正面提示词：', '').strip()
                elif line.startswith('负面提示词：'):
                    current_section = 'negative'
                    negative_prompt = line.replace('负面提示词：', '').strip()
                elif current_section == 'positive' and line:
                    positive_prompt += ' ' + line
                elif current_section == 'negative' and line:
                    negative_prompt += ' ' + line
            
            return positive_prompt.strip(), negative_prompt.strip() if negative_prompt else None
            
        except Exception as e:
            logger.error(f"解析提示词结果失败: {str(e)}")
            return result, None
    
    def _apply_optimization_rules(self, prompt: str, scene_info: Dict[str, str]) -> str:
        """应用提示词优化规则"""
        # 规则1: 确保包含漫画风格
        if '漫画' not in prompt and 'anime' not in prompt.lower():
            prompt += ', 漫画风格'
        
        # 规则2: 添加质量标签
        quality_tags = ['高质量', '细节丰富', '8K']
        for tag in quality_tags:
            if tag not in prompt:
                prompt += f', {tag}'
        
        # 规则3: 确保角色描述一致性
        if scene_info['characters']:
            prompt = f"{scene_info['characters']}, {prompt}"
        
        # 规则4: 优化场景描述
        if scene_info['environment']:
            prompt = f"{scene_info['environment']}, {prompt}"
        
        return prompt
    
    def _generate_default_negative_prompt(self) -> str:
        """生成默认负面提示词"""
        return "低质量, 变形, 模糊, 丑陋, 水印, 文字, 签名, 多余的手指, 错误的解剖结构"
    
    def _extract_style(self, scene: Dict[str, Any]) -> str:
        """提取艺术风格"""
        visual_narrative = scene.get('visual_narrative', {})
        style = visual_narrative.get('style', {})
        return style.get('art_style', '漫画风格')
    
    def _extract_quality_tags(self, scene: Dict[str, Any]) -> List[str]:
        """提取质量标签"""
        visual_narrative = scene.get('visual_narrative', {})
        style = visual_narrative.get('style', {})
        return style.get('quality_tags', ['高质量', '细节丰富'])
    
    def _determine_aspect_ratio(self, scene: Dict[str, Any]) -> str:
        """根据场景类型确定宽高比"""
        shot_type = scene.get('visual_narrative', {}).get('composition', {}).get('shot_type', '')
        
        if '特写' in shot_type:
            return "4:5"
        elif '全景' in shot_type or '远景' in shot_type:
            return "16:9"
        else:
            return "3:4"
    
    def _generate_fallback_prompt(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        """生成备用提示词"""
        scene_description = scene.get('scene_description', '场景')
        environment = scene.get('environment', '环境')
        
        fallback_prompt = f"{scene_description}, {environment}, 漫画风格, 高质量, 细节丰富"
        
        return {
            'prompt_id': f"{scene.get('segment_index', 0)}-{scene.get('scene_id', 1)}",
            'segment_id': scene.get('segment_id', ''),
            'segment_index': scene.get('segment_index', 0),
            'scene_id': scene.get('scene_id', 1),
            'scene_index_in_segment': scene.get('scene_index_in_segment', 0),
            'text_content': scene.get('text', ''),
            'prompt_text': fallback_prompt,
            'negative_prompt': self._generate_default_negative_prompt(),
            'metadata': {
                'style': '漫画风格',
                'quality_tags': ['高质量', '细节丰富'],
                'aspect_ratio': '3:4',
                'importance_score': scene.get('importance_score', 5),
                'visual_suitability': scene.get('visual_suitability', 5)
            }
        }
    
    def optimize_batch_prompts(self, chapter_title: str, prompts: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        批量优化提示词以确保风格一致性
        
        Args:
            chapter_title: 章节标题
            prompts: 提示词列表
            
        Returns:
            优化建议字典
        """
        try:
            # 生成场景概要
            scenes_summary = self._generate_scenes_summary(prompts)
            
            # 获取风格一致性建议
            formatted_prompt = self.batch_optimizer_prompt.format(
                chapter_title=chapter_title,
                scenes_summary=scenes_summary,
                style_consistency_notes='确保角色外观、场景风格、色彩方案的连贯性'
            )
            result = self.llm.invoke(formatted_prompt)
            
            return self._parse_optimization_result(result.content)
            
        except Exception as e:
            logger.error(f"批量优化提示词失败: {str(e)}")
            return {
                '角色一致性': '保持角色外观特征一致',
                '场景一致性': '保持场景风格统一',
                '色彩一致性': '保持色彩方案连贯',
                '风格指导': '保持整体艺术风格统一'
            }
    
    def _generate_scenes_summary(self, prompts: List[Dict[str, Any]]) -> str:
        """生成场景概要"""
        summary_parts = []
        for i, prompt in enumerate(prompts[:5]):  # 只取前5个场景作为参考
            summary_parts.append(f"场景{i+1}: {prompt.get('prompt_text', '')[:100]}...")
        
        return '\n'.join(summary_parts)
    
    def _parse_optimization_result(self, result: str) -> Dict[str, str]:
        """解析优化结果"""
        try:
            lines = result.strip().split('\n')
            optimization_dict = {}
            
            for line in lines:
                line = line.strip()
                if '：' in line:
                    key, value = line.split('：', 1)
                    optimization_dict[key] = value
            
            return optimization_dict
            
        except Exception as e:
            logger.error(f"解析优化结果失败: {str(e)}")
            return {
                '角色一致性': '保持角色外观特征一致',
                '场景一致性': '保持场景风格统一',
                '色彩一致性': '保持色彩方案连贯',
                '风格指导': '保持整体艺术风格统一'
            }
    
    def check_prompt_quality(self, prompt: str, scene_context: str) -> Dict[str, Any]:
        """
        检查提示词质量
        
        Args:
            prompt: 提示词
            scene_context: 场景上下文
            
        Returns:
            质量检查结果
        """
        try:
            formatted_prompt = self.quality_checker_prompt.format(
                prompt=prompt,
                scene_context=scene_context
            )
            result = self.llm.invoke(formatted_prompt)
            
            return self._parse_quality_result(result.content)
            
        except Exception as e:
            logger.error(f"检查提示词质量失败: {str(e)}")
            return {
                'quality_score': 7,
                'improvement_suggestions': '增加更多视觉细节',
                'needs_optimization': False
            }
    
    def _parse_quality_result(self, result: str) -> Dict[str, Any]:
        """解析质量检查结果"""
        try:
            lines = result.strip().split('\n')
            quality_dict = {}
            
            for line in lines:
                line = line.strip()
                if '：' in line:
                    key, value = line.split('：', 1)
                    if '评分' in key:
                        quality_dict['quality_score'] = int(value.strip())
                    elif '建议' in key:
                        quality_dict['improvement_suggestions'] = value.strip()
                    elif '优化' in key:
                        quality_dict['needs_optimization'] = '是' in value
            
            return quality_dict
            
        except Exception as e:
            logger.error(f"解析质量检查结果失败: {str(e)}")
            return {
                'quality_score': 7,
                'improvement_suggestions': '增加更多视觉细节',
                'needs_optimization': False
            }
