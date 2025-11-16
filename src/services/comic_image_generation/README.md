# 漫画图片生成接口

这个模块提供了一个基于ComfyUI的漫画图片生成接口，支持使用参考图片来生成一致的角色形象。

## 功能特点

- 支持参考图片输入，保持角色一致性
- 基于PuLID技术，能够精确捕捉参考图片中的角色特征
- 提供多种生成模式：单张图片生成、批量生成、角色变体生成
- 可调节的参数控制：PuLID权重、采样步数、CFG等

## 安装依赖

确保已安装项目所需的所有依赖：

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本使用

```python
from src.services.comic_image_generation import ComicImageGeneration

# 创建接口实例
comic_gen = ComicImageGeneration()

# 生成图片
image_paths = comic_gen.generate_image(
    prompt="一个英俊的年轻男子，黑发，穿着现代服装，站在城市街道上，动漫风格",
    save_dir="output/images",
    reference_image="path/to/reference/image.jpg",
    batch_size=2,
    weight=0.8,
    steps=20,
    cfg=1.0
)
```

### 角色变体生成

```python
# 生成同一角色的不同表情或姿势
variations = ["微笑的表情", "愤怒的表情", "悲伤的表情"]
results = comic_gen.generate_character_variations(
    base_prompt="一个英俊的年轻男子，黑发，穿着现代服装，动漫风格",
    variations=variations,
    reference_image="path/to/reference/image.jpg",
    save_dir="output/variations",
    batch_size=1,
    weight=0.8,
    steps=20,
    cfg=1.0
)
```

### 批量生成

```python
# 使用同一参考图片生成多个不同角色
prompts = [
    "一个美丽的年轻女子，长发，穿着传统服装",
    "一个中年男性角色，胡须，穿着盔甲",
    "一个可爱的宠物，类似小猫，有翅膀"
]
results = comic_gen.generate_multiple_images(
    prompts=prompts,
    save_dir="output/batch",
    reference_image="path/to/reference/image.jpg",
    batch_size=2,
    weight=0.7,
    steps=15,
    cfg=1.0
)
```

## 参数说明

### generate_image 方法参数

- `prompt`: 图片描述提示词
- `save_dir`: 图片保存目录
- `reference_image`: 参考图片路径（可选）
- `batch_size`: 批量生成数量，默认为1
- `weight`: PuLID权重，控制参考图片的影响程度（0.0-1.0），默认为0.8
- `steps`: 采样步数，默认为15
- `cfg`: CFG scale，默认为1.0
- `seed`: 随机种子（可选）

### 注意事项

1. **参考图片要求**：
   - 建议使用清晰、正面的人脸图片
   - 图片中人物特征应明显
   - 避免使用过小或模糊的图片

2. **PuLID权重调整**：
   - 权重越高，生成图片与参考图片越相似
   - 权重越低，生成图片越自由发挥
   - 建议从0.8开始调整

3. **ComfyUI设置**：
   - 确保ComfyUI服务器正在运行
   - 确保已安装所需的模型和插件
   - 默认工作流模板：`comfyui/novel_t2I_flux_pulid.json`

## 工作流配置

默认使用的工作流配置文件为 `comfyui/novel_t2I_flux_pulid.json`，该工作流包含以下关键节点：

- CLIP文本编码（节点1）：处理提示词
- LoadImage（节点26）：加载参考图片
- ApplyPulidFlux（节点32）：应用PuLID技术
- KSampler（节点5）：采样器
- VAEDecode（节点10）：VAE解码

可以通过 `update_workflow_template` 方法更换工作流：

```python
comic_gen.update_workflow_template("path/to/your/workflow.json")
```

## 测试

运行测试文件验证接口功能：

```bash
python src/services/comic_image_generation/test_comic_image_generation.py
```

## 示例

查看 `example_usage.py` 文件获取更多使用示例。

## 故障排除

1. **连接ComfyUI失败**：
   - 确保ComfyUI服务器正在运行
   - 检查服务器地址和端口是否正确

2. **参考图片未生效**：
   - 确保参考图片路径正确
   - 检查图片是否已上传到ComfyUI的input目录
   - 尝试调整PuLID权重

3. **生成图片质量不佳**：
   - 调整提示词描述
   - 增加采样步数
   - 调整CFG值
   - 尝试不同的随机种子