#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
龙心 OS 反馈学习器
记录路由决策 → 收集用户反馈 → 优化权重

版本：v1.0
创建：2026-04-17
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class RoutingRecord:
    """路由记录"""
    timestamp: str
    input_text: str
    scene_code: str
    scene_name: str
    engines: List[str]
    confidence: float
    user_feedback: Optional[str] = None  # positive/negative/neutral
    actual_engines_used: Optional[List[str]] = None


class FeedbackLearner:
    """反馈学习器 - 持续优化路由权重"""
    
    def __init__(self, log_dir: str = None):
        """
        初始化反馈学习器
        
        Args:
            log_dir: 日志目录
        """
        if log_dir is None:
            log_dir = Path(__file__).parent.parent / "logs"
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.routing_log = self.log_dir / "routing.log"
        self.learning_log = self.log_dir / "learning.log"
        self.feedback_log = self.log_dir / "feedback.log"
        
        # 权重调整配置
        self.learning_rate = 0.1
        self.weight_adjustments = {}
    
    def log_routing(self, record: RoutingRecord):
        """
        记录路由决策
        
        Args:
            record: 路由记录
        """
        log_entry = {
            'type': 'routing',
            'timestamp': record.timestamp,
            'scene_code': record.scene_code,
            'engines': record.engines,
            'confidence': record.confidence,
            'input_preview': record.input_text[:100] if record.input_text else ''
        }
        
        self._append_log(self.routing_log, log_entry)
    
    def log_feedback(self, scene_code: str, engines: List[str], feedback: str, details: str = ""):
        """
        记录用户反馈
        
        Args:
            scene_code: 场景代码
            engines: 使用的引擎
            feedback: 反馈类型 (positive/negative/neutral)
            details: 详细反馈内容
        """
        log_entry = {
            'type': 'feedback',
            'timestamp': datetime.now().isoformat(),
            'scene_code': scene_code,
            'engines': engines,
            'feedback': feedback,
            'details': details
        }
        
        self._append_log(self.feedback_log, log_entry)
        
        # 根据反馈调整权重
        if feedback == 'positive':
            self._adjust_weights(scene_code, engines, delta=0.05)
        elif feedback == 'negative':
            self._adjust_weights(scene_code, engines, delta=-0.05)
    
    def _adjust_weights(self, scene_code: str, engines: List[str], delta: float):
        """
        调整场景 - 引擎权重
        
        Args:
            scene_code: 场景代码
            engines: 引擎列表
            delta: 调整幅度
        """
        key = f"{scene_code}:{','.join(engines)}"
        
        if key not in self.weight_adjustments:
            self.weight_adjustments[key] = 0.0
        
        self.weight_adjustments[key] += delta
        
        # 记录学习
        learning_entry = {
            'type': 'weight_adjustment',
            'timestamp': datetime.now().isoformat(),
            'key': key,
            'delta': delta,
            'new_weight': self.weight_adjustments[key]
        }
        
        self._append_log(self.learning_log, learning_entry)
    
    def _append_log(self, log_file: Path, entry: Dict):
        """追加日志条目"""
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    def get_optimized_engines(self, scene_code: str, base_engines: List[str]) -> List[str]:
        """
        获取优化后的引擎列表
        
        Args:
            scene_code: 场景代码
            base_engines: 基础引擎列表
            
        Returns:
            List[str]: 优化后的引擎列表
        """
        key = f"{scene_code}:{','.join(base_engines)}"
        
        if key in self.weight_adjustments:
            weight = self.weight_adjustments[key]
            
            # 如果权重过低，考虑降级
            if weight < -0.3:
                # 降级到 S0
                return ['人机协同五象限']
            elif weight > 0.3:
                # 权重高，保持原引擎
                return base_engines
        
        return base_engines
    
    def get_learning_summary(self) -> Dict:
        """获取学习摘要"""
        summary = {
            'total_routings': 0,
            'total_feedback': 0,
            'weight_adjustments': len(self.weight_adjustments),
            'positive_feedback': 0,
            'negative_feedback': 0,
            'top_adjustments': []
        }
        
        # 统计路由日志
        if self.routing_log.exists():
            with open(self.routing_log, 'r', encoding='utf-8') as f:
                summary['total_routings'] = sum(1 for _ in f)
        
        # 统计反馈日志
        if self.feedback_log.exists():
            with open(self.feedback_log, 'r', encoding='utf-8') as f:
                for line in f:
                    entry = json.loads(line)
                    summary['total_feedback'] += 1
                    if entry.get('feedback') == 'positive':
                        summary['positive_feedback'] += 1
                    elif entry.get('feedback') == 'negative':
                        summary['negative_feedback'] += 1
        
        # 权重调整 Top 5
        sorted_adjustments = sorted(
            self.weight_adjustments.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )[:5]
        
        summary['top_adjustments'] = [
            {'key': k, 'weight': v} for k, v in sorted_adjustments
        ]
        
        return summary
    
    def export_learning_report(self) -> str:
        """导出学习报告"""
        summary = self.get_learning_summary()
        
        report = f"""# 龙心 OS 学习报告

**生成时间**: {datetime.now().isoformat()}

## 总体统计

- 总路由次数：{summary['total_routings']}
- 总反馈次数：{summary['total_feedback']}
- 权重调整项：{summary['weight_adjustments']}
- 正面反馈：{summary['positive_feedback']}
- 负面反馈：{summary['negative_feedback']}

## 权重调整 Top 5

"""
        for i, adj in enumerate(summary['top_adjustments'], 1):
            report += f"{i}. `{adj['key']}`: {adj['weight']:+.3f}\n"
        
        report += f"\n---\n_龙心 OS 反馈学习报告 · {datetime.now().strftime('%Y-%m-%d')}_\n"
        
        return report


def main():
    """测试反馈学习器"""
    learner = FeedbackLearner()
    
    # 模拟路由记录
    record = RoutingRecord(
        timestamp=datetime.now().isoformat(),
        input_text="帮我分析这个概念如何落地",
        scene_code='S4',
        scene_name='分析决策',
        engines=['五色光思维', '知行合一'],
        confidence=0.88
    )
    
    learner.log_routing(record)
    print("✅ 路由记录已保存")
    
    # 模拟用户反馈
    learner.log_feedback('S4', ['五色光思维', '知行合一'], 'positive', '分析很到位')
    print("✅ 用户反馈已记录")
    
    # 获取学习摘要
    summary = learner.get_learning_summary()
    print(f"\n学习摘要:")
    print(f"  总路由：{summary['total_routings']}")
    print(f"  总反馈：{summary['total_feedback']}")
    print(f"  权重调整：{summary['weight_adjustments']}")
    
    # 导出报告
    report = learner.export_learning_report()
    print(f"\n{report}")


if __name__ == "__main__":
    main()
