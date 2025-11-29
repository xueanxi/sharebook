"""
配置文件管理模块
"""

import os
import yaml
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path


class ConfigManager:
    """配置文件管理器"""
    
    def __init__(self, config_path: str):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config = self._load_config()
        # 获取项目根目录
        # 从 src/services/extraction_character/config_manager.py 到项目根目录需要向上4级
        self.project_root = Path(__file__).resolve().parent.parent.parent.parent
    
    def _get_absolute_path(self, relative_path: str) -> str:
        """
        将相对路径转换为绝对路径
        
        Args:
            relative_path: 相对路径
            
        Returns:
            绝对路径
        """
        # 如果已经是绝对路径，直接返回
        if os.path.isabs(relative_path):
            return relative_path
        
        # 转换为绝对路径
        return str(self.project_root / relative_path)
    
    def _load_config(self) -> Dict[str, Any]:
        """
        加载配置文件
        
        Returns:
            配置字典
        """
        if not os.path.exists(self.config_path):
            # 创建默认配置
            default_config = self._create_default_config()
            self._save_config(default_config)
            return default_config
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """
        创建默认配置
        
        Returns:
            默认配置字典
        """
        return {
            'extraction': {
                'progress': {
                    'current_chapter': '',
                    'last_update_time': ''
                },
                'paths': {
                    'novel_path': 'data/cleaned_novel',
                    'csv_path': 'data/characters/characters.csv',
                    'config_path': self.config_path
                },
                'parallel': {
                    'max_analyzer_agents': 6,
                    'max_csv_agents': 6
                },
                'llm': {
                    'config_path': 'sharebook/config/llm_config.py',
                    'temperature': 0.4,
                    'max_tokens': 2000,
                    'timeout': 30
                },
                'error_handling': {
                    'retry_count': 3,
                    'log_errors': True
                }
            }
        }
    
    def _save_config(self, config: Dict[str, Any]) -> bool:
        """
        保存配置文件
        
        Args:
            config: 配置字典
            
        Returns:
            是否保存成功
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # 原子性写入
            temp_path = f"{self.config_path}.tmp"
            with open(temp_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            
            # 原子性替换
            os.replace(temp_path, self.config_path)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def get_config(self) -> Dict[str, Any]:
        """
        获取配置
        
        Returns:
            配置字典
        """
        return self.config
    
    def get_novel_path(self) -> str:
        """获取小说文件目录路径"""
        relative_path = self.config['extraction']['paths']['novel_path']
        return self._get_absolute_path(relative_path)
    
    def get_csv_path(self) -> str:
        """获取CSV文件路径"""
        relative_path = self.config['extraction']['paths']['csv_path']
        return self._get_absolute_path(relative_path)
    
    def get_max_analyzer_agents(self) -> int:
        """获取角色分析最大并行agent数"""
        return self.config['extraction']['parallel']['max_analyzer_agents']
    
    def get_max_csv_agents(self) -> int:
        """获取CSV更新最大并行agent数"""
        return self.config['extraction']['parallel']['max_csv_agents']
    
    def get_llm_config(self) -> Dict[str, Any]:
        """获取LLM配置"""
        llm_config = self.config['extraction']['llm'].copy()
        # 转换LLM配置路径为绝对路径
        if 'config_path' in llm_config:
            llm_config['config_path'] = self._get_absolute_path(llm_config['config_path'])
        return llm_config
    
    def get_retry_count(self) -> int:
        """获取重试次数"""
        return self.config['extraction']['error_handling']['retry_count']
    
    def get_current_chapter(self) -> str:
        """获取当前处理章节"""
        return self.config['extraction']['progress']['current_chapter']
    
    def update_progress(self, current_chapter: str) -> bool:
        """
        更新进度信息
        
        Args:
            current_chapter: 当前章节
            
        Returns:
            是否更新成功
        """
        self.config['extraction']['progress']['current_chapter'] = current_chapter
        self.config['extraction']['progress']['last_update_time'] = datetime.now().isoformat()
        
        return self._save_config(self.config)
    
    def reset_progress(self) -> bool:
        """
        重置进度信息
        
        Returns:
            是否重置成功
        """
        self.config['extraction']['progress']['current_chapter'] = ''
        self.config['extraction']['progress']['last_update_time'] = ''
        
        return self._save_config(self.config)