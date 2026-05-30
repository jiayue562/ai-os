#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI OS 调度引擎 - 进化沉淀模块
自动知行合一和经验沉淀

版本: 1.0.0
开发者: 龙龟神将
用户: 悟空
"""

from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
from datetime import datetime
import json
import re
from .engine_router import SceneType, RouteDecision


class PrecipitationStage(Enum):
    """沉淀阶段枚举"""
    REPRESENTATION_SPACE = "表示空间"  # 阶段1：完整表示对话
    COMPRESSION = "压缩"              # 阶段2：压缩核心洞察
    GENERALIZATION = "泛化"           # 阶段3：泛化为可复用知识


class PrecipitationCard:
    """沉淀卡"""
    
    def __init__(self, card_id: str, title: str, content: Dict, 
                 scene_type: SceneType, recipe_type: str,
                 precipitation_date: datetime, metadata: Optional[Dict] = None):
        """
        初始化沉淀卡
        
        参数:
            card_id: 卡片ID
            title: 标题
            content: 内容字典
            scene_type: 场景类型
            recipe_type: 配方类型
            precipitation_date: 沉淀日期
            metadata: 元数据
        """
        self.card_id = card_id
        self.title = title
        self.content = content
        self.scene_type = scene_type
        self.recipe_type = recipe_type
        self.precipitation_date = precipitation_date
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "card_id": self.card_id,
            "title": self.title,
            "content": self.content,
            "scene_type": self.scene_type.value,
            "recipe_type": self.recipe_type,
            "precipitation_date": self.precipitation_date.isoformat(),
            "metadata": self.metadata,
        }
    
    def to_markdown(self) -> str:
        """转换为Markdown格式（用于存入Obsidian）"""
        # YAML frontmatter
        frontmatter = "---\n"
        frontmatter += f"id: {self.card_id}\n"
        frontmatter += f"title: {self.title}\n"
        frontmatter += f"scene_type: {self.scene_type.value}\n"
        frontmatter += f"recipe_type: {self.recipe_type}\n"
        frontmatter += f"date: {self.precipitation_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        # 添加元数据
        for key, value in self.metadata.items():
            if isinstance(value, (str, int, float, bool)):
                frontmatter += f"{key}: {value}\n"
            else:
                frontmatter += f"{key}: {json.dumps(value, ensure_ascii=False)}\n"
        
        frontmatter += "tags: [沉淀卡, 知行合一]\n"
        frontmatter += "---\n\n"
        
        # 内容部分
        markdown = frontmatter
        
        # 添加内容标题
        markdown += f"# {self.title}\n\n"
        
        # 添加各个部分
        if "representation" in self.content:
            markdown += "## 表示空间（完整对话）\n\n"
            markdown += f"{self.content['representation']}\n\n"
        
        if "compression" in self.content:
            markdown += "## 核心压缩（关键洞察）\n\n"
            if isinstance(self.content['compression'], list):
                for i, item in enumerate(self.content['compression'], 1):
                    markdown += f"{i}. {item}\n"
                markdown += "\n"
            else:
                markdown += f"{self.content['compression']}\n\n"
        
        if "generalization" in self.content:
            markdown += "## 知识泛化（可复用模式）\n\n"
            if isinstance(self.content['generalization'], list):
                for i, item in enumerate(self.content['generalization'], 1):
                    markdown += f"{i}. {item}\n"
                markdown += "\n"
            else:
                markdown += f"{self.content['generalization']}\n\n"
        
        if "system_evolution" in self.content:
            markdown += "## 系统进化建议\n\n"
            markdown += f"{self.content['system_evolution']}\n\n"
        
        if "action_items" in self.content:
            markdown += "## 行动项\n\n"
            if isinstance(self.content['action_items'], list):
                for i, item in enumerate(self.content['action_items'], 1):
                    markdown += f"- [ ] {item}\n"
                markdown += "\n"
        
        # 添加签名
        markdown += "---\n\n"
        markdown += "*沉淀于龙心OS·知行合一引擎*\n"
        markdown += f"*{self.precipitation_date.strftime('%Y年%m月%d日 %H:%M')}*\n"
        
        return markdown
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"沉淀卡[{self.card_id}]: {self.title} ({self.scene_type.value})"


class EvolutionPrecipitator:
    """进化沉淀器（知行合一引擎）"""
    
    def __init__(self, obsidian_path: Optional[str] = None):
        """
        初始化进化沉淀器
        
        参数:
            obsidian_path: Obsidian笔记库路径（可选）
        """
        self.obsidian_path = obsidian_path
        
        # 必须启动知行合一的条件（来自决策树文档）
        self.must_precipitate_conditions = {
            "completed_deep_learning": "完成了深度学习（S2型场景）",
            "completed_innovation_breakthrough": "完成了创新突破（S3型场景）",
            "completed_major_decision": "完成了重大决策（S5型场景）",
            "completed_system_planning": "完成了系统规划（S7型场景）",
            "image_thinking_original_insight": "象思维产生了原象级洞察",
            "exceeded_user_expectation": "对话中产生了超出悟空预期的新认知",
            "system_upgrade": "龙心OS本身的系统升级（S9型场景）",
            "cultural_practice": "修行/文化/哲学深度探索（S8型场景）",
        }
        
        # 可选启动条件
        self.optional_precipitate_conditions = {
            "medium_decision_completed": "中等决策完成后",
            "complex_execution_completed": "较复杂的执行任务完成后",
            "user_requested_summary": "悟空主动说'总结一下''这次有什么收获'",
        }
        
        # 不启动条件
        self.no_precipitate_conditions = {
            "simple_qa": "简单问答",
            "direct_small_task": "直接执行的明确小任务（高效助理模式）",
            "casual_chat": "闲聊性质的对话",
            "shallow_info_query": "S1信息查询（浅层）",
        }
        
        # 沉淀卡计数器
        self.card_counter = 0
    
    def should_precipitate(self, route_decision: RouteDecision, 
                          dialogue_history: List[Dict],
                          user_feedback: Optional[str] = None,
                          context: Optional[Dict] = None) -> Tuple[bool, str, List[str]]:
        """
        判断是否需要启动知行合一沉淀
        
        参数:
            route_decision: 路由决策
            dialogue_history: 对话历史
            user_feedback: 用户反馈（可选）
            context: 上下文信息（可选）
            
        返回:
            (should_precipitate, reason, triggered_conditions): 
                是否需要沉淀、原因描述、触发的条件列表
        """
        if context is None:
            context = {}
        
        triggered_conditions = []
        
        # 检查必须启动的条件
        must_conditions = self._check_must_conditions(route_decision, dialogue_history, context)
        triggered_conditions.extend(must_conditions)
        
        if must_conditions:
            reason = "必须启动知行合一：" + "，".join(must_conditions)
            return True, reason, triggered_conditions
        
        # 检查可选启动条件
        optional_conditions = self._check_optional_conditions(route_decision, dialogue_history, user_feedback, context)
        triggered_conditions.extend(optional_conditions)
        
        if optional_conditions:
            # 可选条件：至少满足2个，或者用户明确要求
            if len(optional_conditions) >= 2 or self._user_requested_summary(user_feedback):
                reason = "可选条件满足，启动知行合一：" + "，".join(optional_conditions)
                return True, reason, triggered_conditions
        
        # 检查不启动条件
        no_conditions = self._check_no_conditions(route_decision, dialogue_history, context)
        
        if no_conditions:
            reason = "不满足沉淀条件：" + "，".join(no_conditions)
            return False, reason, []
        
        # 默认不启动
        reason = "未触发沉淀条件"
        return False, reason, []
    
    def _check_must_conditions(self, route_decision: RouteDecision, 
                              dialogue_history: List[Dict], 
                              context: Dict) -> List[str]:
        """检查必须启动的条件"""
        triggered = []
        
        # 条件1: 完成了深度学习（S2型场景）
        if route_decision.scene_type == SceneType.S2_DEEP_LEARNING:
            triggered.append(self.must_precipitate_conditions["completed_deep_learning"])
        
        # 条件2: 完成了创新突破（S3型场景）
        elif route_decision.scene_type == SceneType.S3_INNOVATION_BREAKTHROUGH:
            triggered.append(self.must_precipitate_conditions["completed_innovation_breakthrough"])
        
        # 条件3: 完成了重大决策（S5型场景）
        elif route_decision.scene_type == SceneType.S5_MAJOR_DECISION:
            triggered.append(self.must_precipitate_conditions["completed_major_decision"])
        
        # 条件4: 完成了系统规划（S7型场景）
        elif route_decision.scene_type == SceneType.S7_SYSTEM_PLANNING:
            triggered.append(self.must_precipitate_conditions["completed_system_planning"])
        
        # 条件5: 系统升级（S9型场景）
        elif route_decision.scene_type == SceneType.S9_SYSTEM_EVOLUTION:
            triggered.append(self.must_precipitate_conditions["system_upgrade"])
        
        # 条件6: 文化修行（S8型场景）
        elif route_decision.scene_type == SceneType.S8_CULTURAL_PRACTICE:
            triggered.append(self.must_precipitate_conditions["cultural_practice"])
        
        # 条件7: 象思维产生了原象级洞察
        # 需要从对话历史中检测（简化实现：检查是否包含"象思维"和"洞察"关键词）
        if self._contains_original_insight(dialogue_history):
            triggered.append(self.must_precipitate_conditions["image_thinking_original_insight"])
        
        # 条件8: 超出用户预期的新认知
        if self._exceeded_user_expectation(dialogue_history, context):
            triggered.append(self.must_precipitate_conditions["exceeded_user_expectation"])
        
        return triggered
    
    def _check_optional_conditions(self, route_decision: RouteDecision, 
                                  dialogue_history: List[Dict],
                                  user_feedback: Optional[str],
                                  context: Dict) -> List[str]:
        """检查可选启动条件"""
        triggered = []
        
        # 条件1: 中等决策完成后
        if route_decision.scene_type == SceneType.S4_ANALYSIS_DECISION:
            # 检查是否是中等复杂度
            if len(dialogue_history) >= 3:  # 简化判断
                triggered.append(self.optional_precipitate_conditions["medium_decision_completed"])
        
        # 条件2: 较复杂的执行任务完成后
        if route_decision.scene_type == SceneType.S6_TASK_EXECUTION:
            # 检查任务复杂度
            if self._is_complex_task(dialogue_history):
                triggered.append(self.optional_precipitate_conditions["complex_execution_completed"])
        
        # 条件3: 用户主动要求总结
        if self._user_requested_summary(user_feedback):
            triggered.append(self.optional_precipitate_conditions["user_requested_summary"])
        
        return triggered
    
    def _check_no_conditions(self, route_decision: RouteDecision, 
                            dialogue_history: List[Dict], 
                            context: Dict) -> List[str]:
        """检查不启动条件"""
        triggered = []
        
        # 条件1: 简单问答
        if route_decision.scene_type == SceneType.S0_SIMPLE_QA:
            triggered.append(self.no_precipitate_conditions["simple_qa"])
        
        # 条件2: 直接执行的明确小任务
        elif (route_decision.scene_type == SceneType.S6_TASK_EXECUTION and 
              route_decision.recipe_type in ["E型", "E型·高效助理"]):
            triggered.append(self.no_precipitate_conditions["direct_small_task"])
        
        # 条件3: 闲聊性质的对话
        if self._is_casual_chat(dialogue_history):
            triggered.append(self.no_precipitate_conditions["casual_chat"])
        
        # 条件4: 浅层信息查询
        elif route_decision.scene_type == SceneType.S1_INFO_QUERY:
            triggered.append(self.no_precipitate_conditions["shallow_info_query"])
        
        return triggered
    
    def _contains_original_insight(self, dialogue_history: List[Dict]) -> bool:
        """检查是否包含原象级洞察"""
        # 简化实现：检查是否包含"象思维"和"洞察"相关关键词
        insight_keywords = ["原象", "洞察", "顿悟", "突破", "本质", "核心", "根本"]
        image_thinking_keywords = ["象思维", "🐉", "整体感知", "悬置已知"]
        
        for entry in dialogue_history:
            content = entry.get('content', '').lower()
            if any(keyword in content for keyword in image_thinking_keywords):
                if any(keyword in content for keyword in insight_keywords):
                    return True
        
        return False
    
    def _exceeded_user_expectation(self, dialogue_history: List[Dict], context: Dict) -> bool:
        """检查是否超出用户预期"""
        # 简化实现：检查用户是否表达惊喜或肯定
        positive_feedback_keywords = ["惊喜", "超出预期", "没想到", "太好了", "优秀", "厉害", "赞"]
        
        for entry in dialogue_history:
            if entry.get('role') == 'user':
                content = entry.get('content', '').lower()
                if any(keyword in content for keyword in positive_feedback_keywords):
                    return True
        
        return False
    
    def _is_complex_task(self, dialogue_history: List[Dict]) -> bool:
        """判断是否是复杂任务"""
        # 简化实现：基于对话长度和内容
        if len(dialogue_history) >= 5:
            return True
        
        # 检查是否包含复杂任务关键词
        complexity_keywords = ["复杂", "困难", "挑战", "多步骤", "多任务", "协调", "管理"]
        for entry in dialogue_history:
            content = entry.get('content', '').lower()
            if any(keyword in content for keyword in complexity_keywords):
                return True
        
        return False
    
    def _user_requested_summary(self, user_feedback: Optional[str]) -> bool:
        """检查用户是否要求总结"""
        if not user_feedback:
            return False
        
        summary_keywords = ["总结", "收获", "学到了什么", "这次有什么", "沉淀", "记录"]
        return any(keyword in user_feedback.lower() for keyword in summary_keywords)
    
    def _is_casual_chat(self, dialogue_history: List[Dict]) -> bool:
        """判断是否是闲聊"""
        if len(dialogue_history) < 2:
            return True
        
        # 检查是否包含闲聊关键词
        casual_keywords = ["你好", "在吗", "谢谢", "再见", "拜拜", "哈哈", "呵呵"]
        for entry in dialogue_history:
            content = entry.get('content', '').lower()
            if any(keyword in content for keyword in casual_keywords):
                return True
        
        return False
    
    def precipitate(self, route_decision: RouteDecision, 
                   dialogue_history: List[Dict],
                   final_result: Any,
                   context: Optional[Dict] = None) -> PrecipitationCard:
        """
        执行知行合一沉淀过程
        
        参数:
            route_decision: 路由决策
            dialogue_history: 对话历史
            final_result: 最终结果
            context: 上下文信息
            
        返回:
            PrecipitationCard: 沉淀卡
        """
        if context is None:
            context = {}
        
        # 阶段1: 表示空间（完整表示对话）
        representation = self._create_representation_space(dialogue_history, context)
        
        # 阶段2: 压缩（提取核心洞察）
        compression = self._compress_insights(representation, final_result, context)
        
        # 阶段3: 泛化（生成可复用知识）
        generalization = self._generalize_knowledge(compression, route_decision, context)
        
        # 系统进化建议
        system_evolution = self._generate_system_evolution(route_decision, compression, context)
        
        # 行动项
        action_items = self._generate_action_items(compression, context)
        
        # 生成沉淀卡
        card_id = self._generate_card_id()
        title = self._generate_card_title(route_decision, compression)
        
        content = {
            "representation": representation,
            "compression": compression,
            "generalization": generalization,
            "system_evolution": system_evolution,
            "action_items": action_items,
        }
        
        card = PrecipitationCard(
            card_id=card_id,
            title=title,
            content=content,
            scene_type=route_decision.scene_type,
            recipe_type=route_decision.recipe_type.value,
            precipitation_date=datetime.now(),
            metadata={
                "dialogue_turns": len(dialogue_history),
                "main_engine": route_decision.main_engine.value,
                "auxiliary_engines": [eng.value for eng in route_decision.auxiliary_engines],
                "requires_declaration": route_decision.requires_declaration,
            }
        )
        
        # 保存到Obsidian（如果配置了路径）
        if self.obsidian_path:
            self._save_to_obsidian(card)
        
        return card
    
    def _create_representation_space(self, dialogue_history: List[Dict], 
                                    context: Dict) -> str:
        """创建表示空间（完整对话记录）"""
        representation = "## 完整对话记录\n\n"
        
        for i, entry in enumerate(dialogue_history, 1):
            role = entry.get('role', 'unknown')
            content = entry.get('content', '')
            timestamp = entry.get('timestamp', '')
            
            representation += f"**{i}. {role}**"
            if timestamp:
                representation += f" ({timestamp})"
            representation += ":\n"
            
            # 格式化内容
            formatted_content = content.replace('\n', '\n  ')
            representation += f"  {formatted_content}\n\n"
        
        return representation
    
    def _compress_insights(self, representation: str, final_result: Any, 
                          context: Dict) -> List[str]:
        """压缩核心洞察"""
        insights = []
        
        # 简化实现：从表示空间中提取关键信息
        # 实际应该使用更复杂的NLP技术
        
        # 1. 提取用户的核心问题
        user_questions = self._extract_user_questions(representation)
        if user_questions:
            insights.append(f"用户核心问题: {user_questions[0]}")
        
        # 2. 提取关键结论
        if isinstance(final_result, str):
            # 尝试提取结论句
            conclusion_sentences = self._extract_conclusion_sentences(final_result)
            if conclusion_sentences:
                insights.append(f"关键结论: {conclusion_sentences[0]}")
        
        # 3. 提取重要决策或建议
        decision_keywords = ["决定", "选择", "建议", "推荐", "方案", "策略"]
        for keyword in decision_keywords:
            if keyword in representation:
                # 提取包含关键词的句子
                sentences = re.findall(r'[^。！？]*' + keyword + r'[^。！？]*[。！？]', representation)
                if sentences:
                    insights.append(f"重要决策: {sentences[0]}")
                    break
        
        # 4. 提取创新点或突破
        innovation_keywords = ["创新", "突破", "新方法", "新思路", "原创", "创造"]
        for keyword in innovation_keywords:
            if keyword in representation:
                sentences = re.findall(r'[^。！？]*' + keyword + r'[^。！？]*[。！？]', representation)
                if sentences:
                    insights.append(f"创新突破: {sentences[0]}")
                    break
        
        # 如果没有提取到足够洞察，添加默认洞察
        if len(insights) < 2:
            insights.append("本次对话完成了知识传递或问题解决")
            insights.append("用户需求得到满足，系统功能正常")
        
        return insights
    
    def _generalize_knowledge(self, compression: List[str], 
                             route_decision: RouteDecision, 
                             context: Dict) -> List[str]:
        """泛化为可复用知识"""
        generalizations = []
        
        # 基于场景类型生成通用知识
        scene_type = route_decision.scene_type
        
        if scene_type == SceneType.S2_DEEP_LEARNING:
            generalizations.append("深度学习模式：当用户需要深入理解复杂概念时，应采用知识学习引擎+象思维的组合")
            generalizations.append("深度学习的关键是溯源、融合和启发，需要完整的十项认知指令")
        
        elif scene_type == SceneType.S3_INNOVATION_BREAKTHROUGH:
            generalizations.append("创新突破模式：对于0→1的原创需求，象思维引擎应主导，配合绿光发散和蓝光验证")
            generalizations.append("创新需要悬置已知、整体感知，从原象层面寻找突破点")
        
        elif scene_type == SceneType.S4_ANALYSIS_DECISION:
            generalizations.append("分析决策模式：多选项权衡时，五色光思维引擎能提供全面分析框架")
            generalizations.append("决策分析应遵循白光事实→绿光发散→黄光价值→蓝光风险→红光执行的完整序列")
        
        elif scene_type == SceneType.S5_MAJOR_DECISION:
            generalizations.append("重大决策模式：战略级决策需要全系统启动，整合所有引擎的智慧")
            generalizations.append("重大决策应考虑长期影响、系统联动和风险缓冲")
        
        elif scene_type == SceneType.S7_SYSTEM_PLANNING:
            generalizations.append("系统规划模式：复杂项目规划需要人机协同明确分工，五色光评估方案")
            generalizations.append("系统规划应明确目标、资源、时间线和关键里程碑")
        
        # 从压缩洞察中提取通用模式
        for insight in compression:
            if "模式" in insight or "方法" in insight or "策略" in insight:
                generalizations.append(f"可复用模式: {insight}")
        
        # 添加默认泛化知识
        if not generalizations:
            generalizations.append("本次对话展示了有效的AI-人类协作模式")
            generalizations.append("根据场景类型选择合适的引擎组合能提高问题解决效率")
        
        return generalizations
    
    def _generate_system_evolution(self, route_decision: RouteDecision, 
                                  compression: List[str], 
                                  context: Dict) -> str:
        """生成系统进化建议"""
        suggestions = []
        
        # 基于对话效果生成改进建议
        # 简化实现：根据场景类型生成建议
        
        if route_decision.scene_type == SceneType.S2_DEEP_LEARNING:
            suggestions.append("优化知识学习引擎的溯源算法，提高概念关联度")
        
        elif route_decision.scene_type == SceneType.S3_INNOVATION_BREAKTHROUGH:
            suggestions.append("增强象思维引擎的跨领域联想能力")
            suggestions.append("添加创新评估指标，量化创新突破程度")
        
        elif route_decision.scene_type == SceneType.S4_ANALYSIS_DECISION:
            suggestions.append("丰富五色光思维的颜色维度，添加更多分析视角")
        
        elif route_decision.scene_type == SceneType.S9_SYSTEM_EVOLUTION:
            suggestions.append("根据本次沉淀优化调度器决策树")
            suggestions.append("更新技能库配置，提高调用效率")
        
        # 通用建议
        suggestions.append("持续收集用户反馈，优化对话体验")
        suggestions.append("定期回顾沉淀卡，提炼系统改进方向")
        
        return "\n".join(suggestions)
    
    def _generate_action_items(self, compression: List[str], context: Dict) -> List[str]:
        """生成行动项"""
        actions = []
        
        # 从压缩洞察中提取行动项
        for insight in compression:
            if "需要" in insight or "应该" in insight or "建议" in insight:
                # 提取行动项
                action_match = re.search(r'[需要|应该|建议]([^。！？]+)', insight)
                if action_match:
                    action = action_match.group(1).strip()
                    if action and len(action) > 5:
                        actions.append(action)
        
        # 默认行动项
        if not actions:
            actions.append("回顾本次对话，提炼可复用的协作模式")
            actions.append("将核心洞察应用到相关场景中")
        
        return actions
    
    def _generate_card_id(self) -> str:
        """生成沉淀卡ID"""
        self.card_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        return f"PRECIPITATION_{timestamp}_{self.card_counter:04d}"
    
    def _generate_card_title(self, route_decision: RouteDecision, 
                            compression: List[str]) -> str:
        """生成沉淀卡标题"""
        scene_name = route_decision.scene_type.value.replace(" ", "")
        
        # 从压缩洞察中提取关键词
        keywords = []
        for insight in compression[:2]:  # 取前两个洞察
            # 提取名词或关键短语
            words = re.findall(r'[\u4e00-\u9fa5]{2,4}', insight)
            if words:
                keywords.extend(words[:2])
        
        if keywords:
            unique_keywords = list(dict.fromkeys(keywords))[:3]  # 去重并取前3个
            keyword_str = "·".join(unique_keywords)
            return f"{scene_name}沉淀卡：{keyword_str}"
        else:
            return f"{scene_name}沉淀卡：知识沉淀"
    
    def _extract_user_questions(self, representation: str) -> List[str]:
        """提取用户问题"""
        # 简化实现：提取包含"？"或"?"的句子
        questions = re.findall(r'[^。！？]*[？?][^。！？]*[。！？]', representation)
        
        # 过滤掉AI的回答（包含"AI"或"assistant"的句子）
        user_questions = []
        for q in questions:
            if not any(keyword in q.lower() for keyword in ["ai", "assistant", "系统", "引擎"]):
                user_questions.append(q.strip())
        
        return user_questions[:3]  # 返回前3个问题
    
    def _extract_conclusion_sentences(self, text: str) -> List[str]:
        """提取结论句"""
        # 结论句通常包含以下关键词
        conclusion_keywords = ["因此", "所以", "总之", "综上所述", "结论", "建议", "推荐"]
        
        sentences = re.split(r'[。！？]', text)
        conclusion_sentences = []
        
        for sentence in sentences:
            if any(keyword in sentence for keyword in conclusion_keywords):
                conclusion_sentences.append(sentence.strip())
        
        # 如果没有找到结论句，取最后几句
        if not conclusion_sentences and sentences:
            conclusion_sentences = [sentences[-1].strip()] if sentences[-1].strip() else []
        
        return conclusion_sentences
    
    def _save_to_obsidian(self, card: PrecipitationCard) -> bool:
        """保存沉淀卡到Obsidian"""
        if not self.obsidian_path:
            return False
        
        try:
            import os
            
            # 创建目录（如果不存在）
            precipitations_dir = os.path.join(self.obsidian_path, "沉淀卡")
            os.makedirs(precipitations_dir, exist_ok=True)
            
            # 生成文件名
            filename = f"{card.card_id}.md"
            filepath = os.path.join(precipitations_dir, filename)
            
            # 写入文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(card.to_markdown())
            
            return True
        except Exception as e:
            print(f"保存到Obsidian失败: {e}")
            return False


# 测试函数
def test_evolution_precipitator():
    """测试进化沉淀器"""
    from .engine_router import RouteDecision, EngineType, RecipeType
    
    # 创建测试路由决策
    test_decision = RouteDecision(
        scene_type=SceneType.S2_DEEP_LEARNING,
        main_engine=EngineType.KNOWLEDGE_LEARNING,
        auxiliary_engines=[EngineType.IMAGE_THINKING],
        tail_engine=EngineType.ZHI_XING_HE_YI,
        recipe_type=RecipeType.C_STANDARD,
        requires_declaration=True,
        declaration_text="「📚 知识学习引擎启动」",
    )
    
    # 创建测试对话历史
    dialogue_history = [
        {"role": "user", "content": "帮我深度学习这篇文章：AI OS的架构设计", "timestamp": "10:00"},
        {"role": "assistant", "content": "好的，我来深度学习这篇文章。首先分析核心概念...", "timestamp": "10:01"},
        {"role": "assistant", "content": "通过象思维，我获得了原象级洞察：AI OS应该像人脑一样分层处理", "timestamp": "10:05"},
        {"role": "user", "content": "这个洞察太棒了！超出了我的预期", "timestamp": "10:06"},
    ]
    
    # 创建测试结果
    final_result = "经过深度学习，我理解了AI OS的四层架构：灵魂层、调度层、执行层、基础设施层。关键洞察是木火共生关系是系统的灵魂。"
    
    print("进化沉淀器测试：")
    print("-" * 80)
    
    # 初始化沉淀器
    precipitator = EvolutionPrecipitator()
    
    # 测试是否应该沉淀
    should_precipitate, reason, conditions = precipitator.should_precipitate(
        test_decision, dialogue_history, "总结一下这次对话", {}
    )
    
    print(f"是否应该沉淀: {should_precipitate}")
    print(f"原因: {reason}")
    print(f"触发条件: {conditions}")
    print()
    
    if should_precipitate:
        # 执行沉淀
        card = precipitator.precipitate(test_decision, dialogue_history, final_result, {})
        
        print(f"生成的沉淀卡:")
        print(f"  ID: {card.card_id}")
        print(f"  标题: {card.title}")
        print(f"  场景: {card.scene_type.value}")
        print(f"  配方: {card.recipe_type}")
        print()
        
        # 打印部分内容
        print("沉淀卡内容预览:")
        markdown = card.to_markdown()
        lines = markdown.split('\n')[:20]  # 前20行
        for line in lines:
            print(line)
        
        print("\n...（内容已截断）")
    
    # 测试其他场景
    print("\n" + "="*80)
    print("测试S1信息查询场景（不应该沉淀）:")
    
    s1_decision = RouteDecision(
        scene_type=SceneType.S1_INFO_QUERY,
        main_engine=EngineType.KNOWLEDGE_LEARNING,
        auxiliary_engines=[],
        tail_engine=None,
        recipe_type=RecipeType.C_SIMPLE,
        requires_declaration=False,
        declaration_text="",
    )
    
    s1_history = [
        {"role": "user", "content": "粘贴复制快捷键是什么", "timestamp": "11:00"},
        {"role": "assistant", "content": "Ctrl+C复制，Ctrl+V粘贴", "timestamp": "11:01"},
    ]
    
    should_precipitate2, reason2, conditions2 = precipitator.should_precipitate(
        s1_decision, s1_history, None, {}
    )
    
    print(f"是否应该沉淀: {should_precipitate2}")
    print(f"原因: {reason2}")
    print()


if __name__ == "__main__":
    test_evolution_precipitator()