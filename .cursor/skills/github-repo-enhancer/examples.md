# 使用示例

## 示例 1：美化 Python 项目的 README.md

### 输入（原始 README.md）
```markdown
# Project Name

A simple project description.

## Features
- Feature 1
- Feature 2

## Installation
pip install -r requirements.txt
```

### 输出（美化后的 README.md）
```markdown
# 🎯 Project Name

> A simple project description with enhanced visual appeal.

![Status](https://img.shields.io/badge/status-active-success)
![Version](https://img.shields.io/badge/version-0.1.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.8+-blue)

## 📋 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [安装指南](#安装指南)

## 📖 项目简介

A simple project description.

## ✨ 功能特性

- **Feature 1**：详细描述
- **Feature 2**：详细描述

## 📦 安装指南

```bash
pip install -r requirements.txt
```

## 📄 许可证

MIT License
```

## 示例 2：更新开发进度

### 对话摘要
- 完成了新功能：用户认证模块
- 修改了文件：src/auth.py, tests/test_auth.py
- 更新了文档：docs/auth_guide.md

### 更新 DEVELOPMENT_PROGRESS.md

**更新前**：
```markdown
## 最新更新日志

### 2026-02-16
- ✅ 完成基础框架
```

**更新后**：
```markdown
## 最新更新日志

### 2026-02-17
- ✅ 完成用户认证模块
  - 实现登录/注册功能
  - 添加 JWT 令牌支持
  - 完成单元测试
  - 更新文档

### 2026-02-16
- ✅ 完成基础框架
```

### 更新完成度统计

**更新前**：
```markdown
### 核心功能模块
- ✅ 基础框架：100%
- 🔄 用户认证：0%
```

**更新后**：
```markdown
### 核心功能模块
- ✅ 基础框架：100%
- ✅ 用户认证：100%
```

## 示例 3：添加专业徽章

### 根据项目特点选择合适的徽章

**Python 项目**：
```markdown
![Python](https://img.shields.io/badge/python-3.8+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
```

**有测试的项目**：
```markdown
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-80%25-yellow)
```

**GitHub 项目**：
```markdown
![GitHub stars](https://img.shields.io/github/stars/username/repo?style=social)
![GitHub forks](https://img.shields.io/github/forks/username/repo?style=social)
```

## 示例 4：美化进度文档

### 更新前
```markdown
## 开发进度

已完成：
- 模块1
- 模块2

进行中：
- 模块3
```

### 更新后
```markdown
## 📊 开发进度

### 📈 项目概览

| 指标 | 数值 |
|------|------|
| 总体完成度 | 75% |
| 核心模块 | 3/5 ✅ |
| 文档完成度 | 80% |
| 测试覆盖率 | 70% |

### ✅ 已完成功能

- ✅ **模块1**：100% 完成
- ✅ **模块2**：100% 完成

### 🔄 进行中功能

- 🔄 **模块3**：60% 完成

### 📋 计划中功能

- 📋 **模块4**：计划中
- 📋 **模块5**：计划中
```

## 示例 5：Git 提交消息

### 美化文档
```
docs: 美化 README.md 和项目文档
- 添加专业徽章（状态、版本、许可证、Python版本）
- 优化文档结构和布局
- 添加目录导航
- 增强视觉设计（emoji、分隔线）
```

### 更新进度
```
docs: 更新开发进度 - 2026-02-17
- 完成用户认证模块
- 更新完成度统计（75% → 80%）
- 更新下一步计划
```

### 综合更新
```
docs: 美化文档并更新开发进度 - 2026-02-17
- 美化 README.md（添加徽章、优化布局）
- 美化 DEVELOPMENT_PROGRESS.md（添加进度可视化）
- 更新开发进度信息
- 更新完成度统计
```
