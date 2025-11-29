"""
参考图片管理器
负责管理角色参考图片的加载和验证
"""
from typing import Dict, List, Optional, Any
from pathlib import Path
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


class ReferenceImageManager:
    """参考图片管理器类"""
    
    def __init__(self, image_dir: Optional[str] = None):
        """
        初始化参考图片管理器
        
        Args:
            image_dir: 角色图片目录路径，如果为None则使用默认路径
        """
        if image_dir is None:
            image_dir = data_helper.get_character_image_dir()
        
        self.image_dir = Path(image_dir)
        self.supported_formats = [".jpg", ".jpeg", ".png", ".webp"]
        
        # 确保图片目录存在
        self._ensure_directory_exists()
    
    def _ensure_directory_exists(self):
        """确保图片目录存在"""
        try:
            self.image_dir.mkdir(parents=True, exist_ok=True)
            logger.debug(f"确保图片目录存在: {self.image_dir}")
        except Exception as e:
            logger.error(f"创建图片目录失败 {self.image_dir}: {str(e)}")
    
    def validate_reference_image(self, image_path: Path) -> Dict[str, Any]:
        """
        验证参考图片
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            验证结果字典
        """
        validation_result = {
            'is_valid': False,
            'exists': False,
            'format_supported': False,
            'file_size': 0,
            'errors': []
        }
        
        try:
            # 检查文件是否存在
            if not image_path.exists():
                validation_result['errors'].append(f"图片文件不存在: {image_path}")
                return validation_result
            
            validation_result['exists'] = True
            validation_result['file_size'] = image_path.stat().st_size
            
            # 检查文件格式
            if image_path.suffix.lower() not in self.supported_formats:
                validation_result['errors'].append(f"不支持的图片格式: {image_path.suffix}")
                return validation_result
            
            validation_result['format_supported'] = True
            
            # 如果没有错误，则验证通过
            validation_result['is_valid'] = len(validation_result['errors']) == 0
            
        except Exception as e:
            validation_result['errors'].append(f"验证图片时发生异常: {str(e)}")
        
        return validation_result
    
    def get_character_images(self, character_name: str) -> List[Dict[str, Any]]:
        """
        获取指定角色的所有参考图片
        
        Args:
            character_name: 角色名称
            
        Returns:
            图片信息列表
        """
        images = []
        
        # 首先检查角色子文件夹
        character_dir = self.image_dir / character_name
        if character_dir.exists() and character_dir.is_dir():
            # 查找子文件夹中的所有图片
            for image_file in character_dir.glob("*"):
                if image_file.is_file() and image_file.suffix.lower() in self.supported_formats:
                    validation = self.validate_reference_image(image_file)
                    images.append({
                        'path': str(image_file),
                        'type': 'folder_match',
                        'validation': validation
                    })
        else:
            # 如果没有子文件夹，则在主目录中查找
            # 查找所有匹配的图片文件
            for format_ext in self.supported_formats:
                # 精确匹配
                exact_path = self.image_dir / f"{character_name}{format_ext}"
                if exact_path.exists():
                    validation = self.validate_reference_image(exact_path)
                    images.append({
                        'path': str(exact_path),
                        'type': 'exact_match',
                        'validation': validation
                    })
            
            # 查找包含角色名称的图片
            for image_file in self.image_dir.glob(f"*{character_name}*"):
                if image_file.is_file() and image_file.suffix.lower() in self.supported_formats:
                    # 避免重复添加精确匹配的文件
                    if not any(img['path'] == str(image_file) for img in images):
                        validation = self.validate_reference_image(image_file)
                        images.append({
                            'path': str(image_file),
                            'type': 'partial_match',
                            'validation': validation
                        })
        
        return images
    
    def get_best_reference_image(self, character_name: str) -> Optional[Dict[str, Any]]:
        """
        获取角色的最佳参考图片
        
        Args:
            character_name: 角色名称
            
        Returns:
            最佳图片信息，如果没有找到返回None
        """
        images = self.get_character_images(character_name)
        
        if not images:
            return None
        
        # 优先选择文件夹匹配且验证通过的图片
        folder_matches = [img for img in images if img['type'] == 'folder_match' and img['validation']['is_valid']]
        if folder_matches:
            return folder_matches[0]
        
        # 优先选择精确匹配且验证通过的图片
        exact_matches = [img for img in images if img['type'] == 'exact_match' and img['validation']['is_valid']]
        if exact_matches:
            return exact_matches[0]
        
        # 其次选择部分匹配且验证通过的图片
        partial_matches = [img for img in images if img['type'] == 'partial_match' and img['validation']['is_valid']]
        if partial_matches:
            return partial_matches[0]
        
        # 最后选择存在的图片（即使验证失败）
        existing_images = [img for img in images if img['validation']['exists']]
        if existing_images:
            return existing_images[0]
        
        return None
    
    def get_all_images_info(self) -> Dict[str, Any]:
        """
        获取所有图片的信息统计
        
        Returns:
            图片统计信息字典
        """
        stats = {
            'total_images': 0,
            'valid_images': 0,
            'invalid_images': 0,
            'supported_formats': {},
            'images_by_character': {}
        }
        
        try:
            # 首先遍历所有角色子文件夹
            for character_dir in self.image_dir.iterdir():
                if character_dir.is_dir():
                    character_name = character_dir.name
                    
                    # 处理子文件夹中的图片
                    for image_file in character_dir.glob("*"):
                        if image_file.is_file() and image_file.suffix.lower() in self.supported_formats:
                            self._process_image_file(image_file, stats, character_name)
            
            # 然后处理主目录中的图片文件
            for image_file in self.image_dir.glob("*"):
                if image_file.is_file() and image_file.suffix.lower() in self.supported_formats:
                    character_name = image_file.stem
                    self._process_image_file(image_file, stats, character_name)
        
        except Exception as e:
            logger.error(f"获取图片统计信息失败: {str(e)}")
        
        return stats
    
    def _process_image_file(self, image_file: Path, stats: Dict[str, Any], character_name: str):
        """
        处理单个图片文件的统计信息
        
        Args:
            image_file: 图片文件路径
            stats: 统计信息字典
            character_name: 角色名称
        """
        stats['total_images'] += 1
        
        # 统计格式
        ext = image_file.suffix.lower()
        stats['supported_formats'][ext] = stats['supported_formats'].get(ext, 0) + 1
        
        # 验证图片
        validation = self.validate_reference_image(image_file)
        
        if validation['is_valid']:
            stats['valid_images'] += 1
        else:
            stats['invalid_images'] += 1
        
        # 按角色分组
        if character_name not in stats['images_by_character']:
            stats['images_by_character'][character_name] = []
        
        stats['images_by_character'][character_name].append({
            'path': str(image_file),
            'validation': validation
        })
    
    def cleanup_invalid_images(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        清理无效的图片文件
        
        Args:
            dry_run: 是否为试运行模式，True时只报告不删除
            
        Returns:
            清理结果字典
        """
        cleanup_result = {
            'total_checked': 0,
            'invalid_files': [],
            'deleted_files': [],
            'errors': []
        }
        
        try:
            for image_file in self.image_dir.rglob("*"):
                if image_file.is_file() and image_file.suffix.lower() in self.supported_formats:
                    cleanup_result['total_checked'] += 1
                    
                    validation = self.validate_reference_image(image_file)
                    if not validation['is_valid']:
                        cleanup_result['invalid_files'].append(str(image_file))
                        
                        if not dry_run:
                            try:
                                image_file.unlink()
                                cleanup_result['deleted_files'].append(str(image_file))
                                logger.info(f"已删除无效图片: {image_file}")
                            except Exception as e:
                                cleanup_result['errors'].append(f"删除文件失败 {image_file}: {str(e)}")
        
        except Exception as e:
            cleanup_result['errors'].append(f"清理过程中发生异常: {str(e)}")
        
        return cleanup_result