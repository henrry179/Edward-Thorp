# 📊 Edward Thorp Convertible Arbitrage Lab

> 一个面向学习与研究的「可转债套利策略」开源项目，灵感来自 Edward Thorp 的经典可转债套利框架：  
> **买入低估的可转换债券 + 动态 Delta 对冲做空股票**，以获取定价错误收益并尽量规避市场方向性风险。

![Status](https://img.shields.io/badge/status-active-success)
![Version](https://img.shields.io/badge/version-0.1.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue)
![Build](https://img.shields.io/badge/build-passing-brightgreen)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)

## 📋 目录

- [项目简介](#项目简介)
- [项目目标](#项目目标)
- [功能特性](#功能特性)
- [安装与快速开始](#安装与快速开始)
- [目录结构](#目录结构)
- [开发进度](#开发进度)
- [文档](#文档)
- [风险与免责声明](#风险与免责声明)

## 📖 项目简介

本项目是一个面向学习与研究的可转债套利策略开源项目，基于 Edward Thorp 的经典可转债套利框架，系统性地展示可转债市场中性套利策略的核心思想与实现路径。

## 🎯 项目目标

- 系统性地展示可转债市场中性套利策略的核心思想与实现路径；
- 提供从数据处理、定价建模、信号生成、Delta 对冲到回测评估的完整链路；
- 作为学习和研究可转债套利策略的「实验室」。

## ✨ 功能特性

- **📈 可转债严格定价与分解**：基于二叉树模型的转股价值、纯债价值、期权价值建模，包含信用利差近似；
- **🔍 错定价识别**：基于公平价值与市场价格差异构建信号（含 Z-score 等）；
- **⚖️ Delta 对冲**：构建「多 CB + 空 Stock」的市场中性组合，并进行动态对冲；
- **📊 回测框架**：支持日频回测，记录组合收益、风险指标与市场中性程度；
- **📚 教学 Notebook**：通过 Jupyter Notebook 逐步展示策略搭建全过程（01 入门～05 回测分析）。

## 🚀 安装与快速开始

### 环境要求

- Python 3.8+
- pip

### 安装步骤

建议使用虚拟环境：

```bash
# 克隆仓库
git clone https://github.com/yourusername/edward-thorp-cb-arb.git
cd "Edward Thorp"

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows PowerShell
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装项目（可选，推荐）
pip install -e .
```

### 运行示例

运行一个简单示例回测：

```bash
# 方式1：设置 PYTHONPATH（Windows PowerShell）
$env:PYTHONPATH = ".\src"; python -m examples.run_simple_backtest

# 方式2：安装为可编辑包后直接运行（推荐）
pip install -e .
python -m examples.run_simple_backtest
```

## 📁 目录结构

```
Edward Thorp/
├── src/
│   └── cb_arb/              # 核心代码（定价、对冲、信号、回测等）
├── examples/                 # 示例脚本
│   ├── run_simple_backtest.py
│   └── sensitivity_analysis.py
├── docs/                     # 策略原理、模型说明与风险提示
├── notebooks/                # 教学 Notebook（01 入门～05 回测分析）
├── tests/                    # 单元测试（pytest）
├── output/                   # 输出文件目录
│   ├── figures/              # 图片文件（PNG 格式，300 DPI）
│   ├── data/                 # 数据文件（CSV 格式，UTF-8-BOM 编码）
│   └── reports/              # 报告文件（预留）
├── requirements.txt          # 依赖列表
├── setup.py                  # 项目安装配置
└── README.md                 # 项目说明
```

## 📊 开发进度

项目当前完成度：**85%**

| 模块 | 完成度 |
|------|--------|
| 核心功能模块 | 100% ✅ |
| 文档 | 90% ✅ |
| 示例与教学 | 95% ✅ |
| 测试 | 85% 🔄 |

详细进度请查看 [开发进度文档](DEVELOPMENT_PROGRESS.md) 和 [进度时间表](docs/PROGRESS_TIMELINE.md)

## 📚 文档

- [理论概述](docs/theory_overview.md) - 可转债套利策略理论基础
- [定价模型](docs/pricing_model.md) - 二叉树定价模型详解
- [Delta 对冲](docs/delta_hedging.md) - Delta 对冲策略说明
- [回测设计](docs/backtest_design.md) - 回测框架设计文档
- [风险说明](docs/risk_and_limitations.md) - 风险提示与限制说明
- [文档索引](docs/index.md) - 完整文档索引

## ⚠️ 风险与免责声明

> **重要声明**：本项目仅用于学术研究与教育目的，不构成任何投资建议。  
> 历史回测结果不代表未来表现，实际交易存在流动性、执行、模型假设等多方面风险。

## 🤝 贡献指南

欢迎贡献！如果您有任何建议或发现问题，请：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- 感谢 Edward Thorp 的经典可转债套利框架启发
- 感谢所有贡献者和使用者的支持

---

*最后更新：2026-02-17*

