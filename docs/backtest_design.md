## 回测架构设计与实现（Backtest Design）

本节对应代码模块 `src/cb_arb/backtest.py` 与 `examples/run_simple_backtest.py`，重点解释策略回测的整体结构、假设与局限。

### 1. 回测目标与视角

本项目的回测目标是：

- 在给定的股票价格路径与可转债市场价格时间序列上，评估「多低估可转债 + Delta 对冲空股票」策略的表现；
- 验证在严谨定价 + Delta 对冲的前提下，策略的收益是否主要来自「错定价收敛」，而非对标的股价方向的押注。

注意：  
本回测框架是**学习与研究导向**的，重点在于阐释「定价–信号–对冲–PnL」链条，而非工业级实盘系统。

### 2. 数据输入与预处理

回测依赖以下时间序列：

1. **股票价格序列** \(\{S_t\}\)
   - 频率：通常为日频（交易日）；
   - 来源：可以是历史数据，也可以是模拟 GBM 路径（如示例脚本中）。

2. **可转债市场价格序列** \(\{\text{CB}_t^{\text{mkt}}\}\)
   - 频率：与股票价格对齐；
   - 来源：历史行情或基于某个“理论价 + 噪声”的构造。

在代码中，我们假设二者索引完全对齐，即：

\[
\text{index}(\text{cb\_market\_price}) = \text{index}(\text{stock\_price}).
\]

### 3. 策略结构：错定价信号 + 对冲组合

回测包含两个层次：

1. **信号层（Signal Layer）**
   - 使用模型公允价值与市场价格的差值：
     \[
     \text{mispricing}_t = \text{CB}_t^{\text{fair}} - \text{CB}_t^{\text{mkt}}
     \]
   - 对错定价序列进行滚动标准化，得到 Z-score：
     \[
     z_t = \frac{\text{mispricing}_t - \mu_t}{\sigma_t},
     \]
     其中 \(\mu_t, \sigma_t\) 为一定回看窗口内的滚动均值与标准差。
   - 根据阈值规则生成持仓信号：
     - 若 \(z_t < z_{\text{entry}} < 0\)：认为可转债被显著低估 → 开仓（signal = 1）；  
     - 若持仓中且 \(z_t > z_{\text{exit}}\)：偏离已收敛 → 平仓（signal = 0）。

2. **组合层（Portfolio / Hedging Layer）**
   - 当 signal = 1 时：
     - 持有一定名义面值的可转债；
     - 按当日 Delta 对冲空股票，维持组合近似 Delta 中性；
     - 记录组合价值 \(\Pi_t\)。
   - 当 signal = 0 时：
     - 视为不持有任何头寸，组合价值为 0。

### 4. 回测流程分解

`CBArbBacktester.run` 中的主要步骤如下：

1. **定价与错定价计算**
   - 调用 `compute_mispricing_series`：
     - 对每个日期，用 `price_convertible_bond_binomial` 计算公允价值 \(\text{CB}_t^{\text{fair}}\)；
     - 计算 \(\text{mispricing}_t = \text{CB}_t^{\text{fair}} - \text{CB}_t^{\text{mkt}}\)；
   - 得到包含 `cb_market / stock / cb_fair / mispricing` 的 DataFrame。

2. **Z-score 与信号生成**
   - 调用 `add_zscore_and_signals`：
     - 对 `mispricing` 做滚动均值与标准差，得到 Z-score；
     - 根据 `MispricingSignalConfig`（窗口长度、入场 / 离场阈值）生成 `signal` 列。

3. **Delta 对冲组合轨迹**
   - 构造 `DeltaHedger` 实例；
   - 调用 `run_daily_hedging(stock_price)`：
     - 对给定的股票路径进行逐日可转债定价；
     - 对每一日计算 Delta、对冲股数与市场中性组合价值 `portfolio_value_raw`。

4. **将信号与组合价值结合**
   - 用 hedger 输出的 `portfolio_value_raw` 作为「标准对冲组合价值」；
   - 在 `CBArbBacktester.run` 中：
     - 若当天 `signal == 1`，组合价值 \(\Pi_t\) 取自 `portfolio_value_raw`；
     - 若 `signal == 0`，组合价值设为 0（视为完全平仓）；
   - 通过差分得到日度 PnL：
     \[
     \text{PnL}_t = \Pi_t - \Pi_{t-1}.
     \]
   - 累计收益：
     \[
     \text{CumPnL}_t = \sum_{k \le t} \text{PnL}_k.
     \]

最终输出的 DataFrame 包含：

- `mispricing, zscore, signal`：策略信号与因子；
- `portfolio_value, pnl, cum_pnl`：组合价值与收益轨迹。

### 5. 示例脚本中的模拟实验

`examples/run_simple_backtest.py` 中给出了一个可运行的「模拟实验」：

1. 使用 GBM 生成一条股票价格路径；
2. 构造一个「纯债 + 折扣转股价值」的理论可转债价格；
3. 叠加随机噪声得到可转债市场价格；
4. 在此基础上运行套利策略回测；
5. 绘制累计 PnL 与股票价格的对比曲线：
   - 若模型与参数合适，应观察到：
     - 策略的累计 PnL 具有一定的正期望；
     - 策略收益与股票价格走势之间相关性较低（即具备一定市场中性特征）。

### 6. 重要假设与局限性

当前回测框架的主要假设与局限包括：

1. **忽略交易成本与滑点**
   - 未计入买卖价差、佣金、冲击成本等；
   - 在现实场景中，交易成本会显著侵蚀高频再平衡的收益。

2. **对数据质量的理想化假设**
   - 示例使用的是模拟数据，真实市场中存在停牌、缺失、成交量不足等问题；
   - 历史数据预处理与质量控制在实际策略开发中非常关键。

3. **定价模型的近似**
   - 信用风险通过信用利差简单折现，而非显式违约模型；
   - 利率与波动率结构假设为平坦或简单函数，未考虑微笑 / 期限结构细节。

4. **离散对冲频率**
   - Delta 对冲频率为每日一次，现实中可能根据波动环境调整；
   - 高波动时期，对冲误差与 Gamma 暴露可能导致显著的非线性影响。

### 7. 扩展方向

未来可以在以下方向增强回测模块：

- 加入交易成本模型（固定费用 + 买卖价差 + 冲击成本）；
- 接入真实可转债与正股历史数据，处理日常数据清洗问题；
- 扩展为多只可转债组合，加入资金约束、风险预算与多因子选券；
- 引入更复杂的信用与利率模型，提高定价精度，研究模型误差对策略表现的影响。

本项目当前的回测架构刻意保持清晰和模块化，使得上述扩展都可以在不破坏核心代码结构的前提下逐步添加。

