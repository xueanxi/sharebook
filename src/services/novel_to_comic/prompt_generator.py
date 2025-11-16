"""
提示词生成器模块
用于读取storyboards JSON文件并生成适合文生图模型的英文提示词和中文旁白
"""

import os
import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path

from src.services.novel_to_comic.data_models import Scene, VisualNarrative


class PromptGenerator:
    """
    提示词生成器类
    
    功能：
    1. 读取storyboards目录下的章节JSON文件
    2. 提取场景分镜、旁白和环境氛围信息
    3. 生成每章所有画面的英文提示词和中文旁白
    4. 将结果保存到storyboards_prompt目录
    """
    
    def __init__(self, storyboards_dir: str = "data/storyboards", output_dir: str = "data/storyboards_prompt"):
        """
        初始化提示词生成器
        
        Args:
            storyboards_dir: storyboards目录路径
            output_dir: 输出目录路径
        """
        self.storyboards_dir = Path(storyboards_dir)
        self.output_dir = Path(output_dir)
        
        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def load_storyboard_file(self, chapter_file: str) -> Dict[str, Any]:
        """
        加载章节故事板JSON文件
        
        Args:
            chapter_file: 章节文件名
            
        Returns:
            章节故事板数据
        """
        file_path = self.storyboards_dir / chapter_file
        
        if not file_path.exists():
            raise FileNotFoundError(f"故事板文件不存在: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def extract_chapter_number(self, chapter_file: str) -> str:
        """
        从文件名中提取章节号
        
        Args:
            chapter_file: 章节文件名
            
        Returns:
            章节号字符串
        """
        # 匹配 "第X章" 或 "chapterX" 或 "chX" 等格式
        patterns = [
            r"第(\d+)章",
            r"chapter(\d+)",
            r"ch(\d+)",
            r"(\d+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, chapter_file.lower())
            if match:
                return match.group(1)
        
        return "unknown"
    
    def generate_english_prompt(self, scene: Dict[str, Any], visual_narrative: Dict[str, Any]) -> str:
        """
        生成英文提示词
        
        Args:
            scene: 场景数据
            visual_narrative: 视觉叙述数据
            
        Returns:
            英文提示词
        """
        # 提取场景基本信息
        scene_description = scene.get("description", "")
        scene_type = scene.get("type", "")
        setting = scene.get("setting", "")
        mood = scene.get("mood", "")
        
        # 提取视觉叙述信息
        visual_description = visual_narrative.get("visual_description", "")
        camera_angle = visual_narrative.get("camera_angle", "")
        composition = visual_narrative.get("composition", "")
        lighting = visual_narrative.get("lighting", "")
        color_scheme = visual_narrative.get("color_scheme", "")
        
        # 提取角色信息
        characters = scene.get("characters", [])
        character_descriptions = []
        
        for character in characters:
            char_name = character.get("name", "")
            char_appearance = character.get("appearance", "")
            char_expression = character.get("expression", "")
            char_action = character.get("action", "")
            
            char_desc = f"{char_name}"
            if char_appearance:
                char_desc += f", {char_appearance}"
            if char_expression:
                char_desc += f", {char_expression}"
            if char_action:
                char_desc += f", {char_action}"
                
            character_descriptions.append(char_desc)
        
        # 构建英文提示词
        prompt_parts = []
        
        # 添加场景类型和风格
        if scene_type:
            prompt_parts.append(f"{scene_type} scene")
        
        # 添加视觉描述
        if visual_description:
            prompt_parts.append(visual_description)
        
        # 添加场景描述
        if scene_description:
            prompt_parts.append(scene_description)
        
        # 添加环境设置
        if setting:
            prompt_parts.append(f"setting: {setting}")
        
        # 添加角色描述
        if character_descriptions:
            prompt_parts.append(f"characters: {', '.join(character_descriptions)}")
        
        # 添加构图和镜头角度
        if camera_angle:
            prompt_parts.append(f"camera angle: {camera_angle}")
        if composition:
            prompt_parts.append(f"composition: {composition}")
        
        # 添加光照和色彩
        if lighting:
            prompt_parts.append(f"lighting: {lighting}")
        if color_scheme:
            prompt_parts.append(f"color scheme: {color_scheme}")
        
        # 添加氛围
        if mood:
            prompt_parts.append(f"mood: {mood}")
        
        # 添加质量修饰词
        prompt_parts.append("high quality, detailed, masterpiece")
        
        # 组合成最终提示词
        english_prompt = ", ".join(prompt_parts)
        
        return english_prompt
    
    def extract_chinese_narration(self, visual_narrative: Dict[str, Any]) -> str:
        """
        提取中文旁白
        
        Args:
            visual_narrative: 视觉叙述数据
            
        Returns:
            中文旁白
        """
        # 从视觉叙述中提取旁白
        narration = visual_narrative.get("narration", "")
        
        # 如果没有旁白，尝试从描述中提取
        if not narration:
            visual_description = visual_narrative.get("visual_description", "")
            if visual_description:
                narration = visual_description
        
        return narration
    
    def generate_chapter_prompts(self, chapter_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        为章节生成所有画面的提示词和旁白
        
        Args:
            chapter_data: 章节故事板数据
            
        Returns:
            包含每个画面提示词和旁白的列表
        """
        scenes = chapter_data.get("scenes", [])
        chapter_prompts = []
        
        for i, scene in enumerate(scenes):
            # 获取场景的视觉叙述
            visual_narratives = scene.get("visual_narratives", [])
            
            # 为每个视觉叙述生成提示词和旁白
            for j, visual_narrative in enumerate(visual_narratives):
                # 生成英文提示词
                english_prompt = self.generate_english_prompt(scene, visual_narrative)
                
                # 提取中文旁白
                chinese_narration = self.extract_chinese_narration(visual_narrative)
                
                # 创建提示词对象
                prompt_data = {
                    "scene_index": i + 1,
                    "narrative_index": j + 1,
                    "english_prompt": english_prompt,
                    "chinese_narration": chinese_narration
                }
                
                chapter_prompts.append(prompt_data)
        
        return chapter_prompts
    
    def save_chapter_prompts(self, chapter_file: str, chapter_prompts: List[Dict[str, str]]) -> None:
        """
        保存章节提示词到JSON文件
        
        Args:
            chapter_file: 原始章节文件名
            chapter_prompts: 章节提示词列表
        """
        # 提取章节号
        chapter_number = self.extract_chapter_number(chapter_file)
        
        # 创建输出文件名
        output_file = self.output_dir / f"第{chapter_number}章_prompts.json"
        
        # 创建完整的数据结构
        output_data = {
            "chapter_number": chapter_number,
            "source_file": chapter_file,
            "total_prompts": len(chapter_prompts),
            "prompts": chapter_prompts
        }
        
        # 保存到文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"已保存章节提示词到: {output_file}")
    
    def process_chapter(self, chapter_file: str) -> List[Dict[str, str]]:
        """
        处理单个章节文件，生成提示词和旁白
        
        Args:
            chapter_file: 章节文件名
            
        Returns:
            生成的提示词列表
        """
        try:
            # 加载故事板文件
            chapter_data = self.load_storyboard_file(chapter_file)
            
            # 生成章节提示词
            chapter_prompts = self.generate_chapter_prompts(chapter_data)
            
            # 保存章节提示词
            self.save_chapter_prompts(chapter_file, chapter_prompts)
            
            print(f"成功处理章节: {chapter_file}, 生成了 {len(chapter_prompts)} 个提示词")
            
            return chapter_prompts
            
        except Exception as e:
            print(f"处理章节 {chapter_file} 时出错: {str(e)}")
            raise


# 主函数，用于单独运行此模块
def main():
    """
    主函数，处理指定的章节故事板文件并生成提示词
    """
    import sys
    
    if len(sys.argv) < 2:
        print("请指定要处理的章节文件名，例如: python prompt_generator.py 第二十八章.json")
        return
    
    chapter_file = sys.argv[1]
    generator = PromptGenerator()
    generator.process_chapter(chapter_file)


if __name__ == "__main__":
    main()