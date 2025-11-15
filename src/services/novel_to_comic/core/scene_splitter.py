"""
场景分割Agent
"""

import json
import uuid
import time
from typing import List, Dict, Any, Optional

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI

from src.services.novel_to_comic.config.prompts import SCENE_SPLITTER_PROMPT
from src.services.novel_to_comic.config.processing_config import SCENE_SPLITTER_CONFIG, MAX_RETRIES, RETRY_DELAY
from src.services.novel_to_comic.models.data_models import TextSegment, Scene, SceneCharacter
from src.services.novel_to_comic.utils.character_manager import CharacterManager
from src.utils.logging_manager import get_logger, LogCategory, get_agent_file_logger
from config.llm_config import LLMConfig

logger = get_logger(__name__, LogCategory.AGENT)


class SceneSplitterAgent:
    """场景分割Agent"""
    
    def __init__(self, character_manager: CharacterManager):
        self.character_manager = character_manager
        self.logger = logger
        self.file_logger = get_agent_file_logger(self.__class__.__name__)
        
        # 初始化LLM
        self.llm_kwargs = LLMConfig.get_openai_kwargs()
        self.llm_kwargs.update(SCENE_SPLITTER_CONFIG)
        self.llm = ChatOpenAI(**self.llm_kwargs)
        
        # 创建提示模板
        self.prompt_template = ChatPromptTemplate.from_template(SCENE_SPLITTER_PROMPT)
        
        # 创建输出解析器
        self.output_parser = JsonOutputParser()
        
        # 创建处理链
        self.chain = self.prompt_template | self.llm | self.output_parser
    
    def split_segment_to_scenes(self, segment: TextSegment, context: Dict[str, Any]) -> List[Scene]:
        """
        将段落分割为场景
        
        Args:
            segment: 文本段落
            context: 上下文信息
            
        Returns:
            场景列表
        """
        self.logger.info(f"开始处理段落: {segment.segment_id}")
        
        # 准备角色信息
        character_info = self.character_manager.format_character_info(
            segment.metadata.character_mentions
        )
        
        # 准备输入参数
        input_params = {
            "novel_type": context.get("novel_type", "未知"),
            "chapter_title": context.get("chapter_title", "未知章节"),
            "previous_scene_summary": context.get("previous_scene_summary", "无"),
            "character_info": character_info,
            "segment_text": segment.text
        }
        
        # 调用LLM进行场景分析
        scenes_data = self._call_llm_with_retry(input_params)
        
        # 转换为Scene对象
        result_scenes = []
        for i, scene_data in enumerate(scenes_data):
            scene = self._convert_to_scene(scene_data, segment, i)
            result_scenes.append(scene)
        
        self.logger.info(f"段落 {segment.segment_id} 分割完成，共生成 {len(result_scenes)} 个场景")
        return result_scenes
    
    def _call_llm_with_retry(self, input_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        带重试机制的LLM调用
        
        Args:
            input_params: 输入参数
            
        Returns:
            场景数据列表
        """
        last_error = None
        
        for attempt in range(MAX_RETRIES):
            try:
                self.logger.debug(f"LLM调用尝试 {attempt + 1}/{MAX_RETRIES}")
                
                # 记录输入
                self.file_logger.info(f"输入参数: {json.dumps(input_params, ensure_ascii=False, indent=2)}")
                
                # 调用链
                start_time = time.time()
                result = self.chain.invoke(input_params)
                end_time = time.time()
                
                # 记录输出
                self.file_logger.info(f"LLM响应 (耗时: {end_time - start_time:.2f}秒):\n{json.dumps(result, ensure_ascii=False, indent=2)}")
                
                # 提取场景数据
                if "scenes" in result:
                    return result["scenes"]
                else:
                    self.logger.warning("LLM响应中未找到scenes字段，尝试手动解析")
                    return self._manual_parse(result)
                
            except Exception as e:
                last_error = e
                self.logger.warning(f"LLM调用失败 (尝试 {attempt + 1}/{MAX_RETRIES}): {e}")
                
                if attempt < MAX_RETRIES - 1:
                    self.logger.info(f"等待 {RETRY_DELAY} 秒后重试...")
                    time.sleep(RETRY_DELAY)
        
        # 所有重试都失败了
        self.logger.error(f"LLM调用最终失败: {last_error}")
        raise Exception(f"场景分割失败: {last_error}")
    
    def _manual_parse(self, result: Any) -> List[Dict[str, Any]]:
        """
        手动解析LLM输出
        
        Args:
            result: LLM输出结果
            
        Returns:
            场景数据列表
        """
        self.logger.warning("使用手动解析模式")
        
        # 创建默认场景
        default_scene = {
            "scene_id": str(uuid.uuid4()),
            "scene_description": "无法解析的场景描述",
            "environment": "未知环境",
            "atmosphere": "未知氛围",
            "time": "未知时间",
            "characters": [],
            "main_action": "未知动作",
            "emotional_tone": "未知情绪",
            "importance_score": 5,
            "visual_suitability": 5,
            "transition_cue": "无转换提示"
        }
        
        return [default_scene]
    
    def _convert_to_scene(self, scene_data: Dict[str, Any], segment: TextSegment, scene_index: int) -> Scene:
        """
        将场景数据转换为Scene对象
        
        Args:
            scene_data: 场景数据
            segment: 原始段落
            scene_index: 场景在段落中的索引
            
        Returns:
            Scene对象
        """
        # 转换角色数据
        scene_characters = []
        for char_data in scene_data.get("characters", []):
            character = SceneCharacter(
                name=char_data.get("name", "未知角色"),
                appearance=char_data.get("appearance", "未知外观"),
                expression=char_data.get("expression", "未知表情"),
                action=char_data.get("action", "未知动作"),
                emotion=char_data.get("emotion", "未知情绪")
            )
            scene_characters.append(character)
        
        # 创建Scene对象
        scene = Scene(
            scene_id=scene_data.get("scene_id", str(uuid.uuid4())),
            scene_description=scene_data.get("scene_description", "未知场景描述"),
            environment=scene_data.get("environment", "未知环境"),
            atmosphere=scene_data.get("atmosphere", "未知氛围"),
            time=scene_data.get("time", "未知时间"),
            characters=scene_characters,
            main_action=scene_data.get("main_action", "未知动作"),
            emotional_tone=scene_data.get("emotional_tone", "未知情绪"),
            importance_score=scene_data.get("importance_score", 5),
            visual_suitability=scene_data.get("visual_suitability", 5),
            transition_cue=scene_data.get("transition_cue", "无转换提示"),
            segment_index=segment.segment_index,
            scene_index_in_segment=scene_index
        )
        
        return scene