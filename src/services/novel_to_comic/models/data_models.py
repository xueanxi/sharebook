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
    name: str
    aliases: List[str] = field(default_factory=list)
    gender: Optional[str] = None
    appearance: Optional[str] = None
    clothing: Optional[str] = None
    personality: Optional[str] = None
    role_type: Optional[str] = None


@dataclass
class SegmentMetadata:
    """段落元数据"""
    dialogue_count: int = 0
    action_count: int = 0
    environment_count: int = 0
    character_mentions: List[str] = field(default_factory=list)
    previous_segment_summary: str = ""
    next_segment_preview: str = ""
    segment_index: int = 0


@dataclass
class TextSegment:
    """文本段落"""
    segment_id: str
    segment_index: int
    text: str
    metadata: SegmentMetadata
    scenes: List['Scene'] = field(default_factory=list)


@dataclass
class SceneCharacter:
    """场景中的角色"""
    name: str
    appearance: str
    expression: str
    action: str
    emotion: str


@dataclass
class Scene:
    """场景信息"""
    scene_id: str
    scene_description: str
    environment: str
    atmosphere: str
    time: str
    characters: List[SceneCharacter]
    main_action: str
    emotional_tone: str
    importance_score: int
    visual_suitability: int
    transition_cue: str
    segment_index: int
    scene_index_in_segment: int
    visual_narrative: Optional['VisualNarrative'] = None


@dataclass
class VisualCharacter:
    """视觉描述中的角色"""
    name: str
    position: str
    pose: str
    expression: str
    clothing_details: str
    action: str


@dataclass
class Composition:
    """构图信息"""
    shot_type: str
    angle: str
    layout: str
    focus: str


@dataclass
class Environment:
    """环境信息"""
    background: str
    atmosphere: str
    lighting: str
    color_scheme: str


@dataclass
class Style:
    """风格信息"""
    art_style: str
    quality_tags: str
    additional_details: str


@dataclass
class Narration:
    """旁白信息"""
    scene_description: str
    inner_monologue: str
    emotional_text: str
    transition_text: str


@dataclass
class StoryboardSuggestions:
    """分镜建议"""
    panel_type: str
    dialogue_position: str
    effects: str
    page_layout: str


@dataclass
class VisualNarrative:
    """视觉叙述信息"""
    visual_description: str
    composition: Composition
    characters: List[VisualCharacter]
    environment: Environment
    style: Style
    narration: Narration
    storyboard_suggestions: StoryboardSuggestions
    scene_id: str


@dataclass
class ProcessingError:
    """处理错误信息"""
    error_type: str
    error_message: str
    segment_id: Optional[str] = None
    scene_id: Optional[str] = None
    timestamp: str = ""
    stack_trace: Optional[str] = None


@dataclass
class ChapterInfo:
    """章节信息"""
    chapter_title: str
    chapter_file: str
    novel_type: str
    processing_time: str
    total_segments: int
    total_scenes: int
    total_storyboards: int


@dataclass
class BasicStats:
    """基础统计信息"""
    total_segments: int
    total_scenes: int
    total_storyboards: int


@dataclass
class ProcessingSummary:
    """处理摘要"""
    success: bool
    total_segments: int
    total_scenes: int
    total_storyboards: int
    processing_time: str
    error_count: int


@dataclass
class ChapterResult:
    """章节处理结果"""
    chapter_info: ChapterInfo
    basic_stats: BasicStats
    segments: List[TextSegment]
    errors: List[ProcessingError] = field(default_factory=list)
    
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
    success: bool
    output_path: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    processing_summary: Optional[ProcessingSummary] = None