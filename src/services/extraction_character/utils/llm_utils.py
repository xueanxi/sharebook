"""
LLM调用工具模块
"""

import json
import importlib
import sys
import importlib.util
from typing import Dict, Any, List, Optional
from pathlib import Path


class LLMUtils:
    """LLM调用工具类"""
    
    def __init__(self, llm_config_path: str = "config/llm_config.py"):
        """
        初始化LLM工具
        
        Args:
            llm_config_path: LLM配置文件路径
        """
        self.llm_config = self._load_llm_config(llm_config_path)
        self.llm = self._initialize_llm()
    
    def _load_llm_config(self, config_path: str) -> Dict[str, Any]:
        """
        加载LLM配置
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            LLM配置字典
        """
        try:
            # 添加项目根目录到Python路径
            project_root = Path(__file__).parent.parent.parent.parent.parent
            if str(project_root) not in sys.path:
                sys.path.append(str(project_root))
            
            # 动态导入配置模块
            spec = importlib.util.spec_from_file_location("llm_config", config_path)
            config_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config_module)
            
            # 尝试从LLMConfig类获取配置
            if hasattr(config_module, 'LLMConfig'):
                llm_config = config_module.LLMConfig.get_config()
                config = {
                    'api_base': llm_config.get('api_base', 'http://127.0.0.1:8000/v1'),
                    'model_name': llm_config.get('model_name', 'local-llm'),
                    'api_key': llm_config.get('api_key', '123'),
                    'timeout': llm_config.get('timeout', 30),
                    'max_retries': llm_config.get('max_retries', 3),
                    'temperature': llm_config.get('temperature', 0.4),
                    'max_tokens': llm_config.get('max_tokens', 2000)
                }
            else:
                # 直接从模块获取配置
                config = {
                    'api_base': getattr(config_module, 'API_BASE', 'http://127.0.0.1:8000/v1'),
                    'model_name': getattr(config_module, 'MODEL_NAME', 'local-llm'),
                    'api_key': getattr(config_module, 'API_KEY', '123'),
                    'timeout': getattr(config_module, 'TIMEOUT', 30),
                    'max_retries': getattr(config_module, 'MAX_RETRIES', 3),
                    'temperature': getattr(config_module, 'TEMPERATURE', 0.4),
                    'max_tokens': getattr(config_module, 'MAX_TOKENS', 2000)
                }
            
            return config
        except Exception as e:
            print(f"加载LLM配置失败: {e}")
            # 返回默认配置
            return {
                'api_base': 'http://127.0.0.1:8000/v1',
                'model_name': 'local-llm',
                'api_key': '123',
                'timeout': 30,
                'max_retries': 3,
                'temperature': 0.4,
                'max_tokens': 2000
            }
    
    def _initialize_llm(self):
        """
        初始化LLM客户端
        
        Returns:
            LLM客户端实例
        """
        try:
            from langchain_openai import ChatOpenAI
            
            llm = ChatOpenAI(
                api_key=self.llm_config['api_key'],
                base_url=self.llm_config['api_base'],
                model=self.llm_config['model_name'],
                temperature=self.llm_config['temperature'],
                max_tokens=self.llm_config['max_tokens'],
                timeout=self.llm_config['timeout']
            )
            
            return llm
        except Exception as e:
            print(f"初始化LLM客户端失败: {e}")
            return None
    
    def extract_characters(self, chapter_content: str) -> List[Dict[str, Any]]:
        """
        从章节内容中提取角色
        
        Args:
            chapter_content: 章节内容
            
        Returns:
            角色列表
        """
        if not self.llm:
            return []
        
        prompt = f"""
你是一个专业的小说角色提取专家。请从以下章节文本中提取所有角色名称。

任务要求：
1. 识别文本中提到的所有角色名称（包括主角、配角、反派等）
2. 忽略无明确名称的泛指角色（如"路人甲"、"众人"等）
3. 只返回明确有姓名或称号的角色
4. 对于每个角色，尽可能识别其可能的别名、昵称或称号

输出格式：
[
  {{
    "name": "角色名称",
    "aliases": ["别名1", "别名2", ...]  // 可选，如果没有别名则为空列表
  }},
  ...
]

章节文本：
{chapter_content}
"""
        
        try:
            response = self.llm.invoke(prompt)
            result = response.content.strip()
            
            # 尝试解析JSON
            if result.startswith('```json'):
                result = result[7:-3]
            elif result.startswith('```'):
                result = result[3:-3]
            
            characters = json.loads(result)
            return characters if isinstance(characters, list) else []
        except Exception as e:
            print(f"角色提取失败: {e}")
            return []
    
    def analyze_character(self, character_name: str, character_aliases: List[str] = None) -> Dict[str, Any]:
        """
        分析单个角色
        
        Args:
            character_name: 角色名称
            character_aliases: 角色别名列表
            
        Returns:
            角色分析结果
        """
        if not self.llm:
            return {}
        
        aliases_str = ", ".join(character_aliases) if character_aliases else "无"
        
        prompt = f"""
你是一个专业的小说角色分析专家。请对以下角色进行全面分析。

角色信息：
- 姓名：{character_name}
- 别名：{aliases_str}

任务要求：
1. 判断角色性别（男/女/未知）
2. 提取外貌特征（发型、面容、身材等，50字以内）
3. 提取服装特点（衣着风格、特殊装饰等，50字以内）
4. 判断角色类型（主角/配角/反派/其他）
5. 整合和补充别名信息（如果有）

输出格式（JSON）：
{{
  "性别": "男/女/未知",
  "外貌特征": "外貌描述（50字以内）",
  "服装特点": "服装描述（50字以内）",
  "角色类型": "主角/配角/反派/其他",
  "别名": ["别名1", "别名2", ...]  // 如果没有别名则为空列表
}}

注意：如果某项信息不明确，请填写"未知"。保持描述简洁准确。
"""
        
        try:
            response = self.llm.invoke(prompt)
            result = response.content.strip()
            
            # 尝试解析JSON
            if result.startswith('```json'):
                result = result[7:-3]
            elif result.startswith('```'):
                result = result[3:-3]
            
            character_info = json.loads(result)
            
            # 添加姓名字段
            character_info["姓名"] = character_name
            
            return character_info
        except Exception as e:
            print(f"角色分析失败: {e}")
            return {
                "姓名": character_name,
                "性别": "未知",
                "外貌特征": "未知",
                "服装特点": "未知",
                "角色类型": "其他",
                "别名": character_aliases or []
            }
    
    def merge_character_info(self, existing_info: Dict[str, Any], new_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        合并角色信息
        
        Args:
            existing_info: 已有角色信息
            new_info: 新角色信息
            
        Returns:
            合并后的角色信息
        """
        if not self.llm:
            # 简单合并逻辑
            return {
                "姓名": existing_info.get("姓名", new_info.get("姓名", "")),
                "性别": new_info.get("性别", existing_info.get("性别", "未知")),
                "外貌特征": new_info.get("外貌特征", existing_info.get("外貌特征", "未知")),
                "服装特点": new_info.get("服装特点", existing_info.get("服装特点", "未知")),
                "角色类型": new_info.get("角色类型", existing_info.get("角色类型", "其他")),
                "别名": list(set(existing_info.get("别名", []) + new_info.get("别名", [])))
            }
        
        prompt = f"""
你是一个专业的角色信息整合专家。请根据已有信息和新信息，合并角色数据。

已有角色信息：
{json.dumps(existing_info, ensure_ascii=False, indent=2)}

新角色信息：
{json.dumps(new_info, ensure_ascii=False, indent=2)}

任务要求：
1. 智能合并新旧信息：
   - 优先保留更详细、更准确的描述
   - 去除重复信息
   - 补充缺失信息
   - 保持描述简洁（每项不超过50字）
2. 确保合并后的信息逻辑一致
3. 合并别名信息，去除重复，保持唯一性

输出格式（JSON）：
{{
  "姓名": "角色姓名",
  "性别": "男/女/未知",
  "外貌特征": "外貌描述（50字以内）",
  "服装特点": "服装描述（50字以内）",
  "角色类型": "主角/配角/反派/其他",
  "别名": ["别名1", "别名2", ...]  // 如果没有别名则为空列表
}}

注意：如果某项信息不明确，请填写"未知"。保持描述简洁准确。
"""
        
        try:
            response = self.llm.invoke(prompt)
            result = response.content.strip()
            
            # 尝试解析JSON
            if result.startswith('```json'):
                result = result[7:-3]
            elif result.startswith('```'):
                result = result[3:-3]
            
            merged_info = json.loads(result)
            return merged_info
        except Exception as e:
            print(f"角色信息合并失败: {e}")
            # 返回简单合并结果
            return {
                "姓名": existing_info.get("姓名", new_info.get("姓名", "")),
                "性别": new_info.get("性别", existing_info.get("性别", "未知")),
                "外貌特征": new_info.get("外貌特征", existing_info.get("外貌特征", "未知")),
                "服装特点": new_info.get("服装特点", existing_info.get("服装特点", "未知")),
                "角色类型": new_info.get("角色类型", existing_info.get("角色类型", "其他")),
                "别名": list(set(existing_info.get("别名", []) + new_info.get("别名", [])))
            }