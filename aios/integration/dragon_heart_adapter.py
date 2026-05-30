# 龙心OS适配器 - 核心调度中枢集成
"""
龙心OS（Dragon Heart OS）适配器
提供统一的接口调用龙心OS核心调度智能体，支持：
1. 意图识别和场景分类（S0-S9）
2. 引擎智能路由（1+5架构）
3. 子智能体调用（知行合一、知识学习、人机协同五象限、象思维、五色光思维）
4. 动态调整和结果整合

基于龙心OS调度协议（dispatch-protocol.md）和场景识别矩阵（scene-router.md）
"""

import json
import logging
import uuid
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from enum import Enum

# 导入技能调用层
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from skills.skill_invoker import SkillInvoker
from skills.parameter_handler import ParameterHandler
from skills.error_handler import CompositeErrorHandler

logger = logging.getLogger(__name__)


class IntentType(Enum):
    """六大意图类型（来自龙心OS scene-router.md）"""
    GET_INFORMATION = "获取信息"
    DEEP_UNDERSTANDING = "深度理解"
    INNOVATION_BREAKTHROUGH = "创新突破"
    ANALYSIS_DECISION = "分析决策"
    TASK_EXECUTION = "任务执行"
    SYSTEM_EVOLUTION = "系统进化"


class SceneType(Enum):
    """S0-S9场景类型（来自龙心OS scene-router.md）"""
    S0_EXTREME_SIMPLE = "极简问答型"
    S1_INFORMATION_QUERY = "信息查询型"
    S2_DEEP_LEARNING = "深度学习型"
    S3_INNOVATION_BREAKTHROUGH = "创新突破型"
    S4_ANALYSIS_DECISION = "分析决策型"
    S5_MAJOR_DECISION = "重大决策型"
    S6_TASK_EXECUTION = "任务执行型"
    S7_SYSTEM_PLANNING = "系统规划型"
    S8_CULTIVATION_CULTURE = "修行文化型"
    S9_SYSTEM_EVOLUTION = "系统进化型"


class EngineType(Enum):
    """五大引擎类型（1+5架构）"""
    KNOWLEDGE_LEARNING = "知识学习"
    IMAGE_THINKING = "象思维"
    FIVE_COLOR_THINKING = "五色光思维"
    HUMAN_AI_COLLABORATION = "人机协同五象限"
    KNOWING_DOING_UNITY = "知行合一"


class RecipeType(Enum):
    """调度配方类型（来自龙心OS dispatch-protocol.md）"""
    MAJOR_DECISION = "重大决策配方"
    INNOVATION_BREAKTHROUGH = "创新突破配方"
    DEEP_LEARNING = "深度学习配方"
    STRUCTURED_ANALYSIS = "结构化分析配方"
    DAILY_COLLABORATION = "日常协作配方"


