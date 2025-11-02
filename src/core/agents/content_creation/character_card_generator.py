"""
主控角色卡生成器
协调各个子Agent的工作，实现完整的角色卡生成流程
"""

from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

from .base import BaseContentAgent, CharacterCardState
from .character_grouping_agent import CharacterGroupingAgent
from .character_extraction_agent import CharacterExtractionAgent
from .character_merge_agent import CharacterMergeAgent
from .character_update_agent import CharacterUpdateAgent
from src.utils.logging_manager import get_agent_logger


class CharacterCardGenerator(BaseContentAgent):
    """主控角色卡生成器，协调各个子Agent的工作"""
    
    def __init__(self, model_name: str = None, temperature: float = 0.5):
        super().__init__(model_name, temperature)
        self.logger = get_agent_logger(__class__.__name__)
        
        # 初始化各个子Agent
        self.grouping_agent = CharacterGroupingAgent(model_name, temperature)
        self.extraction_agent = CharacterExtractionAgent(model_name, temperature)
        self.merge_agent = CharacterMergeAgent(model_name, temperature)
        self.update_agent = CharacterUpdateAgent(model_name, temperature)
    
    def extract(self, character_info: Dict[str, Any], original_text: str, 
                existing_cards: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """生成角色卡片
        
        Args:
            character_info: 角色基本信息
            original_text: 原文文本
            existing_cards: 已存在的角色卡片（可选）
            
        Returns:
            角色卡片生成结果
        """
        try:
            # 初始化状态
            state = self._initialize_state(character_info, original_text, existing_cards)
            
            # 构建工作流图
            workflow = self._build_workflow()
            
            # 执行工作流
            result = workflow.invoke(state)
            
            # 检查是否有错误
            if result.get("errors"):
                return {
                    "success": False,
                    "error": "角色卡生成过程中出现错误",
                    "details": result["errors"],
                    "final_cards": result.get("final_cards", {}),
                    "agent": "主控角色卡生成器"
                }
            
            return {
                "success": True,
                "final_cards": result["final_cards"],
                "completed_tasks": result["completed_tasks"],
                "total_characters": len(result["final_cards"]),
                "agent": "主控角色卡生成器"
            }
            
        except Exception as e:
            self.logger.error(f"角色卡生成失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "agent": "主控角色卡生成器"
            }
    
    def _initialize_state(self, character_info: Dict[str, Any], original_text: str,
                         existing_cards: Optional[Dict[str, Any]]) -> CharacterCardState:
        """初始化状态
        
        Args:
            character_info: 角色基本信息
            original_text: 原文文本
            existing_cards: 已存在的角色卡片
            
        Returns:
            初始化的状态
        """
        return {
            "character_info": character_info,
            "original_text": original_text,
            "existing_cards": existing_cards or {},
            "temp_cards": {},
            "final_cards": {},
            "grouped_characters": {},
            "completed_tasks": [],
            "errors": [],
            "grouping_done": False,
            "extraction_done": False,
            "merging_done": False,
            "updating_done": False
        }
    
    def _build_workflow(self) -> StateGraph:
        """构建工作流图
        
        Returns:
            工作流图
        """
        # 创建工作流图
        workflow = StateGraph(CharacterCardState)
        
        # 添加节点
        workflow.add_node("group_characters", self._group_characters)
        workflow.add_node("extract_character_cards", self._extract_character_cards)
        workflow.add_node("merge_character_info", self._merge_character_info)
        workflow.add_node("update_character_cards", self._update_character_cards)
        
        # 添加边
        workflow.add_edge(START, "group_characters")
        workflow.add_edge("group_characters", "extract_character_cards")
        workflow.add_edge("extract_character_cards", "merge_character_info")
        workflow.add_edge("merge_character_info", "update_character_cards")
        workflow.add_edge("update_character_cards", END)
        
        return workflow.compile()
    
    def _group_characters(self, state: CharacterCardState) -> CharacterCardState:
        """分组角色"""
        return self.grouping_agent.process(state)
    
    def _extract_character_cards(self, state: CharacterCardState) -> CharacterCardState:
        """提取角色卡片"""
        return self.extraction_agent.process(state)
    
    def _merge_character_info(self, state: CharacterCardState) -> CharacterCardState:
        """合并角色信息"""
        return self.merge_agent.process(state)
    
    def _update_character_cards(self, state: CharacterCardState) -> CharacterCardState:
        """更新角色卡片"""
        return self.update_agent.process(state)
    
    def generate_character_cards_parallel(self, chapters_data: Dict[str, Any], 
                                        existing_cards: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """并行生成多个章节的角色卡片
        
        Args:
            chapters_data: 章节数据字典，键为章节名，值为角色信息和原文
            existing_cards: 已存在的角色卡片（可选）
            
        Returns:
            角色卡片生成结果
        """
        try:
            all_final_cards = {}
            all_completed_tasks = []
            all_errors = []
            
            # 处理每个章节
            for chapter_name, chapter_data in chapters_data.items():
                self.logger.info(f"开始处理章节: {chapter_name}")
                
                # 提取角色信息和原文
                character_info = chapter_data.get("character_info", {})
                original_text = chapter_data.get("original_text", "")
                
                # 生成角色卡片
                result = self.extract(character_info, original_text, existing_cards)
                
                if result["success"]:
                    # 合并结果
                    all_final_cards.update(result["final_cards"])
                    all_completed_tasks.extend(result["completed_tasks"])
                    
                    # 更新已存在的卡片，供下一章节使用
                    existing_cards = result["final_cards"]
                    
                    self.logger.info(f"章节 {chapter_name} 处理完成，生成 {len(result['final_cards'])} 个角色卡片")
                else:
                    # 记录错误
                    error_msg = f"章节 {chapter_name} 处理失败: {result['error']}"
                    all_errors.append(error_msg)
                    self.logger.error(error_msg)
            
            # 返回最终结果
            return {
                "success": len(all_errors) == 0,
                "final_cards": all_final_cards,
                "completed_tasks": all_completed_tasks,
                "errors": all_errors,
                "total_characters": len(all_final_cards),
                "processed_chapters": len(chapters_data),
                "agent": "主控角色卡生成器"
            }
            
        except Exception as e:
            self.logger.error(f"并行角色卡生成失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "agent": "主控角色卡生成器"
            }
    
    def validate_all_cards(self, final_cards: Dict[str, Any]) -> Dict[str, Any]:
        """验证所有角色卡片
        
        Args:
            final_cards: 角色卡片字典
            
        Returns:
            验证结果
        """
        try:
            validation_results = {}
            all_errors = []
            all_warnings = []
            
            # 验证每个角色卡片
            for character_name, card in final_cards.items():
                update_agent = CharacterUpdateAgent()
                validation_result = update_agent.validate_character_card(card)
                
                validation_results[character_name] = validation_result
                
                # 收集所有错误和警告
                all_errors.extend([f"{character_name}: {error}" for error in validation_result["errors"]])
                all_warnings.extend([f"{character_name}: {warning}" for warning in validation_result["warnings"]])
            
            return {
                "success": len(all_errors) == 0,
                "validation_results": validation_results,
                "total_errors": len(all_errors),
                "total_warnings": len(all_warnings),
                "errors": all_errors,
                "warnings": all_warnings,
                "agent": "主控角色卡生成器"
            }
            
        except Exception as e:
            self.logger.error(f"角色卡片验证失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "agent": "主控角色卡生成器"
            }