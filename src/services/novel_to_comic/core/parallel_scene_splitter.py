"""
固定节点的并行场景分割工作流
创建固定数量的场景分割节点，将段落平均分配
"""

import uuid
import time
from typing import Dict, List, Any, Optional, TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
import operator

from src.services.novel_to_comic.core.scene_splitter import SceneSplitterAgent
from src.services.novel_to_comic.models.data_models import (
    TextSegment, Scene, ProcessingError
)
from src.services.novel_to_comic.utils.character_manager import CharacterManager
from src.services.novel_to_comic.config.processing_config import MAX_SCENE_SPLITTING_CONCURRENT
from src.utils.logging_manager import get_logger, LogCategory

logger = get_logger(__name__, LogCategory.PERFORMANCE)


class FixedParallelState(TypedDict):
    """固定节点并行处理状态"""
    # 输入
    segments: List[TextSegment]
    context: Dict[str, Any]
    
    # 分段分配
    worker_segments: Dict[str, List[TextSegment]]  # worker_id -> segments
    
    # 输出
    all_scenes: Annotated[List[Scene], operator.add]
    errors: Annotated[List[ProcessingError], operator.add]
    
    # 完成状态
    completed_workers: Annotated[List[str], operator.add]
    
    # 控制参数
    total_workers: int


