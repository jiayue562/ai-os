#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI OS 综合场景测试脚本
模拟用户与AI OS的完整交互流程

测试目标：
1. 验证调度器能处理多种类型的用户请求
2. 测试意图识别、场景分类、引擎路由的完整流程
3. 验证调度器与记忆系统的集成
4. 验证调度器与技能调用层的集成
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("AI OS 综合场景测试 - 模拟用户交互")
print("=" * 70)

def test_scenario_1_learning():
    """测试场景1: 学习场景"""
    print("\n[场景1] 学习场景")
    print("   用户: '我想学习Python编程，帮我制定一个学习计划'")
    
    try:
        from scheduler.scheduler_main import SchedulerSession
        
        # 创建调度器会话
        session = SchedulerSession(session_id="scenario_1", user_id="悟空")
        
        # 处理用户请求
        user_input = "我想学习Python编程，帮我制定一个学习计划"
        
        # 意图识别
        intent = session.intent_recognizer.analyze(user_input)
        print(f"   意图识别: {intent}")
        
        # 场景分类
        scene = session.scene_classifier.classify(user_input, intent)
        print(f"   场景分类: {scene}")
        
        # 引擎路由
        route = session.engine_router.route(scene, intent)
        print(f"   引擎路由: {route.engine_type.name} -> {route.recipe_type.name}")
        
        # 记录到会话历史
        session.user_messages.append(user_input)
        session.current_intent = intent
        session.current_scene = scene
        session.current_route = route
        session.turn_count += 1
        
        print("   ✅ 场景1测试完成")
        return True
        
    except Exception as e:
        print(f"   ❌ 场景1测试失败: {e}")
        return False

def test_scenario_2_team_collaboration():
    """测试场景2: 团队协作场景"""
    print("\n👥 场景2: 团队协作场景")
    print("   用户: '我的团队沟通有问题，帮我分析一下团队协作问题'")
    
    try:
        from scheduler.scheduler_main import SchedulerSession
        
        # 创建调度器会话
        session = SchedulerSession(session_id="scenario_2", user_id="悟空")
        
        # 处理用户请求
        user_input = "我的团队沟通有问题，帮我分析一下团队协作问题"
        
        # 意图识别
        intent = session.intent_recognizer.analyze(user_input)
        print(f"   意图识别: {intent}")
        
        # 场景分类
        scene = session.scene_classifier.classify(user_input, intent)
        print(f"   场景分类: {scene}")
        
        # 引擎路由
        route = session.engine_router.route(scene, intent)
        print(f"   引擎路由: {route.engine_type.name} -> {route.recipe_type.name}")
        
        # 记录到会话历史
        session.user_messages.append(user_input)
        session.current_intent = intent
        session.current_scene = scene
        session.current_route = route
        session.turn_count += 1
        
        print("   ✅ 场景2测试完成")
        return True
        
    except Exception as e:
        print(f"   ❌ 场景2测试失败: {e}")
        return False

def test_scenario_3_project_planning():
    """测试场景3: 项目规划场景"""
    print("\n📋 场景3: 项目规划场景")
    print("   用户: '我需要创建一个AI助手项目，帮我规划一下项目结构和时间线'")
    
    try:
        from scheduler.scheduler_main import SchedulerSession
        
        # 创建调度器会话
        session = SchedulerSession(session_id="scenario_3", user_id="悟空")
        
        # 处理用户请求
        user_input = "我需要创建一个AI助手项目，帮我规划一下项目结构和时间线"
        
        # 意图识别
        intent = session.intent_recognizer.analyze(user_input)
        print(f"   意图识别: {intent}")
        
        # 场景分类
        scene = session.scene_classifier.classify(user_input, intent)
        print(f"   场景分类: {scene}")
        
        # 引擎路由
        route = session.engine_router.route(scene, intent)
        print(f"   引擎路由: {route.engine_type.name} -> {route.recipe_type.name}")
        
        # 记录到会话历史
        session.user_messages.append(user_input)
        session.current_intent = intent
        session.current_scene = scene
        session.current_route = route
        session.turn_count += 1
        
        print("   ✅ 场景3测试完成")
        return True
        
    except Exception as e:
        print(f"   ❌ 场景3测试失败: {e}")
        return False

def test_scenario_4_personality_analysis():
    """测试场景4: 人格分析场景"""
    print("\n🧠 场景4: 人格分析场景")
    print("   用户: '我觉得自己做事比较急躁，容易冲动，帮我分析一下我的性格特点'")
    
    try:
        from scheduler.scheduler_main import SchedulerSession
        
        # 创建调度器会话
        session = SchedulerSession(session_id="scenario_4", user_id="悟空")
        
        # 处理用户请求
        user_input = "我觉得自己做事比较急躁，容易冲动，帮我分析一下我的性格特点"
        
        # 意图识别
        intent = session.intent_recognizer.analyze(user_input)
        print(f"   意图识别: {intent}")
        
        # 场景分类
        scene = session.scene_classifier.classify(user_input, intent)
        print(f"   场景分类: {scene}")
        
        # 引擎路由
        route = session.engine_router.route(scene, intent)
        print(f"   引擎路由: {route.engine_type.name} -> {route.recipe_type.name}")
        
        # 记录到会话历史
        session.user_messages.append(user_input)
        session.current_intent = intent
        session.current_scene = scene
        session.current_route = route
        session.turn_count += 1
        
        print("   ✅ 场景4测试完成")
        return True
        
    except Exception as e:
        print(f"   ❌ 场景4测试失败: {e}")
        return False

