"""
AI龙龟共生伙伴操作系统 (AI OS) — 系统初始化脚本
版本: 1.0.0
"""

import os, sys, json
sys.stdout.reconfigure(encoding="utf-8")


def check_environment() -> dict:
    """检查系统环境配置"""
    result = {
        "workbuddy": os.path.isdir(os.path.expanduser("~/.workbuddy")),
        "skills_dir": os.path.isdir(os.path.expanduser("~/.agents/skills")),
        "opencode_config": os.path.isfile(os.path.expanduser("~/.config/opencode/AGENTS.md")),
        "memory_system": os.path.isdir(os.path.expanduser("~/.agents/skills/agent-memory-systems")),
    }
    return result


def init_system() -> bool:
    """一键初始化系统"""
    env = check_environment()
    print("=" * 50)
    print("AI龙龟共生伙伴操作系统 v1.0.0 — 系统初始化")
    print("=" * 50)
    for k, v in env.items():
        print(f"  {k}: {'OK' if v else 'MISSING'}")
    success = all(env.values())
    print(f"\n状态: {'OK' if success else 'MISSING'} 组件缺失")
    return success


if __name__ == "__main__":
    init_system()
