#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIOS 核心调度器
集成龙心OS、龙脑OS、龙爪OS的统一调度引擎

版本：v1.0
创建：2026-04-22
"""

import sys
import os
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

# 添加服务路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services"))

try:
    # 尝试导入龙心OS
    from dragonheart.core import DragonHeartOS
    from dragonheart.scene_classifier import SceneClassifier
    from dragonheart.engine_router import EngineRouter
    DRAGONHEART_AVAILABLE = True
except ImportError:
    print("警告: 龙心OS模块不可用，将使用简化版本")
    DRAGONHEART_AVAILABLE = False

try:
    # 尝试导入龙脑OS（如果存在）
    # 这里需要根据实际模块结构调整
    DRAGONBRAIN_AVAILABLE = False
except ImportError:
    DRAGONBRAIN_AVAILABLE = False

try:
    # 尝试导入龙爪OS（如果存在）
    # 这里需要根据实际模块结构调整
    DRAGONCLAW_AVAILABLE = False
except ImportError:
    DRAGONCLAW_AVAILABLE = False


class ServiceStatus(Enum):
    """服务状态"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


class ProcessPriority(Enum):
    """进程优先级"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ServiceInfo:
    """服务信息"""
    name: str
    display_name: str
    version: str
    status: ServiceStatus
    pid: Optional[int] = None
    start_time: Optional[datetime] = None
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    dependencies: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)


class AiosScheduler:
    """AIOS 核心调度器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化AIOS调度器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        
        # 初始化组件
        self.services: Dict[str, ServiceInfo] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # 初始化龙心OS（如果可用）
        self.dragonheart = None
        if DRAGONHEART_AVAILABLE:
            try:
                self.dragonheart = DragonHeartOS()
                print("龙心OS初始化成功")
            except Exception as e:
                print(f"龙心OS初始化失败: {e}")
        
        # 初始化进程管理器
        self.process_manager = ProcessManager()
        
        # 初始化资源监控器
        self.resource_monitor = ResourceMonitor()
        
        # 服务状态
        self.running = False
        self.start_time = None
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """加载配置文件"""
        default_config = {
            "system": {
                "name": "AIOS",
                "version": "1.0.0",
                "mode": "development",
                "log_level": "INFO",
                "data_dir": str(Path.home() / ".aios"),
            },
            "services": {
                "dragonheart": {
                    "enabled": True,
                    "auto_start": True,
                    "config": {}
                },
                "dragonbrain": {
                    "enabled": False,
                    "auto_start": False,
                    "config": {}
                },
                "dragonclaw": {
                    "enabled": False,
                    "auto_start": False,
                    "config": {}
                }
            },
            "scheduler": {
                "max_processes": 10,
                "default_priority": "normal",
                "health_check_interval": 30,
                "resource_limit": {
                    "cpu_percent": 80,
                    "memory_mb": 1024
                }
            }
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # 合并配置
                    self._merge_config(default_config, user_config)
            except Exception as e:
                print(f"配置文件加载失败 {config_path}: {e}")
        
        return default_config
    
    def _merge_config(self, base: Dict, update: Dict) -> None:
        """递归合并配置"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def start(self) -> bool:
        """启动AIOS调度器"""
        if self.running:
            print("AIOS调度器已经在运行中")
            return True
        
        print("正在启动AIOS调度器...")
        self.start_time = datetime.now()
        
        try:
            # 启动资源监控
            self.resource_monitor.start()
            
            # 注册核心服务
            self._register_core_services()
            
            # 启动配置为自动启动的服务
            self._start_auto_services()
            
            self.running = True
            print(f"AIOS调度器启动成功 (启动时间: {self.start_time})")
            return True
            
        except Exception as e:
            print(f"AIOS调度器启动失败: {e}")
            return False
    
    def stop(self) -> bool:
        """停止AIOS调度器"""
        if not self.running:
            print("AIOS调度器未运行")
            return True
        
        print("正在停止AIOS调度器...")
        
        try:
            # 停止所有服务
            for service_name in list(self.services.keys()):
                self.stop_service(service_name)
            
            # 停止资源监控
            self.resource_monitor.stop()
            
            self.running = False
            print("AIOS调度器已停止")
            return True
            
        except Exception as e:
            print(f"AIOS调度器停止失败: {e}")
            return False
    
    def _register_core_services(self) -> None:
        """注册核心服务"""
        # 注册龙心OS服务
        if self.config["services"]["dragonheart"]["enabled"] and self.dragonheart:
            self.register_service(
                name="dragonheart",
                display_name="龙心OS",
                version="1.0",
                dependencies=[],
                config=self.config["services"]["dragonheart"]["config"]
            )
        
        # TODO: 注册龙脑OS服务
        # TODO: 注册龙爪OS服务
        
        # 注册系统服务
        self.register_service(
            name="system_monitor",
            display_name="系统监控",
            version="1.0",
            dependencies=[],
            config={}
        )
    
    def _start_auto_services(self) -> None:
        """启动自动启动的服务"""
        for service_name, service_config in self.config["services"].items():
            if service_config.get("enabled", False) and service_config.get("auto_start", False):
                self.start_service(service_name)
    
    def register_service(self, name: str, display_name: str, version: str,
                         dependencies: List[str] = None, config: Dict = None) -> bool:
        """注册服务
        
        Args:
            name: 服务名称
            display_name: 显示名称
            version: 版本号
            dependencies: 依赖服务列表
            config: 服务配置
            
        Returns:
            bool: 是否注册成功
        """
        if name in self.services:
            print(f"服务 {name} 已注册")
            return False
        
        service_info = ServiceInfo(
            name=name,
            display_name=display_name,
            version=version,
            status=ServiceStatus.STOPPED,
            dependencies=dependencies or [],
            config=config or {}
        )
        
        self.services[name] = service_info
        print(f"服务注册成功: {display_name} ({name}) v{version}")
        return True
    
    def start_service(self, service_name: str) -> bool:
        """启动服务
        
        Args:
            service_name: 服务名称
            
        Returns:
            bool: 是否启动成功
        """
        if service_name not in self.services:
            print(f"服务 {service_name} 未注册")
            return False
        
        service = self.services[service_name]
        
        if service.status == ServiceStatus.RUNNING:
            print(f"服务 {service_name} 已经在运行中")
            return True
        
        # 检查依赖
        for dep_name in service.dependencies:
            if dep_name not in self.services:
                print(f"依赖服务 {dep_name} 未注册")
                return False
            if self.services[dep_name].status != ServiceStatus.RUNNING:
                print(f"依赖服务 {dep_name} 未运行")
                return False
        
        print(f"正在启动服务: {service.display_name}")
        service.status = ServiceStatus.STARTING
        
        try:
            # 根据服务类型执行不同的启动逻辑
            if service_name == "dragonheart":
                # 龙心OS服务已初始化，只需标记为运行
                service.status = ServiceStatus.RUNNING
                service.start_time = datetime.now()
                print(f"服务启动成功: {service.display_name}")
                return True
                
            elif service_name == "system_monitor":
                # 系统监控服务
                service.status = ServiceStatus.RUNNING
                service.start_time = datetime.now()
                print(f"服务启动成功: {service.display_name}")
                return True
                
            else:
                # 其他服务
                print(f"未知服务类型: {service_name}")
                service.status = ServiceStatus.ERROR
                return False
                
        except Exception as e:
            print(f"服务启动失败 {service_name}: {e}")
            service.status = ServiceStatus.ERROR
            return False
    
    def stop_service(self, service_name: str) -> bool:
        """停止服务
        
        Args:
            service_name: 服务名称
            
        Returns:
            bool: 是否停止成功
        """
        if service_name not in self.services:
            print(f"服务 {service_name} 未注册")
            return False
        
        service = self.services[service_name]
        
        if service.status in [ServiceStatus.STOPPED, ServiceStatus.STOPPING]:
            print(f"服务 {service_name} 已停止或正在停止")
            return True
        
        print(f"正在停止服务: {service.display_name}")
        service.status = ServiceStatus.STOPPING
        
        try:
            # 根据服务类型执行不同的停止逻辑
            if service_name == "dragonheart":
                # 龙心OS服务
                service.status = ServiceStatus.STOPPED
                service.start_time = None
                print(f"服务停止成功: {service.display_name}")
                return True
                
            else:
                service.status = ServiceStatus.STOPPED
                service.start_time = None
                print(f"服务停止成功: {service.display_name}")
                return True
                
        except Exception as e:
            print(f"服务停止失败 {service_name}: {e}")
            service.status = ServiceStatus.ERROR
            return False
    
    def process_input(self, input_text: str, context: Dict = None) -> Dict[str, Any]:
        """处理用户输入（集成龙心OS功能）
        
        Args:
            input_text: 用户输入文本
            context: 上下文信息
            
        Returns:
            Dict: 处理结果
        """
        if not self.running:
            return {"error": "AIOS调度器未运行"}
        
        if not self.dragonheart:
            return {"error": "龙心OS不可用"}
        
        try:
            # 使用龙心OS处理输入
            result = self.dragonheart.process(input_text, context)
            
            # 添加AIOS特定信息
            result["aios"] = {
                "timestamp": datetime.now().isoformat(),
                "scheduler_status": "running",
                "service_count": len(self.services)
            }
            
            return result
            
        except Exception as e:
            return {"error": f"处理失败: {str(e)}"}
    
    def get_status(self) -> Dict[str, Any]:
        """获取AIOS状态
        
        Returns:
            Dict: 状态信息
        """
        running_services = []
        for service in self.services.values():
            if service.status == ServiceStatus.RUNNING:
                running_services.append(service.name)
        
        return {
            "system": {
                "name": self.config["system"]["name"],
                "version": self.config["system"]["version"],
                "mode": self.config["system"]["mode"],
                "running": self.running,
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "uptime": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
            },
            "services": {
                "total": len(self.services),
                "running": len(running_services),
                "list": [{
                    "name": s.name,
                    "display_name": s.display_name,
                    "status": s.status.value,
                    "version": s.version
                } for s in self.services.values()]
            },
            "resources": self.resource_monitor.get_current_stats() if hasattr(self, 'resource_monitor') else {},
            "dragonheart_available": DRAGONHEART_AVAILABLE,
            "dragonbrain_available": DRAGONBRAIN_AVAILABLE,
            "dragonclaw_available": DRAGONCLAW_AVAILABLE
        }
    
    def subscribe_event(self, event_type: str, handler: Callable) -> None:
        """订阅事件
        
        Args:
            event_type: 事件类型
            handler: 事件处理函数
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def publish_event(self, event_type: str, data: Any = None) -> None:
        """发布事件
        
        Args:
            event_type: 事件类型
            data: 事件数据
        """
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(event_type, data)
                except Exception as e:
                    print(f"事件处理失败 {event_type}: {e}")


# 简化版本的ProcessManager和ResourceMonitor类
class ProcessManager:
    """进程管理器（简化版本）"""
    def __init__(self):
        self.processes = {}
    
    def start_process(self, name, command, **kwargs):
        """启动进程"""
        print(f"启动进程: {name} ({command})")
        return {"name": name, "status": "running", "pid": 9999}
    
    def stop_process(self, name):
        """停止进程"""
        print(f"停止进程: {name}")
        return True


class ResourceMonitor:
    """资源监控器（简化版本）"""
    def __init__(self):
        self.running = False
    
    def start(self):
        """启动监控"""
        self.running = True
        print("资源监控器已启动")
    
    def stop(self):
        """停止监控"""
        self.running = False
        print("资源监控器已停止")
    
    def get_current_stats(self):
        """获取当前资源统计"""
        return {
            "cpu_percent": 5.5,
            "memory_mb": 128.3,
            "disk_usage": "45%",
            "timestamp": datetime.now().isoformat()
        }


# 主函数（用于测试）
def main():
    """测试AIOS调度器"""
    print("=== AIOS调度器测试 ===")
    
    # 创建调度器实例
    scheduler = AiosScheduler()
    
    # 启动调度器
    if scheduler.start():
        print("调度器启动成功")
        
        # 显示状态
        status = scheduler.get_status()
        print(f"系统状态: {status['system']}")
        print(f"服务数量: {status['services']['total']}")
        
        # 测试处理输入
        test_input = "你好，AIOS"
        result = scheduler.process_input(test_input)
        print(f"测试输入: {test_input}")
        print(f"处理结果: {result}")
        
        # 停止调度器
        scheduler.stop()
    else:
        print("调度器启动失败")


if __name__ == "__main__":
    main()