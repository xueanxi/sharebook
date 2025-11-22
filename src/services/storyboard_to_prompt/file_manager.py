"""
文件管理器类
负责文件读写操作和目录管理
"""
import os
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import yaml

logger = logging.getLogger(__name__)


class FileManager:
    """文件管理器类"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化文件管理器
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认配置
        """
        self.config = self._load_config(config_path)
        self.storyboard_dir = Path(self.config['storyboard_to_prompt']['paths']['storyboard_dir'])
        self.output_dir = Path(self.config['storyboard_to_prompt']['paths']['output_dir'])
        
        # 确保输出目录存在
        self._ensure_directory_exists(self.output_dir)
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            if config_path is None:
                # 使用默认配置文件路径
                current_dir = Path(__file__).parent
                config_path = current_dir / 'config.yaml'
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            logger.info(f"成功加载配置文件: {config_path}")
            return config
            
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            # 返回默认配置
            return {
                'storyboard_to_prompt': {
                    'paths': {
                        'storyboard_dir': 'data/storyboards',
                        'output_dir': 'data/prompts'
                    }
                }
            }
    
    def _ensure_directory_exists(self, directory: Path):
        """确保目录存在"""
        try:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"确保目录存在: {directory}")
        except Exception as e:
            logger.error(f"创建目录失败 {directory}: {str(e)}")
            raise
    
    def get_storyboard_files(self) -> List[Path]:
        """
        获取所有故事板文件列表
        
        Returns:
            故事板文件路径列表，按章节顺序排序
        """
        try:
            if not self.storyboard_dir.exists():
                logger.warning(f"故事板目录不存在: {self.storyboard_dir}")
                return []
            
            # 获取所有JSON文件
            storyboard_files = list(self.storyboard_dir.glob('*_storyboards.json'))
            
            # 按章节顺序排序
            storyboard_files = self._sort_chapter_files(storyboard_files)
            
            logger.info(f"找到 {len(storyboard_files)} 个故事板文件")
            return storyboard_files
            
        except Exception as e:
            logger.error(f"获取故事板文件列表失败: {str(e)}")
            return []
    
    def _sort_chapter_files(self, files: List[Path]) -> List[Path]:
        """
        按章节顺序排序文件
        
        Args:
            files: 文件路径列表
            
        Returns:
            排序后的文件路径列表
        """
        try:
            # 导入章节排序工具
            from src.utils.text_processing.chapter_sorter import ChapterSorter
            
            # 转换为字符串路径列表
            file_paths = [str(path) for path in files]
            
            # 使用ChapterSorter进行排序
            sorted_paths = ChapterSorter.sort_chapter_files(file_paths)
            
            # 转换回Path对象
            return [Path(path) for path in sorted_paths]
            
        except Exception as e:
            logger.error(f"使用ChapterSorter排序失败: {str(e)}")
            # 降级到简单的文件名排序
            return sorted(files, key=lambda x: x.name)
    
    def load_storyboard_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        加载故事板文件
        
        Args:
            file_path: 故事板文件路径
            
        Returns:
            故事板数据字典，如果加载失败返回None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                storyboard_data = json.load(f)
            
            logger.info(f"成功加载故事板文件: {file_path}")
            return storyboard_data
            
        except Exception as e:
            logger.error(f"加载故事板文件失败 {file_path}: {str(e)}")
            return None
    
    def save_prompts(self, chapter_info: Dict[str, Any], prompts: List[Dict[str, Any]], 
                     output_path: Optional[Path] = None) -> bool:
        """
        保存提示词到JSON文件
        
        Args:
            chapter_info: 章节信息
            prompts: 提示词列表
            output_path: 输出文件路径，如果为None则自动生成
            
        Returns:
            保存是否成功
        """
        try:
            # 生成输出文件路径
            if output_path is None:
                chapter_title = chapter_info.get('chapter_title', '未知章节')
                output_filename = f"{chapter_title}_prompts.json"
                output_path = self.output_dir / output_filename
            
            # 构建输出数据
            output_data = {
                "chapter_info": {
                    **chapter_info,
                    "total_prompts": len(prompts)
                },
                "basic_stats": {
                    **chapter_info.get('basic_stats', {}),
                    "total_prompts": len(prompts)
                },
                "prompts": prompts
            }
            
            # 确保输出目录存在
            self._ensure_directory_exists(output_path.parent)
            
            # 保存文件
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"成功保存提示词文件: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存提示词文件失败: {str(e)}")
            return False
    
    def file_exists(self, file_path: Path) -> bool:
        """
        检查文件是否存在
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件是否存在
        """
        return file_path.exists() and file_path.is_file()
    
    def get_output_file_path(self, chapter_title: str) -> Path:
        """
        获取输出文件路径
        
        Args:
            chapter_title: 章节标题
            
        Returns:
            输出文件路径
        """
        output_filename = f"{chapter_title}_prompts.json"
        return self.output_dir / output_filename
    
    def create_backup(self, file_path: Path) -> Optional[Path]:
        """
        创建文件备份
        
        Args:
            file_path: 要备份的文件路径
            
        Returns:
            备份文件路径，如果备份失败返回None
        """
        try:
            if not self.file_exists(file_path):
                logger.warning(f"文件不存在，无法备份: {file_path}")
                return None
            
            # 创建备份目录
            backup_dir = self.output_dir / 'backup'
            self._ensure_directory_exists(backup_dir)
            
            # 生成备份文件名
            import datetime
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"{file_path.stem}_{timestamp}{file_path.suffix}"
            backup_path = backup_dir / backup_filename
            
            # 复制文件
            import shutil
            shutil.copy2(file_path, backup_path)
            
            logger.info(f"成功创建备份: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"创建备份失败: {str(e)}")
            return None
    
    def clean_old_backups(self, keep_count: int = 10):
        """
        清理旧备份文件
        
        Args:
            keep_count: 保留的备份文件数量
        """
        try:
            backup_dir = self.output_dir / 'backup'
            if not backup_dir.exists():
                return
            
            # 获取所有备份文件
            backup_files = list(backup_dir.glob('*_prompts_*.json'))
            
            # 按修改时间排序
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # 删除多余的备份
            for backup_file in backup_files[keep_count:]:
                backup_file.unlink()
                logger.debug(f"删除旧备份: {backup_file}")
            
            logger.info(f"清理完成，保留最新 {keep_count} 个备份文件")
            
        except Exception as e:
            logger.error(f"清理备份文件失败: {str(e)}")
    
    def get_file_stats(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        获取文件统计信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件统计信息字典，如果获取失败返回None
        """
        try:
            if not self.file_exists(file_path):
                return None
            
            stat = file_path.stat()
            return {
                'file_size': stat.st_size,
                'modified_time': stat.st_mtime,
                'created_time': stat.st_ctime,
                'file_path': str(file_path)
            }
            
        except Exception as e:
            logger.error(f"获取文件统计信息失败: {str(e)}")
            return None