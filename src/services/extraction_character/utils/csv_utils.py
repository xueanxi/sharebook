"""
CSV操作工具模块
"""

import os
import csv
from typing import List, Dict, Any, Tuple, Set
from pathlib import Path

# 尝试导入pandas，如果没有则使用基础csv操作
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    print("警告: pandas未安装，将使用基础csv操作")


class CSVUtils:
    """CSV操作工具类"""
    
    def __init__(self, csv_path: str):
        """
        初始化CSV工具
        
        Args:
            csv_path: CSV文件路径
        """
        self.csv_path = csv_path
        self._ensure_csv_exists()
    
    def _ensure_csv_exists(self):
        """确保CSV文件存在"""
        if not os.path.exists(self.csv_path):
            # 确保目录存在
            os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
            
            # 创建CSV文件并写入表头
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['姓名', '性别', '外貌特征', '服装特点', '角色类型', '别名'])
    
    def read_csv(self):
        """
        读取CSV文件
        
        Returns:
            DataFrame包含所有角色信息（如果有pandas）或字典列表
        """
        try:
            if not os.path.exists(self.csv_path):
                if HAS_PANDAS:
                    return pd.DataFrame(columns=['姓名', '性别', '外貌特征', '服装特点', '角色类型', '别名'])
                else:
                    return []
            
            if HAS_PANDAS:
                return pd.read_csv(self.csv_path, encoding='utf-8')
            else:
                # 使用基础csv操作
                with open(self.csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    return list(reader)
        except Exception as e:
            print(f"读取CSV文件失败: {e}")
            if HAS_PANDAS:
                return pd.DataFrame(columns=['姓名', '性别', '外貌特征', '服装特点', '角色类型', '别名'])
            else:
                return []
    
    def write_csv(self, data) -> bool:
        """
        写入CSV文件
        
        Args:
            data: 要写入的数据（DataFrame或字典列表）
            
        Returns:
            是否写入成功
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
            
            if HAS_PANDAS and hasattr(data, 'to_csv'):
                # 使用pandas写入
                data.to_csv(self.csv_path, index=False, encoding='utf-8')
            else:
                # 使用基础csv操作
                with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
                    if data:
                        writer = csv.DictWriter(f, fieldnames=['姓名', '性别', '外貌特征', '服装特点', '角色类型', '别名'])
                        writer.writeheader()
                        writer.writerows(data)
                    else:
                        writer = csv.writer(f)
                        writer.writerow(['姓名', '性别', '外貌特征', '服装特点', '角色类型', '别名'])
            
            return True
        except Exception as e:
            print(f"写入CSV文件失败: {e}")
            return False
    
    def append_characters(self, characters: List[Dict[str, Any]]) -> bool:
        """
        追加角色到CSV文件
        
        Args:
            characters: 角色列表
            
        Returns:
            是否追加成功
        """
        try:
            # 读取现有数据
            existing_data = self.read_csv()
            
            if HAS_PANDAS:
                # 使用pandas
                new_df = pd.DataFrame(characters)
                combined_df = pd.concat([existing_data, new_df], ignore_index=True)
                return self.write_csv(combined_df)
            else:
                # 使用基础csv操作
                combined_data = existing_data + characters
                return self.write_csv(combined_data)
        except Exception as e:
            print(f"追加角色到CSV失败: {e}")
            return False
    
    def update_characters(self, characters: List[Dict[str, Any]]) -> bool:
        """
        更新CSV文件中的角色信息
        
        Args:
            characters: 角色列表
            
        Returns:
            是否更新成功
        """
        try:
            # 读取现有数据
            existing_data = self.read_csv()
            
            if HAS_PANDAS:
                # 使用pandas
                new_df = pd.DataFrame(characters)
                
                if not existing_data.empty:
                    # 删除已存在的角色（基于姓名）
                    existing_names = set(existing_data['姓名'].tolist())
                    new_names = set(new_df['姓名'].tolist())
                    
                    # 保留新数据中没有的旧角色
                    old_characters = existing_data[~existing_data['姓名'].isin(new_names)]
                    
                    # 合并新旧数据
                    combined_df = pd.concat([old_characters, new_df], ignore_index=True)
                else:
                    combined_df = new_df
                
                return self.write_csv(combined_df)
            else:
                # 使用基础csv操作
                # 获取新角色名称
                new_names = {char.get('姓名', '') for char in characters if char.get('姓名')}
                
                # 保留新数据中没有的旧角色
                old_characters = [
                    char for char in existing_data 
                    if char.get('姓名', '') not in new_names
                ]
                
                # 合并数据
                combined_data = old_characters + characters
                return self.write_csv(combined_data)
        except Exception as e:
            print(f"更新CSV失败: {e}")
            return False
    
    def find_existing_characters(self, characters: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        查找已存在的角色
        
        Args:
            characters: 角色列表
            
        Returns:
            (新角色列表, 已存在角色列表)
        """
        try:
            # 读取现有数据
            existing_data = self.read_csv()
            
            if not existing_data:
                return characters, []
            
            # 创建角色名称和别名的集合
            existing_names = set()
            existing_aliases = set()
            
            if HAS_PANDAS:
                # 使用pandas
                for _, row in existing_data.iterrows():
                    name = row['姓名']
                    aliases = str(row['别名']).split('|') if pd.notna(row['别名']) and row['别名'] else []
                    
                    existing_names.add(name)
                    existing_aliases.update(aliases)
                    existing_aliases.add(name)  # 主名称也算作别名
            else:
                # 使用基础csv操作
                for row in existing_data:
                    name = row.get('姓名', '')
                    aliases = str(row.get('别名', '')).split('|') if row.get('别名') else []
                    
                    existing_names.add(name)
                    existing_aliases.update(aliases)
                    existing_aliases.add(name)  # 主名称也算作别名
            
            new_characters = []
            existing_characters = []
            
            for character in characters:
                name = character.get('姓名', '')
                aliases = character.get('别名', [])
                
                # 检查主名称或别名是否已存在
                all_names = [name] + aliases
                is_existing = any(alias in existing_names or alias in existing_aliases for alias in all_names)
                
                if is_existing:
                    existing_characters.append(character)
                else:
                    new_characters.append(character)
            
            return new_characters, existing_characters
        except Exception as e:
            print(f"查找已存在角色失败: {e}")
            return characters, []
    
    def get_character_by_name(self, name: str) -> Dict[str, Any]:
        """
        根据姓名获取角色信息
        
        Args:
            name: 角色姓名
            
        Returns:
            角色信息字典
        """
        try:
            existing_data = self.read_csv()
            
            if not existing_data:
                return {}
            
            if HAS_PANDAS:
                # 使用pandas
                # 查找匹配的角色
                character_rows = existing_data[existing_data['姓名'] == name]
                
                if not character_rows.empty:
                    return character_rows.iloc[0].to_dict()
                
                # 检查别名
                for _, row in existing_data.iterrows():
                    aliases = str(row['别名']).split('|') if pd.notna(row['别名']) and row['别名'] else []
                    if name in aliases:
                        return row.to_dict()
            else:
                # 使用基础csv操作
                for row in existing_data:
                    if row.get('姓名', '') == name:
                        return row
                    
                    # 检查别名
                    aliases = str(row.get('别名', '')).split('|') if row.get('别名') else []
                    if name in aliases:
                        return row
            
            return {}
        except Exception as e:
            print(f"获取角色信息失败: {e}")
            return {}
    
    def get_all_character_names_and_aliases(self) -> Set[str]:
        """
        获取所有角色名称和别名
        
        Returns:
            角色名称和别名的集合
        """
        try:
            existing_data = self.read_csv()
            
            if not existing_data:
                return set()
            
            all_names = set()
            
            if HAS_PANDAS:
                # 使用pandas
                for _, row in existing_data.iterrows():
                    name = row['姓名']
                    aliases = str(row['别名']).split('|') if pd.notna(row['别名']) and row['别名'] else []
                    
                    all_names.add(name)
                    all_names.update(aliases)
            else:
                # 使用基础csv操作
                for row in existing_data:
                    name = row.get('姓名', '')
                    aliases = str(row.get('别名', '')).split('|') if row.get('别名') else []
                    
                    all_names.add(name)
                    all_names.update(aliases)
            
            return all_names
        except Exception as e:
            print(f"获取角色名称和别名失败: {e}")
            return set()
    
    def merge_character_info(self, existing_info: Dict[str, Any], new_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        合并角色信息（简单版本，不使用LLM）
        
        Args:
            existing_info: 已有角色信息
            new_info: 新角色信息
            
        Returns:
            合并后的角色信息
        """
        try:
            merged = {}
            
            # 姓名
            merged['姓名'] = existing_info.get('姓名', new_info.get('姓名', ''))
            
            # 性别
            existing_gender = existing_info.get('性别', '未知')
            new_gender = new_info.get('性别', '未知')
            merged['性别'] = new_gender if new_gender != '未知' else existing_gender
            
            # 外貌特征
            existing_appearance = existing_info.get('外貌特征', '未知')
            new_appearance = new_info.get('外貌特征', '未知')
            if new_appearance != '未知' and new_appearance != existing_appearance:
                merged['外貌特征'] = new_appearance
            else:
                merged['外貌特征'] = existing_appearance
            
            # 服装特点
            existing_clothing = existing_info.get('服装特点', '未知')
            new_clothing = new_info.get('服装特点', '未知')
            if new_clothing != '未知' and new_clothing != existing_clothing:
                merged['服装特点'] = new_clothing
            else:
                merged['服装特点'] = existing_clothing
            
            # 角色类型
            existing_type = existing_info.get('角色类型', '其他')
            new_type = new_info.get('角色类型', '其他')
            merged['角色类型'] = new_type if new_type != '其他' else existing_type
            
            # 别名
            existing_aliases = set(existing_info.get('别名', []))
            new_aliases = set(new_info.get('别名', []))
            merged_aliases = existing_aliases.union(new_aliases)
            
            # 转换为字符串，用|分隔
            merged['别名'] = '|'.join(sorted(merged_aliases)) if merged_aliases else ''
            
            return merged
        except Exception as e:
            print(f"合并角色信息失败: {e}")
            return new_info