"""
角色提取工作流状态定义
"""

from typing import TypedDict, List, Dict, Optional


class CharacterExtractionState(TypedDict):
    """角色提取工作流状态"""
    current_chapter: str  # 当前处理的章节文件名
    chapter_content: str  # 章节内容
    extracted_characters: List[Dict]  # 当前章节提取的角色
    all_characters: Dict[str, Dict]  # 所有角色信息（以姓名为键）
    processed_chapters: List[str]  # 已处理的章节列表
    csv_path: str  # CSV文件路径
    error: Optional[str]  # 错误信息
    config_path: str  # 配置文件路径
    character_aliases: Dict[str, List[str]]  # 角色别名映射（主名称到别名列表）
    is_completed: bool  # 是否完成所有章节处理