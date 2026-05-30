#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
    
input("
按Enter键退出...")