class DragonHeartAdapter:
    """龙心OS适配器"""
    
    def __init__(self, skill_invoker: Optional[SkillInvoker] = None):
        """
        初始化龙心OS适配器
        
        Args:
            skill_invoker: 技能调用器实例，如果为None则创建新实例
        """
        self.skill_invoker = skill_invoker or SkillInvoker()
        self.param_handler = ParameterHandler()
        self.error_handler = CompositeErrorHandler()
        
        # 龙心OS技能名称（根据WorkBuddy技能目录）
        self.skill_name = "龙心OS"
        
        # 调用协议版本
        self.protocol_version = "v6.0"
        
        # 场景到引擎的映射（来自trigger-rules.yaml）
        self.scene_to_engines_mapping = {
            SceneType.S0_EXTREME_SIMPLE: [],
            SceneType.S1_INFORMATION_QUERY: [EngineType.KNOWLEDGE_LEARNING],
            SceneType.S2_DEEP_LEARNING: [EngineType.KNOWLEDGE_LEARNING, EngineType.IMAGE_THINKING, EngineType.KNOWING_DOING_UNITY],
            SceneType.S3_INNOVATION_BREAKTHROUGH: [EngineType.IMAGE_THINKING, EngineType.FIVE_COLOR_THINKING, EngineType.KNOWING_DOING_UNITY],
            SceneType.S4_ANALYSIS_DECISION: [EngineType.FIVE_COLOR_THINKING, EngineType.KNOWING_DOING_UNITY],
            SceneType.S5_MAJOR_DECISION: [EngineType.IMAGE_THINKING, EngineType.KNOWLEDGE_LEARNING, EngineType.FIVE_COLOR_THINKING, EngineType.HUMAN_AI_COLLABORATION, EngineType.KNOWING_DOING_UNITY],
            SceneType.S6_TASK_EXECUTION: [EngineType.HUMAN_AI_COLLABORATION],
            SceneType.S7_SYSTEM_PLANNING: [EngineType.HUMAN_AI_COLLABORATION, EngineType.FIVE_COLOR_THINKING, EngineType.KNOWING_DOING_UNITY],
            SceneType.S8_CULTIVATION_CULTURE: [EngineType.IMAGE_THINKING, EngineType.KNOWLEDGE_LEARNING, EngineType.KNOWING_DOING_UNITY],
            SceneType.S9_SYSTEM_EVOLUTION: [EngineType.KNOWING_DOING_UNITY]
        }
        
        # 配方到引擎序列的映射（来自dispatch-protocol.md）
        self.recipe_to_engines_mapping = {
            RecipeType.MAJOR_DECISION: [
                EngineType.IMAGE_THINKING,
                EngineType.KNOWLEDGE_LEARNING,
                EngineType.FIVE_COLOR_THINKING,
                EngineType.HUMAN_AI_COLLABORATION,
                EngineType.KNOWING_DOING_UNITY
            ],
            RecipeType.INNOVATION_BREAKTHROUGH: [
                EngineType.IMAGE_THINKING,
                EngineType.FIVE_COLOR_THINKING,
                EngineType.KNOWING_DOING_UNITY
            ],
            RecipeType.DEEP_LEARNING: [
                EngineType.KNOWLEDGE_LEARNING,
                EngineType.IMAGE_THINKING,
                EngineType.KNOWING_DOING_UNITY
            ],
            RecipeType.STRUCTURED_ANALYSIS: [
                EngineType.FIVE_COLOR_THINKING,
                EngineType.KNOWING_DOING_UNITY
            ],
            RecipeType.DAILY_COLLABORATION: [
                EngineType.HUMAN_AI_COLLABORATION,
                EngineType.KNOWING_DOING_UNITY
            ]
        }
        
        logger.info(f"龙心OS适配器初始化完成，技能名称：{self.skill_name}")
    
    def process_user_input(self,
                          user_input: str,
                          context: Optional[Dict[str, Any]] = None,
                          enable_automatic_routing: bool = True) -> Dict[str, Any]:
        """
        处理用户输入（完整的龙心OS调度流程）
        
        Args:
            user_input: 用户输入文本
            context: 上下文信息（对话历史、用户偏好等）
            enable_automatic_routing: 是否启用自动路由（默认True）
            
        Returns:
            处理结果字典，包含：
            - success: 是否成功
            - intent_analysis: 意图分析结果
            - scene_classification: 场景分类结果
            - routing_decision: 路由决策
            - engine_sequence: 引擎调用序列
            - error: 错误信息（如果失败）
        """
        start_time = datetime.now()
        
        try:
            # 1. 意图识别
            intent_result = self.analyze_intent(user_input, context)
            if not intent_result["success"]:
                return intent_result
            
            # 2. 场景分类
            scene_result = self.classify_scene(user_input, intent_result["intent"], context)
            if not scene_result["success"]:
                return scene_result
            
            # 3. 引擎路由（如果启用自动路由）
            routing_result = None
            engine_sequence = []
            
            if enable_automatic_routing:
                routing_result = self.route_engines(
                    intent=intent_result["intent"],
                    scene=scene_result["scene"],
                    user_input=user_input,
                    context=context
                )
                
                if not routing_result["success"]:
                    return routing_result
                
                engine_sequence = routing_result.get("engine_sequence", [])
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"龙心OS处理完成，场景：{scene_result['scene'].value}，意图：{intent_result['intent'].value}，执行时间：{execution_time:.2f}秒")
            
            return {
                "success": True,
                "intent_analysis": intent_result,
                "scene_classification": scene_result,
                "routing_decision": routing_result,
                "engine_sequence": engine_sequence,
                "execution_time": execution_time,
                "metadata": {
                    "protocol_version": self.protocol_version,
                    "user_input_preview": user_input[:50] + "..." if len(user_input) > 50 else user_input,
                    "enable_automatic_routing": enable_automatic_routing,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.exception(f"龙心OS处理异常：{str(e)}")
            return {
                "success": False,
                "error": f"适配器内部错误：{str(e)}",
                "execution_time": execution_time
            }
    
    def analyze_intent(self,
                      user_input: str,
                      context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        分析用户意图（六大意图类型）
        
        Args:
            user_input: 用户输入文本
            context: 上下文信息
            
        Returns:
            意图分析结果字典
        """
        start_time = datetime.now()
        
        try:
            # 构建意图分析请求
            request = self._build_intent_analysis_request(user_input, context or {})
            
            logger.info(f"龙心OS意图分析，输入长度：{len(user_input)}字符")
            
            # 调用龙心OS技能
            result = self.error_handler.execute_with_retry(
                func=self._call_dragon_heart_skill,
                func_args=["analyze_intent", request],
                operation_name="龙心OS意图分析"
            )
            
            # 验证和解析响应
            if not result.get("success", False):
                error_msg = result.get("error", "未知错误")
                logger.error(f"龙心OS意图分析失败：{error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "execution_time": (datetime.now() - start_time).total_seconds()
                }
            
            # 提取意图分析结果
            response_data = result.get("data", {})
            intent_analysis = self._parse_intent_analysis(response_data)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"龙心OS意图分析成功，意图：{intent_analysis.get('primary_intent', '未知')}，执行时间：{execution_time:.2f}秒")
            
            return {
                "success": True,
                "intent": intent_analysis.get("primary_intent"),
                "confidence": intent_analysis.get("confidence", 0.0),
                "supporting_evidence": intent_analysis.get("supporting_evidence", []),
                "alternative_intents": intent_analysis.get("alternative_intents", []),
                "execution_time": execution_time,
                "raw_analysis": intent_analysis
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.exception(f"龙心OS意图分析异常：{str(e)}")
            return {
                "success": False,
                "error": f"适配器内部错误：{str(e)}",
                "execution_time": execution_time
            }
    
    def classify_scene(self,
                      user_input: str,
                      intent: IntentType,
                      context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        场景分类（S0-S9）
        
        Args:
            user_input: 用户输入文本
            intent: 已识别的意图类型
            context: 上下文信息
            
        Returns:
            场景分类结果字典
        """
        start_time = datetime.now()
        
        try:
            # 构建场景分类请求
            request = self._build_scene_classification_request(user_input, intent, context or {})
            
            logger.info(f"龙心OS场景分类，意图：{intent.value}")
            
            # 调用龙心OS技能
            result = self.error_handler.execute_with_retry(
                func=self._call_dragon_heart_skill,
                func_args=["classify_scene", request],
                operation_name="龙心OS场景分类"
            )
            
            # 验证和解析响应
            if not result.get("success", False):
                error_msg = result.get("error", "未知错误")
                logger.error(f"龙心OS场景分类失败：{error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "execution_time": (datetime.now() - start_time).total_seconds()
                }
            
            # 提取场景分类结果
            response_data = result.get("data", {})
            scene_classification = self._parse_scene_classification(response_data)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"龙心OS场景分类成功，场景：{scene_classification.get('primary_scene', '未知')}，执行时间：{execution_time:.2f}秒")
            
            return {
                "success": True,
                "scene": scene_classification.get("primary_scene"),
                "confidence": scene_classification.get("confidence", 0.0),
                "complexity": scene_classification.get("complexity", "中等"),
                "urgency": scene_classification.get("urgency", "普通"),
                "execution_time": execution_time,
                "raw_classification": scene_classification
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.exception(f"龙心OS场景分类异常：{str(e)}")
            return {
                "success": False,
                "error": f"适配器内部错误：{str(e)}",
                "execution_time": execution_time
            }
    
    def route_engines(self,
                     intent: IntentType,
                     scene: SceneType,
                     user_input: str,
                     context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        引擎路由（根据意图和场景确定引擎调用序列）
        
        Args:
            intent: 意图类型
            scene: 场景类型
            user_input: 用户输入文本
            context: 上下文信息
            
        Returns:
            路由决策结果字典
        """
        start_time = datetime.now()
        
        try:
            # 确定引擎序列
            engine_sequence = self.scene_to_engines_mapping.get(scene, [])
            
            # 如果场景没有映射，使用默认配方
            if not engine_sequence:
                recipe = self._select_recipe(intent, scene, user_input)
                engine_sequence = self.recipe_to_engines_mapping.get(recipe, [])
            
            # 构建路由决策
            routing_decision = {
                "intent": intent.value,
                "scene": scene.value,
                "engine_sequence": [engine.value for engine in engine_sequence],
                "rationale": self._generate_routing_rationale(intent, scene, engine_sequence),
                "estimated_complexity": self._estimate_complexity(engine_sequence),
                "timestamp": datetime.now().isoformat()
            }
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"龙心OS引擎路由完成，引擎数量：{len(engine_sequence)}，执行时间：{execution_time:.2f}秒")
            
            return {
                "success": True,
                "routing_decision": routing_decision,
                "engine_sequence": engine_sequence,
                "execution_time": execution_time,
                "metadata": {
                    "protocol_version": self.protocol_version,
                    "scene": scene.value,
                    "intent": intent.value
                }
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.exception(f"龙心OS引擎路由异常：{str(e)}")
            return {
                "success": False,
                "error": f"适配器内部错误：{str(e)}",
                "execution_time": execution_time
            }
    
    def invoke_engine(self,
                     engine: EngineType,
                     input_data: Dict[str, Any],
                     context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        调用单个引擎
        
        Args:
            engine: 引擎类型
            input_data: 输入数据
            context: 上下文信息
            
        Returns:
            引擎调用结果字典
        """
        start_time = datetime.now()
        
        try:
            # 构建引擎调用请求
            request = self._build_engine_invocation_request(engine, input_data, context or {})
            
            logger.info(f"调用龙心OS引擎：{engine.value}")
            
            # 调用龙心OS技能
            result = self.error_handler.execute_with_retry(
                func=self._call_dragon_heart_skill,
                func_args=["invoke_engine", request],
                operation_name=f"龙心OS引擎调用_{engine.value}"
            )
            
            # 验证和解析响应
            if not result.get("success", False):
                error_msg = result.get("error", "未知错误")
                logger.error(f"龙心OS引擎调用失败：{error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "execution_time": (datetime.now() - start_time).total_seconds()
                }
            
            # 提取引擎调用结果
            response_data = result.get("data", {})
            engine_result = self._parse_engine_result(response_data, engine)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"龙心OS引擎调用成功，引擎：{engine.value}，执行时间：{execution_time:.2f}秒")
            
            return {
                "success": True,
                "engine": engine.value,
                "result": engine_result,
                "execution_time": execution_time,
                "metadata": {
                    "protocol_version": self.protocol_version,
                    "engine_type": engine.value,
                    "input_preview": str(input_data)[:100] + "..." if len(str(input_data)) > 100 else str(input_data)
                }
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.exception(f"龙心OS引擎调用异常：{str(e)}")
            return {
                "success": False,
                "error": f"适配器内部错误：{str(e)}",
                "execution_time": execution_time
            }
    
    def invoke_engine_sequence(self,
                              engine_sequence: List[EngineType],
                              input_data: Dict[str, Any],
                              context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        调用引擎序列（按顺序执行多个引擎）
        
        Args:
            engine_sequence: 引擎序列
            input_data: 输入数据
            context: 上下文信息
            
        Returns:
            序列调用结果字典
        """
        start_time = datetime.now()
        results = []
        current_data = input_data
        
        try:
            for i, engine in enumerate(engine_sequence):
                logger.info(f"执行引擎序列第{i+1}/{len(engine_sequence)}步：{engine.value}")
                
                # 调用单个引擎
                engine_result = self.invoke_engine(engine, current_data, context)
                
                if not engine_result["success"]:
                    logger.error(f"引擎序列在第{i+1}步失败，引擎：{engine.value}")
                    return {
                        "success": False,
                        "error": f"引擎序列在第{i+1}步失败：{engine_result.get('error', '未知错误')}",
                        "completed_engines": [eng.value for eng in engine_sequence[:i]],
                        "failed_engine": engine.value,
                        "partial_results": results,
                        "execution_time": (datetime.now() - start_time).total_seconds()
                    }
                
                # 保存结果
                results.append({
                    "engine": engine.value,
                    "result": engine_result["result"],
                    "execution_time": engine_result["execution_time"]
                })
                
                # 更新当前数据（将上一个引擎的输出作为下一个引擎的输入）
                if "output" in engine_result["result"]:
                    current_data = {"previous_output": engine_result["result"]["output"]}
                elif "analysis_result" in engine_result["result"]:
                    current_data = {"previous_analysis": engine_result["result"]["analysis_result"]}
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"引擎序列执行完成，共{len(engine_sequence)}个引擎，总执行时间：{execution_time:.2f}秒")
            
            return {
                "success": True,
                "results": results,
                "total_execution_time": execution_time,
                "metadata": {
                    "protocol_version": self.protocol_version,
                    "engine_count": len(engine_sequence),
                    "engines_executed": [engine.value for engine in engine_sequence]
                }
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.exception(f"引擎序列调用异常：{str(e)}")
            return {
                "success": False,
                "error": f"适配器内部错误：{str(e)}",
                "execution_time": execution_time,
                "partial_results": results
            }
    
    def _build_intent_analysis_request(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """构建意图分析请求"""
        
        request = {
            "operation": "analyze_intent",
            "user_input": user_input,
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "caller": "AI_OS_WorkBuddy_Integration"
        }
        
        return request
    
    def _build_scene_classification_request(self, user_input: str, intent: IntentType, context: Dict[str, Any]) -> Dict[str, Any]:
        """构建场景分类请求"""
        
        request = {
            "operation": "classify_scene",
            "user_input": user_input,
            "intent": intent.value,
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "caller": "AI_OS_WorkBuddy_Integration"
        }
        
        return request
    
    def _build_engine_invocation_request(self, engine: EngineType, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """构建引擎调用请求"""
        
        request = {
            "operation": "invoke_engine",
            "engine": engine.value,
            "input_data": input_data,
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "caller": "AI_OS_WorkBuddy_Integration"
        }
        
        return request
    
    def _call_dragon_heart_skill(self, operation: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """调用龙心OS技能（实际技能调用）"""
        
        # 参数验证和转换
        validated_params = self.param_handler.validate_and_convert(
            skill_name=self.skill_name,
            function_name=operation,
            parameters=request
        )
        
        # 调用技能
        result = self.skill_invoker.invoke_skill(
            skill_name=self.skill_name,
            function_name=operation,
            parameters=validated_params,
            timeout=60  # 龙心OS操作可能需要较长时间
        )
        
        return result
    
    def _parse_intent_analysis(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """解析意图分析响应"""
        
        # 提供默认值
        intent_analysis = {
            "primary_intent": IntentType.GET_INFORMATION,
            "confidence": 0.8,
            "supporting_evidence": [],
            "alternative_intents": [],
            "raw_response": response_data
        }
        
        # 尝试从响应中提取意图
        if "intent" in response_data:
            intent_str = response_data["intent"]
            try:
                intent_analysis["primary_intent"] = IntentType(intent_str)
            except:
                # 尝试映射字符串到枚举
                for intent_enum in IntentType:
                    if intent_str == intent_enum.value:
                        intent_analysis["primary_intent"] = intent_enum
                        break
        
        if "confidence" in response_data:
            intent_analysis["confidence"] = response_data["confidence"]
        
        if "evidence" in response_data:
            intent_analysis["supporting_evidence"] = response_data["evidence"]
        
        return intent_analysis
    
    def _parse_scene_classification(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """解析场景分类响应"""
        
        # 提供默认值
        scene_classification = {
            "primary_scene": SceneType.S0_EXTREME_SIMPLE,
            "confidence": 0.8,
            "complexity": "中等",
            "urgency": "普通",
            "raw_response": response_data
        }
        
        # 尝试从响应中提取场景
        if "scene" in response_data:
            scene_str = response_data["scene"]
            try:
                # 尝试解析为S0-S9格式
                if scene_str.startswith("S"):
                    scene_number = int(scene_str[1:])
                    scene_mapping = {
                        0: SceneType.S0_EXTREME_SIMPLE,
                        1: SceneType.S1_INFORMATION_QUERY,
                        2: SceneType.S2_DEEP_LEARNING,
                        3: SceneType.S3_INNOVATION_BREAKTHROUGH,
                        4: SceneType.S4_ANALYSIS_DECISION,
                        5: SceneType.S5_MAJOR_DECISION,
                        6: SceneType.S6_TASK_EXECUTION,
                        7: SceneType.S7_SYSTEM_PLANNING,
                        8: SceneType.S8_CULTIVATION_CULTURE,
                        9: SceneType.S9_SYSTEM_EVOLUTION
                    }
                    if scene_number in scene_mapping:
                        scene_classification["primary_scene"] = scene_mapping[scene_number]
            except:
                # 尝试直接匹配
                for scene_enum in SceneType:
                    if scene_str == scene_enum.value or scene_str == scene_enum.name:
                        scene_classification["primary_scene"] = scene_enum
                        break
        
        if "confidence" in response_data:
            scene_classification["confidence"] = response_data["confidence"]
        
        if "complexity" in response_data:
            scene_classification["complexity"] = response_data["complexity"]
        
        if "urgency" in response_data:
            scene_classification["urgency"] = response_data["urgency"]
        
        return scene_classification
    
    def _parse_engine_result(self, response_data: Dict[str, Any], engine: EngineType) -> Dict[str, Any]:
        """解析引擎调用结果"""
        
        # 根据引擎类型提供不同的默认结构
        engine_result = {
            "engine": engine.value,
            "status": "完成",
            "output": response_data.get("output", {}),
            "analysis_result": response_data.get("analysis_result", {}),
            "recommendations": response_data.get("recommendations", []),
            "next_steps": response_data.get("next_steps", []),
            "confidence": response_data.get("confidence", 0.8),
            "raw_response": response_data
        }
        
        return engine_result
    
    def _select_recipe(self, intent: IntentType, scene: SceneType, user_input: str) -> RecipeType:
        """选择调度配方"""
        
        # 根据意图和场景选择配方
        if intent == IntentType.MAJOR_DECISION or scene == SceneType.S5_MAJOR_DECISION:
            return RecipeType.MAJOR_DECISION
        
        if intent == IntentType.INNOVATION_BREAKTHROUGH or scene == SceneType.S3_INNOVATION_BREAKTHROUGH:
            return RecipeType.INNOVATION_BREAKTHROUGH
        
        if intent == IntentType.DEEP_UNDERSTANDING or scene == SceneType.S2_DEEP_LEARNING:
            return RecipeType.DEEP_LEARNING
        
        if intent == IntentType.ANALYSIS_DECISION or scene == SceneType.S4_ANALYSIS_DECISION:
            return RecipeType.STRUCTURED_ANALYSIS
        
        if intent == IntentType.TASK_EXECUTION or scene == SceneType.S6_TASK_EXECUTION:
            return RecipeType.DAILY_COLLABORATION
        
        # 默认返回日常协作配方
        return RecipeType.DAILY_COLLABORATION
    
    def _generate_routing_rationale(self, intent: IntentType, scene: SceneType, engine_sequence: List[EngineType]) -> str:
        """生成路由决策的理由"""
        
        rationale = f"意图为{intent.value}，场景为{scene.value}，"
        
        if engine_sequence:
            engine_names = [engine.value for engine in engine_sequence]
            rationale += f"推荐引擎序列：{' → '.join(engine_names)}。"
            
            if len(engine_sequence) == 1:
                rationale += "使用单引擎快速响应。"
            elif len(engine_sequence) >= 4:
                rationale += "使用全系统启动进行深度分析。"
            else:
                rationale += "使用组合引擎实现最佳效果。"
        else:
            rationale += "无需启动引擎，直接回答即可。"
        
        return rationale
    
    def _estimate_complexity(self, engine_sequence: List[EngineType]) -> str:
        """估计执行复杂度"""
        
        if not engine_sequence:
            return "极简"
        
        engine_count = len(engine_sequence)
        
        if engine_count == 1:
            return "简单"
        elif engine_count <= 3:
            return "中等"
        else:
            return "复杂"
    
    def get_available_engines(self) -> List[Dict[str, Any]]:
        """获取可用的引擎列表"""
        
        engines = [
            {
                "name": EngineType.KNOWLEDGE_LEARNING.value,
                "description": "知识学习引擎：十项认知指令逐层深入，深度学习与知识重构",
                "icon": "📚",
                "scenes": ["S1", "S2", "S5", "S8"],
                "intents": ["获取信息", "深度理解", "系统进化"]
            },
            {
                "name": EngineType.IMAGE_THINKING.value,
                "description": "象思维引擎：0→1直觉洞察，整体感知与原创突破",
                "icon": "🐉",
                "scenes": ["S2", "S3", "S5", "S8"],
                "intents": ["创新突破", "深度理解", "系统进化"]
            },
            {
                "name": EngineType.FIVE_COLOR_THINKING.value,
                "description": "五色光思维引擎：多维度结构化分析，白→绿→黄→蓝→红完整序列",
                "icon": "🌈",
                "scenes": ["S3", "S4", "S5", "S7"],
                "intents": ["分析决策", "创新突破", "系统规划"]
            },
            {
                "name": EngineType.HUMAN_AI_COLLABORATION.value,
                "description": "人机协同五象限引擎：五象限分工协作，高效执行与任务落地",
                "icon": "🤝",
                "scenes": ["S5", "S6", "S7"],
                "intents": ["任务执行", "系统规划", "重大决策"]
            },
            {
                "name": EngineType.KNOWING_DOING_UNITY.value,
                "description": "知行合一引擎：表示空间→压缩→泛化，经验沉淀与系统进化",
                "icon": "🔄",
                "scenes": ["S0-S9全部"],  # 知行合一始终参与
                "intents": ["系统进化", "所有意图"]
            }
        ]
        
        return engines


# 简化版本适配器（用于测试和快速集成）
class SimpleDragonHeartAdapter:
    """简化版龙心OS适配器（不依赖技能调用层）"""
    
    def __init__(self):
        self.protocol_version = "v6.0"
        logger.info("简化版龙心OS适配器初始化")
    
    def process_user_input(self, user_input, **kwargs):
        """简化处理用户输入（模拟响应）"""
        
        # 模拟意图分析
        intent = IntentType.GET_INFORMATION
        if "分析" in user_input or "决策" in user_input:
            intent = IntentType.ANALYSIS_DECISION
        elif "学习" in user_input or "理解" in user_input:
            intent = IntentType.DEEP_UNDERSTANDING
        elif "创新" in user_input or "想法" in user_input:
            intent = IntentType.INNOVATION_BREAKTHROUGH
        elif "执行" in user_input or "做" in user_input:
            intent = IntentType.TASK_EXECUTION
        elif "总结" in user_input or "复盘" in user_input:
            intent = IntentType.SYSTEM_EVOLUTION
        
        # 模拟场景分类
        scene = SceneType.S0_EXTREME_SIMPLE
        if len(user_input) > 100:
            scene = SceneType.S2_DEEP_LEARNING
        elif "重要" in user_input or "重大" in user_input:
            scene = SceneType.S5_MAJOR_DECISION
        elif "规划" in user_input or "系统" in user_input:
            scene = SceneType.S7_SYSTEM_PLANNING
        
        # 模拟引擎路由
        engine_sequence = []
        if scene == SceneType.S5_MAJOR_DECISION:
            engine_sequence = [
                EngineType.IMAGE_THINKING,
                EngineType.KNOWLEDGE_LEARNING,
                EngineType.FIVE_COLOR_THINKING,
                EngineType.HUMAN_AI_COLLABORATION,
                EngineType.KNOWING_DOING_UNITY
            ]
        elif scene == SceneType.S2_DEEP_LEARNING:
            engine_sequence = [
                EngineType.KNOWLEDGE_LEARNING,
                EngineType.IMAGE_THINKING,
                EngineType.KNOWING_DOING_UNITY
            ]
        
        return {
            "success": True,
            "intent_analysis": {
                "intent": intent,
                "confidence": 0.85,
                "supporting_evidence": ["输入长度分析", "关键词匹配"]
            },
            "scene_classification": {
                "scene": scene,
                "confidence": 0.8,
                "complexity": "中等",
                "urgency": "普通"
            },
            "routing_decision": {
                "engine_sequence": [engine.value for engine in engine_sequence],
                "rationale": f"基于意图{intent.value}和场景{scene.value}的路由决策"
            },
            "engine_sequence": engine_sequence,
            "execution_time": 0.3,
            "metadata": {
                "protocol_version": self.protocol_version,
                "is_simulation": True
            }
        }
    
    def invoke_engine(self, engine, input_data, **kwargs):
        """简化引擎调用（模拟响应）"""
        
        engine_result = {
            "engine": engine.value,
            "status": "完成",
            "output": {
                "analysis": f"{engine.value}引擎执行完成",
                "key_insights": ["模拟洞察1", "模拟洞察2"],
                "recommendations": ["建议1", "建议2"]
            },
            "confidence": 0.9
        }
        
        return {
            "success": True,
            "engine": engine.value,
            "result": engine_result,
            "execution_time": 0.2
        }


if __name__ == "__main__":
    # 测试适配器
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("测试龙心OS适配器...")
    
    # 使用简化版适配器进行测试
    adapter = SimpleDragonHeartAdapter()
    
    # 测试处理用户输入
    result = adapter.process_user_input(
        user_input="我需要做一个重大决策，关于公司未来的发展方向"
    )
    
    print(f"处理结果：{result['success']}")
    if result['success']:
        print(f"意图：{result['intent_analysis']['intent'].value}")
        print(f"场景：{result['scene_classification']['scene'].value}")
        print(f"引擎序列：{result['routing_decision']['engine_sequence']}")
        
        # 测试引擎调用
        if result['engine_sequence']:
            engine = result['engine_sequence'][0]
            engine_result = adapter.invoke_engine(
                engine=engine,
                input_data={"topic": "重大决策分析"}
            )
            print(f"引擎调用结果：{engine_result['success']}")
            if engine_result['success']:
                print(f"引擎输出：{engine_result['result']['output']['analysis']}")