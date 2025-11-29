"""
角色数据管理器
负责加载和管理角色CSV数据
"""
import csv
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging
import os
import sys

# 添加项目根目录到路径
current_file = os.path.abspath(__file__)
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from sharebook.utils.logging_manager import LogModule, get_module_logger
from sharebook.utils.data_helper import data_helper

logger = get_module_logger(LogModule.STORYBOARD_TO_PROMPT)


class CharacterDataManager:
    """角色数据管理器类"""
    
    def __init__(self, csv_path: Optional[str] = None):
        """
        初始化角色数据管理器
        
        Args:
            csv_path: 角色CSV文件路径，如果为None则使用默认路径
        """
        if csv_path is None:
            csv_path = data_helper.get_characters_csv_path()
        
        self.csv_path = Path(csv_path)
        self.characters_data = {}
        self.aliases_index = {}
        
        # 加载角色数据
        self._load_characters_data()
    
    def _load_characters_data(self):
        """加载角色CSV数据"""
        try:
            if not self.csv_path.exists():
                logger.error(f"角色CSV文件不存在: {self.csv_path}")
                return
            
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    # 解析别名（JSON格式）
                    aliases = []
                    if row['别名']:
                        try:
                            aliases = json.loads(row['别名']) if row['别名'].startswith('[') else [row['别名']]
                        except:
                            aliases = [row['别名']]
                    
                    # 构建角色数据
                    character_data = {
                        'name': row['姓名'],
                        'aliases': aliases,
                        'gender': row['性别'],
                        'appearance': row['外貌特征'],
                        'clothing': row['服装特点'],
                        'character_type': row['角色类型'],
                        'appearance_prompt': row['容貌提示词']
                    }
                    
                    # 存储主名称数据
                    self.characters_data[row['姓名']] = character_data
                    
                    # 建立别名索引
                    for alias in aliases:
                        self.aliases_index[alias] = row['姓名']
            
            logger.info(f"成功加载 {len(self.characters_data)} 个角色数据")
            
        except Exception as e:
            logger.error(f"加载角色CSV数据失败: {str(e)}")
    
    def get_character_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        根据角色名称查找角色信息
        
        Args:
            name: 角色名称或别名
            
        Returns:
            角色数据字典，如果未找到返回None
        """
        # 首先尝试直接查找主名称
        if name in self.characters_data:
            return self.characters_data[name].copy()
        
        # 然后尝试查找别名
        if name in self.aliases_index:
            main_name = self.aliases_index[name]
            return self.characters_data[main_name].copy()
        
        return None
    
    def get_character_reference_info(self, character_name: str) -> Dict[str, Any]:
        """
        获取角色的参考信息
        
        Args:
            character_name: 角色名称
            
        Returns:
            角色参考信息字典
        """
        character = self.get_character_by_name(character_name)
        if not character:
            return {}
        
        # 构建参考图片路径
        reference_image_path = data_helper.get_character_image_path(character_name)
        image_path = Path(reference_image_path)
        
        return {
            'name': character['name'],
            'aliases': character['aliases'],
            'gender': character['gender'],
            'character_type': character['character_type'],
            'reference_image_path': reference_image_path if image_path.exists() else None,
            'character_prompt': character['appearance_prompt'],
            'appearance': character['appearance'],
            'clothing': character['clothing']
        }
    
    def get_all_characters(self) -> List[Dict[str, Any]]:
        """
        获取所有角色信息
        
        Returns:
            所有角色数据列表
        """
        return [data.copy() for data in self.characters_data.values()]
    
    def search_characters_by_type(self, character_type: str) -> List[Dict[str, Any]]:
        """
        根据角色类型搜索角色
        
        Args:
            character_type: 角色类型（主角/配角/反派）
            
        Returns:
            匹配的角色列表
        """
        results = []
        for character in self.characters_data.values():
            if character['character_type'] == character_type:
                results.append(character.copy())
        
        return results
    
    def validate_character_data(self) -> Dict[str, Any]:
        """
        验证角色数据的完整性
        
        Returns:
            验证结果字典
        """
        validation_result = {
            'total_characters': len(self.characters_data),
            'valid_characters': 0,
            'missing_images': [],
            'missing_prompts': [],
            'errors': []
        }
        
        for name, character in self.characters_data.items():
            is_valid = True
            
            # 检查必要字段
            if not character['name']:
                validation_result['errors'].append(f"角色 {name} 缺少姓名")
                is_valid = False
            
            if not character['appearance_prompt']:
                validation_result['missing_prompts'].append(name)
                is_valid = False
            
            # 检查参考图片
            image_path = Path(data_helper.get_character_image_path(name))
            if not image_path.exists():
                validation_result['missing_images'].append(name)
                is_valid = False
            
            if is_valid:
                validation_result['valid_characters'] += 1
        
        return validation_result
    
    def reload_data(self):
        """重新加载角色数据"""
        self.characters_data.clear()
        self.aliases_index.clear()
        self._load_characters_data()