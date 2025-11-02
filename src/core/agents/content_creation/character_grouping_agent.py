"""
角色分组Agent
根据角色重要性进行分组处理
"""

import json
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage

from .base import BaseCharacterCardAgent, CharacterCardState
from src.utils.logging_manager import get_agent_logger

logger = get_agent_logger(__name__)


class CharacterGroupingAgent(BaseCharacterCardAgent):
    """角色分组Agent，根据角色重要性进行分组"""
    
    def __init__(self, model_name: str = None, temperature: float = 0.3):
        super().__init__(model_name, temperature)
    
    def extract(self, character_info: Dict[str, Any]) -> Dict[str, Any]:
        """根据角色重要性进行分组

        Args:
            character_info: 角色信息字典，包含角色列表和重要性标记
            
        Returns:
            分组结果
        """
        try:
            # 提取角色列表，处理嵌套结构
            characters = {}
            
            # 检查是否是嵌套结构
            if "characters" in character_info and isinstance(character_info["characters"], dict):
                if "result" in character_info["characters"] and "characters" in character_info["characters"]["result"]:
                    # 嵌套结构: characters.result.characters
                    raw_characters = character_info["characters"]["result"]["characters"]
                    # 转换为字典格式，以角色名为键
                    for char in raw_characters:
                        if isinstance(char, dict) and "name" in char:
                            characters[char["name"]] = char
                else:
                    # 直接结构: characters
                    characters = character_info["characters"]
            else:
                # 其他情况，尝试直接使用
                characters = character_info.get("characters", {})
            
            # 初始化分组
            grouped_characters = {
                "main": [],      # 主角
                "support": [],   # 重要配角
                "minor": [],     # 普通配角
                "extra": []      # 龙套角色
            }
            
            # 遍历所有角色，按重要性分组
            for character_name, character_data in characters.items():
                role = character_data.get("role", "配角").lower()
                
                # 标准化角色类型
                if role in ["主角", "main", "男主", "女主"]:
                    grouped_characters["main"].append(character_name)
                elif role in ["重要配角", "重要", "support", "主要配角"]:
                    grouped_characters["support"].append(character_name)
                elif role in ["配角", "普通配角", "minor", "次要"]:
                    grouped_characters["minor"].append(character_name)
                else:
                    # 默认为龙套角色
                    grouped_characters["extra"].append(character_name)
            
            return {
                "success": True,
                "grouped_characters": grouped_characters,
                "character_count": len(characters),
                "agent": "角色分组Agent"
            }
            
        except Exception as e:
            logger.error(f"角色分组失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "agent": "角色分组Agent"
            }
    
    def process(self, state: CharacterCardState) -> CharacterCardState:
        """处理角色分组状态
        
        Args:
            state: 角色卡生成状态
            
        Returns:
            更新后的状态
        """
        try:
            # 执行角色分组
            result = self.extract(state["character_info"])
            
            if result["success"]:
                # 更新状态
                state["grouped_characters"] = result["grouped_characters"]
                state["grouping_done"] = True
                state["completed_tasks"].append("角色分组")
                
                logger.info(f"角色分组完成: 主角{len(result['grouped_characters']['main'])}人, "
                           f"重要配角{len(result['grouped_characters']['support'])}人, "
                           f"普通配角{len(result['grouped_characters']['minor'])}人, "
                           f"龙套角色{len(result['grouped_characters']['extra'])}人")
            else:
                # 记录错误
                state["errors"].append(f"角色分组失败: {result['error']}")
                logger.error(f"角色分组失败: {result['error']}")
            
            return state
            
        except Exception as e:
            error_msg = f"角色分组处理异常: {str(e)}"
            state["errors"].append(error_msg)
            logger.error(error_msg)
            return state
    
    def create_processing_groups(self, grouped_characters: Dict[str, List]) -> List[List[str]]:
        """创建实际的处理组
        
        Args:
            grouped_characters: 分组后的角色字典
            
        Returns:
            处理组列表，每个组包含2-3个角色
        """
        processing_groups = []
        
        # 主角单独处理
        if grouped_characters.get("main"):
            for character in grouped_characters["main"]:
                processing_groups.append([character])
        
        # 重要配角每2-3个一组
        if grouped_characters.get("support"):
            support_chars = grouped_characters["support"]
            for i in range(0, len(support_chars), 2):
                group = support_chars[i:i+3]  # 最多3个一组
                if group:
                    processing_groups.append(group)
        
        # 普通配角每3-4个一组
        if grouped_characters.get("minor"):
            minor_chars = grouped_characters["minor"]
            for i in range(0, len(minor_chars), 3):
                group = minor_chars[i:i+4]  # 最多4个一组
                if group:
                    processing_groups.append(group)
        
        # 龙套角色批量处理
        if grouped_characters.get("extra"):
            extra_chars = grouped_characters["extra"]
            # 龙套角色可以更多一组，比如5-8个
            for i in range(0, len(extra_chars), 5):
                group = extra_chars[i:i+8]  # 最多8个一组
                if group:
                    processing_groups.append(group)
        
        return processing_groups