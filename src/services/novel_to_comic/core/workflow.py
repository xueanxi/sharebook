"""
工作流定义
"""

from typing import Dict, Any, List, Optional
import time
from datetime import datetime

from src.services.novel_to_comic.core.segmenter import IntelligentSegmenter
from src.services.novel_to_comic.core.scene_splitter import SceneSplitterAgent
from src.services.novel_to_comic.core.visual_narrative import VisualNarrativeAgent
from src.services.novel_to_comic.core.parallel_scene_splitter import ParallelSceneSplitterWorkflow
from src.services.novel_to_comic.core.parallel_visual_narrative import ParallelVisualNarrativeWorkflow
from src.services.novel_to_comic.models.data_models import (
    TextSegment, Scene, VisualNarrative, ChapterResult, 
    ChapterInfo, BasicStats, ProcessingSummary, ProcessingError
)
from src.services.novel_to_comic.utils.character_manager import CharacterManager
from src.services.novel_to_comic.utils.file_handler import FileHandler
from src.services.novel_to_comic.config.processing_config import (
    OUTPUT_DIR, ENABLE_PARALLEL_SCENE_SPLITTING, 
    MAX_SCENE_SPLITTING_CONCURRENT
)
from src.utils.logging_manager import get_logger, LogCategory

logger = get_logger(__name__, LogCategory.GENERAL)


