"""
漫画图片生成接口模块

封装ComfyUI API调用, 提供支持参考图片的漫画图片生成功能.
"""

import os
import json
import time
import yaml
from typing import List, Dict, Optional, Union, Any
from src.utils.comfyui_wrapper import ComfyUIWrapper
from config.logging_config import get_logger

logger = get_logger(__name__)


class ComicImageGeneration:
    """漫画图片生成接口封装类，支持参考图片"""
    
    def __init__(self, config_path: str = "src/services/comic_image_generation/config.yaml"):
        """
        初始化漫画图片生成接口
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.workflow_template = self.config.get("comic_image_generation", {}).get("paths", {}).get("workflow_template", "comfyui/novel_t2I_flux_pulid.json")
        self.comfyui_input_dir = self.config.get("comic_image_generation", {}).get("paths", {}).get("comfyui_input_dir", "ComfyUI/input")
        self.wrapper = None
        self.workflow = None
        
    def _load_config(self, config_path: str) -> Dict:
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            配置字典
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"已加载配置文件: {config_path}")
            return config
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            return {}
        
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
    
    def _update_workflow_param(self, node_id: str, param_name: str, param_value: Any) -> None:
        """
        更新工作流节点的参数
        
        Args:
            node_id: 节点ID
            param_name: 参数名称
            param_value: 参数值
        """
        if node_id in self.workflow and "inputs" in self.workflow[node_id]:
            self.workflow[node_id]["inputs"][param_name] = param_value
        else:
            raise ValueError(f"无法找到节点 {node_id} 或其 {param_name} 参数")
    
    def generate_image(
        self, 
        prompt: str, 
        save_dir: str, 
        reference_image: Optional[str] = None,
        batch_size: Optional[int] = None,
        seed: Optional[int] = None
    ) -> List[str]:
        """
        生成图片
        
        Args:
            prompt: 提示词
            save_dir: 保存目录
            reference_image: 参考图片路径
            batch_size: 批处理大小，如果为None则使用配置文件中的默认值
            seed: 随机种子，如果为None则自动生成
            
        Returns:
            生成的图片路径列表
        """
        try:
            # 从配置文件获取默认参数
            generation_config = self.config.get("comic_image_generation", {}).get("generation", {})
            default_batch_size = generation_config.get("default_batch_size", 1)
            # 使用传入参数或默认值
            batch_size = batch_size if batch_size is not None else default_batch_size

        
            workflow = self.setup_workflow()
            
            # 更新提示词
            self.wrapper.update_workflow_text(workflow, "1", prompt)
            
            # 设置批处理大小
            self.wrapper.update_workflow_batch_size(workflow, "9", batch_size)
            
            # 设置随机种子
            if seed is None:
                seed = int(time.time())
            self.wrapper.update_workflow_seed(workflow, "5", seed)
 
            
            # 更新参考图片
            if reference_image:
                if not os.path.exists(reference_image):
                    raise FileNotFoundError(f"参考图片不存在: {reference_image}")
                
                # 获取图片文件名
                image_filename = os.path.basename(reference_image)
                
                self._update_workflow_param("26", "image", image_filename)
                
                # 将参考图片复制到ComfyUI的input目录
                self._copy_reference_image(reference_image)
            else:
                logger.warning("未提供参考图片，将使用工作流中的默认参考图片")
            
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
        reference_image: Optional[str] = None,
        batch_size: Optional[int] = None,
        weight: Optional[float] = None,
        steps: Optional[int] = None,
        cfg: Optional[float] = None
    ) -> Dict[str, List[str]]:
        """
        生成多张图片
        
        Args:
            prompts: 提示词列表
            save_dir: 保存目录
            reference_image: 参考图片路径
            batch_size: 批处理大小，如果为None则使用配置文件中的默认值
            weight: PuLID权重，控制参考图片的影响程度，如果为None则使用配置文件中的默认值
            steps: 采样步数，如果为None则使用配置文件中的默认值
            cfg: CFG scale，如果为None则使用配置文件中的默认值
            
        Returns:
            提示词和图片路径的映射字典
        """
        results = {}
        
        for i, prompt in enumerate(prompts):
            try:
                # 为每个提示词创建子目录
                prompt_dir = os.path.join(save_dir, f"prompt_{i+1}")
                image_paths = self.generate_image(
                    prompt=prompt,
                    save_dir=prompt_dir,
                    reference_image=reference_image,
                    batch_size=batch_size,
                    weight=weight,
                    steps=steps,
                    cfg=cfg
                )
                results[prompt] = image_paths
                logger.info(f"提示词 '{prompt[:30]}...' 的图片生成完成")
            except Exception as e:
                logger.error(f"处理提示词 '{prompt[:30]}...' 时出错: {str(e)}")
                results[prompt] = []
        
        return results
    
    def generate_character_variations(
        self,
        base_prompt: str,
        variations: List[str],
        reference_image: str,
        save_dir: str,
        batch_size: int = 1,
        weight: float = 0.8,
        steps: int = 15,
        cfg: float = 1.0
    ) -> Dict[str, List[str]]:
        """
        生成角色变体图片
        
        Args:
            base_prompt: 基础提示词
            variations: 变体描述列表，例如["微笑的表情", "愤怒的表情", "悲伤的表情"]
            reference_image: 角色参考图片路径
            save_dir: 保存目录
            batch_size: 批处理大小
            weight: PuLID权重，控制参考图片的影响程度
            steps: 采样步数
            cfg: CFG scale
            
        Returns:
            变体描述和图片路径的映射字典
        """
        results = {}
        
        for variation in variations:
            try:
                # 组合基础提示词和变体描述
                prompt = f"{base_prompt}, {variation}"
                
                # 为每个变体创建子目录
                safe_variation = "".join(c for c in variation if c.isalnum() or c in (' ', '-', '_')).rstrip()
                variation_dir = os.path.join(save_dir, safe_variation)
                
                image_paths = self.generate_image(
                    prompt=prompt,
                    save_dir=variation_dir,
                    reference_image=reference_image,
                    batch_size=batch_size,
                    weight=weight,
                    steps=steps,
                    cfg=cfg
                )
                results[variation] = image_paths
                logger.info(f"变体 '{variation}' 的图片生成完成")
            except Exception as e:
                logger.error(f"处理变体 '{variation}' 时出错: {str(e)}")
                results[variation] = []
        
        return results
    
    def _copy_reference_image(self, reference_image_path: str) -> None:
        """
        将参考图片复制到ComfyUI的input目录
        
        Args:
            reference_image_path: 参考图片路径
        """
        try:
            # 获取ComfyUI的input目录路径
            comfyui_input_dir = self.comfyui_input_dir
            
            # 确保路径使用正确的格式
            comfyui_input_dir = os.path.normpath(comfyui_input_dir)
            
            # 如果ComfyUI运行在本地，尝试复制图片
            if os.path.exists(comfyui_input_dir):
                import shutil
                image_filename = os.path.basename(reference_image_path)
                destination = os.path.join(comfyui_input_dir, image_filename)
                
                # 创建目录（如果不存在）
                os.makedirs(comfyui_input_dir, exist_ok=True)
                
                # 复制文件
                shutil.copy2(reference_image_path, destination)
                logger.info(f"已将参考图片复制到: {destination}")
            else:
                logger.warning(f"ComfyUI input目录不存在: {comfyui_input_dir}")
                logger.warning(f"请手动将参考图片 {reference_image_path} 上传到ComfyUI的input目录")
        except Exception as e:
            logger.warning(f"复制参考图片时出错: {str(e)}，请手动将参考图片上传到ComfyUI的input目录")
    
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