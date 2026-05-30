#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动压缩归档管理器
基于策略的智能记忆归档系统

策略类型:
1. 时间策略 - 按创建时间归档旧记忆
2. 重要性策略 - 按重要性阈值归档低重要性记忆
3. 访问频率策略 - 归档长时间未访问的记忆
4. 场景策略 - 按场景分类归档
5. 组合策略 - 多种策略组合

版本: 1.0.0
开发者: 龙龟神将
用户: 悟空
"""

import json
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from .memory_manager import ExtendedMemorySystem, DRAGON_HEART_SCENES


class ArchivePolicy:
    """归档策略基类"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.conditions = []
    
    def should_archive(self, memory_entry: Dict) -> bool:
        """
        判断是否应归档该记忆
        
        Args:
            memory_entry: 记忆条目
            
        Returns:
            bool: 是否归档
        """
        raise NotImplementedError("子类必须实现此方法")
    
    def get_stats(self) -> Dict:
        """获取策略统计信息"""
        return {
            "name": self.name,
            "description": self.description,
            "type": self.__class__.__name__
        }


class TimeBasedPolicy(ArchivePolicy):
    """基于时间的归档策略"""
    
    def __init__(self, days_threshold: int = 30, 
                 exclude_layers: List[str] = None):
        super().__init__(
            name="时间策略",
            description=f"归档创建时间超过{days_threshold}天的记忆"
        )
        self.days_threshold = days_threshold
        self.exclude_layers = exclude_layers or ["soul", "scenes"]  # 默认不归档灵魂层和场景层
    
    def should_archive(self, memory_entry: Dict) -> bool:
        # 排除特定层
        if memory_entry.get("layer") in self.exclude_layers:
            return False
        
        # 检查创建时间
        created_at_str = memory_entry.get("created_at")
        if not created_at_str:
            return False
        
        try:
            created_at = datetime.fromisoformat(created_at_str)
            age_days = (datetime.now() - created_at).days
            return age_days > self.days_threshold
        except:
            return False
    
    def get_stats(self) -> Dict:
        stats = super().get_stats()
        stats.update({
            "days_threshold": self.days_threshold,
            "exclude_layers": self.exclude_layers
        })
        return stats


class ImportanceBasedPolicy(ArchivePolicy):
    """基于重要性的归档策略"""
    
    def __init__(self, importance_threshold: int = 3,
                 exclude_scenes: List[str] = None):
        super().__init__(
            name="重要性策略",
            description=f"归档重要性低于{importance_threshold}的记忆"
        )
        self.importance_threshold = importance_threshold
        self.exclude_scenes = exclude_scenes or ["S8", "S9"]  # 默认不归档原象和大圆满场景
    
    def should_archive(self, memory_entry: Dict) -> bool:
        # 排除特定场景
        scene = memory_entry.get("scene")
        if scene in self.exclude_scenes:
            return False
        
        # 检查重要性
        importance = memory_entry.get("importance", 5)
        return importance < self.importance_threshold
    
    def get_stats(self) -> Dict:
        stats = super().get_stats()
        stats.update({
            "importance_threshold": self.importance_threshold,
            "exclude_scenes": self.exclude_scenes
        })
        return stats


class AccessFrequencyPolicy(ArchivePolicy):
    """基于访问频率的归档策略"""
    
    def __init__(self, min_access_count: int = 1,
                 days_without_access: int = 90):
        super().__init__(
            name="访问频率策略",
            description=f"归档{days_without_access}天内访问次数低于{min_access_count}的记忆"
        )
        self.min_access_count = min_access_count
        self.days_without_access = days_without_access
    
    def should_archive(self, memory_entry: Dict) -> bool:
        # 检查访问次数
        access_count = memory_entry.get("access_count", 0)
        if access_count >= self.min_access_count:
            return False
        
        # 检查最后访问时间
        last_accessed_str = memory_entry.get("last_accessed")
        if not last_accessed_str:
            # 从未访问过，检查创建时间
            created_at_str = memory_entry.get("created_at")
            if not created_at_str:
                return False
            
            try:
                created_at = datetime.fromisoformat(created_at_str)
                days_since_creation = (datetime.now() - created_at).days
                return days_since_creation > self.days_without_access
            except:
                return False
        
        try:
            last_accessed = datetime.fromisoformat(last_accessed_str)
            days_since_access = (datetime.now() - last_accessed).days
            return days_since_access > self.days_without_access
        except:
            return False
    
    def get_stats(self) -> Dict:
        stats = super().get_stats()
        stats.update({
            "min_access_count": self.min_access_count,
            "days_without_access": self.days_without_access
        })
        return stats


