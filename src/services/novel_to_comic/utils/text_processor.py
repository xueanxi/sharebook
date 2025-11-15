"""
文本处理工具
"""

import re
from typing import List, Dict, Any, Tuple, Optional

from src.utils.logging_manager import get_logger, LogCategory

logger = get_logger(__name__, LogCategory.DATA)


class TextProcessor:
    """文本处理工具类"""
    
    def __init__(self):
        self.logger = logger
        # 对话标记
        self.dialogue_markers = ["说：", "道：", "喊道：", "问道：", "答道：", "心想：", "心里想："]
        # 动作动词
        self.action_verbs = ["走", "跑", "跳", "飞", "打", "杀", "攻击", "防御", "躲闪", "追逐", "逃跑"]
        # 环境词汇
        self.environment_words = ["天空", "大地", "山", "水", "森林", "河流", "湖泊", "海洋", "沙漠", "草原"]
    
    def normalize_text(self, text: str) -> str:
        """
        标准化文本
        
        Args:
            text: 原始文本
            
        Returns:
            标准化后的文本
        """
        # 标准化换行符
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # 删除多余空白字符
        text = re.sub(r'[ \t]+', ' ', text)  # 连续空格和制表符替换为单个空格
        
        # 删除连续3个或以上的换行符，替换为双换行符
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 删除首尾空白字符
        text = text.strip()
        
        return text
    
    def split_by_paragraphs(self, text: str) -> List[str]:
        """
        按自然段落分割文本
        
        Args:
            text: 输入文本
            
        Returns:
            段落列表
        """
        paragraphs = text.split('\n\n')
        
        # 过滤空段落
        non_empty_paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        self.logger.debug(f"将文本分割为 {len(non_empty_paragraphs)} 个段落")
        return non_empty_paragraphs
    
    def analyze_paragraph_type(self, paragraph: str) -> str:
        """
        分析段落类型
        
        Args:
            paragraph: 段落文本
            
        Returns:
            段落类型：dialogue/action/environment/mixed
        """
        has_dialogue = self._has_dialogue(paragraph)
        has_action = self._has_action(paragraph)
        has_environment = self._has_environment(paragraph)
        
        type_count = sum([has_dialogue, has_action, has_environment])
        
        if type_count == 0:
            return "other"
        elif type_count == 1:
            if has_dialogue:
                return "dialogue"
            elif has_action:
                return "action"
            else:
                return "environment"
        else:
            return "mixed"
    
    def _has_dialogue(self, text: str) -> bool:
        """检查是否包含对话"""
        # 检查引号
        if '"' in text or '"' in text or '"' in text or '「' in text or '」' in text:
            return True
        
        # 检查对话标记
        for marker in self.dialogue_markers:
            if marker in text:
                return True
        
        return False
    
    def _has_action(self, text: str) -> bool:
        """检查是否包含动作"""
        for verb in self.action_verbs:
            if verb in text:
                return True
        return False
    
    def _has_environment(self, text: str) -> bool:
        """检查是否包含环境描述"""
        for word in self.environment_words:
            if word in text:
                return True
        return False
    
    def extract_character_mentions(self, text: str, character_names: List[str]) -> List[str]:
        """
        提取文本中提及的角色
        
        Args:
            text: 输入文本
            character_names: 角色名称列表
            
        Returns:
            提及的角色列表
        """
        mentioned_characters = []
        
        for name in character_names:
            if name in text:
                mentioned_characters.append(name)
        
        # 去重并保持顺序
        seen = set()
        unique_mentions = [x for x in mentioned_characters if not (x in seen or seen.add(x))]
        
        return unique_mentions
    
    def count_content_types(self, text: str) -> Dict[str, int]:
        """
        统计内容类型数量
        
        Args:
            text: 输入文本
            
        Returns:
            内容类型统计字典
        """
        return {
            "dialogue_count": 1 if self._has_dialogue(text) else 0,
            "action_count": 1 if self._has_action(text) else 0,
            "environment_count": 1 if self._has_environment(text) else 0,
        }
    
    def split_long_paragraph(self, paragraph: str, max_length: int) -> List[str]:
        """
        分割过长的段落
        
        Args:
            paragraph: 段落文本
            max_length: 最大长度
            
        Returns:
            分割后的段落列表
        """
        if len(paragraph) <= max_length:
            return [paragraph]
        
        # 尝试在句号处分割
        sentences = re.split(r'。', paragraph)
        result = []
        current_segment = ""
        
        for sentence in sentences:
            if not sentence.strip():
                continue
                
            sentence = sentence.strip() + "。"  # 添加句号
            
            if len(current_segment + sentence) <= max_length:
                current_segment += sentence
            else:
                if current_segment:
                    result.append(current_segment.strip())
                current_segment = sentence
        
        if current_segment:
            result.append(current_segment.strip())
        
        return result
    
    def get_text_summary(self, text: str, max_length: int = 50) -> str:
        """
        获取文本摘要
        
        Args:
            text: 输入文本
            max_length: 最大长度
            
        Returns:
            文本摘要
        """
        if len(text) <= max_length:
            return text
        
        # 尝试在句号处截断
        truncated = text[:max_length]
        last_period = truncated.rfind('。')
        
        if last_period > max_length * 0.8:  # 如果句号位置合理
            return truncated[:last_period + 1]
        else:
            return truncated + "..."