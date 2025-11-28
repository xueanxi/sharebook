"""
视觉文案生成Agent
"""

import json
import time
from typing import List, Dict, Any, Optional

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI

from src.services.novel_to_comic.config.prompts import VISUAL_PROMPT
from src.services.novel_to_comic.config.processing_config import VISUAL_GENERATOR_CONFIG, MAX_RETRIES, RETRY_DELAY
from src.services.novel_to_comic.models.data_models import (
    Scene, VisualNarrative, VisualCharacter, Composition, 
    Environment, Style, Narration, StoryboardSuggestions
)
from src.services.novel_to_comic.utils.character_manager import CharacterManager
from src.utils import common_config
from src.utils.logging_manager import get_module_logger, LogModule
from config.llm_config import LLMConfig

logger = get_module_logger(LogModule.NOVEL_TO_COMIC)
is_show_llm_log = common_config.get_common_config().get_show_llm_log()

class VisualNarrativeAgent:
    """视觉文案生成Agent"""
    
    def __init__(self, character_manager: CharacterManager):
        self.character_manager = character_manager
        self.logger = logger
        self.file_logger = get_module_logger(LogModule.NOVEL_TO_COMIC)
        
        # 初始化LLM
        self.llm_kwargs = LLMConfig.get_openai_kwargs()
        self.llm_kwargs.update(VISUAL_GENERATOR_CONFIG)
        self.llm = ChatOpenAI(**self.llm_kwargs)
        
        # 创建提示模板
        self.prompt_template = ChatPromptTemplate.from_template(VISUAL_PROMPT)
        
        # 创建输出解析器
        self.output_parser = JsonOutputParser()
        
        # 创建处理链
        self.chain = self.prompt_template | self.llm | self.output_parser
    
    def generate_visual_narrative(self, scene: Scene, context: Dict[str, Any]) -> VisualNarrative:
        """
        生成视觉叙述信息
        
        Args:
            scene: 场景信息
            context: 上下文信息
            
        Returns:
            视觉叙述信息
        """
        self.logger.info(f"开始为场景 {scene.scene_id} 生成视觉叙述")
        
        # 准备场景信息
        scene_info = self._format_scene_info(scene)
        
        # 准备角色详细信息
        character_details = self._get_character_details(scene)
        
        # 准备输入参数
        input_params = {
            "novel_type": context.get("novel_type", "未知"),
            "chapter_title": context.get("chapter_title", "未知章节"),
            "previous_scene_summary": context.get("previous_scene_summary", "无"),
            "importance_score": scene.importance_score,
            "visual_suitability": scene.visual_suitability,
            "scene_info": scene_info,
            "character_details": character_details
        }
        
        # 调用LLM生成视觉描述和旁白
        visual_data = self._call_llm_with_retry(input_params)
        
        # 转换为VisualNarrative对象
        visual_narrative = self._convert_to_visual_narrative(visual_data, scene)
        
        self.logger.info(f"场景 {scene.scene_id} 视觉叙述生成完成")
        return visual_narrative
    
    def _format_scene_info(self, scene: Scene) -> str:
        """
        格式化场景信息为字符串
        
        Args:
            scene: 场景对象
            
        Returns:
            格式化的场景信息字符串
        """
        info_lines = [
            f"场景描述: {scene.scene_description}",
            f"环境: {scene.environment}",
            f"氛围: {scene.atmosphere}",
            f"时间: {scene.time}",
            f"主要动作: {scene.main_action}",
            f"情绪基调: {scene.emotional_tone}",
            f"转换提示: {scene.transition_cue}"
        ]
        
        # 添加角色信息
        if scene.characters:
            info_lines.append("角色:")
            for char in scene.characters:
                char_info = f"  - {char.name}: {char.appearance}, {char.expression}, {char.action}, {char.emotion}"
                info_lines.append(char_info)
        
        return "\n".join(info_lines)
    
    def _get_character_details(self, scene: Scene) -> str:
        """
        获取场景中角色的详细信息
        
        Args:
            scene: 场景对象
            
        Returns:
            角色详细信息字符串
        """
        if not scene.characters:
            return "无角色信息"
        
        character_names = [char.name for char in scene.characters]
        details = self.character_manager.get_character_details(character_names)
        
        detail_lines = []
        for name, info in details.items():
            detail_lines.append(f"- {name}:")
            detail_lines.append(f"  外貌: {info['appearance']}")
            detail_lines.append(f"  服装: {info['clothing']}")
            detail_lines.append(f"  性格: {info['personality']}")
            detail_lines.append(f"  类型: {info['role_type']}")
        
        return "\n".join(detail_lines)
    
    def _call_llm_with_retry(self, input_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        带重试机制的LLM调用
        
        Args:
            input_params: 输入参数
            
        Returns:
            视觉叙述数据
        """
        last_error = None
        
        for attempt in range(MAX_RETRIES):
            try:
                self.logger.debug(f"LLM调用尝试 {attempt + 1}/{MAX_RETRIES}")
                
                # 记录输入
                if is_show_llm_log:
                    self.file_logger.debug(f"输入参数: {json.dumps(input_params, ensure_ascii=False, indent=2)}")
                
                # 调用链
                start_time = time.time()
                result = self.chain.invoke(input_params)
                end_time = time.time()
                
                # 记录输出
                if is_show_llm_log:
                    self.file_logger.debug(f"LLM响应 (耗时: {end_time - start_time:.2f}秒):\n{json.dumps(result, ensure_ascii=False, indent=2)}")
                
                return result
                
            except Exception as e:
                last_error = e
                self.logger.warning(f"LLM调用失败 (尝试 {attempt + 1}/{MAX_RETRIES}): {e}")
                
                if attempt < MAX_RETRIES - 1:
                    self.logger.info(f"等待 {RETRY_DELAY} 秒后重试...")
                    time.sleep(RETRY_DELAY)
        
        # 所有重试都失败了
        self.logger.error(f"LLM调用最终失败: {last_error}")
        raise Exception(f"视觉叙述生成失败: {last_error}")
    
    def _convert_to_visual_narrative(self, visual_data: Dict[str, Any], scene: Scene) -> VisualNarrative:
        """
        将视觉数据转换为VisualNarrative对象
        
        Args:
            visual_data: 视觉数据
            scene: 原始场景
            
        Returns:
            VisualNarrative对象
        """
        try:
            # 转换构图信息
            composition_data = visual_data.get("composition", {})
            composition = Composition(
                shot_type=composition_data.get("shot_type", "中景"),
                angle=composition_data.get("angle", "平视"),
                layout=composition_data.get("layout", "标准布局"),
                focus=composition_data.get("focus", "角色")
            )
            
            # 转换角色信息
            visual_characters = []
            character_data = visual_data.get("character")
            if character_data:
                character = VisualCharacter(
                    name=character_data.get("name", "未知角色"),
                    position=character_data.get("position", "中心"),
                    pose=character_data.get("pose", "站立"),
                    expression=character_data.get("expression", "平静"),
                    clothing_details=character_data.get("clothing_details", "普通服装"),
                    action=character_data.get("action", "静止")
                )
                visual_characters.append(character)
            
            # 如果没有角色信息，创建一个默认角色
            if not visual_characters and scene.character:
                scene_char = scene.character
                self.logger.warning(f"视觉数据中未包含角色信息，使用场景中的角色: {scene_char.name}")
                default_character = VisualCharacter(
                    name=scene_char.name,
                    position="中心",
                    pose="站立",
                    expression=scene_char.expression,
                    clothing_details="根据场景描述",
                    action=scene_char.action
                )
                visual_characters.append(default_character)
                self.logger.warning(f"视觉数据中未包含角色信息，使用场景中的角色: {scene_char.name}")

            
            # 转换环境信息
            env_data = visual_data.get("environment", {})
            environment = Environment(
                background=env_data.get("background", scene.environment if scene.environment else "简单背景"),
                atmosphere=env_data.get("atmosphere", scene.atmosphere if scene.atmosphere else "平和"),
                lighting=env_data.get("lighting", "自然光"),
                color_scheme=env_data.get("color_scheme", "自然色彩")
            )
            
            # 转换风格信息
            style_data = visual_data.get("style", {})
            style = Style(
                art_style=style_data.get("art_style", "写实风格"),
                quality_tags=style_data.get("quality_tags", "高质量"),
                additional_details=style_data.get("additional_details", "无额外细节")
            )
            
            # 转换旁白信息
            narration_data = visual_data.get("narration", {})
            narration = Narration(
                scene_description=narration_data.get("scene_description", scene.scene_description if scene.scene_description else ""),
                inner_monologue=narration_data.get("inner_monologue", ""),
                emotional_text=narration_data.get("emotional_text", scene.emotional_tone if scene.emotional_tone else ""),
                transition_text=narration_data.get("transition_text", scene.transition_cue if scene.transition_cue else "")
            )
            
            # 创建VisualNarrative对象
            visual_narrative = VisualNarrative(
                visual_description=visual_data.get("visual_description", scene.scene_description if scene.scene_description else "视觉描述"),
                composition=composition,
                characters=visual_characters,
                environment=environment,
                style=style,
                narration=narration,
                scene_id=scene.scene_id
            )
            
            return visual_narrative
            
        except Exception as e:
            self.logger.error(f"转换视觉数据失败: {e}")
            # 返回一个默认的VisualNarrative对象
            return self._create_default_visual_narrative(scene)
    
    def _create_default_visual_narrative(self, scene: Scene) -> VisualNarrative:
        """
        创建默认的视觉叙述对象
        
        Args:
            scene: 场景对象
            
        Returns:
            默认的VisualNarrative对象
        """
        # 创建默认构图
        composition = Composition(
            shot_type="中景",
            angle="平视",
            layout="标准布局",
            focus="角色"
        )
        
        # 创建默认角色
        visual_characters = []
        if scene.character:
            scene_char = scene.character
            default_character = VisualCharacter(
                name=scene_char.name,
                position="中心",
                pose="站立",
                expression=scene_char.expression,
                clothing_details="根据场景描述",
                action=scene_char.action
            )
            visual_characters.append(default_character)
        
        # 创建默认环境
        environment = Environment(
            background=scene.environment if scene.environment else "简单背景",
            atmosphere=scene.atmosphere if scene.atmosphere else "平和",
            lighting="自然光",
            color_scheme="自然色彩"
        )
        
        # 创建默认风格
        style = Style(
            art_style="写实风格",
            quality_tags="高质量",
            additional_details="无额外细节"
        )
        
        # 创建默认旁白
        narration = Narration(
            scene_description=scene.scene_description if scene.scene_description else "",
            inner_monologue="",
            emotional_text=scene.emotional_tone if scene.emotional_tone else "",
            transition_text=scene.transition_cue if scene.transition_cue else ""
        )
        
        # 创建默认VisualNarrative对象
        return VisualNarrative(
            visual_description=scene.scene_description if scene.scene_description else "默认视觉描述",
            composition=composition,
            characters=visual_characters,
            environment=environment,
            style=style,
            narration=narration,
            scene_id=scene.scene_id
        )