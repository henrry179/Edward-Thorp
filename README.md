# Edward Thorp Convertible Arbitrage Lab

> 一个面向学习与研究的「可转债套利策略」开源项目，灵感来自 Edward Thorp 的经典可转债套利框架：  
> **买入低估的可转换债券 + 动态 Delta 对冲做空股票**，以获取定价错误收益并尽量规避市场方向性风险。

## 项目目标

- 系统性地展示可转债市场中性套利策略的核心思想与实现路径；
- 提供从数据处理、定价建模、信号生成、Delta 对冲到回测评估的完整链路；
- 作为学习和研究可转债套利策略的「实验室」。

## 功能特性

- **可转债严格定价与分解**：基于二叉树模型的转股价值、纯债价值、期权价值建模，包含信用利差近似；
- **错定价识别**：基于公平价值与市场价格差异构建信号（含 Z-score 等）；
- **Delta 对冲**：构建「多 CB + 空 Stock」的市场中性组合，并进行动态对冲；
- **回测框架**：支持日频回测，记录组合收益、风险指标与市场中性程度；
- **教学 Notebook（预留）**：通过 Jupyter Notebook 逐步展示策略搭建全过程。

## 安装与快速开始

建议使用虚拟环境：

```bash
cd "Edward Thorp"
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

运行一个简单示例回测：

```bash
python -m examples.run_simple_backtest
```

（首次运行前，需要先确保本项目已被添加到 `PYTHONPATH`，或在仓库根目录下运行。）

## 目录结构（目标）

- `src/cb_arb/`：核心代码（定价、对冲、信号、回测等）
- `examples/`：示例脚本（如 `run_simple_backtest.py`）
- `docs/`：策略原理、模型说明与风险提示（预留）
- `notebooks/`：教学 Notebook（预留）

## 风险与免责声明

本项目仅用于学术研究与教育目的，不构成任何投资建议。  
历史回测结果不代表未来表现，实际交易存在流动性、执行、模型假设等多方面风险。

