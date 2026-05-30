#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI OS 调度引擎 - 动态调整模块
基于龙心OS动态调整机制v2.0实现

版本: 1.0.0
开发者: 龙龟神将
用户: 悟空
"""

from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
from .engine_router import RouteDecision, SceneType, EngineType, RecipeType


class AdjustmentSignal(Enum):
    """动态调整信号枚举"""
    NONE = "无信号"
    MORE_COMPLEX = "比预想更复杂"
    MORE_SIMPLE = "比预想更简单"
    NEW_KEY_INFO = "发现新关键信息"
    USER_SPECIFIED = "用户明确指定引擎"
    USER_FEEDBACK = "用户反馈"


class AdjustmentAction(Enum):
    """调整动作枚举"""
    NONE = "无需调整"
    UPGRADE_RECIPE = "升级配方"
    DOWNGRADE_RECIPE = "降级配方"
    CHANGE_SCENE = "切换场景"
    PAUSE_AND_ADJUST = "暂停并调整"
    FOLLOW_USER_SPEC = "遵循用户指定"


class DynamicAdjuster:
    """动态调整器（基于龙心OS动态调整机制）"""
    
    def __init__(self):
        # 调整信号检测关键词
        self.signal_keywords = {
            AdjustmentSignal.MORE_COMPLEX: [
                "新维度", "新问题", "更复杂", "没想到", "超出预期",
                "更深层", "更深入", "更全面", "更多角度", "更系统",
            ],
            AdjustmentSignal.MORE_SIMPLE: [
                "不用那么复杂", "简单点", "直接点", "别搞复杂", "简洁",
                "快速", "简单处理", "直接回答", "不用分析", "不用深入",
            ],
            AdjustmentSignal.NEW_KEY_INFO: [
                "突然想到", "补充一下", "还有一点", "另外", "此外",
                "重要补充", "关键信息", "忘记说了", "需要说明", "强调",
            ],
            AdjustmentSignal.USER_SPECIFIED: [
                "用知识学习", "用象思维", "用五色光", "用人机协同",
                "用知行合一", "用全系统", "用S2", "用S3", "用S4",
                "用深度学习", "用创新", "用分析", "用执行", "用规划",
            ],
            AdjustmentSignal.USER_FEEDBACK: [
                "不对", "错了", "不是这样", "重新", "调整",
                "改进", "优化", "更好", "不够", "不足",
            ],
        }
        
        # 场景升级/降级路径
        self.scene_upgrade_path = {
            SceneType.S0_SIMPLE_QA: SceneType.S1_INFO_QUERY,
            SceneType.S1_INFO_QUERY: SceneType.S2_DEEP_LEARNING,
            SceneType.S2_DEEP_LEARNING: SceneType.S3_INNOVATION_BREAKTHROUGH,
            SceneType.S3_INNOVATION_BREAKTHROUGH: SceneType.S5_MAJOR_DECISION,
            SceneType.S4_ANALYSIS_DECISION: SceneType.S5_MAJOR_DECISION,
            SceneType.S5_MAJOR_DECISION: SceneType.S5_MAJOR_DECISION,  # 已达最高
            SceneType.S6_TASK_EXECUTION: SceneType.S7_SYSTEM_PLANNING,
            SceneType.S7_SYSTEM_PLANNING: SceneType.S5_MAJOR_DECISION,
            SceneType.S8_CULTURAL_PRACTICE: SceneType.S5_MAJOR_DECISION,
            SceneType.S9_SYSTEM_EVOLUTION: SceneType.S9_SYSTEM_EVOLUTION,  # 已达最高
        }
        
        self.scene_downgrade_path = {
            SceneType.S0_SIMPLE_QA: SceneType.S0_SIMPLE_QA,  # 已达最低
            SceneType.S1_INFO_QUERY: SceneType.S0_SIMPLE_QA,
            SceneType.S2_DEEP_LEARNING: SceneType.S1_INFO_QUERY,
            SceneType.S3_INNOVATION_BREAKTHROUGH: SceneType.S2_DEEP_LEARNING,
            SceneType.S4_ANALYSIS_DECISION: SceneType.S1_INFO_QUERY,
            SceneType.S5_MAJOR_DECISION: SceneType.S4_ANALYSIS_DECISION,
            SceneType.S6_TASK_EXECUTION: SceneType.S0_SIMPLE_QA,
            SceneType.S7_SYSTEM_PLANNING: SceneType.S6_TASK_EXECUTION,
            SceneType.S8_CULTURAL_PRACTICE: SceneType.S2_DEEP_LEARNING,
            SceneType.S9_SYSTEM_EVOLUTION: SceneType.S7_SYSTEM_PLANNING,
        }
        
        # 配方升级/降级路径
        self.recipe_upgrade_path = {
            RecipeType.NONE: RecipeType.C_SIMPLE,
            RecipeType.C_SIMPLE: RecipeType.C_STANDARD,
            RecipeType.C_STANDARD: RecipeType.B_INNOVATION,
            RecipeType.B_INNOVATION: RecipeType.A_FULL_SYSTEM,
            RecipeType.C_B_MIXED: RecipeType.A_FULL_SYSTEM,
            RecipeType.D_SIMPLE: RecipeType.D_STANDARD,
            RecipeType.D_STANDARD: RecipeType.A_FULL_SYSTEM,
            RecipeType.A_FULL_SYSTEM: RecipeType.A_FULL_SYSTEM,  # 已达最高
            RecipeType.E_EFFICIENT: RecipeType.E_D_MIXED,
            RecipeType.E_CREATIVE_PARTNER: RecipeType.E_D_MIXED,
            RecipeType.E_CREATIVE_TUTOR: RecipeType.E_D_MIXED,
            RecipeType.E_D_MIXED: RecipeType.A_FULL_SYSTEM,
            RecipeType.C_B_CULTURE: RecipeType.A_FULL_SYSTEM,
            RecipeType.EVOLUTION_SPECIAL: RecipeType.EVOLUTION_SPECIAL,  # 已达最高
        }
        
        self.recipe_downgrade_path = {
            RecipeType.NONE: RecipeType.NONE,  # 已达最低
            RecipeType.C_SIMPLE: RecipeType.NONE,
            RecipeType.C_STANDARD: RecipeType.C_SIMPLE,
            RecipeType.B_INNOVATION: RecipeType.C_STANDARD,
            RecipeType.C_B_MIXED: RecipeType.C_STANDARD,
            RecipeType.D_SIMPLE: RecipeType.NONE,
            RecipeType.D_STANDARD: RecipeType.D_SIMPLE,
            RecipeType.A_FULL_SYSTEM: RecipeType.D_STANDARD,
            RecipeType.E_EFFICIENT: RecipeType.NONE,
            RecipeType.E_CREATIVE_PARTNER: RecipeType.E_EFFICIENT,
            RecipeType.E_CREATIVE_TUTOR: RecipeType.E_EFFICIENT,
            RecipeType.E_D_MIXED: RecipeType.E_EFFICIENT,
            RecipeType.C_B_CULTURE: RecipeType.C_STANDARD,
            RecipeType.EVOLUTION_SPECIAL: RecipeType.E_D_MIXED,
        }
        
        # 用户指定引擎映射
        self.user_specified_mapping = {
            "知识学习": EngineType.KNOWLEDGE_LEARNING,
            "象思维": EngineType.IMAGE_THINKING,
            "五色光": EngineType.FIVE_COLOR_THINKING,
            "人机协同": EngineType.HUMAN_AI_COLLABORATION,
            "知行合一": EngineType.ZHI_XING_HE_YI,
            "全系统": EngineType.FULL_SYSTEM,
            "深度学习": SceneType.S2_DEEP_LEARNING,
            "创新": SceneType.S3_INNOVATION_BREAKTHROUGH,
            "分析": SceneType.S4_ANALYSIS_DECISION,
            "执行": SceneType.S6_TASK_EXECUTION,
            "规划": SceneType.S7_SYSTEM_PLANNING,
            "文化": SceneType.S8_CULTURAL_PRACTICE,
            "进化": SceneType.S9_SYSTEM_EVOLUTION,
        }
    
    def detect_signals(self, user_input: str, context: Dict) -> List[AdjustmentSignal]:
        """
        检测动态调整信号
        
        参数:
            user_input: 用户输入文本
            context: 上下文信息
            
        返回:
            List[AdjustmentSignal]: 检测到的信号列表
        """
        detected_signals = []
        cleaned_input = user_input.lower()
        
        for signal_type, keywords in self.signal_keywords.items():
            for keyword in keywords:
                if keyword in cleaned_input:
                    detected_signals.append(signal_type)
                    break  # 每个信号类型只需要检测到一个关键词
        
        return detected_signals
    
    def adjust_decision(self, current_decision: RouteDecision, 
                       signals: List[AdjustmentSignal],
                       user_input: str, context: Dict) -> Tuple[RouteDecision, AdjustmentAction, str]:
        """
        根据信号调整路由决策
        
        参数:
            current_decision: 当前路由决策
            signals: 检测到的调整信号列表
            user_input: 用户输入文本
            context: 上下文信息
            
        返回:
            (adjusted_decision, action, message): 调整后的决策、执行的动作、说明消息
        """
        # 如果没有信号，返回原决策
        if not signals:
            return current_decision, AdjustmentAction.NONE, "无调整信号，保持原决策"
        
        # 优先处理用户指定引擎信号
        if AdjustmentSignal.USER_SPECIFIED in signals:
            return self._handle_user_specified(current_decision, user_input, context)
        
        # 处理其他信号
        for signal in signals:
            if signal == AdjustmentSignal.MORE_COMPLEX:
                return self._handle_more_complex(current_decision, context)
            elif signal == AdjustmentSignal.MORE_SIMPLE:
                return self._handle_more_simple(current_decision, context)
            elif signal == AdjustmentSignal.NEW_KEY_INFO:
                return self._handle_new_key_info(current_decision, user_input, context)
            elif signal == AdjustmentSignal.USER_FEEDBACK:
                return self._handle_user_feedback(current_decision, user_input, context)
        
        # 默认返回原决策
        return current_decision, AdjustmentAction.NONE, "信号已处理，但无需调整"
    
    def _handle_user_specified(self, current_decision: RouteDecision, 
                              user_input: str, context: Dict) -> Tuple[RouteDecision, AdjustmentAction, str]:
        """处理用户明确指定引擎的情况"""
        cleaned_input = user_input.lower()
        
        # 查找用户指定的引擎或场景
        specified_engine = None
        specified_scene = None
        
        for keyword, target in self.user_specified_mapping.items():
            if keyword in cleaned_input:
                if isinstance(target, EngineType):
                    specified_engine = target
                elif isinstance(target, SceneType):
                    specified_scene = target
        
        if not specified_engine and not specified_scene:
            # 未找到明确指定，返回原决策
            return current_decision, AdjustmentAction.NONE, "未识别到明确的引擎指定"
        
        # 创建调整后的决策
        adjusted_decision = RouteDecision(
            scene_type=specified_scene if specified_scene else current_decision.scene_type,
            main_engine=specified_engine if specified_engine else current_decision.main_engine,
            auxiliary_engines=current_decision.auxiliary_engines.copy(),
            tail_engine=current_decision.tail_engine,
            recipe_type=current_decision.recipe_type,
            requires_declaration=True,  # 用户指定时总是声明
            declaration_text=f"「遵循用户指定：{specified_engine.value if specified_engine else specified_scene.value}」"
        )
        
        # 如果指定了场景，需要更新对应的引擎配置
        if specified_scene:
            # 这里需要根据场景重新配置引擎，简化处理：使用默认配置
            from .engine_router import EngineRouter
            router = EngineRouter()
            default_route = router._get_default_route(specified_scene)
            adjusted_decision = default_route
        
        message = f"已遵循用户指定，调整为：{specified_engine.value if specified_engine else specified_scene.value}"
        return adjusted_decision, AdjustmentAction.FOLLOW_USER_SPEC, message
    
    def _handle_more_complex(self, current_decision: RouteDecision, 
                            context: Dict) -> Tuple[RouteDecision, AdjustmentAction, str]:
        """处理比预想更复杂的情况（升级配方）"""
        # 升级场景
        current_scene = current_decision.scene_type
        upgraded_scene = self.scene_upgrade_path.get(current_scene, current_scene)
        
        # 升级配方
        current_recipe = current_decision.recipe_type
        upgraded_recipe = self.recipe_upgrade_path.get(current_recipe, current_recipe)
        
        if upgraded_scene == current_scene and upgraded_recipe == current_recipe:
            # 无法再升级
            message = "已是最复杂配置，无法进一步升级"
            return current_decision, AdjustmentAction.NONE, message
        
        # 创建升级后的决策（简化处理：使用新场景的默认配置）
        from .engine_router import EngineRouter
        router = EngineRouter()
        
        if upgraded_scene != current_scene:
            adjusted_decision = router._get_default_route(upgraded_scene)
            message = f"问题比预想更复杂，升级为：{upgraded_scene.value}"
        else:
            # 只升级配方，不改变场景
            adjusted_decision = router._get_default_route(current_scene)
            adjusted_decision.recipe_type = upgraded_recipe
            message = f"问题比预想更复杂，配方升级为：{upgraded_recipe.value}"
        
        # 更新声明文本
        adjusted_decision.declaration_text = f"「这个问题比较复杂，升级为[{adjusted_decision.recipe_type.value}]」"
        
        return adjusted_decision, AdjustmentAction.UPGRADE_RECIPE, message
    
    def _handle_more_simple(self, current_decision: RouteDecision, 
                           context: Dict) -> Tuple[RouteDecision, AdjustmentAction, str]:
        """处理比预想更简单的情况（降级配方）"""
        # 降级场景
        current_scene = current_decision.scene_type
        downgraded_scene = self.scene_downgrade_path.get(current_scene, current_scene)
        
        # 降级配方
        current_recipe = current_decision.recipe_type
        downgraded_recipe = self.recipe_downgrade_path.get(current_recipe, current_recipe)
        
        if downgraded_scene == current_scene and downgraded_recipe == current_recipe:
            # 无法再降级
            message = "已是最简配置，无法进一步降级"
            return current_decision, AdjustmentAction.NONE, message
        
        # 创建降级后的决策
        from .engine_router import EngineRouter
        router = EngineRouter()
        
        if downgraded_scene != current_scene:
            adjusted_decision = router._get_default_route(downgraded_scene)
            message = f"问题比预想更简单，降级为：{downgraded_scene.value}"
        else:
            # 只降级配方，不改变场景
            adjusted_decision = router._get_default_route(current_scene)
            adjusted_decision.recipe_type = downgraded_recipe
            message = f"问题比预想更简单，配方降级为：{downgraded_recipe.value}"
        
        # 静默执行，不声明
        adjusted_decision.requires_declaration = False
        adjusted_decision.declaration_text = ""
        
        return adjusted_decision, AdjustmentAction.DOWNGRADE_RECIPE, message
    
    def _handle_new_key_info(self, current_decision: RouteDecision, 
                            user_input: str, context: Dict) -> Tuple[RouteDecision, AdjustmentAction, str]:
        """处理发现新关键信息的情况（暂停并调整）"""
        # 分析新信息是否改变场景判断
        # 这里简化处理：重新运行意图识别和场景分类
        from .intent_recognizer import IntentRecognizer
        from .scene_classifier import SceneClassifier
        from .engine_router import EngineRouter
        
        intent_recognizer = IntentRecognizer()
        scene_classifier = SceneClassifier()
        engine_router = EngineRouter()
        
        # 重新识别意图
        new_intent, new_intensity = intent_recognizer.recognize(user_input, context)
        
        # 重新分类场景
        new_scene, new_complexity = scene_classifier.classify(
            user_input, new_intent, new_intensity, context
        )
        
        # 重新路由
        new_decision = engine_router.route(
            user_input, new_intent, new_intensity, new_scene, new_complexity, context
        )
        
        # 检查是否与原来不同
        if (new_decision.scene_type == current_decision.scene_type and 
            new_decision.recipe_type == current_decision.recipe_type):
            message = "新信息未改变场景判断，保持原决策"
            return current_decision, AdjustmentAction.NONE, message
        
        message = f"发现新关键信息，调整为：{new_decision.scene_type.value}"
        new_decision.declaration_text = f"「发现新维度，调整为[{new_decision.recipe_type.value}]」"
        
        return new_decision, AdjustmentAction.PAUSE_AND_ADJUST, message
    
    def _handle_user_feedback(self, current_decision: RouteDecision, 
                             user_input: str, context: Dict) -> Tuple[RouteDecision, AdjustmentAction, str]:
        """处理用户反馈（通常需要降级或调整）"""
        # 用户反馈通常表示当前方案不够好，需要简化或调整
        # 这里简化处理：降级一级
        
        # 首先尝试降级
        downgraded_decision, action, message = self._handle_more_simple(current_decision, context)
        
        if action == AdjustmentAction.NONE:
            # 如果无法降级，尝试切换场景
            # 切换到更简单的场景：S0或S1
            from .engine_router import EngineRouter
            router = EngineRouter()
            
            # 尝试切换到S1信息查询
            new_decision = router._get_default_route(SceneType.S1_INFO_QUERY)
            message = "根据用户反馈，切换为信息查询模式"
            new_decision.declaration_text = "「根据用户反馈调整模式」"
            
            return new_decision, AdjustmentAction.CHANGE_SCENE, message
        
        return downgraded_decision, action, message
    
    def generate_adjustment_message(self, action: AdjustmentAction, 
                                   original_decision: RouteDecision,
                                   adjusted_decision: RouteDecision) -> str:
        """生成调整说明消息"""
        if action == AdjustmentAction.NONE:
            return "保持原决策，无需调整。"
        
        messages = {
            AdjustmentAction.UPGRADE_RECIPE: f"问题比预想更复杂，从 {original_decision.recipe_type.value} 升级为 {adjusted_decision.recipe_type.value}。",
            AdjustmentAction.DOWNGRADE_RECIPE: f"问题比预想更简单，从 {original_decision.recipe_type.value} 降级为 {adjusted_decision.recipe_type.value}。",
            AdjustmentAction.CHANGE_SCENE: f"根据新信息/反馈，从 {original_decision.scene_type.value} 切换为 {adjusted_decision.scene_type.value}。",
            AdjustmentAction.PAUSE_AND_ADJUST: f"发现新关键信息，暂停原流程，调整为 {adjusted_decision.scene_type.value}。",
            AdjustmentAction.FOLLOW_USER_SPEC: f"遵循用户指定，使用 {adjusted_decision.main_engine.value if adjusted_decision.main_engine != EngineType.NONE else adjusted_decision.scene_type.value}。",
        }
        
        return messages.get(action, "已进行调整。")


# 测试函数
def test_dynamic_adjuster():
    """测试动态调整器"""
    from .intent_recognizer import IntentRecognizer
    from .scene_classifier import SceneClassifier
    from .engine_router import EngineRouter
    
    # 初始化组件
    intent_recognizer = IntentRecognizer()
    scene_classifier = SceneClassifier()
    engine_router = EngineRouter()
    dynamic_adjuster = DynamicAdjuster()
    
    # 测试案例：从简单问题开始，然后用户说"这个问题更复杂"
    test_input = "分析一下这个方案的优缺点"
    
    print("动态调整器测试：")
    print("-" * 80)
    
    # 初始决策
    intent, intensity = intent_recognizer.recognize(test_input)
    scene, complexity = scene_classifier.classify(test_input, intent, intensity)
    initial_decision = engine_router.route(test_input, intent, intensity, scene, complexity)
    
    print(f"初始输入: {test_input}")
    print(f"初始决策: {initial_decision}")
    print(f"初始场景: {initial_decision.scene_type.value}")
    print(f"初始配方: {initial_decision.recipe_type.value}")
    print()
    
    # 测试1: 用户说"这个问题更复杂"
    follow_up_input = "等等，这个问题更复杂，涉及多个维度"
    signals = dynamic_adjuster.detect_signals(follow_up_input, {})
    print(f"后续输入: {follow_up_input}")
    print(f"检测到的信号: {[signal.value for signal in signals]}")
    
    adjusted_decision, action, message = dynamic_adjuster.adjust_decision(
        initial_decision, signals, follow_up_input, {}
    )
    
    print(f"调整动作: {action.value}")
    print(f"调整消息: {message}")
    print(f"调整后决策: {adjusted_decision}")
    print()
    
    # 测试2: 用户说"不用那么复杂"
    follow_up_input2 = "不用那么复杂，简单点说"
    signals2 = dynamic_adjuster.detect_signals(follow_up_input2, {})
    print(f"后续输入: {follow_up_input2}")
    print(f"检测到的信号: {[signal.value for signal in signals2]}")
    
    adjusted_decision2, action2, message2 = dynamic_adjuster.adjust_decision(
        adjusted_decision, signals2, follow_up_input2, {}
    )
    
    print(f"调整动作: {action2.value}")
    print(f"调整消息: {message2}")
    print(f"调整后决策: {adjusted_decision2}")
    print()
    
    # 测试3: 用户明确指定引擎
    follow_up_input3 = "用五色光分析"
    signals3 = dynamic_adjuster.detect_signals(follow_up_input3, {})
    print(f"后续输入: {follow_up_input3}")
    print(f"检测到的信号: {[signal.value for signal in signals3]}")
    
    adjusted_decision3, action3, message3 = dynamic_adjuster.adjust_decision(
        adjusted_decision2, signals3, follow_up_input3, {}
    )
    
    print(f"调整动作: {action3.value}")
    print(f"调整消息: {message3}")
    print(f"调整后决策: {adjusted_decision3}")
    print()


if __name__ == "__main__":
    test_dynamic_adjuster()