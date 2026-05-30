#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# UTF-8 BOM

"""
龙脑 OS 思维模型路由器
根据场景识别结果，路由到对应的思维模型组合

版本：v1.0
创建：2026-04-17
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class ModelFrequency(Enum):
    """模型频率分类"""
    HIGH = "high"      # 高频（9 个，本能反应）
    MEDIUM = "medium"  # 中频（20 个，场景激活）
    LOW = "low"        # 低频（71 个，按需加载）


@dataclass
class ThinkingModel:
    """思维模型定义"""
    name: str
    frequency: ModelFrequency
    category: str  # 分析/决策/战略/创新/系统/沟通
    description: str
    triggers: List[str]  # 触发关键词


@dataclass
class ModelRoute:
    """模型路由结果"""
    models: List[ThinkingModel]
    reasoning: str
    combination_type: str  # single/multi/parallel


class ModelRouter:
    """思维模型路由器 - 分层设计 + 动态路由"""
    
    def __init__(self):
        """初始化路由器"""
        # 高频模型（9 个，本能反应）
        self.high_frequency_models = [
            ThinkingModel(
                name="第一性原理",
                frequency=ModelFrequency.HIGH,
                category="分析",
                description="从基本原理出发，剥离表象，直达本质",
                triggers=["本质", "根本", "原理", "为什么", "底层逻辑"]
            ),
            ThinkingModel(
                name="MECE 原则",
                frequency=ModelFrequency.HIGH,
                category="分析",
                description="相互独立，完全穷尽",
                triggers=["分类", "分解", "结构化", "完整", "不重叠"]
            ),
            ThinkingModel(
                name="SWOT 分析",
                frequency=ModelFrequency.HIGH,
                category="战略",
                description="优势/劣势/机会/威胁",
                triggers=["优势", "劣势", "机会", "威胁", "内外部"]
            ),
            ThinkingModel(
                name="五色光思维",
                frequency=ModelFrequency.HIGH,
                category="决策",
                description="白光/红光/黄光/绿光/蓝光多维度思考",
                triggers=["多角度", "全面", "团队", "决策", "会议"]
            ),
            ThinkingModel(
                name="象思维",
                frequency=ModelFrequency.HIGH,
                category="创新",
                description="观物取象，0→1 原创突破",
                triggers=["创意", "灵感", "原创", "0 到 1", "突破"]
            ),
            ThinkingModel(
                name="金字塔原理",
                frequency=ModelFrequency.HIGH,
                category="沟通",
                description="结论先行，以上统下，归类分组，逻辑递进",
                triggers=["表达", "汇报", "结构", "逻辑", "清晰"]
            ),
            ThinkingModel(
                name="5Why 分析法",
                frequency=ModelFrequency.HIGH,
                category="分析",
                description="连续问 5 个为什么，找到根本原因",
                triggers=["原因", "为什么", "根源", "问题"]
            ),
            ThinkingModel(
                name="艾森豪威尔矩阵",
                frequency=ModelFrequency.HIGH,
                category="决策",
                description="重要/紧急四象限",
                triggers=["优先级", "重要", "紧急", "时间管理"]
            ),
            ThinkingModel(
                name="知行合一",
                frequency=ModelFrequency.HIGH,
                category="决策",
                description="从知道到做到，概念落地",
                triggers=["落地", "实施", "执行", "怎么做", "行动"]
            )
        ]
        
        # 中频模型（20 个，场景激活）- 示例 5 个
        self.medium_frequency_models = [
            ThinkingModel(
                name="波特五力",
                frequency=ModelFrequency.MEDIUM,
                category="战略",
                description="行业竞争分析五力模型",
                triggers=["行业", "竞争", "供应商", "客户", "替代品"]
            ),
            ThinkingModel(
                name="BCG 矩阵",
                frequency=ModelFrequency.MEDIUM,
                category="战略",
                description="明星/现金牛/问题/瘦狗",
                triggers=["产品组合", "市场份额", "增长", "投资"]
            ),
            ThinkingModel(
                name="PDCA 循环",
                frequency=ModelFrequency.MEDIUM,
                category="系统",
                description="计划 - 执行 - 检查 - 行动",
                triggers=["改进", "循环", "持续", "优化"]
            ),
            ThinkingModel(
                name="SCQA 框架",
                frequency=ModelFrequency.MEDIUM,
                category="沟通",
                description="情境 - 冲突 - 疑问 - 回答",
                triggers=["故事", "叙述", "开场", "引入"]
            ),
            ThinkingModel(
                name="决策矩阵",
                frequency=ModelFrequency.MEDIUM,
                category="决策",
                description="多标准决策分析",
                triggers=["选择", "评估", "标准", "权重"]
            )
        ]
        
        # 低频模型（71 个，按需加载）- 示例 5 个
        self.low_frequency_models = [
            ThinkingModel(
                name="鱼骨图",
                frequency=ModelFrequency.LOW,
                category="分析",
                description="因果分析图",
                triggers=["因果", "鱼骨", "石川图"]
            ),
            ThinkingModel(
                name="六顶思考帽",
                frequency=ModelFrequency.LOW,
                category="决策",
                description="平行思维工具",
                triggers=["六帽", "平行思维", "德博诺"]
            ),
            ThinkingModel(
                name="商业模式画布",
                frequency=ModelFrequency.LOW,
                category="战略",
                description="9 个构造块描述商业模式",
                triggers=["商业模式", "画布", "价值主张"]
            ),
            ThinkingModel(
                name="系统循环图",
                frequency=ModelFrequency.LOW,
                category="系统",
                description="因果关系循环图",
                triggers=["系统", "循环", "反馈", "增强", "调节"]
            ),
            ThinkingModel(
                name="非暴力沟通",
                frequency=ModelFrequency.LOW,
                category="沟通",
                description="观察 - 感受 - 需要 - 请求",
                triggers=["沟通", "冲突", "感受", "需要"]
            )
        ]
        
        # 场景到模型的映射
        self.scene_to_models = {
            'S0': ['五色光思维'],  # 日常对话
            'S1': ['艾森豪威尔矩阵', '知行合一'],  # 任务执行
            'S2': ['第一性原理', '5Why 分析法', '金字塔原理'],  # 深度理解
            'S3': ['象思维', '第一性原理'],  # 创意创新
            'S4': ['SWOT 分析', 'MECE 原则', '五色光思维', '知行合一'],  # 分析决策
            'S5': ['SWOT 分析', '波特五力', '第一性原理', '五色光思维', '知行合一'],  # 重大决策
            'S6': ['五色光思维', '金字塔原理', 'SCQA 框架'],  # 会议引导
            'S7': ['MECE 原则', '金字塔原理', '第一性原理'],  # 知识编译
            'S8': ['象思维', '五行分类'],  # 修行文化
            'S9': ['PDCA 循环', '第一性原理', '知行合一']  # 系统进化
        }
    
    def route(self, scene_code: str, input_text: str) -> ModelRoute:
        """
        根据场景和输入文本路由到思维模型
        
        Args:
            scene_code: 场景代码 (S0-S9)
            input_text: 用户输入文本
            
        Returns:
            ModelRoute: 模型路由结果
        """
        # 获取场景对应的模型列表
        scene_models = self.scene_to_models.get(scene_code, [])
        
        # 从输入文本中提取额外触发
        triggered_models = self._trigger_from_text(input_text)
        
        # 合并模型列表（去重）
        all_model_names = list(set(scene_models + triggered_models))
        
        # 查找模型对象
        selected_models = []
        for model_name in all_model_names:
            model = self._find_model(model_name)
            if model:
                selected_models.append(model)
        
        # 确定组合类型
        if len(selected_models) == 0:
            combination_type = "none"
            reasoning = "未匹配到合适的思维模型"
        elif len(selected_models) == 1:
            combination_type = "single"
            reasoning = f"单模型：{selected_models[0].name}"
        else:
            combination_type = "parallel"
            reasoning = f"多模型并行：{' + '.join([m.name for m in selected_models])}"
        
        return ModelRoute(
            models=selected_models,
            reasoning=reasoning,
            combination_type=combination_type
        )
    
    def _find_model(self, name: str) -> Optional[ThinkingModel]:
        """查找模型"""
        all_models = (
            self.high_frequency_models + 
            self.medium_frequency_models + 
            self.low_frequency_models
        )
        
        for model in all_models:
            if model.name == name:
                return model
        
        return None
    
    def _trigger_from_text(self, text: str) -> List[str]:
        """从文本中触发模型"""
        triggered = []
        all_models = (
            self.high_frequency_models + 
            self.medium_frequency_models
        )  # 低频模型不自动触发
        
        for model in all_models:
            for trigger in model.triggers:
                if trigger in text:
                    triggered.append(model.name)
                    break
        
        return triggered
    
    def get_models_by_frequency(self, frequency: ModelFrequency) -> List[ThinkingModel]:
        """按频率获取模型"""
        if frequency == ModelFrequency.HIGH:
            return self.high_frequency_models
        elif frequency == ModelFrequency.MEDIUM:
            return self.medium_frequency_models
        else:
            return self.low_frequency_models
    
    def route_with_details(self, scene_code: str, input_text: str) -> Dict:
        """
        带详细信息的完整路由
        
        Returns:
            Dict: 完整路由信息
        """
        route = self.route(scene_code, input_text)
        
        return {
            'scene_code': scene_code,
            'input_preview': input_text[:50] + '...' if len(input_text) > 50 else input_text,
            'models': [
                {
                    'name': m.name,
                    'frequency': m.frequency.value,
                    'category': m.category,
                    'description': m.description
                }
                for m in route.models
            ],
            'combination_type': route.combination_type,
            'reasoning': route.reasoning,
            'next_steps': self._get_next_steps(route)
        }
    
    def _get_next_steps(self, route: ModelRoute) -> List[str]:
        """获取下一步行动建议"""
        if route.combination_type == "none":
            return ["使用默认分析框架"]
        
        elif route.combination_type == "single":
            model = route.models[0]
            return [
                f"激活{model.name}思维模式",
                f"应用{model.category}维度分析",
                "输出洞察结果"
            ]
        
        else:  # parallel
            return [
                f"并行激活{len(route.models)}个思维模型",
                f"模型组合：{' + '.join([m.name for m in route.models])}",
                "整合多维度洞察",
                "输出综合战略建议"
            ]


def main():
    """测试思维模型路由器"""
    router = ModelRouter()
    
    test_cases = [
        ('S0', '你好，最近怎么样？'),
        ('S1', '帮我写一个 Python 脚本'),
        ('S2', '深度学习这篇文章的核心观点'),
        ('S3', '需要创意，这个问题没有标准答案'),
        ('S4', '如何把超级个体概念落地实施？'),
        ('S5', '人生重大决策，应该选择哪个方向？'),
        ('S6', '开会讨论总是跑题，怎么办？'),
        ('S7', '编译这个知识库到 LLM Wiki'),
        ('S8', '修行和文化的关系是什么？'),
        ('S9', '系统如何自动进化优化？')
    ]
    
    print("=" * 70)
    print("龙脑 OS 思维模型路由器测试")
    print("=" * 70)
    
    for scene_code, input_text in test_cases:
        result = router.route_with_details(scene_code, input_text)
        print(f"\n场景：{scene_code}")
        print(f"输入：{result['input_preview']}")
        print(f"组合类型：{result['combination_type']}")
        print(f"激活模型:")
        for model in result['models']:
            print(f"  - {model['name']} ({model['frequency']}, {model['category']})")
        print(f"推理：{result['reasoning']}")
        print(f"下一步:")
        for step in result['next_steps']:
            print(f"  - {step}")


if __name__ == "__main__":
    main()
