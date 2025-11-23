# 漫画图片生成功能模块

## 概述

漫画图片生成功能模块 (`comic_image_generation`) 是 ShareNovel 项目中专门用于生成漫画风格图片的核心组件。该模块基于 ComfyUI 平台，集成了 PuLID (Prompt-based Universal Latent IDentification) 技术，能够根据文本提示词和参考图片生成高质量、风格一致的漫画图片。

## 新功能特性

### 1. 双工作流支持

- **单角色工作流**: 使用一张参考图片生成单个角色场景
  - 工作流文件: `comfyui/novel_single_charator_refimage.json`
  - 参数: prompt, reference_image
  - 适用场景: 单个角色的特写、单人动作场景

- **多角色工作流**: 使用两张参考图片生成多角色场景
  - 工作流文件: `comfyui/novel_multi_charator_refiamge.json`
  - 参数: prompt, ref_image_1, ref_image_2
  - 适用场景: 对话场景、战斗场景、多人互动场景

### 2. 章节自动化处理

- **自动读取**: 扫描 `data/storyboards_prompt/` 目录下的所有 JSON 文件
- **智能排序**: 使用 ChapterSorter 对章节文件进行智能排序
- **场景解析**: 自动解析章节 JSON 中的场景数据
- **工作流选择**: 根据场景中角色数量自动选择合适的工作流

## 安装和设置

1. **确保 ComfyUI 服务器正在运行**
   ```bash
   # 启动 ComfyUI 服务器
   python main.py --port 8188
   ```

2. **配置文件设置**
   
   编辑 `src/services/comic_image_generation/config.yaml`:
   ```yaml
   comic_image_generation:
     paths:
       comfyui_input_dir: "D:/ComfyUI-aki-v2/ComfyUI/input/"
       single_character_workflow: "comfyui/novel_single_charator_refimage.json"
       multi_character_workflow: "comfyui/novel_multi_charator_refiamge.json"
       storyboards_prompt_dir: "data/storyboards_prompt/"
       output_root_dir: "data/storyboards_image/"
     generation:
       default_batch_size: 1
     error_handling:
       log_errors: true
       retry_count: 3
   ```

## 使用方法

### 1. 单角色图片生成

```python
from src.services.comic_image_generation import ComicImageGeneration

# 创建接口实例
comic_gen = ComicImageGeneration()

# 生成单角色图片
image_paths = comic_gen.generate_image(
    prompt="一个英俊的年轻男子，黑发，穿着现代服装，站在城市街道上，动漫风格",
    save_dir="output/single_character",
    reference_image="path/to/character_reference.jpg",
    batch_size=1
)
```

### 2. 多角色图片生成

```python
# 生成多角色图片
image_paths = comic_gen.generate_multi_character_image(
    prompt="男女主角背靠背站立，男性持盾，女性握剑，气氛严肃，背景为海洋",
    ref_image_1="path/to/male_character.jpg",
    ref_image_2="path/to/female_character.jpg",
    save_dir="output/multi_character",
    batch_size=1
)
```

### 3. 章节处理

```python
# 处理单个章节
chapter_results = comic_gen.process_chapter(
    chapter_json_path="data/storyboards_prompt/第一章.json",
    save_dir="output/chapters"
)

# 处理所有章节
all_results = comic_gen.process_all_chapters(
    storyboards_prompt_dir="data/storyboards_prompt/",
    save_dir="output/all_chapters"
)
```

### 4. 批量生成

```python
# 批量生成多张图片
prompts = [
    "主角站在山巅，俯瞰下方云海，白袍飘飘",
    "主角与神秘人对峙，气氛紧张",
    "激烈的战斗场面，剑光闪烁"
]

image_paths = comic_gen.generate_multiple_images(
    prompts=prompts,
    save_dir="output/batch",
    reference_image="path/to/character_reference.jpg",
    batch_size=1
)
```

## 章节JSON数据格式

章节JSON文件应包含以下结构：

```json
{
  "chapter_title": "第一章 遇强则强",
  "scenes": [
    {
      "scene_id": 1,
      "prompt": "主角站在山巅，俯瞰下方云海，白袍飘飘",
      "characters": ["主角"],
      "character_references": {
        "主角": "path/to/main_character.jpg"
      }
    },
    {
      "scene_id": 2,
      "prompt": "主角与神秘人对峙，气氛紧张",
      "characters": ["主角", "神秘人"],
      "character_references": {
        "主角": "path/to/main_character.jpg",
        "神秘人": "path/to/mystery_character.jpg"
      }
    }
  ]
}
```

## API 接口

### 核心方法

- `generate_image()`: 生成单角色图片
- `generate_multi_character_image()`: 生成多角色图片
- `generate_multiple_images()`: 批量生成多张图片
- `process_chapter()`: 处理单个章节的所有场景
- `process_all_chapters()`: 处理所有章节的场景

### 辅助方法

- `test_connection()`: 测试 ComfyUI 连接
- `detect_character_count()`: 检测场景中的角色数量
- `select_workflow()`: 根据角色数量选择合适的工作流

## 测试

运行基本功能测试：
```bash
python src/services/comic_image_generation/test_basic.py
```

运行综合功能测试（需要ComfyUI服务器运行）：
```bash
python src/services/comic_image_generation/test_comprehensive.py
```

## 故障排除

1. **ComfyUI连接问题**
   - 确保ComfyUI服务器正在运行
   - 检查服务器地址和端口配置

2. **工作流模板文件问题**
   - 确保工作流模板文件存在
   - 检查文件路径是否正确

3. **参考图片问题**
   - 确保参考图片文件存在
   - 检查图片格式是否支持

4. **权限问题**
   - 确保有写入输出目录的权限
   - 检查ComfyUI input目录的访问权限

## 更新日志

### v2.0.0
- 新增多角色图片生成功能
- 新增章节自动化处理功能
- 新增智能工作流选择逻辑
- 更新配置文件支持双工作流
- 增强ComfyUIWrapper功能