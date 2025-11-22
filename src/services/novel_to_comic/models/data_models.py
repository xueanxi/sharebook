"""
数据模型定义
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, TYPE_CHECKING
import json

if TYPE_CHECKING:
    from typing import ForwardRef


@dataclass
class CharacterInfo:
    """角色信息"""
    name: str  # 角色名称
    aliases: List[str] = field(default_factory=list)  # 角色别名列表
    gender: Optional[str] = None  # 角色性别
    appearance: Optional[str] = None  # 角色外貌描述
    clothing: Optional[str] = None  # 角色服装描述
    personality: Optional[str] = None  # 角色性格特点
    role_type: Optional[str] = None  # 角色类型（主角、配角等）


@dataclass
class SegmentMetadata:
    """段落元数据"""
    dialogue_count: int = 0  # 对话数量
    action_count: int = 0  # 动作描述数量
    environment_count: int = 0  # 环境描述数量
    character_mentions: List[str] = field(default_factory=list)  # 提及的角色列表
    previous_segment_summary: str = ""  # 前一段落摘要
    next_segment_preview: str = ""  # 下一段落预览
    segment_index: int = 0  # 段落索引


@dataclass
class TextSegment:
    """文本段落"""
    segment_id: str  # 段落唯一标识符
    segment_index: int  # 段落索引
    text: str  # 段落文本内容
    metadata: SegmentMetadata  # 段落元数据
    scenes: List['Scene'] = field(default_factory=list)  # 包含的场景列表


@dataclass
class SceneCharacter:
    """场景中的角色"""
    name: str  # 角色名称
    appearance: str  # 角色外观描述
    expression: str  # 角色表情
    action: str  # 角色动作
    emotion: str  # 角色情绪


@dataclass
class Scene:
    """场景信息"""
    scene_id: str  # 场景唯一标识符
    scene_description: str  # 场景描述
    environment: str  # 环境描述
    atmosphere: str  # 氛围描述
    time: str  # 时间设定
    characters: List[SceneCharacter]  # 场景中的角色列表
    main_action: str  # 主要动作描述
    emotional_tone: str  # 情感基调
    importance_score: int  # 重要性评分
    visual_suitability: int  # 视觉呈现适合度
    transition_cue: str  # 过渡提示
    segment_index: int  # 所属段落索引
    scene_index_in_segment: int  # 在段落中的场景索引
    visual_narrative: Optional['VisualNarrative'] = None  # 视觉叙述信息


@dataclass
class VisualCharacter:
    """视觉描述中的角色"""
    name: str  # 角色名称
    position: str  # 在画面中的位置
    pose: str  # 姿势描述
    expression: str  # 表情描述
    clothing_details: str  # 服装细节
    action: str  # 动作描述


@dataclass
class Composition:
    """构图信息"""
    shot_type: str  # 镜头类型（远景、特写等）
    angle: str  # 拍摄角度
    layout: str  # 布局方式
    focus: str  # 焦点描述


@dataclass
class Environment:
    """环境信息"""
    background: str  # 背景描述
    atmosphere: str  # 氛围描述
    lighting: str  # 光线描述
    color_scheme: str  # 色彩方案


@dataclass
class Style:
    """风格信息"""
    art_style: str  # 艺术风格
    quality_tags: str  # 质量标签
    additional_details: str  # 附加细节


@dataclass
class Narration:
    """旁白信息"""
    scene_description: str  # 场景的视觉描述，用于漫画画面呈现
    inner_monologue: str  # 角色内心独白，可用于思想泡泡或旁白
    emotional_text: str  # 情感描述文本，用于表达场景的情绪氛围
    transition_text: str  # 场景过渡文本，用于连接不同场景的叙述


@dataclass
class StoryboardSuggestions:
    """分镜建议"""
    panel_type: str  # 面板类型
    dialogue_position: str  # 对话框位置
    effects: str  # 特效描述
    page_layout: str  # 页面布局


@dataclass
class VisualNarrative:
    """视觉叙述信息"""
    visual_description: str  # 视觉描述
    composition: Composition  # 构图信息
    characters: List[VisualCharacter]  # 视觉角色列表
    environment: Environment  # 环境信息
    style: Style  # 风格信息
    narration: Narration  # 旁白信息
    scene_id: str  # 关联的场景ID


@dataclass
class ProcessingError:
    """处理错误信息"""
    error_type: str  # 错误类型
    error_message: str  # 错误消息
    segment_id: Optional[str] = None  # 出错的段落ID
    scene_id: Optional[str] = None  # 出错的场景ID
    timestamp: str = ""  # 错误时间戳
    stack_trace: Optional[str] = None  # 错误堆栈跟踪


@dataclass
class ChapterInfo:
    """章节信息"""
    chapter_title: str  # 章节标题
    chapter_file: str  # 章节文件路径
    novel_type: str  # 小说类型
    processing_time: str  # 处理时间
    total_segments: int  # 总段落数
    total_scenes: int  # 总场景数
    total_storyboards: int  # 总故事板数


@dataclass
class BasicStats:
    """基础统计信息"""
    total_segments: int  # 总段落数
    total_scenes: int  # 总场景数
    total_storyboards: int  # 总故事板数


@dataclass
class ProcessingSummary:
    """处理摘要"""
    success: bool  # 是否成功
    total_segments: int  # 总段落数
    total_scenes: int  # 总场景数
    total_storyboards: int  # 总故事板数
    processing_time: str  # 处理时间
    error_count: int  # 错误数量


@dataclass
class ChapterResult:
    """章节处理结果"""
    chapter_info: ChapterInfo  # 章节信息
    basic_stats: BasicStats  # 基础统计信息
    scenes: List[Scene]  # 场景列表
    errors: List[ProcessingError] = field(default_factory=list)  # 错误列表
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self, default=lambda o: o.__dict__, ensure_ascii=False, indent=2)
    
    def save_to_file(self, file_path: str):
        """保存到文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(self.to_json())


@dataclass
class ProcessingResult:
    """处理结果"""
    success: bool  # 是否成功
    output_path: Optional[str] = None  # 输出路径
    errors: List[str] = field(default_factory=list)  # 错误列表
    processing_summary: Optional[ProcessingSummary] = None  # 处理摘要