# ComfyUIWrapper 工具类使用说明

## 概述

ComfyUIWrapper是一个封装了ComfyUI API的工具类，提供了简化的接口来与ComfyUI服务器交互，包括工作流管理、图像生成等功能。

## 功能特性

- WebSocket连接管理
- 工作流模板加载和参数修改
- 图像生成和保存
- 任务历史查询
- 上下文管理器支持

## 安装要求

- Python 3.7+
- ComfyUI服务器运行中
- 依赖包：urllib3, json, websocket-client, os, io, time

## 基本用法

### 1. 初始化和连接

```python
from src.utils.comfyui_wrapper import ComfyUIWrapper

# 方式1：使用上下文管理器（推荐）
with ComfyUIWrapper(server_address="127.0.0.1:8188") as comfy:
    # 在这里使用comfy对象
    pass

# 方式2：手动管理连接
comfy = ComfyUIWrapper(server_address="127.0.0.1:8188")
comfy.connect()
# 使用comfy对象
comfy.disconnect()
```

### 2. 加载工作流模板

```python
# 加载JSON格式的工作流模板
workflow = comfy.load_workflow_template("path/to/workflow.json")
```

### 3. 修改工作流参数

```python
# 更新文本参数（如提示词）
comfy.update_workflow_text(workflow, "1", "新的提示词")

# 更新批处理大小
comfy.update_workflow_batch_size(workflow, "9", 2)
```

### 4. 生成图像

```python
# 生成图像并保存到指定目录
output_images = comfy.generate_images(workflow, save_dir="output/path")

# 查看生成的图像
for filename, path in output_images.items():
    print(f"生成的图像: {filename} -> {path}")
```

## 完整示例

```python
import os
from src.utils.comfyui_wrapper import ComfyUIWrapper

def generate_image_example():
    """生成图像的完整示例"""
    # 创建输出目录
    output_dir = "data/generated_images"
    os.makedirs(output_dir, exist_ok=True)
    
    # 使用上下文管理器
    with ComfyUIWrapper(server_address="127.0.0.1:8188") as comfy:
        # 加载工作流模板
        workflow = comfy.load_workflow_template("comfyui/novel_t2I_flux.json")
        
        # 设置提示词
        prompt = "一个美丽的风景画，有山脉、湖泊和日落"
        comfy.update_workflow_text(workflow, "1", prompt)
        
        # 设置批处理大小
        comfy.update_workflow_batch_size(workflow, "9", 1)
        
        # 生成图像
        output_images = comfy.generate_images(workflow, save_dir=output_dir)
        
        # 显示结果
        print(f"生成了 {len(output_images)} 张图像")
        for filename, path in output_images.items():
            print(f"图像已保存到: {path}")

if __name__ == "__main__":
    generate_image_example()
```

## API 参考

### ComfyUIWrapper 类

#### 构造函数

```python
ComfyUIWrapper(server_address="127.0.0.1:8188", client_id=None)
```

- `server_address`: ComfyUI服务器地址，格式为"host:port"
- `client_id`: 客户端ID，如果为None则自动生成

#### 方法

- `connect()`: 连接到ComfyUI服务器
- `disconnect()`: 断开连接
- `queue_prompt(workflow)`: 提交工作流到队列，返回任务ID
- `get_history(prompt_id)`: 获取任务历史
- `get_image(filename, subfolder="", folder_type="output")`: 获取图像数据
- `get_images(prompt_id, save_dir=None)`: 获取任务生成的所有图像
- `load_workflow_template(template_path)`: 加载工作流模板
- `update_workflow_text(workflow, node_id, text)`: 更新工作流中的文本参数
- `update_workflow_batch_size(workflow, node_id, batch_size)`: 更新工作流中的批处理大小
- `generate_images(workflow, save_dir=None)`: 生成图像的便捷方法

## 测试

项目包含完整的测试套件：

1. 单元测试：`tests/test_comfyui_wrapper.py`
2. 功能测试：`test_comfyui_functional.py`

运行测试：

```bash
# 运行单元测试
python tests/test_comfyui_wrapper.py

# 运行功能测试
python test_comfyui_functional.py
```

## 注意事项

1. 确保ComfyUI服务器正在运行并且可访问
2. 工作流模板必须是有效的JSON格式
3. 节点ID和参数名称必须与工作流模板匹配
4. 生成图像可能需要一些时间，取决于工作流复杂度和服务器性能

## 故障排除

### 连接错误

- 检查ComfyUI服务器是否运行
- 确认服务器地址和端口是否正确
- 检查防火墙设置

### 工作流错误

- 验证工作流模板JSON格式是否正确
- 确认节点ID和参数名称是否存在
- 检查工作流是否与ComfyUI版本兼容

### 图像生成错误

- 检查工作流参数是否正确设置
- 确认输出目录是否有写入权限
- 查看ComfyUI服务器日志获取更多错误信息