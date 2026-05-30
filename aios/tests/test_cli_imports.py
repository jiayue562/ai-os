#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试CLI导入
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("测试AI OS CLI导入...")

# 测试意图识别器导入
try:
    from scheduler.intent_recognizer import IntentRecognizer, IntentType
    print("[OK] 意图识别器导入成功")
    
    # 测试意图识别
    recognizer = IntentRecognizer()
    intent, intensity = recognizer.recognize("我想学习Python编程")
    print(f"  测试识别: intent={intent.name}, intensity={intensity}")
    
except Exception as e:
    print(f"[FAIL] 意图识别器导入失败: {e}")
    import traceback
    traceback.print_exc()

# 测试场景分类器导入
try:
    from scheduler.scene_classifier import SceneClassifier
    print("[OK] 场景分类器导入成功")
except Exception as e:
    print(f"[FAIL] 场景分类器导入失败: {e}")
    import traceback
    traceback.print_exc()

# 测试调度器主类导入
try:
    from scheduler.scheduler_main import SchedulerSession
    print("[OK] 调度器主类导入成功")
except Exception as e:
    print(f"[FAIL] 调度器主类导入失败: {e}")
    import traceback
    traceback.print_exc()

# 测试记忆系统导入
try:
    from memory.memory_manager import ExtendedMemorySystem
    print("[OK] 记忆系统导入成功")
except Exception as e:
    print(f"[FAIL] 记忆系统导入失败: {e}")
    import traceback
    traceback.print_exc()

# 测试技能调用层导入
try:
    from skills.skill_invoker import SkillInvoker
    print("[OK] 技能调用层导入成功")
except Exception as e:
    print(f"[FAIL] 技能调用层导入失败: {e}")
    import traceback
    traceback.print_exc()

print("\n导入测试完成！")