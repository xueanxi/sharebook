"""
故事板到提示词转换功能的提示词模板
"""

# 单场景到提示词转换提示词模板
SINGLE_SCENE_TO_PROMPT_CONVERTER = """
你是一个专业的故事板到提示词转换专家，擅长将单个场景的故事板数据转换为适合文生图模型的详细提示词。

任务：基于以下单个场景信息，生成高质量的视觉提示词，用于生成漫画图像。

背景信息：
- 小说类型：{novel_type}

场景信息：
{scene_info}

角色信息：
{character_info}

转换要求：
1. 为当前场景生成详细的视觉提示词，确保角色一致性
2. 专注于场景中的关键视觉元素和情感表达
3. 提供适合文生图模型的详细描述，包括构图、光线、色彩等
4. 为当前场景生成相应的旁白文案，增强故事连贯性
5. 确保提示词符合漫画风格，适合连续阅读
6. 所有输出内容必须使用英文

请按以下要求生成：

1. **视觉提示词**：生成适合文生图模型的详细视觉描述，包括：
   - 场景主要构图和视角
   - 角色外观、表情和动作的详细描述
   - 环境背景和氛围
   - 光线和色彩设置
   - 适合漫画风格的艺术指导

2. **旁白文案**：生成与场景匹配的旁白，包括：
   - 场景描述性旁白
   - 角色对话或内心独白（如适用）
   - 情绪渲染文案
   - 场景过渡提示

输出格式（字符串）：
请直接输出一个字符串，包含以下内容，使用换行符分隔。所有内容必须使用英文：

Visual Prompt:
[Detailed visual prompt describing scene composition, character appearance, expressions, actions, environmental background, atmosphere, lighting and color settings, etc.]

Art Style Guidance:
[Artistic guidance suitable for comic style, including composition, lighting, color suggestions, etc.]

Character Focus:
[character appearance description, expression description, pose description, clothing description]
"""