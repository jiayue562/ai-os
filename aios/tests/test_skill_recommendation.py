#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试技能推荐功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("测试技能推荐功能...")

# 导入必要模块
try:
    from scheduler.intent_recognizer import IntentRecognizer, IntentType
    from scheduler.scene_classifier import SceneClassifier, SceneType
    from aios_cli import recommend_skills
    
    print("[OK] 模块导入成功")
    
    # 创建测试实例
    recognizer = IntentRecognizer()
    classifier = SceneClassifier()
    
    # 测试用例
    test_cases = [
        ("我想学习Python编程", IntentType.GET_INFO, "S2_DEEP_LEARNING"),
        ("分析团队协作问题", IntentType.ANALYSIS_DECISION, "S4_ANALYSIS_DECISION"),
        ("创建一个AI助手项目计划", IntentType.TASK_EXECUTION, "S6_TASK_EXECUTION"),
        ("分析我的性格特点", IntentType.ANALYSIS_DECISION, "S8_CULTIVATION_CULTURE"),
        ("龙心OS需要升级优化", IntentType.SYSTEM_EVOLUTION, "S9_SYSTEM_EVOLUTION"),
    ]
    
    print("\n技能推荐测试结果：")
    print("=" * 60)
    
    for user_input, expected_intent, expected_scene in test_cases:
        print(f"\n输入: '{user_input}'")
        
        # 识别意图
        intent, intensity = recognizer.recognize(user_input)
        print(f"  识别意图: {intent.name} (预期: {expected_intent.name})")
        
        # 分类场景（使用模拟场景）
        scene = expected_scene  # 简化测试，直接使用预期场景
        
        # 推荐技能
        recommendations = recommend_skills(intent, scene, user_input)
        print(f"  推荐技能: {recommendations}")
        print(f"  推荐数量: {len(recommendations)}")
        
        # 验证推荐不为空
        if recommendations:
            print(f"  [PASS] 成功推荐技能")
        else:
            print(f"  [WARNING] 未推荐任何技能")
    
    print("\n" + "=" * 60)
    print("技能推荐测试完成！")
    
except Exception as e:
    print(f"[FAIL] 测试失败: {e}")
    import traceback
    traceback.print_exc()