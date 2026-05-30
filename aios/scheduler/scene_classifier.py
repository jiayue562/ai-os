#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI OS 调度引擎 - 场景分类模块
基于龙心OS S0-S9场景矩阵实现

版本: 1.0.0
开发者: 龙龟神将
用户: 悟空
"""

from typing import Dict, List, Tuple, Optional
from enum import Enum
from .intent_recognizer import IntentType, IntentRecognizer


class SceneType(Enum):
    """S0-S9场景类型（龙心OS定义）"""
    S0_SIMPLE_QA = "S0 极简问答"          # 单句直接问题/闲聊/确认
    S1_INFO_QUERY = "S1 信息查询"         # "是什么"/"告诉我"/定义查询
    S2_DEEP_LEARNING = "S2 深度学习"      # 提供文章/要求深入理解
    S3_INNOVATION_BREAKTHROUGH = "S3 创新突破"  # 全新问题/0→1需求
    S4_ANALYSIS_DECISION = "S4 分析决策"  # 多选项/需权衡
    S5_MAJOR_DECISION = "S5 重大决策"     # 战略级/影响深远
    S6_TASK_EXECUTION = "S6 任务执行"     # 明确指令/直接执行
    S7_SYSTEM_PLANNING = "S7 系统规划"    # 项目规划/任务分工
    S8_CULTURAL_PRACTICE = "S8 修行文化"  # 心文化/大圆满/传统智慧
    S9_SYSTEM_EVOLUTION = "S9 系统进化"   # 龙心OS自身升级


class SceneClassifier:
    """场景分类器（龙心OS S0-S9逻辑）"""
    
    def __init__(self):
        self.intent_recognizer = IntentRecognizer()
        
        # 场景识别关键词映射
        self.scene_keywords = {
            SceneType.S0_SIMPLE_QA: [
                "你好", "在吗", "谢谢", "明白", "知道了",
                "好的", "嗯", "哦", "再见", "拜拜",
                "确认", "对", "是的", "不是", "否",
            ],
            SceneType.S1_INFO_QUERY: [
                "是什么", "告诉我", "查一下", "查询", "搜索",
                "定义", "解释", "什么意思", "含义", "概念",
                "怎么用", "如何使用", "操作步骤", "方法",
                "谁", "哪里", "何时", "为什么", "多少",
            ],
            SceneType.S2_DEEP_LEARNING: [
                "深度学习", "深入理解", "深度分析", "透彻理解",
                "分析文章", "解读文档", "研究一下", "搞懂",
                "掌握", "精通", "学习", "理解", "剖析",
                "解构", "思辨", "溯源", "融合", "启发",
            ],
            SceneType.S3_INNOVATION_BREAKTHROUGH: [
                "创新", "创意", "突破", "原创", "0→1",
                "无中生有", "从零开始", "全新", "前所未有",
                "创造", "发明", "设计", "构思", "想法",
                "新思路", "新方案", "新方法", "颠覆",
            ],
            SceneType.S4_ANALYSIS_DECISION: [
                "分析", "决策", "选择", "权衡", "比较",
                "评估", "判断", "决定", "方案", "选项",
                "利弊", "优缺点", "优劣", "好坏",
                "值不值得", "该不该", "建议", "推荐",
                "可行性", "效果", "影响",
            ],
            SceneType.S5_MAJOR_DECISION: [
                "战略", "重大", "重要", "关键", "核心",
                "长远", "未来", "规划", "方向", "目标",
                "转型", "变革", "升级", "重组", "调整",
                "投资", "合作", "并购", "上市", "扩张",
            ],
            SceneType.S6_TASK_EXECUTION: [
                "执行", "做", "完成", "实现", "操作",
                "运行", "启动", "开始", "进行", "处理",
                "任务", "工作", "项目", "计划", "安排",
                "帮忙", "协助", "支持", "帮助", "搞定",
            ],
            SceneType.S7_SYSTEM_PLANNING: [
                "规划", "设计", "架构", "系统", "流程",
                "方案", "计划", "路线图", "时间表", "分工",
                "协调", "管理", "组织", "团队", "项目",
                "工作流", "自动化", "优化", "改进",
            ],
            SceneType.S8_CULTURAL_PRACTICE: [
                "修行", "文化", "哲学", "心文化", "大圆满",
                "传统", "智慧", "道德", "伦理", "价值观",
                "信仰", "精神", "灵魂", "生命", "人生",
                "意义", "境界", "觉悟", "修炼", "成长",
            ],
            SceneType.S9_SYSTEM_EVOLUTION: [
                "系统升级", "优化", "改进", "完善", "增强",
                "进化", "升级", "更新", "版本", "新功能",
                "龙心OS", "AI OS", "操作系统", "调度器",
                "架构", "设计", "重构", "重写", "性能",
            ],
        }
        
        # 场景复杂度评估标准
        self.complexity_criteria = {
            "simple": [SceneType.S0_SIMPLE_QA, SceneType.S1_INFO_QUERY],
            "medium": [SceneType.S2_DEEP_LEARNING, SceneType.S4_ANALYSIS_DECISION, 
                      SceneType.S6_TASK_EXECUTION, SceneType.S8_CULTURAL_PRACTICE],
            "complex": [SceneType.S3_INNOVATION_BREAKTHROUGH, SceneType.S5_MAJOR_DECISION,
                       SceneType.S7_SYSTEM_PLANNING, SceneType.S9_SYSTEM_EVOLUTION],
        }
        
        # 意图到场景的映射关系
        self.intent_to_scene_mapping = {
            IntentType.GET_INFO: [SceneType.S0_SIMPLE_QA, SceneType.S1_INFO_QUERY],
            IntentType.DEEP_UNDERSTANDING: [SceneType.S2_DEEP_LEARNING],
            IntentType.CREATIVE_BREAKTHROUGH: [SceneType.S3_INNOVATION_BREAKTHROUGH],
            IntentType.ANALYSIS_DECISION: [SceneType.S4_ANALYSIS_DECISION, SceneType.S5_MAJOR_DECISION],
            IntentType.TASK_EXECUTION: [SceneType.S6_TASK_EXECUTION, SceneType.S7_SYSTEM_PLANNING],
            IntentType.SYSTEM_EVOLUTION: [SceneType.S9_SYSTEM_EVOLUTION],
        }
    
    def classify(self, user_input: str, intent_type: IntentType, 
                 intensity_score: int, context: Optional[Dict] = None) -> Tuple[SceneType, str]:
        """
        分类场景类型和复杂度
        
        参数:
            user_input: 用户输入文本
            intent_type: 意图类型
            intensity_score: 意图强度分数(1-10)
            context: 上下文信息（可选）
            
        返回:
            (scene_type, complexity): 场景类型和复杂度(simple/medium/complex)
        """
        # 初始化上下文
        if context is None:
            context = {}
        
        # 预处理输入
        cleaned_input = user_input.lower()
        
        # 步骤1：基于意图的初始场景分类
        initial_scenes = self.intent_to_scene_mapping.get(intent_type, [SceneType.S0_SIMPLE_QA])
        
        # 步骤2：基于关键词的细粒度分类
        scene_scores = {}
        for scene_type in initial_scenes:
            score = self._calculate_scene_score(cleaned_input, scene_type)
            scene_scores[scene_type] = score
        
        # 步骤3：基于强度分数的调整
        scene_scores = self._adjust_by_intensity(scene_scores, intensity_score)
        
        # 步骤4：基于上下文的调整
        scene_scores = self._adjust_by_context(scene_scores, context)
        
        # 步骤5：选择最高分场景
        selected_scene = max(scene_scores.items(), key=lambda x: x[1])[0]
        
        # 步骤6：确定复杂度
        complexity = self._determine_complexity(selected_scene, intensity_score)
        
        return selected_scene, complexity
    
    def _calculate_scene_score(self, text: str, scene_type: SceneType) -> int:
        """计算场景匹配分数"""
        score = 0
        keywords = self.scene_keywords.get(scene_type, [])
        
        for keyword in keywords:
            if keyword in text:
                score += 2
                # 完全匹配的权重更高
                if f" {keyword} " in f" {text} ":
                    score += 3
        
        return score
    
    def _adjust_by_intensity(self, scene_scores: Dict[SceneType, int], intensity_score: int) -> Dict[SceneType, int]:
        """基于意图强度调整场景分数"""
        adjusted_scores = scene_scores.copy()
        
        # 高强度倾向于复杂场景
        if intensity_score >= 8:
            for scene_type in self.complexity_criteria["complex"]:
                if scene_type in adjusted_scores:
                    adjusted_scores[scene_type] += 3
        
        # 中等强度倾向于中等场景
        elif intensity_score >= 5:
            for scene_type in self.complexity_criteria["medium"]:
                if scene_type in adjusted_scores:
                    adjusted_scores[scene_type] += 2
        
        # 低强度倾向于简单场景
        else:
            for scene_type in self.complexity_criteria["simple"]:
                if scene_type in adjusted_scores:
                    adjusted_scores[scene_type] += 2
        
        return adjusted_scores
    
    def _adjust_by_context(self, scene_scores: Dict[SceneType, int], context: Dict) -> Dict[SceneType, int]:
        """基于上下文调整场景分数"""
        adjusted_scores = scene_scores.copy()
        
        # 如果是后续对话
        if context.get('is_follow_up', False):
            previous_scene = context.get('previous_scene')
            if previous_scene:
                # 倾向于延续之前的场景类型
                if previous_scene in adjusted_scores:
                    adjusted_scores[previous_scene] += 2
        
        # 如果是深度讨论
        if context.get('in_depth_discussion', False):
            # 倾向于深度学习或分析决策场景
            for scene_type in [SceneType.S2_DEEP_LEARNING, SceneType.S4_ANALYSIS_DECISION]:
                if scene_type in adjusted_scores:
                    adjusted_scores[scene_type] += 3
        
        # 如果是系统相关讨论
        if context.get('system_discussion', False):
            # 倾向于系统进化场景
            if SceneType.S9_SYSTEM_EVOLUTION in adjusted_scores:
                adjusted_scores[SceneType.S9_SYSTEM_EVOLUTION] += 5
        
        return adjusted_scores
    
    def _determine_complexity(self, scene_type: SceneType, intensity_score: int) -> str:
        """确定场景复杂度"""
        # 基于场景类型的初始复杂度
        for complexity_level, scenes in self.complexity_criteria.items():
            if scene_type in scenes:
                base_complexity = complexity_level
                break
        else:
            base_complexity = "medium"
        
        # 基于强度分数调整
        if intensity_score >= 8:
            if base_complexity == "simple":
                return "medium"
            elif base_complexity == "medium":
                return "complex"
        elif intensity_score <= 3:
            if base_complexity == "complex":
                return "medium"
            elif base_complexity == "medium":
                return "simple"
        
        return base_complexity
    
    def get_scene_description(self, scene_type: SceneType) -> str:
        """获取场景描述"""
        descriptions = {
            SceneType.S0_SIMPLE_QA: "单句直接问题、闲聊或确认，无需启动引擎",
            SceneType.S1_INFO_QUERY: "信息查询、定义解释，浅层知识学习引擎",
            SceneType.S2_DEEP_LEARNING: "深度学习、文章分析，完整知识学习配方",
            SceneType.S3_INNOVATION_BREAKTHROUGH: "创新突破、0→1原创，象思维主导",
            SceneType.S4_ANALYSIS_DECISION: "分析决策、多选项权衡，五色光思维",
            SceneType.S5_MAJOR_DECISION: "重大战略决策，全系统启动",
            SceneType.S6_TASK_EXECUTION: "任务执行、明确指令，人机协同",
            SceneType.S7_SYSTEM_PLANNING: "系统规划、项目分工，人机协同+五色光",
            SceneType.S8_CULTURAL_PRACTICE: "修行文化、传统智慧，象思维+知识学习",
            SceneType.S9_SYSTEM_EVOLUTION: "系统进化、龙心OS升级，知行合一主导",
        }
        return descriptions.get(scene_type, "未知场景")
    
    def get_scene_emoji(self, scene_type: SceneType) -> str:
        """获取场景对应的emoji"""
        emojis = {
            SceneType.S0_SIMPLE_QA: "💬",
            SceneType.S1_INFO_QUERY: "🔍",
            SceneType.S2_DEEP_LEARNING: "📚",
            SceneType.S3_INNOVATION_BREAKTHROUGH: "💡",
            SceneType.S4_ANALYSIS_DECISION: "⚖️",
            SceneType.S5_MAJOR_DECISION: "🎯",
            SceneType.S6_TASK_EXECUTION: "🤝",
            SceneType.S7_SYSTEM_PLANNING: "📊",
            SceneType.S8_CULTURAL_PRACTICE: "🐉",
            SceneType.S9_SYSTEM_EVOLUTION: "🔄",
        }
        return emojis.get(scene_type, "❓")
    
    def get_recommended_engines(self, scene_type: SceneType) -> List[str]:
        """获取推荐引擎（龙心OS引擎调度决策树）"""
        engine_mapping = {
            SceneType.S0_SIMPLE_QA: [],
            SceneType.S1_INFO_QUERY: ["📚 知识学习（浅层）"],
            SceneType.S2_DEEP_LEARNING: ["📚→🐉→🔄 完整学习配方"],
            SceneType.S3_INNOVATION_BREAKTHROUGH: ["🐉 象思维主导"],
            SceneType.S4_ANALYSIS_DECISION: ["🌈 五色光思维"],
            SceneType.S5_MAJOR_DECISION: ["A型全系统"],
            SceneType.S6_TASK_EXECUTION: ["🤝 人机协同"],
            SceneType.S7_SYSTEM_PLANNING: ["🤝+🌈 混合"],
            SceneType.S8_CULTURAL_PRACTICE: ["🐉+📚 文化模式"],
            SceneType.S9_SYSTEM_EVOLUTION: ["🔄 知行合一主导"],
        }
        return engine_mapping.get(scene_type, [])


# 测试函数
def test_scene_classifier():
    """测试场景分类器"""
    classifier = SceneClassifier()
    intent_recognizer = IntentRecognizer()
    
    test_cases = [
        ("粘贴复制快捷键是什么", IntentType.GET_INFO, 3, SceneType.S1_INFO_QUERY, "simple"),
        ("帮我深度学习这篇文章", IntentType.DEEP_UNDERSTANDING, 6, SceneType.S2_DEEP_LEARNING, "medium"),
        ("我需要一个全新的产品创意", IntentType.CREATIVE_BREAKTHROUGH, 7, SceneType.S3_INNOVATION_BREAKTHROUGH, "complex"),
        ("分析一下这个方案的优缺点", IntentType.ANALYSIS_DECISION, 6, SceneType.S4_ANALYSIS_DECISION, "medium"),
        ("帮我执行这个任务", IntentType.TASK_EXECUTION, 5, SceneType.S6_TASK_EXECUTION, "medium"),
        ("龙心OS需要升级优化", IntentType.SYSTEM_EVOLUTION, 8, SceneType.S9_SYSTEM_EVOLUTION, "complex"),
        ("你好", IntentType.GET_INFO, 2, SceneType.S0_SIMPLE_QA, "simple"),
        ("如何进行系统规划", IntentType.TASK_EXECUTION, 6, SceneType.S7_SYSTEM_PLANNING, "complex"),
        ("谈谈修行文化", IntentType.DEEP_UNDERSTANDING, 7, SceneType.S8_CULTURAL_PRACTICE, "medium"),
    ]
    
    print("场景分类器测试结果：")
    print("-" * 80)
    
    for input_text, expected_intent, expected_intensity, expected_scene, expected_complexity in test_cases:
        # 识别意图
        intent, intensity = intent_recognizer.recognize(input_text)
        
        # 分类场景
        scene, complexity = classifier.classify(input_text, intent, intensity)
        
        intent_match = "✓" if intent == expected_intent else "✗"
        intensity_match = "✓" if abs(intensity - expected_intensity) <= 2 else "✗"
        scene_match = "✓" if scene == expected_scene else "✗"
        complexity_match = "✓" if complexity == expected_complexity else "✗"
        
        print(f"输入: {input_text}")
        print(f"  识别意图: {intent.value} {intent_match}")
        print(f"  强度分数: {intensity} {intensity_match}")
        print(f"  场景分类: {scene.value} {scene_match}")
        print(f"  复杂度: {complexity} {complexity_match}")
        print(f"  场景描述: {classifier.get_scene_description(scene)}")
        print(f"  推荐引擎: {', '.join(classifier.get_recommended_engines(scene))}")
        print()


if __name__ == "__main__":
    test_scene_classifier()