class SceneBasedPolicy(ArchivePolicy):
    """基于场景的归档策略"""
    
    def __init__(self, scenes_to_archive: List[str] = None,
                 scenes_to_preserve: List[str] = None):
        super().__init__(
            name="场景策略",
            description="按场景分类归档"
        )
        self.scenes_to_archive = scenes_to_archive or ["S0", "S1"]  # 默认归档简单场景
        self.scenes_to_preserve = scenes_to_preserve or ["S8", "S9"]  # 默认保留高级场景
    
    def should_archive(self, memory_entry: Dict) -> bool:
        scene = memory_entry.get("scene")
        if not scene:
            return False
        
        # 保留的场景不归档
        if scene in self.scenes_to_preserve:
            return False
        
        # 指定要归档的场景
        return scene in self.scenes_to_archive
    
    def get_stats(self) -> Dict:
        stats = super().get_stats()
        stats.update({
            "scenes_to_archive": self.scenes_to_archive,
            "scenes_to_preserve": self.scenes_to_preserve
        })
        return stats


class CompositePolicy(ArchivePolicy):
    """组合策略（多个策略的组合）"""
    
    def __init__(self, policies: List[ArchivePolicy], 
                 logic: str = "any"):
        """
        Args:
            policies: 策略列表
            logic: 组合逻辑 ("any": 任一策略匹配即归档, "all": 所有策略匹配才归档)
        """
        policy_names = [p.name for p in policies]
        super().__init__(
            name="组合策略",
            description=f"{logic}逻辑组合: {', '.join(policy_names)}"
        )
        self.policies = policies
        self.logic = logic
    
    def should_archive(self, memory_entry: Dict) -> bool:
        if not self.policies:
            return False
        
        results = [p.should_archive(memory_entry) for p in self.policies]
        
        if self.logic == "any":
            return any(results)
        elif self.logic == "all":
            return all(results)
        else:
            return any(results)  # 默认any
    
    def get_stats(self) -> Dict:
        stats = super().get_stats()
        stats.update({
            "logic": self.logic,
            "sub_policies": [p.get_stats() for p in self.policies]
        })
        return stats


