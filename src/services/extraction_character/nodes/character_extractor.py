"""
角色提取节点
"""

from typing import Dict, Any, List
from state import CharacterExtractionState
from utils.llm_utils import LLMUtils


class CharacterExtractor:
    """角色提取节点"""
    
    def __init__(self, llm_config_path: str = "config/llm_config.py"):
        """
        初始化角色提取节点
        
        Args:
            llm_config_path: LLM配置文件路径
        """
        self.llm_utils = LLMUtils(llm_config_path)
    
    def extract_characters(self, state: CharacterExtractionState) -> CharacterExtractionState:
        """
        从章节内容中提取角色
        
        Args:
            state: 当前状态
            
        Returns:
            更新后的状态
        """
        try:
            chapter_content = state.get("chapter_content", "")
            
            if not chapter_content:
                state["error"] = "章节内容为空，无法提取角色"
                return state
            
            # 使用LLM提取角色
            extracted_characters = self.llm_utils.extract_characters(chapter_content)
            
            # 更新状态
            state["extracted_characters"] = extracted_characters
            state["error"] = None
            
            return state
        except Exception as e:
            state["error"] = f"角色提取失败: {str(e)}"
            state["extracted_characters"] = []
            return state
    
    def validate_extracted_characters(self, state: CharacterExtractionState) -> bool:
        """
        验证提取的角色是否有效
        
        Args:
            state: 当前状态
            
        Returns:
            角色是否有效
        """
        extracted_characters = state.get("extracted_characters", [])
        
        # 检查是否为列表
        if not isinstance(extracted_characters, list):
            return False
        
        # 检查每个角色是否有姓名
        for character in extracted_characters:
            if not isinstance(character, dict):
                return False
            
            name = character.get("name", "")
            if not name or not isinstance(name, str):
                return False
        
        return True
    
    def preprocess_characters(self, state: CharacterExtractionState) -> CharacterExtractionState:
        """
        预处理提取的角色信息
        
        Args:
            state: 当前状态
            
        Returns:
            更新后的状态
        """
        try:
            extracted_characters = state.get("extracted_characters", [])
            processed_characters = []
            
            for character in extracted_characters:
                # 确保有姓名
                name = character.get("name", "").strip()
                if not name:
                    continue
                
                # 处理别名
                aliases = character.get("aliases", [])
                if isinstance(aliases, str):
                    # 如果别名是字符串，尝试分割
                    aliases = [alias.strip() for alias in aliases.split(",") if alias.strip()]
                elif isinstance(aliases, list):
                    # 确保别名是字符串列表
                    aliases = [str(alias).strip() for alias in aliases if str(alias).strip()]
                else:
                    aliases = []
                
                # 去除重复的别名
                aliases = list(set(aliases))
                
                # 创建处理后的角色信息
                processed_character = {
                    "name": name,
                    "aliases": aliases
                }
                
                processed_characters.append(processed_character)
            
            # 更新状态
            state["extracted_characters"] = processed_characters
            state["error"] = None
            
            return state
        except Exception as e:
            state["error"] = f"角色预处理失败: {str(e)}"
            state["extracted_characters"] = []
            return state