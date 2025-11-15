"""
提示词模板
"""

# 场景分割Agent提示词模板
SCENE_SPLITTER_PROMPT = """
你是一个专业的小说场景分析专家，擅长从小说文本中识别和提取关键场景信息。

任务：分析以下小说段落，识别其中的关键场景，并提取场景信息。

背景信息：
- 小说类型：{novel_type}
- 当前章节：{chapter_title}
- 前一场景概要：{previous_scene_summary}
- 相关角色信息：{character_info}

文本内容：
{segment_text}

请按以下要求分析：
1. 识别场景数量（每个场景应包含连贯的环境和动作）
2. 对每个场景提取以下信息：
   - 场景描述（环境、氛围、时间等）
   - 出现的角色及其状态
   - 主要动作或事件
   - 场景情绪基调
   - 场景重要性评分（1-10分）
   - 视觉表现适合度（1-10分）

注意：场景分割应保持故事的完整性和连续性，不要跳过多角色互动的重要场景。

输出格式（JSON）：{{
    "scenes": [
        {{
            "scene_id": "场景编号",
            "scene_description": "场景描述",
            "environment": "环境细节",
            "atmosphere": "氛围描述",
            "time": "时间设定",
            "characters": [
                {{
                    "name": "角色名",
                    "appearance": "外观描述",
                    "expression": "表情",
                    "action": "主要动作",
                    "emotion": "情绪状态"
                }}
            ],
            "main_action": "主要动作或事件",
            "emotional_tone": "情绪基调",
            "importance_score": 重要性评分,
            "visual_suitability": 视觉表现适合度,
            "transition_cue": "场景转换提示"
        }}
    ]
}}
"""

# 视觉文案生成Agent提示词模板
VISUAL_PROMPT = """
你是一个专业的漫画视觉设计师和文案专家，擅长将小说场景转换为适合文生图模型的视觉描述和旁白。

任务：基于以下场景信息，生成专注于单一角色特写的视觉描述和旁白文案。

背景信息：
- 小说类型：{novel_type}
- 章节标题：{chapter_title}
- 前一场景概要：{previous_scene_summary}
- 场景重要性：{importance_score}/10
- 视觉表现适合度：{visual_suitability}/10

场景信息：
{scene_info}

角色信息：
{character_details}

重要约束：
1. 每个画面只聚焦一个主要角色，确保角色一致性
2. 避免复杂构图，专注于角色特写或半身像
3. 背景简洁，不喧宾夺主
4. 突出角色情感和个性特征
5. 如果场景中有多个角色，选择当前场景最重要或情感最丰富的角色作为焦点

请按以下要求生成：

1. **视觉描述**：生成适合文生图模型的详细视觉描述，专注于：
   - 单一角色的特写或半身像构图
   - 角色面部表情和神态细节
   - 服装和配饰的精细描述
   - 简洁的背景环境
   - 适合角色造型的光线和色彩

2. **角色选择策略**：如果场景有多个角色，按以下优先级选择：
   - 选择情感表达最强烈的角色
   - 选择动作最关键的角色
   - 选择场景叙述视角的主要角色

3. **旁白文案**：生成与场景匹配的旁白，包括：
   - 场景描述性旁白
   - 角色内心独白（如适用）
   - 情绪渲染文案
   - 过渡性文案

输出格式（JSON）：{{
    "visual_description": "详细的视觉描述，适合文生图模型，专注于单一角色",
    "composition": {{
        "shot_type": "画面类型（特写/半身像/胸像）",
        "angle": "拍摄角度（平视/微仰/微俯）",
        "layout": "画面布局描述",
        "focus": "焦点元素（角色面部或上半身）"
    }},
    "character": {{
        "name": "选定的主要角色名",
        "position": "在画面中的位置",
        "pose": "姿态描述",
        "expression": "表情描述",
        "clothing_details": "服装细节",
        "action": "正在执行的动作"
    }},
    "environment": {{
        "background": "简洁背景描述",
        "atmosphere": "氛围描述",
        "lighting": "光线描述",
        "color_scheme": "色彩方案"
    }},
    "style": {{
        "art_style": "艺术风格",
        "quality_tags": "质量标签",
        "additional_details": "额外细节"
    }},
    "narration": {{
        "scene_description": "场景描述性旁白",
        "inner_monologue": "角色内心独白（如有）",
        "emotional_text": "情绪渲染文案",
        "transition_text": "过渡性文案"
    }}
}}
"""