class AutoArchiver:
    """自动归档管理器"""
    
    def __init__(self, memory_system: Optional[ExtendedMemorySystem] = None,
                 config_path: Optional[str] = None):
        self.memory = memory_system or ExtendedMemorySystem()
        self.policies = []
        self.archive_dir = self.memory._layer_path("archive")
        self.load_config(config_path)
    
    def load_config(self, config_path: Optional[str] = None):
        """加载配置文件"""
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                self._create_policies_from_config(config)
            except Exception as e:
                print(f"⚠️  配置文件加载失败: {e}")
                self._create_default_policies()
        else:
            self._create_default_policies()
    
    def _create_default_policies(self):
        """创建默认策略"""
        # 默认策略组合
        time_policy = TimeBasedPolicy(days_threshold=30)
        importance_policy = ImportanceBasedPolicy(importance_threshold=3)
        access_policy = AccessFrequencyPolicy(min_access_count=1, days_without_access=90)
        
        # 组合策略：时间超过30天 AND 重要性低于3
        composite = CompositePolicy(
            policies=[time_policy, importance_policy],
            logic="all"
        )
        
        self.policies = [composite, access_policy]
    
    def _create_policies_from_config(self, config: Dict):
        """从配置创建策略"""
        self.policies = []
        
        for policy_config in config.get("policies", []):
            policy_type = policy_config.get("type")
            params = policy_config.get("params", {})
            
            if policy_type == "time":
                policy = TimeBasedPolicy(**params)
            elif policy_type == "importance":
                policy = ImportanceBasedPolicy(**params)
            elif policy_type == "access":
                policy = AccessFrequencyPolicy(**params)
            elif policy_type == "scene":
                policy = SceneBasedPolicy(**params)
            elif policy_type == "composite":
                sub_policies = []
                for sub_config in params.get("sub_policies", []):
                    sub_policy = self._create_single_policy(sub_config)
                    if sub_policy:
                        sub_policies.append(sub_policy)
                policy = CompositePolicy(
                    policies=sub_policies,
                    logic=params.get("logic", "any")
                )
            else:
                print(f"⚠️  未知策略类型: {policy_type}")
                continue
            
            self.policies.append(policy)
    
    def _create_single_policy(self, config: Dict) -> Optional[ArchivePolicy]:
        """创建单个策略"""
        policy_type = config.get("type")
        params = config.get("params", {})
        
        if policy_type == "time":
            return TimeBasedPolicy(**params)
        elif policy_type == "importance":
            return ImportanceBasedPolicy(**params)
        elif policy_type == "access":
            return AccessFrequencyPolicy(**params)
        elif policy_type == "scene":
            return SceneBasedPolicy(**params)
        
        return None
    
    def run_archival(self, dry_run: bool = False) -> Dict:
        """
        执行归档
        
        Args:
            dry_run: 试运行（不实际归档）
            
        Returns:
            归档统计信息
        """
        stats = {
            "total_checked": 0,
            "archived": 0,
            "preserved": 0,
            "errors": 0,
            "policy_stats": {},
            "dry_run": dry_run
        }
        
        # 遍历所有层（除了archive层）
        layers_to_check = ["soul", "user", "tools", "session", "scenes"]
        
        for layer_name in layers_to_check:
            layer_dir = self.memory._layer_path(layer_name)
            if not layer_dir.exists():
                continue
            
            for json_file in layer_dir.glob("*.json"):
                stats["total_checked"] += 1
                
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        entry = json.load(f)
                    
                    # 应用所有策略判断是否归档
                    should_archive = False
                    policy_reasons = []
                    
                    for policy in self.policies:
                        if policy.should_archive(entry):
                            should_archive = True
                            policy_reasons.append(policy.name)
                    
                    if should_archive:
                        if not dry_run:
                            # 移动到归档层
                            archive_path = self.archive_dir / json_file.name
                            entry["archived_at"] = datetime.now().isoformat()
                            entry["original_layer"] = layer_name
                            entry["archive_reasons"] = policy_reasons
                            
                            with open(archive_path, "w", encoding="utf-8") as f:
                                json.dump(entry, f, ensure_ascii=False, indent=2)
                            json_file.unlink()
                        
                        stats["archived"] += 1
                        
                        # 记录策略统计
                        for reason in policy_reasons:
                            stats["policy_stats"][reason] = stats["policy_stats"].get(reason, 0) + 1
                    else:
                        stats["preserved"] += 1
                
                except Exception as e:
                    stats["errors"] += 1
                    if not dry_run:
                        print(f"❌ 处理文件 {json_file} 时出错: {e}")
        
        # 记录策略详细信息
        stats["policies_applied"] = [p.get_stats() for p in self.policies]
        
        return stats
    
    def generate_archival_report(self, stats: Dict) -> str:
        """生成归档报告"""
        report_lines = []
        
        if stats["dry_run"]:
            report_lines.append("📋 归档试运行报告")
        else:
            report_lines.append("📋 归档执行报告")
        
        report_lines.append("=" * 50)
        report_lines.append(f"检查总数: {stats['total_checked']}")
        report_lines.append(f"归档数量: {stats['archived']}")
        report_lines.append(f"保留数量: {stats['preserved']}")
        report_lines.append(f"错误数量: {stats['errors']}")
        
        if stats["policy_stats"]:
            report_lines.append("\n策略归档统计:")
            for policy_name, count in stats["policy_stats"].items():
                report_lines.append(f"  {policy_name}: {count} 条")
        
        report_lines.append("\n应用的策略:")
        for policy in stats.get("policies_applied", []):
            report_lines.append(f"  • {policy['name']} ({policy['type']})")
            if "days_threshold" in policy:
                report_lines.append(f"    时间阈值: {policy['days_threshold']} 天")
            if "importance_threshold" in policy:
                report_lines.append(f"    重要性阈值: {policy['importance_threshold']}")
        
        return "\n".join(report_lines)
    
    def save_config(self, config_path: str):
        """保存配置到文件"""
        config = {
            "policies": []
        }
        
        for policy in self.policies:
            policy_config = {
                "type": policy.__class__.__name__.replace("Policy", "").lower(),
                "params": {}
            }
            
            # 根据策略类型提取参数
            if isinstance(policy, TimeBasedPolicy):
                policy_config["params"] = {
                    "days_threshold": policy.days_threshold,
                    "exclude_layers": policy.exclude_layers
                }
            elif isinstance(policy, ImportanceBasedPolicy):
                policy_config["params"] = {
                    "importance_threshold": policy.importance_threshold,
                    "exclude_scenes": policy.exclude_scenes
                }
            elif isinstance(policy, AccessFrequencyPolicy):
                policy_config["params"] = {
                    "min_access_count": policy.min_access_count,
                    "days_without_access": policy.days_without_access
                }
            elif isinstance(policy, SceneBasedPolicy):
                policy_config["params"] = {
                    "scenes_to_archive": policy.scenes_to_archive,
                    "scenes_to_preserve": policy.scenes_to_preserve
                }
            elif isinstance(policy, CompositePolicy):
                # 简化：不保存组合策略的子策略
                policy_config["params"] = {
                    "logic": policy.logic,
                    "sub_policies": []
                }
            
            config["policies"].append(policy_config)
        
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, allow_unicode=True, indent=2)


