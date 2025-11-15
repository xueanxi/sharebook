"""
处理参数配置
"""

# 文本分割参数
SEGMENT_MAX_LENGTH = 800  # 每个段落最大长度
SEGMENT_MIN_LENGTH = 200  # 每个段落最小长度

# 场景分割参数
SCENE_MIN_LENGTH = 100    # 每个场景最小长度
SCENE_MAX_LENGTH = 300    # 每个场景最大长度

# Agent配置
SCENE_SPLITTER_CONFIG = {
    "temperature": 0.3,  # 较低温度，确保场景分割的一致性
    "max_tokens": 2000,
}

VISUAL_GENERATOR_CONFIG = {
    "temperature": 0.5,  # 中等温度，平衡创造性和一致性
    "max_tokens": 3000,
}

# 输出配置
OUTPUT_DIR = "data/storyboards"  # 故事板输出目录

# 错误处理配置
MAX_RETRIES = 3  # 最大重试次数
RETRY_DELAY = 2  # 重试延迟(秒)

# 并行处理配置
ENABLE_PARALLEL_SCENE_SPLITTING = True  # 是否启用并行场景分割
MAX_SCENE_SPLITTING_CONCURRENT = 5  # 场景分割最大并发数