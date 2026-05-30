#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
龙心 OS 智能调度中枢
感知上下文 → 识别场景 → 路由引擎 → 执行调度 → 反馈学习

版本：v1.0
创建：2026-04-17
"""

import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# 导入框架模块
from scene_classifier import SceneClassifier, SceneMatch
from engine_router import EngineRouter, RouteType
from feedback_learner import FeedbackLearner, RoutingRecord

# 导入龙脑 OS 模块
import sys
from pathlib import Path
longnao_path = Path(__file__).parent.parent.parent / "龙脑 OS" / "framework"
sys.path.insert(0, str(longnao_path))
from model_router import ModelRouter


class DragonHeartOS:
    """龙心 OS 智能调度中枢"""
    
    def __init__(self):
        """初始化龙心 OS"""
        self.classifier = SceneClassifier()
        self.router = EngineRouter()
        self.learner = FeedbackLearner()
        self.model_router = ModelRouter()  # 龙脑 OS 思维模型路由器
        
        self.session_id = None
        self.user_id = None
    
    def process(self, input_text: str, context: Dict = None) -> Dict:
        """
        处理用户输入 - 完整调度流程
        
        Args:
            input_text: 用户输入文本
            context: 上下文信息
            
        Returns:
            Dict: 调度结果
        """
        # Step 1: 场景识别
        scene_result = self.classifier.classify_with_reasoning(input_text)
        
        # Step 2: 引擎路由
        route_result = self.router.route_with_details(
            scene_result['scene_code'],
            scene_result['confidence']
        )
        
        # Step 2.5: 龙脑 OS 思维模型路由（新增）
        model_route_result = self.model_router.route_with_details(
            scene_result['scene_code'],
            input_text
        )
        
        # Step 3: 生成调度指令
        dispatch_cmd = self._generate_dispatch_command(route_result, model_route_result)
        
        # Step 4: 记录路由
        record = RoutingRecord(
            timestamp=datetime.now().isoformat(),
            input_text=input_text,
            scene_code=scene_result['scene_code'],
            scene_name=scene_result['scene_name'],
            engines=route_result['engines'],
            confidence=scene_result['confidence']
        )
        self.learner.log_routing(record)
        
        # Step 5: 返回调度结果
        return {
            'success': True,
            'scene': scene_result,
            'route': route_result,
            'dispatch': dispatch_cmd,
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_dispatch_command(self, route_result: Dict, model_route_result: Dict = None) -> Dict:
        """生成调度指令"""
        engines = route_result['engines']
        route_type = route_result['route_type']
        
        # 整合思维模型路由结果
        thinking_models = []
        if model_route_result:
            thinking_models = model_route_result.get('models', [])
        
        if route_type == 'single':
            return {
                'mode': 'single',
                'primary_engine': engines[0],
                'action': f'activate_skill({engines[0]})',
                'thinking_models': thinking_models,
                'description': route_result['reasoning']
            }
        
        elif route_type == 'multi':
            return {
                'mode': 'multi',
                'engines': engines,
                'sequence': ' -> '.join(engines),
                'action': f'activate_skills_sequential({", ".join(engines)})',
                'thinking_models': thinking_models,
                'description': route_result['reasoning']
            }
        
        else:  # full
            return {
                'mode': 'full',
                'engines': engines,
                'action': 'activate_all_engines()',
                'thinking_models': thinking_models,
                'description': route_result['reasoning']
            }
    
    def process_with_feedback(self, input_text: str, feedback: str, context: Dict = None) -> Dict:
        """
        处理用户输入并收集反馈
        
        Args:
            input_text: 用户输入
            feedback: 用户反馈 (positive/negative/neutral)
            context: 上下文信息
            
        Returns:
            Dict: 处理结果
        """
        # 先处理输入
        result = self.process(input_text, context)
        
        # 记录反馈
        self.learner.log_feedback(
            result['scene']['scene_code'],
            result['route']['engines'],
            feedback,
            f"用户反馈：{feedback}"
        )
        
        result['feedback_recorded'] = True
        return result
    
    def get_status(self) -> Dict:
        """获取龙心 OS 状态"""
        learning_summary = self.learner.get_learning_summary()
        
        return {
            'status': 'online',
            'version': '1.0',
            'mode': 'auto_dispatch',
            'scene_classifier': 'active',
            'engine_router': 'active',
            'feedback_learner': 'active',
            'learning_stats': learning_summary,
            'timestamp': datetime.now().isoformat()
        }
    
    def export_report(self) -> str:
        """导出调度报告"""
        learning_report = self.learner.export_learning_report()
        
        status = self.get_status()
        
        report = f"""# 龙心 OS 调度报告

## 系统状态

- 状态：{status['status']}
- 版本：{status['version']}
- 模式：{status['mode']}
- 场景识别器：{status['scene_classifier']}
- 引擎路由器：{status['engine_router']}
- 反馈学习器：{status['feedback_learner']}

---

{learning_report}

---

_龙心 OS 调度报告 · {datetime.now().strftime('%Y-%m-%d %H:%M')} · 龙龟神将_
"""
        return report


def main():
    """测试龙心 OS 调度中枢"""
    os = DragonHeartOS()
    
    print("=" * 70)
    print("龙心 OS 智能调度中枢 - 测试")
    print("=" * 70)
    
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
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"测试 {i}/{len(test_cases)}: {test}")
        print(f"{'='*70}")
        
        result = os.process(test)
        
        print(f"\n[SCENE] 场景识别:")
        print(f"   场景：{result['scene']['scene_code']} - {result['scene']['scene_name']}")
        print(f"   置信度：{result['scene']['confidence']:.1%}")
        print(f"   推理：{result['scene']['reasoning']}")
        
        print(f"\n[ROUTE] 引擎路由:")
        print(f"   类型：{result['route']['route_type']}")
        print(f"   引擎：{', '.join(result['route']['engines'])}")
        print(f"   激活：{result['route']['activation_prompt']}")
        
        print(f"\n[DISPATCH] 调度指令:")
        dispatch = result['dispatch']
        print(f"   模式：{dispatch['mode']}")
        print(f"   动作：{dispatch['action']}")
        print(f"   说明：{dispatch['description']}")
    
    # 导出报告
    print(f"\n{'='*70}")
    print("导出学习报告")
    print(f"{'='*70}")
    report = os.export_report()
    print(report)


if __name__ == "__main__":
    main()
