"""
漫画图片生成接口模块

封装ComfyUI API调用, 提供支持参考图片的漫画图片生成功能.
"""

import os
import json
import time
import yaml
import glob
from typing import List, Dict, Optional, Union, Any
from sharebook.utils.comfyui_wrapper import ComfyUIWrapper
from sharebook.utils.text_processing.chapter_sorter import ChapterSorter
from sharebook.utils.text_processing.chapter_info_hander import extract_chapter_info
from sharebook.utils.logging_manager import get_module_logger, LogModule
from sharebook.utils.data_helper import data_helper

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
        self.single_character_workflow = self.config.get("comic_image_generation", {}).get("paths", {}).get("single_character_workflow", "comfyui/novel_single_charator_refimage.json")
        self.multi_character_workflow = self.config.get("comic_image_generation", {}).get("paths", {}).get("multi_character_workflow", "comfyui/novel_multi_charator_refiamge.json")
        self.storyboards_prompt_dir = self.config.get("comic_image_generation", {}).get("paths", {}).get("storyboards_prompt_dir", str(data_helper.get_storyboards_prompt_path("")))
        self.comfyui_input_dir = self.config.get("comic_image_generation", {}).get("paths", {}).get("comfyui_input_dir", "ComfyUI/input")
        self.output_root_dir = self.config.get("comic_image_generation", {}).get("paths", {}).get("output_root_dir", "custom_output/")
        self.wrapper = None
        self.single_workflow = None
        self.multi_workflow = None
        
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
        
    def setup_workflow(self, workflow_type: str = "single") -> Dict:
        """
        设置工作流
        
        Args:
            workflow_type: 工作流类型，"single" 或 "multi"
            
        Returns:
            工作流数据
        """
        if not self.wrapper:
            self.wrapper = ComfyUIWrapper()
            self.wrapper.connect()
        
        # 根据工作流类型选择模板
        if workflow_type == "single":
            workflow_template = self.single_character_workflow
            if not self.single_workflow:
                if not os.path.exists(workflow_template):
                    raise FileNotFoundError(f"单角色工作流模板文件不存在: {workflow_template}")
                self.single_workflow = self.wrapper.load_workflow_template(workflow_template)
                logger.info(f"已加载单角色工作流模板: {workflow_template}")
            return self.single_workflow
        elif workflow_type == "multi":
            workflow_template = self.multi_character_workflow
            if not self.multi_workflow:
                if not os.path.exists(workflow_template):
                    raise FileNotFoundError(f"多角色工作流模板文件不存在: {workflow_template}")
                self.multi_workflow = self.wrapper.load_workflow_template(workflow_template)
                logger.info(f"已加载多角色工作流模板: {workflow_template}")
            return self.multi_workflow
        else:
            raise ValueError(f"不支持的工作流类型: {workflow_type}")
    
    def _update_workflow_param(self, workflow: Dict, node_id: str, param_name: str, param_value: Any) -> None:
        """
        更新工作流节点的参数
        
        Args:
            workflow: 工作流数据
            node_id: 节点ID
            param_name: 参数名称
            param_value: 参数值
        """
        if node_id in workflow and "inputs" in workflow[node_id]:
            workflow[node_id]["inputs"][param_name] = param_value
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
        生成单角色图片
        
        Args:
            prompt: 提示词
            save_dir: 保存目录，相对于output_root_dir的相对路径，如果为None则直接使用output_root_dir
            reference_image: 参考图片路径
            batch_size: 批处理大小，如果为None则使用配置文件中的默认值
            seed: 随机种子，如果为None则自动生成
            
        Returns:
            生成的图片路径列表
        """
        import time
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
                # 如果save_dir是绝对路径，直接使用
                if os.path.isabs(save_dir):
                    full_save_dir = save_dir
                else:
                    # 确保路径格式正确
                    save_dir = save_dir.replace('\\', '/').strip('/')
                    # 检查save_dir是否已经包含output_root_dir，避免重复拼接
                    if save_dir.startswith(self.output_root_dir):
                        full_save_dir = save_dir
                    else:
                        full_save_dir = os.path.join(self.output_root_dir, save_dir)

        
            workflow = self.setup_workflow("single")
            
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
                
                # 生成唯一的文件名，避免冲突
                unique_id = int(time.time() * 1000) % 10000  # 取时间戳的后4位
                custom_filename = f"ref_single_{unique_id}"
                
                # 复制参考图片并获取新文件名
                image_filename = self._copy_reference_image(reference_image, custom_filename)
                
                # 更新工作流参数
                self._update_workflow_param(workflow, "26", "image", image_filename)
            else:
                logger.warning("未提供参考图片，将使用工作流中的默认参考图片")
            
            # 确保保存目录存在
            os.makedirs(full_save_dir, exist_ok=True)
            logger.info(f"图片将保存到目录: {full_save_dir}")
            
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
            for i, path in enumerate(image_paths, 1):
                logger.info(f"  图片 {i}: {path}")
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
            # 如果save_dir是绝对路径，直接使用
            if os.path.isabs(save_dir):
                full_save_dir = save_dir
            else:
                # 确保路径格式正确
                save_dir = save_dir.replace('\\', '/').strip('/')
                # 检查save_dir是否已经包含output_root_dir，避免重复拼接
                if save_dir.startswith(self.output_root_dir):
                    full_save_dir = save_dir
                else:
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
    

    
    def _copy_reference_image(self, reference_image_path: str, custom_filename: Optional[str] = None) -> str:
        """
        将参考图片复制到ComfyUI的input目录
        
        Args:
            reference_image_path: 参考图片路径
            custom_filename: 自定义文件名（不包括扩展名），如果为None则使用原文件名
            
        Returns:
            复制后的文件名
        """
        try:
            # 获取ComfyUI的input目录路径
            comfyui_input_dir = self.comfyui_input_dir
            
            # 确保路径使用正确的格式
            comfyui_input_dir = os.path.normpath(comfyui_input_dir)
            
            # 如果ComfyUI运行在本地，尝试复制图片
            if os.path.exists(comfyui_input_dir):
                import shutil
                
                # 获取原文件名和扩展名
                original_filename = os.path.basename(reference_image_path)
                name, ext = os.path.splitext(original_filename)
                
                # 使用自定义文件名或原文件名
                if custom_filename:
                    image_filename = f"{custom_filename}{ext}"
                else:
                    image_filename = original_filename
                
                destination = os.path.join(comfyui_input_dir, image_filename)
                
                # 创建目录（如果不存在）
                os.makedirs(comfyui_input_dir, exist_ok=True)
                
                # 复制文件
                shutil.copy2(reference_image_path, destination)
                logger.info(f"已将参考图片复制到: {destination}")
                return image_filename
            else:
                logger.warning(f"ComfyUI input目录不存在: {comfyui_input_dir}")
                logger.warning(f"请手动将参考图片 {reference_image_path} 上传到ComfyUI的input目录")
                return os.path.basename(reference_image_path)
        except Exception as e:
            logger.warning(f"复制参考图片时出错: {str(e)}，请手动将参考图片上传到ComfyUI的input目录")
            return os.path.basename(reference_image_path)
    
    def update_workflow_template(self, template_path: str) -> None:
        """
        更新工作流模板
        
        Args:
            template_path: 新的模板文件路径
        """
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"工作流模板文件不存在: {template_path}")
        
        # 根据模板路径判断是单角色还是多角色工作流
        if "single" in template_path:
            self.single_character_workflow = template_path
            self.single_workflow = None  # 重置工作流，强制重新加载
            logger.info(f"已更新单角色工作流模板: {template_path}")
        elif "multi" in template_path:
            self.multi_character_workflow = template_path
            self.multi_workflow = None  # 重置工作流，强制重新加载
            logger.info(f"已更新多角色工作流模板: {template_path}")
        else:
            logger.warning(f"无法确定工作流类型，请确保模板路径包含'single'或'multi'关键字")
    
    def generate_multi_character_image(
        self,
        prompt: str,
        ref_image_1: str,
        ref_image_2: str,
        save_dir: Optional[str] = None,
        batch_size: Optional[int] = None,
        seed: Optional[int] = None
    ) -> List[str]:
        """
        生成多角色图片
        
        Args:
            prompt: 提示词
            ref_image_1: 参考图片1路径
            ref_image_2: 参考图片2路径
            save_dir: 保存目录，相对于output_root_dir的相对路径，如果为None则直接使用output_root_dir
            batch_size: 批处理大小，如果为None则使用配置文件中的默认值
            seed: 随机种子，如果为None则自动生成
            
        Returns:
            生成的图片路径列表
        """
        import time
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
                # 如果save_dir是绝对路径，直接使用
                if os.path.isabs(save_dir):
                    full_save_dir = save_dir
                else:
                    # 确保路径格式正确
                    save_dir = save_dir.replace('\\', '/').strip('/')
                    # 检查save_dir是否已经包含output_root_dir，避免重复拼接
                    if save_dir.startswith(self.output_root_dir):
                        full_save_dir = save_dir
                    else:
                        full_save_dir = os.path.join(self.output_root_dir, save_dir)
            
            workflow = self.setup_workflow("multi")
            
            # 更新提示词
            self.wrapper.update_workflow_text(workflow, "6", prompt)
            
            # 设置批处理大小
            self.wrapper.update_workflow_batch_size(workflow, "188", batch_size)
            
            # 设置随机种子
            if seed is None:
                seed = int(time.time())
            self.wrapper.update_workflow_seed(workflow, "31", seed)
            
            # 更新参考图片1
            if ref_image_1:
                if not os.path.exists(ref_image_1):
                    raise FileNotFoundError(f"参考图片1不存在: {ref_image_1}")
                
                # 生成唯一的文件名，避免冲突
                unique_id = int(time.time() * 1000) % 10000  # 取时间戳的后4位
                custom_filename_1 = f"ref_multi_1_{unique_id}"
                
                # 复制参考图片并获取新文件名
                image_filename_1 = self._copy_reference_image(ref_image_1, custom_filename_1)
                
                # 更新工作流参数
                self._update_workflow_param(workflow, "195", "image", image_filename_1)
            else:
                logger.warning("未提供参考图片1，将使用工作流中的默认参考图片")
            
            # 更新参考图片2
            if ref_image_2:
                if not os.path.exists(ref_image_2):
                    raise FileNotFoundError(f"参考图片2不存在: {ref_image_2}")
                
                # 生成唯一的文件名，避免冲突
                unique_id = int(time.time() * 1000) % 10000  # 取时间戳的后4位
                custom_filename_2 = f"ref_multi_2_{unique_id}"
                
                # 复制参考图片并获取新文件名
                image_filename_2 = self._copy_reference_image(ref_image_2, custom_filename_2)
                
                # 更新工作流参数
                self._update_workflow_param(workflow, "200", "image", image_filename_2)
            else:
                logger.warning("未提供参考图片2，将使用工作流中的默认参考图片")
            
            # 确保保存目录存在
            os.makedirs(full_save_dir, exist_ok=True)
            logger.info(f"多角色图片将保存到目录: {full_save_dir}")
            
            # 生成图片
            try:
                if not self.wrapper.ws:
                    self.wrapper.connect()
                    
                output_images = self.wrapper.generate_images(workflow, full_save_dir)
            finally:
                # 确保在生成完成后断开连接
                if self.wrapper and self.wrapper.ws:
                    self.wrapper.disconnect()
            
            image_paths = list(output_images.values())
            logger.info(f"成功生成 {len(image_paths)} 张多角色图片到目录: {full_save_dir}")
            for i, path in enumerate(image_paths, 1):
                logger.info(f"  图片 {i}: {path}")
            return image_paths
            
        except Exception as e:
            logger.error(f"生成多角色图片时出错: {str(e)}")
            # 确保在出错时也断开连接
            if self.wrapper and self.wrapper.ws:
                try:
                    self.wrapper.disconnect()
                except:
                    pass
            raise
    
    def detect_character_count(self, scene_data: Dict) -> int:
        """
        检测场景中的角色数量
        
        Args:
            scene_data: 场景数据
            
        Returns:
            角色数量
        """
        characters = scene_data.get("characters", [])
        # 过滤掉没有参考图片的角色
        valid_characters = []
        for character in characters:
            if isinstance(character, dict):
                character_name = character.get("name", "")
                # 检查是否有有效的参考图片路径
                if character.get("reference_image_path"):
                    valid_characters.append(character_name)
        return len(valid_characters)
    
    def select_workflow(self, scene_data: Dict) -> str:
        """
        根据场景数据选择合适的工作流
        
        Args:
            scene_data: 场景数据
            
        Returns:
            工作流类型 ("single" 或 "multi")
        """
        character_count = self.detect_character_count(scene_data)
        
        if character_count <= 1:
            return "single"
        else:
            return "multi"
    
    def process_chapter(
        self,
        chapter_json_path: str,
        save_dir: Optional[str] = None
    ) -> Dict[str, List[str]]:
        """
        处理单个章节的所有场景
        
        Args:
            chapter_json_path: 章节JSON文件路径
            save_dir: 保存目录，相对于output_root_dir的相对路径，如果为None则直接使用output_root_dir
            
        Returns:
            场景ID到生成图片路径列表的映射
        """
        try:
            # 读取章节JSON文件
            with open(chapter_json_path, 'r', encoding='utf-8') as f:
                chapter_data = json.load(f)
            
            # 提取章节信息
            chapter_info = extract_chapter_info(chapter_json_path)
            chapter_title = chapter_data.get("chapter_title", os.path.basename(chapter_json_path))
            scenes = chapter_data.get("scenes", [])
            
            # 使用提取的章节信息作为目录名，如果没有则使用原标题
            chapter_dir_name = chapter_info if chapter_info else chapter_title
            
            logger.info(f"开始处理章节: {chapter_title}，共 {len(scenes)} 个场景")
            logger.info(f"章节目录名: {chapter_dir_name}")
            
            # 构建完整的保存路径
            if save_dir is None:
                full_save_dir = self.output_root_dir
            else:
                # 如果save_dir是绝对路径，直接使用
                if os.path.isabs(save_dir):
                    full_save_dir = save_dir
                else:
                    # 确保路径格式正确
                    save_dir = save_dir.replace('\\', '/').strip('/')
                    # 避免路径重复拼接
                    if save_dir.startswith(self.output_root_dir):
                        full_save_dir = save_dir
                    else:
                        full_save_dir = os.path.join(self.output_root_dir, save_dir)
            
            # 为章节创建子目录
            chapter_save_dir = os.path.join(full_save_dir, chapter_dir_name)
            os.makedirs(chapter_save_dir, exist_ok=True)
            logger.info(f"章节保存目录: {chapter_save_dir}")
            
            results = {}
            
            for scene in scenes:
                scene_id = scene.get("scene_id", 0)
                # 尝试多个可能的提示词字段
                prompt = scene.get("english_prompt") or scene.get("prompt", "")
                characters = scene.get("characters", [])
                
                # 构建角色引用映射
                character_references = {}
                for character in characters:
                    if isinstance(character, dict):
                        character_name = character.get("name", "")
                        reference_image = character.get("reference_image_path")
                        if character_name and reference_image:
                            # 标准化路径，处理反斜杠
                            reference_image = os.path.normpath(reference_image)
                            # 如果是相对路径，转换为绝对路径
                            if not os.path.isabs(reference_image):
                                # 假设相对于项目根目录
                                reference_image = os.path.abspath(reference_image)
                            character_references[character_name] = reference_image
                
                # 为场景创建子目录
                # 确保scene_id是数字类型
                if isinstance(scene_id, str):
                    # 尝试从字符串中提取数字
                    import re
                    match = re.search(r'\d+', scene_id)
                    if match:
                        scene_num = int(match.group())
                    else:
                        scene_num = 0
                else:
                    scene_num = int(scene_id) if scene_id else 0
                
                scene_save_dir = os.path.join(chapter_save_dir, f"scene_{scene_num:03d}")
                os.makedirs(scene_save_dir, exist_ok=True)
                logger.info(f"场景 {scene_num} 保存目录: {scene_save_dir}")
                
                try:
                    # 根据角色数量选择工作流
                    workflow_type = self.select_workflow(scene)
                    logger.info(f"场景 {scene_num} 使用 {workflow_type} 角色工作流")
                    
                    if workflow_type == "single":
                        # 单角色工作流
                        ref_image = None
                        character_name = "未知"
                        for character in characters:
                            if isinstance(character, dict) and character.get("reference_image_path"):
                                ref_image = character.get("reference_image_path")
                                character_name = character.get("name", "未知")
                                break
                        
                        logger.info(f"单角色生成 - 角色: {character_name}, 参考图片: {ref_image}")
                        image_paths = self.generate_image(
                            prompt=prompt,
                            save_dir=scene_save_dir,
                            reference_image=ref_image
                        )
                    else:
                        # 多角色工作流
                        ref_image_1 = None
                        ref_image_2 = None
                        character_names = []
                        
                        valid_characters = [c for c in characters if isinstance(c, dict) and c.get("reference_image_path")]
                        if len(valid_characters) >= 1:
                            ref_image_1 = valid_characters[0].get("reference_image_path")
                            character_names.append(valid_characters[0].get("name", "角色1"))
                        if len(valid_characters) >= 2:
                            ref_image_2 = valid_characters[1].get("reference_image_path")
                            character_names.append(valid_characters[1].get("name", "角色2"))
                        
                        logger.info(f"多角色生成 - 角色: {', '.join(character_names)}, 参考图片1: {ref_image_1}, 参考图片2: {ref_image_2}")
                        image_paths = self.generate_multi_character_image(
                            prompt=prompt,
                            ref_image_1=ref_image_1,
                            ref_image_2=ref_image_2,
                            save_dir=scene_save_dir
                        )
                    
                    results[f"scene_{scene_num:03d}"] = image_paths
                    logger.info(f"场景 {scene_num} 处理完成，生成 {len(image_paths)} 张图片")
                    for i, path in enumerate(image_paths, 1):
                        logger.info(f"  图片 {i}: {path}")
                    
                except Exception as e:
                    logger.error(f"处理场景 {scene_id} 时出错: {str(e)}")
                    results[f"scene_{scene_num:03d}"] = []
                    continue
            
            logger.info(f"章节 {chapter_title} 处理完成")
            return results
            
        except Exception as e:
            logger.error(f"处理章节 {chapter_json_path} 时出错: {str(e)}")
            raise
    
    def process_all_chapters(
        self,
        storyboards_prompt_dir: Optional[str] = None,
        save_dir: Optional[str] = None
    ) -> Dict[str, Dict[str, List[str]]]:
        """
        处理所有章节的场景
        
        Args:
            storyboards_prompt_dir: 故事板提示词目录，如果为None则使用配置文件中的默认值
            save_dir: 保存目录，相对于output_root_dir的相对路径，如果为None则直接使用output_root_dir
            
        Returns:
            章节标题到场景结果映射的字典
        """
        try:
            # 使用传入的目录或配置文件中的默认值
            if storyboards_prompt_dir is None:
                storyboards_prompt_dir = self.storyboards_prompt_dir
            
            # 处理相对路径
            if not os.path.isabs(storyboards_prompt_dir):
                storyboards_prompt_dir = os.path.abspath(storyboards_prompt_dir)
            
            # 确保路径格式正确
            storyboards_prompt_dir = os.path.normpath(storyboards_prompt_dir)
            
            # 检查目录是否存在
            if not os.path.exists(storyboards_prompt_dir):
                logger.error(f"故事板提示词目录不存在: {storyboards_prompt_dir}")
                return {}
            
            # 扫描所有JSON文件
            json_files = glob.glob(os.path.join(storyboards_prompt_dir, "*.json"))
            
            if not json_files:
                logger.warning(f"在目录 {storyboards_prompt_dir} 中未找到JSON文件")
                return {}
            
            # 按章节号排序
            sorted_files = ChapterSorter.sort_chapter_files(json_files)
            
            logger.info(f"找到 {len(sorted_files)} 个章节文件，按顺序处理:")
            for i, file in enumerate(sorted_files, 1):
                logger.info(f"  {i}. {os.path.basename(file)}")
            
            all_results = {}
            
            for json_file in sorted_files:
                try:
                    chapter_results = self.process_chapter(json_file, save_dir)
                    # 使用提取的章节信息作为键，如果没有则使用文件名
                    chapter_info = extract_chapter_info(json_file)
                    chapter_key = chapter_info if chapter_info else os.path.basename(json_file).replace('.json', '')
                    all_results[chapter_key] = chapter_results
                except Exception as e:
                    logger.error(f"处理章节文件 {json_file} 时出错: {str(e)}")
                    continue
            
            logger.info(f"所有章节处理完成，共处理 {len(all_results)} 个章节")
            return all_results
            
        except Exception as e:
            logger.error(f"处理所有章节时出错: {str(e)}")
            raise
    
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