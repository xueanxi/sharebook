# DataHelper 使用指南

## 概述

DataHelper 是一个统一的数据访问工具类，用于管理项目中 data 目录的所有访问操作。它避免了在项目各处进行路径转换，提供了统一的数据读写接口。

## 导入方式

```python
from sharebook.utils.data_helper import data_helper
```

## 主要功能

### 1. 路径获取

```python
# 获取各个目录的文件路径
raw_path = data_helper.get_raw_path("novel.txt")                    # data/raw/novel.txt
cleaned_path = data_helper.get_cleaned_novel_path("chapter1.txt")   # data/cleaned_novel/chapter1.txt
output_path = data_helper.get_output_path("result.json")           # data/output/result.json
characters_path = data_helper.get_characters_path()                # data/characters/characters.csv
character_image_path = data_helper.get_character_image_path("角色名", "image_001.png")  # data/characters/image/角色名/image_001.png
storyboard_path = data_helper.get_storyboards_path("story.json")   # data/storyboards/story.json
prompt_path = data_helper.get_storyboards_prompt_path("prompts.json")  # data/storyboards_prompt/prompts.json
```

### 2. 文件列表

```python
# 列出目录中的文件
raw_files = data_helper.list_raw_files("*.txt")                    # 返回 Path 对象列表
cleaned_files = data_helper.list_cleaned_novel_files("*.txt")
prompt_files = data_helper.list_storyboards_prompt_files("*.json")
```

### 3. 文件读写

#### 文本文件
```python
# 读取文本文件
content = data_helper.read_text_file("raw/novel.txt")
content = data_helper.read_text_file(data_helper.get_raw_path("novel.txt"))

# 写入文本文件
data_helper.write_text_file("内容", "output/result.txt")
data_helper.write_text_file("内容", data_helper.get_output_path("result.txt"))
```

#### JSON 文件
```python
# 读取 JSON 文件
data = data_helper.read_json_file("output/data.json")
data = data_helper.read_json_file(data_helper.get_output_path("data.json"))

# 写入 JSON 文件
data_helper.write_json_file({"key": "value"}, "output/data.json")
data_helper.write_json_file({"key": "value"}, data_helper.get_output_path("data.json"), indent=4)
```

#### CSV 文件
```python
import pandas as pd

# 读取 CSV 文件
df = data_helper.read_csv_file("characters/characters.csv")
df = data_helper.read_csv_file(data_helper.get_characters_path(), encoding='utf-8')

# 写入 CSV 文件
data_helper.write_csv_file(df, "output/result.csv")
data_helper.write_csv_file(df, data_helper.get_output_path("result.csv"), index=False)
```

#### YAML 文件
```python
# 读取 YAML 文件
config = data_helper.read_yaml_file("config/settings.yaml")

# 写入 YAML 文件
data_helper.write_yaml_file({"key": "value"}, "config/settings.yaml")
```

### 4. 文件检查

```python
# 检查文件是否存在
exists = data_helper.file_exists("raw/novel.txt")
exists = data_helper.file_exists(data_helper.get_raw_path("novel.txt"))

# 获取相对路径
rel_path = data_helper.get_relative_path(data_helper.get_raw_path("novel.txt"))  # 返回 "raw/novel.txt"
```

## 使用示例

### 示例 1：小说处理流程

```python
from sharebook.utils.data_helper import data_helper

# 读取原始小说
raw_files = data_helper.list_raw_files("*.txt")
for raw_file in raw_files:
    # 读取内容
    content = data_helper.read_text_file(raw_file)
    
    # 处理内容...
    processed_content = process_novel(content)
    
    # 保存到清理后目录
    cleaned_path = data_helper.get_cleaned_novel_path(raw_file.name)
    data_helper.write_text_file(processed_content, cleaned_path)
```

### 示例 2：角色数据处理

```python
import pandas as pd
from sharebook.utils.data_helper import data_helper

# 读取角色数据
characters_df = data_helper.read_csv_file(data_helper.get_characters_path())

# 处理每个角色
for _, character in characters_df.iterrows():
    character_name = character['name']
    
    # 生成角色图片路径
    image_path = data_helper.get_character_image_path(character_name, "image_001.png")
    
    # 保存角色相关信息
    character_data = {
        "name": character_name,
        "description": character['description'],
        "image_path": str(image_path)
    }
    
    output_path = data_helper.get_output_path(f"{character_name}_info.json")
    data_helper.write_json_file(character_data, output_path)
```

### 示例 3：故事板生成

```python
from sharebook.utils.data_helper import data_helper

# 处理每个章节
novel_files = data_helper.list_cleaned_novel_files("*.txt")
for novel_file in novel_files:
    # 生成故事板数据
    storyboard_data = generate_storyboard(novel_file)
    
    # 保存故事板
    storyboard_path = data_helper.get_storyboards_path(f"{novel_file.stem}_storyboards.json")
    data_helper.write_json_file(storyboard_data, storyboard_path)
    
    # 生成提示词
    prompt_data = generate_prompts(storyboard_data)
    prompt_path = data_helper.get_storyboards_prompt_path(f"{novel_file.stem}_prompts.json")
    data_helper.write_json_file(prompt_data, prompt_path)
```

## 优势

1. **统一路径管理**：所有数据路径都通过 DataHelper 管理，避免硬编码路径
2. **自动目录创建**：写入文件时自动创建必要的目录结构
3. **相对路径支持**：支持相对路径和绝对路径的自动转换
4. **类型安全**：返回 Path 对象，提供更好的类型支持
5. **错误处理**：统一的文件不存在等错误处理
6. **编码支持**：统一使用 UTF-8 编码处理中文内容

## 注意事项

1. 所有路径都是相对于项目根目录的 data 目录
2. 写入文件时会自动创建父目录
3. 文件读写默认使用 UTF-8 编码
4. 使用相对路径时，会自动相对于 data 目录进行解析
5. 建议使用 get_xxx_path() 方法获取路径，而不是直接拼接路径字符串

## 目录结构

```
data/
├── raw/                    # 原始数据文件
├── cleaned_novel/         # 清理后的小说文件
├── output/                # 输出结果文件
├── characters/            # 角色相关数据
│   ├── image/            # 角色图片
│   ├── history/          # 历史记录
│   └── characters.csv    # 角色数据表
├── storyboards/           # 故事板数据
├── storyboards_image/     # 故事板图片
├── storyboards_prompt/    # 故事板提示词
├── processed/            # 处理后的数据
└── prompts/              # 提示词数据
```