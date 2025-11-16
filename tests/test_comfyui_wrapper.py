"""
测试ComfyUIWrapper工具类
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock, mock_open
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.comfyui_wrapper import ComfyUIWrapper


class TestComfyUIWrapper(unittest.TestCase):
    """ComfyUIWrapper测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.wrapper = ComfyUIWrapper(server_address="127.0.0.1:8188")
        self.test_workflow = {
            "1": {
                "inputs": {
                    "text": "测试文本",
                    "other_param": "其他参数"
                }
            },
            "9": {
                "inputs": {
                    "batch_size": 1,
                    "other_param": "其他参数"
                }
            }
        }
    
    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.wrapper.server_address, "127.0.0.1:8188")
        self.assertIsNotNone(self.wrapper.client_id)
        self.assertIsNone(self.wrapper.ws)
        
        # 测试自定义client_id
        custom_id = "custom-client-id"
        wrapper_custom = ComfyUIWrapper(client_id=custom_id)
        self.assertEqual(wrapper_custom.client_id, custom_id)
    
    @patch('src.utils.comfyui_wrapper.websocket.WebSocket')
    def test_connect_disconnect(self, mock_websocket):
        """测试连接和断开"""
        mock_ws_instance = MagicMock()
        mock_websocket.return_value = mock_ws_instance
        
        # 测试连接
        self.wrapper.connect()
        self.assertIsNotNone(self.wrapper.ws)
        mock_ws_instance.connect.assert_called_once()
        
        # 测试断开
        self.wrapper.disconnect()
        self.assertIsNone(self.wrapper.ws)
        mock_ws_instance.close.assert_called_once()
    
    def test_update_workflow_text(self):
        """测试更新工作流文本"""
        new_text = "新的文本内容"
        self.wrapper.update_workflow_text(self.test_workflow, "1", new_text)
        self.assertEqual(self.test_workflow["1"]["inputs"]["text"], new_text)
        
        # 测试无效节点ID
        with self.assertRaises(ValueError):
            self.wrapper.update_workflow_text(self.test_workflow, "999", new_text)
    
    def test_update_workflow_batch_size(self):
        """测试更新工作流批处理大小"""
        new_batch_size = 3
        self.wrapper.update_workflow_batch_size(self.test_workflow, "9", new_batch_size)
        self.assertEqual(self.test_workflow["9"]["inputs"]["batch_size"], new_batch_size)
        
        # 测试无效节点ID
        with self.assertRaises(ValueError):
            self.wrapper.update_workflow_batch_size(self.test_workflow, "999", new_batch_size)
    
    @patch('builtins.open', new_callable=mock_open, read_data='{"test": "data"}')
    def test_load_workflow_template(self, mock_file):
        """测试加载工作流模板"""
        template_path = "test_template.json"
        result = self.wrapper.load_workflow_template(template_path)
        
        mock_file.assert_called_once_with(template_path, "r", encoding="utf-8")
        self.assertEqual(result, {"test": "data"})
    
    @patch('src.utils.comfyui_wrapper.urllib.request.urlopen')
    def test_queue_prompt(self, mock_urlopen):
        """测试提交任务"""
        # 模拟服务器响应
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"prompt_id": "test-id"}'
        mock_urlopen.return_value = mock_response
        
        result = self.wrapper.queue_prompt(self.test_workflow)
        
        self.assertEqual(result["prompt_id"], "test-id")
        mock_urlopen.assert_called_once()
    
    @patch('src.utils.comfyui_wrapper.urllib.request.urlopen')
    def test_get_history(self, mock_urlopen):
        """测试获取任务历史"""
        # 模拟服务器响应
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"test-id": {"status": "completed"}}'
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = self.wrapper.get_history("test-id")
        
        self.assertEqual(result["test-id"]["status"], "completed")
        mock_urlopen.assert_called_once()
    
    @patch('src.utils.comfyui_wrapper.urllib.request.urlopen')
    def test_get_image(self, mock_urlopen):
        """测试获取图片数据"""
        # 模拟服务器响应
        mock_response = MagicMock()
        test_image_data = b"fake-image-data"
        mock_response.read.return_value = test_image_data
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = self.wrapper.get_image("test.png", "subfolder", "output")
        
        self.assertEqual(result, test_image_data)
        mock_urlopen.assert_called_once()
    
    def test_context_manager(self):
        """测试上下文管理器"""
        with patch.object(self.wrapper, 'connect') as mock_connect, \
             patch.object(self.wrapper, 'disconnect') as mock_disconnect:
            
            with self.wrapper as wrapper:
                self.assertEqual(wrapper, self.wrapper)
                mock_connect.assert_called_once()
            
            mock_disconnect.assert_called_once()
    
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    @patch.object(ComfyUIWrapper, 'get_image')
    @patch.object(ComfyUIWrapper, 'get_history')
    @patch.object(ComfyUIWrapper, 'queue_prompt')
    def test_generate_images(self, mock_queue, mock_history, mock_get_image, 
                            mock_file_open, mock_makedirs):
        """测试生成图像"""
        # 设置模拟返回值
        mock_queue.return_value = {"prompt_id": "test-id"}
        mock_history.return_value = {
            "test-id": {
                "outputs": {
                    "10": {
                        "images": [
                            {
                                "filename": "test.png",
                                "subfolder": "test_subfolder",
                                "type": "output"
                            }
                        ]
                    }
                }
            }
        }
        mock_get_image.return_value = b"fake-image-data"
        
        # 模拟WebSocket连接
        mock_ws = MagicMock()
        mock_ws.recv.return_value = '{"type": "executing", "data": {"node": null, "prompt_id": "test-id"}}'
        self.wrapper.ws = mock_ws
        
        # 调用生成图像方法
        result = self.wrapper.generate_images(self.test_workflow, save_dir="test_output")
        
        # 验证结果
        self.assertIn("test.png", result)
        self.assertEqual(result["test.png"], os.path.join("test_output", "test.png"))
        
        # 验证调用
        mock_queue.assert_called_once_with(self.test_workflow)
        mock_history.assert_called_once_with("test-id")
        mock_get_image.assert_called_once_with("test.png", "test_subfolder", "output")
        mock_makedirs.assert_called_once_with("test_output", exist_ok=True)
        mock_file_open.assert_called_once()


