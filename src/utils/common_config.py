"""
通用配置文件管理模块
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path

# 使用 get_common_config 来获取全局单例，不要自己尝试实例化
class CommonConfig:
    """通用配置文件管理器"""

    def __init__(self, config_path: str = None):
        """
        初始化通用配置管理器
        
        Args:
            config_path: 配置文件路径，默认为项目根目录下的common_config.yaml
        """
        if config_path is None:
            # 默认配置文件路径
            project_root = Path(__file__).parent.parent.parent
            config_path = os.path.join(project_root, "src", "common_config.yaml")
        
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
            raise Exception(f"配置文件不存在: {self.config_path}")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            raise Exception(f"加载配置文件失败: {e}")

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

    def get_show_llm_log(self) -> bool:
        """获取是否显示LLM日志"""
        return self.config.get('show_llm_log', True)
    
    def set_show_llm_log(self, show: bool) -> bool:
        """
        设置是否显示LLM日志
        
        Args:
            show: 是否显示LLM日志
            
        Returns:
            是否设置成功
        """
        self.config['show_llm_log'] = show
        return self._save_config(self.config)
    
    def get_llm_config(self) -> Dict[str, Any]:
        """获取LLM配置"""
        return self.config.get('llm', {})
    
    def get_llm_config_path(self) -> str:
        """获取LLM配置文件路径"""
        return self.config.get('llm', {}).get('config_path', '')
    
    def get_llm_max_tokens(self) -> int:
        """获取LLM最大token数"""
        return self.config.get('llm', {}).get('max_tokens', 3000)
    
    def get_llm_temperature(self) -> float:
        """获取LLM温度参数"""
        return self.config.get('llm', {}).get('temperature', 0.4)
    
    def get_llm_timeout(self) -> int:
        """获取LLM超时时间"""
        return self.config.get('llm', {}).get('timeout', 30)
    

    def get_novel_type(self) -> str:
        """获取小说类型"""
        return self.config.get('novel_type', '玄幻修真')
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项
        
        Args:
            key: 配置键，支持点号分隔的嵌套键，如 'llm.timeout'
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """
        设置配置项
        
        Args:
            key: 配置键，支持点号分隔的嵌套键，如 'llm.timeout'
            value: 配置值
            
        Returns:
            是否设置成功
        """
        keys = key.split('.')
        config = self.config
        
        # 导航到最后一级的父级
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 设置值
        config[keys[-1]] = value
        
        return self._save_config(self.config)
    
    def reload(self) -> bool:
        """
        重新加载配置文件
        
        Returns:
            是否加载成功
        """
        self.config = self._load_config()
        return True


# 创建全局配置实例
_global_config = None


def get_common_config(config_path: str = None) -> CommonConfig:
    """
    获取全局配置实例
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置实例
    """
    global _global_config
    
    if _global_config is None:
        _global_config = CommonConfig(config_path)
    
    return _global_config


def reset_common_config():
    """重置全局配置实例"""
    global _global_config
    _global_config = None