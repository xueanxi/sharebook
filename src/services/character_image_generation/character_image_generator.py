"""
角色图片生成控制模块

控制整个图片生成流程, 协调各个子模块的工作.
"""

import os
from typing import List, Dict, Optional
from .character_data_reader import CharacterDataReader
from .comfyui_interface import ComfyUIInterface
from .file_manager import FileManager
from config.logging_config import get_logger

logger = get_logger(__name__)


class CharacterImageGenerator:
    """角色图片生成器"""
    
    def __init__(self, 
                 csv_file_path: str = "data/characters/characters.csv",
                 output_base_dir: str = "data/characters/image",
                 workflow_template: str = "comfyui/novel_t2I_flux.json"):
        """
        初始化角色图片生成器
        
        Args:
            csv_file_path: 角色数据CSV文件路径
            output_base_dir: 图片输出基础目录
            workflow_template: ComfyUI工作流模板文件路径
        """
        self.data_reader = CharacterDataReader(csv_file_path)
        self.comfyui_interface = ComfyUIInterface(workflow_template)
        self.file_manager = FileManager(output_base_dir)
        
        try:
            self.characters = self.data_reader.read_characters()
            logger.info(f"已加载 {len(self.characters)} 个角色数据")
        except Exception as e:
            logger.error(f"加载角色数据失败: {str(e)}")
            self.characters = []
    
    def generate_all_characters(self, batch_size: int = 1, skip_existing: bool = True) -> Dict[str, List[str]]:
        """
        生成所有角色图片
        
        Args:
            batch_size: 批处理大小
            skip_existing: 是否跳过已有图片的角色
            
        Returns:
            角色名和图片路径的映射字典
        """
        results = {}
        total = len(self.characters)
        
        logger.info(f"开始生成 {total} 个角色的图片")
        
        for i, character in enumerate(self.characters, 1):
            name = character['name']
            logger.info(f"处理角色 {i}/{total}: {name}")
            
            try:
                # 检查是否跳过已有图片的角色
                if skip_existing:
                    existing_images = self.file_manager.list_character_images(name)
                    if existing_images:
                        logger.info(f"角色 {name} 已有 {len(existing_images)} 张图片, 跳过生成")
                        results[name] = existing_images
                        continue
                
                image_paths = self.generate_single_character(name, batch_size)
                results[name] = image_paths
                logger.info(f"成功生成角色 {name} 的 {len(image_paths)} 张图片")
                
            except Exception as e:
                logger.error(f"生成角色 {name} 图片时出错: {str(e)}")
                results[name] = []
        
        logger.info(f"角色图片生成完成, 共处理 {total} 个角色")
        return results
    
    def generate_single_character(self, name: str, batch_size: int = 1) -> List[str]:
        """
        生成指定角色图片
        
        Args:
            name: 角色名称
            batch_size: 批处理大小
            
        Returns:
            生成的图片路径列表
        """
        # 查找角色
        character = next((c for c in self.characters if c['name'] == name), None)
        if not character:
            raise ValueError(f"未找到角色: {name}")
        
        # 创建角色目录
        character_dir = self.file_manager.create_character_directory(name)
        
        # 获取下一个图片编号
        next_num = self.file_manager.get_next_image_number(name)
        
        # 生成图片
        image_paths = self.comfyui_interface.generate_image(
            prompt=character['prompt'],
            save_dir=character_dir,
            batch_size=batch_size
        )
        
        # 重命名生成的图片为有序文件名
        renamed_paths = []
        for i, old_path in enumerate(image_paths):
            new_filename = f"image_{next_num + i:03d}.png"
            new_path = self.file_manager.get_image_path(name, new_filename)
            
            # 重命名文件
            os.rename(old_path, new_path)
            renamed_paths.append(new_path)
        
        return renamed_paths
    
    def batch_generate(self, names: List[str], batch_size: int = 1) -> Dict[str, List[str]]:
        """
        批量生成指定角色图片
        
        Args:
            names: 角色名称列表
            batch_size: 批处理大小
            
        Returns:
            角色名和图片路径的映射字典
        """
        results = {}
        
        for name in names:
            try:
                image_paths = self.generate_single_character(name, batch_size)
                results[name] = image_paths
                logger.info(f"成功生成角色 {name} 的图片")
            except Exception as e:
                logger.error(f"生成角色 {name} 图片时出错: {str(e)}")
                results[name] = []
        
        return results
    
    def get_character_list(self) -> List[str]:
        """
        获取所有角色名称列表
        
        Returns:
            角色名称列表
        """
        return [character['name'] for character in self.characters]
    
    def get_character_info(self, name: str) -> Optional[Dict[str, str]]:
        """
        获取角色信息
        
        Args:
            name: 角色名称
            
        Returns:
            角色信息字典
        """
        character = next((c for c in self.characters if c['name'] == name), None)
        return character
    
    def test_connection(self) -> bool:
        """
        测试ComfyUI连接
        
        Returns:
            连接是否成功
        """
        return self.comfyui_interface.test_connection()
    
    def update_workflow_template(self, template_path: str) -> None:
        """
        更新工作流模板
        
        Args:
            template_path: 新的模板文件路径
        """
        self.comfyui_interface.update_workflow_template(template_path)
    
    def get_character_images(self, name: str) -> List[str]:
        """
        获取角色的所有图片路径
        
        Args:
            name: 角色名称
            
        Returns:
            图片路径列表
        """
        return self.file_manager.list_character_images(name)
    
    def delete_character_images(self, name: str) -> bool:
        """
        删除角色的所有图片
        
        Args:
            name: 角色名称
            
        Returns:
            删除是否成功
        """
        result = self.file_manager.delete_character_directory(name)
        if result:
            logger.info(f"已删除角色 {name} 的所有图片")
        else:
            logger.error(f"删除角色 {name} 的图片失败")
        return result