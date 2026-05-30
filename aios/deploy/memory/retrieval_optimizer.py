#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆检索优化算法
提供更智能的记忆检索功能

功能:
1. 关键词扩展（同义词、相关词）
2. 场景感知检索优化
3. 重要性加权检索
4. 时间衰减因子
5. 检索结果重排序

版本: 1.0.0
开发者: 龙龟神将
用户: 悟空
"""

import re
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Set
from pathlib import Path
from .memory_manager import ExtendedMemorySystem, DRAGON_HEART_SCENES


class RetrievalOptimizer:
    """记忆检索优化器"""
    
    # 同义词词典（简化版）
    SYNONYM_DICT = {
        # 调度相关
        "调度": ["调度", "安排", "分配", "路由", "分配"],
        "引擎": ["引擎", "发动机", "处理器", "核心"],
        "算法": ["算法", "方法", "策略", "方案"],
        
        # 记忆相关
        "记忆": ["记忆", "回忆", "记录", "存储"],
        "学习": ["学习", "掌握", "理解", "认知"],
        "理解": ["理解", "领会", "明白", "懂得"],
        
        # 技能相关
        "技能": ["技能", "能力", "技术", "功能"],
        "调用": ["调用", "执行", "运行", "启动"],
        "执行": ["执行", "实施", "完成", "落实"],
        
        # 场景相关
        "简单": ["简单", "容易", "基础", "初级"],
        "复杂": ["复杂", "困难", "高级", "深入"],
        "创新": ["创新", "创造", "突破", "革新"],
        
        # 龙心OS相关
        "龙心": ["龙心", "核心", "心脏", "中枢"],
        "龙脑": ["龙脑", "思维", "智能", "大脑"],
        "龙爪": ["龙爪", "执行", "工具", "手段"],
    }
    
    # 场景相关关键词映射
    SCENE_KEYWORDS = {
        "S0": ["信息", "获取", "查询", "查找", "搜索", "简单"],
        "S1": ["理解", "分析", "解释", "说明", "常规"],
        "S2": ["学习", "深度", "探索", "研究", "掌握"],
        "S3": ["创新", "创造", "突破", "设计", "创作"],
        "S4": ["问题", "解决", "方案", "复杂", "处理"],
        "S5": ["决策", "判断", "选择", "重大", "决定"],
        "S6": ["协同", "协作", "系统", "多系统", "整合"],
        "S7": ["优化", "演进", "改进", "提升", "系统"],
        "S8": ["原象", "涌现", "创造", "本源", "本质"],
        "S9": ["大圆满", "见地", "实践", "修行", "觉悟"],
    }
    
    def __init__(self, memory_system: Optional[ExtendedMemorySystem] = None):
        self.memory = memory_system or ExtendedMemorySystem()
        self._build_keyword_index()
    
    def _build_keyword_index(self):
        """构建关键词索引（简化版，实际应使用倒排索引）"""
        self.keyword_to_memory = {}
        # 在实际实现中，这里会构建完整的倒排索引
        # 为简化，我们只在搜索时动态计算
    
    def expand_keywords(self, query: str) -> List[str]:
        """
        扩展关键词（同义词扩展）
        
        Args:
            query: 原始查询
            
        Returns:
            扩展后的关键词列表
        """
        words = re.findall(r'[\u4e00-\u9fff\w]+', query.lower())
        expanded = set(words)
        
        for word in words:
            # 查找同义词
            for key, synonyms in self.SYNONYM_DICT.items():
                if word == key.lower() or word in [s.lower() for s in synonyms]:
                    expanded.update([s.lower() for s in synonyms])
                    break
        
        return list(expanded)
    
    def infer_scene_from_query(self, query: str) -> Optional[str]:
        """
        从查询推断可能的场景
        
        Args:
            query: 用户查询
            
        Returns:
            场景代码 (S0-S9) 或 None
        """
        query_lower = query.lower()
        scene_scores = {}
        
        for scene_code, keywords in self.SCENE_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in query_lower:
                    score += 1
            if score > 0:
                scene_scores[scene_code] = score
        
        if not scene_scores:
            return None
        
        # 返回得分最高的场景
        return max(scene_scores.items(), key=lambda x: x[1])[0]
    
    def calculate_relevance_score(self, memory_entry: Dict, 
                                 query_keywords: List[str],
                                 query_scene: Optional[str] = None,
                                 current_time: Optional[datetime] = None) -> float:
        """
        计算记忆条目与查询的相关性分数
        
        Args:
            memory_entry: 记忆条目
            query_keywords: 查询关键词列表
            query_scene: 查询场景
            current_time: 当前时间（用于时间衰减）
            
        Returns:
            相关性分数（0-100）
        """
        if current_time is None:
            current_time = datetime.now()
        
        # 基础匹配分数
        base_score = 0.0
        
        title = memory_entry.get("title", "").lower()
        content = memory_entry.get("content", "").lower()
        tags = " ".join(memory_entry.get("tags", [])).lower()
        scene = memory_entry.get("scene")
        
        # 关键词匹配
        for keyword in query_keywords:
            if keyword in title:
                base_score += 10.0
            if keyword in content:
                base_score += 5.0
            if keyword in tags:
                base_score += 8.0
        
        # 场景匹配加分
        if query_scene and scene == query_scene:
            base_score += 15.0
        
        # 技能上下文匹配
        skill_context = memory_entry.get("skill_context")
        if skill_context:
            skill_name = skill_context.get("skill_name", "").lower()
            for keyword in query_keywords:
                if keyword in skill_name:
                    base_score += 7.0
        
        # 重要性加权
        importance = memory_entry.get("importance", 5)
        base_score *= (importance / 5.0)  # 重要性5为基准
        
        # 时间衰减因子（越新的记忆越相关）
        try:
            created_at = datetime.fromisoformat(memory_entry.get("created_at", current_time.isoformat()))
            days_old = (current_time - created_at).days
            time_decay = max(0.3, 1.0 - (days_old / 365.0))  # 一年衰减到30%
            base_score *= time_decay
        except:
            pass
        
        # 访问频率加权（越常访问的越相关）
        access_count = memory_entry.get("access_count", 0)
        access_boost = 1.0 + (access_count * 0.1)  # 每次访问增加10%相关性
        base_score *= min(access_boost, 3.0)  # 最大3倍加成
        
        return base_score
    
    def optimized_search(self, query: str, layer: str = "all",
                        limit: int = 10, use_scene_inference: bool = True) -> List[Dict]:
        """
        优化搜索（带关键词扩展和场景推断）
        
        Args:
            query: 查询字符串
            layer: 层级过滤
            limit: 最大返回数量
            use_scene_inference: 是否使用场景推断
            
        Returns:
            优化排序的记忆列表
        """
        # 关键词扩展
        expanded_keywords = self.expand_keywords(query)
        
        # 场景推断
        inferred_scene = None
        if use_scene_inference:
            inferred_scene = self.infer_scene_from_query(query)
        
        # 获取所有记忆（简化实现，实际应使用索引）
        all_entries = []
        search_layers = list(self.memory.memory_dir.parent.glob("*")) if layer == "all" else [self.memory._layer_path(layer)]
        
        for layer_dir in search_layers:
            if not layer_dir.is_dir():
                continue
            
            for json_file in layer_dir.glob("*.json"):
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        entry = json.load(f)
                    all_entries.append(entry)
                except:
                    continue
        
        # 计算相关性分数
        scored_entries = []
        for entry in all_entries:
            score = self.calculate_relevance_score(
                memory_entry=entry,
                query_keywords=expanded_keywords,
                query_scene=inferred_scene
            )
            if score > 0:
                entry["_optimized_score"] = score
                scored_entries.append(entry)
        
        # 按优化分数排序
        scored_entries.sort(key=lambda x: x.get("_optimized_score", 0), reverse=True)
        
        return scored_entries[:limit]
    
    def search_with_context(self, query: str, context: Dict,
                           limit: int = 10) -> List[Dict]:
        """
        上下文感知搜索
        
        Args:
            query: 查询
            context: 上下文信息（包含场景、用户、技能等信息）
            limit: 最大返回数量
            
        Returns:
            上下文相关的记忆列表
        """
        # 从上下文中提取信息
        scene = context.get("scene")
        user_id = context.get("user_id")
        current_skill = context.get("current_skill")
        history_queries = context.get("recent_queries", [])
        
        # 组合查询（当前查询 + 历史查询）
        combined_query = query + " " + " ".join(history_queries[-3:])  # 最近3条查询
        
        # 执行优化搜索
        results = self.optimized_search(
            query=combined_query,
            layer="all",
            limit=limit * 2,  # 获取更多结果用于过滤
            use_scene_inference=False  # 手动指定场景
        )
        
        # 上下文过滤和重排序
        filtered_results = []
        for entry in results:
            entry_score = entry.get("_optimized_score", 0)
            
            # 场景匹配加分
            if scene and entry.get("scene") == scene:
                entry_score *= 1.5
            
            # 用户相关记忆加分（如果有用户ID字段）
            if user_id and entry.get("user_id") == user_id:
                entry_score *= 1.3
            
            # 当前技能相关记忆加分
            if current_skill:
                skill_context = entry.get("skill_context")
                if skill_context and skill_context.get("skill_name") == current_skill:
                    entry_score *= 1.4
            
            entry["_context_aware_score"] = entry_score
            filtered_results.append(entry)
        
        # 按上下文感知分数排序
        filtered_results.sort(key=lambda x: x.get("_context_aware_score", 0), reverse=True)
        
        return filtered_results[:limit]
    
    def get_search_suggestions(self, query: str, limit: int = 5) -> List[str]:
        """
        获取搜索建议（基于历史搜索和场景）
        
        Args:
            query: 查询前缀
            limit: 最大建议数
            
        Returns:
            搜索建议列表
        """
        # 这里可以集成历史搜索记录
        # 简化实现：基于关键词扩展和场景推断生成建议
        
        suggestions = []
        query_lower = query.lower()
        
        # 基于场景的建议
        inferred_scene = self.infer_scene_from_query(query)
        if inferred_scene:
            scene_desc = DRAGON_HEART_SCENES.get(inferred_scene, "")
            suggestions.append(f"{query} ({scene_desc}相关)")
        
        # 基于同义词的建议
        words = re.findall(r'[\u4e00-\u9fff\w]+', query_lower)
        for word in words:
            for key, synonyms in self.SYNONYM_DICT.items():
                if word == key.lower() or word in [s.lower() for s in synonyms]:
                    for synonym in synonyms:
                        if synonym.lower() != word:
                            new_query = query.replace(word, synonym)
                            if new_query != query:
                                suggestions.append(new_query)
        
        # 去重和截断
        unique_suggestions = []
        seen = set()
        for s in suggestions:
            if s not in seen:
                seen.add(s)
                unique_suggestions.append(s)
        
        return unique_suggestions[:limit]
    
    def analyze_search_patterns(self, days: int = 30) -> Dict:
        """
        分析搜索模式
        
        Args:
            days: 分析天数
            
        Returns:
            搜索模式分析结果
        """
        # 这里可以集成搜索日志分析
        # 简化实现：返回场景分布和热门搜索
        
        # 获取所有记忆的访问统计
        all_entries = []
        for layer_name in ["soul", "user", "tools", "session", "scenes"]:
            layer_dir = self.memory._layer_path(layer_name)
            if not layer_dir.exists():
                continue
            
            for json_file in layer_dir.glob("*.json"):
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        entry = json.load(f)
                    all_entries.append(entry)
                except:
                    continue
        
        # 分析场景分布
        scene_access = {}
        total_access = 0
        
        for entry in all_entries:
            scene = entry.get("scene")
            access_count = entry.get("access_count", 0)
            
            if scene:
                scene_access[scene] = scene_access.get(scene, 0) + access_count
                total_access += access_count
        
        # 分析热门记忆
        sorted_entries = sorted(all_entries, key=lambda x: x.get("access_count", 0), reverse=True)
        top_memories = []
        for entry in sorted_entries[:10]:
            top_memories.append({
                "id": entry.get("id"),
                "title": entry.get("title", "")[:50],
                "layer": entry.get("layer"),
                "scene": entry.get("scene"),
                "access_count": entry.get("access_count", 0),
                "importance": entry.get("importance", 5),
            })
        
        return {
            "total_access_count": total_access,
            "scene_access_distribution": scene_access,
            "top_memories": top_memories,
            "analysis_period_days": days,
        }


# ============================================================
# CLI 接口
# ============================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="记忆检索优化器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python retrieval_optimizer.py search --query "龙心OS调度算法"
  python retrieval_optimizer.py expand --query "学习记忆系统"
  python retrieval_optimizer.py infer-scene --query "如何优化系统性能"
  python retrieval_optimizer.py suggestions --query "技能"
  python retrieval_optimizer.py analyze --days 30
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # search
    p_search = subparsers.add_parser("search", help="优化搜索")
    p_search.add_argument("--query", required=True, help="搜索查询")
    p_search.add_argument("--layer", default="all", help="层级过滤")
    p_search.add_argument("--limit", type=int, default=10, help="最大结果数")
    
    # expand
    p_expand = subparsers.add_parser("expand", help="关键词扩展")
    p_expand.add_argument("--query", required=True, help="原始查询")
    
    # infer-scene
    p_infer = subparsers.add_parser("infer-scene", help="推断场景")
    p_infer.add_argument("--query", required=True, help="查询")
    
    # suggestions
    p_suggest = subparsers.add_parser("suggestions", help="搜索建议")
    p_suggest.add_argument("--query", required=True, help="查询前缀")
    p_suggest.add_argument("--limit", type=int, default=5, help="最大建议数")
    
    # analyze
    p_analyze = subparsers.add_parser("analyze", help="分析搜索模式")
    p_analyze.add_argument("--days", type=int, default=30, help="分析天数")
    
    args = parser.parse_args()
    
    optimizer = RetrievalOptimizer()
    
    if args.command == "search":
        results = optimizer.optimized_search(
            query=args.query,
            layer=args.layer,
            limit=args.limit
        )
        
        if not results:
            print(f"🔍 未找到与 '{args.query}' 相关的记忆")
            return
        
        print(f"🔍 优化搜索 '{args.query}' → 找到 {len(results)} 条记忆:\n")
        for i, r in enumerate(results, 1):
            score = r.get("_optimized_score", 0)
            print(f"  [{i}] [{r['layer'].upper()}] {r['title']}")
            print(f"       相关度: {score:.1f} | 重要性: {'★' * r['importance']}")
            if r.get("scene"):
                print(f"       场景: {r['scene']} - {DRAGON_HEART_SCENES.get(r['scene'], '未知')}")
            print(f"       {r['content'][:80]}{'...' if len(r['content']) > 80 else ''}")
            print()
    
    elif args.command == "expand":
        expanded = optimizer.expand_keywords(args.query)
        print(f"🔤 关键词扩展 '{args.query}':")
        print(f"   原始关键词: {re.findall(r'[\u4e00-\u9fff\w]+', args.query.lower())}")
        print(f"   扩展关键词: {expanded}")
    
    elif args.command == "infer-scene":
        scene = optimizer.infer_scene_from_query(args.query)
        if scene:
            desc = DRAGON_HEART_SCENES.get(scene, "未知")
            print(f"🎭 查询 '{args.query}' 推断场景: {scene} - {desc}")
        else:
            print(f"🎭 查询 '{args.query}' 无法推断场景")
    
    elif args.command == "suggestions":
        suggestions = optimizer.get_search_suggestions(args.query, limit=args.limit)
        if not suggestions:
            print(f"💡 查询 '{args.query}' 暂无搜索建议")
            return
        
        print(f"💡 搜索建议 '{args.query}':")
        for i, s in enumerate(suggestions, 1):
            print(f"  [{i}] {s}")
    
    elif args.command == "analyze":
        analysis = optimizer.analyze_search_patterns(days=args.days)
        print(f"📊 搜索模式分析 (最近{args.days}天):\n")
        print(f"  总访问次数: {analysis['total_access_count']}")
        
        if analysis['scene_access_distribution']:
            print("\n  场景访问分布:")
            for scene, count in sorted(analysis['scene_access_distribution'].items(), key=lambda x: x[1], reverse=True):
                desc = DRAGON_HEART_SCENES.get(scene, "未知")
                print(f"    {scene}: {count}次 - {desc}")
        
        if analysis['top_memories']:
            print("\n  热门记忆 TOP 10:")
            for i, mem in enumerate(analysis['top_memories'], 1):
                print(f"    [{i}] {mem['title']}")
                print(f"        场景: {mem['scene']} | 层级: {mem['layer']} | 访问: {mem['access_count']}次")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()