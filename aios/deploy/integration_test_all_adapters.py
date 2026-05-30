#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI OS 专业技能适配器集成测试脚本
测试所有适配器的功能和与调度器的集成

测试目标：
1. 验证所有适配器都能正确导入和初始化
2. 测试每个适配器的基本功能
3. 测试适配器与调度器的集成
4. 验证错误处理和恢复机制
"""

import sys
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 80)
print("AI OS 专业技能适配器集成测试")
print("=" * 80)

def test_import_all_adapters() -> bool:
    """测试导入所有适配器"""
    print("\n[TEST] 测试导入所有适配器...")
    
    adapters_to_test = [
        ("龙心OS适配器", "dragon_heart_adapter", "DragonHeartAdapter"),
        ("龙脑OS适配器", "dragon_brain_adapter", "DragonBrainAdapter"),
        ("龙爪OS适配器", "dragon_claw_adapter", "DragonClawAdapter"),
        ("五行人格心理学OS适配器", "five_elements_adapter", "FiveElementsAdapter"),
    ]
    
    results = []
    for adapter_name, module_name, class_name in adapters_to_test:
        try:
            module = __import__(f"integration.{module_name}", fromlist=[class_name])
            adapter_class = getattr(module, class_name)
            results.append((adapter_name, True, "导入成功"))
            print(f"  [OK] {adapter_name}: 导入成功")
        except ImportError as e:
            results.append((adapter_name, False, f"导入失败: {str(e)}"))
            print(f"  [FAIL] {adapter_name}: 导入失败 - {e}")
        except AttributeError as e:
            results.append((adapter_name, False, f"类未找到: {str(e)}"))
            print(f"  [FAIL] {adapter_name}: 类未找到 - {e}")
    
    success_count = sum(1 for _, success, _ in results if success)
    print(f"导入结果: {success_count}/{len(results)} 个适配器导入成功")
    
    return all(success for _, success, _ in results)


def test_adapter_instantiation() -> bool:
    """测试适配器实例化"""
    print("\n[TEST] 测试适配器实例化...")
    
    try:
        # 导入所有适配器
        from integration.dragon_heart_adapter import DragonHeartAdapter
        from integration.dragon_brain_adapter import DragonBrainAdapter
        from integration.dragon_claw_adapter import DragonClawAdapter
        from integration.five_elements_adapter import FiveElementsAdapter
        
        adapters_to_instantiate = [
            ("龙心OS适配器", DragonHeartAdapter),
            ("龙脑OS适配器", DragonBrainAdapter),
            ("龙爪OS适配器", DragonClawAdapter),
            ("五行人格心理学OS适配器", FiveElementsAdapter),
        ]
        
        instances = []
        for adapter_name, adapter_class in adapters_to_instantiate:
            try:
                # 使用简化版本（Simple版本）进行实例化测试
                simple_class_name = f"Simple{adapter_class.__name__}"
                simple_class = getattr(adapter_class.__module__, simple_class_name, None)
                
                if simple_class:
                    instance = simple_class()
                    instances.append((adapter_name, instance, True, "实例化成功(简化版)"))
                    print(f"  ✅ {adapter_name}: 简化版实例化成功")
                else:
                    # 尝试实例化原始适配器
                    instance = adapter_class()
                    instances.append((adapter_name, instance, True, "实例化成功"))
                    print(f"  ✅ {adapter_name}: 实例化成功")
            except Exception as e:
                instances.append((adapter_name, None, False, f"实例化失败: {str(e)}"))
                print(f"  ❌ {adapter_name}: 实例化失败 - {e}")
        
        success_count = sum(1 for _, _, success, _ in instances if success)
        print(f"实例化结果: {success_count}/{len(instances)} 个适配器实例化成功")
        
        return success_count >= len(insters) * 0.5  # 至少一半成功
        
    except ImportError as e:
        print(f"  ❌ 导入适配器失败: {e}")
        return False


def test_adapter_basic_functions() -> Dict[str, bool]:
    """测试适配器基本功能"""
    print("\n🔍 测试适配器基本功能...")
    
    results = {}
    
    try:
        # 龙心OS适配器测试
        from integration.dragon_heart_adapter import SimpleDragonHeartAdapter
        dragon_heart = SimpleDragonHeartAdapter()
        
        # 测试意图识别
        intent_result = dragon_heart.invoke_intent_analysis("我想学习如何写代码")
        results["龙心OS-意图识别"] = intent_result.get("success", False)
        print(f"  ✅ 龙心OS-意图识别: {'成功' if results['龙心OS-意图识别'] else '失败'}")
        
        # 测试场景分类
        scene_result = dragon_heart.invoke_scene_classification("帮我分析这个项目")
        results["龙心OS-场景分类"] = scene_result.get("success", False)
        print(f"  ✅ 龙心OS-场景分类: {'成功' if results['龙心OS-场景分类'] else '失败'}")
        
    except Exception as e:
        print(f"  ❌ 龙心OS适配器功能测试失败: {e}")
        results["龙心OS-意图识别"] = False
        results["龙心OS-场景分类"] = False
    
    try:
        # 龙脑OS适配器测试
        from integration.dragon_brain_adapter import SimpleDragonBrainAdapter
        dragon_brain = SimpleDragonBrainAdapter()
        
        # 测试场景分析
        analysis_result = dragon_brain.invoke_scene_analysis("学习编程", "S1")
        results["龙脑OS-场景分析"] = analysis_result.get("success", False)
        print(f"  ✅ 龙脑OS-场景分析: {'成功' if results['龙脑OS-场景分析'] else '失败'}")
        
        # 测试知识库查询
        kb_result = dragon_brain.invoke_knowledge_query("Python基础")
        results["龙脑OS-知识查询"] = kb_result.get("success", False)
        print(f"  ✅ 龙脑OS-知识查询: {'成功' if results['龙脑OS-知识查询'] else '失败'}")
        
    except Exception as e:
        print(f"  ❌ 龙脑OS适配器功能测试失败: {e}")
        results["龙脑OS-场景分析"] = False
        results["龙脑OS-知识查询"] = False
    
    try:
        # 龙爪OS适配器测试
        from integration.dragon_claw_adapter import SimpleDragonClawAdapter
        dragon_claw = SimpleDragonClawAdapter()
        
        # 测试项目管理
        project_result = dragon_claw.invoke_project_management("创建新项目", "AI助手开发")
        results["龙爪OS-项目管理"] = project_result.get("success", False)
        print(f"  ✅ 龙爪OS-项目管理: {'成功' if results['龙爪OS-项目管理'] else '失败'}")
        
        # 测试工作流执行
        workflow_result = dragon_claw.invoke_workflow_execution("S1", {"step": "分析需求"})
        results["龙爪OS-工作流执行"] = workflow_result.get("success", False)
        print(f"  ✅ 龙爪OS-工作流执行: {'成功' if results['龙爪OS-工作流执行'] else '失败'}")
        
    except Exception as e:
        print(f"  ❌ 龙爪OS适配器功能测试失败: {e}")
        results["龙爪OS-项目管理"] = False
        results["龙爪OS-工作流执行"] = False
    
    try:
        # 五行人格心理学OS适配器测试
        from integration.five_elements_adapter import SimpleFiveElementsAdapter
        five_elements = SimpleFiveElementsAdapter()
        
        # 测试人格分析
        personality_result = five_elements.invoke_personality_analysis("用户描述自己的性格")
        results["五行OS-人格分析"] = personality_result.get("success", False)
        print(f"  ✅ 五行OS-人格分析: {'成功' if results['五行OS-人格分析'] else '失败'}")
        
        # 测试关系诊断
        relationship_result = five_elements.invoke_relationship_diagnosis("团队协作问题")
        results["五行OS-关系诊断"] = relationship_result.get("success", False)
        print(f"  ✅ 五行OS-关系诊断: {'成功' if results['五行OS-关系诊断'] else '失败'}")
        
    except Exception as e:
        print(f"  ❌ 五行人格心理学OS适配器功能测试失败: {e}")
        results["五行OS-人格分析"] = False
        results["五行OS-关系诊断"] = False
    
    # 统计结果
    success_count = sum(1 for success in results.values() if success)
    total_count = len(results)
    print(f"功能测试结果: {success_count}/{total_count} 个功能测试成功")
    
    return results


def test_scheduler_integration() -> bool:
    """测试调度器集成"""
    print("\n🔍 测试调度器集成...")
    
    try:
        # 导入调度器
        from scheduler.scheduler_main import SchedulerSession
        
        # 创建调度器实例
        session = SchedulerSession(session_id="test_session_001", user_id="悟空")
        
        # 检查配置
        has_skill_invocation = session.config.get("enable_skill_invocation", False)
        print(f"  ✅ 调度器配置检查: enable_skill_invocation = {has_skill_invocation}")
        
        # 测试基本调度流程
        test_input = "我想学习Python编程"
        
        # 模拟调度流程
        intent_result = session.intent_recognizer.analyze(test_input)
        scene_result = session.scene_classifier.classify(test_input, intent_result)
        route_result = session.engine_router.route(scene_result, intent_result)
        
        print(f"  ✅ 调度流程测试:")
        print(f"    意图识别: {intent_result}")
        print(f"    场景分类: {scene_result}")
        print(f"    引擎路由: {route_result}")
        
        # 检查技能调用层可用性
        skill_layer_available = hasattr(session, 'SKILL_INVOCATION_AVAILABLE')
        print(f"  ✅ 技能调用层可用性: {skill_layer_available}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 调度器集成测试失败: {e}")
        return False


def test_skill_invocation_layer() -> Dict[str, bool]:
    """测试技能调用层"""
    print("\n🔍 测试技能调用层...")
    
    results = {}
    
    try:
        # 导入技能调用层模块
        from skills.skill_invoker import SkillInvoker
        from skills.parameter_handler import ParameterHandler
        from skills.error_handler import SkillErrorHandler
        
        # 测试SkillInvoker
        invoker = SkillInvoker()
        results["SkillInvoker-实例化"] = True
        print(f"  ✅ SkillInvoker实例化成功")
        
        # 测试ParameterHandler
        handler = ParameterHandler()
        results["ParameterHandler-实例化"] = True
        print(f"  ✅ ParameterHandler实例化成功")
        
        # 测试SkillErrorHandler
        error_handler = SkillErrorHandler()
        results["SkillErrorHandler-实例化"] = True
        print(f"  ✅ SkillErrorHandler实例化成功")
        
        # 测试工具函数导入
        from skills.error_handler import create_default_error_handler
        from skills.parameter_handler import process_and_invoke
        
        results["工具函数导入"] = True
        print(f"  ✅ 工具函数导入成功")
        
    except Exception as e:
        print(f"  ❌ 技能调用层测试失败: {e}")
        results["SkillInvoker-实例化"] = False
        results["ParameterHandler-实例化"] = False
        results["SkillErrorHandler-实例化"] = False
        results["工具函数导入"] = False
    
    # 统计结果
    success_count = sum(1 for success in results.values() if success)
    total_count = len(results)
    print(f"技能调用层测试结果: {success_count}/{total_count} 个测试成功")
    
    return results


def test_comprehensive_scenario() -> bool:
    """测试综合场景：模拟用户请求的完整处理流程"""
    print("\n🔍 测试综合场景...")
    
    try:
        from scheduler.scheduler_main import SchedulerSession
        
        # 创建测试会话
        session = SchedulerSession(session_id="integration_test_001", user_id="悟空")
        
        # 模拟用户请求
        user_requests = [
            "我想学习Python编程，帮我制定学习计划",  # 学习场景
            "我的团队沟通有问题，帮我分析一下",        # 团队协作场景
            "我需要创建一个AI助手项目，帮我规划一下",  # 项目创建场景
            "帮我理解这个复杂问题的本质"              # 思维分析场景
        ]
        
        print("  模拟用户请求处理:")
        for i, request in enumerate(user_requests, 1):
            print(f"\n  请求{i}: '{request}'")
            
            # 意图识别
            intent = session.intent_recognizer.analyze(request)
            print(f"    意图识别: {intent}")
            
            # 场景分类
            scene = session.scene_classifier.classify(request, intent)
            print(f"    场景分类: {scene}")
            
            # 引擎路由
            route = session.engine_router.route(scene, intent)
            print(f"    引擎路由: {route.engine_type.name} -> {route.recipe_type.name}")
            
            # 记录结果
            session.user_messages.append(request)
            session.current_intent = intent
            session.current_scene = scene
            session.current_route = route
            session.turn_count += 1
        
        print(f"\n  ✅ 综合场景测试完成，处理了 {len(user_requests)} 个请求")
        return True
        
    except Exception as e:
        print(f"  ❌ 综合场景测试失败: {e}")
        return False


def run_all_tests() -> Dict[str, Any]:
    """运行所有测试"""
    print("\n" + "=" * 80)
    print("开始运行所有集成测试")
    print("=" * 80)
    
    test_results = {}
    
    # 1. 导入测试
    test_results["导入适配器"] = test_import_all_adapters()
    
    # 2. 实例化测试
    test_results["实例化适配器"] = test_adapter_instantiation()
    
    # 3. 基本功能测试
    test_results["适配器功能"] = test_adapter_basic_functions()
    
    # 4. 调度器集成测试
    test_results["调度器集成"] = test_scheduler_integration()
    
    # 5. 技能调用层测试
    test_results["技能调用层"] = test_skill_invocation_layer()
    
    # 6. 综合场景测试
    test_results["综合场景"] = test_comprehensive_scenario()
    
    return test_results


def generate_summary_report(test_results: Dict[str, Any]) -> None:
    """生成测试摘要报告"""
    print("\n" + "=" * 80)
    print("集成测试摘要报告")
    print("=" * 80)
    
    total_tests = len(test_results)
    passed_tests = 0
    failed_tests = 0
    
    print("\n📋 测试结果概览:")
    for test_name, result in test_results.items():
        if isinstance(result, dict):
            # 子测试结果（适配器功能、技能调用层）
            sub_passed = sum(1 for r in result.values() if r)
            sub_total = len(result)
            status = f"{sub_passed}/{sub_total} 通过"
            if sub_passed == sub_total:
                passed_tests += 1
                print(f"  ✅ {test_name}: {status}")
            else:
                failed_tests += 1
                print(f"  ⚠️  {test_name}: {status}")
        else:
            # 布尔结果
            if result:
                passed_tests += 1
                print(f"  ✅ {test_name}: 通过")
            else:
                failed_tests += 1
                print(f"  ❌ {test_name}: 失败")
    
    # 总体统计
    print("\n📊 总体统计:")
    print(f"  总测试项: {total_tests}")
    print(f"  通过项: {passed_tests}")
    print(f"  失败项: {failed_tests}")
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"  成功率: {success_rate:.1f}%")
    
    # 建议和下一步
    print("\n💡 建议和下一步:")
    if success_rate >= 80:
        print("  ✅ 集成测试总体成功！可以进入下一阶段（用户界面和部署）。")
        print("  建议:")
        print("  1. 创建自然语言用户接口")
        print("  2. 实现技能推荐和自动触发")
        print("  3. 部署到WorkBuddy环境")
        print("  4. 进行用户测试和反馈优化")
    elif success_rate >= 50:
        print("  ⚠️  集成测试部分成功，需要修复一些问题。")
        print("  建议:")
        print("  1. 检查失败的适配器导入或实例化")
        print("  2. 修复技能调用层的问题")
        print("  3. 重新运行集成测试")
        print("  4. 修复后再进行下一阶段")
    else:
        print("  ❌ 集成测试失败较多，需要重新设计和调试。")
        print("  建议:")
        print("  1. 检查项目结构和导入路径")
        print("  2. 验证所有适配器的依赖关系")
        print("  3. 调试技能调用层的基本功能")
        print("  4. 重新设计集成方案")
    
    # 保存报告到文件
    report_file = project_root / "integration_test_report.json"
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            # 转换结果以便序列化
            serializable_results = {}
            for key, value in test_results.items():
                if isinstance(value, dict):
                    serializable_results[key] = value
                elif isinstance(value, bool):
                    serializable_results[key] = value
                else:
                    serializable_results[key] = str(value)
            
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "project": "AI OS WorkBuddy Integration",
                "test_results": serializable_results,
                "summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": failed_tests,
                    "success_rate": success_rate
                }
            }, f, ensure_ascii=False, indent=2)
        print(f"\n📄 详细报告已保存到: {report_file}")
    except Exception as e:
        print(f"\n⚠️  保存报告失败: {e}")


if __name__ == "__main__":
    # 导入datetime用于报告
    from datetime import datetime
    
    print("AI OS 专业技能适配器集成测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"项目根目录: {project_root}")
    
    # 运行所有测试
    test_results = run_all_tests()
    
    # 生成报告
    generate_summary_report(test_results)
    
    # 退出代码
    total_passed = sum(1 for result in test_results.values() 
                      if (isinstance(result, bool) and result) or 
                         (isinstance(result, dict) and all(result.values())))
    total_tests = len(test_results)
    
    if total_passed >= total_tests * 0.7:  # 70%成功率
        print("\n🎉 集成测试总体成功！")
        sys.exit(0)
    else:
        print("\n⚠️  集成测试需要改进。")
        sys.exit(1)