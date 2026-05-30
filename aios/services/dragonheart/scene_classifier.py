#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# UTF-8 BOM

"""
龙心 OS 场景识别器
感知上下文 → 识别场景 (S0-S9) → 输出场景代码和置信度

版本：v1.1 (简化版 - 字符串匹配)
创建：2026-04-17
"""

from typing import Dict, List
from dataclasses import dataclass


@dataclass
class SceneMatch:
    """场景匹配结果"""
    scene_code: str
    scene_name: str
    confidence: float
    matched_signals: List[str]


class SceneClassifier:
    """场景识别器 - 基于字符串匹配的简化版本"""
    
    def __init__(self):
        """初始化场景识别器"""
        # S0-S9 场景定义 - 使用关键词列表替代正则
        self.scenes = {
            'S0': {
                'name': '日常对话',
                'engine': '人机协同',
                'keywords': ['你好', '早', '好', '在吗', '嗨', 'hello', 'hi', '最近怎么样', '谢谢', '感谢', '哈哈'],
                'threshold': 0.7
            },
            'S1': {
                'name': '任务执行',
                'engine': '人机协同 Q1',
                'keywords': ['帮我', '给我', '创建', '生成', '制作', '写', '画', '做', '需要', '想要', '希望', '任务', '工作', '执行', '完成', '写一个', '做一个', '创建一个', '脚本', 'Python', '代码'],
                'threshold': 0.6
            },
            'S2': {
                'name': '深度理解',
                'engine': '知识学习',
                'keywords': ['学习', '理解', '读懂', '分析', '解读', '文章', '文档', '理论', '概念', '核心观点', '主要思想', '本质', '深度', '深入', '详细'],
                'threshold': 0.8
            },
            'S3': {
                'name': '创意创新',
                'engine': '象思维',
                'keywords': ['创意', '灵感', '创新', '原创', '突破', '0 到 1', '从 0 到 1', '想象', '构思', '设计', '没有标准答案', '开放性', '像什么', '比喻', '类比', '隐喻', '阴阳', '五行', '易经', '需要创意', '需要灵感', '这个问题', '问题没有'],
                'threshold': 0.6
            },
            'S4': {
                'name': '分析决策',
                'engine': '五色光 + 知行合一',
                'keywords': ['分析', '评估', '权衡', '比较', '选择', '方案', '选项', '路径', '策略', '决策', '决定', '判断', '结论', '问题', '困难', '挑战', '落地', '实施', '执行', '实操', '怎么', '如何', '怎样', '方法', '概念落地', '落地实施', '超级个体'],
                'threshold': 0.85
            },
            'S5': {
                'name': '重大决策',
                'engine': '全引擎协同',
                'keywords': ['重大', '重要', '关键', '核心', '战略', '人生', '事业', '企业', '团队', '组织', '方向', '目标', '愿景', '使命', '价值观', '长期', '短期', '未来', '规划', '人生重大', '重大决策', '选择哪个'],
                'threshold': 0.5
            },
            'S6': {
                'name': '会议引导',
                'engine': '五色光思维',
                'keywords': ['会议', '开会', '讨论', '研讨', '工作坊', '团队', '集体', '大家', '一起', '共同', '主持', '引导', '流程', '过程', '共识', '一致', '统一', '跑题', '混乱', '分歧', '开会讨论', '总是跑题'],
                'threshold': 0.85
            },
            'S7': {
                'name': '知识编译',
                'engine': '知识学习+LLM Wiki',
                'keywords': ['编译', '整理', '结构化', '体系化', '知识库', 'Wiki', '知识图谱', '知识体系', 'LLM', 'AI', '大模型', '沉淀', '积累', '归档', '存储'],
                'threshold': 0.8
            },
            'S8': {
                'name': '修行文化',
                'engine': '象思维 + 五行分类',
                'keywords': ['修行', '修炼', '修心', '心性', '觉悟', '文化', '传统', '哲学', '智慧', '东方', '大圆满', '本净', '本觉', '信仰', '信念', '人生意义', '修行和', '和文化'],
                'threshold': 0.8
            },
            'S9': {
                'name': '系统进化',
                'engine': '龙心 OS 自省',
                'keywords': ['进化', '优化', '改进', '提升', '升级', '系统', '架构', '机制', '流程', '体系', '反思', '复盘', '总结', '教训', '错误', '问题', 'bug', '缺陷', '不足', '自动', '自主', '智能'],
                'threshold': 0.5
            }
        }
        
    def classify(self, input_text: str, context: Dict = None) -> SceneMatch:
        """
        识别输入文本的场景
        
        Args:
            input_text: 用户输入文本
            context: 上下文信息（可选）
            
        Returns:
            SceneMatch: 场景匹配结果
        """
        scores = {}
        matched_signals = {}
        
        # 遍历所有场景，计算匹配分数
        for scene_code, scene_info in self.scenes.items():
            score = 0.0
            signals_matched = []
            
            for keyword in scene_info['keywords']:
                if keyword.lower() in input_text.lower():
                    score += 0.2  # 每个关键词权重 0.2
                    signals_matched.append(keyword)
            
            # 归一化分数（最多 5 个关键词，满分 1.0）
            max_possible = min(len(scene_info['keywords']), 5) * 0.2
            if max_possible > 0:
                normalized_score = min(score / max_possible, 1.0)
            else:
                normalized_score = 0.0
                
            scores[scene_code] = normalized_score
            matched_signals[scene_code] = signals_matched
        
        # 选择最高分场景
        best_scene = max(scores, key=scores.get)
        best_confidence = scores[best_scene]
        
        # 检查是否达到阈值
        threshold = self.scenes[best_scene]['threshold']
        if best_confidence < threshold:
            # 未达到阈值，降级到 S0（日常对话）
            best_scene = 'S0'
            best_confidence = max(scores['S0'], 0.5)
        
        return SceneMatch(
            scene_code=best_scene,
            scene_name=self.scenes[best_scene]['name'],
            confidence=best_confidence,
            matched_signals=matched_signals[best_scene]
        )
    
    def get_engine_for_scene(self, scene_code: str) -> str:
        """获取场景对应的引擎"""
        if scene_code in self.scenes:
            return self.scenes[scene_code]['engine']
        return '人机协同'  # 默认引擎
    
    def classify_with_reasoning(self, input_text: str) -> Dict:
        """
        带推理过程的场景识别
        
        Returns:
            Dict: 包含完整推理过程的结果
        """
        result = self.classify(input_text)
        
        return {
            'input': input_text[:100] + '...' if len(input_text) > 100 else input_text,
            'scene_code': result.scene_code,
            'scene_name': result.scene_name,
            'engine': self.get_engine_for_scene(result.scene_code),
            'confidence': round(result.confidence, 3),
            'matched_signals_count': len(result.matched_signals),
            'matched_keywords': result.matched_signals,
            'reasoning': f"匹配到{len(result.matched_signals)}个关键词：{', '.join(result.matched_signals[:3])}",
            'threshold': self.scenes[result.scene_code]['threshold']
        }


def main():
    """测试场景识别器"""
    classifier = SceneClassifier()
    
    test_cases = [
        "你好，最近怎么样？",
        "帮我写一个 Python 脚本",
        "深度学习这篇文章的核心观点",
        "需要创意，这个问题没有标准答案",
        "如何把超级个体概念落地实施？",
        "人生重大决策，应该选择哪个方向？",
        "开会讨论总是跑题，怎么办？",
        "编译这个知识库到 LLM Wiki",
        "修行和文化的关系是什么？",
        "系统如何自动进化优化？"
    ]
    
    print("=" * 70)
    print("龙心 OS 场景识别器测试 (v1.1 字符串匹配)")
    print("=" * 70)
    
    for i, test in enumerate(test_cases, 1):
        result = classifier.classify_with_reasoning(test)
        print(f"\n测试 {i}: {test}")
        print(f"  场景：{result['scene_code']} - {result['scene_name']}")
        print(f"  引擎：{result['engine']}")
        print(f"  置信度：{result['confidence']:.1%}")
        print(f"  关键词：{result['matched_keywords']}")
        print(f"  推理：{result['reasoning']}")


if __name__ == "__main__":
    main()

