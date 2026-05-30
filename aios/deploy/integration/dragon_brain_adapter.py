# 龙脑OS适配器 - 思维模型与方法论引擎集成
"""
龙脑OS（Dragon Brain OS）适配器
提供统一的接口调用龙脑OS知识库智能体，支持：
1. 场景分析路由
2. 知识库智能匹配
3. 思维模型调用
4. 结果整合和格式化

基于龙心OS-龙脑OS调用协议 v1.0（integration.md）
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

# 导入技能调用层
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from skills.skill_invoker import SkillInvoker
from skills.parameter_handler import ParameterHandler
from skills.error_handler import CompositeErrorHandler

logger = logging.getLogger(__name__)


class DragonBrainAdapter:
    """龙脑OS适配器"""
    
    def __init__(self, skill_invoker: Optional[SkillInvoker] = None):
        """
        初始化龙脑OS适配器
        
        Args:
            skill_invoker: 技能调用器实例，如果为None则创建新实例
        """
        self.skill_invoker = skill_invoker or SkillInvoker()
        self.param_handler = ParameterHandler()
        self.error_handler = CompositeErrorHandler()
        
        # 龙脑OS技能名称（根据WorkBuddy技能目录）
        self.skill_name = "龙脑OS"
        
        # 调用协议版本
        self.protocol_version = "v1.0"
        
        # 知识库映射表（场景类型 -> 推荐知识库）
        self.knowledge_base_mapping = {
            "S0": "思维模型库",  # 紧急救援
            "S1": "思维模型库",  # 信息查询
            "S2": "思维模型库",  # 深度理解
            "S3": "思维模型库",  # 创意创新
            "S4": "思维模型库",  # 分析决策
            "S5": "思维模型库",  # 重大决策（多知识库组合）
            "S6": "思维模型库",  # 任务执行
            "S7": "麦肯锡思考框架",  # 系统规划
            "S8": "五行人格心理学OS",  # 修行文化
            "S9": "思维模型库",  # 进化升级
        }
        
        logger.info(f"龙脑OS适配器初始化完成，技能名称：{self.skill_name}")
    
    def invoke_knowledge_base(self, 
                             scene_type: str,
                             user_need: str,
                             target_knowledge_base: Optional[str] = None,
                             specific_model: Optional[str] = None,
                             combination_needed: bool = False,
                             depth_level: str = "standard",
                             context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        调用龙脑OS知识库智能体
        
        Args:
            scene_type: 场景类型（S0-S9）
            user_need: 用户需求描述
            target_knowledge_base: 目标知识库（可选，如未指定则智能路由）
            specific_model: 具体模型（可选，如SWOT、波特五力等）
            combination_needed: 是否需要组合多个知识库（默认False）
            depth_level: 分析深度（"quick"/"standard"/"deep"）
            context: 上下文信息（对话历史、用户偏好等）
            
        Returns:
            调用结果字典，包含：
            - success: 是否成功
            - result: 分析结果（如果成功）
            - error: 错误信息（如果失败）
            - metadata: 元数据（执行时间、置信度等）
        """
        start_time = datetime.now()
        
        try:
            # 1. 构建调用请求（遵循龙心OS-龙脑OS调用协议）
            request = self._build_request(
                scene_type=scene_type,
                user_need=user_need,
                target_knowledge_base=target_knowledge_base,
                specific_model=specific_model,
                combination_needed=combination_needed,
                depth_level=depth_level,
                context=context or {}
            )
            
            logger.info(f"调用龙脑OS，场景：{scene_type}，需求：{user_need[:50]}...")
            
            # 2. 调用龙脑OS技能
            # 使用错误处理器包装调用，支持重试和断路器
            result = self.error_handler.execute_with_retry(
                func=self._call_dragon_brain_skill,
                func_args=[request],
                operation_name=f"龙脑OS调用_{scene_type}"
            )
            
            # 3. 验证和解析响应
            if not result.get("success", False):
                error_msg = result.get("error", "未知错误")
                logger.error(f"龙脑OS调用失败：{error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "execution_time": (datetime.now() - start_time).total_seconds()
                }
            
            # 4. 提取和格式化结果
            response_data = result.get("data", {})
            formatted_result = self._parse_response(response_data)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"龙脑OS调用成功，执行时间：{execution_time:.2f}秒")
            
            return {
                "success": True,
                "result": formatted_result,
                "execution_time": execution_time,
                "metadata": {
                    "protocol_version": self.protocol_version,
                    "scene_type": scene_type,
                    "knowledge_base": formatted_result.get("knowledge_base"),
                    "model_used": formatted_result.get("model_used"),
                    "confidence_score": formatted_result.get("confidence_score", 0.8)
                }
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.exception(f"龙脑OS适配器异常：{str(e)}")
            return {
                "success": False,
                "error": f"适配器内部错误：{str(e)}",
                "execution_time": execution_time
            }
    
    def _build_request(self, 
                      scene_type: str,
                      user_need: str,
                      target_knowledge_base: Optional[str],
                      specific_model: Optional[str],
                      combination_needed: bool,
                      depth_level: str,
                      context: Dict[str, Any]) -> Dict[str, Any]:
        """构建龙脑OS调用请求（遵循协议格式）"""
        
        # 如果没有指定目标知识库，根据场景类型推荐
        if not target_knowledge_base:
            target_knowledge_base = self.knowledge_base_mapping.get(scene_type, "思维模型库")
        
        request = {
            "from": "AI_OS_Scheduler",
            "to": "龙脑OS",
            "protocol_version": self.protocol_version,
            "timestamp": datetime.now().isoformat(),
            
            # 必需参数
            "scene_type": scene_type,
            "user_need": user_need,
            
            # 可选参数
            "target_knowledge_base": target_knowledge_base,
            "specific_model": specific_model,
            "combination_needed": combination_needed,
            "depth_level": depth_level,
            
            # 上下文信息
            "context": {
                "conversation_history": context.get("conversation_history", ""),
                "user_preferences": context.get("user_preferences", {}),
                "previous_analysis": context.get("previous_analysis", []),
                "caller": "AI_OS_WorkBuddy_Integration"
            }
        }
        
        # 移除值为None的字段
        request = {k: v for k, v in request.items() if v is not None}
        
        return request
    
    def _call_dragon_brain_skill(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """调用龙脑OS技能（实际技能调用）"""
        
        # 参数验证和转换
        validated_params = self.param_handler.validate_and_convert(
            skill_name=self.skill_name,
            function_name="invoke_knowledge_base",  # 假设的函数名
            parameters=request
        )
        
        # 调用技能
        # 注意：这里假设龙脑OS技能有一个名为"invoke_knowledge_base"的函数
        # 实际函数名可能需要从技能配置中获取
        result = self.skill_invoker.invoke_skill(
            skill_name=self.skill_name,
            function_name="invoke_knowledge_base",
            parameters=validated_params,
            timeout=30  # 龙脑OS调用超时时间（秒）
        )
        
        return result
    
    def _parse_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """解析龙脑OS响应，提取核心结果"""
        
        # 根据协议，响应应该包含以下字段
        # 我们提供默认值以防响应格式不匹配
        
        result = {
            "knowledge_base": response_data.get("knowledge_base", "未知知识库"),
            "model_used": response_data.get("model_used", "未知模型"),
            "analysis_result": response_data.get("analysis_result", {}),
            "recommendations": response_data.get("recommendations", []),
            "next_steps": response_data.get("next_steps", []),
            "related_models": response_data.get("related_models", []),
            "confidence_score": response_data.get("confidence_score", 0.8),
            "raw_response": response_data  # 保留原始响应以便调试
        }
        
        # 如果analysis_result是字符串，尝试解析为JSON
        if isinstance(result["analysis_result"], str):
            try:
                result["analysis_result"] = json.loads(result["analysis_result"])
            except:
                # 保持原样
                pass
        
        return result
    
    def list_available_knowledge_bases(self) -> List[Dict[str, Any]]:
        """获取可用的知识库列表"""
        
        # 这里可以硬编码，也可以从龙脑OS技能动态获取
        knowledge_bases = [
            {
                "name": "思维模型库",
                "description": "100个实战思维模型（6阶段），AI时代超级个体认知武器库",
                "model_count": 100,
                "scenes": ["S0", "S1", "S2", "S3", "S4", "S5", "S6", "S9"],
                "path": "~/.workbuddy/skills/思维模型库/"
            },
            {
                "name": "麦肯锡思考框架",
                "description": "25+西方商业分析工具精华",
                "model_count": 25,
                "scenes": ["S4", "S5", "S7"],
                "path": "~/.workbuddy/skills/麦肯锡思考框架/"
            },
            {
                "name": "五行人格心理学OS",
                "description": "东方人格心理学智能体系统，一心三界五行九层完整体系",
                "model_count": 1,  # 总智能体
                "scenes": ["S2", "S8"],
                "path": "~/.workbuddy/skills/五行人格心理学/"
            }
        ]
        
        return knowledge_bases
    
    def get_scene_recommendation(self, scene_type: str) -> Dict[str, Any]:
        """获取场景推荐的知识库和模型"""
        
        knowledge_base = self.knowledge_base_mapping.get(scene_type, "思维模型库")
        
        # 场景到模型的映射建议
        model_recommendations = {
            "S0": "快速查询",  # 紧急救援
            "S1": "快速查询",  # 信息查询
            "S2": "十项认知指令",  # 深度理解
            "S3": "第一性原理",  # 创意创新
            "S4": "SWOT分析",  # 分析决策
            "S5": "多知识库组合",  # 重大决策
            "S6": "IPO模型",  # 任务执行
            "S7": "麦肯锡7S模型",  # 系统规划
            "S8": "五行总智能体",  # 修行文化
            "S9": "进化升级框架",  # 进化升级
        }
        
        return {
            "scene_type": scene_type,
            "recommended_knowledge_base": knowledge_base,
            "recommended_model": model_recommendations.get(scene_type, "通用分析"),
            "description": f"场景{scene_type}推荐使用{knowledge_base}的{model_recommendations.get(scene_type, '通用分析')}模型"
        }


# 简化版本适配器（用于快速集成）
class SimpleDragonBrainAdapter:
    """简化版龙脑OS适配器（不依赖技能调用层，用于测试和快速集成）"""
    
    def __init__(self):
        self.protocol_version = "v1.0"
        logger.info("简化版龙脑OS适配器初始化")
    
    def invoke_knowledge_base(self, scene_type, user_need, **kwargs):
        """简化调用（模拟龙脑OS响应）"""
        
        # 模拟知识库选择
        knowledge_bases = {
            "S0": "思维模型库", "S1": "思维模型库", "S2": "思维模型库",
            "S3": "思维模型库", "S4": "思维模型库", "S5": "思维模型库",
            "S6": "思维模型库", "S7": "麦肯锡思考框架", "S8": "五行人格心理学OS",
            "S9": "思维模型库"
        }
        
        knowledge_base = knowledge_bases.get(scene_type, "思维模型库")
        
        # 模拟分析结果
        analysis_result = {
            "scene_analysis": f"场景{scene_type}: {user_need}",
            "key_insights": ["模拟洞察1", "模拟洞察2", "模拟洞察3"],
            "recommendations": ["建议1: 采取行动A", "建议2: 考虑选项B", "建议3: 评估风险C"]
        }
        
        return {
            "success": True,
            "result": {
                "knowledge_base": knowledge_base,
                "model_used": "模拟模型",
                "analysis_result": analysis_result,
                "recommendations": analysis_result["recommendations"],
                "confidence_score": 0.85
            },
            "execution_time": 0.5,
            "metadata": {
                "protocol_version": self.protocol_version,
                "scene_type": scene_type,
                "is_simulation": True
            }
        }


if __name__ == "__main__":
    # 测试适配器
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("测试龙脑OS适配器...")
    
    # 使用简化版适配器进行测试
    adapter = SimpleDragonBrainAdapter()
    
    # 测试场景S4（分析决策）
    result = adapter.invoke_knowledge_base(
        scene_type="S4",
        user_need="用SWOT分析一下我的副业项目"
    )
    
    print(f"调用结果：{result['success']}")
    if result['success']:
        print(f"知识库：{result['result']['knowledge_base']}")
        print(f"模型：{result['result']['model_used']}")
        print(f"置信度：{result['result']['confidence_score']}")
        print(f"执行时间：{result['execution_time']}秒")