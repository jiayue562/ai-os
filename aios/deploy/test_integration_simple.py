#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI OS 适配器简单集成测试
不使用emoji字符，避免编码问题
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("AI OS 适配器简单集成测试")
print("=" * 60)

def test_imports():
    """测试导入"""
    print("\n1. 测试导入适配器...")
    
    adapters = [
        ("龙心OS适配器", "dragon_heart_adapter", "DragonHeartAdapter"),
        ("龙脑OS适配器", "dragon_brain_adapter", "DragonBrainAdapter"),
        ("龙爪OS适配器", "dragon_claw_adapter", "DragonClawAdapter"),
        ("五行人格心理学OS适配器", "five_elements_adapter", "FiveElementPersonalityAdapter"),
    ]
    
    for name, module, cls in adapters:
        try:
            mod = __import__(f"integration.{module}", fromlist=[cls])
            getattr(mod, cls)
            print(f"  [OK] {name}: 导入成功")
        except Exception as e:
            print(f"  [FAIL] {name}: 导入失败 - {e}")
    
    # 测试调度器
    try:
        from scheduler.scheduler_main import SchedulerSession
        print(f"  [OK] 调度器: 导入成功")
    except Exception as e:
        print(f"  [FAIL] 调度器: 导入失败 - {e}")
    
    # 测试技能调用层
    try:
        from skills.skill_invoker import SkillInvoker
        from skills.parameter_handler import ParameterHandler
        print(f"  [OK] 技能调用层: 导入成功")
    except Exception as e:
        print(f"  [FAIL] 技能调用层: 导入失败 - {e}")

def test_simple_instantiation():
    """测试简单实例化"""
    print("\n2. 测试简单实例化...")
    
    try:
        # 尝试导入简化版本
        from integration.dragon_heart_adapter import SimpleDragonHeartAdapter
        adapter1 = SimpleDragonHeartAdapter()
        print(f"  [OK] SimpleDragonHeartAdapter: 实例化成功")
    except Exception as e:
        print(f"  [FAIL] SimpleDragonHeartAdapter: 实例化失败 - {e}")
    
    try:
        from integration.dragon_brain_adapter import SimpleDragonBrainAdapter
        adapter2 = SimpleDragonBrainAdapter()
        print(f"  [OK] SimpleDragonBrainAdapter: 实例化成功")
    except Exception as e:
        print(f"  [FAIL] SimpleDragonBrainAdapter: 实例化失败 - {e}")
    
    try:
        from integration.dragon_claw_adapter import SimpleDragonClawAdapter
        adapter3 = SimpleDragonClawAdapter()
        print(f"  [OK] SimpleDragonClawAdapter: 实例化成功")
    except Exception as e:
        print(f"  [FAIL] SimpleDragonClawAdapter: 实例化失败 - {e}")
    
    try:
        from integration.five_elements_adapter import SimpleFiveElementsAdapter
        adapter4 = SimpleFiveElementsAdapter()
        print(f"  [OK] SimpleFiveElementsAdapter: 实例化成功")
    except Exception as e:
        print(f"  [FAIL] SimpleFiveElementsAdapter: 实例化失败 - {e}")

def test_basic_functionality():
    """测试基本功能"""
    print("\n3. 测试基本功能...")
    
    # 测试龙心OS适配器 - 使用实际存在的方法
    try:
        from integration.dragon_heart_adapter import SimpleDragonHeartAdapter
        adapter = SimpleDragonHeartAdapter()
        result = adapter.process_user_input("测试请求")
        if result and "intent" in result:
            print(f"  [OK] 龙心OS-用户输入处理: 功能正常")
        else:
            print(f"  [WARN] 龙心OS-用户输入处理: 返回结果不完整")
    except Exception as e:
        print(f"  [FAIL] 龙心OS-用户输入处理: 功能失败 - {e}")
    
    # 测试龙脑OS适配器 - 使用实际存在的方法
    try:
        from integration.dragon_brain_adapter import SimpleDragonBrainAdapter
        adapter = SimpleDragonBrainAdapter()
        # 简单适配器可能没有场景分析方法，测试它是否能响应
        result = adapter.process_user_input("学习场景分析")
        if result and "analysis" in result:
            print(f"  [OK] 龙脑OS-场景分析: 功能正常")
        else:
            print(f"  [WARN] 龙脑OS-场景分析: 返回结果不完整")
    except Exception as e:
        print(f"  [FAIL] 龙脑OS-场景分析: 功能失败 - {e}")
    
    # 测试龙爪OS适配器 - 使用实际存在的方法
    try:
        from integration.dragon_claw_adapter import SimpleDragonClawAdapter
        adapter = SimpleDragonClawAdapter()
        result = adapter.process_user_input("项目管理")
        if result and "project" in result:
            print(f"  [OK] 龙爪OS-项目管理: 功能正常")
        else:
            print(f"  [WARN] 龙爪OS-项目管理: 返回结果不完整")
    except Exception as e:
        print(f"  [FAIL] 龙爪OS-项目管理: 功能失败 - {e}")
    
    # 测试五行人格心理学OS适配器 - 使用实际存在的方法
    try:
        from integration.five_elements_adapter import SimpleFiveElementsAdapter
        adapter = SimpleFiveElementsAdapter()
        result = adapter.process_user_input("人格分析测试")
        if result and "personality" in result:
            print(f"  [OK] 五行OS-人格分析: 功能正常")
        else:
            print(f"  [WARN] 五行OS-人格分析: 返回结果不完整")
    except Exception as e:
        print(f"  [FAIL] 五行OS-人格分析: 功能失败 - {e}")

def test_scheduler_integration():
    """测试调度器集成"""
    print("\n4. 测试调度器集成...")
    
    try:
        from scheduler.scheduler_main import SchedulerSession
        
        # 创建调度器实例
        session = SchedulerSession(session_id="test_simple", user_id="悟空")
        
        # 检查配置
        has_skill_invocation = session.config.get("enable_skill_invocation", False)
        print(f"  [OK] 调度器配置检查: enable_skill_invocation = {has_skill_invocation}")
        
        # 检查记忆系统
        has_memory = session.memory_system is not None
        print(f"  [OK] 记忆系统检查: {'可用' if has_memory else '不可用'}")
        
        # 检查技能调用层
        has_skill_layer = session.skill_invoker is not None
        print(f"  [OK] 技能调用层检查: {'可用' if has_skill_layer else '不可用'}")
        
        return True
        
    except Exception as e:
        print(f"  [FAIL] 调度器集成测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始运行简单集成测试...")
    
    # 运行所有测试
    test_imports()
    test_simple_instantiation()
    test_basic_functionality()
    test_scheduler_integration()
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
    
    # 总结
    print("\n总结:")
    print("1. 所有适配器应能正常导入")
    print("2. 简化版适配器应能实例化")
    print("3. 基本功能应能正常工作")
    print("4. 调度器应能集成所有组件")
    print("\n如果上述测试大部分通过，可以进入下一阶段：")
    print("1. 创建自然语言用户接口")
    print("2. 实现技能推荐和自动触发")
    print("3. 部署到WorkBuddy环境")

if __name__ == "__main__":
    main()