# ============================================================
# CLI 接口
# ============================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="自动压缩归档管理器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python auto_archiver.py run --dry-run
  python auto_archiver.py run
  python auto_archiver.py config --save config.yaml
  python auto_archiver.py config --load config.yaml
  python auto_archiver.py stats
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # run
    p_run = subparsers.add_parser("run", help="执行归档")
    p_run.add_argument("--dry-run", action="store_true", help="试运行（不实际归档）")
    p_run.add_argument("--config", help="配置文件路径")
    
    # config
    p_config = subparsers.add_parser("config", help="配置管理")
    p_config.add_argument("--save", help="保存配置到文件")
    p_config.add_argument("--load", help="从文件加载配置")
    
    # stats
    p_stats = subparsers.add_parser("stats", help="查看归档统计")
    
    args = parser.parse_args()
    
    archiver = AutoArchiver(config_path=args.config if hasattr(args, "config") and args.config else None)
    
    if args.command == "run":
        stats = archiver.run_archival(dry_run=args.dry_run)
        report = archiver.generate_archival_report(stats)
        print(report)
        
        if args.dry_run:
            print("\n💡 这是试运行，未实际归档任何记忆。")
        else:
            print(f"\n✅ 归档完成！归档了 {stats['archived']} 条记忆。")
    
    elif args.command == "config":
        if args.save:
            archiver.save_config(args.save)
            print(f"✅ 配置已保存到: {args.save}")
        elif args.load:
            archiver.load_config(args.load)
            print(f"✅ 配置已从 {args.load} 加载")
            print(f"   加载了 {len(archiver.policies)} 个策略")
        else:
            print("当前策略配置:")
            for i, policy in enumerate(archiver.policies, 1):
                print(f"\n  [{i}] {policy.name}")
                print(f"      类型: {policy.__class__.__name__}")
                print(f"      描述: {policy.description}")
    
    elif args.command == "stats":
        # 获取归档层统计
        archive_dir = archiver.archive_dir
        if archive_dir.exists():
            archive_count = len(list(archive_dir.glob("*.json")))
            print(f"📦 归档层统计:")
            print(f"   归档记忆总数: {archive_count}")
            
            # 按原始层统计
            layer_stats = {}
            for json_file in archive_dir.glob("*.json"):
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        entry = json.load(f)
                    original_layer = entry.get("original_layer", "unknown")
                    layer_stats[original_layer] = layer_stats.get(original_layer, 0) + 1
                except:
                    pass
            
            if layer_stats:
                print("\n   按原始层分布:")
                for layer, count in layer_stats.items():
                    print(f"     {layer}: {count} 条")
        else:
            print("📦 归档层为空")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()