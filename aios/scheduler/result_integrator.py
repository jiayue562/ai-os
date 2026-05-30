#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI OS 调度引擎 - 结果整合模块
整合多个子智能体的输出结果

版本: 1.0.0
开发者: 龙龟神将
用户: 悟空
"""

from typing import Dict, List, Tuple, Optional, Any, Union
from enum import Enum
import json
import re


class ResultType(Enum):
    """结果类型枚举"""
    TEXT = "文本"
    STRUCTURED = "结构化数据"
    CODE = "代码"
    LIST = "列表"
    TABLE = "表格"
    MIXED = "混合类型"


class IntegrationStrategy(Enum):
    """整合策略枚举"""
    MERGE = "合并"           # 简单合并所有结果
    PRIORITY = "优先级"      # 按优先级选择或合并
    CONFLICT_RESOLUTION = "冲突解决"  # 解决冲突后合并
    STRUCTURED_MERGE = "结构化合并"  # 结构化合并
    SUMMARY = "摘要"         # 生成摘要


class SkillResult:
    """技能执行结果"""
    
    def __init__(self, skill_name: str, result_data: Any, 
                 result_type: ResultType = ResultType.TEXT,
                 confidence: float = 1.0,
                 metadata: Optional[Dict] = None):
        """
        初始化技能结果
        
        参数:
            skill_name: 技能名称
            result_data: 结果数据
            result_type: 结果类型
            confidence: 置信度 (0.0-1.0)
            metadata: 元数据
        """
        self.skill_name = skill_name
        self.result_data = result_data
        self.result_type = result_type
        self.confidence = confidence
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "skill_name": self.skill_name,
            "result_data": self.result_data,
            "result_type": self.result_type.value,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"{self.skill_name}: {str(self.result_data)[:100]}... (置信度: {self.confidence:.2f})"


class IntegratedResult:
    """整合后的结果"""
    
    def __init__(self, integrated_data: Any, 
                 result_type: ResultType = ResultType.TEXT,
                 source_results: List[SkillResult] = None,
                 integration_strategy: IntegrationStrategy = IntegrationStrategy.MERGE,
                 confidence: float = 1.0,
                 metadata: Optional[Dict] = None):
        """
        初始化整合结果
        
        参数:
            integrated_data: 整合后的数据
            result_type: 结果类型
            source_results: 源结果列表
            integration_strategy: 整合策略
            confidence: 整体置信度
            metadata: 元数据
        """
        self.integrated_data = integrated_data
        self.result_type = result_type
        self.source_results = source_results or []
        self.integration_strategy = integration_strategy
        self.confidence = confidence
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "integrated_data": self.integrated_data,
            "result_type": self.result_type.value,
            "source_results": [result.to_dict() for result in self.source_results],
            "integration_strategy": self.integration_strategy.value,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }
    
    def __str__(self) -> str:
        """字符串表示"""
        data_str = str(self.integrated_data)
        if len(data_str) > 200:
            data_str = data_str[:200] + "..."
        return f"整合结果({self.integration_strategy.value}): {data_str}"


class ResultIntegrator:
    """结果整合器"""
    
    def __init__(self):
        # 技能优先级配置（从高到低）
        self.skill_priority = {
            "知识学习": 90,
            "象思维": 85,
            "五色光": 80,
            "人机协同": 75,
            "知行合一": 95,  # 知行合一通常作为收尾，优先级高
            "全系统": 100,   # 全系统最高优先级
        }
        
        # 结果类型处理映射
        self.type_handlers = {
            ResultType.TEXT: self._integrate_text,
            ResultType.STRUCTURED: self._integrate_structured,
            ResultType.CODE: self._integrate_code,
            ResultType.LIST: self._integrate_list,
            ResultType.TABLE: self._integrate_table,
            ResultType.MIXED: self._integrate_mixed,
        }
        
        # 冲突解决规则
        self.conflict_rules = {
            "default": self._resolve_conflict_by_confidence,
            "text": self._resolve_text_conflict,
            "numeric": self._resolve_numeric_conflict,
        }
    
    def integrate(self, skill_results: List[SkillResult], 
                  strategy: IntegrationStrategy = IntegrationStrategy.MERGE,
                  context: Optional[Dict] = None) -> IntegratedResult:
        """
        整合多个技能结果
        
        参数:
            skill_results: 技能结果列表
            strategy: 整合策略
            context: 上下文信息
            
        返回:
            IntegratedResult: 整合后的结果
        """
        if context is None:
            context = {}
        
        # 如果没有结果，返回空结果
        if not skill_results:
            return IntegratedResult(
                integrated_data="无结果",
                result_type=ResultType.TEXT,
                source_results=[],
                integration_strategy=strategy,
                confidence=0.0,
            )
        
        # 如果只有一个结果，直接返回
        if len(skill_results) == 1:
            single_result = skill_results[0]
            return IntegratedResult(
                integrated_data=single_result.result_data,
                result_type=single_result.result_type,
                source_results=skill_results,
                integration_strategy=strategy,
                confidence=single_result.confidence,
                metadata={"note": "单结果直接返回"},
            )
        
        # 根据策略选择整合方法
        if strategy == IntegrationStrategy.MERGE:
            return self._integrate_merge(skill_results, context)
        elif strategy == IntegrationStrategy.PRIORITY:
            return self._integrate_priority(skill_results, context)
        elif strategy == IntegrationStrategy.CONFLICT_RESOLUTION:
            return self._integrate_with_conflict_resolution(skill_results, context)
        elif strategy == IntegrationStrategy.STRUCTURED_MERGE:
            return self._integrate_structured_merge(skill_results, context)
        elif strategy == IntegrationStrategy.SUMMARY:
            return self._integrate_summary(skill_results, context)
        else:
            # 默认使用合并策略
            return self._integrate_merge(skill_results, context)
    
    def _integrate_merge(self, skill_results: List[SkillResult], 
                        context: Dict) -> IntegratedResult:
        """合并策略：简单合并所有结果"""
        # 按技能优先级排序
        sorted_results = self._sort_by_priority(skill_results)
        
        # 确定结果类型（取第一个结果的类型，或混合类型）
        result_types = set(result.result_type for result in sorted_results)
        if len(result_types) == 1:
            result_type = sorted_results[0].result_type
        else:
            result_type = ResultType.MIXED
        
        # 调用对应的类型处理器
        handler = self.type_handlers.get(result_type, self._integrate_mixed)
        integrated_data = handler(sorted_results, context)
        
        # 计算整体置信度（取平均值）
        avg_confidence = sum(result.confidence for result in sorted_results) / len(sorted_results)
        
        return IntegratedResult(
            integrated_data=integrated_data,
            result_type=result_type,
            source_results=skill_results,
            integration_strategy=IntegrationStrategy.MERGE,
            confidence=avg_confidence,
            metadata={"merge_method": "简单合并"},
        )
    
    def _integrate_priority(self, skill_results: List[SkillResult], 
                           context: Dict) -> IntegratedResult:
        """优先级策略：按优先级选择或合并"""
        # 按优先级排序
        sorted_results = self._sort_by_priority(skill_results)
        
        # 取最高优先级的结果
        top_result = sorted_results[0]
        
        # 检查是否有其他高优先级结果需要合并
        # 如果前几个结果优先级接近，合并它们
        if len(sorted_results) > 1:
            top_priority = self._get_skill_priority(top_result.skill_name)
            second_priority = self._get_skill_priority(sorted_results[1].skill_name)
            
            # 如果优先级差距小于10，合并前两个结果
            if abs(top_priority - second_priority) < 10:
                # 合并前两个结果
                merged_data = self._merge_two_results(top_result, sorted_results[1], context)
                return IntegratedResult(
                    integrated_data=merged_data,
                    result_type=top_result.result_type,
                    source_results=skill_results,
                    integration_strategy=IntegrationStrategy.PRIORITY,
                    confidence=max(top_result.confidence, sorted_results[1].confidence),
                    metadata={"priority_merge": "前两个结果合并"},
                )
        
        # 否则只返回最高优先级结果
        return IntegratedResult(
            integrated_data=top_result.result_data,
            result_type=top_result.result_type,
            source_results=skill_results,
            integration_strategy=IntegrationStrategy.PRIORITY,
            confidence=top_result.confidence,
            metadata={"priority_selection": "最高优先级结果"},
        )
    
    def _integrate_with_conflict_resolution(self, skill_results: List[SkillResult], 
                                           context: Dict) -> IntegratedResult:
        """冲突解决策略：检测并解决冲突后合并"""
        # 检测冲突
        conflicts = self._detect_conflicts(skill_results, context)
        
        if conflicts:
            # 解决冲突
            resolved_results = self._resolve_conflicts(skill_results, conflicts, context)
            
            # 使用合并策略整合解决冲突后的结果
            return self._integrate_merge(resolved_results, context)
        else:
            # 无冲突，直接合并
            return self._integrate_merge(skill_results, context)
    
    def _integrate_structured_merge(self, skill_results: List[SkillResult], 
                                   context: Dict) -> IntegratedResult:
        """结构化合并策略"""
        # 尝试提取结构化信息
        structured_results = []
        
        for result in skill_results:
            structured = self._extract_structured_data(result, context)
            if structured:
                structured_results.append((result, structured))
        
        if not structured_results:
            # 无法提取结构化信息，回退到普通合并
            return self._integrate_merge(skill_results, context)
        
        # 合并结构化数据
        merged_structured = {}
        for result, structured in structured_results:
            # 深度合并字典
            merged_structured = self._deep_merge_dicts(merged_structured, structured)
        
        return IntegratedResult(
            integrated_data=merged_structured,
            result_type=ResultType.STRUCTURED,
            source_results=skill_results,
            integration_strategy=IntegrationStrategy.STRUCTURED_MERGE,
            confidence=sum(result.confidence for result, _ in structured_results) / len(structured_results),
            metadata={"structured_merge": True},
        )
    
    def _integrate_summary(self, skill_results: List[SkillResult], 
                          context: Dict) -> IntegratedResult:
        """摘要策略：生成摘要"""
        # 将所有文本结果合并
        text_parts = []
        for result in skill_results:
            if result.result_type == ResultType.TEXT:
                text_parts.append(str(result.result_data))
            elif result.result_type == ResultType.STRUCTURED:
                text_parts.append(json.dumps(result.result_data, ensure_ascii=False, indent=2))
            else:
                text_parts.append(f"[{result.result_type.value}]: {result.result_data}")
        
        full_text = "\n\n".join(text_parts)
        
        # 生成摘要（简化版：取前500字符）
        if len(full_text) > 500:
            summary = full_text[:500] + "..."
            summary += f"\n\n（完整内容共{len(full_text)}字符，已截断）"
        else:
            summary = full_text
        
        return IntegratedResult(
            integrated_data=summary,
            result_type=ResultType.TEXT,
            source_results=skill_results,
            integration_strategy=IntegrationStrategy.SUMMARY,
            confidence=sum(result.confidence for result in skill_results) / len(skill_results),
            metadata={"summary_length": len(summary)},
        )
    
    def _sort_by_priority(self, skill_results: List[SkillResult]) -> List[SkillResult]:
        """按技能优先级排序（从高到低）"""
        return sorted(skill_results, 
                     key=lambda x: self._get_skill_priority(x.skill_name), 
                     reverse=True)
    
    def _get_skill_priority(self, skill_name: str) -> int:
        """获取技能优先级"""
        # 检查精确匹配
        if skill_name in self.skill_priority:
            return self.skill_priority[skill_name]
        
        # 检查部分匹配
        for key, priority in self.skill_priority.items():
            if key in skill_name:
                return priority
        
        # 默认优先级
        return 50
    
    def _detect_conflicts(self, skill_results: List[SkillResult], 
                         context: Dict) -> List[Dict]:
        """检测结果之间的冲突"""
        conflicts = []
        
        if len(skill_results) < 2:
            return conflicts
        
        # 简单冲突检测：检查相同主题的不同结论
        # 这里简化实现，实际需要更复杂的冲突检测逻辑
        for i in range(len(skill_results)):
            for j in range(i + 1, len(skill_results)):
                result_i = skill_results[i]
                result_j = skill_results[j]
                
                # 如果两个结果类型相同且置信度都高，但内容差异大，可能冲突
                if (result_i.result_type == result_j.result_type and
                    result_i.confidence > 0.7 and result_j.confidence > 0.7):
                    
                    # 简单文本相似度检测（简化）
                    if self._calculate_text_difference(result_i.result_data, result_j.result_data) > 0.7:
                        conflicts.append({
                            "result1": result_i,
                            "result2": result_j,
                            "type": "content_conflict",
                            "confidence_diff": abs(result_i.confidence - result_j.confidence),
                        })
        
        return conflicts
    
    def _resolve_conflicts(self, skill_results: List[SkillResult], 
                          conflicts: List[Dict], context: Dict) -> List[SkillResult]:
        """解决冲突"""
        if not conflicts:
            return skill_results
        
        # 简化处理：保留置信度最高的结果
        resolved_results = skill_results.copy()
        
        for conflict in conflicts:
            result1 = conflict["result1"]
            result2 = conflict["result2"]
            
            # 按置信度选择
            if result1.confidence >= result2.confidence:
                # 移除result2
                if result2 in resolved_results:
                    resolved_results.remove(result2)
            else:
                # 移除result1
                if result1 in resolved_results:
                    resolved_results.remove(result1)
        
        return resolved_results
    
    def _calculate_text_difference(self, text1: Any, text2: Any) -> float:
        """计算文本差异度（简化版）"""
        str1 = str(text1).lower()
        str2 = str(text2).lower()
        
        if str1 == str2:
            return 0.0
        
        # 简单差异计算：基于长度差异和共同词汇
        words1 = set(re.findall(r'\w+', str1))
        words2 = set(re.findall(r'\w+', str2))
        
        if not words1 and not words2:
            return 1.0
        
        common_words = words1.intersection(words2)
        union_words = words1.union(words2)
        
        if not union_words:
            return 1.0
        
        # Jaccard差异度
        similarity = len(common_words) / len(union_words)
        return 1.0 - similarity
    
    def _extract_structured_data(self, skill_result: SkillResult, 
                                context: Dict) -> Optional[Dict]:
        """从结果中提取结构化数据"""
        result_data = skill_result.result_data
        
        if isinstance(result_data, dict):
            return result_data
        elif isinstance(result_data, str):
            # 尝试解析JSON
            try:
                parsed = json.loads(result_data)
                if isinstance(parsed, dict):
                    return parsed
            except:
                pass
            
            # 尝试提取键值对
            key_value_pattern = r'(\w+)[:：]\s*([^\n]+)'
            matches = re.findall(key_value_pattern, result_data)
            
            if matches:
                structured = {}
                for key, value in matches:
                    structured[key.strip()] = value.strip()
                return structured
        
        return None
    
    def _deep_merge_dicts(self, dict1: Dict, dict2: Dict) -> Dict:
        """深度合并两个字典"""
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge_dicts(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _merge_two_results(self, result1: SkillResult, result2: SkillResult, 
                          context: Dict) -> Any:
        """合并两个结果"""
        # 如果类型相同，使用对应的处理器
        if result1.result_type == result2.result_type:
            handler = self.type_handlers.get(result1.result_type, self._integrate_mixed)
            return handler([result1, result2], context)
        else:
            # 类型不同，创建混合结果
            return f"{result1.result_data}\n\n---\n\n{result2.result_data}"
    
    # 类型处理器方法
    def _integrate_text(self, skill_results: List[SkillResult], context: Dict) -> str:
        """整合文本结果"""
        texts = []
        for result in skill_results:
            texts.append(str(result.result_data))
        
        # 去重并合并
        unique_texts = []
        seen = set()
        for text in texts:
            if text not in seen:
                seen.add(text)
                unique_texts.append(text)
        
        return "\n\n".join(unique_texts)
    
    def _integrate_structured(self, skill_results: List[SkillResult], context: Dict) -> Dict:
        """整合结构化结果"""
        merged = {}
        for result in skill_results:
            if isinstance(result.result_data, dict):
                merged = self._deep_merge_dicts(merged, result.result_data)
            else:
                # 尝试转换
                structured = self._extract_structured_data(result, context)
                if structured:
                    merged = self._deep_merge_dicts(merged, structured)
        
        return merged
    
    def _integrate_code(self, skill_results: List[SkillResult], context: Dict) -> str:
        """整合代码结果"""
        code_blocks = []
        for result in skill_results:
            code_blocks.append(str(result.result_data))
        
        # 简单合并代码块
        return "\n\n# --- 下一个代码块 ---\n\n".join(code_blocks)
    
    def _integrate_list(self, skill_results: List[SkillResult], context: Dict) -> List:
        """整合列表结果"""
        all_items = []
        for result in skill_results:
            if isinstance(result.result_data, list):
                all_items.extend(result.result_data)
            else:
                all_items.append(result.result_data)
        
        # 去重
        unique_items = []
        seen = set()
        for item in all_items:
            item_str = str(item)
            if item_str not in seen:
                seen.add(item_str)
                unique_items.append(item)
        
        return unique_items
    
    def _integrate_table(self, skill_results: List[SkillResult], context: Dict) -> str:
        """整合格式化表格结果"""
        tables = []
        for result in skill_results:
            tables.append(str(result.result_data))
        
        return "\n\n--- 下一个表格 ---\n\n".join(tables)
    
    def _integrate_mixed(self, skill_results: List[SkillResult], context: Dict) -> str:
        """整合混合类型结果"""
        sections = []
        for result in skill_results:
            section_title = f"[{result.skill_name} - {result.result_type.value}]"
            section_content = str(result.result_data)
            sections.append(f"{section_title}\n{section_content}")
        
        return "\n\n" + "="*50 + "\n\n".join(sections)
    
    # 冲突解决方法
    def _resolve_conflict_by_confidence(self, result1: SkillResult, 
                                       result2: SkillResult, context: Dict) -> SkillResult:
        """按置信度解决冲突"""
        if result1.confidence >= result2.confidence:
            return result1
        else:
            return result2
    
    def _resolve_text_conflict(self, result1: SkillResult, 
                              result2: SkillResult, context: Dict) -> SkillResult:
        """解决文本冲突"""
        # 如果一个是另一个的子集，返回更全面的
        text1 = str(result1.result_data).lower()
        text2 = str(result2.result_data).lower()
        
        if text1 in text2:
            return result2
        elif text2 in text1:
            return result1
        
        # 否则按置信度选择
        return self._resolve_conflict_by_confidence(result1, result2, context)
    
    def _resolve_numeric_conflict(self, result1: SkillResult, 
                                 result2: SkillResult, context: Dict) -> SkillResult:
        """解决数值冲突"""
        # 尝试提取数值
        def extract_number(text):
            numbers = re.findall(r'\d+\.?\d*', str(text))
            if numbers:
                return float(numbers[0])
            return None
        
        num1 = extract_number(result1.result_data)
        num2 = extract_number(result2.result_data)
        
        if num1 is not None and num2 is not None:
            # 如果有上下文知道哪个更合理，使用上下文
            # 否则返回置信度高的
            return self._resolve_conflict_by_confidence(result1, result2, context)
        else:
            # 无法提取数值，按置信度选择
            return self._resolve_conflict_by_confidence(result1, result2, context)


# 测试函数
def test_result_integrator():
    """测试结果整合器"""
    integrator = ResultIntegrator()
    
    # 创建测试结果
    results = [
        SkillResult(
            skill_name="知识学习",
            result_data="根据资料显示，AI OS的核心是调度引擎。",
            result_type=ResultType.TEXT,
            confidence=0.9,
        ),
        SkillResult(
            skill_name="象思维",
            result_data={"洞察": "AI OS应该像人脑一样具有层次化结构", "创新点": "木火共生关系"},
            result_type=ResultType.STRUCTURED,
            confidence=0.8,
        ),
        SkillResult(
            skill_name="五色光",
            result_data=["优点：结构清晰", "缺点：实现复杂", "建议：分阶段实施"],
            result_type=ResultType.LIST,
            confidence=0.85,
        ),
    ]
    
    print("结果整合器测试：")
    print("-" * 80)
    
    # 测试不同整合策略
    strategies = [
        IntegrationStrategy.MERGE,
        IntegrationStrategy.PRIORITY,
        IntegrationStrategy.CONFLICT_RESOLUTION,
        IntegrationStrategy.STRUCTURED_MERGE,
        IntegrationStrategy.SUMMARY,
    ]
    
    for strategy in strategies:
        print(f"\n整合策略: {strategy.value}")
        integrated_result = integrator.integrate(results, strategy)
        
        print(f"  结果类型: {integrated_result.result_type.value}")
        print(f"  置信度: {integrated_result.confidence:.2f}")
        print(f"  源结果数: {len(integrated_result.source_results)}")
        
        # 打印整合后的数据（前200字符）
        data_str = str(integrated_result.integrated_data)
        if len(data_str) > 200:
            data_str = data_str[:200] + "..."
        print(f"  整合数据: {data_str}")
        print()


if __name__ == "__main__":
    test_result_integrator()