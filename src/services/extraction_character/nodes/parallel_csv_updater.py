"""
并行CSV更新节点
"""

import concurrent.futures
from typing import Dict, Any, List, Tuple
from state import CharacterExtractionState
from utils.csv_utils import CSVUtils, COLUMNS_ORDER
from utils.llm_utils import LLMUtils
from utils.backup_utils import BackupUtils


class ParallelCSVUpdater:
    """并行CSV更新节点"""
    
    def __init__(self, csv_path: str, llm_config_path: str = "config/llm_config.py", max_workers: int = 6):
        """
        
        初始化并行CSV更新节点
        
        Args:
            csv_path: CSV文件路径
            llm_config_path: LLM配置文件路径
            max_workers: 最大并行worker数
        """
        self.csv_utils = CSVUtils(csv_path)
        self.llm_utils = LLMUtils(llm_config_path)
        self.max_workers = max_workers
    
    def update_csv_parallel(self, state: CharacterExtractionState) -> CharacterExtractionState:
        """
        并行更新CSV文件
        
        Args:
            state: 当前状态
            
        Returns:
            更新后的状态
        """
        try:
            all_characters = state.get("all_characters", {})
            
            if not all_characters:
                state["error"] = "没有需要更新的角色信息"
                return state
            
            # 创建备份
            BackupUtils.create_csv_backup(state.get("csv_path", ""))
            
            # 转换为角色列表
            characters_list = list(all_characters.values())
            
            # 分离新角色和已存在角色
            new_characters, existing_characters = self.csv_utils.find_existing_characters(characters_list)
            
            # 处理新角色（直接添加）
            processed_new_characters = new_characters
            
            # 并行处理已存在角色（需要合并）
            processed_existing_characters = []
            if existing_characters:
                processed_existing_characters = self._merge_existing_characters_parallel(existing_characters)
            
            # 合并所有角色
            all_processed_characters = processed_new_characters + processed_existing_characters
            
            # 更新CSV文件
            success = self.csv_utils.update_characters(all_processed_characters)
            
            if not success:
                state["error"] = "CSV文件更新失败"
                return state
            
            # 更新状态
            state["error"] = None
            
            return state
        except Exception as e:
            state["error"] = f"并行CSV更新失败: {str(e)}"
            return state
    
    def _merge_existing_characters_parallel(self, existing_characters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        并行合并已存在的角色
        
        Args:
            existing_characters: 已存在角色列表
            
        Returns:
            合并后的角色列表
        """
        merged_characters = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有合并任务
            future_to_character = {
                executor.submit(
                    self._merge_single_character,
                    character
                ): character
                for character in existing_characters
            }
            
            # 收集结果
            for future in concurrent.futures.as_completed(future_to_character):
                character = future_to_character[future]
                try:
                    merged_character = future.result()
                    merged_characters.append(merged_character)
                except Exception as e:
                    print(f"角色合并失败 {character.get('姓名', '')}: {e}")
                    # 使用简单合并作为后备
                    existing_info = self.csv_utils.get_character_by_name(character.get("姓名", ""))
                    if existing_info:
                        merged_character = self.csv_utils.merge_character_info(existing_info, character)
                        merged_characters.append(merged_character)
                    else:
                        # 如果找不到已存在信息，直接使用新信息
                        merged_characters.append(character)
        
        return merged_characters
    
    def _merge_single_character(self, new_character: Dict[str, Any]) -> Dict[str, Any]:
        """
        合并单个角色
        
        Args:
            new_character: 新角色信息
            
        Returns:
            合并后的角色信息
        """
        character_name = new_character.get("姓名", "")
        
        if not character_name:
            return new_character
        
        # 获取已存在的角色信息
        existing_info = self.csv_utils.get_character_by_name(character_name)
        
        if not existing_info:
            # 如果角色不存在，直接返回新角色
            return new_character
        
        # 使用LLM合并角色信息
        return self.llm_utils.merge_character_info(existing_info, new_character)
    
    def validate_csv_update(self, state: CharacterExtractionState) -> bool:
        """
        验证CSV更新是否成功
        
        Args:
            state: 当前状态
            
        Returns:
            更新是否成功
        """
        try:
            # 读取更新后的CSV
            data = self.csv_utils.read_csv()
            
            # 检查是否有数据
            if hasattr(data, 'empty'):
                # pandas DataFrame
                if data.empty:
                    return False
            else:
                # 列表或其他类型
                if not data:
                    return False
            
            # 检查数据长度
            if len(data) == 0:
                return False
            
            # 如果是pandas DataFrame，检查列
            if hasattr(data, 'columns'):
                # 检查必要的列是否存在
                required_columns = COLUMNS_ORDER
                for column in required_columns:
                    if column not in data.columns:
                        return False
            else:
                # 如果是列表，检查第一个元素是否有必要的键
                if data and isinstance(data[0], dict):
                    required_keys = COLUMNS_ORDER
                    for key in required_keys:
                        if key not in data[0]:
                            return False
            
            return True
        except Exception as e:
            print(f"CSV更新验证失败: {e}")
            return False