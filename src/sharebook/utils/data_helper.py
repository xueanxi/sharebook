"""
数据访问工具类

统一管理项目中data目录的访问，避免在项目各处进行路径转换操作。
遵循项目结构规范文档中的数据文件处理规范。
"""

import os
from pathlib import Path
from typing import Union, Optional, List
import pandas as pd
import json
import yaml


class DataHelper:
    """数据访问工具类，统一管理data目录的访问"""
    
    def __init__(self):
        """初始化数据助手"""
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.data_dir = self.project_root / "data"
        
        # 确保data目录存在
        self.data_dir.mkdir(exist_ok=True)
        
        # 定义各个子目录
        self.raw_dir = self.data_dir / "raw"
        self.cleaned_novel_dir = self.data_dir / "cleaned_novel"
        self.output_dir = self.data_dir / "output"
        self.characters_dir = self.data_dir / "characters"
        self.storyboards_dir = self.data_dir / "storyboards"
        self.storyboards_image_dir = self.data_dir / "storyboards_image"
        self.storyboards_prompt_dir = self.data_dir / "storyboards_prompt"
        self.processed_dir = self.data_dir / "processed"
        self.prompts_dir = self.data_dir / "prompts"
        
        # 创建所有需要的子目录
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保所有必要的目录存在"""
        directories = [
            self.raw_dir,
            self.cleaned_novel_dir,
            self.output_dir,
            self.characters_dir,
            self.storyboards_dir,
            self.storyboards_image_dir,
            self.storyboards_prompt_dir,
            self.processed_dir,
            self.prompts_dir,
            self.characters_dir / "image",
            self.characters_dir / "history"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_raw_path(self, filename: str) -> Path:
        """获取raw目录下的文件路径
        
        Args:
            filename: 文件名
            
        Returns:
            完整的文件路径
        """
        return self.raw_dir / filename
    
    def get_cleaned_novel_path(self, filename: str) -> Path:
        """获取cleaned_novel目录下的文件路径
        
        Args:
            filename: 文件名
            
        Returns:
            完整的文件路径
        """
        return self.cleaned_novel_dir / filename
    
    def get_output_path(self, filename: str) -> Path:
        """获取output目录下的文件路径
        
        Args:
            filename: 文件名
            
        Returns:
            完整的文件路径
        """
        return self.output_dir / filename
    
    def get_characters_path(self, filename: str = "characters.csv") -> Path:
        """获取characters目录下的文件路径
        
        Args:
            filename: 文件名，默认为characters.csv
            
        Returns:
            完整的文件路径
        """
        return self.characters_dir / filename
    
    def get_character_image_path(self, character_name: str, filename: str) -> Path:
        """获取角色图片目录下的文件路径
        
        Args:
            character_name: 角色名称
            filename: 图片文件名
            
        Returns:
            完整的文件路径
        """
        character_dir = self.characters_dir / "image" / character_name
        character_dir.mkdir(parents=True, exist_ok=True)
        return character_dir / filename
    
    def get_storyboards_path(self, filename: str) -> Path:
        """获取storyboards目录下的文件路径
        
        Args:
            filename: 文件名
            
        Returns:
            完整的文件路径
        """
        return self.storyboards_dir / filename
    
    def get_storyboards_image_path(self, filename: str) -> Path:
        """获取storyboards_image目录下的文件路径
        
        Args:
            filename: 文件名
            
        Returns:
            完整的文件路径
        """
        return self.storyboards_image_dir / filename
    
    def get_storyboards_prompt_path(self, filename: str) -> Path:
        """获取storyboards_prompt目录下的文件路径
        
        Args:
            filename: 文件名
            
        Returns:
            完整的文件路径
        """
        return self.storyboards_prompt_dir / filename
    
    def get_processed_path(self, filename: str) -> Path:
        """获取processed目录下的文件路径
        
        Args:
            filename: 文件名
            
        Returns:
            完整的文件路径
        """
        return self.processed_dir / filename
    
    def get_prompts_path(self, filename: str) -> Path:
        """获取prompts目录下的文件路径
        
        Args:
            filename: 文件名
            
        Returns:
            完整的文件路径
        """
        return self.prompts_dir / filename
    
    def list_raw_files(self, pattern: str = "*.txt") -> List[Path]:
        """列出raw目录下的文件
        
        Args:
            pattern: 文件匹配模式，默认为*.txt
            
        Returns:
            文件路径列表
        """
        return list(self.raw_dir.glob(pattern))
    
    def list_cleaned_novel_files(self, pattern: str = "*.txt") -> List[Path]:
        """列出cleaned_novel目录下的文件
        
        Args:
            pattern: 文件匹配模式，默认为*.txt
            
        Returns:
            文件路径列表
        """
        return list(self.cleaned_novel_dir.glob(pattern))
    
    def list_storyboards_prompt_files(self, pattern: str = "*.json") -> List[Path]:
        """列出storyboards_prompt目录下的文件
        
        Args:
            pattern: 文件匹配模式，默认为*.json
            
        Returns:
            文件路径列表
        """
        return list(self.storyboards_prompt_dir.glob(pattern))
    
    def read_text_file(self, file_path: Union[str, Path]) -> str:
        """读取文本文件
        
        Args:
            file_path: 文件路径（可以是相对路径或绝对路径）
            
        Returns:
            文件内容
        """
        path = Path(file_path)
        if not path.is_absolute():
            # 如果是相对路径，假设相对于data目录
            path = self.data_dir / path
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def write_text_file(self, content: str, file_path: Union[str, Path]) -> Path:
        """写入文本文件
        
        Args:
            content: 文件内容
            file_path: 文件路径（可以是相对路径或绝对路径）
            
        Returns:
            写入的文件路径
        """
        path = Path(file_path)
        if not path.is_absolute():
            # 如果是相对路径，假设相对于data目录
            path = self.data_dir / path
        
        # 确保目录存在
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return path
    
    def read_json_file(self, file_path: Union[str, Path]) -> dict:
        """读取JSON文件
        
        Args:
            file_path: 文件路径（可以是相对路径或绝对路径）
            
        Returns:
            JSON数据
        """
        path = Path(file_path)
        if not path.is_absolute():
            path = self.data_dir / path
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def write_json_file(self, data: dict, file_path: Union[str, Path], indent: int = 2) -> Path:
        """写入JSON文件
        
        Args:
            data: 要写入的数据
            file_path: 文件路径（可以是相对路径或绝对路径）
            indent: JSON缩进
            
        Returns:
            写入的文件路径
        """
        path = Path(file_path)
        if not path.is_absolute():
            path = self.data_dir / path
        
        # 确保目录存在
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        
        return path
    
    def read_csv_file(self, file_path: Union[str, Path], **kwargs) -> pd.DataFrame:
        """读取CSV文件
        
        Args:
            file_path: 文件路径（可以是相对路径或绝对路径）
            **kwargs: pandas.read_csv的其他参数
            
        Returns:
            DataFrame
        """
        path = Path(file_path)
        if not path.is_absolute():
            path = self.data_dir / path
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {path}")
        
        return pd.read_csv(path, **kwargs)
    
    def write_csv_file(self, df: pd.DataFrame, file_path: Union[str, Path], **kwargs) -> Path:
        """写入CSV文件
        
        Args:
            df: 要写入的DataFrame
            file_path: 文件路径（可以是相对路径或绝对路径）
            **kwargs: pandas.to_csv的其他参数
            
        Returns:
            写入的文件路径
        """
        path = Path(file_path)
        if not path.is_absolute():
            path = self.data_dir / path
        
        # 确保目录存在
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # 默认参数
        default_kwargs = {
            'index': False,
            'encoding': 'utf-8'
        }
        default_kwargs.update(kwargs)
        
        df.to_csv(path, **default_kwargs)
        return path
    
    def read_yaml_file(self, file_path: Union[str, Path]) -> dict:
        """读取YAML文件
        
        Args:
            file_path: 文件路径（可以是相对路径或绝对路径）
            
        Returns:
            YAML数据
        """
        path = Path(file_path)
        if not path.is_absolute():
            path = self.data_dir / path
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def write_yaml_file(self, data: dict, file_path: Union[str, Path]) -> Path:
        """写入YAML文件
        
        Args:
            data: 要写入的数据
            file_path: 文件路径（可以是相对路径或绝对路径）
            
        Returns:
            写入的文件路径
        """
        path = Path(file_path)
        if not path.is_absolute():
            path = self.data_dir / path
        
        # 确保目录存在
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
        
        return path
    
    def file_exists(self, file_path: Union[str, Path]) -> bool:
        """检查文件是否存在
        
        Args:
            file_path: 文件路径（可以是相对路径或绝对路径）
            
        Returns:
            文件是否存在
        """
        path = Path(file_path)
        if not path.is_absolute():
            path = self.data_dir / path
        
        return path.exists()
    
    def get_relative_path(self, file_path: Union[str, Path]) -> Path:
        """获取相对于data目录的路径
        
        Args:
            file_path: 文件路径（应该是绝对路径）
            
        Returns:
            相对于data目录的路径
        """
        path = Path(file_path)
        if path.is_absolute():
            try:
                return path.relative_to(self.data_dir)
            except ValueError:
                # 如果路径不在data目录下，返回原路径
                return path
        return path


# 创建全局实例
data_helper = DataHelper()