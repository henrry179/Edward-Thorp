---
name: github-repo-enhancer
description: 美化 GitHub 开源项目仓库的主文档和主页展示效果，包括设计、美工、页面布局优化，自动更新项目开发进度到主文档，并自动推送更新到 GitHub 仓库。当用户要求美化文档、更新进度、改进项目展示效果或推送到 GitHub 时使用。
---

# GitHub 仓库美化与进度管理

专业级别的 GitHub 开源项目文档美化、进度更新和自动推送工具。

## 使用场景

在以下情况自动触发：
- 用户要求美化 README.md 或项目文档
- 用户要求更新项目开发进度
- 用户要求改进 GitHub 仓库展示效果
- 用户要求推送到 GitHub
- 完成重要开发任务后需要更新文档
- 用户说"美化文档"、"更新进度"、"推送到 GitHub"等类似表达时

## 核心功能

### 1. README.md 美化

美化项目主文档，包括：

#### 1.1 添加专业徽章（Badges）
- 项目状态徽章（如：![Status](https://img.shields.io/badge/status-active-success)）
- 版本徽章（如：![Version](https://img.shields.io/badge/version-0.1.0-blue)）
- 许可证徽章（如：![License](https://img.shields.io/badge/license-MIT-green)）
- Python 版本徽章（如：![Python](https://img.shields.io/badge/python-3.8+-blue)）
- 构建状态徽章（如：![Build](https://img.shields.io/badge/build-passing-brightgreen)）
- 测试覆盖率徽章（如：![Coverage](https://img.shields.io/badge/coverage-80%25-yellow)）

#### 1.2 优化文档结构
- 添加项目 Logo 或图标区域（使用 emoji 或 ASCII art）
- 添加目录导航（Table of Contents）
- 使用分隔线和视觉元素增强可读性
- 添加项目截图或演示 GIF（如有）
- 优化代码块格式和语法高亮

#### 1.3 增强视觉设计
- 使用 emoji 图标增强可读性（📊 📈 🔬 💡 ⚡ 🎯 等）
- 添加项目特色亮点区域
- 使用表格展示功能对比或特性列表
- 添加贡献指南链接
- 添加相关资源链接

#### 1.4 专业布局模板

标准 README.md 结构：
```markdown
# 🎯 项目名称

> 简短的项目描述和核心价值

[徽章区域]

## 📋 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [快速开始](#快速开始)
- [安装指南](#安装指南)
- [使用示例](#使用示例)
- [项目结构](#项目结构)
- [开发进度](#开发进度)
- [贡献指南](#贡献指南)
- [许可证](#许可证)
- [致谢](#致谢)

## 📖 项目简介

[项目背景、目标和价值]

## ✨ 功能特性

- **特性1**：描述
- **特性2**：描述
- **特性3**：描述

## 🚀 快速开始

[快速开始指南]

## 📦 安装指南

[详细的安装步骤]

## 💡 使用示例

[代码示例和使用说明]

## 📁 项目结构

```
项目结构树
```

## 📊 开发进度

[开发进度概览，链接到 DEVELOPMENT_PROGRESS.md]

## 🤝 贡献指南

[如何贡献]

## 📄 许可证

[许可证信息]

## 🙏 致谢

[致谢内容]
```

### 2. DEVELOPMENT_PROGRESS.md 美化

美化开发进度文档：

#### 2.1 添加进度可视化
- 使用进度条显示完成度（如：████████░░ 80%）
- 使用表格展示各模块完成状态
- 添加时间线图表（使用 Markdown 表格或 Mermaid 图表）
- 使用颜色编码（✅ 已完成、🔄 进行中、📋 计划中）

#### 2.2 优化进度展示
- 添加项目概览统计（总体完成度、模块数量等）
- 使用卡片式布局展示各阶段
- 添加里程碑标记
- 优化更新日志格式

#### 2.3 进度文档模板

```markdown
# 📊 项目开发进度

## 📈 项目概览

| 指标 | 数值 |
|------|------|
| 总体完成度 | 85% |
| 核心模块 | 5/5 ✅ |
| 文档完成度 | 90% |
| 测试覆盖率 | 80% |

## 🎯 开发时间线

[时间线展示]

## ✅ 已完成功能

[已完成功能列表]

## 🔄 进行中功能

[进行中功能列表]

## 📋 计划中功能

[计划中功能列表]

## 📝 最新更新日志

[更新日志]
```

### 3. 自动更新开发进度

#### 3.1 提取对话摘要
从当前对话中提取：
- 完成的主要任务（使用 ✅ 标记）
- 进行中的任务（使用 🔄 标记）
- 修改的文件列表
- 新增的功能
- 解决的问题

#### 3.2 更新 DEVELOPMENT_PROGRESS.md
1. 读取现有的 `DEVELOPMENT_PROGRESS.md`
2. 在"最新更新日志"部分顶部添加今天的更新
3. 更新"当前完成度统计"中的相关百分比
4. 更新"下一步行动计划"
5. 更新"最后更新"日期

#### 3.3 更新 README.md
如果 README.md 包含进度信息，同步更新：
- 更新项目状态
- 更新功能列表
- 更新完成度信息
- 更新最后更新时间

### 4. Git 提交与推送

执行以下 Git 操作：
1. 检查是否有未提交的更改
2. 添加所有更改的文件
3. 提交消息格式：
   - 美化文档：`docs: 美化项目文档和 README.md`
   - 更新进度：`docs: 更新开发进度 - YYYY-MM-DD`
   - 综合更新：`docs: 美化文档并更新开发进度 - YYYY-MM-DD`
4. 推送到远程仓库（自动检测分支：main/master/main/develop）

## 工作流程

### 美化文档流程

1. **分析现有文档**
   - 读取 README.md 和 DEVELOPMENT_PROGRESS.md
   - 识别需要改进的部分
   - 确定项目类型和特点

2. **应用美化模板**
   - 添加徽章（根据项目实际情况）
   - 优化结构和布局
   - 添加视觉元素（emoji、分隔线等）
   - 优化代码块和表格格式

3. **更新内容**
   - 确保所有链接有效
   - 检查格式一致性
   - 验证 Markdown 语法

4. **保存并提交**
   - 保存更新后的文档
   - Git 提交和推送

### 更新进度流程

1. **提取对话摘要**
   - 分析对话历史
   - 提取完成的任务
   - 提取修改的文件

2. **更新进度文档**
   - 更新 DEVELOPMENT_PROGRESS.md
   - 更新 README.md（如需要）
   - 更新完成度统计

3. **保存对话历史**
   - 保存到 `.cursor/conversation_history/{日期}.md`

4. **Git 提交和推送**
   - 提交更改
   - 推送到远程仓库

## 徽章生成指南

### 常用徽章类型

1. **状态徽章**
   ```
   ![Status](https://img.shields.io/badge/status-active-success)
   ![Status](https://img.shields.io/badge/status-maintenance-yellow)
   ```

2. **版本徽章**
   ```
   ![Version](https://img.shields.io/badge/version-0.1.0-blue)
   ```

3. **许可证徽章**
   ```
   ![License](https://img.shields.io/badge/license-MIT-green)
   ```

4. **语言/框架徽章**
   ```
   ![Python](https://img.shields.io/badge/python-3.8+-blue)
   ![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue)
   ```

5. **构建/测试徽章**
   ```
   ![Build](https://img.shields.io/badge/build-passing-brightgreen)
   ![Tests](https://img.shields.io/badge/tests-passing-brightgreen)
   ![Coverage](https://img.shields.io/badge/coverage-80%25-yellow)
   ```

6. **GitHub 相关徽章**
   ```
   ![GitHub stars](https://img.shields.io/github/stars/username/repo?style=social)
   ![GitHub forks](https://img.shields.io/github/forks/username/repo?style=social)
   ```

### 自定义徽章

使用 shields.io 生成自定义徽章：
```
https://img.shields.io/badge/{label}-{message}-{color}
```

颜色选项：brightgreen, green, yellowgreen, yellow, orange, red, blue, lightgrey, success, important, critical, informational, inactive

## 视觉设计原则

### 1. 一致性
- 使用统一的 emoji 风格
- 保持格式一致性
- 统一的分隔线样式

### 2. 可读性
- 合理使用空行分隔
- 使用标题层级清晰
- 代码块使用语法高亮

### 3. 专业性
- 避免过度使用 emoji
- 保持文档简洁明了
- 使用专业的术语和描述

### 4. 响应式
- 确保表格在不同设备上可读
- 避免过长的代码行
- 使用相对路径而非绝对路径

## Emoji 使用指南

### 常用 Emoji 分类

**状态/进度**
- ✅ 完成
- 🔄 进行中
- 📋 计划中
- ⏳ 等待中
- ❌ 已取消

**功能/特性**
- 📊 数据分析
- 📈 图表/可视化
- 🔬 研究/实验
- 💡 想法/创新
- ⚡ 性能
- 🎯 目标
- 🔒 安全
- 🚀 快速/高效

**文档/信息**
- 📖 文档
- 📝 笔记
- 📚 书籍/资源
- 🔍 搜索/查找
- 💬 讨论

**工具/技术**
- 🐍 Python
- 📦 包/模块
- 🔧 工具
- ⚙️ 配置
- 🧪 测试

## 注意事项

1. **Git 权限**：确保有 Git 写入权限，且已配置远程仓库
2. **分支检测**：自动检测当前分支（main/master/main/develop）
3. **冲突处理**：如果存在冲突，提示用户手动解决
4. **文件存在性**：如果文档不存在，创建它们
5. **编码**：所有文件使用 UTF-8 编码
6. **错误处理**：如果 Git 操作失败，记录错误但不中断流程
7. **徽章链接**：确保徽章链接有效，使用 shields.io 或自定义服务
8. **保持简洁**：避免过度美化，保持文档的专业性和可读性

## 执行方式

**直接实现**：使用工具直接执行文件读写和 Git 操作，而不是调用外部脚本。

**关键操作**：
1. 使用 `read_file` 读取现有文档
2. 使用 `search_replace` 或 `write` 更新文档
3. 使用 `run_terminal_cmd` 执行 Git 命令
4. 确保所有操作都在项目根目录（Git 仓库根目录）执行

## 示例

### 示例 1：美化 README.md

**场景**：用户要求美化项目 README.md

**执行流程**：
1. 读取现有 README.md
2. 分析项目特点（Python 项目、金融量化、教育用途）
3. 添加合适的徽章（Python、License、Status 等）
4. 优化文档结构（添加目录、使用 emoji、优化格式）
5. 保存并提交：
   - `git add README.md`
   - `git commit -m "docs: 美化 README.md 文档"`
   - `git push origin {当前分支}`

### 示例 2：更新开发进度

**场景**：用户完成了一个新功能并说"更新进度"

**执行流程**：
1. 提取对话摘要：完成的功能、修改的文件等
2. 读取 DEVELOPMENT_PROGRESS.md
3. 更新"最新更新日志"，添加今天的条目
4. 更新"当前完成度统计"
5. 更新 README.md（如需要）
6. 保存对话到 `.cursor/conversation_history/{日期}.md`
7. 执行 Git 操作：
   - `git add .`
   - `git commit -m "docs: 更新开发进度 - YYYY-MM-DD"`
   - `git push origin {当前分支}`

### 示例 3：综合美化与更新

**场景**：用户要求美化文档并更新进度

**执行流程**：
1. 美化 README.md（添加徽章、优化布局）
2. 美化 DEVELOPMENT_PROGRESS.md（添加进度可视化）
3. 更新开发进度信息
4. 保存对话历史
5. 执行 Git 操作：
   - `git add .`
   - `git commit -m "docs: 美化文档并更新开发进度 - YYYY-MM-DD"`
   - `git push origin {当前分支}`

## 输出示例

**美化文档后**：
```
✅ 已美化 README.md
   - 添加了 6 个专业徽章
   - 优化了文档结构
   - 添加了目录导航
   - 增强了视觉设计

✅ 已美化 DEVELOPMENT_PROGRESS.md
   - 添加了进度可视化
   - 优化了进度展示格式
   - 更新了完成度统计

✅ 已提交更改
✅ 已推送到远程仓库
```

**更新进度后**：
```
✅ 对话上下文已保存
✅ 已更新开发进度文档
   - 添加了今天的更新日志
   - 更新了完成度统计（85% → 87%）
   - 更新了下一步计划

✅ 已提交更改
✅ 已推送到远程仓库
```
