"""
故事板到提示词转换功能的提示词模板
"""

# 单场景到提示词转换提示词模板（保留原有模板作为备用）
SINGLE_SCENE_TO_PROMPT_CONVERTER = """
你是一个专业的故事板到提示词转换专家，擅长将单个场景的故事板数据转换为适合文生图模型的详细提示词。

任务：基于以下单个场景信息，生成高质量的视觉提示词，用于生成漫画图像。

背景信息：
- 小说类型：{novel_type}

故事板信息：
{scene_info}

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

# 单角色场景提示词模板
SINGLE_CHARACTER_PROMPT_TEMPLATE = """
你是一个专业的单角色场景提示词生成专家，擅长生成适合单个角色参考图的文生图提示词。

任务：基于以下单个角色场景信息，生成高质量的视觉提示词。

背景信息：
- 小说类型：{novel_type}

故事板信息：
{scene_info}

特殊要求：
1. 使用"this people"或"this character"指代角色，不要使用具体姓名
2. 重点描述角色的外观、表情、动作和情感
3. 详细描述角色与环境的互动关系
4. 确保提示词适合配合单张角色参考图使用

输出格式：
Visual Prompt:
[详细的视觉描述，使用"this people"指代角色，包含构图、角色外观、表情、动作、环境背景、光线色彩等]
"""

# 双角色场景提示词模板
DOUBLE_CHARACTER_PROMPT_TEMPLATE = """
你是一个专业的双角色场景提示词生成专家，擅长生成适合两个角色参考图的文生图提示词。

任务：基于以下双角色场景信息，生成高质量的视觉提示词，确保两个角色能够被准确区分。

背景信息：
- 小说类型：{novel_type}

故事板信息：
{scene_info}

角色特征分析：
{character_analysis}

特殊要求：
1. 分析两个角色的差异化特征（性别、外貌、服装、配饰等）
2. 使用差异化特征进行角色指代，如"this man"、"this woman"、"this character with red clothes"等
3. 重点描述两个角色之间的交互和情感交流
4. 确保提示词适合配合两张角色参考图使用

输出格式：
Character Differentiation:
[角色差异化分析，明确两个角色的区分特征]

Visual Prompt:
[详细的视觉描述，使用差异化特征指代角色，包含构图、角色交互、表情、动作、环境背景等]
"""

# 多角色场景提示词模板
MULTIPLE_CHARACTER_PROMPT_TEMPLATE = """
你是一个专业的多角色场景提示词生成专家，擅长从多个角色中筛选关键角色并生成适合的文生图提示词。

任务：基于以下多角色场景信息，筛选出最重要的两个角色并生成高质量的视觉提示词。

背景信息：
- 小说类型：{novel_type}

故事板信息：
{scene_info}

所有角色信息：
{all_characters}

角色筛选要求：
1. 基于场景重要性、角色活跃度、情感表达等维度分析所有角色
2. 筛选出对场景最关键的两个角色
3. 分析这两个角色的差异化特征

提示词生成要求：
1. 使用差异化特征进行角色指代
2. 重点描述两个关键角色之间的交互
3. 确保提示词适合配合两张角色参考图使用

输出格式：
Character Selection:
[角色筛选结果，说明选择这两个角色的理由]

Character Differentiation:
[两个关键角色的差异化特征分析]

Visual Prompt:
[详细的视觉描述，使用差异化特征指代角色，包含构图、角色交互、表情、动作等]
"""

# 角色特征分析模板
CHARACTER_FEATURE_ANALYSIS_TEMPLATE = """
你是一个角色特征分析专家，擅长分析角色特征并生成差异化描述。

任务：分析以下角色信息，提取关键特征并生成差异化描述。

角色信息：
{characters}

分析要求：
1. 提取每个角色的以下特征：
   - 性别特征（male/female/other）
   - 外貌特征（发色、体型、特殊标记等）
   - 服装特征（颜色、款式、材质等）
   - 配饰特征（武器、饰品、特殊物品等）
   - 位置特征（在场景中的相对位置）

2. 识别角色之间的明显差异
3. 生成适合用于区分角色的描述方式

输出格式：
Character Features:
[每个角色的详细特征分析]

Differentiation Strategy:
[角色差异化策略，说明如何区分不同角色]

Reference Descriptions:
[用于指代角色的差异化描述，如"this man"、"this character with red clothes"等]
"""