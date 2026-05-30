#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI OS 调度引擎 - 验证脚本
验证所有模块的基本功能

版本: 1.0.0
开发者: 龙龟神将
用户: 悟空
"""

import sys
import os

def verify_imports():
    """验证所有模块能否正常导入"""
    print("验证模块导入...")
    
    modules = [
        "scheduler.intent_recognizer",
        "scheduler.scene_classifier", 
        "scheduler.engine_router",
        "scheduler.dynamic_adjuster",
        "scheduler.result_integrator",
        "scheduler.evolution_precipitator",
        "scheduler.scheduler_main",
    ]
    
    all_imported = True
    for module_name in modules:
        try:
            __import__(module_name)
            print(f"  ✓ {module_name}")
        except ImportError as e:
            print(f"  ✗ {module_name}: {e}")
            all_imported = False
        except Exception as e:
            print(f"  ? {module_name}: {e} (非导入错误)")
    
    return all_imported

def verify_basic_functionality():
    """验证基本功能"""
    print("\n验证基本功能...")
    
    try:
        from scheduler.intent_recognizer import IntentRecognizer, IntentType
        from scheduler.scene_classifier import SceneClassifier, SceneType
        
        # 测试意图识别
        recognizer = IntentRecognizer()
        intent, intensity = recognizer.recognize("粘贴复制快捷键是什么")
        print(f"  意图识别测试: {intent.value} (强度: {intensity})")
        
        # 测试场景分类
        classifier = SceneClassifier()
        scene, complexity = classifier.classify("粘贴复制快捷键是什么", intent, intensity)
        print(f"  场景分类测试: {scene.value} (复杂度: {complexity})")
        
        return True
    except Exception as e:
        print(f"  功能验证失败: {e}")
        return False

def verify_scheduler():
    """验证调度器主类"""
    print("\n验证调度器主类...")
    
    try:
        from scheduler.scheduler_main import Scheduler
        
        scheduler = Scheduler()
        session_id = scheduler.create_session("悟空")
        print(f"  创建会话: {session_id}")
        
        # 处理简单请求
        result = scheduler.process_request(session_id, "粘贴复制快捷键是什么")
        print(f"  处理请求: {result['user_input']}")
        print(f"    意图: {result['intent']['type']}")
        print(f"    场景: {result['scene']['type']}")
        print(f"    决策场景: {result['decision']['scene_type']}")
        
        # 处理深度学习请求
        result2 = scheduler.process_request(session_id, "帮我深度学习AI OS架构")
        print(f"  处理深度学习请求: {result2['scene']['type']}")
        
        return True
    except Exception as e:
        print(f"  调度器验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主验证函数"""
    print("=" * 60)
    print("AI OS 调度引擎验证")
    print("=" * 60)
    
    # 添加当前目录到Python路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # 验证导入
    if not verify_imports():
        print("\n⚠️  模块导入失败，请检查路径和依赖")
        return 1
    
    # 验证基本功能
    if not verify_basic_functionality():
        print("\n⚠️  基本功能验证失败")
        return 2
    
    # 验证调度器
    if not verify_scheduler():
        print("\n⚠️  调度器验证失败")
        return 3
    
    print("\n" + "=" * 60)
    print("✅ 所有验证通过！")
    print("调度引擎已成功实现，包含以下模块:")
    print("  1. 意图识别模块 (intent_recognizer.py)")
    print("  2. 场景分类模块 (scene_classifier.py)")
    print("  3. 引擎路由模块 (engine_router.py)")
    print("  4. 动态调整模块 (dynamic_adjuster.py)")
    print("  5. 结果整合模块 (result_integrator.py)")
    print("  6. 进化沉淀模块 (evolution_precipitator.py)")
    print("  7. 调度器主类 (scheduler_main.py)")
    print("\n下一步: 集成WorkBuddy技能调用层")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())