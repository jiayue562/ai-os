#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技能调用历史管理器
记录和分析WorkBuddy技能调用情况

功能:
1. 记录技能调用（成功/失败）
2. 统计技能使用频率和性能
3. 分析技能调用模式
4. 提供优化建议

版本: 1.0.0
开发者: 龙龟神将
用户: 悟空
"""

import json
import time
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from .memory_manager import ExtendedMemorySystem


class SkillHistoryManager:
    """技能调用历史管理器"""
    
    def __init__(self, memory_system: Optional[ExtendedMemorySystem] = None):
        self.memory = memory_system or ExtendedMemorySystem()
        self._cache = {}  # 缓存常用统计结果
    
    def record_skill_call(self, skill_name: str, skill_params: Dict,
                         result: Any, execution_time: float,
                         success: bool = True, error_msg: Optional[str] = None) -> str:
        """
        记录技能调用
        
        Args:
            skill_name: 技能名称
            skill_params: 技能参数
            result: 执行结果
            execution_time: 执行时间（秒）
            success: 是否成功
            error_msg: 错误信息
            
        Returns:
            memory_id: 记录ID
        """
        # 清除缓存
        self._cache.clear()
        
        return self.memory.store_skill_history(
            skill_name=skill_name,
            skill_params=skill_params,
            result=result,
            execution_time=execution_time,
            success=success,
            error_msg=error_msg
        )
    
    def get_skill_stats(self, skill_name: Optional[str] = None,
                       days: int = 30) -> Dict:
        """
        获取技能统计信息
        
        Args:
            skill_name: 技能名称（None表示所有技能）
            days: 统计天数
            
        Returns:
            统计信息字典
        """
        cache_key = f"stats_{skill_name}_{days}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        cutoff_date = datetime.now() - timedelta(days=days)
        all_records = self.memory.search_skill_history(
            skill_name=skill_name,
            limit=1000  # 获取足够多的记录
        )
        
        # 按技能名称分组
        skill_data = {}
        
        for record in all_records:
            created_at = datetime.fromisoformat(record.get("created_at", datetime.now().isoformat()))
            if created_at < cutoff_date:
                continue
            
            skill_ctx = record.get("skill_context", {})
            s_name = skill_ctx.get("skill_name", "unknown")
            
            if s_name not in skill_data:
                skill_data[s_name] = {
                    "total_calls": 0,
                    "success_calls": 0,
                    "failed_calls": 0,
                    "total_time": 0.0,
                    "execution_times": [],
                    "last_call": None,
                    "error_messages": []
                }
            
            data = skill_data[s_name]
            data["total_calls"] += 1
            data["total_time"] += skill_ctx.get("execution_time", 0)
            data["execution_times"].append(skill_ctx.get("execution_time", 0))
            
            if skill_ctx.get("success", True):
                data["success_calls"] += 1
            else:
                data["failed_calls"] += 1
                if "error_msg" in skill_ctx:
                    data["error_messages"].append(skill_ctx["error_msg"])
            
            # 更新最后调用时间
            if not data["last_call"] or created_at > datetime.fromisoformat(data["last_call"]):
                data["last_call"] = record["created_at"]
        
        # 计算衍生统计
        result = {}
        for s_name, data in skill_data.items():
            if data["total_calls"] == 0:
                continue
            
            avg_time = data["total_time"] / data["total_calls"]
            success_rate = data["success_calls"] / data["total_calls"] * 100
            
            # 计算时间统计
            if data["execution_times"]:
                time_stats = {
                    "avg": avg_time,
                    "min": min(data["execution_times"]),
                    "max": max(data["execution_times"]),
                    "median": statistics.median(data["execution_times"]) if len(data["execution_times"]) > 1 else avg_time,
                    "std": statistics.stdev(data["execution_times"]) if len(data["execution_times"]) > 1 else 0,
                }
            else:
                time_stats = {"avg": 0, "min": 0, "max": 0, "median": 0, "std": 0}
            
            result[s_name] = {
                "total_calls": data["total_calls"],
                "success_rate": success_rate,
                "success_calls": data["success_calls"],
                "failed_calls": data["failed_calls"],
                "time_stats": time_stats,
                "last_call": data["last_call"],
                "common_errors": self._extract_common_errors(data["error_messages"]),
                "call_frequency": self._calculate_frequency(data["total_calls"], days),
            }
        
        self._cache[cache_key] = result
        return result
    
    def _extract_common_errors(self, error_messages: List[str]) -> List[Tuple[str, int]]:
        """提取常见错误"""
        if not error_messages:
            return []
        
        error_counts = {}
        for error in error_messages:
            error_counts[error] = error_counts.get(error, 0) + 1
        
        # 按频率排序
        sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_errors[:5]  # 返回前5个常见错误
    
    def _calculate_frequency(self, total_calls: int, days: int) -> str:
        """计算调用频率"""
        if days == 0:
            return "N/A"
        
        calls_per_day = total_calls / days
        if calls_per_day >= 10:
            return "极高"
        elif calls_per_day >= 5:
            return "高"
        elif calls_per_day >= 1:
            return "中等"
        elif calls_per_day >= 0.1:
            return "低"
        else:
            return "极低"
    
    def get_skill_performance_trend(self, skill_name: str, 
                                   days: int = 30) -> Dict[str, List[float]]:
        """
        获取技能性能趋势（按天）
        
        Args:
            skill_name: 技能名称
            days: 天数
            
        Returns:
            趋势数据 {dates: [], success_rates: [], avg_times: []}
        """
        records = self.memory.search_skill_history(
            skill_name=skill_name,
            limit=1000
        )
        
        # 按日期分组
        daily_data = {}
        for record in records:
            created_at = datetime.fromisoformat(record.get("created_at", datetime.now().isoformat()))
            date_str = created_at.strftime("%Y-%m-%d")
            
            if date_str not in daily_data:
                daily_data[date_str] = {
                    "total": 0,
                    "success": 0,
                    "total_time": 0.0,
                    "times": []
                }
            
            data = daily_data[date_str]
            data["total"] += 1
            skill_ctx = record.get("skill_context", {})
            if skill_ctx.get("success", True):
                data["success"] += 1
            
            exec_time = skill_ctx.get("execution_time", 0)
            data["total_time"] += exec_time
            data["times"].append(exec_time)
        
        # 按日期排序
        sorted_dates = sorted(daily_data.keys())[-days:]  # 最近N天
        
        dates = []
        success_rates = []
        avg_times = []
        
        for date_str in sorted_dates:
            data = daily_data[date_str]
            if data["total"] > 0:
                success_rate = data["success"] / data["total"] * 100
                avg_time = data["total_time"] / data["total"]
            else:
                success_rate = 0
                avg_time = 0
            
            dates.append(date_str)
            success_rates.append(success_rate)
            avg_times.append(avg_time)
        
        return {
            "dates": dates,
            "success_rates": success_rates,
            "avg_times": avg_times
        }
    
    def get_skill_recommendations(self) -> List[Dict]:
        """
        获取技能使用优化建议
        
        Returns:
            建议列表
        """
        stats = self.get_skill_stats(days=30)
        recommendations = []
        
        for skill_name, data in stats.items():
            # 建议1: 高频失败技能
            if data["failed_calls"] > 5 and data["success_rate"] < 50:
                recommendations.append({
                    "skill": skill_name,
                    "type": "高频失败",
                    "priority": "高",
                    "message": f"技能 '{skill_name}' 失败率较高 ({100-data['success_rate']:.1f}%)，建议检查参数配置或技能状态",
                    "data": {
                        "success_rate": data["success_rate"],
                        "failed_calls": data["failed_calls"],
                        "common_errors": data["common_errors"]
                    }
                })
            
            # 建议2: 性能低下技能
            avg_time = data["time_stats"]["avg"]
            if avg_time > 10.0:  # 超过10秒
                recommendations.append({
                    "skill": skill_name,
                    "type": "性能低下",
                    "priority": "中",
                    "message": f"技能 '{skill_name}' 平均执行时间较长 ({avg_time:.1f}秒)，建议优化或考虑替代方案",
                    "data": {"avg_time": avg_time}
                })
            
            # 建议3: 低频使用但有价值的技能
            if data["call_frequency"] in ["极低", "低"] and data["success_rate"] > 90:
                recommendations.append({
                    "skill": skill_name,
                    "type": "低频率用",
                    "priority": "低",
                    "message": f"技能 '{skill_name}' 使用频率较低但成功率很高，可考虑更广泛应用",
                    "data": {
                        "call_frequency": data["call_frequency"],
                        "success_rate": data["success_rate"]
                    }
                })
        
        # 按优先级排序
        priority_order = {"高": 0, "中": 1, "低": 2}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))
        
        return recommendations
    
    def export_skill_history(self, output_format: str = "json",
                            skill_name: Optional[str] = None) -> str:
        """
        导出技能调用历史
        
        Args:
            output_format: 输出格式 (json, csv)
            skill_name: 技能名称过滤
            
        Returns:
            导出文件路径
        """
        records = self.memory.search_skill_history(
            skill_name=skill_name,
            limit=10000
        )
        
        export_dir = Path(__file__).parent / "exports"
        export_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        skill_suffix = f"_{skill_name}" if skill_name else "_all"
        
        if output_format == "json":
            file_path = export_dir / f"skill_history{skill_suffix}_{timestamp}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
        
        elif output_format == "csv":
            file_path = export_dir / f"skill_history{skill_suffix}_{timestamp}.csv"
            # 简化的CSV导出
            import csv
            with open(file_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["时间", "技能名称", "参数", "执行时间(s)", "成功", "错误信息"])
                
                for record in records:
                    skill_ctx = record.get("skill_context", {})
                    writer.writerow([
                        record.get("created_at", ""),
                        skill_ctx.get("skill_name", ""),
                        json.dumps(skill_ctx.get("skill_params", {}), ensure_ascii=False),
                        skill_ctx.get("execution_time", 0),
                        skill_ctx.get("success", True),
                        skill_ctx.get("error_msg", "")
                    ])
        else:
            raise ValueError(f"不支持的格式: {output_format}")
        
        return str(file_path)
    
    def clear_old_records(self, days_old: int = 90) -> Dict:
        """
        清理旧记录（保留统计摘要）
        
        Args:
            days_old: 保留天数
            
        Returns:
            清理统计
        """
        cutoff_date = datetime.now() - timedelta(days=days_old)
        tools_dir = Path(__file__).parent.parent / "memory" / "tools"
        
        if not tools_dir.exists():
            return {"deleted": 0, "kept": 0}
        
        deleted = 0
        kept = 0
        
        for json_file in tools_dir.glob("*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    record = json.load(f)
                
                created_at = datetime.fromisoformat(record.get("created_at", datetime.now().isoformat()))
                
                # 保留重要记录或新记录
                importance = record.get("importance", 5)
                if created_at < cutoff_date and importance < 7:
                    json_file.unlink()
                    deleted += 1
                else:
                    kept += 1
            
            except Exception:
                continue
        
        # 清除缓存
        self._cache.clear()
        
        return {"deleted": deleted, "kept": kept}


# ============================================================
# CLI 接口
# ============================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="技能调用历史管理器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python skill_history.py stats --skill 龙心OS --days 30
  python skill_history.py trend --skill 龙脑OS --days 14
  python skill_history.py recommendations
  python skill_history.py export --format json --skill 龙爪OS
  python skill_history.py clean --days 90
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # stats
    p_stats = subparsers.add_parser("stats", help="技能统计")
    p_stats.add_argument("--skill", help="技能名称")
    p_stats.add_argument("--days", type=int, default=30, help="统计天数")
    
    # trend
    p_trend = subparsers.add_parser("trend", help="性能趋势")
    p_trend.add_argument("--skill", required=True, help="技能名称")
    p_trend.add_argument("--days", type=int, default=30, help="天数")
    
    # recommendations
    subparsers.add_parser("recommendations", help="优化建议")
    
    # export
    p_export = subparsers.add_parser("export", help="导出历史")
    p_export.add_argument("--format", choices=["json", "csv"], default="json", help="输出格式")
    p_export.add_argument("--skill", help="技能名称")
    
    # clean
    p_clean = subparsers.add_parser("clean", help="清理旧记录")
    p_clean.add_argument("--days", type=int, default=90, help="保留天数")
    
    args = parser.parse_args()
    
    manager = SkillHistoryManager()
    
    if args.command == "stats":
        stats = manager.get_skill_stats(skill_name=args.skill, days=args.days)
        if not stats:
            print("📊 暂无技能调用统计")
            return
        
        print(f"📊 技能调用统计 (最近{args.days}天):\n")
        for skill_name, data in stats.items():
            print(f"  🔧 {skill_name}:")
            print(f"     调用次数: {data['total_calls']} | 成功率: {data['success_rate']:.1f}%")
            print(f"     平均时间: {data['time_stats']['avg']:.2f}s | 频率: {data['call_frequency']}")
            print(f"     最后调用: {data['last_call'][:19] if data['last_call'] else '无'}")
            if data['common_errors']:
                print(f"     常见错误: {data['common_errors'][0][0]}")
            print()
    
    elif args.command == "trend":
        trend = manager.get_skill_performance_trend(skill_name=args.skill, days=args.days)
        if not trend["dates"]:
            print(f"📈 技能 '{args.skill}' 无趋势数据")
            return
        
        print(f"📈 技能 '{args.skill}' 性能趋势 (最近{args.days}天):\n")
        print("  日期        成功率(%)  平均时间(s)")
        print("  ----------  ---------  ----------")
        for date_str, success_rate, avg_time in zip(trend["dates"], trend["success_rates"], trend["avg_times"]):
            print(f"  {date_str}  {success_rate:9.1f}  {avg_time:10.2f}")
    
    elif args.command == "recommendations":
        recommendations = manager.get_skill_recommendations()
        if not recommendations:
            print("💡 暂无优化建议")
            return
        
        print("💡 技能使用优化建议:\n")
        for i, rec in enumerate(recommendations, 1):
            priority_icon = "🔴" if rec["priority"] == "高" else "🟡" if rec["priority"] == "中" else "🟢"
            print(f"  [{i}] {priority_icon} {rec['priority']}优先级 - {rec['type']}")
            print(f"      技能: {rec['skill']}")
            print(f"      建议: {rec['message']}")
            print()
    
    elif args.command == "export":
        file_path = manager.export_skill_history(output_format=args.format, skill_name=args.skill)
        print(f"📤 技能调用历史已导出: {file_path}")
    
    elif args.command == "clean":
        result = manager.clear_old_records(days_old=args.days)
        print(f"🗑️  清理完成: 删除 {result['deleted']} 条，保留 {result['kept']} 条")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()