"""
角色合并变更日志记录模块
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# 导入公用日志管理器
try:
    from ...utils.logging_manager import get_module_logger, LogModule
except ImportError:
    # 如果导入失败，使用基础日志
    import logging
    def get_logger(module):
        return logging.getLogger(module.value)
    
    class LogModule:
        EXTRACTION_CHARACTER = type('obj', (object,), {'value': 'extraction_character'})()


class ChangeLogger:
    """变更日志记录器"""
    
    def __init__(self, log_dir: str = "data/characters/history"):
        """
        初始化变更日志记录器
        
        Args:
            log_dir: 日志目录路径
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger(LogModule.EXTRACTION_CHARACTER)
    
    def log_character_merge(self, 
                          merge_operation: Dict[str, Any], 
                          original_characters: List[Dict[str, Any]], 
                          merged_character: Dict[str, Any]) -> bool:
        """
        记录角色合并操作
        
        Args:
            merge_operation: 合并操作信息
            original_characters: 原始角色列表
            merged_character: 合并后的角色
            
        Returns:
            是否记录成功
        """
        try:
            # 生成日志文件名
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            main_name = merged_character.get("name", merged_character.get("姓名", "unknown"))
            
            self.logger.info(f"记录角色合并操作: {main_name}, 合并了 {len(original_characters)} 个角色")
            # 创建日志记录
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "operation_type": "character_merge",
                "merge_operation": merge_operation,
                "original_characters": original_characters,
                "merged_character": merged_character,
                "changes_summary": self._generate_changes_summary(original_characters, merged_character)
            }
            log_filename = f"merge_{main_name}_{timestamp_str}.json"
            log_filepath = self.log_dir / log_filename
            
            # 写入日志文件
            with open(log_filepath, 'w', encoding='utf-8') as f:
                json.dump(log_entry, f, ensure_ascii=False, indent=2)
            
            # 同时写入汇总日志
            self._append_to_summary_log(log_entry)
            
            self.logger.info(f"角色合并日志记录成功: {log_filename}")
            return True
        except Exception as e:
            self.logger.error(f"记录角色合并日志失败: {e}")
            return False
    
    def log_character_update(self, 
                           original_character: Dict[str, Any], 
                           updated_character: Dict[str, Any],
                           update_reason: str = "信息更新") -> bool:
        """
        记录角色更新操作
        
        Args:
            original_character: 原始角色信息
            updated_character: 更新后的角色信息
            update_reason: 更新原因
            
        Returns:
            是否记录成功
        """
        try:
            # 创建日志记录
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "operation_type": "character_update",
                "update_reason": update_reason,
                "original_character": original_character,
                "updated_character": updated_character,
                "changes_summary": self._generate_update_changes_summary(original_character, updated_character)
            }
            
            # 生成日志文件名
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = updated_character.get("name", updated_character.get("姓名", "unknown"))
            log_filename = f"update_{name}_{timestamp_str}.json"
            log_filepath = self.log_dir / log_filename
            
            # 写入日志文件
            with open(log_filepath, 'w', encoding='utf-8') as f:
                json.dump(log_entry, f, ensure_ascii=False, indent=2)
            
            # 同时写入汇总日志
            self._append_to_summary_log(log_entry)
            
            self.logger.info(f"角色更新日志记录成功: {log_filename}")
            return True
        except Exception as e:
            self.logger.error(f"记录角色更新日志失败: {e}")
            return False
    
    def _generate_changes_summary(self, original_characters: List[Dict[str, Any]], merged_character: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成合并变更摘要
        
        Args:
            original_characters: 原始角色列表
            merged_character: 合并后的角色
            
        Returns:
            变更摘要
        """
        # 收集所有原始名称
        original_names = []
        original_aliases = []
        for char in original_characters:
            name = char.get("name", char.get("姓名", ""))
            aliases = char.get("aliases", char.get("别名", []))
            if name:
                original_names.append(name)
            if isinstance(aliases, list):
                original_aliases.extend(aliases)
            elif isinstance(aliases, str):
                original_aliases.extend([alias.strip() for alias in aliases.split('|') if alias.strip()])
        
        # 获取合并后的名称和别名
        merged_name = merged_character.get("name", merged_character.get("姓名", ""))
        merged_aliases = merged_character.get("aliases", [])
        if isinstance(merged_aliases, str):
            merged_aliases = [alias.strip() for alias in merged_aliases.split('|') if alias.strip()]
        
        return {
            "merged_from_count": len(original_characters),
            "original_names": original_names,
            "original_aliases": original_aliases,
            "merged_name": merged_name,
            "merged_aliases": merged_aliases,
            "new_aliases_added": list(set(merged_aliases) - set(original_aliases)),
            "duplicate_aliases_removed": list(set(original_aliases) - set(merged_aliases)),
            "merge_reason": merged_character.get("reason", "智能合并")
        }
    
    def _generate_update_changes_summary(self, original_character: Dict[str, Any], updated_character: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成更新变更摘要
        
        Args:
            original_character: 原始角色信息
            updated_character: 更新后的角色信息
            
        Returns:
            变更摘要
        """
        changes = {}
        
        # 比较各个字段
        fields_to_compare = ["性别", "外貌特征", "服装特点", "角色类型", "容貌提示词", "别名"]
        
        for field in fields_to_compare:
            original_value = original_character.get(field, "未知" if field != "容貌提示词" else "")
            updated_value = updated_character.get(field, "未知" if field != "容貌提示词" else "")
            
            if original_value != updated_value:
                changes[field] = {
                    "from": original_value,
                    "to": updated_value
                }
        
        return {
            "name": updated_character.get("name", updated_character.get("姓名", "")),
            "changed_fields": list(changes.keys()),
            "field_changes": changes
        }
    
    def _append_to_summary_log(self, log_entry: Dict[str, Any]):
        """
        追加到汇总日志文件
        
        Args:
            log_entry: 日志条目
        """
        try:
            summary_log_path = self.log_dir / "summary_log.jsonl"
            
            # 写入JSONL格式（每行一个JSON对象）
            with open(summary_log_path, 'a', encoding='utf-8') as f:
                # 只写入关键信息，避免文件过大
                summary_entry = {
                    "timestamp": log_entry["timestamp"],
                    "operation_type": log_entry["operation_type"],
                    "summary": log_entry["changes_summary"]
                }
                
                if log_entry["operation_type"] == "character_merge":
                    summary_entry["merge_reason"] = log_entry["merge_operation"].get("reason", "")
                elif log_entry["operation_type"] == "character_update":
                    summary_entry["update_reason"] = log_entry["update_reason"]
                
                f.write(json.dumps(summary_entry, ensure_ascii=False) + '\n')
            self.logger.debug(f"写入汇总日志: {summary_log_path}")
        except Exception as e:
            self.logger.error(f"写入汇总日志失败: {e}")
    
    def get_merge_history(self, character_name: str = None) -> List[Dict[str, Any]]:
        """
        获取角色合并历史
        
        Args:
            character_name: 角色名称，如果为None则获取所有历史
            
        Returns:
            合并历史列表
        """
        try:
            summary_log_path = self.log_dir / "summary_log.jsonl"
            
            if not summary_log_path.exists():
                return []
            
            history = []
            with open(summary_log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        entry = json.loads(line)
                        if entry["operation_type"] == "character_merge":
                            if character_name is None:
                                history.append(entry)
                            else:
                                # 检查是否涉及指定角色
                                summary = entry["summary"]
                                if (character_name in summary.get("merged_name", "") or
                                    character_name in summary.get("original_names", []) or
                                    character_name in summary.get("original_aliases", []) or
                                    character_name in summary.get("merged_aliases", [])):
                                    history.append(entry)
                    except json.JSONDecodeError:
                        continue
            
            # 按时间戳排序（最新的在前）
            history.sort(key=lambda x: x["timestamp"], reverse=True)
            self.logger.debug(f"获取合并历史记录: {len(history)} 条")
            return history
        except Exception as e:
            self.logger.error(f"获取合并历史失败: {e}")
            return []
    
    def get_character_history(self, character_name: str) -> Dict[str, Any]:
        """
        获取指定角色的完整历史记录
        
        Args:
            character_name: 角色名称
            
        Returns:
            角色历史记录
        """
        try:
            summary_log_path = self.log_dir / "summary_log.jsonl"
            
            if not summary_log_path.exists():
                return {"character": character_name, "history": []}
            
            history = []
            with open(summary_log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        entry = json.loads(line)
                        summary = entry["summary"]
                        
                        # 检查是否涉及指定角色
                        is_relevant = False
                        if entry["operation_type"] == "character_merge":
                            if (character_name in summary.get("merged_name", "") or
                                character_name in summary.get("original_names", []) or
                                character_name in summary.get("original_aliases", []) or
                                character_name in summary.get("merged_aliases", [])):
                                is_relevant = True
                        elif entry["operation_type"] == "character_update":
                            if character_name == summary.get("name", ""):
                                is_relevant = True
                        
                        if is_relevant:
                            history.append(entry)
                    except json.JSONDecodeError:
                        continue
            
            # 按时间戳排序（最新的在前）
            history.sort(key=lambda x: x["timestamp"], reverse=True)
            
            result = {
                "character": character_name,
                "history": history,
                "total_operations": len(history)
            }
            self.logger.debug(f"获取角色历史: {character_name}, 操作数量: {len(history)}")
            return result
        except Exception as e:
            self.logger.error(f"获取角色历史失败: {e}")
            return {"character": character_name, "history": [], "error": str(e)}
