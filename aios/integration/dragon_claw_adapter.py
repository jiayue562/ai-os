# 龙爪OS适配器 - 项目执行引擎集成
"""
龙爪OS（Dragon Claw OS）适配器
提供统一的接口调用龙爪OS项目执行智能体，支持：
1. 项目管理（启动、监控、调整）
2. 工作流引擎（步骤分解、执行、状态跟踪）
3. SOP标准化流程
4. 与龙心OS、龙脑OS的协同

基于龙心OS-龙爪OS调用协议 v1.0（integration.md）
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


class ProjectType(Enum):
    """项目类型枚举"""
    CULTURE_PROJECT = "企业文化项目"
    FIVE_ELEMENTS_PROJECT = "五行人格项目"
    WORKFLOW_PROJECT = "工作流项目"
    SOP_PROJECT = "SOP标准化项目"
    CUSTOM_PROJECT = "自定义项目"


class ProjectPhase(Enum):
    """项目阶段枚举"""
    INITIATION = "启动阶段"
    PLANNING = "规划阶段"
    EXECUTION = "执行阶段"
    MONITORING = "监控阶段"
    CLOSURE = "收尾阶段"


class StepType(Enum):
    """工作流步骤类型"""
    DATA_COLLECTION = "数据收集"
    PROBLEM_ANALYSIS = "问题分析"
    INNOVATION_SOLUTION = "创新方案"
    VALUE_EVALUATION = "价值评估"
    DECISION_MAKING = "决策制定"
    INTERPERSONAL_ANALYSIS = "人际分析"
    STRATEGIC_PLANNING = "战略规划"
    EXECUTION_IMPLEMENTATION = "执行落地"


class DragonClawAdapter:
    """龙爪OS适配器"""
    
    def __init__(self, skill_invoker: Optional[SkillInvoker] = None):
        """
        初始化龙爪OS适配器
        
        Args:
            skill_invoker: 技能调用器实例，如果为None则创建新实例
        """
        self.skill_invoker = skill_invoker or SkillInvoker()
        self.param_handler = ParameterHandler()
        self.error_handler = CompositeErrorHandler()
        
        # 龙爪OS技能名称（根据WorkBuddy技能目录）
        self.skill_name = "龙爪OS"
        
        # 调用协议版本
        self.protocol_version = "LongXin-to-LongZhao-Protocol-v1"
        
        # 场景到项目类型的映射
        self.scene_to_project_mapping = {
            "S7": ProjectType.CULTURE_PROJECT,  # 系统规划
            "S9": ProjectType.WORKFLOW_PROJECT,  # 系统升级
            "S5": ProjectType.FIVE_ELEMENTS_PROJECT,  # 重大决策（可能涉及人格分析）
            "S6": ProjectType.SOP_PROJECT,  # 任务执行
        }
        
        # 步骤类型到思维模型的映射（来自integration.md的选择矩阵）
        self.step_to_model_mapping = {
            StepType.DATA_COLLECTION: {
                "primary": "白光思维",
                "secondary": ["麦肯锡七步成诗"],
                "reasoning": "客观事实收集+结构化分析"
            },
            StepType.PROBLEM_ANALYSIS: {
                "primary": "蓝光思维",
                "secondary": ["根因分析"],
                "reasoning": "风险识别+深层原因分析"
            },
            StepType.INNOVATION_SOLUTION: {
                "primary": "绿光思维",
                "secondary": ["象思维"],
                "reasoning": "发散思维+0→1突破创新"
            },
            StepType.VALUE_EVALUATION: {
                "primary": "黄光思维",
                "secondary": ["成本效益分析"],
                "reasoning": "积极思维+量化评估"
            },
            StepType.DECISION_MAKING: {
                "primary": "五色光完整序列",
                "secondary": ["二阶思维"],
                "reasoning": "全面分析+长远考虑"
            },
            StepType.INTERPERSONAL_ANALYSIS: {
                "primary": "五行人格心理学OS",
                "secondary": ["非暴力沟通"],
                "reasoning": "人格洞察+沟通技巧"
            },
            StepType.STRATEGIC_PLANNING: {
                "primary": "第一性原理",
                "secondary": ["二阶思维"],
                "reasoning": "本质分析+长远规划"
            },
            StepType.EXECUTION_IMPLEMENTATION: {
                "primary": "知行合一",
                "secondary": ["PDCA循环"],
                "reasoning": "实践执行+迭代优化"
            }
        }
        
        logger.info(f"龙爪OS适配器初始化完成，技能名称：{self.skill_name}")
    
    def start_project(self,
                     scene_type: str,
                     requirements: str,
                     project_type: Optional[ProjectType] = None,
                     complexity: str = "中等",
                     urgency: str = "普通",
                     context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        启动新项目
        
        Args:
            scene_type: 场景类型（S0-S9）
            requirements: 项目需求描述
            project_type: 项目类型（如果未指定则根据场景自动选择）
            complexity: 复杂度（"简单"/"中等"/"复杂"）
            urgency: 紧急度（"紧急"/"普通"/"可延期"）
            context: 上下文信息（用户偏好、历史记录等）
            
        Returns:
            启动结果字典，包含：
            - success: 是否成功
            - project_id: 项目ID（如果成功）
            - project_info: 项目信息
            - error: 错误信息（如果失败）
        """
        start_time = datetime.now()
        
        try:
            # 1. 确定项目类型
            if not project_type:
                project_type = self._determine_project_type(scene_type, requirements)
            
            # 2. 构建启动请求
            request = self._build_project_start_request(
                scene_type=scene_type,
                requirements=requirements,
                project_type=project_type,
                complexity=complexity,
                urgency=urgency,
                context=context or {}
            )
            
            logger.info(f"启动龙爪OS项目，场景：{scene_type}，类型：{project_type.value}")
            
            # 3. 调用龙爪OS技能
            result = self.error_handler.execute_with_retry(
                func=self._call_dragon_claw_skill,
                func_args=["start_project", request],
                operation_name=f"龙爪OS启动项目_{project_type.value}"
            )
            
            # 4. 验证和解析响应
            if not result.get("success", False):
                error_msg = result.get("error", "未知错误")
                logger.error(f"龙爪OS项目启动失败：{error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "execution_time": (datetime.now() - start_time).total_seconds()
                }
            
            # 5. 提取项目信息
            response_data = result.get("data", {})
            project_info = self._parse_project_start_response(response_data)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"龙爪OS项目启动成功，项目ID：{project_info.get('id', '未知')}，执行时间：{execution_time:.2f}秒")
            
            return {
                "success": True,
                "project_id": project_info.get("id", str(uuid.uuid4())),
                "project_info": project_info,
                "execution_time": execution_time,
                "metadata": {
                    "protocol_version": self.protocol_version,
                    "scene_type": scene_type,
                    "project_type": project_type.value,
                    "complexity": complexity,
                    "urgency": urgency
                }
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.exception(f"龙爪OS项目启动异常：{str(e)}")
            return {
                "success": False,
                "error": f"适配器内部错误：{str(e)}",
                "execution_time": execution_time
            }
    
    def execute_workflow_step(self,
                            project_id: str,
                            step_type: StepType,
                            step_data: Dict[str, Any],
                            step_number: Optional[int] = None,
                            use_models: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        执行工作流步骤
        
        Args:
            project_id: 项目ID
            step_type: 步骤类型
            step_data: 步骤输入数据
            step_number: 步骤序号（可选）
            use_models: 指定使用的模型（可选，如果未指定则根据步骤类型自动选择）
            
        Returns:
            执行结果字典，包含：
            - success: 是否成功
            - step_result: 步骤执行结果
            - next_step: 下一步建议
            - error: 错误信息（如果失败）
        """
        start_time = datetime.now()
        
        try:
            # 1. 确定使用的模型
            if not use_models:
                model_config = self.step_to_model_mapping.get(step_type, {})
                primary_model = model_config.get("primary", "白光思维")
                secondary_models = model_config.get("secondary", [])
                use_models = [primary_model] + secondary_models
            
            # 2. 构建步骤执行请求
            request = self._build_workflow_step_request(
                project_id=project_id,
                step_type=step_type,
                step_data=step_data,
                step_number=step_number,
                use_models=use_models
            )
            
            logger.info(f"执行龙爪OS工作流步骤，项目：{project_id}，步骤类型：{step_type.value}")
            
            # 3. 调用龙爪OS技能
            result = self.error_handler.execute_with_retry(
                func=self._call_dragon_claw_skill,
                func_args=["execute_workflow_step", request],
                operation_name=f"龙爪OS执行步骤_{step_type.value}"
            )
            
            # 4. 验证和解析响应
            if not result.get("success", False):
                error_msg = result.get("error", "未知错误")
                logger.error(f"龙爪OS步骤执行失败：{error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "execution_time": (datetime.now() - start_time).total_seconds()
                }
            
            # 5. 提取步骤结果
            response_data = result.get("data", {})
            step_result = self._parse_workflow_step_response(response_data)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"龙爪OS步骤执行成功，项目：{project_id}，执行时间：{execution_time:.2f}秒")
            
            return {
                "success": True,
                "step_result": step_result,
                "execution_time": execution_time,
                "metadata": {
                    "protocol_version": self.protocol_version,
                    "project_id": project_id,
                    "step_type": step_type.value,
                    "models_used": use_models
                }
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.exception(f"龙爪OS步骤执行异常：{str(e)}")
            return {
                "success": False,
                "error": f"适配器内部错误：{str(e)}",
                "execution_time": execution_time
            }
    
    def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """
        获取项目状态
        
        Args:
            project_id: 项目ID
            
        Returns:
            项目状态字典，包含：
            - success: 是否成功
            - status: 项目状态信息
            - error: 错误信息（如果失败）
        """
        start_time = datetime.now()
        
        try:
            # 构建状态查询请求
            request = {
                "operation": "get_project_status",
                "project_id": project_id,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"查询龙爪OS项目状态，项目：{project_id}")
            
            # 调用龙爪OS技能
            result = self.error_handler.execute_with_retry(
                func=self._call_dragon_claw_skill,
                func_args=["get_project_status", request],
                operation_name=f"龙爪OS查询状态_{project_id}"
            )
            
            # 验证和解析响应
            if not result.get("success", False):
                error_msg = result.get("error", "未知错误")
                logger.error(f"龙爪OS项目状态查询失败：{error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "execution_time": (datetime.now() - start_time).total_seconds()
                }
            
            # 提取状态信息
            response_data = result.get("data", {})
            project_status = self._parse_project_status_response(response_data)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"龙爪OS项目状态查询成功，项目：{project_id}，状态：{project_status.get('status', '未知')}")
            
            return {
                "success": True,
                "status": project_status,
                "execution_time": execution_time
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.exception(f"龙爪OS项目状态查询异常：{str(e)}")
            return {
                "success": False,
                "error": f"适配器内部错误：{str(e)}",
                "execution_time": execution_time
            }
    
    def _determine_project_type(self, scene_type: str, requirements: str) -> ProjectType:
        """根据场景和需求确定项目类型"""
        
        # 首先检查场景映射
        if scene_type in self.scene_to_project_mapping:
            return self.scene_to_project_mapping[scene_type]
        
        # 根据需求关键词判断
        requirements_lower = requirements.lower()
        
        if "企业文化" in requirements_lower or "文化项目" in requirements_lower:
            return ProjectType.CULTURE_PROJECT
        
        if "五行人格" in requirements_lower or "人格分析" in requirements_lower or "五行" in requirements_lower:
            return ProjectType.FIVE_ELEMENTS_PROJECT
        
        if "工作流" in requirements_lower or "流程" in requirements_lower:
            return ProjectType.WORKFLOW_PROJECT
        
        if "sop" in requirements_lower or "标准化" in requirements_lower or "标准操作" in requirements_lower:
            return ProjectType.SOP_PROJECT
        
        # 默认返回自定义项目
        return ProjectType.CUSTOM_PROJECT
    
    def _build_project_start_request(self,
                                   scene_type: str,
                                   requirements: str,
                                   project_type: ProjectType,
                                   complexity: str,
                                   urgency: str,
                                   context: Dict[str, Any]) -> Dict[str, Any]:
        """构建项目启动请求（遵循龙心OS-龙爪OS协议）"""
        
        request = {
            "from": "AI_OS_Scheduler",
            "to": "龙爪OS",
            "protocol_version": self.protocol_version,
            "timestamp": datetime.now().isoformat(),
            
            # 场景信息
            "scene": {
                "category": scene_type,
                "complexity": complexity,
                "urgency": urgency
            },
            
            # 用户意图
            "intent": {
                "type": "启动项目",
                "projectType": project_type.value,
                "requirements": requirements
            },
            
            # 上下文信息
            "context": {
                "history": context.get("conversation_history", []),
                "userPreferences": context.get("user_preferences", {}),
                "systemState": context.get("system_state", {}),
                "caller": "AI_OS_WorkBuddy_Integration"
            }
        }
        
        return request
    
    def _build_workflow_step_request(self,
                                   project_id: str,
                                   step_type: StepType,
                                   step_data: Dict[str, Any],
                                   step_number: Optional[int],
                                   use_models: List[str]) -> Dict[str, Any]:
        """构建工作流步骤执行请求"""
        
        # 确定主要模型和辅助模型
        primary_model = use_models[0] if use_models else "白光思维"
        secondary_models = use_models[1:] if len(use_models) > 1 else []
        
        request = {
            "operation": "execute_workflow_step",
            "project_id": project_id,
            "timestamp": datetime.now().isoformat(),
            
            # 步骤信息
            "step": {
                "type": step_type.value,
                "number": step_number,
                "description": f"{step_type.value}步骤",
                "data": step_data
            },
            
            # 模型需求（遵循龙爪OS-龙脑OS协议）
            "model_request": {
                "call": {
                    "requestId": str(uuid.uuid4()),
                    "timestamp": datetime.now().isoformat(),
                    "priority": "高"  # 工作流步骤通常高优先级
                },
                "models": {
                    "primary": primary_model,
                    "secondary": secondary_models,
                    "combination": "顺序" if len(use_models) > 1 else "单一"
                },
                "data": {
                    "type": "混合",
                    "content": step_data,
                    "context": f"项目{project_id}的{step_type.value}步骤"
                },
                "output": {
                    "format": "结构化",
                    "length": "详细",
                    "language": "中文"
                }
            }
        }
        
        return request
    
    def _call_dragon_claw_skill(self, operation: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """调用龙爪OS技能（实际技能调用）"""
        
        # 参数验证和转换
        validated_params = self.param_handler.validate_and_convert(
            skill_name=self.skill_name,
            function_name=operation,
            parameters=request
        )
        
        # 调用技能
        # 注意：这里假设龙爪OS技能有对应的函数（start_project, execute_workflow_step, get_project_status等）
        result = self.skill_invoker.invoke_skill(
            skill_name=self.skill_name,
            function_name=operation,
            parameters=validated_params,
            timeout=60  # 项目操作可能较长时间
        )
        
        return result
    
    def _parse_project_start_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """解析项目启动响应"""
        
        # 根据协议，响应应该包含项目信息
        # 我们提供默认值以防响应格式不匹配
        
        project_info = {
            "id": response_data.get("project_id", str(uuid.uuid4())),
            "name": response_data.get("project_name", f"项目_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            "type": response_data.get("project_type", "自定义项目"),
            "currentPhase": response_data.get("current_phase", "启动阶段"),
            "progress": response_data.get("progress", 0),
            "estimatedCompletion": response_data.get("estimated_completion", ""),
            "workflow_steps": response_data.get("workflow_steps", []),
            "created_at": datetime.now().isoformat(),
            "raw_response": response_data  # 保留原始响应以便调试
        }
        
        return project_info
    
    def _parse_workflow_step_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """解析工作流步骤响应"""
        
        step_result = {
            "step_number": response_data.get("step_number", 0),
            "step_type": response_data.get("step_type", "未知"),
            "status": response_data.get("status", "完成"),
            "output": response_data.get("output", {}),
            "analysis_result": response_data.get("analysis_result", {}),
            "recommendations": response_data.get("recommendations", []),
            "next_step_suggestion": response_data.get("next_step_suggestion", ""),
            "execution_time_ms": response_data.get("execution_time_ms", 0),
            "raw_response": response_data
        }
        
        return step_result
    
    def _parse_project_status_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """解析项目状态响应"""
        
        project_status = {
            "id": response_data.get("project_id", ""),
            "name": response_data.get("project_name", ""),
            "status": response_data.get("project_status", "进行中"),
            "current_phase": response_data.get("current_phase", ""),
            "progress": response_data.get("progress", 0),
            "completed_steps": response_data.get("completed_steps", []),
            "current_step": response_data.get("current_step", {}),
            "next_steps": response_data.get("next_steps", []),
            "issues": response_data.get("issues", []),
            "last_updated": response_data.get("last_updated", datetime.now().isoformat()),
            "raw_response": response_data
        }
        
        return project_status
    
    def recommend_models_for_step(self, step_type: StepType) -> Dict[str, Any]:
        """为步骤类型推荐模型"""
        
        model_config = self.step_to_model_mapping.get(step_type, {})
        
        return {
            "step_type": step_type.value,
            "recommended_primary_model": model_config.get("primary", "白光思维"),
            "recommended_secondary_models": model_config.get("secondary", []),
            "reasoning": model_config.get("reasoning", "标准分析模型"),
            "combination_strategy": "顺序执行" if model_config.get("secondary") else "单一模型"
        }


# 简化版本适配器（用于测试和快速集成）
class SimpleDragonClawAdapter:
    """简化版龙爪OS适配器（不依赖技能调用层）"""
    
    def __init__(self):
        self.protocol_version = "LongXin-to-LongZhao-Protocol-v1"
        self.active_projects = {}
        logger.info("简化版龙爪OS适配器初始化")
    
    def start_project(self, scene_type, requirements, **kwargs):
        """简化项目启动（模拟响应）"""
        
        project_id = str(uuid.uuid4())
        
        # 确定项目类型
        project_type = "自定义项目"
        if "文化" in requirements:
            project_type = "企业文化项目"
        elif "五行" in requirements or "人格" in requirements:
            project_type = "五行人格项目"
        elif "工作流" in requirements:
            project_type = "工作流项目"
        
        # 创建模拟项目
        project_info = {
            "id": project_id,
            "name": f"{project_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": project_type,
            "currentPhase": "启动阶段",
            "progress": 0,
            "estimatedCompletion": "7天后",
            "workflow_steps": [
                {"id": 1, "type": "数据收集", "description": "收集项目相关信息"},
                {"id": 2, "type": "问题分析", "description": "分析核心问题和挑战"},
                {"id": 3, "type": "创新方案", "description": "设计解决方案"},
                {"id": 4, "type": "价值评估", "description": "评估方案价值和可行性"},
                {"id": 5, "type": "决策制定", "description": "制定最终决策"}
            ]
        }
        
        # 存储项目状态
        self.active_projects[project_id] = {
            "info": project_info,
            "current_step": 0,
            "steps_completed": [],
            "created_at": datetime.now()
        }
        
        return {
            "success": True,
            "project_id": project_id,
            "project_info": project_info,
            "execution_time": 0.3,
            "metadata": {
                "protocol_version": self.protocol_version,
                "scene_type": scene_type,
                "project_type": project_type,
                "is_simulation": True
            }
        }
    
    def execute_workflow_step(self, project_id, step_type, step_data, **kwargs):
        """简化步骤执行（模拟响应）"""
        
        if project_id not in self.active_projects:
            return {
                "success": False,
                "error": f"项目不存在：{project_id}",
                "execution_time": 0.1
            }
        
        project = self.active_projects[project_id]
        
        # 模拟步骤执行结果
        step_result = {
            "step_number": project["current_step"] + 1,
            "step_type": step_type.value if hasattr(step_type, 'value') else step_type,
            "status": "完成",
            "output": {
                "analysis": f"对{step_data.get('topic', '数据')}的分析完成",
                "key_findings": ["发现1", "发现2", "发现3"],
                "conclusions": ["结论1", "结论2"]
            },
            "recommendations": ["建议1", "建议2", "建议3"],
            "next_step_suggestion": "继续执行下一步"
        }
        
        # 更新项目状态
        project["current_step"] += 1
        project["steps_completed"].append(step_result)
        project["info"]["progress"] = min(100, (project["current_step"] / 5) * 100)
        
        return {
            "success": True,
            "step_result": step_result,
            "execution_time": 0.5,
            "metadata": {
                "protocol_version": self.protocol_version,
                "project_id": project_id,
                "is_simulation": True
            }
        }
    
    def get_project_status(self, project_id):
        """简化项目状态查询"""
        
        if project_id not in self.active_projects:
            return {
                "success": False,
                "error": f"项目不存在：{project_id}",
                "execution_time": 0.1
            }
        
        project = self.active_projects[project_id]
        
        return {
            "success": True,
            "status": {
                "id": project_id,
                "name": project["info"]["name"],
                "status": "进行中",
                "current_phase": "执行阶段",
                "progress": project["info"]["progress"],
                "completed_steps": project["steps_completed"],
                "current_step": project["current_step"],
                "next_steps": ["继续执行剩余步骤"],
                "last_updated": datetime.now().isoformat()
            },
            "execution_time": 0.1
        }


if __name__ == "__main__":
    # 测试适配器
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("测试龙爪OS适配器...")
    
    # 使用简化版适配器进行测试
    adapter = SimpleDragonClawAdapter()
    
    # 测试项目启动
    start_result = adapter.start_project(
        scene_type="S7",
        requirements="启动一个企业文化建设项目"
    )
    
    print(f"项目启动结果：{start_result['success']}")
    if start_result['success']:
        project_id = start_result['project_id']
        print(f"项目ID：{project_id}")
        print(f"项目名称：{start_result['project_info']['name']}")
        
        # 测试步骤执行
        step_result = adapter.execute_workflow_step(
            project_id=project_id,
            step_type=StepType.DATA_COLLECTION,
            step_data={"topic": "企业文化现状"}
        )
        
        print(f"步骤执行结果：{step_result['success']}")
        
        # 测试状态查询
        status_result = adapter.get_project_status(project_id)
        print(f"状态查询结果：{status_result['success']}")
        if status_result['success']:
            print(f"项目进度：{status_result['status']['progress']}%")