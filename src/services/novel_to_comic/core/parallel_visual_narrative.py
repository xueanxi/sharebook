"""
固定节点的并行视觉生成工作流
创建固定数量的视觉生成节点，将场景平均分配
"""

import uuid
import time
from typing import Dict, List, Any, Optional, TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
import operator

from src.services.novel_to_comic.core.visual_narrative import VisualNarrativeAgent
from src.services.novel_to_comic.models.data_models import (
    Scene, VisualNarrative, ProcessingError
)
from src.services.novel_to_comic.utils.character_manager import CharacterManager
from src.services.novel_to_comic.config.processing_config import MAX_SCENE_SPLITTING_CONCURRENT
from src.utils.logging_manager import get_logger, LogCategory

logger = get_logger(__name__, LogCategory.PERFORMANCE)


class FixedParallelVisualState(TypedDict):
    """固定节点并行视觉生成状态"""
    # 输入
    scenes: List[Scene]
    context: Dict[str, Any]
    
    # 分段分配
    worker_scenes: Dict[str, List[Scene]]  # worker_id -> scenes
    
    # 输出
    all_visual_narratives: Annotated[List[VisualNarrative], operator.add]
    errors: Annotated[List[ProcessingError], operator.add]
    
    # 完成状态
    completed_workers: Annotated[List[str], operator.add]
    
    # 控制参数
    total_workers: int


class ParallelVisualNarrativeWorkflow:
    """固定节点的并行视觉生成工作流"""
    
    def __init__(self, character_manager: CharacterManager, num_workers: int = MAX_SCENE_SPLITTING_CONCURRENT):
        self.character_manager = character_manager
        self.num_workers = num_workers
        self.visual_narrative = VisualNarrativeAgent(character_manager)
        
        # 构建工作流
        self.workflow = self._build_workflow()
    
    def _distribute_scenes(self, state: FixedParallelVisualState) -> Dict[str, Any]:
        """
        分配场景给各个工作者
        """
        scenes = state["scenes"]
        total_workers = state["total_workers"]
        
        logger.info(f"开始分配 {len(scenes)} 个场景给 {total_workers} 个工作者")
        
        # 创建工作者分配字典
        worker_scenes = {}
        
        # 计算每个工作者应该处理的场景数
        scenes_per_worker = max(1, len(scenes) // total_workers)
        remaining_scenes = len(scenes) % total_workers
        
        # 分配场景
        start_idx = 0
        for i in range(total_workers):
            worker_id = f"visual_worker_{i}"
            
            # 计算当前工作者的场景数量
            count = scenes_per_worker
            if i < remaining_scenes:
                count += 1  # 前面的工作者多处理一个场景
            
            # 分配场景
            end_idx = min(start_idx + count, len(scenes))
            worker_scenes[worker_id] = scenes[start_idx:end_idx]
            
            start_idx = end_idx
            
            logger.info(f"工作者 {worker_id} 分配了 {len(worker_scenes[worker_id])} 个场景")
        
        return {
            "worker_scenes": worker_scenes
        }
    
    def _process_worker_scenes(self, state: FixedParallelVisualState, worker_id: str) -> Dict[str, Any]:
        """
        处理分配给特定工作者的场景
        """
        worker_scenes = state.get("worker_scenes", {}).get(worker_id, [])
        
        logger.info(f"工作者 {worker_id} 开始处理 {len(worker_scenes)} 个场景")
        
        # 如果没有分配任务，直接返回
        if not worker_scenes:
            logger.info(f"工作者 {worker_id} 没有分配到任务，直接结束")
            return {
                "completed_workers": [worker_id],
                "visual_narratives": [],
                "errors": []
            }
        
        # 处理分配的场景
        all_visual_narratives = []
        errors = []
        
        for scene in worker_scenes:
            try:
                # 创建上下文
                context = {
                    **state["context"],
                    "previous_scene_summary": self._get_previous_scene_summary(scene, state["scenes"])
                }
                
                # 调用视觉叙述生成
                visual_narrative = self.visual_narrative.generate_visual_narrative(scene, context)
                all_visual_narratives.append(visual_narrative)
                
                logger.info(f"工作者 {worker_id} 处理场景 {scene.scene_id} 完成")
                
            except Exception as e:
                logger.error(f"工作者 {worker_id} 处理场景 {scene.scene_id} 失败: {e}")
                
                error = ProcessingError(
                    error_type="视觉叙述生成错误",
                    error_message=str(e),
                    scene_id=scene.scene_id,
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                )
                errors.append(error)
        
        logger.info(f"工作者 {worker_id} 完成所有任务，共生成 {len(all_visual_narratives)} 个视觉叙述")
        
        return {
            "completed_workers": [worker_id],
            "all_visual_narratives": all_visual_narratives,
            "errors": errors
        }
    
    def _get_previous_scene_summary(self, scene: Scene, all_scenes: List[Scene]) -> str:
        """
        获取前一个场景的概要
        """
        # 找到当前场景的索引
        try:
            current_index = all_scenes.index(scene)
            if current_index > 0:
                previous_scene = all_scenes[current_index - 1]
                text = previous_scene.scene_description
                return text[:100] + "..." if len(text) > 100 else text
        except ValueError:
            pass
        
        return "无"
    
    def _build_workflow(self) -> StateGraph:
        """
        构建工作流
        """
        # 创建状态图
        workflow = StateGraph(FixedParallelVisualState)
        
        # 添加节点
        workflow.add_node("distribute_scenes", self._distribute_scenes)
        
        # 动态添加视觉工作者节点
        for i in range(self.num_workers):
            worker_id = f"visual_worker_{i}"
            # 使用lambda函数绑定_process_worker_scenes方法和worker_id参数
            workflow.add_node(worker_id, lambda state, worker_id=worker_id: self._process_worker_scenes(state, worker_id))
        
        # 设置入口点
        workflow.set_entry_point("distribute_scenes")
        
        # 添加边：分配完成后，所有工作者并行开始
        for i in range(self.num_workers):
            worker_id = f"visual_worker_{i}"
            workflow.add_edge("distribute_scenes", worker_id)
        
        # 添加边：所有工作者完成后直接结束
        for i in range(self.num_workers):
            worker_id = f"visual_worker_{i}"
            workflow.add_edge(worker_id, END)
        
        # 编译工作流
        return workflow.compile()
    
    def process_scenes_parallel(
        self, 
        scenes: List[Scene], 
        context: Dict[str, Any]
    ) -> List[VisualNarrative]:
        """
        并行处理场景
        """
        logger.info(f"开始并行处理 {len(scenes)} 个场景，使用 {self.num_workers} 个固定工作者")
        
        # 初始状态
        initial_state = {
            "scenes": scenes,
            "context": context,
            "worker_scenes": {},
            "all_visual_narratives": [],
            "errors": [],
            "completed_workers": [],
            "total_workers": self.num_workers
        }
        
        # 执行工作流
        start_time = time.time()
        result = self.workflow.invoke(initial_state)
        end_time = time.time()
        
        # 收集结果
        all_visual_narratives = result.get("all_visual_narratives", [])
        errors = result.get("errors", [])
        
        # 记录处理结果
        logger.info(f"并行处理完成，耗时: {end_time - start_time:.2f}秒")
        logger.info(f"总视觉叙述数: {len(all_visual_narratives)}，错误数: {len(errors)}")
        
        if errors:
            logger.warning(f"处理过程中发生 {len(errors)} 个错误")
            for error in errors:
                logger.warning(f"错误: {error.error_message}")
        
        return all_visual_narratives