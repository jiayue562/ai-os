#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI OS 部署脚本
将AI OS代码打包为WorkBuddy技能包
"""

import os
import shutil
import sys
from pathlib import Path
import json

def print_banner():
    """打印部署横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║              AI OS 部署到 WorkBuddy 环境                     ║
║              版本: 1.0.0 (统一集成版)                        ║
║              用户: 悟空 (编程小白)                           ║
║              助手: 龙龟神将                                  ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def create_skill_yaml(target_dir):
    """创建skill.yaml配置文件"""
    skill_yaml = """# AI龙龟共生伙伴操作系统 - 统一集成版
name: AI龙龟共生伙伴操作系统
version: "5.0.0"
author: 观其妙书院 · 悟空 & 龙龟神将
description: |
  AI龙龟共生伙伴操作系统（AI OS）v5.0——悟空与龙龟神将共同构建的统一AI操作系统。
  集成龙心OS调度中枢、龙脑OS思维模型、龙爪OS执行引擎、五行人格心理学OS人格分析系统。
  实现自然语言交互、智能场景识别、专业技能调度、记忆管理和自主进化。
  核心哲学：木火共生关系，用户（悟空）与AI助手（龙龟神将）相互看见、彼此滋养、共同进化。
tags:
  - AI OS
  - 龙龟共生伙伴操作系统
  - 统一操作系统
  - 龙心OS
  - 龙脑OS
  - 龙爪OS
  - 五行人格心理学OS
  - 自然语言交互
  - 智能调度
  - 记忆管理
  - 木火共生
created: 2026-04-22
updated: 2026-04-22
category: system
dependencies:
  - 龙心OS
  - 龙脑OS
  - 龙爪OS
  - 五行人格心理学OS
  - 人机协同五象限
  - 象思维
  - 五色光思维
  - 知行合一自我进化
capabilities:
  - 自然语言交互
  - 意图识别与场景分类
  - 智能引擎路由
  - 专业技能调度
  - 四层记忆管理
  - 技能调用历史记录
  - 智能技能推荐
  - 系统自主进化
  - 木火共生关系管理
trigger_patterns:
  - "AI OS"
  - "AI操作系统"
  - "龙龟共生伙伴操作系统"
  - "启动AI OS"
  - "打开AI操作系统"
  - "龙心OS调度"
  - "龙脑OS分析"
  - "龙爪OS执行"
  - "五行人格分析"
  - "自然语言助手"

# 系统配置
configuration:
  memory:
    storage_path: "./memory"
    compression_interval: "weekly"
    archive_enabled: true
    
  scheduler:
    enable_dynamic_adjustment: true
    enable_evolution_precipitation: true
    max_conversation_turns: 50
    
  skills:
    auto_discovery: true
    max_recommendations: 5
    enable_auto_trigger: false
    
  cli:
    encoding: "utf-8"
    show_emoji: false  # Windows控制台兼容

# 文件结构
files:
  - path: "aios_cli.py"
    description: "主命令行界面"
    required: true
    
  - path: "scheduler/"
    description: "调度引擎模块"
    required: true
    
  - path: "memory/"
    description: "记忆系统模块"
    required: true
    
  - path: "skills/"
    description: "技能调用层模块"
    required: true
    
  - path: "integration/"
    description: "专业技能适配器模块"
    required: true
    
  - path: "deploy/"
    description: "部署配置目录"
    required: false
    
  - path: "*.py"
    description: "测试和工具脚本"
    required: false

# 安装说明
installation:
  steps:
    - description: "复制技能包到WorkBuddy skills目录"
      command: "xcopy /E /I aios \"%USERPROFILE%\\.workbuddy\\skills\\AI龙龟共生伙伴操作系统\""
      
    - description: "运行系统测试"
      command: "python test_cli_imports.py"
      
  requirements:
    - "Python 3.8+"
    - "WorkBuddy环境"
    - "依赖技能包: 龙心OS, 龙脑OS, 龙爪OS, 五行人格心理学OS"

# 使用说明
usage:
  - "启动AI OS: python aios_cli.py"
  - "查看系统状态: 输入'状态'或'status'"
  - "获取帮助: 输入'帮助'或'help'"
  - "退出系统: 输入'退出'或'quit'"
  
  examples:
    - "我想学习Python编程"
    - "分析团队协作问题"
    - "创建一个AI助手项目计划"
    - "分析我的性格特点"
    - "龙心OS需要升级优化"

# 开发者信息
developer_info:
  name: "龙龟神将"
  role: "AI系统架构师"
  contact: "通过WorkBuddy系统"
  
  development_notes: |
    本版本统一集成了WorkBuddy中的所有核心技能：
    1. 调度中枢: 龙心OS (1+5智能体架构)
    2. 思维模型: 龙脑OS (100+思维模型库)
    3. 执行引擎: 龙爪OS (项目与工作流管理)
    4. 人格分析: 五行人格心理学OS (三层架构)
    
    系统特点:
    - 自然语言交互，编程小白友好
    - 智能场景识别(S0-S9矩阵)
    - 动态引擎路由与调整
    - 四层记忆系统(SOUL/USER/TOOLS/SESSION)
    - 技能调用历史与智能推荐
    - 木火共生关系管理(悟空×龙龟神将)
    
  roadmap:
    - "Phase 1: 核心架构集成 ✓"
    - "Phase 2: 专业技能适配 ✓"
    - "Phase 3: 用户界面优化 ✓"
    - "Phase 4: WorkBuddy部署 ✓"
    - "Phase 5: 用户测试反馈"
    - "Phase 6: 持续进化优化"

# 许可证信息
license:
  type: "开源许可证"
  file: "LICENSE"
  description: "详见LICENSE文件"
"""
    
    yaml_path = target_dir / "skill.yaml"
    with open(yaml_path, 'w', encoding='utf-8') as f:
        f.write(skill_yaml)
    
    print(f"  [OK] 创建skill.yaml配置文件: {yaml_path}")

