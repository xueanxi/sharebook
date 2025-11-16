"""
ComfyUI接口模块

封装ComfyUI API调用, 提供图片生成功能.
"""

import os
import json
import time
from typing import List, Dict, Optional
from src.utils.comfyui_wrapper import ComfyUIWrapper
from config.logging_config import get_logger

logger = get_logger(__name__)


class ComfyUIInterface:
    """ComfyUI接口封装类"""
    
    def __init__(self, workflow_template: str = "comfyui/novel_t2I_flux.json"):
        """
        初始化ComfyUI接口
        
        Args:
            workflow_template: 工作流模板文件路径
        """
        self.workflow_template = workflow_template
        self.wrapper = None
        self.workflow = None
        
    def setup_workflow(self) -> Dict:
        """
        设置工作流
        
        Returns:
            工作流数据
        """
        if not self.wrapper:
            self.wrapper = ComfyUIWrapper()
            self.wrapper.connect()
        
        if not self.workflow:
            if not os.path.exists(self.workflow_template):
                raise FileNotFoundError(f"工作流模板文件不存在: {self.workflow_template}")
            
            self.workflow = self.wrapper.load_workflow_template(self.workflow_template)
            logger.info(f"已加载工作流模板: {self.workflow_template}")
        
        return self.workflow
    
    def generate_image(self, prompt: str, save_dir: str, batch_size: int = 1) -> List[str]:
        """
        生成图片
        
        Args:
            prompt: 提示词
            save_dir: 保存目录
            batch_size: 批处理大小
            
        Returns:
            生成的图片路径列表
        """
        try:
            workflow = self.setup_workflow()
            
            # 更新提示词
            self.wrapper.update_workflow_text(workflow, "1", prompt)
            
            # 设置批处理大小
            self.wrapper.update_workflow_batch_size(workflow, "9", batch_size)

            # 设置随机种子
            self.wrapper.update_workflow_seed(workflow, "5", int(time.time()))
            
            # 确保保存目录存在
            os.makedirs(save_dir, exist_ok=True)
            
            # 生成图片 - 不使用上下文管理器，手动管理连接
            try:
                if not self.wrapper.ws:
                    self.wrapper.connect()
                    
                output_images = self.wrapper.generate_images(workflow, save_dir)
            finally:
                # 确保在生成完成后断开连接
                if self.wrapper and self.wrapper.ws:
                    self.wrapper.disconnect()
            
            image_paths = list(output_images.values())
            logger.info(f"成功生成 {len(image_paths)} 张图片到目录: {save_dir}")
            return image_paths
            
        except Exception as e:
            logger.error(f"生成图片时出错: {str(e)}")
            # 确保在出错时也断开连接
            if self.wrapper and self.wrapper.ws:
                try:
                    self.wrapper.disconnect()
                except:
                    pass
            raise
    
    def generate_multiple_images(
        self, 
        prompts: List[str], 
        save_dir: str, 
        batch_size: int = 1
    ) -> Dict[str, List[str]]:
        """
        生成多张图片
        
        Args:
            prompts: 提示词列表
            save_dir: 保存目录
            batch_size: 批处理大小
            
        Returns:
            提示词和图片路径的映射字典
        """
        results = {}
        
        for i, prompt in enumerate(prompts):
            try:
                # 为每个提示词创建子目录
                prompt_dir = os.path.join(save_dir, f"prompt_{i+1}")
                image_paths = self.generate_image(prompt, prompt_dir, batch_size)
                results[prompt] = image_paths
                logger.info(f"提示词 '{prompt[:30]}...' 的图片生成完成")
            except Exception as e:
                logger.error(f"处理提示词 '{prompt[:30]}...' 时出错: {str(e)}")
                results[prompt] = []
        
        return results
    
    def update_workflow_template(self, template_path: str) -> None:
        """
        更新工作流模板
        
        Args:
            template_path: 新的模板文件路径
        """
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"工作流模板文件不存在: {template_path}")
        
        self.workflow_template = template_path
        self.workflow = None  # 重置工作流，强制重新加载
        logger.info(f"已更新工作流模板: {template_path}")
    
    def test_connection(self) -> bool:
        """
        测试与ComfyUI服务器的连接
        
        Returns:
            连接是否成功
        """
        try:
            if not self.wrapper:
                self.wrapper = ComfyUIWrapper()
            
            self.wrapper.connect()
            self.wrapper.disconnect()
            logger.info("ComfyUI连接测试成功")
            return True
        except Exception as e:
            logger.error(f"ComfyUI连接测试失败: {str(e)}")
            return False
    
    def __del__(self):
        """析构函数，确保连接关闭"""
        if self.wrapper:
            try:
                self.wrapper.disconnect()
            except:
                pass