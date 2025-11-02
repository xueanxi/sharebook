"""
角色卡片提取Agent
从原文中提取角色的视觉信息和特征
"""

import json
import re
from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage

from .base import BaseCharacterCardAgent, CharacterCardState
from .character_grouping_agent import CharacterGroupingAgent
from src.utils.logging_manager import get_agent_logger



class CharacterExtractionAgent(BaseCharacterCardAgent):
    """角色卡片提取Agent，从原文中提取角色视觉信息"""
    
    def __init__(self, model_name: str = None   , temperature: float = 0.5):
        super().__init__(model_name, temperature)
        self.logger = get_agent_logger(__class__.__name__)



    def extract(self, character_names: List[str], original_text: str, character_info: Dict[str, Any]) -> Dict[str, Any]:
        """提取角色的视觉信息
        
        Args:
            character_names: 角色名称列表
            original_text: 原文文本
            character_info: 角色基本信息
            
        Returns:
            提取的角色卡片信息
        """
        try:
            # 提示词模板
            prompt_template = """
你是一个专业的角色视觉特征提取专家，专门从小说文本中提取角色的视觉信息。

请根据以下角色名称和原文文本，提取每个角色的视觉特征：

角色名称：{character_names}

原文文本：
{original_text}

请为每个角色提取以下信息：
1. 核心视觉特征（外貌、发型、发色、体型等）
2. 服饰装备（衣物、武器、法宝、饰品等）
3. 气质状态（虚弱/强大/愤怒/平静等）
4. 关键变化（变身、突破、获得、受伤等）
5. 原文引用（最直观的1-2句描述）

请以JSON格式返回结果，格式如下：
{{
    "角色名1": {{
        "core_features": ["特征1", "特征2"],
        "clothing": ["服饰1", "服饰2"],
        "key_items": ["物品1", "物品2"],
        "temperament": "气质描述",
        "key_changes": ["变化1", "变化2"],
        "quote": "原文引用...",
        "stage": "当前阶段"
    }},
    "角色名2": {{
        ...
    }}
}}

注意：
- 如果某个角色在文本中没有明显描述，请标注"无明显描述"
- 优先提取视觉相关的描述
- 原文引用要选择最直观的描述句子
- 如果是主角，需要识别当前处于哪个阶段（早期/中期/晚期）
"""
            
            # 创建处理链
            chain = self._create_json_chain(prompt_template)

            
            # 执行提取
            result = chain.invoke({
                "character_names": ", ".join(character_names),
                "original_text": original_text
            })
            self.logger.debug(f"提取角色卡片原始输出: {result[:200]}...")
            
            # 尝试解析JSON结果
            try:
                # 去除前后空白
                result = result.strip()
                
                character_cards = json.loads(result)
                return {
                    "success": True,
                    "character_cards": character_cards,
                    "processed_characters": character_names,
                    "agent": "角色卡片提取Agent"
                }
            except json.JSONDecodeError:
                # 如果JSON解析失败，尝试提取内容
                self.logger.warning(f"JSON解析失败，原始输出: {result[:200]}...")
                # 这里可以添加更智能的解析逻辑
                return {
                    "success": False,
                    "error": "JSON解析失败",
                    "raw_result": result,
                    "agent": "角色卡片提取Agent"
                }
            
        except Exception as e:
            self.logger.error(f"角色卡片提取失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent": "角色卡片提取Agent"
            }
    
    def process(self, state: CharacterCardState) -> CharacterCardState:
        """处理角色卡片提取状态
        
        Args:
            state: 角色卡生成状态
            
        Returns:
            更新后的状态
        """
        try:
            # 获取分组后的角色
            grouped_characters = state.get("grouped_characters", {})
            
            if not grouped_characters:
                state["errors"].append("没有找到分组后的角色信息")
                return state
            
            # 创建处理组
            grouping_agent = CharacterGroupingAgent()
            processing_groups = grouping_agent.create_processing_groups(grouped_characters)
            
            # 初始化临时角色卡片
            temp_cards = {}
            
            # 处理每个组
            for group in processing_groups:
                # 提取角色名称
                character_names = group
                
                # 执行角色卡片提取
                result = self.extract(
                    character_names,
                    state["original_text"],
                    state["character_info"]
                )
                
                if result["success"]:
                    # 合并到临时卡片
                    temp_cards.update(result["character_cards"])
                    state["completed_tasks"].append(f"提取角色卡片: {', '.join(character_names)}")
                else:
                    # 记录错误
                    state["errors"].append(f"提取角色卡片失败 {', '.join(character_names)}: {result['error']}")
            
            # 更新状态
            state["temp_cards"] = temp_cards
            state["extraction_done"] = True
            
            self.logger.info(f"角色卡片提取完成，共处理 {len(temp_cards)} 个角色")
            
            return state
            
        except Exception as e:
            error_msg = f"角色卡片提取处理异常: {str(e)}"
            state["errors"].append(error_msg)
            self.logger.error(error_msg)
            return state
    
    def identify_character_stage(self, character_name: str, character_info: Dict[str, Any], 
                                original_text: str) -> str:
        """识别角色当前所处的阶段
        
        Args:
            character_name: 角色名称
            character_info: 角色基本信息
            original_text: 原文文本
            
        Returns:
            阶段标识（early/middle/late）
        """
        # 获取角色出现章节
        chapters = character_info.get("chapters", [])
        
        if not chapters:
            return "unknown"
        
        # 简单的章节范围判断
        # 这里可以根据实际需求调整
        if isinstance(chapters, list):
            if max(chapters) <= 15:
                return "early"
            elif max(chapters) <= 35:
                return "middle"
            else:
                return "late"
        else:
            # 如果是字符串或其他格式，返回未知
            return "unknown"
    
    def detect_major_changes(self, character_name: str, original_text: str) -> List[str]:
        """检测角色的重大变化
        
        Args:
            character_name: 角色名称
            original_text: 原文文本
            
        Returns:
            重大变化列表
        """
        # 定义重大变化关键词
        major_change_keywords = {
            "实力突破": ["突破", "晋级", "飞升", "升级", "提升", "进阶"],
            "外貌变化": ["变身", "恢复", "重伤", "衰老", "年轻", "变化"],
            "装备获得": ["获得", "得到", "装备", "法宝", "武器", "神器"]
        }
        
        changes = []
        
        # 在文本中查找角色相关的重大变化
        # 这里可以添加更复杂的逻辑
        for change_type, keywords in major_change_keywords.items():
            for keyword in keywords:
                # 查找包含角色名和关键词的句子
                pattern = f".{keyword}.*{character_name}|{character_name}.*{keyword}."
                matches = re.findall(pattern, original_text)
                if matches:
                    changes.append(change_type)
                    break
        
        return changes