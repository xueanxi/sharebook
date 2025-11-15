"""
文件处理工具
"""

import os
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

from src.utils.logging_manager import get_logger, LogCategory

logger = get_logger(__name__, LogCategory.DATA)


class FileHandler:
    """文件处理工具类"""
    
    def __init__(self):
        self.logger = logger
    
    def read_text_file(self, file_path: str) -> str:
        """
        读取文本文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件内容字符串
            
        Raises:
            FileNotFoundError: 文件不存在
            UnicodeDecodeError: 文件编码问题
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.logger.info(f"成功读取文件: {file_path}")
            return content
        except FileNotFoundError:
            self.logger.error(f"文件不存在: {file_path}")
            raise
        except UnicodeDecodeError as e:
            self.logger.error(f"文件编码错误: {file_path}, 错误: {e}")
            raise
    
    def write_json_file(self, file_path: str, data: Dict[str, Any]) -> None:
        """
        写入JSON文件
        
        Args:
            file_path: 输出文件路径
            data: 要写入的数据
        """
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.logger.info(f"成功写入JSON文件: {file_path}")
        except Exception as e:
            self.logger.error(f"写入JSON文件失败: {file_path}, 错误: {e}")
            raise
    
    def read_csv_file(self, file_path: str) -> List[Dict[str, str]]:
        """
        读取CSV文件
        
        Args:
            file_path: CSV文件路径
            
        Returns:
            包含CSV数据的字典列表
        """
        import csv
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = list(reader)
            self.logger.info(f"成功读取CSV文件: {file_path}, 共{len(data)}行")
            return data
        except FileNotFoundError:
            self.logger.error(f"CSV文件不存在: {file_path}")
            raise
        except Exception as e:
            self.logger.error(f"读取CSV文件失败: {file_path}, 错误: {e}")
            raise
    
    def list_files_in_directory(self, directory: str, pattern: str = "*.txt") -> List[str]:
        """
        列出目录中的文件
        
        Args:
            directory: 目录路径
            pattern: 文件模式（如 "*.txt"）
            
        Returns:
            文件路径列表
        """
        try:
            path = Path(directory)
            files = list(path.glob(pattern))
            file_paths = [str(f) for f in files if f.is_file()]
            self.logger.info(f"在目录 {directory} 中找到 {len(file_paths)} 个匹配文件")
            return sorted(file_paths)
        except Exception as e:
            self.logger.error(f"列出目录文件失败: {directory}, 错误: {e}")
            raise
    
    def ensure_directory_exists(self, directory: str) -> None:
        """
        确保目录存在
        
        Args:
            directory: 目录路径
        """
        try:
            os.makedirs(directory, exist_ok=True)
            self.logger.debug(f"确保目录存在: {directory}")
        except Exception as e:
            self.logger.error(f"创建目录失败: {directory}, 错误: {e}")
            raise
    
    def get_file_name_without_extension(self, file_path: str) -> str:
        """
        获取不带扩展名的文件名
        
        Args:
            file_path: 文件路径
            
        Returns:
            不带扩展名的文件名
        """
        return Path(file_path).stem