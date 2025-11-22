"""
故事板到提示词转换处理器
主处理类，负责协调整个转换流程
"""
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import time
from datetime import datetime

from .file_manager import FileManager
from .prompt_generator import PromptGenerator

logger = logging.getLogger(__name__)


class StoryboardToPromptProcessor:
    """故事板到提示词转换处理器"""
    
    def __init__(self, config_path: Optional[str] = None, llm=None):
        """
        初始化处理器
        
        Args:
            config_path: 配置文件路径
            llm: 语言模型实例
        """
        self.file_manager = FileManager(config_path)
        self.prompt_generator = PromptGenerator(llm)
        
        # 处理统计
        self.processing_stats = {
            'total_chapters': 0,
            'successful_chapters': 0,
            'failed_chapters': 0,
            'total_prompts': 0,
            'processing_time': 0,
            'errors': []
        }
    
    def process_all_chapters(self, optimize_batch: bool = True) -> Dict[str, Any]:
        """
        处理所有章节的故事板文件
        
        Args:
            optimize_batch: 是否进行批量优化
            
        Returns:
            处理结果统计
        """
        start_time = time.time()
        logger.info("开始批量处理所有章节的故事板文件")
        
        # 重置统计
        self.processing_stats = {
            'total_chapters': 0,
            'successful_chapters': 0,
            'failed_chapters': 0,
            'total_prompts': 0,
            'processing_time': 0,
            'errors': []
        }
        
        # 获取所有故事板文件
        storyboard_files = self.file_manager.get_storyboard_files()
        self.processing_stats['total_chapters'] = len(storyboard_files)
        
        if not storyboard_files:
            logger.warning("没有找到故事板文件")
            return self.processing_stats
        
        # 处理每个章节
        all_prompts = []
        for file_path in storyboard_files:
            try:
                result = self.process_chapter(file_path)
                if result['success']:
                    self.processing_stats['successful_chapters'] += 1
                    self.processing_stats['total_prompts'] += result['prompt_count']
                    all_prompts.extend(result['prompts'])
                    logger.info(f"成功处理章节: {file_path.name}")
                else:
                    self.processing_stats['failed_chapters'] += 1
                    error_msg = f"处理章节失败 {file_path.name}: {result.get('error', '未知错误')}"
                    self.processing_stats['errors'].append(error_msg)
                    logger.error(error_msg)
                    
            except Exception as e:
                self.processing_stats['failed_chapters'] += 1
                error_msg = f"处理章节异常 {file_path.name}: {str(e)}"
                self.processing_stats['errors'].append(error_msg)
                logger.error(error_msg)
        
        # 批量优化
        if optimize_batch and all_prompts:
            logger.info("开始批量优化提示词")
            try:
                # 这里可以添加批量优化逻辑
                # optimization_suggestions = self.prompt_generator.optimize_batch_prompts(
                #     "批量章节", all_prompts
                # )
                logger.info("批量优化完成")
            except Exception as e:
                logger.error(f"批量优化失败: {str(e)}")
        
        # 计算处理时间
        self.processing_stats['processing_time'] = time.time() - start_time
        
        logger.info(f"批量处理完成，成功: {self.processing_stats['successful_chapters']}, "
                   f"失败: {self.processing_stats['failed_chapters']}, "
                   f"总提示词数: {self.processing_stats['total_prompts']}, "
                   f"耗时: {self.processing_stats['processing_time']:.2f}秒")
        
        return self.processing_stats
    
    def process_chapter(self, file_path: Path) -> Dict[str, Any]:
        """
        处理单个章节的故事板文件
        
        Args:
            file_path: 故事板文件路径
            
        Returns:
            处理结果
        """
        try:
            logger.info(f"开始处理章节: {file_path}")
            
            # 加载故事板文件
            storyboard_data = self.file_manager.load_storyboard_file(file_path)
            if not storyboard_data:
                return {
                    'success': False,
                    'error': '无法加载故事板文件',
                    'prompt_count': 0,
                    'prompts': []
                }
            
            # 提取章节信息
            chapter_info = storyboard_data.get('chapter_info', {})
            segments = storyboard_data.get('segments', [])
            
            # 生成提示词
            prompts = []
            for segment in segments:
                segment_prompts = self._process_segment(segment)
                prompts.extend(segment_prompts)
            
            # 保存提示词
            output_path = self.file_manager.get_output_file_path(
                chapter_info.get('chapter_title', '未知章节')
            )
            
            # 创建备份（如果文件已存在）
            if self.file_manager.file_exists(output_path):
                self.file_manager.create_backup(output_path)
            
            success = self.file_manager.save_prompts(chapter_info, prompts, output_path)
            
            if success:
                logger.info(f"成功处理章节 {chapter_info.get('chapter_title', '未知章节')}, "
                           f"生成 {len(prompts)} 个提示词")
                return {
                    'success': True,
                    'prompt_count': len(prompts),
                    'prompts': prompts,
                    'output_path': str(output_path)
                }
            else:
                return {
                    'success': False,
                    'error': '保存提示词文件失败',
                    'prompt_count': 0,
                    'prompts': []
                }
                
        except Exception as e:
            logger.error(f"处理章节失败 {file_path}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'prompt_count': 0,
                'prompts': []
            }
    
    def _process_segment(self, segment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        处理单个段落
        
        Args:
            segment: 段落数据
            
        Returns:
            生成的提示词列表
        """
        prompts = []
        scenes = segment.get('scenes', [])
        
        for scene in scenes:
            try:
                # 为场景添加段落信息
                scene['segment_id'] = segment.get('segment_id', '')
                scene['segment_index'] = segment.get('segment_index', 0)
                scene['text'] = segment.get('text', '')
                
                # 生成提示词
                prompt = self.prompt_generator.generate_prompt(scene)
                prompts.append(prompt)
                
            except Exception as e:
                logger.error(f"处理场景失败: {str(e)}")
                # 生成备用提示词
                fallback_prompt = self.prompt_generator._generate_fallback_prompt(scene)
                prompts.append(fallback_prompt)
        
        return prompts
    
    def get_processing_progress(self) -> Dict[str, Any]:
        """
        获取处理进度
        
        Returns:
            进度信息字典
        """
        total = self.processing_stats['total_chapters']
        processed = self.processing_stats['successful_chapters'] + self.processing_stats['failed_chapters']
        
        if total == 0:
            progress_percentage = 0
        else:
            progress_percentage = (processed / total) * 100
        
        return {
            'total_chapters': total,
            'processed_chapters': processed,
            'successful_chapters': self.processing_stats['successful_chapters'],
            'failed_chapters': self.processing_stats['failed_chapters'],
            'progress_percentage': progress_percentage,
            'total_prompts': self.processing_stats['total_prompts'],
            'errors': self.processing_stats['errors']
        }
    
    def reset_stats(self):
        """重置处理统计"""
        self.processing_stats = {
            'total_chapters': 0,
            'successful_chapters': 0,
            'failed_chapters': 0,
            'total_prompts': 0,
            'processing_time': 0,
            'errors': []
        }
        logger.info("处理统计已重置")
    
    def validate_storyboard_file(self, file_path: Path) -> Tuple[bool, List[str]]:
        """
        验证故事板文件格式
        
        Args:
            file_path: 故事板文件路径
            
        Returns:
            (是否有效, 错误信息列表)
        """
        errors = []
        
        try:
            # 检查文件是否存在
            if not self.file_manager.file_exists(file_path):
                errors.append(f"文件不存在: {file_path}")
                return False, errors
            
            # 加载文件
            data = self.file_manager.load_storyboard_file(file_path)
            if not data:
                errors.append("无法加载JSON文件")
                return False, errors
            
            # 检查必要字段
            if 'chapter_info' not in data:
                errors.append("缺少chapter_info字段")
            
            if 'segments' not in data:
                errors.append("缺少segments字段")
                return False, errors
            
            # 检查段落格式
            segments = data['segments']
            if not isinstance(segments, list):
                errors.append("segments字段必须是列表")
                return False, errors
            
            for i, segment in enumerate(segments):
                if 'scenes' not in segment:
                    errors.append(f"段落{i}缺少scenes字段")
                    continue
                
                scenes = segment['scenes']
                if not isinstance(scenes, list):
                    errors.append(f"段落{i}的scenes字段必须是列表")
                    continue
                
                for j, scene in enumerate(scenes):
                    if 'scene_description' not in scene:
                        errors.append(f"段落{i}场景{j}缺少scene_description字段")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"验证文件时发生异常: {str(e)}")
            return False, errors
    
    def get_chapter_list(self) -> List[Dict[str, Any]]:
        """
        获取章节列表
        
        Returns:
            章节信息列表
        """
        chapters = []
        storyboard_files = self.file_manager.get_storyboard_files()
        
        for file_path in storyboard_files:
            try:
                # 验证文件
                is_valid, errors = self.validate_storyboard_file(file_path)
                
                # 获取文件信息
                file_stats = self.file_manager.get_file_stats(file_path)
                
                chapter_info = {
                    'file_name': file_path.name,
                    'file_path': str(file_path),
                    'is_valid': is_valid,
                    'errors': errors,
                    'file_size': file_stats['file_size'] if file_stats else 0,
                    'modified_time': file_stats['modified_time'] if file_stats else 0
                }
                
                # 如果文件有效，提取章节信息
                if is_valid:
                    data = self.file_manager.load_storyboard_file(file_path)
                    if data and 'chapter_info' in data:
                        chapter_info.update(data['chapter_info'])
                
                chapters.append(chapter_info)
                
            except Exception as e:
                logger.error(f"获取章节信息失败 {file_path}: {str(e)}")
                chapters.append({
                    'file_name': file_path.name,
                    'file_path': str(file_path),
                    'is_valid': False,
                    'errors': [str(e)],
                    'file_size': 0,
                    'modified_time': 0
                })
        
        return chapters
    
    def clean_old_backups(self, keep_count: int = 10):
        """清理旧备份文件"""
        self.file_manager.clean_old_backups(keep_count)
    
    def export_processing_report(self, output_path: Optional[Path] = None) -> bool:
        """
        导出处理报告
        
        Args:
            output_path: 输出文件路径
            
        Returns:
            是否导出成功
        """
        try:
            if output_path is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_path = self.file_manager.output_dir / f'processing_report_{timestamp}.json'
            
            # 构建报告数据
            report = {
                'report_time': datetime.now().isoformat(),
                'processing_stats': self.processing_stats,
                'progress': self.get_processing_progress(),
                'chapter_list': self.get_chapter_list()
            }
            
            # 确保目录存在
            self.file_manager._ensure_directory_exists(output_path.parent)
            
            # 保存报告
            import json
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            logger.info(f"处理报告已导出: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"导出处理报告失败: {str(e)}")
            return False