class NovelToComicWorkflow:
    """小说转漫画工作流"""
    
    def __init__(self, enable_parallel: Optional[bool] = None):
        self.logger = logger
        self.file_handler = FileHandler()
        
        # 确定是否启用并行处理
        if enable_parallel is None:
            self.enable_parallel = ENABLE_PARALLEL_SCENE_SPLITTING
        else:
            self.enable_parallel = enable_parallel
            
        # 初始化组件
        self.character_manager = CharacterManager()
        self.segmenter = IntelligentSegmenter(self.character_manager)
        self.scene_splitter = SceneSplitterAgent(self.character_manager)
        self.visual_narrative = VisualNarrativeAgent(self.character_manager)
        
        # 如果启用并行处理，初始化并行工作流
        if self.enable_parallel:
            self.parallel_scene_splitter = ParallelSceneSplitterWorkflow(
                self.character_manager, 
                MAX_SCENE_SPLITTING_CONCURRENT
            )
            self.parallel_visual_workflow = ParallelVisualNarrativeWorkflow(
                self.character_manager, 
                MAX_SCENE_SPLITTING_CONCURRENT
            )
            self.logger.info(f"并行场景分割已启用，固定 {MAX_SCENE_SPLITTING_CONCURRENT} 个工作者")
            self.logger.info(f"并行视觉生成已启用，固定 {MAX_SCENE_SPLITTING_CONCURRENT} 个工作者")
        else:
            self.parallel_scene_splitter = None
            self.parallel_visual_workflow = None
            self.logger.info("使用顺序场景分割和视觉生成模式")
    
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
            
            # 3. 场景分割（支持并行处理）
            all_scenes = []
            if self.enable_parallel and len(segments) > 1:
                # 使用并行处理
                self.logger.info(f"使用并行模式处理 {len(segments)} 个段落")
                try:
                    context = {
                        "novel_type": novel_type,
                        "chapter_title": chapter_title
                    }
                    all_scenes = self.parallel_scene_splitter.process_segments_parallel(segments, context)
                except Exception as e:
                    self.logger.error(f"并行场景分割失败，回退到顺序模式: {e}")
                    # 回退到顺序处理
                    all_scenes = self._process_segments_sequentially(segments, novel_type, chapter_title, errors)
            else:
                # 使用顺序处理
                self.logger.info(f"使用顺序模式处理 {len(segments)} 个段落")
                all_scenes = self._process_segments_sequentially(segments, novel_type, chapter_title, errors)
            
            # 4. 生成视觉文案（支持并行处理）
            storyboards = []
            if self.enable_parallel and len(all_scenes) > 1:
                # 使用并行处理
                self.logger.info(f"使用并行模式处理 {len(all_scenes)} 个场景的视觉生成")
                try:
                    context = {
                        "novel_type": novel_type,
                        "chapter_title": chapter_title
                    }
                    visual_narratives = self.parallel_visual_workflow.process_scenes_parallel(all_scenes, context)
                    
                    # 将视觉叙述添加到场景中
                    for i, visual_narrative in enumerate(visual_narratives):
                        # 找到对应的场景
                        scene_id = visual_narrative.scene_id
                        for scene in all_scenes:
                            if scene.scene_id == scene_id:
                                scene.visual_narrative = visual_narrative
                                storyboards.append(visual_narrative)
                                break
                except Exception as e:
                    self.logger.error(f"并行视觉生成失败，回退到顺序模式: {e}")
                    # 回退到顺序处理
                    storyboards = self._process_scenes_sequentially(all_scenes, novel_type, chapter_title, errors)
            else:
                # 使用顺序处理
                self.logger.info(f"使用顺序模式处理 {len(all_scenes)} 个场景的视觉生成")
                storyboards = self._process_scenes_sequentially(all_scenes, novel_type, chapter_title, errors)
            
            # 5. 创建结果对象
            end_time = time.time()
            processing_time = f"{end_time - start_time:.1f}秒"
            
            # 重新排序场景ID，确保全局唯一性
            self._reorder_scene_ids(all_scenes)
            
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
            
            result = ChapterResult(
                chapter_info=chapter_info,
                basic_stats=basic_stats,
                scenes=all_scenes,  # 使用scenes而不是segments
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
                scenes=[],  # 使用scenes而不是segments
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
    
    def save_prompts(self, prompts: List[Dict[str, str]], chapter_title: str) -> str:
        """
        保存提示词和旁白
        
        Args:
            prompts: 提示词列表
            chapter_title: 章节标题
            
        Returns:
            保存的文件路径
        """
        # 生成输出文件名
        file_name = f"{chapter_title}_prompts.json"
        output_path = f"{OUTPUT_DIR}/{file_name}"
        
        # 确保输出目录存在
        self.file_handler.ensure_directory_exists(OUTPUT_DIR)
        
        # 保存提示词
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(prompts, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"提示词已保存到: {output_path}")
        return output_path
    
    def _process_segments_sequentially(
        self, 
        segments: List[TextSegment], 
        novel_type: str, 
        chapter_title: str, 
        errors: List[ProcessingError]
    ) -> List[Scene]:
        """
        顺序处理段落（原流程）
        
        Args:
            segments: 段落列表
            novel_type: 小说类型
            chapter_title: 章节标题
            errors: 错误列表
            
        Returns:
            场景列表
        """
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
        
        return all_scenes
    
    def _process_scenes_sequentially(
        self, 
        scenes: List[Scene], 
        novel_type: str, 
        chapter_title: str, 
        errors: List[ProcessingError]
    ) -> List[VisualNarrative]:
        """
        顺序处理场景的视觉生成（原流程）
        
        Args:
            scenes: 场景列表
            novel_type: 小说类型
            chapter_title: 章节标题
            errors: 错误列表
            
        Returns:
            视觉叙述列表
        """
        storyboards = []
        for scene in scenes:
            try:
                context = {
                    "novel_type": novel_type,
                    "chapter_title": chapter_title,
                    "previous_scene_summary": self._get_previous_scene_summary(scenes[:scenes.index(scene)])
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
        
        return storyboards
    
    def _reorder_scene_ids(self, scenes: List[Scene]) -> None:
        """
        重新排序场景ID，确保全局唯一性
        
        Args:
            scenes: 场景列表
        """
        for i, scene in enumerate(scenes):
            # 更新场景ID，使用全局索引
            old_scene_id = scene.scene_id
            scene.scene_id = f"scene_{i+1:03d}"  # 格式化为 scene_001, scene_002, ...
            
            # 如果场景有视觉叙述，也需要更新其中的scene_id
            if scene.visual_narrative:
                scene.visual_narrative.scene_id = scene.scene_id
            
            self.logger.debug(f"场景ID已更新: {old_scene_id} -> {scene.scene_id}")