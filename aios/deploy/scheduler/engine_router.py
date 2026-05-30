#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI OS 调度引擎 - 引擎路由模块
基于龙心OS引擎调度决策树v2.0实现

版本: 1.0.0
开发者: 龙龟神将
用户: 悟空
"""

from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
from .intent_recognizer import IntentType
from .scene_classifier import SceneType, SceneClassifier


class EngineType(Enum):
    """引擎类型枚举（龙心OS定义）"""
    NONE = "无引擎"                     # S0场景
    KNOWLEDGE_LEARNING = "📚 知识学习"   # 知识学习引擎
    IMAGE_THINKING = "🐉 象思维"        # 象思维引擎
    FIVE_COLOR_THINKING = "🌈 五色光"    # 五色光思维引擎
    HUMAN_AI_COLLABORATION = "🤝 人机协同"  # 人机协同引擎
    ZHI_XING_HE_YI = "🔄 知行合一"       # 知行合一引擎
    FULL_SYSTEM = "🐉 全系统"           # A型全系统启动


class RecipeType(Enum):
    """配方类型枚举（龙心OS定义）"""
    NONE = "无配方"
    C_SIMPLE = "C精简"           # S1信息查询
    C_STANDARD = "C标准"         # S2深度学习
    B_INNOVATION = "B型"         # S3纯创新
    C_B_MIXED = "C+B混合"        # S3创新+学习
    D_SIMPLE = "D精简"           # S4小决策
    D_STANDARD = "D标准"         # S4中等决策
    A_FULL_SYSTEM = "A型全系统"  # S5重大决策
    E_EFFICIENT = "E型"          # S6高效助理
    E_CREATIVE_PARTNER = "E型·共创伙伴"  # S6共创伙伴
    E_CREATIVE_TUTOR = "E型·共创导师"    # S6共创导师
    E_D_MIXED = "E+D混合"        # S7系统规划
    C_B_CULTURE = "C+B文化版"    # S8文化修行
    EVOLUTION_SPECIAL = "进化专项"  # S9系统升级


class RouteDecision:
    """路由决策结果"""
    
    def __init__(self, scene_type: SceneType, 
                 main_engine: EngineType,
                 auxiliary_engines: List[EngineType],
                 tail_engine: Optional[EngineType],
                 recipe_type: RecipeType,
                 requires_declaration: bool,
                 declaration_text: str):
        """
        初始化路由决策
        
        参数:
            scene_type: 场景类型 (S0-S9)
            main_engine: 主引擎
            auxiliary_engines: 辅助引擎列表
            tail_engine: 收尾引擎（知行合一）
            recipe_type: 配方类型
            requires_declaration: 是否需要声明
            declaration_text: 声明文本
        """
        self.scene_type = scene_type
        self.main_engine = main_engine
        self.auxiliary_engines = auxiliary_engines
        self.tail_engine = tail_engine
        self.recipe_type = recipe_type
        self.requires_declaration = requires_declaration
        self.declaration_text = declaration_text
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "scene_type": self.scene_type.value,
            "main_engine": self.main_engine.value,
            "auxiliary_engines": [engine.value for engine in self.auxiliary_engines],
            "tail_engine": self.tail_engine.value if self.tail_engine else None,
            "recipe_type": self.recipe_type.value,
            "requires_declaration": self.requires_declaration,
            "declaration_text": self.declaration_text,
        }
    
    def __str__(self) -> str:
        """字符串表示"""
        engines = [self.main_engine.value]
        engines.extend([engine.value for engine in self.auxiliary_engines])
        if self.tail_engine:
            engines.append(self.tail_engine.value)
        
        engines_str = " → ".join(engines)
        return f"{self.scene_type.value}: {engines_str} ({self.recipe_type.value})"


class EngineRouter:
    """引擎路由器（基于龙心OS决策树v2.0）"""
    
    def __init__(self):
        self.scene_classifier = SceneClassifier()
        
        # 决策树配置
        self.decision_tree_config = {
            # Gate 0: 是否简单？
            "gate0_simple_keywords": [
                "你好", "在吗", "谢谢", "明白", "确认", "对", "是的", "不是", "否",
                "快捷键", "命令", "操作", "步骤", "怎么用", "如何使用",
            ],
            
            # Gate 2A: 获取/理解信息的深度要求
            "gate2a_depth_keywords": {
                "shallow": ["解释", "查询", "定义", "是什么", "告诉我", "查一下"],
                "medium": ["理解概念", "分析结构", "原理", "机制", "逻辑"],
                "deep": ["提供文章", "深度学习", "深度分析", "透彻理解", "完整学习"],
            },
            
            # Gate 2B: 创造/创新方案的参考案例
            "gate2b_reference_keywords": {
                "none": ["全新", "前所未有", "0→1", "无中生有", "从零开始"],
                "partial": ["在基础上", "优化", "改进", "升级", "增强"],
                "framework": ["框架", "模板", "结构", "模型", "模式"],
            },
            
            # Gate 2C: 分析/决策的影响范围
            "gate2c_impact_keywords": {
                "small": ["日常", "小事", "简单", "快速", "一般"],
                "medium": ["中等", "有一定影响", "重要", "关键", "需要考虑"],
                "major": ["战略", "重大", "长远", "未来", "核心", "转型", "变革"],
                "cultural": ["修行", "文化", "哲学", "心文化", "大圆满", "传统"],
            },
            
            # Gate 2D: 执行/规划任务的分工需求
            "gate2d_division_keywords": [
                "规划", "分工", "协调", "管理", "组织", "团队", "项目", "工作流",
                "系统规划", "项目规划", "任务分工", "工作计划", "时间表",
            ],
            
            # Gate 2E: 直接执行模式的信息掌握度
            "gate2e_knowledge_keywords": {
                "both_know": ["我知道", "我了解", "我熟悉", "我掌握", "我懂"],
                "user_knows": ["我的经验", "我的方法", "我的做法", "我的习惯"],
                "partial_know": ["部分了解", "有些知道", "不太确定", "有点模糊"],
            },
            
            # Gate 2F: 系统进化诊断的需求类型
            "gate2f_evolution_keywords": {
                "skills_update": ["Skills文件", "技能文件", "配置更新", "参数调整"],
                "mechanism_optimization": ["机制", "流程", "算法", "逻辑", "策略"],
                "new_engine": ["新引擎", "新工具", "新功能", "新模块", "新组件"],
            },
        }
        
        # 场景到引擎的默认映射（速查表）
        self.scene_engine_mapping = {
            SceneType.S0_SIMPLE_QA: {
                "main_engine": EngineType.NONE,
                "auxiliary_engines": [],
                "tail_engine": None,
                "recipe_type": RecipeType.NONE,
                "requires_declaration": False,
                "declaration_text": "",
            },
            SceneType.S1_INFO_QUERY: {
                "main_engine": EngineType.KNOWLEDGE_LEARNING,
                "auxiliary_engines": [],
                "tail_engine": None,
                "recipe_type": RecipeType.C_SIMPLE,
                "requires_declaration": False,
                "declaration_text": "",
            },
            SceneType.S2_DEEP_LEARNING: {
                "main_engine": EngineType.KNOWLEDGE_LEARNING,
                "auxiliary_engines": [EngineType.IMAGE_THINKING],
                "tail_engine": EngineType.ZHI_XING_HE_YI,
                "recipe_type": RecipeType.C_STANDARD,
                "requires_declaration": True,
                "declaration_text": "「📚 知识学习引擎启动」",
            },
            SceneType.S3_INNOVATION_BREAKTHROUGH: {
                "main_engine": EngineType.IMAGE_THINKING,
                "auxiliary_engines": [EngineType.FIVE_COLOR_THINKING],
                "tail_engine": EngineType.ZHI_XING_HE_YI,
                "recipe_type": RecipeType.B_INNOVATION,
                "requires_declaration": True,
                "declaration_text": "「🐉 象思维·创新突破模式」",
            },
            SceneType.S4_ANALYSIS_DECISION: {
                "main_engine": EngineType.FIVE_COLOR_THINKING,
                "auxiliary_engines": [],
                "tail_engine": EngineType.ZHI_XING_HE_YI,
                "recipe_type": RecipeType.D_STANDARD,
                "requires_declaration": True,
                "declaration_text": "「🌈 五色光·标准分析模式」",
            },
            SceneType.S5_MAJOR_DECISION: {
                "main_engine": EngineType.FULL_SYSTEM,
                "auxiliary_engines": [EngineType.IMAGE_THINKING, EngineType.KNOWLEDGE_LEARNING, 
                                    EngineType.FIVE_COLOR_THINKING, EngineType.HUMAN_AI_COLLABORATION],
                "tail_engine": EngineType.ZHI_XING_HE_YI,
                "recipe_type": RecipeType.A_FULL_SYSTEM,
                "requires_declaration": True,
                "declaration_text": "「🐉 龙心OS 全系统启动·A型」",
            },
            SceneType.S6_TASK_EXECUTION: {
                "main_engine": EngineType.HUMAN_AI_COLLABORATION,
                "auxiliary_engines": [],
                "tail_engine": None,
                "recipe_type": RecipeType.E_EFFICIENT,
                "requires_declaration": True,
                "declaration_text": "「🤝 人机协同·高效助理模式」",
            },
            SceneType.S7_SYSTEM_PLANNING: {
                "main_engine": EngineType.HUMAN_AI_COLLABORATION,
                "auxiliary_engines": [EngineType.FIVE_COLOR_THINKING],
                "tail_engine": EngineType.ZHI_XING_HE_YI,
                "recipe_type": RecipeType.E_D_MIXED,
                "requires_declaration": True,
                "declaration_text": "「🤝 人机协同·系统规划」",
            },
            SceneType.S8_CULTURAL_PRACTICE: {
                "main_engine": EngineType.IMAGE_THINKING,
                "auxiliary_engines": [EngineType.KNOWLEDGE_LEARNING],
                "tail_engine": EngineType.ZHI_XING_HE_YI,
                "recipe_type": RecipeType.C_B_CULTURE,
                "requires_declaration": True,
                "declaration_text": "「🐉 象思维·文化深度模式」",
            },
            SceneType.S9_SYSTEM_EVOLUTION: {
                "main_engine": EngineType.ZHI_XING_HE_YI,
                "auxiliary_engines": [EngineType.IMAGE_THINKING, EngineType.FIVE_COLOR_THINKING],
                "tail_engine": None,
                "recipe_type": RecipeType.EVOLUTION_SPECIAL,
                "requires_declaration": True,
                "declaration_text": "「🔄 龙心OS 系统进化」",
            },
        }
    
    def route(self, user_input: str, intent_type: IntentType, 
              intensity_score: int, scene_type: SceneType,
              complexity: str, context: Optional[Dict] = None) -> RouteDecision:
        """
        基于决策树进行引擎路由
        
        参数:
            user_input: 用户输入文本
            intent_type: 意图类型
            intensity_score: 意图强度分数(1-10)
            scene_type: 场景分类器返回的场景类型
            complexity: 场景复杂度(simple/medium/complex)
            context: 上下文信息（可选）
            
        返回:
            RouteDecision: 路由决策结果
        """
        # 初始化上下文
        if context is None:
            context = {}
        
        # 预处理输入
        cleaned_input = user_input.lower()
        
        # Gate 0: 是否简单任务？
        if self._is_simple_task(cleaned_input, scene_type):
            return self._create_simple_route()
        
        # 根据意图类型进入不同的Gate
        if intent_type == IntentType.GET_INFO:
            return self._gate2a_get_info(cleaned_input, scene_type, complexity, context)
        elif intent_type == IntentType.DEEP_UNDERSTANDING:
            return self._gate2a_get_info(cleaned_input, scene_type, complexity, context)
        elif intent_type == IntentType.CREATIVE_BREAKTHROUGH:
            return self._gate2b_creative_breakthrough(cleaned_input, scene_type, complexity, context)
        elif intent_type == IntentType.ANALYSIS_DECISION:
            return self._gate2c_analysis_decision(cleaned_input, scene_type, complexity, context)
        elif intent_type == IntentType.TASK_EXECUTION:
            return self._gate2d_task_execution(cleaned_input, scene_type, complexity, context)
        elif intent_type == IntentType.SYSTEM_EVOLUTION:
            return self._gate2f_system_evolution(cleaned_input, scene_type, complexity, context)
        else:
            # 默认回退到场景映射
            return self._get_default_route(scene_type)
    
    def _is_simple_task(self, text: str, scene_type: SceneType) -> bool:
        """Gate 0: 判断是否是简单任务"""
        # S0场景直接认为是简单任务
        if scene_type == SceneType.S0_SIMPLE_QA:
            return True
        
        # 检查简单任务关键词
        simple_keywords = self.decision_tree_config["gate0_simple_keywords"]
        for keyword in simple_keywords:
            if keyword in text:
                return True
        
        # 检查文本长度（很短的文本可能是简单任务）
        if len(text) < 20 and "?" not in text and "？" not in text:
            return True
        
        return False
    
    def _create_simple_route(self) -> RouteDecision:
        """创建简单任务路由（S0）"""
        config = self.scene_engine_mapping[SceneType.S0_SIMPLE_QA]
        return RouteDecision(
            scene_type=SceneType.S0_SIMPLE_QA,
            main_engine=config["main_engine"],
            auxiliary_engines=config["auxiliary_engines"],
            tail_engine=config["tail_engine"],
            recipe_type=config["recipe_type"],
            requires_declaration=config["requires_declaration"],
            declaration_text=config["declaration_text"],
        )
    
    def _gate2a_get_info(self, text: str, scene_type: SceneType, 
                         complexity: str, context: Dict) -> RouteDecision:
        """Gate 2A: 获取/理解信息的路由"""
        # 检查深度要求
        depth = self._assess_depth_requirement(text)
        
        if depth == "shallow":
            # S1信息查询
            return self._get_default_route(SceneType.S1_INFO_QUERY)
        elif depth == "medium":
            # S1-S2边界，轻量知行合一
            route = self._get_default_route(SceneType.S2_DEEP_LEARNING)
            # 调整为轻量版本
            route.auxiliary_engines = []  # 去掉象思维
            route.recipe_type = RecipeType.C_SIMPLE
            route.declaration_text = "「📚 知识学习引擎启动（轻量版）」"
            return route
        else:  # deep
            # S2深度学习，完整配方
            return self._get_default_route(SceneType.S2_DEEP_LEARNING)
    
    def _assess_depth_requirement(self, text: str) -> str:
        """评估深度要求（浅层/中层/深层）"""
        config = self.decision_tree_config["gate2a_depth_keywords"]
        
        deep_count = sum(1 for keyword in config["deep"] if keyword in text)
        medium_count = sum(1 for keyword in config["medium"] if keyword in text)
        shallow_count = sum(1 for keyword in config["shallow"] if keyword in text)
        
        if deep_count > 0:
            return "deep"
        elif medium_count > 0:
            return "medium"
        else:
            return "shallow"
    
    def _gate2b_creative_breakthrough(self, text: str, scene_type: SceneType,
                                     complexity: str, context: Dict) -> RouteDecision:
        """Gate 2B: 创造/创新方案的路由"""
        # 检查参考案例情况
        reference_level = self._assess_reference_level(text)
        
        if reference_level == "none":
            # S3纯创新，象思维主导
            route = self._get_default_route(SceneType.S3_INNOVATION_BREAKTHROUGH)
            route.recipe_type = RecipeType.B_INNOVATION
            return route
        elif reference_level == "partial":
            # S3创新+学习，混合模式
            route = self._get_default_route(SceneType.S3_INNOVATION_BREAKTHROUGH)
            route.auxiliary_engines = [EngineType.KNOWLEDGE_LEARNING, EngineType.FIVE_COLOR_THINKING]
            route.recipe_type = RecipeType.C_B_MIXED
            route.declaration_text = "「🐉 象思维·创新学习混合模式」"
            return route
        else:  # framework
            # S4优化，五色光轻量
            route = self._get_default_route(SceneType.S4_ANALYSIS_DECISION)
            route.auxiliary_engines = []
            route.tail_engine = None  # 可选知行合一
            route.recipe_type = RecipeType.D_SIMPLE
            route.declaration_text = "「🌈 五色光·轻量优化模式」"
            return route
    
    def _assess_reference_level(self, text: str) -> str:
        """评估参考案例水平（无/部分/框架）"""
        config = self.decision_tree_config["gate2b_reference_keywords"]
        
        none_count = sum(1 for keyword in config["none"] if keyword in text)
        partial_count = sum(1 for keyword in config["partial"] if keyword in text)
        framework_count = sum(1 for keyword in config["framework"] if keyword in text)
        
        if none_count > 0:
            return "none"
        elif framework_count > 0:
            return "framework"
        else:
            return "partial"
    
    def _gate2c_analysis_decision(self, text: str, scene_type: SceneType,
                                 complexity: str, context: Dict) -> RouteDecision:
        """Gate 2C: 分析/决策的路由"""
        # 检查影响范围和重要程度
        impact_level = self._assess_impact_level(text)
        
        if impact_level == "small":
            # S4小决策，五色光精简
            route = self._get_default_route(SceneType.S4_ANALYSIS_DECISION)
            route.auxiliary_engines = []
            route.tail_engine = None  # 轻量知行合一
            route.recipe_type = RecipeType.D_SIMPLE
            route.declaration_text = "「🌈 五色光·精简分析模式」"
            return route
        elif impact_level == "medium":
            # S4中等决策，五色光标准
            return self._get_default_route(SceneType.S4_ANALYSIS_DECISION)
        elif impact_level == "cultural":
            # S8文化修行
            return self._get_default_route(SceneType.S8_CULTURAL_PRACTICE)
        else:  # major
            # S5重大决策，全系统
            return self._get_default_route(SceneType.S5_MAJOR_DECISION)
    
    def _assess_impact_level(self, text: str) -> str:
        """评估影响水平（小/中/大/文化）"""
        config = self.decision_tree_config["gate2c_impact_keywords"]
        
        major_count = sum(1 for keyword in config["major"] if keyword in text)
        cultural_count = sum(1 for keyword in config["cultural"] if keyword in text)
        medium_count = sum(1 for keyword in config["medium"] if keyword in text)
        small_count = sum(1 for keyword in config["small"] if keyword in text)
        
        if cultural_count > 0:
            return "cultural"
        elif major_count > 0:
            return "major"
        elif medium_count > 0:
            return "medium"
        else:
            return "small"
    
    def _gate2d_task_execution(self, text: str, scene_type: SceneType,
                              complexity: str, context: Dict) -> RouteDecision:
        """Gate 2D: 执行/规划任务的路由"""
        # 检查是否需要规划分工
        needs_division = self._check_division_need(text)
        
        if not needs_division:
            # 进入Gate 2E: 直接执行模式
            return self._gate2e_direct_execution(text, scene_type, complexity, context)
        else:
            # S7系统规划
            return self._get_default_route(SceneType.S7_SYSTEM_PLANNING)
    
    def _check_division_need(self, text: str) -> bool:
        """检查是否需要规划分工"""
        division_keywords = self.decision_tree_config["gate2d_division_keywords"]
        for keyword in division_keywords:
            if keyword in text:
                return True
        return False
    
    def _gate2e_direct_execution(self, text: str, scene_type: SceneType,
                                complexity: str, context: Dict) -> RouteDecision:
        """Gate 2E: 直接执行模式的路由"""
        # 评估信息掌握度组合
        knowledge_combo = self._assess_knowledge_combo(text, context)
        
        if knowledge_combo == "both_know":
            # S6高效助理模式
            route = self._get_default_route(SceneType.S6_TASK_EXECUTION)
            route.recipe_type = RecipeType.E_EFFICIENT
            route.declaration_text = "「🤝 人机协同·高效助理模式」"
            return route
        elif knowledge_combo == "user_knows":
            # S6共创导师模式
            route = self._get_default_route(SceneType.S6_TASK_EXECUTION)
            route.recipe_type = RecipeType.E_CREATIVE_TUTOR
            route.declaration_text = "「🤝 人机协同·共创导师模式」"
            return route
        else:  # partial_know
            # S6共创伙伴模式
            route = self._get_default_route(SceneType.S6_TASK_EXECUTION)
            route.recipe_type = RecipeType.E_CREATIVE_PARTNER
            route.declaration_text = "「🤝 人机协同·共创伙伴模式」"
            return route
    
    def _assess_knowledge_combo(self, text: str, context: Dict) -> str:
        """评估信息掌握度组合"""
        config = self.decision_tree_config["gate2e_knowledge_keywords"]
        
        both_know_count = sum(1 for keyword in config["both_know"] if keyword in text)
        user_knows_count = sum(1 for keyword in config["user_knows"] if keyword in text)
        
        if both_know_count > 0:
            return "both_know"
        elif user_knows_count > 0:
            return "user_knows"
        else:
            return "partial_know"
    
    def _gate2f_system_evolution(self, text: str, scene_type: SceneType,
                                complexity: str, context: Dict) -> RouteDecision:
        """Gate 2F: 系统进化诊断的路由"""
        # 检查进化需求类型
        evolution_type = self._assess_evolution_type(text)
        
        # S9系统进化
        route = self._get_default_route(SceneType.S9_SYSTEM_EVOLUTION)
        
        if evolution_type == "skills_update":
            route.declaration_text = "「🔄 龙心OS 系统进化·技能更新」"
        elif evolution_type == "mechanism_optimization":
            route.declaration_text = "「🔄 龙心OS 系统进化·机制优化」"
        else:  # new_engine
            route.declaration_text = "「🔄 龙心OS 系统进化·新引擎引入」"
        
        return route
    
    def _assess_evolution_type(self, text: str) -> str:
        """评估进化需求类型"""
        config = self.decision_tree_config["gate2f_evolution_keywords"]
        
        skills_update_count = sum(1 for keyword in config["skills_update"] if keyword in text)
        mechanism_optimization_count = sum(1 for keyword in config["mechanism_optimization"] if keyword in text)
        new_engine_count = sum(1 for keyword in config["new_engine"] if keyword in text)
        
        if skills_update_count > 0:
            return "skills_update"
        elif mechanism_optimization_count > 0:
            return "mechanism_optimization"
        else:
            return "new_engine"
    
    def _get_default_route(self, scene_type: SceneType) -> RouteDecision:
        """获取默认路由配置"""
        config = self.scene_engine_mapping[scene_type]
        return RouteDecision(
            scene_type=scene_type,
            main_engine=config["main_engine"],
            auxiliary_engines=config["auxiliary_engines"],
            tail_engine=config["tail_engine"],
            recipe_type=config["recipe_type"],
            requires_declaration=config["requires_declaration"],
            declaration_text=config["declaration_text"],
        )


# 测试函数
def test_engine_router():
    """测试引擎路由器"""
    from .intent_recognizer import IntentRecognizer
    
    router = EngineRouter()
    intent_recognizer = IntentRecognizer()
    scene_classifier = SceneClassifier()
    
    test_cases = [
        ("粘贴复制快捷键是什么", "S1信息查询", "simple"),
        ("帮我深度学习这篇文章", "S2深度学习", "medium"),
        ("我需要一个全新的产品创意", "S3创新突破", "complex"),
        ("分析一下这个方案的优缺点", "S4分析决策", "medium"),
        ("这个战略决策很重要，需要慎重考虑", "S5重大决策", "complex"),
        ("帮我执行这个任务，我知道怎么做", "S6任务执行", "medium"),
        ("如何进行系统规划和工作分工", "S7系统规划", "complex"),
        ("谈谈修行文化和心文化", "S8修行文化", "medium"),
        ("龙心OS需要升级优化Skills文件", "S9系统进化", "complex"),
        ("你好", "S0极简问答", "simple"),
    ]
    
    print("引擎路由器测试结果：")
    print("-" * 80)
    
    for input_text, expected_scene_desc, expected_complexity in test_cases:
        # 识别意图
        intent, intensity = intent_recognizer.recognize(input_text)
        
        # 分类场景
        scene, complexity = scene_classifier.classify(input_text, intent, intensity)
        
        # 引擎路由
        decision = router.route(input_text, intent, intensity, scene, complexity)
        
        scene_match = "✓" if scene.value == expected_scene_desc else "✗"
        complexity_match = "✓" if complexity == expected_complexity else "✗"
        
        print(f"输入: {input_text}")
        print(f"  意图: {intent.value} (强度: {intensity})")
        print(f"  场景: {scene.value} {scene_match}")
        print(f"  复杂度: {complexity} {complexity_match}")
        print(f"  路由决策: {decision}")
        print(f"  主引擎: {decision.main_engine.value}")
        if decision.auxiliary_engines:
            print(f"  辅助引擎: {[eng.value for eng in decision.auxiliary_engines]}")
        if decision.tail_engine:
            print(f"  收尾引擎: {decision.tail_engine.value}")
        print(f"  配方: {decision.recipe_type.value}")
        print(f"  声明: {decision.declaration_text if decision.requires_declaration else '无需声明'}")
        print()


if __name__ == "__main__":
    test_engine_router()