#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI龙龟共生伙伴操作系统 - 扩展四层记忆管理系统
集成龙心OS场景记忆和技能调用历史

架构:
  SOUL    层 - 灵魂记忆（信仰、文化、人格、思维模型）
  USER    层 - 用户记忆（偏好、历史、行为、成长）
  TOOLS   层 - 工具记忆（技能库、API、工作流）
  SESSION 层 - 会话记忆（当前对话、临时数据）
  场景记忆   - 龙心OS S0-S9场景分类记忆
  技能历史   - WorkBuddy技能调用记录

版本: 2.0.0
开发者: 龙龟神将
用户: 悟空
"""

import os
import sys
import json
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
import hashlib


BASE_DIR = Path(__file__).parent.parent
MEMORY_DIR = BASE_DIR / "memory"

LAYERS = {
    "soul":    MEMORY_DIR / "soul",
    "user":    MEMORY_DIR / "user",
    "tools":   MEMORY_DIR / "tools",
    "session": MEMORY_DIR / "session",
    "archive": MEMORY_DIR / "archive",
    "scenes":  MEMORY_DIR / "scenes",    # 新增：场景记忆专用层
}

LAYER_DESCRIPTIONS = {
    "soul":    "灵魂层 - 信仰、文化、人格、思维模型",
    "user":    "用户层 - 偏好、历史、行为、成长轨迹",
    "tools":   "工具层 - 技能库、API接口、工作流配置",
    "session": "会话层 - 当前对话、临时数据、上下文",
    "archive": "归档层 - 压缩后的历史记忆",
    "scenes":  "场景层 - 龙心OS S0-S9场景分类记忆",
}

# 龙心OS场景分类
DRAGON_HEART_SCENES = {
    "S0": "简单信息获取",
    "S1": "常规理解分析",
    "S2": "深度学习探索",
    "S3": "创新突破创作",
    "S4": "复杂问题解决",
    "S5": "重大决策判断",
    "S6": "多系统协同",
    "S7": "系统优化演进",
    "S8": "原象涌现创造",
    "S9": "大圆满见地实践",
}


class ExtendedMemorySystem:
    """扩展四层记忆系统 - 支持场景记忆和技能历史"""
    
    def __init__(self, memory_path: Optional[str] = None):
        self.memory_dir = Path(memory_path) if memory_path else MEMORY_DIR
        self._ensure_dirs()
    
    def _ensure_dirs(self):
        """确保所有目录存在"""
        for layer, path in LAYERS.items():
            path.mkdir(parents=True, exist_ok=True)
    
    def _layer_path(self, layer: str) -> Path:
        """获取层目录路径"""
        if layer not in LAYERS:
            raise ValueError(f"无效层级: {layer}，有效值: {list(LAYERS.keys())}")
        return LAYERS[layer]
    
    def store(self, layer: str, content: str, title: str = "",
              importance: int = 5, tags: Optional[List[str]] = None,
              scene: Optional[str] = None, skill_context: Optional[Dict] = None) -> str:
        """
        存储记忆到指定层（支持场景和技能上下文）
        
        Args:
            layer:        层级 (soul/user/tools/session/scenes)
            content:      记忆内容
            title:        标题（可选，自动生成）
            importance:   重要性 1-10
            tags:         标签列表
            scene:        场景分类 (S0-S9)
            skill_context: 技能调用上下文
            
        Returns:
            memory_id: 记忆唯一ID
        """
        memory_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()
        title = title or content[:30] + ("..." if len(content) > 30 else "")
        
        # 验证场景分类
        if scene and scene not in DRAGON_HEART_SCENES:
            raise ValueError(f"无效场景: {scene}，有效值: {list(DRAGON_HEART_SCENES.keys())}")
        
        memory_entry = {
            "id": memory_id,
            "layer": layer,
            "title": title,
            "content": content,
            "importance": max(1, min(10, importance)),
            "tags": tags or [],
            "scene": scene,                    # 新增：场景分类
            "skill_context": skill_context,    # 新增：技能调用上下文
            "created_at": timestamp,
            "updated_at": timestamp,
            "access_count": 0,
            "last_accessed": None,
        }
        
        layer_dir = self._layer_path(layer)
        file_path = layer_dir / f"{memory_id}.json"
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(memory_entry, f, ensure_ascii=False, indent=2)
        
        return memory_id
    
    def store_scene_memory(self, scene: str, content: str, 
                          title: str = "", importance: int = 5,
                          tags: Optional[List[str]] = None) -> str:
        """
        专用方法：存储场景记忆
        
        Args:
            scene: 场景分类 (S0-S9)
            content: 记忆内容
            title: 标题
            importance: 重要性
            tags: 标签
            
        Returns:
            memory_id
        """
        return self.store(
            layer="scenes",
            content=content,
            title=title or f"{scene}: {content[:30]}",
            importance=importance,
            tags=tags,
            scene=scene
        )
    
    def store_skill_history(self, skill_name: str, skill_params: Dict,
                           result: Any, execution_time: float,
                           success: bool = True, error_msg: Optional[str] = None) -> str:
        """
        存储技能调用历史
        
        Args:
            skill_name: 技能名称
            skill_params: 技能参数
            result: 执行结果
            execution_time: 执行时间（秒）
            success: 是否成功
            error_msg: 错误信息
            
        Returns:
            memory_id
        """
        skill_context = {
            "skill_name": skill_name,
            "skill_params": skill_params,
            "execution_time": execution_time,
            "success": success,
            "error_msg": error_msg,
            "result_type": type(result).__name__
        }
        
        content = f"技能调用: {skill_name}\n参数: {json.dumps(skill_params, ensure_ascii=False)}\n结果: {str(result)[:200]}"
        
        return self.store(
            layer="tools",
            content=content,
            title=f"技能调用: {skill_name}",
            importance=3,  # 技能调用历史重要性较低
            tags=["skill_call", skill_name],
            skill_context=skill_context
        )
    
    def retrieve(self, memory_id: str, layer: Optional[str] = None) -> Optional[Dict]:
        """按 ID 检索单条记忆"""
        search_layers = [layer] if layer else list(LAYERS.keys())
        
        for lyr in search_layers:
            if lyr == "archive":
                continue
            file_path = LAYERS[lyr] / f"{memory_id}.json"
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    entry = json.load(f)
                # 更新访问统计
                entry["access_count"] += 1
                entry["last_accessed"] = datetime.now().isoformat()
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(entry, f, ensure_ascii=False, indent=2)
                return entry
        return None
    
    def search(self, query: str, layer: str = "all",
               scene: Optional[str] = None, min_importance: int = 0,
               limit: int = 10) -> List[Dict]:
        """
        增强语义搜索（支持场景过滤和重要性阈值）
        
        Args:
            query: 搜索关键词
            layer: 层级过滤（all 表示全部）
            scene: 场景过滤 (S0-S9)
            min_importance: 最小重要性阈值
            limit: 最大返回数量
            
        Returns:
            匹配的记忆列表（按相关性+重要性排序）
        """
        search_layers = list(LAYERS.keys())[:-1] if layer == "all" else [layer]
        results = []
        
        query_lower = query.lower()
        
        for lyr in search_layers:
            layer_dir = LAYERS.get(lyr)
            if not layer_dir or not layer_dir.exists():
                continue
            
            for json_file in layer_dir.glob("*.json"):
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        entry = json.load(f)
                    
                    # 重要性过滤
                    if entry.get("importance", 0) < min_importance:
                        continue
                    
                    # 场景过滤
                    if scene and entry.get("scene") != scene:
                        continue
                    
                    # 计算相关度分数
                    score = 0
                    title = entry.get("title", "").lower()
                    content = entry.get("content", "").lower()
                    tags = " ".join(entry.get("tags", [])).lower()
                    
                    if query_lower in title:
                        score += 10
                    if query_lower in content:
                        score += 5
                    if query_lower in tags:
                        score += 8
                    
                    # 关键词部分匹配
                    for word in query_lower.split():
                        if word in title:
                            score += 3
                        if word in content:
                            score += 1
                        if word in tags:
                            score += 2
                    
                    # 技能上下文匹配
                    skill_context = entry.get("skill_context", {})
                    if skill_context:
                        skill_name = skill_context.get("skill_name", "").lower()
                        if query_lower in skill_name:
                            score += 7
                    
                    if score > 0:
                        entry["_relevance_score"] = score + entry.get("importance", 5)
                        results.append(entry)
                
                except (json.JSONDecodeError, KeyError):
                    continue
        
        # 按相关度排序
        results.sort(key=lambda x: x.get("_relevance_score", 0), reverse=True)
        return results[:limit]
    
    def search_by_scene(self, scene: str, limit: int = 20) -> List[Dict]:
        """按场景分类搜索记忆"""
        results = []
        scene_dir = LAYERS["scenes"]
        
        if not scene_dir.exists():
            return results
        
        for json_file in scene_dir.glob("*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    entry = json.load(f)
                
                if entry.get("scene") == scene:
                    results.append(entry)
            
            except (json.JSONDecodeError, KeyError):
                continue
        
        # 按重要性排序
        results.sort(key=lambda x: x.get("importance", 0), reverse=True)
        return results[:limit]
    
    def search_skill_history(self, skill_name: Optional[str] = None,
                            success_only: bool = False,
                            limit: int = 20) -> List[Dict]:
        """搜索技能调用历史"""
        results = []
        tools_dir = LAYERS["tools"]
        
        if not tools_dir.exists():
            return results
        
        for json_file in tools_dir.glob("*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    entry = json.load(f)
                
                skill_context = entry.get("skill_context")
                if not skill_context:
                    continue
                
                # 技能名称过滤
                if skill_name and skill_context.get("skill_name") != skill_name:
                    continue
                
                # 成功过滤
                if success_only and not skill_context.get("success", True):
                    continue
                
                results.append(entry)
            
            except (json.JSONDecodeError, KeyError):
                continue
        
        # 按时间倒序
        results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return results[:limit]
    
    def list_layer(self, layer: str, limit: int = 20) -> List[Dict]:
        """列出某层所有记忆（按时间倒序）"""
        layer_dir = self._layer_path(layer)
        entries = []
        
        for json_file in layer_dir.glob("*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    entry = json.load(f)
                entries.append(entry)
            except (json.JSONDecodeError, KeyError):
                continue
        
        entries.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return entries[:limit]
    
    def compress_and_archive(self, days_old: int = 30,
                            importance_threshold: int = 5) -> Dict:
        """
        增强压缩归档 - 保留场景记忆和重要技能历史
        
        - 保留重要性 >= importance_threshold 的记忆
        - 场景记忆永久保留（除非重要性极低）
        - 技能调用历史按时间归档
        
        Returns:
            统计信息 {compressed, archived, kept}
        """
        cutoff_date = datetime.now() - timedelta(days=days_old)
        stats = {"compressed": 0, "archived": 0, "kept": 0}
        
        archive_dir = LAYERS["archive"]
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        for layer_name in ["user", "tools", "session", "scenes"]:
            layer_dir = LAYERS[layer_name]
            if not layer_dir.exists():
                continue
            
            for json_file in layer_dir.glob("*.json"):
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        entry = json.load(f)
                    
                    created_at = datetime.fromisoformat(entry.get("created_at", datetime.now().isoformat()))
                    importance = entry.get("importance", 5)
                    scene = entry.get("scene")
                    is_skill_call = "skill_call" in entry.get("tags", [])
                    
                    # 特殊处理规则
                    keep = False
                    
                    # 规则1: 场景记忆永久保留（重要性>=3）
                    if layer_name == "scenes" and importance >= 3:
                        keep = True
                    
                    # 规则2: 重要技能调用历史保留
                    elif is_skill_call and importance >= 7:
                        keep = True
                    
                    # 规则3: 普通归档规则
                    elif created_at < cutoff_date and importance < importance_threshold:
                        # 移至归档
                        archive_path = archive_dir / json_file.name
                        entry["archived_at"] = datetime.now().isoformat()
                        entry["original_layer"] = layer_name
                        with open(archive_path, "w", encoding="utf-8") as f:
                            json.dump(entry, f, ensure_ascii=False, indent=2)
                        json_file.unlink()
                        stats["archived"] += 1
                    else:
                        keep = True
                    
                    if keep:
                        stats["kept"] += 1
                
                except Exception:
                    continue
        
        stats["compressed"] = stats["archived"]
        return stats
    
    def get_stats(self) -> Dict:
        """获取各层记忆统计（包含场景和技能统计）"""
        stats = {}
        skill_stats = {}
        scene_stats = {}
        
        for layer_name, layer_dir in LAYERS.items():
            if layer_dir.exists():
                count = len(list(layer_dir.glob("*.json")))
                stats[layer_name] = count
            else:
                stats[layer_name] = 0
        
        # 额外统计：技能调用次数
        tools_dir = LAYERS["tools"]
        if tools_dir.exists():
            skill_calls = 0
            for json_file in tools_dir.glob("*.json"):
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        entry = json.load(f)
                    if entry.get("skill_context"):
                        skill_calls += 1
                except:
                    continue
            stats["skill_calls"] = skill_calls
        
        # 场景分类统计
        scenes_dir = LAYERS["scenes"]
        if scenes_dir.exists():
            for scene_code in DRAGON_HEART_SCENES.keys():
                scene_stats[scene_code] = 0
            
            for json_file in scenes_dir.glob("*.json"):
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        entry = json.load(f)
                    scene = entry.get("scene")
                    if scene in scene_stats:
                        scene_stats[scene] += 1
                except:
                    continue
            stats["scenes"] = scene_stats
        
        return stats
    
    def delete(self, memory_id: str, layer: Optional[str] = None) -> bool:
        """删除指定记忆"""
        search_layers = [layer] if layer else list(LAYERS.keys())
        for lyr in search_layers:
            file_path = LAYERS[lyr] / f"{memory_id}.json"
            if file_path.exists():
                file_path.unlink()
                return True
        return False


# ============================================================
# CLI 接口
# ============================================================

def cli_init(args):
    mem = ExtendedMemorySystem()
    stats = mem.get_stats()
    print("✅ 扩展记忆系统初始化完成")
    print(f"📊 各层记忆数量: {stats}")
    if "scenes" in stats:
        print(f"🎭 场景记忆分布: {stats['scenes']}")


def cli_store_scene(args):
    mem = ExtendedMemorySystem()
    tags = args.tags.split(",") if args.tags else []
    memory_id = mem.store_scene_memory(
        scene=args.scene,
        content=args.content,
        title=args.title,
        importance=args.importance,
        tags=tags
    )
    print(f"✅ 场景记忆已存储 → ID: {memory_id} | 场景: {args.scene}")


def cli_search_scene(args):
    mem = ExtendedMemorySystem()
    results = mem.search_by_scene(scene=args.scene, limit=args.limit)
    
    if not results:
        print(f"🔍 未找到场景 '{args.scene}' 的记忆")
        return
    
    print(f"🔍 场景 '{args.scene}' → 找到 {len(results)} 条记忆:\n")
    for i, r in enumerate(results, 1):
        print(f"  [{i}] {r['title']}")
        print(f"       重要性: {'★' * r['importance']} | 标签: {', '.join(r['tags']) or '无'}")
        print(f"       {r['content'][:100]}{'...' if len(r['content']) > 100 else ''}")
        print()


def cli_skill_history(args):
    mem = ExtendedMemorySystem()
    results = mem.search_skill_history(
        skill_name=args.skill if args.skill else None,
        success_only=args.success_only,
        limit=args.limit
    )
    
    if not results:
        print("🔧 暂无技能调用历史")
        return
    
    print(f"🔧 技能调用历史 ({len(results)} 条):\n")
    for i, r in enumerate(results, 1):
        skill_ctx = r.get("skill_context", {})
        success = "✅" if skill_ctx.get("success") else "❌"
        print(f"  [{i}] {success} {skill_ctx.get('skill_name', '未知技能')}")
        print(f"       时间: {skill_ctx.get('execution_time', 0):.2f}s | {r['created_at'][:19]}")
        if not skill_ctx.get("success"):
            print(f"       错误: {skill_ctx.get('error_msg', '未知错误')}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="AI龙龟共生伙伴OS - 扩展四层记忆管理系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python memory_manager.py init
  python memory_manager.py store-scene S2 "深度学习关于龙心OS调度算法" --title "调度算法学习" --importance 8
  python memory_manager.py search-scene --scene S2 --limit 10
  python memory_manager.py skill-history --skill "龙心OS" --success-only
  python memory_manager.py stats
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # init
    subparsers.add_parser("init", help="初始化记忆系统")
    
    # store-scene
    p_store_scene = subparsers.add_parser("store-scene", help="存储场景记忆")
    p_store_scene.add_argument("scene", choices=list(DRAGON_HEART_SCENES.keys()), help="场景分类 (S0-S9)")
    p_store_scene.add_argument("content", help="记忆内容")
    p_store_scene.add_argument("--title", default="", help="记忆标题")
    p_store_scene.add_argument("--importance", type=int, default=5, help="重要性 1-10")
    p_store_scene.add_argument("--tags", help="标签，逗号分隔")
    
    # search-scene
    p_search_scene = subparsers.add_parser("search-scene", help="搜索场景记忆")
    p_search_scene.add_argument("--scene", required=True, choices=list(DRAGON_HEART_SCENES.keys()), help="场景分类")
    p_search_scene.add_argument("--limit", type=int, default=10, help="最大返回数量")
    
    # skill-history
    p_skill_history = subparsers.add_parser("skill-history", help="查看技能调用历史")
    p_skill_history.add_argument("--skill", help="技能名称过滤")
    p_skill_history.add_argument("--success-only", action="store_true", help="仅显示成功记录")
    p_skill_history.add_argument("--limit", type=int, default=20, help="最大返回数量")
    
    # stats
    subparsers.add_parser("stats", help="查看扩展统计")
    
    args = parser.parse_args()
    
    commands = {
        "init": cli_init,
        "store-scene": cli_store_scene,
        "search-scene": cli_search_scene,
        "skill-history": cli_skill_history,
        "stats": cli_stats,
    }
    
    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()