## Delta 对冲与市场中性组合（Delta Hedging）

本节对应代码模块 `src/cb_arb/delta_hedging.py`，目标是在数学上澄清 Delta 对冲的原理，并说明本项目中的近似与实现选择。

### 1. Delta 的含义与线性近似

对于依赖标的价格 \(S_t\) 的任何金融合约，其价值可写作 \(V(S_t, t, \theta)\)，其中 \(\theta\) 表示其他参数。
在短期内（假设其他因素近似不变），可以对 \(V\) 在 \(S_t\) 附近做一阶泰勒展开：

\[
V(S_t + \Delta S, t) \approx V(S_t, t) + \frac{\partial V}{\partial S}(S_t, t) \cdot \Delta S.
\]

这里的一阶导数：

\[
\Delta_V(S_t, t) := \frac{\partial V}{\partial S}(S_t, t)
\]

就是我们常说的「**Delta**」——合约价值对标的价格的小变动的线性敏感度。

对于一只可转债，其价值 \(V_{\text{CB}}(S_t, t)\) 来自「纯债 + 转股期权 + 条款效应」的综合，Delta 通常主要由**隐含的期权部分**贡献。

### 2. 组合 Delta 与中性条件

考虑一个两腿组合：

- 多头：名义为 \(N_{\text{CB}}\) 的可转债；
- 空头：卖空 \(n_{\text{stock}}\) 股标的股票；

则组合价值为：

\[
\Pi_t = N_{\text{CB}} \cdot V_{\text{CB}}(S_t, t) - n_{\text{stock}} \cdot S_t.
\]

对 \(S_t\) 求导，得到组合的 Delta：

\[
\Delta_{\Pi}(S_t, t)
  = N_{\text{CB}} \cdot \Delta_{\text{CB}}(S_t, t) - n_{\text{stock}}.
\]

要使组合在一阶意义上对股票价格变动「中性」，希望：

\[
\Delta_{\Pi}(S_t, t) \approx 0 \quad \Rightarrow \quad
n_{\text{stock}}^{\star} \approx N_{\text{CB}} \cdot \Delta_{\text{CB}}(S_t, t).
\]

在本项目中，我们进一步将 \(N_{\text{CB}}\) 表示为「持有的可转债总面值」（例如 100,000）与每张债的面值（例如 100）的比值：

\[
N_{\text{CB}} = \frac{\text{CB\_face\_total}}{\text{face\_value\_per\_bond}}.
\]

然后组合对冲股数约为：

\[
n_{\text{stock}}^{\star} \approx
\frac{\text{CB\_face\_total}}{\text{face\_value\_per\_bond}}
\cdot \Delta_{\text{CB}}(S_t, t).
\]

在实现中，我们将这一因子简化为「名义面值 * Delta / 股价」，体现为：

\[
\text{hedge\_shares} \approx \frac{\text{notional} \cdot \Delta_{\text{CB}}}{S_t},
\]

从而得到“需要卖空的股票股数”。

### 3. 二叉树中的 Delta 估计

在 `cb_pricing.py` 中，我们通过根节点上一层的有限差分来近似 Delta：

\[
\Delta_{\text{CB}}(S_0, 0) \approx \frac{V_u - V_d}{S_u - S_d},
\]

其中：

- \(V_u, V_d\) 是在「第一步向上 / 向下」节点上的可转债价值；
- \(S_u, S_d\) 是对应的股票价格。

从数值精度角度看，这种离散近似在步长足够小时会收敛到连续时间模型中的解析 Delta。

### 4. 动态 Delta 对冲（Daily Rebalancing）

理论上，为了维持组合的 Delta 中性，需要在每一个无穷小时间间隔 \(dt\) 内不断调整仓位，这在现实中是不可能的。

实际操作中（以及本项目的回测设置中），我们采用每日再平衡（或更粗粒度，如每周）：

1. 在每个交易日 \(t_i\)：
   - 用当日股票价格 \(S_{t_i}\) 对可转债重新定价，求得 \(V_{\text{CB}}(S_{t_i}, t_i)\) 与 \(\Delta_{\text{CB}}(S_{t_i}, t_i)\)；
   - 根据新的 Delta 计算对冲股数 \(n_{\text{stock}}^{\star}(t_i)\)；
   - 调整卖空（或回补）股票数量，使得新的组合 Delta 接近 0。
2. 组合价值更新为：
   \[
   \Pi_{t_i} = \text{CB\_price}(t_i) - n_{\text{stock}}^{\star}(t_i) \cdot S_{t_i}.
   \]

在本项目的 `DeltaHedger.run_daily_hedging` 中，我们对给定的股票价格时间序列执行上述过程，并记录每一日的：

- `cb_price`：组合中可转债头寸的市值；
- `cb_delta`：可转债 Delta；
- `hedge_shares`：卖空股数；
- `portfolio_value`：市场中性组合的总价值 \(\Pi_{t_i}\)。

### 5. 对冲误差与 Gamma / Vega 暴露

值得强调的是：

- Delta 对冲只能在一阶近似下消除对 \(S_t\) 的线性敏感度；
- 组合仍然暴露于二阶及更高阶的敏感度（Gamma、Vega 等）。

例如：

\[
V(S_t + \Delta S, t)
  \approx V(S_t, t)
  + \Delta_{\text{CB}} \Delta S
  + \frac{1}{2} \Gamma_{\text{CB}} (\Delta S)^2
  + \cdots,
\]

在 Delta 对冲后，组合主要暴露在 \(\Gamma\) 和波动率等因素上：

- 当实际波动率与模型假设不匹配时，组合可能获得「波动率套利」型收益或损失；
- 当股价单边大幅移动时，二阶项会显著影响 PnL。

Edward Thorp 的实践表明：

- 在合适的参数估计、合理的对冲频率以及审慎的杠杆控制下，Delta 对冲可以有效地将中长期收益的主要来源集中在「定价错误 + 波动交易」上，而较少依赖纯粹的方向判断。

### 6. 本项目 Delta 对冲实现的局限与扩展方向

当前实现中的主要简化包括：

1. **时间维度简化**  
   - 在 `DeltaHedger.run_daily_hedging` 中，我们将每次定价视为在相同的到期结构下进行（忽略「到期时间滚动减少」的影响），以突出「Delta 函数形式」本身；
   - 更严谨的版本可以将当前时间 \(t_i\) 显式传入定价函数，让树的总步数或剩余期限随时间推移而变化。

2. **交易成本与滑点**  
   - 当前组合价值未显式扣减交易佣金、买卖价差与冲击成本；
   - 在现实中，高频再平衡会显著增加成本，需要在策略评估中加入这些因素。

3. **离散对冲频率**  
   - 组合在两次对冲之间仍然受未对冲的 Delta 暴露影响，尤其在剧烈波动日；
   - 可以通过敏感性分析、改变对冲频率等方式，探索「对冲频率 vs 收益 / 风险」的权衡。

这些扩展在本项目中保留了接口空间，未来可以在不破坏现有结构的前提下逐步加入。

