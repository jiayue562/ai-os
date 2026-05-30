#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI OS 命令行界面 (CLI)
让编程小白通过自然语言与AI OS交互

使用方法:
  python aios_cli.py

功能:
  1. 用户输入自然语言请求
  2. AI OS分析意图、分类场景、路由引擎
  3. 显示处理结果和推荐技能
  4. 支持多轮对话
  5. 记录对话历史
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("AI 龙龟共生伙伴操作系统 (AI OS)")
print("版本: 1.0.0 (WorkBuddy集成版)")
print("用户: 悟空 (编程小白)")
print("助手: 龙龟神将")
print("=" * 70)
print()
print("欢迎使用AI OS！我是你的龙龟神将，可以帮你:")
print("  1. 学习新知识 (深度学习、编程、方法论)")
print("  2. 分析决策 (项目规划、团队协作、问题解决)")
print("  3. 人格分析 (五行人格心理学、性格优化)")
print("  4. 创新突破 (思维模型、创意激发)")
print("  5. 系统进化 (总结复盘、持续改进)")
print()
print("提示: 直接用自然语言告诉我你的需求，我会自动调度合适的技能帮你。")
print("输入 '退出' 或 'quit' 结束对话")
print("输入 '帮助' 或 'help' 查看帮助")
print("输入 '状态' 或 'status' 查看系统状态")
print("=" * 70)

def print_system_status():
    """打印系统状态"""
    print("\n[系统状态]")
    print("  组件状态:")
    
    # 检查调度器
    try:
        from scheduler.scheduler_main import SchedulerSession
        print("  [OK] 调度器: 可用")
    except Exception as e:
        print(f"  [FAIL] 调度器: 不可用 ({e})")
    
    # 检查记忆系统
    try:
        from memory.memory_manager import ExtendedMemorySystem
        print("  [OK] 记忆系统: 可用")
    except Exception as e:
        print(f"  [FAIL] 记忆系统: 不可用 ({e})")
    
    # 检查技能调用层
    try:
        from skills.skill_invoker import SkillInvoker
        print("  [OK] 技能调用层: 可用")
    except Exception as e:
        print(f"  [FAIL] 技能调用层: 不可用 ({e})")
    
    # 检查专业技能适配器
    adapters = [
        ("龙心OS适配器", "dragon_heart_adapter", "DragonHeartAdapter"),
        ("龙脑OS适配器", "dragon_brain_adapter", "DragonBrainAdapter"),
        ("龙爪OS适配器", "dragon_claw_adapter", "DragonClawAdapter"),
        ("五行人格心理学OS适配器", "five_elements_adapter", "FiveElementPersonalityAdapter"),
    ]
    
    print("  专业技能适配器:")
    for name, module, cls in adapters:
        try:
            mod = __import__(f"integration.{module}", fromlist=[cls])
            getattr(mod, cls)
            print(f"    [OK] {name}: 可用")
        except Exception:
            print(f"    [FAIL] {name}: 不可用")

def print_help():
    """打印帮助信息"""
    print("\n[帮助]")
    print("  可用命令:")
    print("    help, 帮助 - 显示此帮助信息")
    print("    status, 状态 - 显示系统状态")
    print("    history, 历史 - 显示对话历史")
    print("    clear, 清除 - 清除对话历史")
    print("    quit, 退出, exit - 退出程序")
    print()
    print("  示例请求:")
    print("    '我想学习Python编程'")
    print("    '帮我分析团队协作问题'")
    print("    '创建一个AI助手项目计划'")
    print("    '分析我的性格特点'")
    print("    '总结我们今天的对话'")

