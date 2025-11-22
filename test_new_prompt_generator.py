#!/usr/bin/env python3
"""
测试新的提示词生成功能
"""

import os
import sys
import json
from pathlib import Path

# 获取项目根目录
current_file = os.path.abspath(__file__)
root_path = os.path.dirname(current_file)
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from src.services.storyboard_to_prompt.prompt_generator import PromptGenerator
from src.utils.logging_manager import LogModule, get_module_logger

logger = get_module_logger(LogModule.STORYBOARD_TO_PROMPT)

def test_single_character_prompt():
    """测试单角色提示词生成"""
    print("=== 测试单角色提示词生成 ===")
    
    # 创建单角色测试场景
    single_character_scene = {
        "scene_id": "test_single_001",
        "scene_description": "主角叶君临独自站在湖边，凝视湖面倒影。",
        "environment": "静谧湖畔，湖面如镜，倒映着天空与山影。",
        "atmosphere": "寂静中带着一丝神秘与压抑。",
        "time": "清晨，薄雾未散。",
        "characters": [
            {
                "name": "叶君临",
                "appearance": "银发如雪，眉如刀锋，面容冷峻俊朗，身穿玄色长袍绣银纹云纹。",
                "expression": "震惊和愤怒，双目赤红，眉头紧锁。",
                "action": "低头凝视湖面倒影，身体微微颤抖。",
                "emotion": "极度震惊与悲愤"
            }
        ],
        "main_action": "叶君临在湖边醒来，发现身体已变为一名白发及腰、满脸皱纹的老者。",
        "emotional_tone": "荒诞、愤怒、悲怆",
        "visual_narrative": {
            "composition": {
                "shot_type": "特写",
                "angle": "微仰",
                "layout": "角色居中，面部占据画面三分之二。",
                "focus": "角色面部与眉心银纹"
            },
            "environment": {
                "background": "极简背景，仅保留湖面倒影的虚化轮廓。",
                "atmosphere": "寂静中蕴含压抑与神秘。",
                "lighting": "晨曦透过云层洒下淡金色光芒。",
                "color_scheme": "主色调为银白、玄黑与淡金。"
            },
            "style": {
                "art_style": "中国玄幻风格，融合写实与幻想元素。",
                "quality_tags": "8K高清，超细节，电影级光影。",
                "additional_details": "湖面倒影中，叶君临的面容短暂扭曲。"
            }
        }
    }
    
    try:
        generator = PromptGenerator()
        prompt = generator.generate_prompt(single_character_scene)
        
        print("生成的单角色提示词:")
        print(prompt)
        print()
        
        # 检查是否使用了"this people"指代
        if "this people" in prompt or "this character" in prompt:
            print("✓ 正确使用了通用指代方式")
        else:
            print("✗ 未使用通用指代方式")
            
        # 检查是否避免了角色姓名
        if "叶君临" not in prompt:
            print("✓ 成功避免了使用角色姓名")
        else:
            print("✗ 仍然使用了角色姓名")
            
    except Exception as e:
        print(f"单角色测试失败: {e}")
    
    print()

def test_double_character_prompt():
    """测试双角色提示词生成"""
    print("=== 测试双角色提示词生成 ===")
    
    # 创建双角色测试场景
    double_character_scene = {
        "scene_id": "test_double_001",
        "scene_description": "叶君临与魔教教主对峙，气氛紧张。",
        "environment": "玄天宗大殿，庄严肃穆。",
        "atmosphere": "紧张对峙，剑拔弩张。",
        "time": "正午时分。",
        "characters": [
            {
                "name": "叶君临",
                "appearance": "银发如雪，身穿玄色长袍绣银纹云纹。",
                "expression": "冷静沉着，眼神锐利。",
                "action": "手持古剑，与魔教教主对峙。",
                "emotion": "警惕与决心"
            },
            {
                "name": "魔教教主",
                "appearance": "黑衣蒙面，身形高大，气势逼人。",
                "expression": "阴冷狡诈，眼中闪烁寒光。",
                "action": "步步紧逼，试图压制叶君临。",
                "emotion": "傲慢与杀意"
            }
        ],
        "main_action": "两大高手在玄天宗大殿内展开激烈对峙。",
        "emotional_tone": "紧张、激烈、一触即发",
        "visual_narrative": {
            "composition": {
                "shot_type": "中景",
                "angle": "平视",
                "layout": "两人分立两侧，形成对峙构图。",
                "focus": "两人之间的紧张关系"
            },
            "environment": {
                "background": "玄天宗大殿内部，雕梁画栋。",
                "atmosphere": "庄严肃穆中透着紧张。",
                "lighting": "正午阳光透过殿窗洒下。",
                "color_scheme": "玄黑与银白的对比。"
            },
            "style": {
                "art_style": "中国玄幻风格，强调气势对比。",
                "quality_tags": "8K高清，动态构图，强烈对比。",
                "additional_details": "两人之间有无形的气场碰撞。"
            }
        }
    }
    
    try:
        generator = PromptGenerator()
        prompt = generator.generate_prompt(double_character_scene)
        
        print("生成的双角色提示词:")
        print(prompt)
        print()
        
        # 检查是否使用了差异化描述
        if "this man" in prompt or "this character" in prompt:
            print("✓ 使用了差异化角色描述")
        else:
            print("✗ 未使用差异化角色描述")
            
        # 检查是否避免了角色姓名
        if "叶君临" not in prompt and "魔教教主" not in prompt:
            print("✓ 成功避免了使用角色姓名")
        else:
            print("✗ 仍然使用了角色姓名")
            
    except Exception as e:
        print(f"双角色测试失败: {e}")
    
    print()

