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
from config.logging_config import get_module_logger, LogModule

logger = get_module_logger(LogModule.COMIC_IMAGE_GENERATION)


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
        self.output_root_dir = self.config.get("comic_image_generation", {}).get("paths", {}).get("output_root_dir", "custom_output/")
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
        save_dir: Optional[str] = None, 
        reference_image: Optional[str] = None,
        batch_size: Optional[int] = None,
        seed: Optional[int] = None
    ) -> List[str]:
        """
        生成图片
        
        Args:
            prompt: 提示词
            save_dir: 保存目录，相对于output_root_dir的相对路径，如果为None则直接使用output_root_dir
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
            
            # 构建完整的保存路径
            if save_dir is None:
                full_save_dir = self.output_root_dir
            else:
                # 确保路径格式正确
                save_dir = save_dir.replace('\\', '/').strip('/')
                full_save_dir = os.path.join(self.output_root_dir, save_dir)

        
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
            os.makedirs(full_save_dir, exist_ok=True)
            
            # 生成图片 - 不使用上下文管理器，手动管理连接
            try:
                if not self.wrapper.ws:
                    self.wrapper.connect()
                    
                output_images = self.wrapper.generate_images(workflow, full_save_dir)
            finally:
                # 确保在生成完成后断开连接
                if self.wrapper and self.wrapper.ws:
                    self.wrapper.disconnect()
            
            image_paths = list(output_images.values())
            logger.info(f"成功生成 {len(image_paths)} 张图片到目录: {full_save_dir}")
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
        save_dir: Optional[str] = None, 
        reference_image: Optional[str] = None,
        batch_size: Optional[int] = None,
        seed: Optional[int] = None
    ) -> List[str]:
        """
        批量生成多张图片
        
        Args:
            prompts: 提示词列表
            save_dir: 保存目录，相对于output_root_dir的相对路径，如果为None则直接使用output_root_dir
            reference_image: 参考图片路径
            batch_size: 每批处理的图片数量，如果为None则使用配置文件中的默认值
            seed: 随机种子，如果为None则自动生成
            
        Returns:
            生成的所有图片路径列表
        """
        # 构建完整的保存路径
        if save_dir is None:
            full_save_dir = self.output_root_dir
        else:
            # 确保路径格式正确
            save_dir = save_dir.replace('\\', '/').strip('/')
            full_save_dir = os.path.join(self.output_root_dir, save_dir)
        
        all_image_paths = []
        
        # 从配置文件获取默认参数
        generation_config = self.config.get("comic_image_generation", {}).get("generation", {})
        default_batch_size = generation_config.get("default_batch_size", 1)
        # 使用传入参数或默认值
        batch_size = batch_size if batch_size is not None else default_batch_size
        
        # 分批处理提示词
        for i in range(0, len(prompts), batch_size):
            batch_prompts = prompts[i:i + batch_size]
            
            # 为每批提示词生成图片
            for prompt in batch_prompts:
                try:
                    image_paths = self.generate_image(
                        prompt=prompt,
                        save_dir=full_save_dir,
                        reference_image=reference_image,
                        batch_size=1,
                        seed=seed
                    )
                    all_image_paths.extend(image_paths)
                except Exception as e:
                    logger.error(f"生成图片时出错 (提示词: {prompt[:50]}...): {str(e)}")
                    # 继续处理其他提示词
                    continue
        
        logger.info(f"批量生成完成，共生成 {len(all_image_paths)} 张图片")
        return all_image_paths
    

    
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