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
# 处理单个章节
python -m src.services.novel_to_comic.main -f "data/cleaned_novel/章节文件.txt" -t "章节标题" -n "玄幻"

# 处理整个目录
python -m src.services.novel_to_comic.main -d "data/cleaned_novel" -n "玄幻"

# 参数说明
# -f, --file: 单个章节文件路径
# -d, --directory: 章节目录路径
# -t, --title: 章节标题（仅在使用-f时有效）
# -n, --novel-type: 小说类型（默认：玄幻）
```

### 输出文件
- 位置：`data/output/storyboards/`
- 格式：JSON文件，包含章节信息、段落分割、场景分析和视觉叙述
- 文件命名：`{章节标题}_storyboards.json`

