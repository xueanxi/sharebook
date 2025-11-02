"""
角色卡片更新Agent
最终更新角色卡片，确保时间线连贯性
"""

import json
from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage

from .base import BaseCharacterCardAgent, CharacterCardState
from src.utils.logging_manager import get_agent_logger

class CharacterUpdateAgent(BaseCharacterCardAgent):
    """角色卡片更新Agent，确保时间线连贯性"""
    
    def __init__(self, model_name: str = None, temperature: float = 0.2):
        super().__init__(model_name, temperature)
        self.logger = get_agent_logger(__class__.__name__)
    
    def extract(self, final_cards: Dict[str, Any]) -> Dict[str, Any]:
        """最终更新角色卡片，确保时间线连贯性
        
        Args:
            final_cards: 合并后的角色卡片
            
        Returns:
            更新后的角色卡片
        """
        try:
            updated_cards = {}
            
            # 处理每个角色卡片
            for character_name, card in final_cards.items():
                updated_card = self._update_character_card(character_name, card)
                updated_cards[character_name] = updated_card
            
            return {
                "success": True,
                "updated_cards": updated_cards,
                "total_characters": len(updated_cards),
                "agent": "角色卡片更新Agent"
            }
            
        except Exception as e:
            self.logger.error(f"角色卡片更新失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "agent": "角色卡片更新Agent"
            }
    
    def process(self, state: CharacterCardState) -> CharacterCardState:
        """处理角色卡片更新状态
        
        Args:
            state: 角色卡生成状态
            
        Returns:
            更新后的状态
        """
        try:
            # 获取最终角色卡片
            final_cards = state.get("final_cards", {})
            
            if not final_cards:
                state["errors"].append("没有找到最终角色卡片信息")
                return state
            
            # 执行角色卡片更新
            result = self.extract(final_cards)
            
            if result["success"]:
                # 更新状态
                state["final_cards"] = result["updated_cards"]
                state["updating_done"] = True
                state["completed_tasks"].append("角色卡片更新")
                
                self.logger.info(f"角色卡片更新完成，共更新 {result['total_characters']} 个角色")
            else:
                # 记录错误
                state["errors"].append(f"角色卡片更新失败: {result['error']}")
                self.logger.error(f"角色卡片更新失败: {result['error']}")
            
            return state
            
        except Exception as e:
            error_msg = f"角色卡片更新处理异常: {str(e)}"
            state["errors"].append(error_msg)
            self.logger.error(error_msg)
            return state
    
    def _update_character_card(self, character_name: str, card: Dict[str, Any]) -> Dict[str, Any]:
        """更新单个角色卡片
        
        Args:
            character_name: 角色名称
            card: 角色卡片
            
        Returns:
            更新后的角色卡片
        """
        updated_card = card.copy()
        
        # 确保时间线连贯性
        if "visual_timeline" in updated_card:
            updated_card["visual_timeline"] = self._ensure_timeline_coherence(
                updated_card["visual_timeline"]
            )
        
        # 更新基础特征
        updated_card["base_features"] = self._update_base_features(updated_card)
        
        # 更新变化列表
        updated_card["changes"] = self._update_changes(updated_card)
        
        # 添加元数据
        updated_card["last_updated"] = self._get_current_timestamp()
        
        return updated_card
    
    def _ensure_timeline_coherence(self, visual_timeline: Dict[str, Any]) -> Dict[str, Any]:
        """确保时间线连贯性
        
        Args:
            visual_timeline: 视觉时间线
            
        Returns:
            更新后的视觉时间线
        """
        # 按阶段名称排序
        stage_order = ["early", "middle", "late"]
        
        # 分离已知和未知阶段
        known_stages = {}
        unknown_stages = {}
        
        for stage_name, stage_data in visual_timeline.items():
            if stage_name in stage_order:
                known_stages[stage_name] = stage_data
            else:
                unknown_stages[stage_name] = stage_data
        
        # 按已知顺序排列
        sorted_timeline = {}
        for stage_name in stage_order:
            if stage_name in known_stages:
                sorted_timeline[stage_name] = known_stages[stage_name]
        
        # 添加未知阶段
        for stage_name, stage_data in unknown_stages.items():
            sorted_timeline[stage_name] = stage_data
        
        # 确保每个阶段都有必要的字段
        for stage_name, stage_data in sorted_timeline.items():
            sorted_timeline[stage_name] = self._ensure_stage_completeness(stage_data)
        
        return sorted_timeline
    
    def _ensure_stage_completeness(self, stage_data: Dict[str, Any]) -> Dict[str, Any]:
        """确保阶段数据完整性
        
        Args:
            stage_data: 阶段数据
            
        Returns:
            完整的阶段数据
        """
        # 确保必要字段存在
        required_fields = [
            "core_features", "clothing", "key_items", "quote", "key_changes"
        ]
        
        for field in required_fields:
            if field not in stage_data:
                stage_data[field] = []
        
        return stage_data
    
    def _update_base_features(self, card: Dict[str, Any]) -> List[str]:
        """更新基础特征
        
        Args:
            card: 角色卡片
            
        Returns:
            更新后的基础特征列表
        """
        base_features = set()
        
        # 从所有阶段收集基础特征
        if "visual_timeline" in card:
            for stage_data in card["visual_timeline"].values():
                stage_features = stage_data.get("core_features", [])
                base_features.update(stage_features)
        
        # 如果已有基础特征，合并
        if "base_features" in card:
            base_features.update(card["base_features"])
        
        return list(base_features)
    
    def _update_changes(self, card: Dict[str, Any]) -> List[str]:
        """更新变化列表
        
        Args:
            card: 角色卡片
            
        Returns:
            更新后的变化列表
        """
        changes = set()
        
        # 从所有阶段收集变化
        if "visual_timeline" in card:
            for stage_data in card["visual_timeline"].values():
                stage_changes = stage_data.get("key_changes", [])
                changes.update(stage_changes)
        
        # 如果已有变化列表，合并
        if "changes" in card:
            changes.update(card["changes"])
        
        return list(changes)
    
    def _get_current_timestamp(self) -> str:
        """获取当前时间戳
        
        Returns:
            当前时间戳字符串
        """
        import datetime
        return datetime.datetime.now().isoformat()
    
    def validate_character_card(self, card: Dict[str, Any]) -> Dict[str, Any]:
        """验证角色卡片的完整性
        
        Args:
            card: 角色卡片
            
        Returns:
            验证结果
        """
        errors = []
        warnings = []
        
        # 检查必要字段
        required_fields = ["name", "importance", "visual_timeline", "base_features"]
        for field in required_fields:
            if field not in card:
                errors.append(f"缺少必要字段: {field}")
        
        # 检查视觉时间线
        if "visual_timeline" in card:
            if not card["visual_timeline"]:
                errors.append("视觉时间线为空")
            else:
                for stage_name, stage_data in card["visual_timeline"].items():
                    if not isinstance(stage_data, dict):
                        errors.append(f"阶段 {stage_name} 数据格式错误")
                        continue
                    
                    stage_fields = ["core_features", "clothing", "key_items", "quote", "key_changes"]
                    for field in stage_fields:
                        if field not in stage_data:
                            warnings.append(f"阶段 {stage_name} 缺少字段: {field}")
        
        # 检查基础特征
        if "base_features" in card:
            if not card["base_features"]:
                warnings.append("基础特征列表为空")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }