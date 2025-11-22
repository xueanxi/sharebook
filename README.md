# 小说信息提取

## 基础信息提取
```bash
python -m src.services.extraction.main data/raw --processes 2 --output data/output
```

## 角色提取系统
```bash
# 查看角色提取进度
python src/services/extraction_character/main.py --progress

# 运行完整角色提取
python src/services/extraction_character/main.py

# 重置进度并重新开始
python src/services/extraction_character/main.py --reset

# 自定义路径
python src/services/extraction_character/main.py --novel-path path/to/novels --csv-path path/to/output.csv
```

## 小说转漫画故事板生成
```bash
# 自动模式：批量处理data/cleaned_novel目录中的所有章节（推荐）
python -m src.services.novel_to_comic.main --auto

# 处理单个章节
python -m src.services.novel_to_comic.main -f "data/cleaned_novel/章节文件.txt" -t "章节标题" -n "玄幻"

# 批量处理指定目录
python -m src.services.novel_to_comic.main -d "data/cleaned_novel" -n "玄幻"

# 参数说明
# --auto: 自动模式，处理data/cleaned_novel目录中的所有章节
# -f, --file: 单个章节文件路径
# -d, --directory: 章节目录路径
# -t, --title: 章节标题（仅在使用-f时有效）
# -n, --novel-type: 小说类型（默认：玄幻）
```

### 批量处理特点
- **智能排序**：自动按章节顺序排序（支持"第X章"、"chapterX"等格式）
- **进度显示**：实时显示处理进度和每个文件的结果
- **错误容错**：单个文件失败不影响其他文件处理
- **详细统计**：完成后显示总体处理统计信息

### 输出文件
- 位置：`data/output/storyboards/`
- 格式：JSON文件，包含章节信息、段落分割、场景分析和视觉叙述
- 文件命名：`{章节标题}_storyboards.json`

## 角色图片生成
```bash
# 列出所有角色
python src/services/character_image_generation/main.py --list

# 生成单个角色图片
python src/services/character_image_generation/main.py --name 叶师弟

# 批量生成多个角色图片
python src/services/character_image_generation/main.py --names "叶师弟,羽化门,陈老狗"

# 生成所有角色图片
python src/services/character_image_generation/main.py --all

# 测试ComfyUI连接
python src/services/character_image_generation/main.py --test

# 参数说明
# --list: 列出所有可用角色
# --name: 生成指定角色的图片
# --names: 批量生成多个角色的图片，用逗号分隔
# --all: 生成所有角色的图片
# --test: 测试ComfyUI连接状态
# --output: 指定图片输出目录（默认：data/characters/image）
# --batch-size: 设置批处理大小（默认：1）
# --force: 强制重新生成已有图片的角色
```

### 功能特点
- **智能角色管理**：从CSV文件自动读取角色信息和容貌提示词
- **目录自动创建**：为每个角色创建专属的图片存储目录
- **图片有序命名**：按序号自动命名（image_001.png, image_002.png等）
- **断点续传**：支持跳过已有图片的角色，避免重复生成
- **批量处理**：支持单个角色、批量角色和全角色批量生成
- **连接检测**：提供ComfyUI连接状态检测功能

### 输出文件
- 位置：`data/characters/image/`
- 结构：每个角色一个独立目录
- 格式：PNG图片文件
- 文件命名：`image_001.png`, `image_002.png`等

## 故事板到提示词转换
```bash
# 处理所有章节
python src/services/storyboard_to_prompt/main.py --all

# 处理单个章节
python src/services/storyboard_to_prompt/main.py --chapter "data/storyboards/第一章 遇强则强_storyboards.json"

# 列出所有可用章节
python src/services/storyboard_to_prompt/main.py --list

# 验证故事板文件格式
python src/services/storyboard_to_prompt/main.py --validate "data/storyboards/第一章 遇强则强_storyboards.json"

# 清理旧备份文件
python src/services/storyboard_to_prompt/main.py --clean-backups --keep 5

# 导出处理报告
python src/services/storyboard_to_prompt/main.py --export-report

# 参数说明
# --all: 处理所有章节
# --chapter: 处理指定章节的故事板文件
# --list: 列出所有可用章节
# --validate: 验证故事板文件格式
# --clean-backups: 清理旧备份文件
# --keep: 保留备份文件数量 (默认: 10)
# --export-report: 导出处理报告
# --no-batch-optimize: 跳过批量优化
# --output: 指定输出目录
# --config: 指定配置文件路径
# --verbose, -v: 详细输出
```

### 功能特点
- **智能提示词生成**：根据故事板场景信息自动生成图像生成提示词
- **批量优化**：支持批量优化提示词，确保风格一致性
- **文件验证**：提供故事板文件格式验证功能
- **备份管理**：自动备份处理结果，支持备份文件管理
- **进度跟踪**：详细记录处理进度和结果统计
- **错误处理**：完善的错误处理和日志记录机制

### 输出文件
- 位置：`data/storyboards_prompt/`
- 格式：JSON文件，包含场景提示词、负面提示词和元数据
- 文件命名：`{章节标题}_prompts.json`
- 备份：自动创建备份文件，文件名包含时间戳

