"""
角色卡提取服务模块
提供角色卡生成和管理的功能
"""

from .main import extract_character_cards, batch_extract_character_cards

__all__ = [
    "extract_character_cards",
    "batch_extract_character_cards"
]