def test_multiple_character_prompt():
    """测试多角色提示词生成"""
    print("=== 测试多角色提示词生成 ===")
    
    # 创建多角色测试场景
    multiple_character_scene = {
        "scene_id": "test_multiple_001",
        "scene_description": "玄天宗大殿内，多人汇聚，讨论重要事宜。",
        "environment": "玄天宗大殿，庄严肃穆。",
        "atmosphere": "严肃讨论，气氛凝重。",
        "time": "上午时分。",
        "characters": [
            {
                "name": "叶君临",
                "appearance": "银发如雪，身穿玄色长袍绣银纹云纹。",
                "expression": "冷静沉着，眼神锐利。",
                "action": "坐在主位，倾听众人发言。",
                "emotion": "审慎与思考"
            },
            {
                "name": "红千叶",
                "appearance": "红衣如火，美艳动人，身姿曼妙。",
                "expression": "关切担忧，眉头微蹙。",
                "action": "站在叶君身边，不时侧目看向叶君临。",
                "emotion": "担忧与关切"
            },
            {
                "name": "灵儿",
                "appearance": "青衣少女，活泼可爱，双瞳灵动。",
                "expression": "好奇兴奋，大眼睛闪烁。",
                "action": "坐在旁边，认真听着大人们讨论。",
                "emotion": "好奇与专注"
            },
            {
                "name": "老者",
                "appearance": "白发苍苍，身穿灰袍，面容慈祥。",
                "expression": "严肃凝重，捻须沉思。",
                "action": "站在下方，向叶君临汇报情况。",
                "emotion": "严肃与忧虑"
            }
        ],
        "main_action": "玄天宗众人汇聚大殿，讨论应对外敌的策略。",
        "emotional_tone": "严肃、凝重、团结一致",
        "visual_narrative": {
            "composition": {
                "shot_type": "全景",
                "angle": "俯视",
                "layout": "多人分层布局，叶君临居于中心。",
                "focus": "整体氛围与人物关系"
            },
            "environment": {
                "background": "玄天宗大殿全景，气势恢宏。",
                "atmosphere": "庄严肃穆中透着凝重。",
                "lighting": "上午阳光透过殿窗洒下。",
                "color_scheme": "多种颜色的和谐统一。"
            },
            "style": {
                "art_style": "中国玄幻风格，宏大场面。",
                "quality_tags": "8K高清，宏大构图，细节丰富。",
                "additional_details": "殿内气氛凝重，众人神情各异。"
            }
        }
    }
    
    try:
        generator = PromptGenerator()
        prompt = generator.generate_prompt(multiple_character_scene)
        
        print("生成的多角色提示词:")
        print(prompt)
        print()
        
        # 检查是否使用了差异化描述
        if "this man" in prompt or "this character" in prompt or "this woman" in prompt:
            print("✓ 使用了差异化角色描述")
        else:
            print("✗ 未使用差异化角色描述")
            
        # 检查是否避免了所有角色姓名
        names = ["叶君临", "红千叶", "灵儿", "老者"]
        used_names = [name for name in names if name in prompt]
        if not used_names:
            print("✓ 成功避免了使用所有角色姓名")
        else:
            print(f"✗ 仍然使用了角色姓名: {used_names}")
            
    except Exception as e:
        print(f"多角色测试失败: {e}")
    
    print()

def main():
    """主测试函数"""
    print("开始测试新的提示词生成功能...")
    print()
    
    # 测试单角色场景
    test_single_character_prompt()
    
    # 测试双角色场景
    test_double_character_prompt()
    
    # 测试多角色场景
    test_multiple_character_prompt()
    
    print("测试完成！")

if __name__ == "__main__":
    main()