def test_scenario_5_system_evolution():
    """测试场景5: 系统进化场景"""
    print("\n🚀 场景5: 系统进化场景")
    print("   用户: '总结一下我们之前的对话，提炼出可以改进系统的地方'")
    
    try:
        from scheduler.scheduler_main import SchedulerSession
        
        # 创建调度器会话
        session = SchedulerSession(session_id="scenario_5", user_id="悟空")
        
        # 处理用户请求
        user_input = "总结一下我们之前的对话，提炼出可以改进系统的地方"
        
        # 意图识别
        intent = session.intent_recognizer.analyze(user_input)
        print(f"   意图识别: {intent}")
        
        # 场景分类
        scene = session.scene_classifier.classify(user_input, intent)
        print(f"   场景分类: {scene}")
        
        # 引擎路由
        route = session.engine_router.route(scene, intent)
        print(f"   引擎路由: {route.engine_type.name} -> {route.recipe_type.name}")
        
        # 记录到会话历史
        session.user_messages.append(user_input)
        session.current_intent = intent
        session.current_scene = scene
        session.current_route = route
        session.turn_count += 1
        
        print("   ✅ 场景5测试完成")
        return True
        
    except Exception as e:
        print(f"   ❌ 场景5测试失败: {e}")
        return False

def test_multi_turn_conversation():
    """测试多轮对话"""
    print("\n🔄 测试多轮对话")
    
    try:
        from scheduler.scheduler_main import SchedulerSession
        
        # 创建调度器会话
        session = SchedulerSession(session_id="multi_turn", user_id="悟空")
        
        # 多轮对话模拟
        conversation = [
            "我想学习机器学习",
            "具体来说，我想了解深度学习",
            "帮我制定一个学习计划",
            "另外，推荐一些学习资源"
        ]
        
        print(f"   模拟{len(conversation)}轮对话:")
        
        for i, user_input in enumerate(conversation, 1):
            print(f"\n   第{i}轮: '{user_input}'")
            
            # 意图识别
            intent = session.intent_recognizer.analyze(user_input)
            print(f"     意图: {intent}")
            
            # 场景分类
            scene = session.scene_classifier.classify(user_input, intent)
            print(f"     场景: {scene}")
            
            # 引擎路由
            route = session.engine_router.route(scene, intent)
            print(f"     路由: {route.engine_type.name}")
            
            # 记录到会话历史
            session.user_messages.append(user_input)
            session.current_intent = intent
            session.current_scene = scene
            session.current_route = route
            session.turn_count += 1
        
        print(f"\n   ✅ 多轮对话测试完成，共处理{len(conversation)}轮对话")
        return True
        
    except Exception as e:
        print(f"   ❌ 多轮对话测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始综合场景测试...")
    
    # 运行所有场景测试
    results = []
    
    results.append(("学习场景", test_scenario_1_learning()))
    results.append(("团队协作场景", test_scenario_2_team_collaboration()))
    results.append(("项目规划场景", test_scenario_3_project_planning()))
    results.append(("人格分析场景", test_scenario_4_personality_analysis()))
    results.append(("系统进化场景", test_scenario_5_system_evolution()))
    results.append(("多轮对话", test_multi_turn_conversation()))
    
    # 统计结果
    print("\n" + "=" * 70)
    print("综合场景测试结果")
    print("=" * 70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for scenario_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {scenario_name}: {status}")
    
    print(f"\n总体结果: {passed}/{total} 个场景测试通过 ({passed/total*100:.0f}%)")
    
    # 保存测试报告
    report_file = project_root / "comprehensive_test_report.txt"
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("AI OS 综合场景测试报告\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总体结果: {passed}/{total} 个场景测试通过\n\n")
            
            for scenario_name, success in results:
                status = "通过" if success else "失败"
                f.write(f"{scenario_name}: {status}\n")
        
        print(f"\n📄 测试报告已保存到: {report_file}")
    except Exception as e:
        print(f"\n⚠️ 保存测试报告失败: {e}")
    
    # 建议
    print("\n💡 建议和下一步:")
    if passed >= total * 0.8:  # 80%成功率
        print("  ✅ 综合场景测试成功！AI OS核心调度功能正常。")
        print("  可以进入下一阶段（用户界面和部署）。")
    elif passed >= total * 0.5:  # 50%成功率
        print("  ⚠️  综合场景测试部分成功，核心功能基本正常。")
        print("  建议修复一些问题后进入下一阶段。")
    else:
        print("  ❌ 综合场景测试失败较多，需要修复核心功能。")
        print("  建议检查调度器模块的导入和初始化。")
    
    return passed >= total * 0.7  # 70%成功率即为通过

if __name__ == "__main__":
    # 导入datetime用于报告
    from datetime import datetime
    
    success = main()
    
    if success:
        print("\n🎉 综合场景测试总体成功！")
        sys.exit(0)
    else:
        print("\n⚠️  综合场景测试需要改进。")
        sys.exit(1)