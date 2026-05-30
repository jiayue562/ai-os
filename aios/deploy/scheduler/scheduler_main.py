#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI OS 调度引擎 - 调度器主类
集成所有模块，提供统一接口

版本: 1.0.0
开发者: 龙龟神将
用户: 悟空
"""

from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import json

from .intent_recognizer import IntentRecognizer, IntentType
from .scene_classifier import SceneClassifier, SceneType
from .engine_router import EngineRouter, RouteDecision, EngineType, RecipeType
from .dynamic_adjuster import DynamicAdjuster, AdjustmentSignal, AdjustmentAction
from .result_integrator import ResultIntegrator, SkillResult, IntegratedResult, IntegrationStrategy
from .evolution_precipitator import EvolutionPrecipitator, PrecipitationCard

# 记忆系统集成
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
try:
    from memory.memory_manager import ExtendedMemorySystem, DRAGON_HEART_SCENES
    from memory.skill_history import SkillHistoryManager
    from memory.retrieval_optimizer import RetrievalOptimizer
    MEMORY_SYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"[WARN] 记忆系统导入失败: {e}")
    MEMORY_SYSTEM_AVAILABLE = False
    ExtendedMemorySystem = None
    SkillHistoryManager = None
    RetrievalOptimizer = None

# 技能调用层集成
try:
    from skills.skill_invoker import SkillInvoker, create_skill_invoker
    from skills.parameter_handler import create_parameter_handler, create_result_parser, process_and_invoke
    from skills.error_handler import create_default_error_handler, with_error_handling, SkillInvocationError
    SKILL_INVOCATION_AVAILABLE = True
    print("[OK] 技能调用层导入成功")
except ImportError as e:
    print(f"[WARN] 技能调用层导入失败: {e}")
    SKILL_INVOCATION_AVAILABLE = False
    SkillInvoker = None
    create_skill_invoker = None
    create_parameter_handler = None
    create_result_parser = None
    process_and_invoke = None
    create_default_error_handler = None
    with_error_handling = None
    SkillInvocationError = Exception


class SchedulerSession:
    """调度器会话，管理单次对话的完整状态"""
    
    def __init__(self, session_id: str, user_id: str = "悟空"):
        """
        初始化调度器会话
        
        参数:
            session_id: 会话ID
            user_id: 用户ID
        """
        self.session_id = session_id
        self.user_id = user_id
        self.start_time = datetime.now()
        
        # 初始化各模块
        self.intent_recognizer = IntentRecognizer()
        self.scene_classifier = SceneClassifier()
        self.engine_router = EngineRouter()
        self.dynamic_adjuster = DynamicAdjuster()
        self.result_integrator = ResultIntegrator()
        self.evolution_precipitator = EvolutionPrecipitator()
        
        # 会话状态
        self.turn_count = 0
        self.user_messages = []
        self.assistant_messages = []
        self.current_intent = None
        self.current_scene = None
        self.current_route = None
        self.last_adjustment = None
        self.integrated_results = []
        self.precipitation_cards = []
        
        # 配置
        self.config = {
            "enable_dynamic_adjustment": True,
            "enable_evolution_precipitation": True,
            "max_turns_before_reset": 50,
            "confidence_threshold": 0.7,
            "enable_skill_invocation": True,
            "skill_invocation_timeout": 30,
            "skill_retry_enabled": True,
            "skill_circuit_breaker_enabled": True
        }
        
        # 记忆系统集成
        if MEMORY_SYSTEM_AVAILABLE:
            try:
                self.memory_system = ExtendedMemorySystem(
                    user_id=user_id,
                    session_id=session_id,
                    enable_auto_archive=True
                )
                self.skill_history_manager = SkillHistoryManager()
                self.retrieval_optimizer = RetrievalOptimizer()
                print(f"[OK] 记忆系统初始化成功 (用户: {user_id}, 会话: {session_id})")
            except Exception as e:
                print(f"[WARN] 记忆系统初始化失败: {e}")
                self.memory_system = None
                self.skill_history_manager = None
                self.retrieval_optimizer = None
        else:
            self.memory_system = None
            self.skill_history_manager = None
            self.retrieval_optimizer = None
            
        # 技能调用层集成
        if SKILL_INVOCATION_AVAILABLE:
            try:
                self.skill_invoker = create_skill_invoker()
                self.parameter_handler = create_parameter_handler()
                self.result_parser = create_result_parser()
                self.error_handler = create_default_error_handler(f"skill_invoker_{session_id}")
                print(f"[OK] 技能调用层初始化成功")
            except Exception as e:
                print(f"[WARN] 技能调用层初始化失败: {e}")
                self.skill_invoker = None
                self.parameter_handler = None
                self.result_parser = None
                self.error_handler = None
        else:
            self.skill_invoker = None
            self.parameter_handler = None
            self.result_parser = None
            self.error_handler = None
        
        # 活跃会话
        self.active_sessions = {}
        
        # 配置
        self.config = {
            "auto_precipitation": True,      # 自动知行合一沉淀
            "auto_adjustment": True,         # 自动动态调整
            "result_integration": True,      # 自动结果整合
            "verbose_logging": False,        # 详细日志
            "max_session_history": 100,      # 最大会话历史记录
            "memory_enabled": True,          # 记忆系统启用
            "memory_auto_archive": True,     # 自动归档
            "memory_retrieval_enabled": True, # 记忆检索启用
        }
    
    def create_session(self, user_id: str = "悟空") -> str:
        """创建新会话"""
        import uuid
        session_id = f"SES_{uuid.uuid4().hex[:8].upper()}"
        
        session = SchedulerSession(session_id, user_id)
        self.active_sessions[session_id] = session
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[SchedulerSession]:
        """获取会话"""
        return self.active_sessions.get(session_id)
    
    def process_request(self, session_id: str, user_input: str, 
                       user_feedback: Optional[str] = None,
                       context_updates: Optional[Dict] = None) -> Dict[str, Any]:
        """
        处理用户请求（主入口点）
        
        参数:
            session_id: 会话ID
            user_input: 用户输入
            user_feedback: 用户反馈（用于动态调整）
            context_updates: 上下文更新
            
        返回:
            Dict: 处理结果，包含决策、调整、结果等信息
        """
        # 获取会话
        session = self.get_session(session_id)
        if not session:
            session_id = self.create_session()
            session = self.get_session(session_id)
        
        # 添加用户输入到对话历史
        session.add_dialogue_turn("user", user_input, {"raw_input": user_input})
        
        # 更新上下文
        if context_updates:
            session.update_context(**context_updates)
        
        # 设置是否为后续对话
        if len(session.dialogue_history) > 1:
            session.update_context(is_follow_up=True)
        
        # 步骤1: 意图识别
        intent, intensity = self._recognize_intent(user_input, session.context)
        session.current_intent = intent
        session.current_intensity = intensity
        
        # 步骤2: 场景分类
        scene, complexity = self._classify_scene(user_input, intent, intensity, session.context)
        session.current_scene = scene
        session.current_complexity = complexity
        
        # 记录场景记忆
        if self.memory_enabled and scene:
            try:
                scene_code = scene.value if hasattr(scene, 'value') else str(scene)
                scene_desc = self.scene_classifier.get_scene_description(scene) if hasattr(self.scene_classifier, 'get_scene_description') else ""
                
                memory_content = f"用户请求: {user_input}\n意图: {intent.value if hasattr(intent, 'value') else intent}\n场景: {scene_code}\n复杂度: {complexity}"
                memory_title = f"{scene_code}: {user_input[:30]}{'...' if len(user_input) > 30 else ''}"
                
                self.memory_system.store_scene_memory(
                    scene=scene_code,
                    content=memory_content,
                    title=memory_title,
                    importance=7,
                    tags=["场景记忆", "调度器", scene_code]
                )
            except Exception as e:
                print(f"[WARN] 场景记忆记录失败: {e}")
        
        # 更新上下文中的前一个场景
        if scene != session.context.get("previous_scene"):
            session.update_context(previous_scene=scene)
        
        # 步骤3: 引擎路由
        decision = self._route_engine(user_input, intent, intensity, scene, complexity, session.context)
        session.current_decision = decision
        
        # 步骤4: 动态调整（如果用户提供了反馈）
        if user_feedback and self.config["auto_adjustment"]:
            adjusted_decision, adjustment_action, adjustment_message = self._apply_dynamic_adjustment(
                decision, user_feedback, session.context
            )
            
            if adjustment_action != AdjustmentAction.NONE:
                # 使用调整后的决策
                decision = adjusted_decision
                session.current_decision = decision
                session.current_adjustment = adjustment_action
                
                # 记录调整
                session.add_dialogue_turn("system", f"动态调整: {adjustment_message}")
        
        # 步骤5: 执行声明（如果需要）
        declaration_result = None
        if decision.requires_declaration:
            declaration_result = self._execute_declaration(decision)
            session.add_dialogue_turn("system", declaration_result)
        
        # 步骤6: 模拟技能执行（实际实现中会调用真正的技能）
        skill_results = self._simulate_skill_execution(decision, user_input, session.context)
        session.skill_results.extend(skill_results)
        
        # 记录技能调用历史
        if self.memory_enabled and self.skill_history_manager and skill_results:
            try:
                for skill_result in skill_results:
                    skill_name = skill_result.skill_name if hasattr(skill_result, 'skill_name') else "未知技能"
                    # 模拟执行时间和成功状态
                    import random
                    execution_time = random.uniform(0.5, 3.0)
                    success = random.random() > 0.1  # 90%成功率
                    
                    self.skill_history_manager.record_skill_call(
                        skill_name=skill_name,
                        skill_params={
                            "input": user_input[:100],
                            "scene": scene.value if hasattr(scene, 'value') else str(scene),
                            "intent": intent.value if hasattr(intent, 'value') else str(intent)
                        },
                        result=str(skill_result.result_data)[:200] if hasattr(skill_result, 'result_data') else "无结果",
                        execution_time=execution_time,
                        success=success,
                        error_msg=None if success else "模拟错误"
                    )
            except Exception as e:
                print(f"[WARN] 技能调用历史记录失败: {e}")
        
        # 步骤7: 结果整合
        integrated_result = None
        if self.config["result_integration"] and skill_results:
            integrated_result = self._integrate_results(skill_results, session.context)
            session.final_result = integrated_result
        
        # 步骤8: 进化沉淀
        precipitation_result = None
        if self.config["auto_precipitation"]:
            should_precipitate, reason, conditions = self._check_precipitation_need(
                decision, session.dialogue_history, user_feedback, session.context
            )
            
            if should_precipitate:
                precipitation_card = self._execute_precipitation(
                    decision, session.dialogue_history, integrated_result, session.context
                )
                session.precipitation_card = precipitation_card
                precipitation_result = {
                    "should_precipitate": True,
                    "reason": reason,
                    "card_id": precipitation_card.card_id,
                    "title": precipitation_card.title,
                }
                
                # 添加沉淀声明
                session.add_dialogue_turn("system", f"🔄 知行合一沉淀: {precipitation_card.title}")
            else:
                precipitation_result = {
                    "should_precipitate": False,
                    "reason": reason,
                }
        
        # 构建返回结果
        result = {
            "session_id": session_id,
            "user_input": user_input,
            "intent": {
                "type": intent.value,
                "description": self.intent_recognizer.get_intent_description(intent),
                "emoji": self.intent_recognizer.get_intent_emoji(intent),
                "intensity": intensity,
            },
            "scene": {
                "type": scene.value,
                "description": self.scene_classifier.get_scene_description(scene),
                "emoji": self.scene_classifier.get_scene_emoji(scene),
                "complexity": complexity,
            },
            "decision": decision.to_dict(),
            "declaration": declaration_result,
            "skill_execution": {
                "skill_count": len(skill_results),
                "skills": [result.skill_name for result in skill_results],
            },
            "integration": integrated_result.to_dict() if integrated_result else None,
            "precipitation": precipitation_result,
            "session_summary": session.to_dict(),
        }
        
        # 添加AI回复到对话历史
        ai_response = self._generate_ai_response(result)
        session.add_dialogue_turn("assistant", ai_response, {"result_summary": result})
        
        return result
    
    def _recognize_intent(self, user_input: str, context: Dict) -> Tuple[IntentType, int]:
        """识别意图"""
        return self.intent_recognizer.recognize(user_input, context)
    
    def _classify_scene(self, user_input: str, intent: IntentType, 
                       intensity: int, context: Dict) -> Tuple[SceneType, str]:
        """分类场景"""
        return self.scene_classifier.classify(user_input, intent, intensity, context)
    
    def _route_engine(self, user_input: str, intent: IntentType, 
                     intensity: int, scene: SceneType, 
                     complexity: str, context: Dict) -> RouteDecision:
        """引擎路由"""
        return self.engine_router.route(user_input, intent, intensity, scene, complexity, context)
    
    def _apply_dynamic_adjustment(self, decision: RouteDecision, 
                                 user_feedback: str, context: Dict) -> Tuple[RouteDecision, AdjustmentAction, str]:
        """应用动态调整"""
        signals = self.dynamic_adjuster.detect_signals(user_feedback, context)
        return self.dynamic_adjuster.adjust_decision(decision, signals, user_feedback, context)
    
    def _execute_declaration(self, decision: RouteDecision) -> str:
        """执行引擎声明"""
        return decision.declaration_text
    
    def _simulate_skill_execution(self, decision: RouteDecision, 
                                 user_input: str, context: Dict) -> List[SkillResult]:
        """模拟技能执行（实际实现中会调用真正的WorkBuddy技能）"""
        from .result_integrator import ResultType
        
        skill_results = []
        
        # 模拟主引擎执行
        main_engine_result = self._simulate_single_skill(
            decision.main_engine, user_input, decision, context
        )
        if main_engine_result:
            skill_results.append(main_engine_result)
        
        # 模拟辅助引擎执行
        for engine in decision.auxiliary_engines:
            auxiliary_result = self._simulate_single_skill(
                engine, user_input, decision, context
            )
            if auxiliary_result:
                skill_results.append(auxiliary_result)
        
        # 模拟收尾引擎执行
        if decision.tail_engine:
            tail_result = self._simulate_single_skill(
                decision.tail_engine, user_input, decision, context
            )
            if tail_result:
                skill_results.append(tail_result)
        
        return skill_results
    
    def _simulate_single_skill(self, engine_type: EngineType, 
                              user_input: str, decision: RouteDecision, 
                              context: Dict) -> Optional[SkillResult]:
        """模拟单个技能执行"""
        from .result_integrator import ResultType
        
        if engine_type == EngineType.NONE:
            return None
        
        # 基于引擎类型生成模拟结果
        skill_name = engine_type.value.split()[1] if " " in engine_type.value else engine_type.value
        
        if engine_type == EngineType.KNOWLEDGE_LEARNING:
            result_data = f"知识学习引擎分析: 用户询问'{user_input}'，这是一个{decision.scene_type.value}场景。关键知识点已提取。"
            result_type = ResultType.TEXT
            confidence = 0.9
        
        elif engine_type == EngineType.IMAGE_THINKING:
            result_data = {
                "insight": "象思维引擎产生原象级洞察",
                "pattern": "整体感知发现新的关联模式",
                "innovation": "跨边界思考带来创新突破",
            }
            result_type = ResultType.STRUCTURED
            confidence = 0.85
        
        elif engine_type == EngineType.FIVE_COLOR_THINKING:
            result_data = [
                "白光（事实）: 用户需求明确",
                "绿光（发散）: 多个解决方案可能性",
                "黄光（价值）: 方案A价值最高",
                "蓝光（风险）: 需要注意实施风险",
                "红光（执行）: 建议分阶段实施",
            ]
            result_type = ResultType.LIST
            confidence = 0.88
        
        elif engine_type == EngineType.HUMAN_AI_COLLABORATION:
            result_data = f"人机协同引擎: 已规划执行方案，用户与AI分工明确。场景: {decision.scene_type.value}"
            result_type = ResultType.TEXT
            confidence = 0.87
        
        elif engine_type == EngineType.ZHI_XING_HE_YI:
            result_data = {
                "representation": "完整对话已记录",
                "compression": ["核心洞察: 用户需要深度学习", "关键决策: 采用完整学习配方"],
                "generalization": ["可复用模式: 深度学习应采用知识学习+象思维组合"],
            }
            result_type = ResultType.STRUCTURED
            confidence = 0.95
        
        elif engine_type == EngineType.FULL_SYSTEM:
            result_data = "全系统引擎: 所有引擎协同工作，提供全方位分析、决策和执行支持。"
            result_type = ResultType.TEXT
            confidence = 0.92
        
        else:
            # 默认结果
            result_data = f"{skill_name}引擎执行完成。输入: {user_input}"
            result_type = ResultType.TEXT
            confidence = 0.8
        
        return SkillResult(
            skill_name=skill_name,
            result_data=result_data,
            result_type=result_type,
            confidence=confidence,
            metadata={
                "engine_type": engine_type.value,
                "scene_type": decision.scene_type.value,
                "recipe_type": decision.recipe_type.value,
            }
        )
    
    def _integrate_results(self, skill_results: List[SkillResult], context: Dict) -> IntegratedResult:
        """整合结果"""
        # 根据结果数量和类型选择整合策略
        if len(skill_results) == 1:
            strategy = IntegrationStrategy.MERGE
        elif len(skill_results) == 2:
            strategy = IntegrationStrategy.PRIORITY
        else:
            # 多个结果，使用结构化合并
            strategy = IntegrationStrategy.STRUCTURED_MERGE
        
        return self.result_integrator.integrate(skill_results, strategy, context)
    
    def _check_precipitation_need(self, decision: RouteDecision, 
                                 dialogue_history: List[Dict],
                                 user_feedback: Optional[str], 
                                 context: Dict) -> Tuple[bool, str, List[str]]:
        """检查是否需要沉淀"""
        return self.evolution_precipitator.should_precipitate(
            decision, dialogue_history, user_feedback, context
        )
    
    def _execute_precipitation(self, decision: RouteDecision, 
                              dialogue_history: List[Dict],
                              final_result: Any, 
                              context: Dict) -> PrecipitationCard:
        """执行沉淀"""
        return self.evolution_precipitator.precipitate(
            decision, dialogue_history, final_result, context
        )
    
    def _generate_ai_response(self, result: Dict) -> str:
        """生成AI回复（基于处理结果）"""
        # 简化实现：基于场景生成回复
        scene_type = result["scene"]["type"]
        decision = result["decision"]
        
        responses = {
            "S0 极简问答": "已为您解答。",
            "S1 信息查询": f"根据查询结果: {decision.get('declaration_text', '信息已提供')}",
            "S2 深度学习": "已完成深度学习，关键洞察已提取并沉淀。",
            "S3 创新突破": "创新突破已完成，新方案已生成。",
            "S4 分析决策": "分析决策已完成，建议方案已提供。",
            "S5 重大决策": "重大决策分析已完成，全系统支持已就绪。",
            "S6 任务执行": "任务执行方案已就绪，可开始实施。",
            "S7 系统规划": "系统规划已完成，分工和路线图已明确。",
            "S8 修行文化": "文化深度探索已完成，心文化洞察已沉淀。",
            "S9 系统进化": "系统进化分析已完成，升级建议已生成。",
        }
        
        default_response = f"{scene_type}处理已完成。{decision.get('declaration_text', '')}"
        
        return responses.get(scene_type, default_response)
    
    def get_session_report(self, session_id: str) -> Dict[str, Any]:
        """获取会话报告"""
        session = self.get_session(session_id)
        if not session:
            return {"error": "会话不存在"}
        
        return session.to_dict()
    
    def list_active_sessions(self) -> List[Dict[str, Any]]:
        """列出所有活跃会话"""
        return [
            {
                "session_id": session_id,
                "user_id": session.user_id,
                "start_time": session.start_time.isoformat(),
                "dialogue_turns": len(session.dialogue_history),
                "current_scene": session.current_scene.value if session.current_scene else None,
                "has_precipitation": session.precipitation_card is not None,
            }
            for session_id, session in self.active_sessions.items()
        ]
    
    def close_session(self, session_id: str) -> bool:
        """关闭会话"""
        if session_id in self.active_sessions:
            # 可以在这里执行会话结束前的清理工作
            del self.active_sessions[session_id]
            return True
        return False
    
    def update_config(self, **kwargs):
        """更新配置"""
        valid_keys = set(self.config.keys())
        for key, value in kwargs.items():
            if key in valid_keys:
                self.config[key] = value


# 测试函数
def test_scheduler():
    """测试调度器"""
    print("调度器测试：")
    print("-" * 80)
    
    # 创建调度器
    scheduler = Scheduler()
    
    # 创建会话
    session_id = scheduler.create_session("悟空")
    print(f"创建会话: {session_id}")
    
    # 测试用例1: 简单问题
    print("\n测试1: 简单问题")
    result1 = scheduler.process_request(session_id, "粘贴复制快捷键是什么")
    print(f"输入: {result1['user_input']}")
    print(f"意图: {result1['intent']['type']}")
    print(f"场景: {result1['scene']['type']}")
    print(f"决策: {result1['decision']['scene_type']}")
    print(f"沉淀: {result1['precipitation']['reason'] if result1['precipitation'] else '无'}")
    
    # 测试用例2: 深度学习请求
    print("\n测试2: 深度学习请求")
    result2 = scheduler.process_request(session_id, "帮我深度学习AI OS的架构设计")
    print(f"输入: {result2['user_input']}")
    print(f"意图: {result2['intent']['type']}")
    print(f"场景: {result2['scene']['type']}")
    print(f"决策: {result2['decision']['scene_type']}")
    print(f"主引擎: {result2['decision']['main_engine']}")
    print(f"沉淀: {result2['precipitation']['reason'] if result2['precipitation'] else '无'}")
    
    # 测试用例3: 动态调整
    print("\n测试3: 动态调整（用户反馈）")
    result3 = scheduler.process_request(
        session_id, 
        "这个问题更复杂，需要多维度分析",
        user_feedback="用五色光详细分析"
    )
    print(f"输入: {result3['user_input']}")
    print(f"反馈: 用五色光详细分析")
    print(f"场景: {result3['scene']['type']}")
    print(f"决策: {result3['decision']['scene_type']}")
    print(f"主引擎: {result3['decision']['main_engine']}")
    
    # 获取会话报告
    print("\n会话报告:")
    report = scheduler.get_session_report(session_id)
    print(f"对话轮次: {report['dialogue_turns']}")
    print(f"当前场景: {report['current_scene']}")
    print(f"是否沉淀: {report['has_precipitation_card']}")
    
    # 列出活跃会话
    print("\n活跃会话列表:")
    active_sessions = scheduler.list_active_sessions()
    for session in active_sessions:
        print(f"  {session['session_id']}: {session['dialogue_turns']}轮对话，场景: {session['current_scene']}")
    
    print("\n测试完成。")


if __name__ == "__main__":
    test_scheduler()