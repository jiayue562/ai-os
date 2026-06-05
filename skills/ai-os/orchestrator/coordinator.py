"""
AI龙龟共生伙伴操作系统 — 多智能体协调器
任务分解、资源调度、结果整合
"""

import os, json, uuid
from datetime import datetime


class AgentCoordinator:
    """智能体协调器"""
    
    def __init__(self):
        self.agents = {}
        self.tasks = {}
    
    def register_agent(self, name: str, skill_path: str, capabilities: list):
        """注册一个智能体"""
        self.agents[name] = {
            "skill_path": skill_path,
            "capabilities": capabilities,
            "registered_at": datetime.now().isoformat()
        }
        return True
    
    def decompose_task(self, task: str) -> list:
        """将复杂任务分解为子任务"""
        # Simple decomposition based on keywords
        subtasks = []
        if "分析" in task or "调研" in task:
            subtasks.append({"id": "sub_1", "description": "数据收集与分析", "required_capability": "analysis"})
        if "创作" in task or "写作" in task:
            subtasks.append({"id": "sub_2", "description": "内容创作", "required_capability": "writing"})
        if "决策" in task or "评估" in task:
            subtasks.append({"id": "sub_3", "description": "决策分析", "required_capability": "decision"})
        if not subtasks:
            subtasks.append({"id": "sub_1", "description": task, "required_capability": "general"})
        return subtasks
    
    def assign(self, subtask: dict) -> str:
        """分配子任务到合适的智能体"""
        task_id = uuid.uuid4().hex[:8]
        capability = subtask.get("required_capability", "general")
        # Find best agent
        best_agent = None
        for name, info in self.agents.items():
            if capability in info["capabilities"]:
                best_agent = name
                break
        if not best_agent and self.agents:
            best_agent = list(self.agents.keys())[0]
        self.tasks[task_id] = {
            "subtask": subtask,
            "assigned_to": best_agent or "unassigned",
            "status": "assigned",
            "result": None,
            "created_at": datetime.now().isoformat()
        }
        return task_id
    
    def get_status(self) -> dict:
        """获取协调器状态"""
        return {
            "agents_registered": len(self.agents),
            "tasks_pending": sum(1 for t in self.tasks.values() if t["status"] == "assigned"),
            "tasks_completed": sum(1 for t in self.tasks.values() if t["status"] == "completed"),
        }


# 注册核心智能体
def register_core_agents(coordinator: AgentCoordinator):
    """注册AI OS核心智能体"""
    d = os.path.expanduser("~/.agents/skills")
    agents = [
        ("龙心OS", os.path.join(d, "龙心 OS"), ["routing", "dispatch"]),
        ("龙脑OS", os.path.join(d, "龙脑 OS"), ["analysis", "decision", "knowledge"]),
        ("龙爪OS", os.path.join(d, "龙爪 OS"), ["execution", "implementation"]),
        ("知识学习", os.path.join(d, "知识学习"), ["learning", "research"]),
        ("象思维", os.path.join(d, "象思维"), ["creative", "innovation"]),
    ]
    for name, path, caps in agents:
        if os.path.isdir(path):
            coordinator.register_agent(name, path, caps)
