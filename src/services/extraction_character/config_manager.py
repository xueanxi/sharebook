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
                    'processed_chapters': [],
                    'last_update_time': ''
                },
                'paths': {
                    'novel_path': 'D:/work/code/python/sharebook2/data/cleaned_novel',
                    'csv_path': 'D:/work/code/python/sharebook2/data/characters/characters.csv',
                    'config_path': self.config_path
                },
                'parallel': {
                    'max_analyzer_agents': 6,
                    'max_csv_agents': 6
                },
                'llm': {
                    'config_path': 'D:/work/code/python/sharebook2/config/llm_config.py',
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
        return self.config['extraction']['paths']['novel_path']
    
    def get_csv_path(self) -> str:
        """获取CSV文件路径"""
        return self.config['extraction']['paths']['csv_path']
    
    def get_max_analyzer_agents(self) -> int:
        """获取角色分析最大并行agent数"""
        return self.config['extraction']['parallel']['max_analyzer_agents']
    
    def get_max_csv_agents(self) -> int:
        """获取CSV更新最大并行agent数"""
        return self.config['extraction']['parallel']['max_csv_agents']
    
    def get_llm_config(self) -> Dict[str, Any]:
        """获取LLM配置"""
        return self.config['extraction']['llm']
    
    def get_retry_count(self) -> int:
        """获取重试次数"""
        return self.config['extraction']['error_handling']['retry_count']
    
    def get_processed_chapters(self) -> List[str]:
        """获取已处理章节列表"""
        return self.config['extraction']['progress']['processed_chapters']
    
    def get_current_chapter(self) -> str:
        """获取当前处理章节"""
        return self.config['extraction']['progress']['current_chapter']
    
    def update_progress(self, current_chapter: str, processed_chapters: List[str]) -> bool:
        """
        更新进度信息
        
        Args:
            current_chapter: 当前章节
            processed_chapters: 已处理章节列表
            
        Returns:
            是否更新成功
        """
        self.config['extraction']['progress']['current_chapter'] = current_chapter
        self.config['extraction']['progress']['processed_chapters'] = processed_chapters
        self.config['extraction']['progress']['last_update_time'] = datetime.now().isoformat()
        
        return self._save_config(self.config)
    
    def reset_progress(self) -> bool:
        """
        重置进度信息
        
        Returns:
            是否重置成功
        """
        self.config['extraction']['progress']['current_chapter'] = ''
        self.config['extraction']['progress']['processed_chapters'] = []
        self.config['extraction']['progress']['last_update_time'] = ''
        
        return self._save_config(self.config)