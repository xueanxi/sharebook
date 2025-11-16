"""
ComfyUI工具类，用于与ComfyUI服务器交互生成图像
"""

import websocket
import uuid
import json
import urllib.request
import urllib.parse
import os
import time
from typing import Dict, Any, Optional, List


class ComfyUIWrapper:
    """ComfyUI API封装类，提供图像生成功能"""
    
    def __init__(self, server_address: str = "127.0.0.1:8188", client_id: Optional[str] = None):
        """
        初始化ComfyUI连接
        
        Args:
            server_address: ComfyUI服务器地址，默认为127.0.0.1:8188
            client_id: 客户端ID，如果不提供将自动生成
        """
        self.server_address = server_address
        self.client_id = client_id or str(uuid.uuid4())
        self.ws = None
        
    def connect(self) -> None:
        """建立WebSocket连接"""
        try:
            self.ws = websocket.WebSocket()
            self.ws.connect(f"ws://{self.server_address}/ws?clientId={self.client_id}")
            # 设置WebSocket接收超时为5秒，以便定期检查
            self.ws.settimeout(5)
        except Exception as e:
            raise ConnectionError(f"无法连接到ComfyUI服务器 {self.server_address}: {str(e)}")
        
    def disconnect(self) -> None:
        """断开WebSocket连接"""
        if self.ws:
            try:
                self.ws.close()
            except:
                pass
            self.ws = None
            
    def queue_prompt(self, prompt: Dict[str, Any]) -> Dict[str, Any]:
        """
        向ComfyUI服务器提交任务
        
        Args:
            prompt: ComfyUI工作流提示词
            
        Returns:
            包含prompt_id的响应字典
        """
        try:
            p = {"prompt": prompt, "client_id": self.client_id}
            data = json.dumps(p).encode('utf-8')
            req = urllib.request.Request(f"http://{self.server_address}/prompt", data=data)
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read())
        except Exception as e:
            raise ConnectionError(f"提交任务到ComfyUI服务器失败: {str(e)}")
        
    def get_history(self, prompt_id: str) -> Dict[str, Any]:
        """
        获取任务历史
        
        Args:
            prompt_id: 任务ID
            
        Returns:
            任务历史数据
        """
        try:
            with urllib.request.urlopen(f"http://{self.server_address}/history/{prompt_id}", timeout=30) as response:
                return json.loads(response.read())
        except Exception as e:
            raise ConnectionError(f"获取任务历史失败: {str(e)}")
            
    def get_image(self, filename: str, subfolder: str, image_type: str) -> bytes:
        """
        获取图片数据
        
        Args:
            filename: 图片文件名
            subfolder: 子文件夹
            image_type: 图片类型
            
        Returns:
            图片二进制数据
        """
        try:
            data = {"filename": filename, "subfolder": subfolder, "type": image_type}
            url_values = urllib.parse.urlencode(data)
            with urllib.request.urlopen(f"http://{self.server_address}/view?{url_values}", timeout=60) as response:
                return response.read()
        except Exception as e:
            raise ConnectionError(f"获取图片数据失败: {str(e)}")
            
    def generate_images(
        self, 
        prompt: Dict[str, Any], 
        save_dir: str = "data/characters/image",
        connect_if_needed: bool = True
    ) -> Dict[str, str]:
        """
        生成图像并保存到指定目录
        
        Args:
            prompt: ComfyUI工作流提示词
            save_dir: 图像保存目录
            connect_if_needed: 如果未连接是否自动连接
            
        Returns:
            包含文件名和保存路径的字典
        """
        # 确保WebSocket连接
        if not self.ws and connect_if_needed:
            self.connect()
            
        if not self.ws:
            raise ConnectionError("WebSocket连接未建立，请先调用connect()方法")
            
        # 提交任务
        prompt_id = self.queue_prompt(prompt)['prompt_id']
        output_images = {}
        
        # 等待任务完成，不设置整体超时，但使用WebSocket超时进行定期检查
        start_time = time.time()
        last_heartbeat = time.time()
        
        while True:
            try:
                # 设置WebSocket接收超时为5秒，以便定期检查
                self.ws.settimeout(5)
                
                try:
                    out = self.ws.recv()
                    if isinstance(out, str):
                        message = json.loads(out)
                        if message['type'] == 'executing':
                            data = message['data']
                            # 当收到执行完成的消息时，退出循环
                            if data['node'] is None and data['prompt_id'] == prompt_id:
                                break
                        elif message['type'] == 'progress':
                            # 打印进度信息
                            data = message['data']
                            if 'value' in data and 'max' in data:
                                logger.info(f"生成进度: {data['value']}/{data['max']}")
                except websocket.WebSocketTimeoutException:
                    # WebSocket接收超时，继续循环
                    pass
                
                # 定期打印心跳信息，每30秒一次
                current_time = time.time()
                if current_time - last_heartbeat > 30:
                    elapsed = int(current_time - start_time)
                    logger.info(f"图片生成中，已等待 {elapsed} 秒...")
                    last_heartbeat = current_time
                    
            except Exception as e:
                logger.error(f"等待图片生成时出错: {str(e)}")
                raise
        
        # 任务完成后，查询历史并获取图片
        try:
            history = self.get_history(prompt_id)[prompt_id]
            for node_id in history['outputs']:
                node_output = history['outputs'][node_id]
                if 'images' in node_output:
                    for image in node_output['images']:
                        image_data = self.get_image(image['filename'], image['subfolder'], image['type'])
                        
                        # 确保保存目录存在
                        os.makedirs(save_dir, exist_ok=True)
                        
                        # 保存图片到指定目录
                        image_path = os.path.join(save_dir, image['filename'])
                        with open(image_path, 'wb') as f:
                            f.write(image_data)
                        
                        # 记录保存的图片路径
                        output_images[image['filename']] = image_path
                        logger.info(f"图片已保存到: {image_path}")
        except Exception as e:
            logger.error(f"保存生成的图片时出错: {str(e)}")
            raise
        
        return output_images
        
    def load_workflow_template(self, template_path: str) -> Dict[str, Any]:
        """
        加载工作流模板
        
        Args:
            template_path: 模板文件路径
            
        Returns:
            工作流模板数据
        """
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise ValueError(f"加载工作流模板失败: {str(e)}")
            
    def update_workflow_text(self, workflow: Dict[str, Any], node_id: str, text: str) -> None:
        """
        更新工作流中的文本参数
        
        Args:
            workflow: 工作流数据
            node_id: 节点ID
            text: 新的文本内容
        """
        if node_id in workflow and "inputs" in workflow[node_id] and "text" in workflow[node_id]["inputs"]:
            workflow[node_id]["inputs"]["text"] = text
        else:
            raise ValueError(f"无法找到节点 {node_id} 或其文本输入参数")
            
    def update_workflow_batch_size(self, workflow: Dict[str, Any], node_id: str, batch_size: int) -> None:
        """
        更新工作流中的批处理大小参数
        
        Args:
            workflow: 工作流数据
            node_id: 节点ID
            batch_size: 批处理大小
        """
        if node_id in workflow and "inputs" in workflow[node_id] and "batch_size" in workflow[node_id]["inputs"]:
            workflow[node_id]["inputs"]["batch_size"] = batch_size
        else:
            raise ValueError(f"无法找到节点 {node_id} 或其batch_size参数")
            
    def __enter__(self):
        """上下文管理器入口，自动建立连接"""
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口，自动断开连接"""
        self.disconnect()


# 添加logger引用
import logging
logger = logging.getLogger(__name__)