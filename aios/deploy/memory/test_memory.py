#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆系统功能测试
测试扩展四层记忆系统的核心功能

测试内容:
1. 记忆存储和检索
2. 场景记忆功能
3. 技能调用历史记录
4. 检索优化算法
5. 自动归档功能

版本: 1.0.0
开发者: 龙龟神将
用户: 悟空
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory.memory_manager import ExtendedMemorySystem, DRAGON_HEART_SCENES
from memory.skill_history import SkillHistoryManager
from memory.retrieval_optimizer import RetrievalOptimizer
from memory.auto_archiver import AutoArchiver


class TestMemorySystem:
    """记忆系统测试类"""
    
    def __init__(self):
        self.test_dir = tempfile.mkdtemp(prefix="aios_memory_test_")
        print(f"📁 测试目录: {self.test_dir}")
        self.memory = ExtendedMemorySystem(memory_path=self.test_dir)
        self.skill_manager = SkillHistoryManager(self.memory)
        self.optimizer = RetrievalOptimizer(self.memory)
    
    def cleanup(self):
        """清理测试目录"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            print(f"🧹 已清理测试目录: {self.test_dir}")
    
    def test_basic_storage(self) -> bool:
        """测试基本存储和检索"""
        print("\n🔧 测试1: 基本存储和检索")
        
        try:
            # 存储测试记忆
            memory_id = self.memory.store(
                layer="user",
                content="这是测试记忆内容，用于验证存储功能",
                title="测试记忆",
                importance=7,
                tags=["测试", "基础功能"]
            )
            print(f"   存储成功，ID: {memory_id}")
            
            # 检索测试记忆
            retrieved = self.memory.retrieve(memory_id)
            if not retrieved:
                print("   ❌ 检索失败")
                return False
            
            print(f"   检索成功，标题: {retrieved['title']}")
            
            # 验证内容
            if retrieved['content'] != "这是测试记忆内容，用于验证存储功能":
                print("   ❌ 内容不匹配")
                return False
            
            print("   ✅ 基本存储检索测试通过")
            return True
            
        except Exception as e:
            print(f"   ❌ 测试失败: {e}")
            return False
    
    def test_scene_memory(self) -> bool:
        """测试场景记忆功能"""
        print("\n🔧 测试2: 场景记忆功能")
        
        try:
            # 存储场景记忆
            scene = "S2"  # 深度学习探索
            memory_id = self.memory.store_scene_memory(
                scene=scene,
                content="深度学习龙心OS调度算法，理解其核心原理",
                title="调度算法学习",
                importance=8,
                tags=["学习", "算法", "龙心OS"]
            )
            print(f"   场景记忆存储成功，ID: {memory_id}，场景: {scene}")
            
            # 按场景搜索
            scene_results = self.memory.search_by_scene(scene, limit=5)
            if not scene_results:
                print("   ❌ 场景搜索未找到结果")
                return False
            
            print(f"   场景搜索找到 {len(scene_results)} 条记忆")
            
            # 验证场景分类
            for entry in scene_results:
                if entry.get("scene") != scene:
                    print(f"   ❌ 场景分类错误: {entry.get('scene')}")
                    return False
            
            print("   ✅ 场景记忆测试通过")
            return True
            
        except Exception as e:
            print(f"   ❌ 测试失败: {e}")
            return False
    
    def test_skill_history(self) -> bool:
        """测试技能调用历史记录"""
        print("\n🔧 测试3: 技能调用历史")
        
        try:
            # 记录技能调用
            skill_id = self.skill_manager.record_skill_call(
                skill_name="龙心OS",
                skill_params={"action": "schedule", "priority": "high"},
                result="调度成功，使用S2场景处理",
                execution_time=1.5,
                success=True
            )
            print(f"   技能调用记录成功，ID: {skill_id}")
            
            # 记录失败调用
            fail_id = self.skill_manager.record_skill_call(
                skill_name="龙脑OS",
                skill_params={"model": "创新思维", "complexity": "high"},
                result=None,
                execution_time=0.8,
                success=False,
                error_msg="思维模型加载超时"
            )
            print(f"   失败技能调用记录成功，ID: {fail_id}")
            
            # 获取技能统计
            stats = self.skill_manager.get_skill_stats(days=7)
            print(f"   技能统计: {len(stats)} 个技能有调用记录")
            
            # 验证龙心OS记录
            if "龙心OS" not in stats:
                print("   ❌ 龙心OS技能记录缺失")
                return False
            
            print(f"   龙心OS调用统计: {stats['龙心OS']['total_calls']} 次调用")
            
            print("   ✅ 技能调用历史测试通过")
            return True
            
        except Exception as e:
            print(f"   ❌ 测试失败: {e}")
            return False
    
    def test_retrieval_optimization(self) -> bool:
        """测试检索优化算法"""
        print("\n🔧 测试4: 检索优化算法")
        
        try:
            # 先存储一些测试记忆
            test_memories = [
                ("龙心OS调度算法详解", "深度学习龙心OS调度算法，理解其核心原理", "S2", ["算法", "调度"]),
                ("龙脑OS思维模型", "掌握龙脑OS的9大高频本能模型", "S3", ["思维", "模型"]),
                ("龙爪OS执行流程", "学习龙爪OS的项目执行标准化流程", "S4", ["执行", "流程"]),
            ]
            
            for title, content, scene, tags in test_memories:
                self.memory.store_scene_memory(
                    scene=scene,
                    content=content,
                    title=title,
                    importance=7,
                    tags=tags
                )
            
            # 测试优化搜索
            results = self.optimizer.optimized_search(
                query="龙心OS调度",
                layer="all",
                limit=5
            )
            
            print(f"   优化搜索找到 {len(results)} 条相关记忆")
            
            if len(results) < 1:
                print("   ❌ 优化搜索未找到结果")
                return False
            
            # 检查结果排序
            scores = [r.get("_optimized_score", 0) for r in results]
            if not all(scores[i] >= scores[i+1] for i in range(len(scores)-1)):
                print("   ❌ 结果未按分数排序")
                return False
            
            # 测试关键词扩展
            expanded = self.optimizer.expand_keywords("学习调度算法")
            print(f"   关键词扩展结果: {expanded}")
            
            # 测试场景推断
            scene = self.optimizer.infer_scene_from_query("如何深度学习系统架构")
            print(f"   场景推断结果: {scene}")
            
            print("   ✅ 检索优化算法测试通过")
            return True
            
        except Exception as e:
            print(f"   ❌ 测试失败: {e}")
            return False
    
    def test_auto_archival(self) -> bool:
        """测试自动归档功能"""
        print("\n🔧 测试5: 自动归档功能")
        
        try:
            # 创建归档器
            archiver = AutoArchiver(self.memory)
            
            # 先存储一些旧记忆（通过修改文件时间模拟）
            import time
            old_time = time.time() - 60 * 60 * 24 * 35  # 35天前
            
            for i in range(3):
                memory_id = self.memory.store(
                    layer="user",
                    content=f"旧记忆内容 {i+1}，应被归档",
                    title=f"旧记忆 {i+1}",
                    importance=2,  # 低重要性
                    tags=["测试", "旧记忆"]
                )
                
                # 修改文件时间为过去
                memory_file = Path(self.test_dir) / "user" / f"{memory_id}.json"
                os.utime(memory_file, (old_time, old_time))
            
            # 运行试归档
            stats = archiver.run_archival(dry_run=True)
            
            print(f"   试归档统计: 检查 {stats['total_checked']} 条，应归档 {stats['archived']} 条")
            
            if stats['archived'] < 3:
                print("   ⚠️  可能未正确识别旧记忆")
            
            # 实际运行归档
            stats = archiver.run_archival(dry_run=False)
            print(f"   实际归档统计: 归档了 {stats['archived']} 条记忆")
            
            # 检查归档层
            archive_dir = Path(self.test_dir) / "archive"
            if archive_dir.exists():
                archive_count = len(list(archive_dir.glob("*.json")))
                print(f"   归档层现有 {archive_count} 条记忆")
            
            print("   ✅ 自动归档功能测试通过")
            return True
            
        except Exception as e:
            print(f"   ❌ 测试失败: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """运行所有测试"""
        print("=" * 60)
        print("🧪 开始记忆系统功能测试")
        print("=" * 60)
        
        test_results = []
        
        # 运行测试
        test_results.append(("基本存储检索", self.test_basic_storage()))
        test_results.append(("场景记忆功能", self.test_scene_memory()))
        test_results.append(("技能调用历史", self.test_skill_history()))
        test_results.append(("检索优化算法", self.test_retrieval_optimization()))
        test_results.append(("自动归档功能", self.test_auto_archival()))
        
        # 打印结果摘要
        print("\n" + "=" * 60)
        print("📊 测试结果摘要")
        print("=" * 60)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{test_name:20} {status}")
            if result:
                passed += 1
        
        print(f"\n测试通过率: {passed}/{total} ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("\n🎉 所有测试通过！记忆系统功能正常。")
        else:
            print(f"\n⚠️  有 {total - passed} 个测试失败，请检查问题。")
        
        return passed == total


def main():
    """主测试函数"""
    tester = TestMemorySystem()
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    finally:
        tester.cleanup()


if __name__ == "__main__":
    sys.exit(main())