class ParallelSceneSplitterWorkflow:
    """固定节点的并行场景分割工作流"""
    
    def __init__(self, character_manager: CharacterManager, num_workers: int = MAX_SCENE_SPLITTING_CONCURRENT):
        self.character_manager = character_manager
        self.num_workers = num_workers
        self.scene_splitter = SceneSplitterAgent(character_manager)
        
        # 构建工作流
        self.workflow = self._build_workflow()
    
    def _distribute_segments(self, state: FixedParallelState) -> Dict[str, Any]:
        """
        分配段落给各个工作者
        """
        segments = state["segments"]
        total_workers = self.num_workers  # 使用实例变量而不是状态中的值
        
        logger.info(f"开始分配 {len(segments)} 个段落给 {total_workers} 个工作者")
        
        # 创建工作者分配字典
        worker_segments = {}
        
        # 计算每个工作者应该处理的段落数
        segments_per_worker = max(1, len(segments) // total_workers)
        remaining_segments = len(segments) % total_workers
        
        # 分配段落
        start_idx = 0
        for i in range(total_workers):
            worker_id = f"worker_{i}"
            
            # 计算当前工作者的段落数量
            count = segments_per_worker
            if i < remaining_segments:
                count += 1  # 前面的工作者多处理一个段落
            
            # 分配段落
            end_idx = min(start_idx + count, len(segments))
            worker_segments[worker_id] = segments[start_idx:end_idx]
            
            start_idx = end_idx
            
            logger.info(f"工作者 {worker_id} 分配了 {len(worker_segments[worker_id])} 个段落")
        
        return {
            "worker_segments": worker_segments
        }
    
    def _process_worker_segments(self, state: FixedParallelState, worker_id: str) -> Dict[str, Any]:
        """
        处理分配给特定工作者的段落
        """
        worker_segments = state.get("worker_segments", {}).get(worker_id, [])
        
        logger.info(f"工作者 {worker_id} 开始处理 {len(worker_segments)} 个段落")
        
        # 如果没有分配任务，直接返回
        if not worker_segments:
            logger.info(f"工作者 {worker_id} 没有分配到任务，直接结束")
            return {
                "completed_workers": [worker_id],
                "scenes": [],
                "errors": []
            }
        
        # 处理分配的段落
        all_scenes = []
        errors = []
        
        for segment in worker_segments:
            try:
                # 创建上下文
                context = {
                    **state["context"],
                    "previous_scene_summary": self._get_previous_scene_summary(segment, state["segments"])
                }
                
                # 调用场景分割
                scenes = self.scene_splitter.split_segment_to_scenes(segment, context)
                all_scenes.extend(scenes)
                
                logger.info(f"工作者 {worker_id} 处理段落 {segment.segment_id} 完成，生成 {len(scenes)} 个场景")
                
            except Exception as e:
                logger.error(f"工作者 {worker_id} 处理段落 {segment.segment_id} 失败: {e}")
                
                error = ProcessingError(
                    error_type="场景分割错误",
                    error_message=str(e),
                    segment_id=segment.segment_id,
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                )
                errors.append(error)
        
        logger.info(f"工作者 {worker_id} 完成所有任务，共生成 {len(all_scenes)} 个场景")
        
        return {
            "completed_workers": [worker_id],
            "all_scenes": all_scenes,
            "errors": errors
        }
    
    def _get_previous_scene_summary(self, segment: TextSegment, all_segments: List[TextSegment]) -> str:
        """
        获取前一个场景的概要
        """
        # 找到当前段落的索引
        try:
            current_index = all_segments.index(segment)
            if current_index > 0:
                previous_segment = all_segments[current_index - 1]
                text = previous_segment.text
                return text[:100] + "..." if len(text) > 100 else text
        except ValueError:
            pass
        
        return "无"
    
    def _check_all_workers_completed(self, state: FixedParallelState) -> str:
        """
        检查所有工作者是否都已完成
        """
        completed_workers = state.get("completed_workers", [])
        total_workers = self.num_workers  # 使用实例变量而不是状态中的值
        
        if len(completed_workers) >= total_workers:
            logger.info(f"所有 {total_workers} 个工作者都已完成")
            return "end"
        else:
            logger.info(f"已完成 {len(completed_workers)}/{total_workers} 个工作者")
            return "continue"
    
    def _build_workflow(self) -> StateGraph:
        """
        构建工作流
        """
        # 创建状态图
        workflow = StateGraph(FixedParallelState)
        
        # 添加节点
        workflow.add_node("distribute_segments", self._distribute_segments)
        
        # 动态添加工作者节点
        for i in range(self.num_workers):
            worker_id = f"worker_{i}"
            # 使用 lambda 创建工作者函数，捕获当前 worker_id
            worker_func = lambda state, worker_id=worker_id: self._process_worker_segments(state, worker_id)
            workflow.add_node(worker_id, worker_func)
        
        # 设置入口点
        workflow.set_entry_point("distribute_segments")
        
        # 添加边：分配完成后，所有工作者并行开始
        for i in range(self.num_workers):
            worker_id = f"worker_{i}"
            workflow.add_edge("distribute_segments", worker_id)
        
        # 添加边：所有工作者完成后直接结束
        for i in range(self.num_workers):
            worker_id = f"worker_{i}"
            workflow.add_edge(worker_id, END)
        
        # 编译工作流
        return workflow.compile()
    
    def process_segments_parallel(
        self, 
        segments: List[TextSegment], 
        context: Dict[str, Any]
    ) -> List[Scene]:
        """
        并行处理段落
        """
        logger.info(f"开始并行处理 {len(segments)} 个段落，使用 {self.num_workers} 个固定工作者")
        
        # 初始状态
        initial_state = {
            "segments": segments,
            "context": context,
            "worker_segments": {},
            "all_scenes": [],
            "errors": [],
            "completed_workers": [],
            "total_workers": self.num_workers  # 确保状态中也有正确的值
        }
        
        # 执行工作流
        start_time = time.time()
        result = self.workflow.invoke(initial_state)
        end_time = time.time()
        
        # 收集结果
        all_scenes = result.get("all_scenes", [])
        errors = result.get("errors", [])
        
        # 按照段落的原始顺序和场景在段落中的顺序排序场景
        # 这确保了即使在并行处理模式下，场景也保持正确的顺序
        all_scenes.sort(key=lambda scene: (scene.segment_index, scene.scene_index_in_segment))
        
        # 记录处理结果
        logger.info(f"并行处理完成，耗时: {end_time - start_time:.2f}秒")
        logger.info(f"总场景数: {len(all_scenes)}，错误数: {len(errors)}")
        
        if errors:
            logger.warning(f"处理过程中发生 {len(errors)} 个错误")
            for error in errors:
                logger.warning(f"错误: {error.error_message}")
        
        return all_scenes