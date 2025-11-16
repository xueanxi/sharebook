"""
并行角色分析节点
"""

import concurrent.futures
from typing import Dict, Any, List
from state import CharacterExtractionState
from utils.llm_utils import LLMUtils


class ParallelCharacterAnalyzer:
    """并行角色分析节点"""
    
    def __init__(self, llm_config_path: str = "config/llm_config.py", extraction_config_path: str = "src/services/extraction_character/config.yaml", max_workers: int = 6):
        """
        初始化并行角色分析节点
        
        Args:
            llm_config_path: LLM配置文件路径
            extraction_config_path: 角色提取配置文件路径
            max_workers: 最大并行worker数
        """
        self.llm_utils = LLMUtils(llm_config_path, extraction_config_path)
        self.max_workers = max_workers
    
    def analyze_characters_parallel(self, state: CharacterExtractionState) -> CharacterExtractionState:
        """
        并行分析角色
        
        Args:
            state: 当前状态
            
        Returns:
            更新后的状态
        """
        try:
            extracted_characters = state.get("extracted_characters", [])
            
            if not extracted_characters:
                state["error"] = "没有需要分析的角色"
                state["all_characters"] = {}
                return state
            
            # 并行分析角色
            analyzed_characters = []
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # 提交所有分析任务
                future_to_character = {
                    executor.submit(
                        self._analyze_single_character,
                        character.get("name", ""),
                        character.get("aliases", [])
                    ): character
                    for character in extracted_characters
                }
                
                # 收集结果
                for future in concurrent.futures.as_completed(future_to_character):
                    character = future_to_character[future]
                    try:
                        analyzed_character = future.result()
                        analyzed_characters.append(analyzed_character)
                    except Exception as e:
                        print(f"角色分析失败 {character.get('name', '')}: {e}")
                        # 创建默认角色信息
                        default_character = {
                            "姓名": character.get("name", ""),
                            "性别": "未知",
                            "外貌特征": "未知",
                            "服装特点": "未知",
                            "角色类型": "其他",
                            "别名": character.get("aliases", [])
                        }
                        analyzed_characters.append(default_character)
            
            # 更新状态
            state["all_characters"] = {
                character.get("姓名", ""): character
                for character in analyzed_characters
            }
            state["error"] = None
            
            return state
        except Exception as e:
            state["error"] = f"并行角色分析失败: {str(e)}"
            state["all_characters"] = {}
            return state
    
    def _analyze_single_character(self, character_name: str, character_aliases: List[str]) -> Dict[str, Any]:
        """
        分析单个角色
        
        Args:
            character_name: 角色名称
            character_aliases: 角色别名列表
            
        Returns:
            角色分析结果
        """
        return self.llm_utils.analyze_character(character_name, character_aliases)
    
    def validate_analyzed_characters(self, state: CharacterExtractionState) -> bool:
        """
        验证分析后的角色是否有效
        
        Args:
            state: 当前状态
            
        Returns:
            角色是否有效
        """
        all_characters = state.get("all_characters", {})
        
        if not isinstance(all_characters, dict):
            return False
        
        # 检查每个角色是否有必要的信息
        for name, character in all_characters.items():
            if not isinstance(character, dict):
                return False
            
            # 检查必要字段
            required_fields = ["姓名", "性别", "外貌特征", "服装特点", "角色类型", "别名"]
            for field in required_fields:
                if field not in character:
                    return False
        
        return True