def recommend_skills(intent, scene, user_input, context=None):
    """
    智能推荐技能
    
    参数:
        intent: 意图类型 (IntentType)
        scene: 场景类型 
        user_input: 用户输入文本
        context: 上下文信息（可选）
        
    返回:
        list: 推荐的技能名称列表
    """
    if context is None:
        context = {}
    
    skill_recommendations = []
    
    # 基于意图的推荐
    intent_based = {
        "GET_INFO": ["龙脑OS (知识学习引擎)", "知识学习智能体", "信息检索技能"],
        "DEEP_UNDERSTANDING": ["龙脑OS (深度学习引擎)", "象思维智能体", "知识图谱构建"],
        "CREATIVE_BREAKTHROUGH": ["龙脑OS (创新突破引擎)", "五色光思维", "创意激发技能"],
        "ANALYSIS_DECISION": ["龙脑OS (分析决策引擎)", "结构化分析技能", "决策矩阵工具"],
        "TASK_EXECUTION": ["龙爪OS (项目执行引擎)", "知行合一智能体", "工作流引擎"],
        "SYSTEM_EVOLUTION": ["龙心OS (系统进化引擎)", "进化沉淀技能", "复盘总结工具"]
    }
    
    intent_name = intent.name if hasattr(intent, 'name') else str(intent)
    for key, skills in intent_based.items():
        if key in intent_name:
            skill_recommendations.extend(skills)
            break
    
    # 基于场景的推荐
    scene_str = str(scene)
    scene_based = {
        "S0_EXTREME_SIMPLE": [],  # 极简场景不需要额外技能
        "S1_INFORMATION_QUERY": ["快速信息检索", "知识库查询"],
        "S2_DEEP_LEARNING": ["深度学习路径规划", "知识体系构建", "学习进度跟踪"],
        "S3_INNOVATION_BREAKTHROUGH": ["创新方法论", "头脑风暴工具", "原型设计"],
        "S4_ANALYSIS_DECISION": ["数据分析工具", "决策支持系统", "风险评估"],
        "S5_MAJOR_DECISION": ["重大决策框架", "多方利益分析", "长期影响评估"],
        "S6_TASK_EXECUTION": ["项目管理工具", "任务分解技能", "进度监控"],
        "S7_SYSTEM_PLANNING": ["系统架构设计", "技术选型分析", "实施路线图"],
        "S8_CULTIVATION_CULTURE": ["五行人格心理学OS", "性格分析工具", "行为改变计划"],
        "S9_SYSTEM_EVOLUTION": ["系统性能监控", "用户反馈分析", "持续改进流程"]
    }
    
    for scene_key, skills in scene_based.items():
        if scene_key in scene_str:
            skill_recommendations.extend(skills)
            break
    
    # 基于用户输入关键词的推荐
    keyword_mapping = {
        "学习": ["学习路径规划", "知识要点提炼", "学习效果评估"],
        "团队": ["团队协作分析", "沟通效率优化", "角色分配建议"],
        "项目": ["项目章程制定", "里程碑规划", "风险管理"],
        "性格": ["人格特质分析", "优势劣势评估", "发展建议"],
        "创新": ["创意生成工具", "可行性分析", "创新实验设计"],
        "决策": ["选项分析", "利弊权衡", "结果预测"],
        "五行": ["五行人格分析", "相生相克关系", "平衡建议"],
        "龙心": ["调度优化", "场景识别改进", "引擎性能调优"],
        "龙脑": ["思维模型库", "方法论应用", "知识关联"],
        "龙爪": ["工作流设计", "SOP标准化", "执行效率提升"]
    }
    
    user_input_lower = user_input.lower()
    for keyword, skills in keyword_mapping.items():
        if keyword in user_input_lower:
            skill_recommendations.extend(skills)
    
    # 去重并保留顺序
    seen = set()
    unique_recommendations = []
    for skill in skill_recommendations:
        if skill not in seen:
            seen.add(skill)
            unique_recommendations.append(skill)
    
    # 限制推荐数量（最多5个）
    return unique_recommendations[:5]

