#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIOS 资源监控器
监控系统资源使用情况

版本：v1.0
创建：2026-04-22
"""

import time
import threading
import psutil
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class ResourceStats:
    """资源统计"""
    timestamp: datetime
    cpu_percent: float
    cpu_count: int
    memory_total: float  # MB
    memory_available: float  # MB
    memory_percent: float
    disk_usage: Dict[str, Dict[str, float]]  # 磁盘使用情况
    network_io: Dict[str, Dict[str, float]]  # 网络IO
    process_count: int
    load_average: Optional[List[float]] = None  # 系统负载（Linux/Mac）


class ResourceMonitor:
    """资源监控器"""
    
    def __init__(self, update_interval: int = 5):
        """初始化资源监控器
        
        Args:
            update_interval: 更新间隔（秒）
        """
        self.update_interval = update_interval
        self.current_stats: Optional[ResourceStats] = None
        self.history: List[ResourceStats] = []
        self.max_history = 1000  # 最大历史记录数
        
        self.monitor_thread = None
        self.monitoring = False
        
        print(f"资源监控器初始化完成，更新间隔: {update_interval}秒")
    
    def start(self) -> bool:
        """启动资源监控器"""
        if self.monitoring:
            print("资源监控器已经在运行中")
            return True
        
        print("启动资源监控器...")
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        print("资源监控器启动成功")
        return True
    
    def stop(self) -> bool:
        """停止资源监控器"""
        if not self.monitoring:
            print("资源监控器未运行")
            return True
        
        print("停止资源监控器...")
        self.monitoring = False
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        print("资源监控器已停止")
        return True
    
    def get_current_stats(self) -> Optional[Dict[str, Any]]:
        """获取当前资源统计
        
        Returns:
            Dict: 当前资源统计，如果不可用则返回None
        """
        if not self.current_stats:
            # 如果没有监控数据，获取一次即时数据
            return self._collect_stats()
        
        return self._stats_to_dict(self.current_stats)
    
    def get_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取历史资源统计
        
        Args:
            limit: 返回的记录数量限制
            
        Returns:
            List[Dict]: 历史资源统计列表
        """
        start_idx = max(0, len(self.history) - limit)
        recent_history = self.history[start_idx:]
        
        return [self._stats_to_dict(stats) for stats in recent_history]
    
    def _monitor_loop(self) -> None:
        """监控循环"""
        print("资源监控循环开始")
        
        while self.monitoring:
            try:
                # 收集资源统计
                stats = self._collect_stats()
                
                # 更新当前统计
                self.current_stats = stats
                
                # 添加到历史记录
                self.history.append(stats)
                
                # 限制历史记录大小
                if len(self.history) > self.max_history:
                    self.history = self.history[-self.max_history:]
                
                # 休眠一段时间
                time.sleep(self.update_interval)
                
            except Exception as e:
                print(f"资源监控异常: {e}")
                time.sleep(10)
        
        print("资源监控循环结束")
    
    def _collect_stats(self) -> ResourceStats:
        """收集资源统计
        
        Returns:
            ResourceStats: 资源统计
        """
        try:
            # CPU信息
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()
            
            # 内存信息
            memory = psutil.virtual_memory()
            memory_total_mb = memory.total / (1024 * 1024)
            memory_available_mb = memory.available / (1024 * 1024)
            memory_percent = memory.percent
            
            # 磁盘信息
            disk_usage = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.mountpoint] = {
                        "total_gb": usage.total / (1024**3),
                        "used_gb": usage.used / (1024**3),
                        "free_gb": usage.free / (1024**3),
                        "percent": usage.percent
                    }
                except Exception as e:
                    print(f"磁盘监控失败 {partition.mountpoint}: {e}")
            
            # 网络IO
            network_io = {}
            net_io_counters = psutil.net_io_counters()
            network_io["total"] = {
                "bytes_sent": net_io_counters.bytes_sent,
                "bytes_recv": net_io_counters.bytes_recv,
                "packets_sent": net_io_counters.packets_sent,
                "packets_recv": net_io_counters.packets_recv
            }
            
            # 进程数量
            process_count = len(psutil.pids())
            
            # 系统负载（Linux/Mac）
            load_average = None
            try:
                load_average = psutil.getloadavg()
            except AttributeError:
                # Windows不支持getloadavg
                pass
            
            return ResourceStats(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                cpu_count=cpu_count,
                memory_total=memory_total_mb,
                memory_available=memory_available_mb,
                memory_percent=memory_percent,
                disk_usage=disk_usage,
                network_io=network_io,
                process_count=process_count,
                load_average=load_average
            )
            
        except Exception as e:
            print(f"资源收集失败: {e}")
            # 返回一个默认的统计对象
            return ResourceStats(
                timestamp=datetime.now(),
                cpu_percent=0.0,
                cpu_count=1,
                memory_total=1024.0,
                memory_available=512.0,
                memory_percent=50.0,
                disk_usage={},
                network_io={},
                process_count=0
            )
    
    def _stats_to_dict(self, stats: ResourceStats) -> Dict[str, Any]:
        """将ResourceStats转换为字典
        
        Args:
            stats: 资源统计对象
            
        Returns:
            Dict: 字典格式的资源统计
        """
        return {
            "timestamp": stats.timestamp.isoformat(),
            "cpu": {
                "percent": stats.cpu_percent,
                "count": stats.cpu_count,
                "load_average": stats.load_average
            },
            "memory": {
                "total_mb": stats.memory_total,
                "available_mb": stats.memory_available,
                "percent": stats.memory_percent,
                "used_mb": stats.memory_total * (stats.memory_percent / 100)
            },
            "disk": stats.disk_usage,
            "network": stats.network_io,
            "system": {
                "process_count": stats.process_count
            }
        }
    
    def check_resource_limits(self, limits: Dict[str, Any]) -> Dict[str, Any]:
        """检查资源限制
        
        Args:
            limits: 资源限制配置
            
        Returns:
            Dict: 检查结果
        """
        if not self.current_stats:
            return {"error": "没有可用的资源统计"}
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "all_passed": True
        }
        
        # 检查CPU限制
        cpu_limit = limits.get("cpu_percent", 80)
        if self.current_stats.cpu_percent > cpu_limit:
            results["checks"]["cpu"] = {
                "passed": False,
                "current": self.current_stats.cpu_percent,
                "limit": cpu_limit,
                "message": f"CPU使用率超过限制: {self.current_stats.cpu_percent:.1f}% > {cpu_limit}%"
            }
            results["all_passed"] = False
        else:
            results["checks"]["cpu"] = {
                "passed": True,
                "current": self.current_stats.cpu_percent,
                "limit": cpu_limit
            }
        
        # 检查内存限制
        memory_limit_mb = limits.get("memory_mb", 1024)
        memory_used_mb = self.current_stats.memory_total * (self.current_stats.memory_percent / 100)
        if memory_used_mb > memory_limit_mb:
            results["checks"]["memory"] = {
                "passed": False,
                "current_mb": memory_used_mb,
                "limit_mb": memory_limit_mb,
                "message": f"内存使用超过限制: {memory_used_mb:.1f}MB > {memory_limit_mb}MB"
            }
            results["all_passed"] = False
        else:
            results["checks"]["memory"] = {
                "passed": True,
                "current_mb": memory_used_mb,
                "limit_mb": memory_limit_mb
            }
        
        # 检查磁盘空间
        disk_limit_percent = limits.get("disk_percent", 90)
        for mount_point, disk_info in self.current_stats.disk_usage.items():
            if disk_info["percent"] > disk_limit_percent:
                results["checks"][f"disk_{mount_point}"] = {
                    "passed": False,
                    "current_percent": disk_info["percent"],
                    "limit_percent": disk_limit_percent,
                    "message": f"磁盘{mount_point}使用率超过限制: {disk_info['percent']:.1f}% > {disk_limit_percent}%"
                }
                results["all_passed"] = False
        
        return results
    
    def get_summary(self) -> Dict[str, Any]:
        """获取资源摘要
        
        Returns:
            Dict: 资源摘要
        """
        if not self.current_stats:
            return {"error": "没有可用的资源统计"}
        
        # 计算历史趋势（最近10个点）
        recent_history = self.history[-10:] if len(self.history) >= 10 else self.history
        
        cpu_trend = []
        memory_trend = []
        for stats in recent_history:
            cpu_trend.append(stats.cpu_percent)
            memory_trend.append(stats.memory_percent)
        
        return {
            "current": self._stats_to_dict(self.current_stats),
            "trends": {
                "cpu": cpu_trend,
                "memory": memory_trend
            },
            "alerts": self._generate_alerts()
        }
    
    def _generate_alerts(self) -> List[Dict[str, Any]]:
        """生成资源警报
        
        Returns:
            List[Dict]: 警报列表
        """
        alerts = []
        
        if not self.current_stats:
            return alerts
        
        # CPU警报
        if self.current_stats.cpu_percent > 90:
            alerts.append({
                "level": "critical",
                "resource": "cpu",
                "message": f"CPU使用率过高: {self.current_stats.cpu_percent:.1f}%",
                "timestamp": datetime.now().isoformat()
            })
        elif self.current_stats.cpu_percent > 80:
            alerts.append({
                "level": "warning",
                "resource": "cpu",
                "message": f"CPU使用率偏高: {self.current_stats.cpu_percent:.1f}%",
                "timestamp": datetime.now().isoformat()
            })
        
        # 内存警报
        if self.current_stats.memory_percent > 90:
            alerts.append({
                "level": "critical",
                "resource": "memory",
                "message": f"内存使用率过高: {self.current_stats.memory_percent:.1f}%",
                "timestamp": datetime.now().isoformat()
            })
        elif self.current_stats.memory_percent > 80:
            alerts.append({
                "level": "warning",
                "resource": "memory",
                "message": f"内存使用率偏高: {self.current_stats.memory_percent:.1f}%",
                "timestamp": datetime.now().isoformat()
            })
        
        # 磁盘警报
        for mount_point, disk_info in self.current_stats.disk_usage.items():
            if disk_info["percent"] > 95:
                alerts.append({
                    "level": "critical",
                    "resource": f"disk_{mount_point}",
                    "message": f"磁盘{mount_point}空间严重不足: {disk_info['percent']:.1f}%",
                    "timestamp": datetime.now().isoformat()
                })
            elif disk_info["percent"] > 90:
                alerts.append({
                    "level": "warning",
                    "resource": f"disk_{mount_point}",
                    "message": f"磁盘{mount_point}空间不足: {disk_info['percent']:.1f}%",
                    "timestamp": datetime.now().isoformat()
                })
        
        return alerts