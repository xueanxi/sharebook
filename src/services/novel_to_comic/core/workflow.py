"""
工作流定义
"""

from typing import Dict, Any, List, Optional
import time
from datetime import datetime

from src.services.novel_to_comic.core.segmenter import IntelligentSegmenter
from src.services.novel_to_comic.core.scene_splitter import SceneSplitterAgent
from src.services.novel_to_comic.core.visual_narrative import VisualNarrativeAgent
from src.services.novel_to_comic.models.data_models import (
    TextSegment, Scene, VisualNarrative, ChapterResult, 
    ChapterInfo, BasicStats, ProcessingSummary, ProcessingError
)
from src.services.novel_to_comic.utils.character_manager import CharacterManager
from src.services.novel_to_comic.utils.file_handler import FileHandler
from src.services.novel_to_comic.config.processing_config import OUTPUT_DIR
from src.utils.logging_manager import get_logger, LogCategory

logger = get_logger(__name__, LogCategory.GENERAL)


class NovelToComicWorkflow:
    """小说转漫画工作流"""
    
    def __init__(self):
        self.logger = logger
        self.file_handler = FileHandler()
        
        # 初始化组件
        self.character_manager = CharacterManager()
        self.segmenter = IntelligentSegmenter(self.character_manager)
        self.scene_splitter = SceneSplitterAgent(self.character_manager)
        self.visual_narrative = VisualNarrativeAgent(self.character_manager)
    
    def process_chapter(
        self, 
        chapter_file: str, 
        chapter_title: str, 
        novel_type: str = "玄幻"
    ) -> ChapterResult:
        """
        处理单个章节
        
        Args:
            chapter_file: 章节文件路径
            chapter_title: 章节标题
            novel_type: 小说类型
            
        Returns:
            章节处理结果
        """
        start_time = time.time()
        self.logger.info(f"开始处理章节: {chapter_title}")
        
        errors = []
        
        try:
            # 1. 读取章节内容
            chapter_text = self.file_handler.read_text_file(chapter_file)
            
            # 2. 智能段落分割
            segments = self.segmenter.split_chapter_to_segments(chapter_text)
            
            # 3. 场景分割
            all_scenes = []
            for segment in segments:
                try:
                    context = {
                        "novel_type": novel_type,
                        "chapter_title": chapter_title,
                        "previous_scene_summary": self._get_previous_scene_summary(all_scenes)
                    }
                    scenes = self.scene_splitter.split_segment_to_scenes(segment, context)
                    all_scenes.extend(scenes)
                except Exception as e:
                    error = ProcessingError(
                        error_type="场景分割错误",
                        error_message=str(e),
                        segment_id=segment.segment_id,
                        timestamp=datetime.now().isoformat()
                    )
                    errors.append(error)
                    self.logger.error(f"段落 {segment.segment_id} 场景分割失败: {e}")
            
            # 4. 生成视觉文案
            storyboards = []
            for scene in all_scenes:
                try:
                    context = {
                        "novel_type": novel_type,
                        "chapter_title": chapter_title,
                        "previous_scene_summary": self._get_previous_scene_summary(all_scenes[:all_scenes.index(scene)])
                    }
                    visual_narrative = self.visual_narrative.generate_visual_narrative(scene, context)
                    
                    # 将视觉叙述添加到场景中
                    scene.visual_narrative = visual_narrative
                    storyboards.append(visual_narrative)
                except Exception as e:
                    error = ProcessingError(
                        error_type="视觉叙述生成错误",
                        error_message=str(e),
                        scene_id=scene.scene_id,
                        timestamp=datetime.now().isoformat()
                    )
                    errors.append(error)
                    self.logger.error(f"场景 {scene.scene_id} 视觉叙述生成失败: {e}")
            
            # 5. 创建结果对象
            end_time = time.time()
            processing_time = f"{end_time - start_time:.1f}秒"
            
            chapter_info = ChapterInfo(
                chapter_title=chapter_title,
                chapter_file=chapter_file,
                novel_type=novel_type,
                processing_time=processing_time,
                total_segments=len(segments),
                total_scenes=len(all_scenes),
                total_storyboards=len(storyboards)
            )
            
            basic_stats = BasicStats(
                total_segments=len(segments),
                total_scenes=len(all_scenes),
                total_storyboards=len(storyboards)
            )
            
            # 更新段落中的场景信息
            for segment in segments:
                segment_scenes = [s for s in all_scenes if s.segment_index == segment.segment_index]
                segment.scenes = segment_scenes
            
            result = ChapterResult(
                chapter_info=chapter_info,
                basic_stats=basic_stats,
                segments=segments,
                errors=errors
            )
            
            self.logger.info(f"章节 {chapter_title} 处理完成，耗时: {processing_time}")
            return result
            
        except Exception as e:
            error = ProcessingError(
                error_type="章节处理错误",
                error_message=str(e),
                timestamp=datetime.now().isoformat()
            )
            errors.append(error)
            self.logger.error(f"章节 {chapter_title} 处理失败: {e}")
            
            # 返回失败结果
            end_time = time.time()
            processing_time = f"{end_time - start_time:.1f}秒"
            
            chapter_info = ChapterInfo(
                chapter_title=chapter_title,
                chapter_file=chapter_file,
                novel_type=novel_type,
                processing_time=processing_time,
                total_segments=0,
                total_scenes=0,
                total_storyboards=0
            )
            
            basic_stats = BasicStats(
                total_segments=0,
                total_scenes=0,
                total_storyboards=0
            )
            
            return ChapterResult(
                chapter_info=chapter_info,
                basic_stats=basic_stats,
                segments=[],
                errors=errors
            )
    
    def _get_previous_scene_summary(self, scenes: List[Scene]) -> str:
        """
        获取前一个场景的概要
        
        Args:
            scenes: 场景列表
            
        Returns:
            前一个场景的概要
        """
        if not scenes:
            return "无"
        
        last_scene = scenes[-1]
        return last_scene.scene_description[:100] + "..." if len(last_scene.scene_description) > 100 else last_scene.scene_description
    
    def save_result(self, result: ChapterResult, output_path: Optional[str] = None) -> str:
        """
        保存处理结果
        
        Args:
            result: 章节处理结果
            output_path: 输出路径，如果为None则自动生成
            
        Returns:
            保存的文件路径
        """
        if output_path is None:
            # 生成输出文件名
            chapter_title = result.chapter_info.chapter_title
            file_name = f"{chapter_title}_storyboards.json"
            output_path = f"{OUTPUT_DIR}/{file_name}"
        
        # 确保输出目录存在
        self.file_handler.ensure_directory_exists(OUTPUT_DIR)
        
        # 保存结果
        result.save_to_file(output_path)
        
        self.logger.info(f"结果已保存到: {output_path}")
        return output_path