def process_user_input(session, user_input, conversation_history):
    """处理用户输入"""
    print(f"\n[用户] {user_input}")
    
    try:
        # 导入必要的模块
        from scheduler.dynamic_adjuster import AdjustmentAction
        
        # 记录用户输入
        conversation_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # 使用调度器处理请求
        print("[系统] 正在分析你的请求...")
        
        # 意图识别
        intent, intensity_score = session.intent_recognizer.recognize(user_input)
        print(f"  [识别意图] {intent.value} (强度: {intensity_score}/10)")
        
        # 场景分类
        scene = session.scene_classifier.classify(user_input, intent)
        print(f"  [分类场景] {scene}")
        
        # 引擎路由
        route = session.engine_router.route(scene, intent)
        print(f"  [路由引擎] {route.engine_type.name}")
        print(f"  [使用配方] {route.recipe_type.name}")
        
        # 动态调整（如果启用）
        if session.config.get("enable_dynamic_adjustment", True):
            adjustment = session.dynamic_adjuster.adjust(route, user_input)
            if adjustment.action != AdjustmentAction.NO_CHANGE:
                print(f"  [动态调整] {adjustment.action.name}")
                route = adjustment.new_route
        
        # 根据意图、场景和用户输入智能推荐技能
        skill_recommendations = recommend_skills(intent, scene, user_input, context={"is_follow_up": False})
        
        if skill_recommendations:
            print(f"  [推荐技能] {', '.join(skill_recommendations)}")
        
        # 生成响应
        response = generate_response(intent, scene, route, skill_recommendations)
        print(f"\n[龙龟神将] {response}")
        
        # 记录助手响应
        conversation_history.append({
            "role": "assistant",
            "content": response,
            "intent": str(intent),
            "scene": str(scene),
            "engine": route.engine_type.name,
            "recipe": route.recipe_type.name,
            "timestamp": datetime.now().isoformat()
        })
        
        # 更新会话状态
        session.user_messages.append(user_input)
        session.current_intent = intent
        session.current_scene = scene
        session.current_route = route
        session.turn_count += 1
        
        # 检查是否触发系统进化
        if session.turn_count % 5 == 0 and session.config.get("enable_evolution_precipitation", True):
            print(f"\n[系统] 已进行{session.turn_count}轮对话，触发系统进化沉淀...")
            # 这里可以添加进化沉淀逻辑
        
        return True
        
    except Exception as e:
        print(f"\n[错误] 处理请求时出错: {e}")
        print("建议: 请重新表述你的请求，或尝试其他类型的请求。")
        return False

def generate_response(intent, scene, route, skill_recommendations):
    """根据分析结果生成自然语言响应"""
    
    # 基础响应模板
    templates = {
        "GET_INFO": [
            "我了解到你想获取关于{topic}的信息。",
            "根据你的问题，我找到了相关的知识资源。",
            "我来帮你查找{domain}领域的信息。"
        ],
        "DEEP_UNDERSTANDING": [
            "你希望深入理解{concept}，这是一个很好的学习目标。",
            "我将引导你深度学习{subject}的核心概念。",
            "让我们一起来探索{field}的深度知识。"
        ],
        "CREATIVE_BREAKTHROUGH": [
            "你希望进行{area}领域的创新突破。",
            "我将用创新思维方法帮你激发新想法。",
            "让我们用创造性思维探索{domain}的新可能性。"
        ],
        "ANALYSIS_DECISION": [
            "你需要对{situation}进行分析和决策。",
            "我将帮你系统分析这个问题，找到最佳方案。",
            "让我们用结构化思维来分析这个决策场景。"
        ],
        "TASK_EXECUTION": [
            "你想执行{task}任务，我来帮你规划实施步骤。",
            "我将协助你完成{project}的项目执行。",
            "让我们制定{action}的具体行动计划。"
        ],
        "SYSTEM_EVOLUTION": [
            "你想要总结复盘，促进系统进化。",
            "我将帮你提炼经验，优化系统性能。",
            "让我们从历史对话中学习，推动系统持续改进。"
        ]
    }
    
    # 选择响应模板
    intent_str = str(intent)
    template_key = "GET_INFO"  # 默认
    
    for key in templates:
        if key in intent_str:
            template_key = key
            break
    
    template = templates[template_key][0]
    
    # 根据场景和路由添加具体内容
    response_parts = [template]
    
    # 添加引擎信息
    engine_info = f"我已经调度了{route.engine_type.name}引擎，使用{route.recipe_type.name}配方来处理你的请求。"
    response_parts.append(engine_info)
    
    # 添加技能推荐
    if skill_recommendations:
        skills_text = "我推荐使用" + "、".join(skill_recommendations) + "来更好地解决你的问题。"
        response_parts.append(skills_text)
    
    # 添加下一步建议
    next_steps = {
        "S1_INFORMATION_QUERY": "如果你需要更详细的信息，可以告诉我具体关注哪些方面。",
        "S2_DEEP_LEARNING": "我们可以从基础概念开始，逐步深入，你觉得怎么样？",
        "S4_ANALYSIS_DECISION": "我们可以先用MECE分析法拆解问题，再用决策矩阵评估选项。",
        "S6_TASK_EXECUTION": "我们可以用甘特图规划时间线，用PDCA循环确保执行质量。",
        "S8_CULTIVATION_CULTURE": "我们可以从觉察开始，逐步培养新的思维和行为模式。"
    }
    
    scene_str = str(scene)
    for scene_key, suggestion in next_steps.items():
        if scene_key in scene_str:
            response_parts.append(suggestion)
            break
    
    return " ".join(response_parts)

