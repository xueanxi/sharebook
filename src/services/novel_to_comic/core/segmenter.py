"""
智能段落分割器
"""

import uuid
from typing import List, Dict, Any

from src.services.novel_to_comic.config.processing_config import SEGMENT_MAX_LENGTH, SEGMENT_MIN_LENGTH
from src.services.novel_to_comic.models.data_models import TextSegment, SegmentMetadata
from src.services.novel_to_comic.utils.text_processor import TextProcessor
from src.services.novel_to_comic.utils.character_manager import CharacterManager
from src.utils.logging_manager import get_module_logger, LogModule

logger = get_module_logger(LogModule.NOVEL_TO_COMIC)


class IntelligentSegmenter:
    """智能段落分割器"""
    
    def __init__(self, character_manager: CharacterManager):
        self.character_manager = character_manager
        self.text_processor = TextProcessor()
        self.logger = logger
    
    def split_chapter_to_segments(self, chapter_text: str) -> List[TextSegment]:
        """
        将章节文本分割为段落
        
        Args:
            chapter_text: 章节文本
            
        Returns:
            分割后的段落列表
        """
        self.logger.info("开始分割章节文本")
        
        # 1. 预处理文本
        normalized_text = self.text_processor.normalize_text(chapter_text)
        
        # 2. 按自然段落分割
        paragraphs = self.text_processor.split_by_paragraphs(normalized_text)
        
        if not paragraphs:
            self.logger.warning("没有找到有效段落")
            return []
        
        # 3. 分析段落并合并/分割
        segments = self._process_paragraphs(paragraphs)
        
        # 4. 添加上下文信息
        self._add_context_info(segments)
        
        self.logger.info(f"章节分割完成，共生成 {len(segments)} 个段落")
        return segments
    
    def _process_paragraphs(self, paragraphs: List[str]) -> List[TextSegment]:
        """
        处理段落，根据长度和内容类型进行合并或分割
        
        Args:
            paragraphs: 自然段落列表
            
        Returns:
            处理后的段落列表
        """
        segments = []
        current_segment_text = ""
        current_metadata = SegmentMetadata()
        segment_index = 0
        
        all_character_names = self.character_manager.get_all_character_names()
        
        for i, paragraph in enumerate(paragraphs):
            # 分析段落类型和内容
            paragraph_type = self.text_processor.analyze_paragraph_type(paragraph)
            content_counts = self.text_processor.count_content_types(paragraph)
            character_mentions = self.text_processor.extract_character_mentions(paragraph, all_character_names)
            
            # 检查是否需要开始新段落
            should_start_new_segment = self._should_start_new_segment(
                current_segment_text, 
                paragraph, 
                paragraph_type,
                current_metadata
            )
            
            if should_start_new_segment and current_segment_text.strip():
                # 保存当前段落
                segment = self._create_segment(
                    current_segment_text, 
                    current_metadata, 
                    segment_index
                )
                segments.append(segment)
                segment_index += 1
                
                # 重置当前段落
                current_segment_text = paragraph
                current_metadata = self._create_metadata(
                    paragraph, 
                    paragraph_type, 
                    content_counts, 
                    character_mentions,
                    segment_index
                )
            else:
                # 合并到当前段落
                if current_segment_text:
                    current_segment_text += "\n\n" + paragraph
                else:
                    current_segment_text = paragraph
                
                # 更新元数据
                self._update_metadata(current_metadata, content_counts, character_mentions)
        
        # 添加最后一个段落
        if current_segment_text.strip():
            segment = self._create_segment(
                current_segment_text, 
                current_metadata, 
                segment_index
            )
            segments.append(segment)
        
        return segments
    
    def _should_start_new_segment(
        self, 
        current_text: str, 
        new_paragraph: str,
        paragraph_type: str,
        current_metadata: SegmentMetadata
    ) -> bool:
        """
        判断是否应该开始新段落
        
        Args:
            current_text: 当前段落文本
            new_paragraph: 新段落文本
            paragraph_type: 新段落类型
            current_metadata: 当前段落元数据
            
        Returns:
            是否开始新段落
        """
        # 如果当前段落为空，不需要开始新段落
        if not current_text.strip():
            return False
        
        # 检查长度限制
        combined_length = len(current_text + "\n\n" + new_paragraph)
        if combined_length > SEGMENT_MAX_LENGTH:
            return True
        
        # 如果当前段落还没达到最小长度，优先合并
        if len(current_text) < SEGMENT_MIN_LENGTH:
            return False
        
        # 如果当前段落已经达到合理长度，检查是否需要分割
        if len(current_text) >= SEGMENT_MIN_LENGTH * 1.5:  # 超过最小长度1.5倍
            current_type = self._get_dominant_type(current_metadata)
            
            # 只有在内容类型发生显著变化时才分割
            if current_type != paragraph_type:
                # 对话段落比较特殊，如果是连续对话，倾向于合并
                if current_type == "dialogue" and paragraph_type == "dialogue":
                    return False
                # 如果是环境描述转动作，可以合并
                elif current_type == "environment" and paragraph_type == "action":
                    return False
                # 其他类型变化考虑分割
                else:
                    return True
        
        return False
    
    def _get_dominant_type(self, metadata: SegmentMetadata) -> str:
        """
        获取段落的主要类型
        
        Args:
            metadata: 段落元数据
            
        Returns:
            主要类型
        """
        type_counts = {
            "dialogue": metadata.dialogue_count,
            "action": metadata.action_count,
            "environment": metadata.environment_count
        }
        
        return max(type_counts.items(), key=lambda x: x[1])[0]
    
    def _create_metadata(
        self, 
        paragraph: str, 
        paragraph_type: str,
        content_counts: Dict[str, int],
        character_mentions: List[str],
        segment_index: int
    ) -> SegmentMetadata:
        """
        创建段落元数据
        
        Args:
            paragraph: 段落文本
            paragraph_type: 段落类型
            content_counts: 内容统计
            character_mentions: 角色提及
            segment_index: 段落索引
            
        Returns:
            段落元数据
        """
        return SegmentMetadata(
            dialogue_count=content_counts.get("dialogue_count", 0),
            action_count=content_counts.get("action_count", 0),
            environment_count=content_counts.get("environment_count", 0),
            character_mentions=character_mentions,
            segment_index=segment_index
        )
    
    def _update_metadata(
        self, 
        metadata: SegmentMetadata, 
        content_counts: Dict[str, int],
        character_mentions: List[str]
    ) -> None:
        """
        更新段落元数据
        
        Args:
            metadata: 要更新的元数据
            content_counts: 内容统计
            character_mentions: 角色提及
        """
        metadata.dialogue_count += content_counts.get("dialogue_count", 0)
        metadata.action_count += content_counts.get("action_count", 0)
        metadata.environment_count += content_counts.get("environment_count", 0)
        
        # 合并角色提及，去重
        all_mentions = list(set(metadata.character_mentions + character_mentions))
        metadata.character_mentions = all_mentions
    
    def _create_segment(
        self, 
        text: str, 
        metadata: SegmentMetadata, 
        segment_index: int
    ) -> TextSegment:
        """
        创建文本段落对象
        
        Args:
            text: 段落文本
            metadata: 段落元数据
            segment_index: 段落索引
            
        Returns:
            文本段落对象
        """
        segment_id = str(uuid.uuid4())
        metadata.segment_index = segment_index
        
        return TextSegment(
            segment_id=segment_id,
            segment_index=segment_index,
            text=text.strip(),
            metadata=metadata
        )
    
    def _add_context_info(self, segments: List[TextSegment]) -> None:
        """
        添加上下文信息
        
        Args:
            segments: 段落列表
        """
        for i, segment in enumerate(segments):
            # 前一段落概要
            if i > 0:
                prev_segment = segments[i - 1]
                segment.metadata.previous_segment_summary = self.text_processor.get_text_summary(
                    prev_segment.text, 50
                )
            
            # 下一段落预览
            if i < len(segments) - 1:
                next_segment = segments[i + 1]
                segment.metadata.next_segment_preview = self.text_processor.get_text_summary(
                    next_segment.text, 50
                )