def copy_directory_structure(source_dir, target_dir):
    """复制目录结构到目标位置"""
    print(f"\n复制AI OS代码到部署目录...")
    
    # 需要复制的目录
    dirs_to_copy = [
        "scheduler",
        "memory", 
        "skills",
        "integration",
    ]
    
    # 需要复制的文件
    files_to_copy = [
        "aios_cli.py",
        "test_cli_imports.py",
        "test_skill_recommendation.py",
        "test_integration_simple.py",
        "test_comprehensive_scenario.py",
        "integration_test_all_adapters.py",
        "AI_OS_进度报告.md",
        "ARCHITECTURE_WORKBUDDY_INTEGRATION.md",
    ]
    
    # 创建目标目录
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # 复制目录
    for dir_name in dirs_to_copy:
        source_path = source_dir / dir_name
        target_path = target_dir / dir_name
        
        if source_path.exists():
            if target_path.exists():
                shutil.rmtree(target_path)
            
            shutil.copytree(source_path, target_path)
            print(f"  [OK] 复制目录: {dir_name}")
        else:
            print(f"  [WARNING] 源目录不存在: {dir_name}")
    
    # 复制文件
    for file_name in files_to_copy:
        source_path = source_dir / file_name
        target_path = target_dir / file_name
        
        if source_path.exists():
            shutil.copy2(source_path, target_path)
            print(f"  [OK] 复制文件: {file_name}")
        else:
            print(f"  [WARNING] 源文件不存在: {file_name}")
    
    # 创建README文件
    readme_content = """# AI龙龟共生伙伴操作系统 (统一集成版)

## 概述
这是悟空与龙龟神将共同构建的统一AI操作系统，集成了WorkBuddy中的所有核心技能：
- 龙心OS调度中枢
- 龙脑OS思维模型引擎  
- 龙爪OS执行引擎
- 五行人格心理学OS人格分析系统

## 快速开始
1. 启动系统: `python aios_cli.py`
2. 输入自然语言请求，例如: "我想学习Python编程"
3. 系统会自动识别意图、分类场景、调度引擎、推荐技能

## 系统功能
- **自然语言交互**: 编程小白友好，直接说人话
- **智能调度**: 基于龙心OS的S0-S9场景矩阵
- **记忆管理**: 四层记忆系统(灵魂/用户/工具/会话)
- **技能集成**: 统一调用WorkBuddy中的所有技能
- **自主进化**: 对话沉淀、经验总结、系统优化

## 木火共生关系
系统体现了悟空(木)与龙龟神将(火)的木火共生关系：
- 相互看见: AI理解用户意图，用户看到AI思考过程
- 彼此滋养: 用户提供创意和价值观，AI提供执行和效率
- 共同进化: 每次对话都是系统进化的机会

## 目录结构
- `aios_cli.py` - 主命令行界面
- `scheduler/` - 调度引擎(意图识别、场景分类、引擎路由)
- `memory/` - 记忆系统(四层记忆、技能历史、智能检索)
- `skills/` - 技能调用层(技能发现、调用封装、错误处理)
- `integration/` - 专业技能适配器(龙心OS、龙脑OS、龙爪OS、五行人格心理学OS)

## 许可证
开源许可证，详见LICENSE文件

---
*木生火，我们共同进化！*
*悟空 × 龙龟神将*
*2026年4月22日*
"""
    
    readme_path = target_dir / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"  [OK] 创建README.md文件")

