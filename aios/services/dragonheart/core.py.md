# 龙心 OS Framework 层

> 🧠 智能体核心架构 · 感知 - 决策 - 学习 · 2026-04-16

**版本**: v1.0  
**日期**: 2026-04-16  
**标签**: #Framework #智能体架构 #龙心 OS

---

## 🏗️ Framework 层定位

Framework 层是龙心 OS 的"大脑"，实现真正的智能体核心能力：
- **自主感知**: 读取上下文、理解意图
- **智能决策**: 场景识别、引擎路由
- **持续学习**: 反馈收集、权重优化

---

## 🌲 三层架构

```
┌─────────────────────────────────────────┐
│ 概念层 (Conceptual Layer)               │
│ - SKILL.md 文档澄清                     │
│ - 智能体 vs Skill 区分                  │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ Framework 层 (核心智能层)                │
│ - 场景识别矩阵 (S0-S9)                  │
│ - 引擎路由决策树                        │
│ - 反馈学习机制                          │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 载体层 (Carrier Layer)                  │
│ - Skill 结构 (triggers/templates)       │
│ - workbuddy 基础设施                    │
└─────────────────────────────────────────┘
```

---

## 🧠 核心模块

### 1. 场景识别器 (Scene Classifier)

```python
class SceneClassifier:
    def __init__(self):
        self.scene_matrix = load_scene_matrix()
        self.weights = load_weights()
    
    def classify(self, input_text, context):
        features = self.extract_features(input_text, context)
        scores = self.calculate_scores(features)
        best_scene = self.select_best_scene(scores)
        confidence = scores[best_scene]
        return best_scene, confidence
```

---

### 2. 引擎路由器 (Engine Router)

```python
class EngineRouter:
    def __init__(self):
        self.engine_map = load_engine_map()
        self.sub_agents = load_sub_agents()
    
    def route(self, scene_code, confidence):
        if confidence >= 0.9:
            return self.single_engine_route(scene_code)
        elif confidence >= 0.7:
            return self.multi_engine_route(scene_code)
        else:
            return self.default_route()
```

---

### 3. 反馈学习器 (Feedback Learner)

```python
class FeedbackLearner:
    def __init__(self):
        self.learning_rate = 0.1
        self.feedback_history = []
    
    def learn(self, scene_code, feedback, outcome):
        # 显式反馈
        if feedback == 'positive':
            self.adjust_weight(scene_code, +0.1)
        elif feedback == 'negative':
            self.adjust_weight(scene_code, -0.2)
        
        # 隐式反馈
        if outcome == 'continued':
            self.adjust_weight(scene_code, +0.05)
        elif outcome == 'abandoned':
            self.adjust_weight(scene_code, -0.1)
```

---

## 📊 数据流

```
用户输入
    │
    ↓
┌─────────────────┐
│ 上下文感知模块  │
│ - 对话历史      │
│ - 情感分析      │
│ - 话题识别      │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ 场景识别器      │
│ - 特征提取      │
│ - 置信度评分    │
│ - S0-S9 分类    │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ 引擎路由器      │
│ - 单引擎        │
│ - 多引擎协同    │
│ - 全引擎        │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ 子智能体执行    │
│ - 知行合一      │
│ - 知识学习      │
│ - 人机协同      │
│ - 象思维        │
│ - 五色光思维    │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ 反馈学习器      │
│ - 收集反馈      │
│ - 调整权重      │
│ - 优化路由      │
└─────────────────┘
```

---

## 🔄 学习闭环

```
┌─────────────────────────────────────────┐
│           持续学习进化                  │
│                                         │
│  感知 → 决策 → 行动 → 反馈 → 学习      │
│   ↑                              │      │
│   └──────────────────────────────┘      │
│                                         │
│  每次交互都是学习机会                   │
│  每次反馈都优化系统                     │
└─────────────────────────────────────────┘
```

---

_Framework 层 v1.0 · 2026-04-16 · 龙心 OS_
