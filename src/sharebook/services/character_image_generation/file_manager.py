"""
文件管理模块

负责管理图片文件的存储, 包括创建角色目录, 保存图片等.
"""

import os
import shutil
from typing import List, Optional


class FileManager:
    """文件管理器"""
    
    def __init__(self, base_dir: str):
        """
        初始化文件管理器
        
        Args:
            base_dir: 基础目录路径
        """
        self.base_dir = base_dir
        # 确保基础目录存在
        os.makedirs(self.base_dir, exist_ok=True)
    
    def create_character_directory(self, character_name: str) -> str:
        """
        为角色创建目录
        
        Args:
            character_name: 角色名称
            
        Returns:
            角色目录的绝对路径
        """
        # 清理角色名称, 移除不适合作为目录名的字符
        safe_name = self._sanitize_filename(character_name)
        character_dir = os.path.join(self.base_dir, safe_name)
        os.makedirs(character_dir, exist_ok=True)
        return character_dir
    
    def get_character_directory(self, character_name: str) -> str:
        """
        获取角色目录路径
        
        Args:
            character_name: 角色名称
            
        Returns:
            角色目录的绝对路径
        """
        safe_name = self._sanitize_filename(character_name)
        return os.path.join(self.base_dir, safe_name)
    
    def save_image(self, image_data: bytes, character_name: str, filename: str) -> str:
        """
        保存图片到角色目录
        
        Args:
            image_data: 图片二进制数据
            character_name: 角色名称
            filename: 文件名
            
        Returns:
            保存后的图片绝对路径
        """
        character_dir = self.create_character_directory(character_name)
        image_path = os.path.join(character_dir, filename)
        
        try:
            with open(image_path, 'wb') as f:
                f.write(image_data)
            return image_path
        except Exception as e:
            raise IOError(f"保存图片失败: {str(e)}")
    
    def get_image_path(self, character_name: str, filename: str) -> str:
        """
        获取图片路径
        
        Args:
            character_name: 角色名称
            filename: 文件名
            
        Returns:
            图片的绝对路径
        """
        safe_name = self._sanitize_filename(character_name)
        return os.path.join(self.base_dir, safe_name, filename)
    
    def list_character_images(self, character_name: str) -> List[str]:
        """
        列出角色的所有图片
        
        Args:
            character_name: 角色名称
            
        Returns:
            图片文件路径列表
        """
        character_dir = self.get_character_directory(character_name)
        if not os.path.exists(character_dir):
            return []
        
        images = []
        for filename in os.listdir(character_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                images.append(os.path.join(character_dir, filename))
        
        return sorted(images)
    
    def delete_character_directory(self, character_name: str) -> bool:
        """
        删除角色目录及其所有内容
        
        Args:
            character_name: 角色名称
            
        Returns:
            删除是否成功
        """
        character_dir = self.get_character_directory(character_name)
        if not os.path.exists(character_dir):
            return True
        
        try:
            shutil.rmtree(character_dir)
            return True
        except Exception:
            return False
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        清理文件名, 移除不适合作为文件/目录名的字符
        
        Args:
            filename: 原始文件名
            
        Returns:
            清理后的文件名
        """
        # 移除或替换不适合作为目录名的字符
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # 移除首尾空格和点
        filename = filename.strip(' .')
        
        # 如果为空, 使用默认名称
        if not filename:
            filename = "unnamed_character"
        
        return filename
    
    def get_next_image_number(self, character_name: str) -> int:
        """
        获取下一个图片编号
        
        Args:
            character_name: 角色名称
            
        Returns:
            下一个可用的图片编号
        """
        character_dir = self.get_character_directory(character_name)
        if not os.path.exists(character_dir):
            return 1
        
        max_num = 0
        for filename in os.listdir(character_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                # 尝试从文件名中提取编号
                base_name = os.path.splitext(filename)[0]
                try:
                    if base_name.startswith('image_'):
                        num = int(base_name.split('_')[1])
                        max_num = max(max_num, num)
                except (IndexError, ValueError):
                    continue
        
        return max_num + 1
