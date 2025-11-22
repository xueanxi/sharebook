"""
LLM调用工具模块
"""

import json
import importlib
import sys
import importlib.util
import yaml
from typing import Dict, Any, List, Optional, Set
from pathlib import Path


class LLMUtils:
    """LLM调用工具类"""
    
    def __init__(self, llm_config_path: str = "config/llm_config.py", extraction_config_path: str = "src/services/extraction_character/config.yaml"):
        """
        初始化LLM工具
        
        Args:
            llm_config_path: LLM配置文件路径
            extraction_config_path: 角色提取配置文件路径
        """
        self.llm_config = self._load_llm_config(llm_config_path)
        self.llm = self._initialize_llm()
        self.novel_type = self._load_novel_type(extraction_config_path)
    
    
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
    
    def _load_novel_type(self, config_path: str) -> str:
        """
        加载小说类型
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            小说类型字符串
        """
        try:
            # 添加项目根目录到Python路径
            project_root = Path(__file__).parent.parent.parent.parent.parent
            if str(project_root) not in sys.path:
                sys.path.append(str(project_root))
            
            # 读取YAML配置文件
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 获取小说类型
            novel_type = config.get('extraction', {}).get('novel_type', '玄幻修真')
            return novel_type
        except Exception as e:
            print(f"加载小说类型失败: {e}")
            # 返回默认小说类型
            return "玄幻修真"
    
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
2. 严格过滤掉地名、门派名、机构名，如：XX宗、XX门、XX派、XX教、XX山、XX峰、XX城、XX寨、XX帮、XX阁、XX楼等
3. 忽略无明确名称的泛指角色（如"路人甲"、"众人"、"长老"、"弟子"等）
4. 只返回明确有个人姓名或个人称号的角色
5. 对于每个角色，尽可能识别其可能的别名、昵称或称号，但要排除通用称呼（如"他"、"她"、"姑娘"、"先生"、"爹"等）
6. 确保提取的是具体的个人角色，而不是组织、地点或群体

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
            
            # 尝试清理可能的额外内容
            result = self._clean_json_response(result)
            
            characters = json.loads(result)
            if not isinstance(characters, list):
                return []
            
            # 使用LLM二次确认每个角色是否为真实人物
            filtered_characters = []
            for character in characters:
                name = character.get("name", "").strip()
                if not name:
                    continue
                
                # 使用LLM二次确认
                if self._confirm_character_with_llm(name, chapter_content):
                    filtered_characters.append(character)
            
            return filtered_characters
        except Exception as e:
            print(f"角色提取失败: {e}")
            return []
    
    def _confirm_character_with_llm(self, character_name: str, chapter_content: str) -> bool:
        """
        使用LLM二次确认角色是否为真实人物
        
        Args:
            character_name: 待确认的角色名称
            chapter_content: 章节内容
            
        Returns:
            是否为真实人物角色
        """
        if not self.llm:
            return True  # 如果没有LLM，默认通过
        
        try:
            # 提取包含该角色的上下文片段
            context_snippets = self._extract_character_context(character_name, chapter_content)
            
            if not context_snippets:
                return False  # 如果找不到上下文，可能不是角色
            
            # 构建确认提示词
            prompt = f"""
你是一个角色识别专家。请仔细判断以下名称是否为小说中的真实人物角色。

待确认名称：{character_name}

上下文片段：
{context_snippets}

判断标准：
1. 是否有具体的人物特征描述（外貌、动作、语言、心理活动等）
2. 是否参与具体的故事情节或对话
3. 是否有个人化的行为表现（如说、想、做、感受等）
4. 是否是地名、门派名、建筑名、组织名等非人物概念

请特别注意：
- 像"李山峰"、"张天门"这样包含地名词汇的真实人名应该确认为人物
- 像"风雷宗"、"玄天宗"这样的纯地名/门派名应该被排除
- 像"山峰主"、"宗主大人"这样的职位称呼，如果指的是具体人物，应该确认为人物

请只回答：是人物 或 非人物
"""
            
            response = self.llm.invoke(prompt)
            result = response.content.strip()
            
            # 解析LLM的回答
            return "是人物" in result
            
        except Exception as e:
            print(f"LLM角色确认失败 {character_name}: {e}")
            return True  # 出错时默认通过，避免误删
    
    def _extract_character_context(self, character_name: str, chapter_content: str) -> str:
        """
        提取包含指定角色的上下文片段
        
        Args:
            character_name: 角色名称
            chapter_content: 章节内容
            
        Returns:
            上下文片段
        """
        try:
            # 分割章节为句子
            import re
            sentences = re.split(r'[。！？\n]', chapter_content)
            
            # 查找包含角色名称的句子
            relevant_sentences = []
            for sentence in sentences:
                if character_name in sentence and len(sentence.strip()) > 5:
                    relevant_sentences.append(sentence.strip())
            
            # 限制上下文长度，避免太长
            if len(relevant_sentences) > 5:
                relevant_sentences = relevant_sentences[:5]
            
            return "\n".join(relevant_sentences)
            
        except Exception as e:
            print(f"提取上下文失败: {e}")
            return ""
    
    def _clean_json_response(self, response: str) -> str:
        """
        清理LLM返回的JSON响应，去除可能的额外内容
        
        Args:
            response: 原始响应
            
        Returns:
            清理后的JSON字符串
        """
        try:
            # 尝试找到JSON数组的开始和结束
            start_idx = response.find('[')
            end_idx = response.rfind(']')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                return response[start_idx:end_idx + 1]
            
            return response
        except Exception:
            return response
    
    def _extract_json_from_text(self, text: str) -> List[Dict[str, Any]]:
        """
        从文本中提取JSON数组
        
        Args:
            text: 包含JSON的文本
            
        Returns:
            解析后的JSON数组
        """
        try:
            # 尝试找到所有JSON数组
            import re
            json_patterns = re.findall(r'\[.*?\]', text, re.DOTALL)
            
            for pattern in json_patterns:
                try:
                    return json.loads(pattern)
                except:
                    continue
            
            # 如果找不到完整的JSON数组，尝试构建一个
            return []
            
        except Exception as e:
            print(f"从文本提取JSON失败: {e}")
            return []
    
    def merge_duplicate_characters(self, characters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        合并重复的角色（基于名称相似度和特征匹配）
        
        Args:
            characters: 角色列表
            
        Returns:
            合并后的角色列表
        """
        if not self.llm:
            return characters
        
        if len(characters) <= 1:
            return characters
        
        try:
            # 构建角色信息文本用于LLM分析
            characters_text = json.dumps(characters, ensure_ascii=False, indent=2)
            
            prompt = f"""
你是一个专业的角色信息合并专家。请分析以下角色列表，识别并合并重复的角色（同一角色的不同别名或称呼）。

角色列表：
{characters_text}

任务要求：
1. 识别可能是同一角色的不同名称或别名
2. 基于角色的性别、外貌特征、角色类型等信息进行判断
3. 合并重复角色，保留最完整的角色名称作为主名称
4. 整合所有别名，去除重复
5. 合并角色特征信息，保留更详细的描述
6. 不要合并明显不同的角色

输出要求：
- 如果没有需要合并的角色，请直接返回：[]
- 如果有需要合并的角色，请严格按照以下JSON格式返回，不要添加任何其他文字说明：
[
  {{
    "name": "主角色名称",
    "aliases": ["别名1", "别名2", ...],
    "reason": "合并原因说明"
  }},
  ...
]

重要提醒：
- 只输出JSON数组，不要输出任何解释性文字
- 确保JSON格式完全正确，包括逗号、括号等
- 如果没有需要合并的角色，只输出 []
"""
            
            response = self.llm.invoke(prompt)
            result = response.content.strip()
            
            # 尝试解析JSON
            if result.startswith('```json'):
                result = result[7:-3]
            elif result.startswith('```'):
                result = result[3:-3]
            
            # 尝试清理可能的额外内容
            result = self._clean_json_response(result)
            
            # 如果没有需要合并的角色，LLM可能返回文本说明
            if not result.strip().startswith('['):
                # 检查是否包含"没有"、"空"等关键词
                if any(keyword in result for keyword in ['没有', '空', '无需', '无', '不需要', '不存在']):
                    merge_instructions = []
                else:
                    # 尝试提取JSON部分
                    merge_instructions = self._extract_json_from_text(result)
            else:
                merge_instructions = json.loads(result)
            if not isinstance(merge_instructions, list):
                print(f"角色合并分析结果格式错误: {type(merge_instructions)}")
                return characters
            
            # 执行合并操作
            return self._execute_character_merge(characters, merge_instructions)
            
        except json.JSONDecodeError as e:
            print(f"角色合并JSON解析失败: {e}")
            # 返回原始角色列表，不进行合并
            return characters
        except Exception as e:
            print(f"角色合并分析失败: {e}")
            return characters
    
    def _execute_character_merge(self, characters: List[Dict[str, Any]], merge_instructions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        执行角色合并操作
        
        Args:
            characters: 原始角色列表
            merge_instructions: 合并指令列表
            
        Returns:
            合并后的角色列表
        """
        if not merge_instructions:
            return characters
        
        merged_characters = []
        processed_names = set()
        
        # 处理合并指令
        for instruction in merge_instructions:
            main_name = instruction.get("name", "")
            aliases = instruction.get("aliases", [])
            reason = instruction.get("reason", "")
            
            if not main_name:
                continue
            
            # 收集需要合并的角色
            characters_to_merge = []
            all_names_to_merge = {main_name} | set(aliases)
            
            for character in characters:
                char_name = character.get("name", "")
                char_aliases = set(character.get("aliases", []))
                all_char_names = {char_name} | char_aliases
                
                # 检查是否有重叠
                if all_names_to_merge & all_char_names:
                    characters_to_merge.append(character)
            
            # 合并角色信息
            if characters_to_merge:
                merged_character = self._merge_character_info_list(characters_to_merge, main_name, aliases)
                merged_characters.append(merged_character)
                processed_names.update(all_names_to_merge)
        
        # 添加未处理的角色
        for character in characters:
            char_name = character.get("name", "")
            char_aliases = set(character.get("aliases", []))
            all_char_names = {char_name} | char_aliases
            
            if not all_char_names & processed_names:
                merged_characters.append(character)
        
        return merged_characters
    
    def _merge_character_info_list(self, characters: List[Dict[str, Any]], main_name: str, merged_aliases: List[str]) -> Dict[str, Any]:
        """
        合并角色信息列表
        
        Args:
            characters: 要合并的角色列表
            main_name: 主名称
            merged_aliases: 合并后的别名列表
            
        Returns:
            合并后的角色信息
        """
        # 收集所有别名
        all_aliases = set(merged_aliases)
        for character in characters:
            all_aliases.update(character.get("aliases", []))
            all_aliases.add(character.get("name", ""))
        
        # 移除主名称
        all_aliases.discard(main_name)
        
        # 选择最详细的角色特征
        best_character = None
        max_details = 0
        
        for character in characters:
            # 计算特征详细程度
            details_count = sum(1 for key in ["性别", "外貌特征", "服装特点", "角色类型"] 
                              if character.get(key) and character.get(key) != "未知")
            if details_count > max_details:
                max_details = details_count
                best_character = character
        
        # 如果没有找到最佳角色，使用第一个
        if not best_character and characters:
            best_character = characters[0]
        
        if best_character:
            result = best_character.copy()
            result["name"] = main_name
            result["aliases"] = list(all_aliases)
        else:
            result = {
                "name": main_name,
                "aliases": list(all_aliases)
            }
        
        return result

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
- 小说类型：{self.novel_type}

任务要求：
1. 判断角色性别（男/女/未知）
2. 提取外貌特征（发型、面容、身材等，50字以内）
3. 提取服装特点（衣着风格、特殊装饰等，50字以内）
4. 判断角色类型（主角/配角/反派/其他）
5. 整合和补充别名信息（如果有，不要把一些通用的，没有区分辨识度的称呼作为别名，比如"他"、"她"、"姑娘"、"先生"、"爹"等）
6. 生成英文的动漫风格容貌提示词，用于文生图生成角色上半身脸部特写，要求符合小说描述和{{novel_type}}类型风格，可以适当发挥以避免千篇一律

输出格式（JSON）：
{{
  "性别": "男/女/未知",
  "外貌特征": "外貌描述（50字以内）",
  "服装特点": "服装描述（50字以内）",
  "角色类型": "主角/配角/反派/其他",
  "别名": ["别名1", "别名2", ...],  // 如果没有别名则为空列表
  "容貌提示词": "英文的动漫风格容貌提示词，用于文生图，包含面部特征、发型、表情等细节，符合{self.novel_type}类型风格，例如：anime style, upper body, close-up portrait, young girl with long silver hair and blue eyes, gentle smile"
}}

注意：
1. 如果某项信息不明确，请填写"未知"
  2. 保持描述简洁准确（除容貌提示词外）
  3. 容貌提示词必须是英文的，应详细描述角色的面部特征、表情、气质等，适合生成动漫风格的图像
  4. 容貌提示词格式为"anime style, upper body, close-up portrait, [详细容貌描述]"，要符合小说中的角色设定和{self.novel_type}类型风格，可以适当发挥以增加独特性
  5. 确保容貌提示词符合{self.novel_type}小说类型的风格特点，避免生成与小说类型不符的图像
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
                "别名": character_aliases or [],
                "容貌提示词": f"anime style, upper body, close-up portrait, {self.novel_type} style character appearance"
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

小说类型：{self.novel_type}

任务要求：
1. 智能合并新旧信息：
   - 优先保留更详细、更准确的描述
   - 去除重复信息
   - 补充缺失信息
   - 保持描述简洁（每项不超过50字，容貌提示词除外）
2. 确保合并后的信息逻辑一致
3. 合并别名信息，去除重复，保持唯一性，不要把一些通用的，没有区分辨识度的称呼作为别名（比如"他"、"她"、"姑娘"、"先生"、"爹"等）
4. 智能合并容貌提示词，生成英文的动漫风格容貌提示词，用于文生图生成角色上半身脸部特写，要求符合小说描述和{{novel_type}}类型风格，可以适当发挥以避免千篇一律

输出格式（JSON）：
{{
  "姓名": "角色姓名",
  "性别": "男/女/未知",
  "外貌特征": "外貌描述（50字以内）",
  "服装特点": "服装描述（50字以内）",
  "角色类型": "主角/配角/反派/其他",
  "别名": ["别名1", "别名2", ...],  // 如果没有别名则为空列表
  "容貌提示词": "英文的动漫风格容貌提示词，用于文生图，包含面部特征、发型、表情等细节，符合{self.novel_type}类型风格，例如：anime style, upper body, close-up portrait, young girl with long silver hair and blue eyes, gentle smile"
}}

注意：
1. 如果某项信息不明确，请填写"未知"
2. 保持描述简洁准确（除容貌提示词外）
3. 容貌提示词必须是英文的，应详细描述角色的面部特征、表情、气质等，适合生成动漫风格的图像
4. 容貌提示词格式为"anime style, upper body, close-up portrait, [详细容貌描述]"，要符合小说中的角色设定和{{novel_type}}类型风格，可以适当发挥以增加独特性
5. 确保容貌提示词符合{{novel_type}}小说类型的风格特点，避免生成与小说类型不符的图像
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
                "别名": list(set(existing_info.get("别名", []) + new_info.get("别名", []))),
                "容貌提示词": new_info.get("容貌提示词", existing_info.get("容貌提示词", f"anime style, upper body, close-up portrait, {self.novel_type} style character appearance"))
            }