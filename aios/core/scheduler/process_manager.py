#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIOS 进程管理器
管理AIOS服务和子进程的生命周期

版本：v1.0
创建：2026-04-22
"""

import os
import time
import signal
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

from .aios_scheduler import ProcessPriority


@dataclass
class ProcessInfo:
    """进程信息"""
    name: str
    pid: int
    command: str
    args: List[str]
    start_time: datetime
    priority: ProcessPriority
    status: str  # running, stopped, error
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    stdout_file: Optional[str] = None
    stderr_file: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ProcessManager:
    """进程管理器"""
    
    def __init__(self, log_dir: Optional[str] = None):
        """初始化进程管理器
        
        Args:
            log_dir: 日志目录路径
        """
        self.processes: Dict[str, ProcessInfo] = {}
        self.log_dir = log_dir or str(Path.home() / ".aios" / "logs")
        
        # 确保日志目录存在
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)
        
        # 监控线程
        self.monitor_thread = None
        self.monitoring = False
        
        print(f"进程管理器初始化完成，日志目录: {self.log_dir}")
    
    def start(self) -> bool:
        """启动进程管理器"""
        if self.monitoring:
            print("进程管理器已经在运行中")
            return True
        
        print("启动进程管理器...")
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        print("进程管理器启动成功")
        return True
    
    def stop(self) -> bool:
        """停止进程管理器"""
        if not self.monitoring:
            print("进程管理器未运行")
            return True
        
        print("停止进程管理器...")
        self.monitoring = False
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        # 停止所有管理的进程
        for process_name in list(self.processes.keys()):
            self.stop_process(process_name)
        
        print("进程管理器已停止")
        return True
    
    def start_process(self, name: str, command: str, args: List[str] = None,
                      priority: ProcessPriority = ProcessPriority.NORMAL,
                      env: Dict[str, str] = None, cwd: Optional[str] = None,
                      capture_output: bool = True) -> Optional[ProcessInfo]:
        """启动进程
        
        Args:
            name: 进程名称
            command: 命令或可执行文件路径
            args: 命令参数
            priority: 进程优先级
            env: 环境变量
            cwd: 工作目录
            capture_output: 是否捕获输出
            
        Returns:
            ProcessInfo: 进程信息，如果启动失败则返回None
        """
        if name in self.processes:
            print(f"进程 {name} 已存在")
            return self.processes[name]
        
        # 构建完整命令
        cmd_list = [command]
        if args:
            cmd_list.extend(args)
        
        # 准备输出文件
        stdout_file = None
        stderr_file = None
        if capture_output:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            stdout_file = str(Path(self.log_dir) / f"{name}_{timestamp}.stdout.log")
            stderr_file = str(Path(self.log_dir) / f"{name}_{timestamp}.stderr.log")
        
        print(f"启动进程: {name} (命令: {' '.join(cmd_list)})")
        
        try:
            # 准备子进程参数
            process_args = {
                'args': cmd_list,
                'env': env if env else os.environ.copy(),
                'cwd': cwd,
                'stdout': subprocess.PIPE if capture_output else subprocess.DEVNULL,
                'stderr': subprocess.PIPE if capture_output else subprocess.DEVNULL,
                'text': True,
                'bufsize': 1
            }
            
            # 启动进程
            proc = subprocess.Popen(**process_args)
            
            # 创建进程信息
            process_info = ProcessInfo(
                name=name,
                pid=proc.pid,
                command=command,
                args=args or [],
                start_time=datetime.now(),
                priority=priority,
                status="running",
                stdout_file=stdout_file,
                stderr_file=stderr_file,
                metadata={
                    "subprocess": proc,
                    "capture_output": capture_output
                }
            )
            
            # 保存进程信息
            self.processes[name] = process_info
            
            # 启动输出捕获线程（如果需要）
            if capture_output:
                threading.Thread(
                    target=self._capture_output,
                    args=(name, proc, stdout_file, stderr_file),
                    daemon=True
                ).start()
            
            print(f"进程启动成功: {name} (PID: {proc.pid})")
            return process_info
            
        except Exception as e:
            print(f"进程启动失败 {name}: {e}")
            return None
    
    def stop_process(self, name: str, timeout: int = 10) -> bool:
        """停止进程
        
        Args:
            name: 进程名称
            timeout: 超时时间（秒）
            
        Returns:
            bool: 是否停止成功
        """
        if name not in self.processes:
            print(f"进程 {name} 不存在")
            return False
        
        process_info = self.processes[name]
        
        if process_info.status != "running":
            print(f"进程 {name} 不在运行状态: {process_info.status}")
            return True
        
        print(f"停止进程: {name} (PID: {process_info.pid})")
        
        try:
            # 获取子进程对象
            proc = process_info.metadata.get("subprocess")
            if proc:
                # 发送SIGTERM信号
                proc.terminate()
                
                # 等待进程结束
                try:
                    proc.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    # 超时后强制终止
                    print(f"进程 {name} 未在 {timeout} 秒内停止，强制终止")
                    proc.kill()
                    proc.wait()
            
            # 更新状态
            process_info.status = "stopped"
            print(f"进程停止成功: {name}")
            return True
            
        except Exception as e:
            print(f"进程停止失败 {name}: {e}")
            process_info.status = "error"
            return False
    
    def get_process(self, name: str) -> Optional[ProcessInfo]:
        """获取进程信息
        
        Args:
            name: 进程名称
            
        Returns:
            ProcessInfo: 进程信息，如果不存在则返回None
        """
        return self.processes.get(name)
    
    def list_processes(self) -> List[ProcessInfo]:
        """获取所有进程列表
        
        Returns:
            List[ProcessInfo]: 进程信息列表
        """
        return list(self.processes.values())
    
    def _capture_output(self, name: str, proc: subprocess.Popen,
                        stdout_file: str, stderr_file: str) -> None:
        """捕获进程输出到文件
        
        Args:
            name: 进程名称
            proc: 子进程对象
            stdout_file: 标准输出文件路径
            stderr_file: 标准错误文件路径
        """
        try:
            # 写入标准输出
            if proc.stdout and stdout_file:
                with open(stdout_file, 'w', encoding='utf-8') as f:
                    for line in iter(proc.stdout.readline, ''):
                        f.write(line)
                        f.flush()
            
            # 写入标准错误
            if proc.stderr and stderr_file:
                with open(stderr_file, 'w', encoding='utf-8') as f:
                    for line in iter(proc.stderr.readline, ''):
                        f.write(line)
                        f.flush()
                        
        except Exception as e:
            print(f"输出捕获失败 {name}: {e}")
    
    def _monitor_loop(self) -> None:
        """监控循环"""
        print("进程监控循环开始")
        
        while self.monitoring:
            try:
                # 检查所有进程状态
                for name, process_info in list(self.processes.items()):
                    if process_info.status == "running":
                        proc = process_info.metadata.get("subprocess")
                        if proc and proc.poll() is not None:
                            # 进程已结束
                            returncode = proc.returncode
                            if returncode == 0:
                                print(f"进程 {name} 正常结束 (退出码: {returncode})")
                                process_info.status = "stopped"
                            else:
                                print(f"进程 {name} 异常结束 (退出码: {returncode})")
                                process_info.status = "error"
                
                # 更新资源使用情况（简化版本）
                for process_info in self.processes.values():
                    if process_info.status == "running":
                        # 这里可以添加实际的资源监控逻辑
                        process_info.cpu_usage = 0.0
                        process_info.memory_usage = 0.0
                
                # 休眠一段时间
                time.sleep(5)
                
            except Exception as e:
                print(f"监控循环异常: {e}")
                time.sleep(10)
        
        print("进程监控循环结束")
    
    def get_resource_usage(self) -> Dict[str, Any]:
        """获取资源使用情况
        
        Returns:
            Dict: 资源使用统计
        """
        total_cpu = 0.0
        total_memory = 0.0
        
        for process_info in self.processes.values():
            if process_info.status == "running":
                total_cpu += process_info.cpu_usage
                total_memory += process_info.memory_usage
        
        return {
            "total_processes": len(self.processes),
            "running_processes": sum(1 for p in self.processes.values() if p.status == "running"),
            "total_cpu_percent": total_cpu,
            "total_memory_mb": total_memory,
            "timestamp": datetime.now().isoformat()
        }