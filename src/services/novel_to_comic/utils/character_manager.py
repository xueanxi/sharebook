"""
角色数据管理工具
"""

import os
from typing import List, Dict, Optional

from src.services.novel_to_comic.models.data_models import CharacterInfo
from src.services.novel_to_comic.utils.file_handler import FileHandler
from src.utils.logging_manager import get_module_logger, LogModule

logger = get_module_logger(LogModule.NOVEL_TO_COMIC)


class CharacterManager:
    """角色数据管理器"""
    
    def __init__(self, character_csv_path: str = "data/characters/characters.csv"):
        self.character_csv_path = character_csv_path
        self.file_handler = FileHandler()
        self.logger = logger
        self._characters: Dict[str, CharacterInfo] = {}
        self._load_characters()
    
    def _load_characters(self) -> None:
        """加载角色数据"""
        try:
            if os.path.exists(self.character_csv_path):
                csv_data = self.file_handler.read_csv_file(self.character_csv_path)
                for row in csv_data:
                    character = self._parse_character_row(row)
                    if character:
                        self._characters[character.name] = character
                
                self.logger.info(f"成功加载 {len(self._characters)} 个角色数据")
            else:
                self.logger.warning(f"角色数据文件不存在: {self.character_csv_path}")
        except Exception as e:
            self.logger.error(f"加载角色数据失败: {e}")
    
    def _parse_character_row(self, row: Dict[str, str]) -> Optional[CharacterInfo]:
        """
        解析CSV行数据为角色对象
        
        Args:
            row: CSV行数据
            
        Returns:
            角色信息对象或None
        """
        try:
            name = row.get("姓名", "").strip()
            if not name:
                return None
            
            # 处理别名
            aliases_str = row.get("别名", "").strip()
            aliases = [alias.strip() for alias in aliases_str.split(",") if alias.strip()] if aliases_str else []
            
            return CharacterInfo(
                name=name,
                aliases=aliases,
                gender=row.get("性别", "").strip() or None,
                appearance=row.get("外貌特征", "").strip() or None,
                clothing=row.get("服装特点", "").strip() or None,
                personality=row.get("性格特点", "").strip() or None,
                role_type=row.get("角色类型", "").strip() or None
            )
        except Exception as e:
            self.logger.error(f"解析角色数据失败: {row}, 错误: {e}")
            return None
    
    def get_character_by_name(self, name: str) -> Optional[CharacterInfo]:
        """
        根据名称获取角色信息
        
        Args:
            name: 角色名称
            
        Returns:
            角色信息对象或None
        """
        return self._characters.get(name)
    
    def find_character_by_alias(self, alias: str) -> Optional[CharacterInfo]:
        """
        根据别名查找角色
        
        Args:
            alias: 角色别名
            
        Returns:
            角色信息对象或None
        """
        for character in self._characters.values():
            if alias in character.aliases:
                return character
        return None
    
    def get_all_character_names(self) -> List[str]:
        """
        获取所有角色名称
        
        Returns:
            角色名称列表
        """
        return list(self._characters.keys())
    
    def get_character_info_for_text(self, text: str) -> List[CharacterInfo]:
        """
        获取文本中提及的角色信息
        
        Args:
            text: 输入文本
            
        Returns:
            文本中提及的角色信息列表
        """
        mentioned_characters = []
        
        for character in self._characters.values():
            # 检查本名
            if character.name in text:
                mentioned_characters.append(character)
                continue
            
            # 检查别名
            for alias in character.aliases:
                if alias in text:
                    mentioned_characters.append(character)
                    break
        
        return mentioned_characters
    
    def format_character_info(self, character_names: List[str]) -> str:
        """
        格式化角色信息为字符串
        
        Args:
            character_names: 角色名称列表
            
        Returns:
            格式化的角色信息字符串
        """
        if not character_names:
            return "无相关角色信息"
        
        info_parts = []
        for name in character_names:
            character = self.get_character_by_name(name)
            if not character:
                # 尝试通过别名查找
                character = self.find_character_by_alias(name)
            
            if character:
                info = f"- {character.name}"
                if character.appearance:
                    info += f" (外貌: {character.appearance})"
                if character.clothing:
                    info += f" (服装: {character.clothing})"
                if character.personality:
                    info += f" (性格: {character.personality})"
                info_parts.append(info)
            else:
                info_parts.append(f"- {name} (无详细信息)")
        
        return "\n".join(info_parts)
    
    def get_character_details(self, character_names: List[str]) -> Dict[str, Dict[str, str]]:
        """
        获取角色详细信息字典
        
        Args:
            character_names: 角色名称列表
            
        Returns:
            角色详细信息字典
        """
        details = {}
        
        for name in character_names:
            character = self.get_character_by_name(name)
            if not character:
                character = self.find_character_by_alias(name)
            
            if character:
                details[name] = {
                    "name": character.name,
                    "appearance": character.appearance or "未知",
                    "clothing": character.clothing or "未知",
                    "personality": character.personality or "未知",
                    "role_type": character.role_type or "未知"
                }
            else:
                details[name] = {
                    "name": name,
                    "appearance": "未知",
                    "clothing": "未知",
                    "personality": "未知",
                    "role_type": "未知"
                }
        
        return details