def run_integration_test():
    """运行集成测试（需要ComfyUI服务器运行）"""
    print("\n=== 集成测试（需要ComfyUI服务器运行）===")
    
    try:
        # 检查工作流模板文件是否存在
        template_path = "comfyui/novel_t2I_flux.json"
        if not os.path.exists(template_path):
            print(f"工作流模板文件不存在: {template_path}")
            return False
            
        # 初始化ComfyUIWrapper
        with ComfyUIWrapper() as comfy:
            print("ComfyUI连接成功")
            
            # 加载工作流模板
            workflow = comfy.load_workflow_template(template_path)
            print("工作流模板加载成功")
            
            # 更新工作流参数
            comfy.update_workflow_text(workflow, "1", "测试图像生成，简单风格，一个微笑的太阳")
            comfy.update_workflow_batch_size(workflow, "9", 1)
            print("工作流参数更新成功")
            
            # 生成图像（注释掉实际生成部分，避免不必要的资源消耗）
            # save_dir = "data/test_output"
            # output_images = comfy.generate_images(workflow, save_dir=save_dir)
            # print(f"图像生成成功: {output_images}")
            print("集成测试准备完成（实际图像生成已注释）")
            
            return True
    except Exception as e:
        print(f"集成测试失败: {str(e)}")
        return False


if __name__ == "__main__":
    # 运行单元测试
    print("=== 单元测试 ===")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # 运行集成测试
    run_integration_test()