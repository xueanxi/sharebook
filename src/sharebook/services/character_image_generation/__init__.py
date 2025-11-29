"""
角色图片生成服务模块

该模块提供基于角色数据生成图片的功能, 支持从CSV文件读取角色信息,
使用ComfyUI生成角色图片, 并按照角色姓名进行分类存储.
"""

from .character_image_generator import CharacterImageGenerator

__all__ = ["CharacterImageGenerator"]