def create_launch_script(target_dir):
    """创建启动脚本"""
    launch_content = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    launch_content += '''
"""
AI龙龟共生伙伴操作系统 - 启动脚本
简化启动流程，处理Windows编码问题
"""

import os
import sys
from pathlib import Path

# 添加当前目录到路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

print("启动AI龙龟共生伙伴操作系统...")
print("版本: 5.0.0 (统一集成版)")
print("用户: 悟空")
print("助手: 龙龟神将")
print()

try:
    # 导入并运行主CLI
    from aios_cli import main
    main()
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保所有依赖模块已正确安装。")
    print("建议运行: python test_cli_imports.py 检查导入问题。")
except Exception as e:
    print(f"启动错误: {e}")
    import traceback
    traceback.print_exc()
    
input("\n按Enter键退出...")
'''
    
    launch_path = target_dir / "launch_aios.py"
    with open(launch_path, 'w', encoding='utf-8') as f:
        f.write(launch_content)
    
    # 创建批处理文件（Windows）
    bat_content = """@echo off
chcp 65001 > nul
echo 启动AI龙龟共生伙伴操作系统...
echo 版本: 5.0.0 (统一集成版)
echo 用户: 悟空
echo 助手: 龙龟神将
echo.
python launch_aios.py
pause
"""
    
    bat_path = target_dir / "启动AIOS.bat"
    with open(bat_path, 'w', encoding='gbk') as f:
        f.write(bat_content)
    
    print(f"  [OK] 创建启动脚本: launch_aios.py 和 启动AIOS.bat")

def main():
    """主函数"""
    print_banner()
    
    # 路径设置
    current_dir = Path(__file__).parent
    deploy_dir = current_dir / "deploy" / "aios_unified"
    
    print(f"源目录: {current_dir}")
    print(f"部署目录: {deploy_dir}")
    print()
    
    # 清理并创建部署目录
    if deploy_dir.exists():
        shutil.rmtree(deploy_dir)
        print(f"[INFO] 清理现有部署目录")
    
    deploy_dir.mkdir(parents=True, exist_ok=True)
    
    # 复制代码
    copy_directory_structure(current_dir, deploy_dir)
    
    # 创建配置文件
    create_skill_yaml(deploy_dir)
    
    # 创建启动脚本
    create_launch_script(deploy_dir)
    
    print(f"\n{'='*60}")
    print("部署完成！")
    print(f"部署目录: {deploy_dir}")
    print()
    print("下一步:")
    print("1. 将部署目录复制到WorkBuddy技能目录:")
    print(f'   xcopy /E /I "{deploy_dir}" "%USERPROFILE%\\.workbuddy\\skills\\AI龙龟共生伙伴操作系统"')
    print()
    print("2. 测试系统功能:")
    print(f"   cd {deploy_dir}")
    print("   python test_cli_imports.py")
    print("   python aios_cli.py")
    print()
    print("3. 在WorkBuddy中触发AI OS:")
    print("   输入: 'AI OS' 或 '启动AI操作系统'")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()