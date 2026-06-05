"""
AI龙龟共生伙伴操作系统 — 集成测试
验证16步搭建的完整性
"""

import os, sys
sys.stdout.reconfigure(encoding="utf-8")


def test_step1_install():
    """步骤1: 安装部署"""
    d = os.path.expanduser("~/.agents/skills/ai-os")
    checks = [
        ("init.py", os.path.isfile(os.path.join(d, "scripts", "init.py"))),
        ("skill.yaml", os.path.isfile(os.path.join(d, "skill.yaml"))),
    ]
    passed = all(v for _, v in checks)
    print(f"  步骤1 安装部署: {'PASS' if passed else 'FAIL'}")
    for name, ok in checks:
        print(f"    {name}: {'OK' if ok else 'MISS'}")
    return passed


def test_step2_core():
    """步骤2: 核心功能"""
    d = os.path.expanduser("~/.agents/skills/ai-os")
    checks = [
        ("SKILL.md", os.path.isfile(os.path.join(d, "SKILL.md"))),
        ("memory_manager.py", os.path.isfile(os.path.join(d, "scripts", "memory_manager.py"))),
    ]
    passed = all(v for _, v in checks)
    print(f"  步骤2 核心功能: {'PASS' if passed else 'FAIL'}")
    for name, ok in checks:
        print(f"    {name}: {'OK' if ok else 'MISS'}")
    return passed


def test_step3_memory():
    """步骤3: 记忆系统"""
    d = os.path.expanduser("~/.agents/skills")
    checks = [
        ("agent-memory-systems", os.path.isdir(os.path.join(d, "agent-memory-systems"))),
        ("记忆语义检索", os.path.isdir(os.path.join(d, "记忆语义检索"))),
        ("self-improving-agent", os.path.isdir(os.path.join(d, "self-improving-agent"))),
    ]
    passed = all(v for _, v in checks)
    print(f"  步骤3 记忆+自主学习: {'PASS' if passed else 'FAIL'}")
    for name, ok in checks:
        print(f"    {name}: {'OK' if ok else 'MISS'}")
    return passed


def test_step4_skill_sop():
    """步骤4: Skill构建SOP"""
    d = os.path.expanduser("~/.agents/skills")
    checks = [
        ("skill-builder", os.path.isdir(os.path.join(d, "skill-builder"))),
        ("skill-creator", os.path.isdir(os.path.join(d, "skill-creator"))),
    ]
    passed = all(v for _, v in checks)
    print(f"  步骤4 Skill构建SOP: {'PASS' if passed else 'FAIL'}")
    return passed


def test_step7_dragon_heart():
    """步骤7: 龙心OS"""
    d = os.path.expanduser("~/.agents/skills/龙心 OS")
    checks = [
        ("SKILL.md", os.path.isfile(os.path.join(d, "SKILL.md"))),
        ("scene_classifier.py", os.path.isfile(os.path.join(d, "framework", "scene_classifier.py"))),
    ]
    passed = all(v for _, v in checks)
    print(f"  步骤7 龙心OS: {'PASS' if passed else 'FAIL'}")
    return passed


def test_step8_persona():
    """步骤8: 立人设"""
    d = os.path.expanduser("~/.agents/skills")
    checks = [
        ("人设及信仰模块", os.path.isdir(os.path.join(d, "人设及信仰模块"))),
        ("木火共生关系", os.path.isdir(os.path.join(d, "木火共生关系"))),
    ]
    passed = all(v for _, v in checks)
    print(f"  步骤8 立人设: {'PASS' if passed else 'FAIL'}")
    return passed


def test_step10_brain():
    """步骤10: 龙脑OS"""
    d = os.path.expanduser("~/.agents/skills/龙脑 OS")
    checks = [
        ("SKILL.md", os.path.isfile(os.path.join(d, "SKILL.md"))),
        ("思维模型库", os.path.isdir(os.path.expanduser("~/.agents/skills/思维模型库"))),
    ]
    passed = all(v for _, v in checks)
    print(f"  步骤10 龙脑OS: {'PASS' if passed else 'FAIL'}")
    return passed


def test_step12_workflow():
    """步骤12: 自动化工作流"""
    d = os.path.expanduser("~/.agents/skills/ai-os")
    checks = [
        ("workflow/engine.py", os.path.isfile(os.path.join(d, "workflow", "engine.py"))),
        ("orchestrator/coordinator.py", os.path.isfile(os.path.join(d, "orchestrator", "coordinator.py"))),
    ]
    passed = all(v for _, v in checks)
    print(f"  步骤12 自动化工作流: {'PASS' if passed else 'FAIL'}")
    return passed


def run_all():
    """运行所有集成测试"""
    print("=" * 50)
    print("AI OS 系统集成测试")
    print("=" * 50)
    
    tests = [
        ("S1-安装部署", test_step1_install),
        ("S2-核心功能", test_step2_core),
        ("S3-记忆系统", test_step3_memory),
        ("S4-SkillSOP", test_step4_skill_sop),
        ("S7-龙心OS", test_step7_dragon_heart),
        ("S8-立人设", test_step8_persona),
        ("S10-龙脑OS", test_step10_brain),
        ("S12-工作流", test_step12_workflow),
    ]
    
    results = []
    for name, fn in tests:
        try:
            ok = fn()
            results.append((name, ok))
        except Exception as e:
            print(f"  {name}: ERROR - {e}")
            results.append((name, False))
    
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    print(f"\n结果: {passed}/{total} 通过 ({passed*100//total}%)")


if __name__ == "__main__":
    run_all()