def save_conversation_history(history, filepath="conversation_history.json"):
    """保存对话历史到文件"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        print(f"\n[系统] 对话历史已保存到: {filepath}")
    except Exception as e:
        print(f"\n[系统] 保存对话历史失败: {e}")

def main():
    """主函数"""
    conversation_history = []
    
    try:
        # 导入调度器
        from scheduler.scheduler_main import SchedulerSession
        
        # 创建调度器会话
        session = SchedulerSession(session_id=f"SES_{datetime.now().strftime('%Y%m%d_%H%M%S')}", user_id="悟空")
        print("[系统] AI OS初始化完成，准备就绪!")
        
    except Exception as e:
        print(f"[系统] AI OS初始化失败: {e}")
        print("将继续使用简化模式...")
        session = None
    
    # 主循环
    while True:
        try:
            user_input = input("\n[输入] ").strip()
            
            if not user_input:
                continue
                
            # 检查命令
            if user_input.lower() in ['退出', 'quit', 'exit']:
                print("\n[系统] 感谢使用AI OS！再见！")
                save_conversation_history(conversation_history)
                break
                
            elif user_input.lower() in ['帮助', 'help']:
                print_help()
                continue
                
            elif user_input.lower() in ['状态', 'status']:
                print_system_status()
                continue
                
            elif user_input.lower() in ['历史', 'history']:
                print(f"\n[对话历史] 共{len(conversation_history)}条记录")
                for i, msg in enumerate(conversation_history[-10:], 1):  # 显示最近10条
                    role = "用户" if msg["role"] == "user" else "助手"
                    print(f"  {i}. {role}: {msg['content'][:50]}...")
                continue
                
            elif user_input.lower() in ['清除', 'clear']:
                conversation_history = []
                print("\n[系统] 对话历史已清除")
                continue
            
            # 处理用户请求
            if session:
                process_user_input(session, user_input, conversation_history)
            else:
                # 简化模式
                print(f"\n[龙龟神将] 我收到你的请求: '{user_input}'")
                print("  (系统提示: AI OS完全模式初始化失败，当前运行在简化模式)")
                print("  建议重启程序或检查系统配置。")
                
                # 记录到历史
                conversation_history.append({
                    "role": "user",
                    "content": user_input,
                    "timestamp": datetime.now().isoformat()
                })
                conversation_history.append({
                    "role": "assistant",
                    "content": f"收到请求: {user_input} (简化模式)",
                    "timestamp": datetime.now().isoformat()
                })
                
        except KeyboardInterrupt:
            print("\n\n[系统] 检测到中断信号，正在保存对话历史...")
            save_conversation_history(conversation_history)
            print("[系统] 感谢使用AI OS！再见！")
            break
        except Exception as e:
            print(f"\n[系统] 发生错误: {e}")
            print("请重新输入你的请求。")

if __name__ == "__main__":
    main()