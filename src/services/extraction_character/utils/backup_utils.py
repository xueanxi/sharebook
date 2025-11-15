"""
备份工具模块
"""

import os
import shutil
from datetime import datetime
from typing import List
from pathlib import Path


class BackupUtils:
    """备份工具类"""
    
    @staticmethod
    def create_csv_backup(csv_path: str) -> str:
        """
        创建CSV文件的备份
        
        Args:
            csv_path: CSV文件路径
            
        Returns:
            备份文件路径，失败返回空字符串
        """
        try:
            if not os.path.exists(csv_path):
                return ""
            
            # 获取当前时间戳
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 构建备份文件名
            dir_name = os.path.dirname(csv_path)
            base_name = os.path.basename(csv_path)
            name, ext = os.path.splitext(base_name)
            
            # 创建history子目录路径
            history_dir = os.path.join(dir_name, "history")
            os.makedirs(history_dir, exist_ok=True)
            
            # 备份文件保存到history子目录
            backup_filename = f"{name}_backup_{timestamp}{ext}"
            backup_path = os.path.join(history_dir, backup_filename)
            
            # 创建备份
            shutil.copy2(csv_path, backup_path)
            
            # 清理旧备份（保留最近5个）
            BackupUtils._cleanup_old_backups(history_dir, name, ext, 5)
            
            return backup_path
        except Exception as e:
            print(f"CSV备份创建失败: {e}")
            return ""
    
    @staticmethod
    def create_config_backup(config_path: str) -> str:
        """
        创建配置文件的备份
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            备份文件路径，失败返回空字符串
        """
        try:
            if not os.path.exists(config_path):
                return ""
            
            # 获取当前时间戳
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 构建备份文件名
            dir_name = os.path.dirname(config_path)
            base_name = os.path.basename(config_path)
            name, ext = os.path.splitext(base_name)
            
            # 创建history子目录路径
            history_dir = os.path.join(dir_name, "history")
            os.makedirs(history_dir, exist_ok=True)
            
            # 备份文件保存到history子目录
            backup_filename = f"{name}_backup_{timestamp}{ext}"
            backup_path = os.path.join(history_dir, backup_filename)
            
            # 创建备份
            shutil.copy2(config_path, backup_path)
            
            # 清理旧备份（保留最近5个）
            BackupUtils._cleanup_old_backups(history_dir, name, ext, 5)
            
            return backup_path
        except Exception as e:
            print(f"配置文件备份创建失败: {e}")
            return ""
    
    @staticmethod
    def _cleanup_old_backups(directory: str, base_name: str, extension: str, keep_count: int):
        """
        清理旧备份文件
        
        Args:
            directory: 目录路径
            base_name: 基础文件名
            extension: 文件扩展名
            keep_count: 保留的备份数量
        """
        try:
            # 查找所有备份文件
            backup_pattern = f"{base_name}_backup_*{extension}"
            backup_files = []
            
            for file_name in os.listdir(directory):
                if file_name.startswith(f"{base_name}_backup_") and file_name.endswith(extension):
                    file_path = os.path.join(directory, file_name)
                    backup_files.append((file_path, os.path.getmtime(file_path)))
            
            # 按修改时间排序（最新的在前）
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # 删除多余的备份
            for file_path, _ in backup_files[keep_count:]:
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"删除备份文件失败: {file_path}, 错误: {e}")
        except Exception as e:
            print(f"清理旧备份失败: {e}")
    
    @staticmethod
    def restore_from_backup(backup_path: str, target_path: str) -> bool:
        """
        从备份恢复文件
        
        Args:
            backup_path: 备份文件路径
            target_path: 目标文件路径
            
        Returns:
            是否恢复成功
        """
        try:
            if not os.path.exists(backup_path):
                print(f"备份文件不存在: {backup_path}")
                return False
            
            # 确保目标目录存在
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            
            # 恢复文件
            shutil.copy2(backup_path, target_path)
            return True
        except Exception as e:
            print(f"从备份恢复文件失败: {e}")
            return False
    
    @staticmethod
    def list_backups(directory: str, base_name: str, extension: str) -> List[str]:
        """
        列出所有备份文件
        
        Args:
            directory: 目录路径
            base_name: 基础文件名
            extension: 文件扩展名
            
        Returns:
            备份文件路径列表
        """
        try:
            # 检查history子目录是否存在
            history_dir = os.path.join(directory, "history")
            if not os.path.exists(history_dir):
                return []
                
            backup_files = []
            
            for file_name in os.listdir(history_dir):
                if file_name.startswith(f"{base_name}_backup_") and file_name.endswith(extension):
                    file_path = os.path.join(history_dir, file_name)
                    backup_files.append(file_path)
            
            # 按修改时间排序（最新的在前）
            backup_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            return backup_files
        except Exception as e:
            print(f"列出备份文件失败: {e}")
            return []