#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI OS 调度引擎 - 意图识别模块
基于龙心OS意图识别逻辑实现

版本: 1.0.0
开发者: 龙龟神将
用户: 悟空
"""

import re
from typing import Dict, List, Tuple, Optional
from enum import Enum


class IntentType(Enum):
    """六大意图类型（龙心OS定义）"""
    GET_INFO = "🔍 获取信息"          # 悟空需要什么信息？
    DEEP_UNDERSTANDING = "📖 深度理解" # 悟空要真正搞懂什么？
    CREATIVE_BREAKTHROUGH = "💡 创造突破" # 悟空要无中生有？
    ANALYSIS_DECISION = "⚖️ 分析决策"   # 悟空要权衡什么？
    TASK_EXECUTION = "🎯 任务执行"     # 悟空要落地什么？
    SYSTEM_EVOLUTION = "🔄 系统进化"    # 龙心OS要升级？


class IntentSignal:
    """意图强度信号"""
    
    HIGH_INTENSITY_KEYWORDS = [
        # 观其妙书院、龙心OS核心战略
        "观其妙书院", "龙心OS", "核心战略", "重要战略",
        # 悟空明确重视
        "重要", "认真想", "系统规划", "认真考虑", "慎重",
        # 多维度问题
        "多方面", "多维度", "多个角度", "综合",
        # 文化/修行/生命层面
        "修行", "文化", "生命", "哲学", "心文化",
    ]
    
    MEDIUM_INTENSITY_KEYWORDS = [
        # 提供完整文章/内容
        "文章", "文档", "报告", "分析一下", "深度分析",
        # 开放性较强的问题
        "怎么办", "如何", "建议", "想法", "看法",
        # 需要学习后落地
        "学习", "掌握", "理解", "搞懂",
    ]
    
    LOW_INTENSITY_KEYWORDS = [
        # 直接明确的问题
        "是什么", "告诉我", "查一下", "怎么用",
        # 闲聊/确认/简单指令
        "你好", "在吗", "谢谢", "确认", "明白",
        # 答案相对确定
        "快捷键", "命令", "操作", "步骤",
    ]


class IntentRecognizer:
    """意图识别器（龙心OS逻辑）"""
    
    def __init__(self):
        # 意图关键词映射
        self.intent_keywords = {
            IntentType.GET_INFO: [
                "是什么", "告诉我", "查一下", "查询", "搜索",
                "定义", "解释", "什么意思", "含义", "概念",
                "查找", "检索", "了解", "知道", "请问",
            ],
            IntentType.DEEP_UNDERSTANDING: [
                "深度学习", "深入理解", "深度分析", "透彻理解",
                "搞清楚", "弄明白", "掌握", "精通", "研究",
                "分析文章", "解读", "剖析", "解构", "思辨",
            ],
            IntentType.CREATIVE_BREAKTHROUGH: [
                "创新", "创意", "突破", "原创", "0→1",
                "无中生有", "从零开始", "全新", "前所未有",
                "创造", "发明", "设计", "构思", "想法",
                "新思路", "新方案", "新方法",
            ],
            IntentType.ANALYSIS_DECISION: [
                "分析", "决策", "选择", "权衡", "比较",
                "评估", "判断", "决定", "方案", "选项",
                "利弊", "优劣", "好坏", "值不值得", "该不该",
                "建议", "推荐", "意见", "看法",
            ],
            IntentType.TASK_EXECUTION: [
                "执行", "做", "完成", "实现", "操作",
                "运行", "启动", "开始", "进行", "处理",
                "任务", "工作", "项目", "计划", "安排",
                "帮忙", "协助", "支持", "帮助",
            ],
            IntentType.SYSTEM_EVOLUTION: [
                "系统升级", "优化", "改进", "完善", "增强",
                "进化", "升级", "更新", "版本", "新功能",
                "龙心OS", "AI OS", "操作系统", "调度器",
                "架构", "设计", "重构", "重写",
            ],
        }
        
        # 意图强度评估器
        self.intensity_evaluator = IntentSignal()
    
    def recognize(self, user_input: str, context: Optional[Dict] = None) -> Tuple[IntentType, int]:
        """
        识别用户意图
        
        参数:
            user_input: 用户输入文本
            context: 上下文信息（可选）
            
        返回:
            (intent_type, intensity_score): 意图类型和强度分数(1-10)
        """
        # 初始化上下文
        if context is None:
            context = {}
        
        # 预处理输入
        cleaned_input = self._preprocess_input(user_input)
        
        # 识别意图类型
        intent_type = self._identify_intent_type(cleaned_input)
        
        # 评估意图强度
        intensity_score = self._evaluate_intensity(cleaned_input, context)
        
        return intent_type, intensity_score
    
    def _preprocess_input(self, text: str) -> str:
        """预处理输入文本"""
        # 转换为小写
        text = text.lower()
        # 移除多余空格
        text = ' '.join(text.split())
        return text
    
    def _identify_intent_type(self, text: str) -> IntentType:
        """识别意图类型"""
        # 计算每种意图的关键词匹配数
        intent_scores = {}
        
        for intent_type, keywords in self.intent_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    score += 1
                    # 完全匹配的权重更高
                    if f" {keyword} " in f" {text} ":
                        score += 2
            
            intent_scores[intent_type] = score
        
        # 找出最高分的意图
        if not intent_scores:
            # 默认返回获取信息意图
            return IntentType.GET_INFO
        
        max_intent = max(intent_scores.items(), key=lambda x: x[1])[0]
        
        # 如果最高分很低，可能是闲聊或简单问题
        if intent_scores[max_intent] <= 1:
            # 检查是否是闲聊
            if self._is_casual_chat(text):
                return IntentType.GET_INFO  # 闲聊按获取信息处理
            
        return max_intent
    
    def _evaluate_intensity(self, text: str, context: Dict) -> int:
        """评估意图强度（1-10分）"""
        intensity_score = 5  # 默认中等强度
        
        # 关键词匹配评估
        high_count = sum(1 for keyword in self.intensity_evaluator.HIGH_INTENSITY_KEYWORDS 
                        if keyword in text)
        medium_count = sum(1 for keyword in self.intensity_evaluator.MEDIUM_INTENSITY_KEYWORDS 
                          if keyword in text)
        low_count = sum(1 for keyword in self.intensity_evaluator.LOW_INTENSITY_KEYWORDS 
                       if keyword in text)
        
        # 基于关键词调整分数
        if high_count > 0:
            intensity_score += high_count * 2
        if medium_count > 0:
            intensity_score += medium_count
        if low_count > 0:
            intensity_score -= low_count
        
        # 上下文调整
        if context.get('is_follow_up', False):
            # 如果是后续对话，强度可能增加
            intensity_score += 1
        
        if context.get('in_depth_discussion', False):
            # 深度讨论中
            intensity_score += 2
        
        # 边界检查
        intensity_score = max(1, min(10, intensity_score))
        
        return intensity_score
    
    def _is_casual_chat(self, text: str) -> bool:
        """判断是否是闲聊"""
        casual_patterns = [
            r'^你好.*$', r'^在吗.*$', r'^谢谢.*$', r'^明白.*$',
            r'^知道了.*$', r'^好的.*$', r'^嗯.*$', r'^哦.*$',
            r'^再见.*$', r'^拜拜.*$',
        ]
        
        for pattern in casual_patterns:
            if re.match(pattern, text):
                return True
        
        # 检查文本长度
        if len(text) < 10 and not any(keyword in text for keywords in self.intent_keywords.values() for keyword in keywords):
            return True
        
        return False
    
    def get_intent_description(self, intent_type: IntentType) -> str:
        """获取意图描述"""
        descriptions = {
            IntentType.GET_INFO: "用户需要获取信息、查询或了解某个概念",
            IntentType.DEEP_UNDERSTANDING: "用户需要深度理解、分析文章或掌握复杂知识",
            IntentType.CREATIVE_BREAKTHROUGH: "用户需要创新突破、原创设计或0→1创造",
            IntentType.ANALYSIS_DECISION: "用户需要分析决策、权衡选项或评估方案",
            IntentType.TASK_EXECUTION: "用户需要执行任务、完成工作或实现目标",
            IntentType.SYSTEM_EVOLUTION: "用户需要系统升级、优化改进或架构设计",
        }
        return descriptions.get(intent_type, "未知意图")
    
    def get_intent_emoji(self, intent_type: IntentType) -> str:
        """获取意图对应的emoji"""
        emojis = {
            IntentType.GET_INFO: "🔍",
            IntentType.DEEP_UNDERSTANDING: "📖",
            IntentType.CREATIVE_BREAKTHROUGH: "💡",
            IntentType.ANALYSIS_DECISION: "⚖️",
            IntentType.TASK_EXECUTION: "🎯",
            IntentType.SYSTEM_EVOLUTION: "🔄",
        }
        return emojis.get(intent_type, "❓")


# 测试函数
def test_intent_recognizer():
    """测试意图识别器"""
    recognizer = IntentRecognizer()
    
    test_cases = [
        ("粘贴复制快捷键是什么", IntentType.GET_INFO, 3),
        ("帮我深度学习这篇文章", IntentType.DEEP_UNDERSTANDING, 6),
        ("我需要一个全新的产品创意", IntentType.CREATIVE_BREAKTHROUGH, 7),
        ("分析一下这个方案的优缺点", IntentType.ANALYSIS_DECISION, 6),
        ("帮我执行这个任务", IntentType.TASK_EXECUTION, 5),
        ("龙心OS需要升级优化", IntentType.SYSTEM_EVOLUTION, 8),
        ("你好", IntentType.GET_INFO, 2),
    ]
    
    print("意图识别器测试结果：")
    print("-" * 50)
    
    for input_text, expected_intent, expected_intensity in test_cases:
        intent, intensity = recognizer.recognize(input_text)
        
        intent_match = "✓" if intent == expected_intent else "✗"
        intensity_match = "✓" if abs(intensity - expected_intensity) <= 2 else "✗"
        
        print(f"输入: {input_text}")
        print(f"  识别意图: {intent.value} {intent_match}")
        print(f"  强度分数: {intensity} {intensity_match}")
        print(f"  描述: {recognizer.get_intent_description(intent)}")
        print()


if __name__ == "__main__":
    test_intent_recognizer()