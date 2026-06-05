# AI OS 更新日志

## 1.1.0 (2026-05-30)

### 新增
- **scripts/ 目录**：init.py（系统初始化）、memory_manager.py（四层记忆系统，SQLite存储）、test_ai_os_integration.py（8项集成测试）
- **workflow/ 目录**：engine.py（工作流引擎，支持创建/执行/列表管理）
- **orchestrator/ 目录**：coordinator.py（多智能体协调器，支持任务分解/智能体注册/分配）
- **skill.yaml**：WorkBuddy技能配置文件，按灵魂/认知/执行/工具四分类

### 修复
- init.py 中跨行 f-string 语法错误修复
- 全部 8 项集成测试通过 (100%)

### 配套技能新增
- 龙脑 OS 思维模型库：004-逻辑层次/SKILL.md
- 龙脑 OS 思维模型库：006-系统思维/SKILL.md

## 1.0.0 (2026-03-15)

### 初始版本
- AI OS 核心技能包：灵魂系统 + 工程身体
- 四层记忆架构设计（SOUL/USER/TOOLS/SESSION）
- 技能框架结构设计
- 300+ 行完整 SKILL.md 文档