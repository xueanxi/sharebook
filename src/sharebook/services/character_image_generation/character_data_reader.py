"""
角色数据读取模块

负责从CSV文件中读取角色数据, 提取姓名和容貌提示词.
"""

import csv
import os
from typing import List, Dict, Optional


class CharacterDataReader:
    """角色数据读取器"""
    
    def __init__(self, csv_file_path: str):
        """
        初始化角色数据读取器
        
        Args:
            csv_file_path: CSV文件路径
        """
        self.csv_file_path = csv_file_path
    
    def read_characters(self) -> List[Dict[str, str]]:
        """
        读取角色数据
        
        Returns:
            角色数据列表, 每个角色包含姓名, 提示词, 性别和角色类型等信息
        """
        if not os.path.exists(self.csv_file_path):
            raise FileNotFoundError(f"角色数据文件不存在: {self.csv_file_path}")
        
        characters = []
        try:
            with open(self.csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # 提取姓名和容貌提示词
                    name = row.get('姓名', '').strip()
                    prompt = row.get('容貌提示词', '').strip().strip('"')
                    gender = row.get('性别', '').strip()
                    char_type = row.get('角色类型', '').strip()
                    
                    if name and prompt:
                        characters.append({
                            'name': name,
                            'prompt': prompt,
                            'gender': gender,
                            'type': char_type
                        })
        except Exception as e:
            raise ValueError(f"读取角色数据文件时出错: {str(e)}")
        
        return characters
    
    def validate_data(self, data: List[Dict[str, str]]) -> bool:
        """
        验证数据完整性
        
        Args:
            data: 角色数据列表
            
        Returns:
            验证结果
        """
        if not data:
            return False
        
        for character in data:
            if not character.get('name') or not character.get('prompt'):
                return False
        
        return True
    
    def get_character_by_name(self, name: str) -> Optional[Dict[str, str]]:
        """
        根据姓名获取角色信息
        
        Args:
            name: 角色姓名
            
        Returns:
            角色信息字典, 如果未找到则返回None
        """
        characters = self.read_characters()
        for character in characters:
            if character['name'] == name:
                return character
        return None