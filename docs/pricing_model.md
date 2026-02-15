## 可转债二叉树定价模型与风险中性测度（定价模型说明）

本节对应代码模块 `src/cb_arb/cb_pricing.py`，目标是以数学博士视角梳理模型假设和数值实现。

### 1. 价格过程与基本假设

1. **标的股票价格过程**

假设标的股票价格 \(S_t\) 服从带股利的几何布朗运动（GBM）：

\[
dS_t = (r(t) - q(t)) S_t\,dt + \sigma(t) S_t\,dW_t,
\]

其中：

- \(r(t)\)：无风险利率（可由 `TermStructure` 给出）；
- \(q(t)\)：股利率 / 股息收益率（可由 `TermStructure` 给出）；
- \(\sigma(t)\)：波动率（在本项目初版中取常数 \(\sigma\)，可扩展为期限结构）。

2. **信用风险与折现**

可转债的现金流受发行人信用风险影响。为保持模型可实现性，我们在初版中采用：

- 给定信用利差曲线 \(s(t)\)（由 `CreditCurve` 提供）；
- 对无风险贴现率 \(r(t)\) 做线性修正，得到「有效贴现率」：
  \[
  r_{\text{eff}}(t) = r(t) + s(t).
  \]

在更高阶模型中，可以引入违约强度 \(\lambda(t)\) 与回收率 \(R\)，构建显式违约树；本项目保留这一扩展空间。

### 2. CRR 二叉树构造

在时间区间 \([0,T]\) 上，将到期时间 \(T\) 划分为 \(N\) 个等长步长 \(\Delta t = T/N\)。  
在每个步长内，股票价格只能「上涨」或「下跌」：

\[
S_{t+\Delta t} =
\begin{cases}
  S_t u, & \text{概率 } p, \\
  S_t d, & \text{概率 } 1-p,
\end{cases}
\]

其中：

\[
u = e^{\sigma \sqrt{\Delta t}}, \quad d = \frac{1}{u}.
\]

在风险中性测度 \(\mathbb{Q}\) 下，贴现后的股票价格是鞅：

\[
\mathbb{E}^{\mathbb{Q}}\left[\frac{S_{t+\Delta t}}{S_t} \mid \mathcal{F}_t \right]
  = e^{(r - q)\Delta t}.
\]

代入二叉树上的离散动态，可得：

\[
p u + (1-p)d = e^{(r - q)\Delta t},
\]

从而得到风险中性概率：

\[
p = \frac{e^{(r - q)\Delta t} - d}{u - d}.
\]

在实现中，我们在 `build_stock_tree` 中对 \(u,d,p\) 做如下处理：

- 使用输入波动率 \(\sigma\) 与步长 \(\Delta t\) 构造 \(u,d\)；
- 使用 `TermStructure` 在 \(t=0\) 处近似取 \(r(0), q(0)\)，得到 \(p\)；
- 检查 \(p \in (0,1)\)，以避免数值上不合理的参数组合。

### 3. 可转债现金流与节点价值

一只可转债在现金流层面主要包含：

1. **票息**：
   - 面值 \(N\)，年化票息率 \(c\)，每年支付频率 \(m\)；
   - 每次支付金额为：\(\text{Coupon} = N \cdot c / m\)；
   - 支付时间为 \(\{t_k\}\)，在数值实现中通过判断当前时间是否接近某个票息日来决定是否在节点上加上票息。

2. **到期偿付**：
   - 持有至到期且不转股、不被赎回/回售时：收到 \(N + \text{最后一次票息}\)。

3. **转换价值**：
   - 在任意可转股时刻，持有人有权以转换比例 \(\text{CR}\) 将债券转换为股票；
   - 转股价值为：
     \[
     \text{ConvValue}_t = \text{CR} \cdot S_t.
     \]

4. **赎回 / 回售条款**：
   - 发行人赎回价 \(\text{CallPrice}\) 及触发条件（通常与股票价格或剩余期限相关）；
   - 投资人回售价 \(\text{PutPrice}\) 及触发条件；
   - 在数值上表现为：当条件满足时，节点上可选择「立即以赎回/回售价结束合约」。

#### 3.1 到期节点价值

在到期时刻 \(T\)，对于任一节点上的股票价格 \(S_T\)，可转债价值为：

\[
V_T = \max\left\{
  N + \text{Coupon}_{\text{last}},
  \text{CR} \cdot S_T,
  \text{CallPrice（如适用）},
  \text{PutPrice（如适用）}
\right\}.
\]

这在代码中对应于对 `bond_redemption`、`conv_value`、`call_price`、`put_price` 的取最大操作。

#### 3.2 非终端节点的向后递推

对任一时间 \(t_i\) 上的节点，设其在下一时间步的「向上 / 向下」节点可转债价值分别为 \(V_u, V_d\)。  
在不考虑立即行权的情况下，「继续持有债券」的期望价值为：

\[
V_{\text{cont}}(t_i) = e^{-(r_{\text{eff}}(t_i)) \Delta t}\left(p V_u + (1-p) V_d\right) + \text{Coupon}_i,
\]

其中：

- \(r_{\text{eff}}(t_i) = r(t_i) + s(t_i)\)；
- 若 \(t_i\) 是票息支付时点，则 \(\text{Coupon}_i = N \cdot c / m\)，否则为 0。

然后，考虑可转债在该节点上的其他行权选择：

- **立即转股**：价值为 \(\text{CR} \cdot S_{t_i}\)；
- **立即赎回/回售**：若触发条件满足，则价值为相应的赎回/回售价；

综上，节点价值为：

\[
V(t_i) = \max\left\{
  V_{\text{cont}}(t_i),
  \text{CR} \cdot S_{t_i},
  \text{CallPrice（触发时）},
  \text{PutPrice（触发时）}
\right\}.
\]

这与代码中对 `values = [continuation_value, conv_value, ...]` 取 `max(values)` 一一对应。

### 4. Delta 的有限差分估计

在离散二叉树框架下，Delta 通常用根节点上一层的有限差分来近似：

\[
\Delta_{\text{CB}}(S_0) \approx \frac{V_u - V_d}{S_u - S_d},
\]

其中：

- \(V_u\)：在第一步「股价上涨」对应节点上的可转债价值；
- \(V_d\)：在第一步「股价下跌」对应节点上的可转债价值；
- \(S_u, S_d\)：对应的股票价格。

在实现中：

- 我们在整棵树回溯完成之后，从 `cb_tree[1, 0]` 与 `cb_tree[1, 1]` 取值作为 \(V_u, V_d\)；
- 对应的股票价格来自 `stock_tree[1, 0]` 与 `stock_tree[1, 1]`；
- 用该 Delta 作为可转债相对于股票的局部线性敏感度基础，为后续 Delta 对冲提供输入。

### 5. 与代码实现的对应关系

- `build_stock_tree`：
  - 输入：\(S_0, T, N, \sigma, r(\cdot), q(\cdot)\)；
  - 输出：股票价格树 `stock_tree` 及 \(u, d, p, \Delta t\)；
  - 数学对应：构建离散 GBM 路径与风险中性概率。

- `price_convertible_bond_binomial`：
  - 初始化终端节点：按「面值+最后票息 / 转股 / 赎回 / 回售」取最大；
  - 逐层向前递推：
    - 计算 \(V_{\text{cont}}(t_i)\)；
    - 与转股价值和赎回/回售价比较取最大；
  - 在根节点上一层计算有限差分 Delta。

通过这一实现路径，我们在代码层面构建了一套**与风险中性定价理论和可转债结构严格对应**的数值定价器，为后续 Delta 对冲和市场中性策略提供了坚实的数学基础。

