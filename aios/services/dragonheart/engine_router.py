#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
龙心 OS 引擎路由器
根据场景识别结果，路由到对应引擎（单引擎/多引擎/全引擎）

版本：v1.0
创建：2026-04-17
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class RouteType(Enum):
    """路由类型"""
    SINGLE = "single"  # 单引擎
    MULTI = "multi"    # 多引擎协同
    FULL = "full"      # 全引擎协同


@dataclass
class EngineRoute:
    """引擎路由结果"""
    route_type: RouteType
    engines: List[str]
    scene_code: str
    confidence: float
    reasoning: str


class EngineRouter:
    """引擎路由器 - 决策树路由"""
    
    def __init__(self):
        """初始化引擎路由器"""
        # 场景到引擎的映射
        self.engine_map = {
            'S0': {
                'engines': ['人机协同五象限'],
                'type': RouteType.SINGLE,
                'description': '日常对话 - 人机协同模式'
            },
            'S1': {
                'engines': ['人机协同五象限'],
                'type': RouteType.SINGLE,
                'description': '任务执行 - 效率协作者 (Q1)'
            },
            'S2': {
                'engines': ['知识学习'],
                'type': RouteType.SINGLE,
                'description': '深度理解 - 十项认知指令'
            },
            'S3': {
                'engines': ['象思维'],
                'type': RouteType.SINGLE,
                'description': '创意创新 - 观物取象 0→1 原创'
            },
            'S4': {
                'engines': ['五色光思维', '知行合一'],
                'type': RouteType.MULTI,
                'description': '分析决策 - 五色光分析 + 知行合一落地'
            },
            'S5': {
                'engines': ['知行合一', '知识学习', '人机协同五象限', '象思维', '五色光思维'],
                'type': RouteType.FULL,
                'description': '重大决策 - 全引擎协同'
            },
            'S6': {
                'engines': ['五色光思维'],
                'type': RouteType.SINGLE,
                'description': '会议引导 - 五色光过程管理'
            },
            'S7': {
                'engines': ['知识学习'],
                'type': RouteType.SINGLE,
                'description': '知识编译 - LLM Wiki 知识库建设'
            },
            'S8': {
                'engines': ['象思维'],
                'type': RouteType.SINGLE,
                'description': '修行文化 - 东方智慧'
            },
            'S9': {
                'engines': ['知行合一', '知识学习', '人机协同五象限', '象思维', '五色光思维'],
                'type': RouteType.FULL,
                'description': '系统进化 - 全引擎自省'
            }
        }
        
        # 置信度阈值配置
        self.thresholds = {
            'high': 0.9,    # 高置信度 - 直接路由
            'medium': 0.7,  # 中置信度 - 确认后路由
            'low': 0.5      # 低置信度 - 降级到 S0
        }
    
    def route(self, scene_code: str, confidence: float) -> EngineRoute:
        """
        根据场景代码和置信度进行路由
        
        Args:
            scene_code: 场景代码 (S0-S9)
            confidence: 置信度 (0-1)
            
        Returns:
            EngineRoute: 引擎路由结果
        """
        # 检查场景是否存在
        if scene_code not in self.engine_map:
            return EngineRoute(
                route_type=RouteType.SINGLE,
                engines=['人机协同五象限'],
                scene_code='S0',
                confidence=confidence,
                reasoning=f"未知场景{scene_code}，降级到 S0 日常对话"
            )
        
        engine_info = self.engine_map[scene_code]
        
        # 根据置信度调整路由策略
        if confidence >= self.thresholds['high']:
            # 高置信度 - 直接路由
            route_type = engine_info['type']
            engines = engine_info['engines']
            reasoning = f"高置信度 ({confidence:.1%})，直接路由到{engine_info['description']}"
            
        elif confidence >= self.thresholds['medium']:
            # 中置信度 - 简化路由（减少引擎数量）
            if engine_info['type'] == RouteType.FULL:
                # 全引擎降级为多引擎
                route_type = RouteType.MULTI
                engines = engine_info['engines'][:2]  # 只取前 2 个
                reasoning = f"中置信度 ({confidence:.1%})，全引擎降级为多引擎协同"
            else:
                route_type = engine_info['type']
                engines = engine_info['engines']
                reasoning = f"中置信度 ({confidence:.1%})，正常路由到{engine_info['description']}"
                
        else:
            # 低置信度 - 降级到 S0
            route_type = RouteType.SINGLE
            engines = ['人机协同五象限']
            reasoning = f"低置信度 ({confidence:.1%})，降级到 S0 日常对话"
            scene_code = 'S0'
        
        return EngineRoute(
            route_type=route_type,
            engines=engines,
            scene_code=scene_code,
            confidence=confidence,
            reasoning=reasoning
        )
    
    def get_activation_prompt(self, route: EngineRoute) -> str:
        """
        生成引擎激活提示词
        
        Args:
            route: 引擎路由结果
            
        Returns:
            str: 激活提示词
        """
        if route.route_type == RouteType.SINGLE:
            return f"激活{route.engines[0]}引擎，处理{route.scene_code}场景任务"
        
        elif route.route_type == RouteType.MULTI:
            engines_str = ' + '.join(route.engines)
            return f"协同激活{engines_str}引擎，处理{route.scene_code}场景任务"
        
        else:  # FULL
            return f"全引擎协同启动，处理{route.scene_code}重大决策场景"
    
    def route_with_details(self, scene_code: str, confidence: float) -> Dict:
        """
        带详细信息的完整路由
        
        Returns:
            Dict: 完整路由信息
        """
        route = self.route(scene_code, confidence)
        
        return {
            'scene_code': route.scene_code,
            'route_type': route.route_type.value,
            'engines': route.engines,
            'confidence': round(confidence, 3),
            'activation_prompt': self.get_activation_prompt(route),
            'reasoning': route.reasoning,
            'next_steps': self._get_next_steps(route)
        }
    
    def _get_next_steps(self, route: EngineRoute) -> List[str]:
        """获取下一步行动建议"""
        steps = []
        
        if route.route_type == RouteType.SINGLE:
            steps.append(f"调用{route.engines[0]}Skill")
            steps.append("执行对应认知操作")
            steps.append("返回结果给用户")
            
        elif route.route_type == RouteType.MULTI:
            steps.append(f"按顺序调用：{' → '.join(route.engines)}")
            steps.append("整合多个引擎输出")
            steps.append("生成综合解决方案")
            
        else:  # FULL
            steps.append("启动全引擎协同模式")
            steps.append("各引擎并行处理")
            steps.append("龙心 OS 整合输出")
            steps.append("生成战略级建议")
        
        return steps


def main():
    """测试引擎路由器"""
    router = EngineRouter()
    
    test_cases = [
        ('S0', 0.85),
        ('S2', 0.92),
        ('S3', 0.78),
        ('S4', 0.88),
        ('S5', 0.95),
        ('S5', 0.65),  # 低置信度
    ]
    
    print("=" * 60)
    print("龙心 OS 引擎路由器测试")
    print("=" * 60)
    
    for scene_code, confidence in test_cases:
        result = router.route_with_details(scene_code, confidence)
        print(f"\n场景：{scene_code}, 置信度：{confidence:.1%}")
        print(f"路由类型：{result['route_type']}")
        print(f"激活引擎：{', '.join(result['engines'])}")
        print(f"激活提示：{result['activation_prompt']}")
        print(f"推理：{result['reasoning']}")
        print(f"下一步:")
        for step in result['next_steps']:
            print(f"  - {step}")


if __name__ == "__main__":
    main()
