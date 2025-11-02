"""
角色信息合并Agent
合并新旧角色信息，判断是否需要新增阶段
"""

import json
from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage

from .base import BaseCharacterCardAgent, CharacterCardState
from src.utils.logging_manager import get_agent_logger

logger = get_agent_logger(__class__.__name__)


class CharacterMergeAgent(BaseCharacterCardAgent):
    """角色信息合并Agent，判断是否需要新增阶段"""
    
    def __init__(self, model_name: str = None, temperature: float = 0.3):
        super().__init__(model_name, temperature)
    
    def extract(self, temp_cards: Dict[str, Any], existing_cards: Dict[str, Any]) -> Dict[str, Any]:
        """合并角色信息，判断是否需要新增阶段
        
        Args:
            temp_cards: 临时角色卡片（当前提取的信息）
            existing_cards: 已存在的角色卡片
            
        Returns:
            合并结果
        """
        try:
            merged_cards = {}
            new_characters = []
            updated_characters = []
            
            # 处理每个临时角色卡片
            for character_name, temp_card in temp_cards.items():
                if character_name in existing_cards:
                    # 角色已存在，判断是否需要新增阶段
                    existing_card = existing_cards[character_name]
                    merge_result = self._merge_character_info(character_name, temp_card, existing_card)
                    
                    merged_cards[character_name] = merge_result["merged_card"]
                    if merge_result["needs_new_stage"]:
                        updated_characters.append(f"{character_name}(新增阶段)")
                    else:
                        updated_characters.append(character_name)
                else:
                    # 新角色，直接添加
                    merged_cards[character_name] = self._format_new_character_card(character_name, temp_card)
                    new_characters.append(character_name)
            
            return {
                "success": True,
                "merged_cards": merged_cards,
                "new_characters": new_characters,
                "updated_characters": updated_characters,
                "agent": "角色信息合并Agent"
            }
            
        except Exception as e:
            logger.error(f"角色信息合并失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "agent": "角色信息合并Agent"
            }
    
    def process(self, state: CharacterCardState) -> CharacterCardState:
        """处理角色信息合并状态
        
        Args:
            state: 角色卡生成状态
            
        Returns:
            更新后的状态
        """
        try:
            # 获取临时角色卡片和已存在的角色卡片
            temp_cards = state.get("temp_cards", {})
            existing_cards = state.get("existing_cards", {})
            
            if not temp_cards:
                state["errors"].append("没有找到临时角色卡片信息")
                return state
            
            # 执行角色信息合并
            result = self.extract(temp_cards, existing_cards)
            
            if result["success"]:
                # 更新状态
                state["final_cards"] = result["merged_cards"]
                state["merging_done"] = True
                state["completed_tasks"].append("角色信息合并")
                
                logger.info(f"角色信息合并完成: 新增角色 {len(result['new_characters'])} 个, "
                           f"更新角色 {len(result['updated_characters'])} 个")
            else:
                # 记录错误
                state["errors"].append(f"角色信息合并失败: {result['error']}")
                logger.error(f"角色信息合并失败: {result['error']}")
            
            return state
            
        except Exception as e:
            error_msg = f"角色信息合并处理异常: {str(e)}"
            state["errors"].append(error_msg)
            logger.error(error_msg)
            return state
    
    def _merge_character_info(self, character_name: str, temp_card: Dict[str, Any], 
                             existing_card: Dict[str, Any]) -> Dict[str, Any]:
        """合并单个角色信息
        
        Args:
            character_name: 角色名称
            temp_card: 临时角色卡片
            existing_card: 已存在的角色卡片
            
        Returns:
            合并结果
        """
        # 判断是否需要新增阶段
        needs_new_stage = self._needs_new_stage(temp_card, existing_card)
        
        if needs_new_stage:
            # 新增阶段
            merged_card = self._add_new_stage(existing_card, temp_card)
        else:
            # 更新现有阶段
            merged_card = self._update_existing_stage(existing_card, temp_card)
        
        return {
            "merged_card": merged_card,
            "needs_new_stage": needs_new_stage
        }
    
    def _needs_new_stage(self, temp_card: Dict[str, Any], existing_card: Dict[str, Any]) -> bool:
        """判断是否需要新增阶段
        
        Args:
            temp_card: 临时角色卡片
            existing_card: 已存在的角色卡片
            
        Returns:
            是否需要新增阶段
        """
        # 检查是否有重大变化
        key_changes = temp_card.get("key_changes", [])
        
        # 如果有重大变化关键词，可能需要新增阶段
        major_change_keywords = ["突破", "晋级", "飞升", "变身", "恢复", "重伤"]
        
        for change in key_changes:
            for keyword in major_change_keywords:
                if keyword in change:
                    return True
        
        # 检查视觉特征是否有显著变化
        temp_features = set(temp_card.get("core_features", []))
        
        # 如果有existing_card，检查是否有新的视觉特征
        if "visual_timeline" in existing_card:
            # 获取所有已有阶段的特征
            existing_features = set()
            for stage_data in existing_card["visual_timeline"].values():
                existing_features.update(stage_data.get("core_features", []))
            
            # 如果有超过50%的新特征，可能需要新增阶段
            new_features = temp_features - existing_features
            if len(new_features) > len(temp_features) * 0.5:
                return True
        
        return False
    
    def _add_new_stage(self, existing_card: Dict[str, Any], temp_card: Dict[str, Any]) -> Dict[str, Any]:
        """为角色添加新阶段
        
        Args:
            existing_card: 已存在的角色卡片
            temp_card: 临时角色卡片
            
        Returns:
            更新后的角色卡片
        """
        merged_card = existing_card.copy()
        
        # 确定新阶段名称
        current_stages = list(merged_card.get("visual_timeline", {}).keys())
        new_stage_name = self._generate_stage_name(current_stages)
        
        # 添加新阶段
        if "visual_timeline" not in merged_card:
            merged_card["visual_timeline"] = {}
        
        merged_card["visual_timeline"][new_stage_name] = {
            "core_features": temp_card.get("core_features", []),
            "clothing": temp_card.get("clothing", []),
            "key_items": temp_card.get("key_items", []),
            "quote": temp_card.get("quote", ""),
            "key_changes": temp_card.get("key_changes", []),
            "chapters": temp_card.get("chapters", "")
        }
        
        # 更新基础特征
        if "base_features" not in merged_card:
            merged_card["base_features"] = []
        
        # 合并新的基础特征
        new_base_features = temp_card.get("core_features", [])
        for feature in new_base_features:
            if feature not in merged_card["base_features"]:
                merged_card["base_features"].append(feature)
        
        return merged_card
    
    def _update_existing_stage(self, existing_card: Dict[str, Any], temp_card: Dict[str, Any]) -> Dict[str, Any]:
        """更新现有阶段
        
        Args:
            existing_card: 已存在的角色卡片
            temp_card: 临时角色卡片
            
        Returns:
            更新后的角色卡片
        """
        merged_card = existing_card.copy()
        
        # 找到最相似的阶段进行更新
        if "visual_timeline" in merged_card and merged_card["visual_timeline"]:
            # 简单策略：更新最后一个阶段
            last_stage = list(merged_card["visual_timeline"].keys())[-1]
            
            # 合并特征，避免重复
            existing_features = set(merged_card["visual_timeline"][last_stage].get("core_features", []))
            new_features = temp_card.get("core_features", [])
            
            # 添加新特征
            for feature in new_features:
                if feature not in existing_features:
                    merged_card["visual_timeline"][last_stage]["core_features"].append(feature)
            
            # 更新其他信息
            if temp_card.get("clothing"):
                existing_clothing = set(merged_card["visual_timeline"][last_stage].get("clothing", []))
                for clothing in temp_card["clothing"]:
                    if clothing not in existing_clothing:
                        merged_card["visual_timeline"][last_stage]["clothing"].append(clothing)
            
            if temp_card.get("key_items"):
                existing_items = set(merged_card["visual_timeline"][last_stage].get("key_items", []))
                for item in temp_card["key_items"]:
                    if item not in existing_items:
                        merged_card["visual_timeline"][last_stage]["key_items"].append(item)
        
        return merged_card
    
    def _format_new_character_card(self, character_name: str, temp_card: Dict[str, Any]) -> Dict[str, Any]:
        """格式化新角色卡片
        
        Args:
            character_name: 角色名称
            temp_card: 临时角色卡片
            
        Returns:
            格式化的角色卡片
        """
        # 确定角色重要性
        importance = "minor"  # 默认为普通配角
        
        # 根据特征数量判断重要性
        feature_count = len(temp_card.get("core_features", []))
        if feature_count >= 5:
            importance = "main"
        elif feature_count >= 3:
            importance = "support"
        
        # 创建新角色卡片
        character_card = {
            "name": character_name,
            "importance": importance,
            "visual_timeline": {
                "current": {
                    "chapters": temp_card.get("chapters", ""),
                    "core_features": temp_card.get("core_features", []),
                    "clothing": temp_card.get("clothing", []),
                    "key_items": temp_card.get("key_items", []),
                    "quote": temp_card.get("quote", ""),
                    "key_changes": temp_card.get("key_changes", [])
                }
            },
            "base_features": temp_card.get("core_features", []),
            "changes": temp_card.get("key_changes", [])
        }
        
        return character_card
    
    def _generate_stage_name(self, existing_stages: List[str]) -> str:
        """生成新阶段名称
        
        Args:
            existing_stages: 已存在的阶段列表
            
        Returns:
            新阶段名称
        """
        # 预定义的阶段名称
        stage_names = ["early", "middle", "late"]
        
        # 找到下一个可用的阶段名称
        for stage_name in stage_names:
            if stage_name not in existing_stages:
                return stage_name
        
        # 如果预定义名称都用完了，生成数字后缀
        i = 1
        while True:
            new_stage = f"stage_{i}"
            if new_stage not in existing_stages:
                return new_stage
            i += 1