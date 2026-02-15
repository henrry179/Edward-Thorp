import math
from typing import Tuple

import numpy as np

from .params import ConvertibleBondContract, TermStructure, CreditCurve


def build_stock_tree(
    S0: float,
    maturity: float,
    steps: int,
    vol: float,
    r_curve: TermStructure,
    q_curve: TermStructure,
) -> Tuple[np.ndarray, float, float, float, float]:
    """
    使用 CRR 二叉树构建股票价格树。

    返回:
        stock_tree: 形状 (steps+1, steps+1)，第 i 行、j 列代表 t=i*dt, j 次向下跳的价格
        u, d, p, dt: 分别为向上因子、向下因子、风险中性概率、时间步长
    """
    if steps <= 0:
        raise ValueError("steps 必须为正整数")

    dt = maturity / steps
    if dt <= 0:
        raise ValueError("dt 必须为正")

    u = math.exp(vol * math.sqrt(dt))
    d = 1.0 / u

    r0 = r_curve.r(0.0)
    q0 = q_curve.r(0.0)

    disc_gross = math.exp((r0 - q0) * dt)
    p = (disc_gross - d) / (u - d)
    if not (0.0 < p < 1.0):
        raise ValueError(f"风险中性概率不在 (0,1): p={p}")

    stock_tree = np.zeros((steps + 1, steps + 1), dtype=float)
    stock_tree[0, 0] = S0
    for i in range(1, steps + 1):
        stock_tree[i, 0] = stock_tree[i - 1, 0] * u
        for j in range(1, i + 1):
            stock_tree[i, j] = stock_tree[i - 1, j - 1] * d

    return stock_tree, u, d, p, dt


def price_convertible_bond_binomial(
    S0: float,
    contract: ConvertibleBondContract,
    steps: int,
    vol: float,
    r_curve: TermStructure,
    q_curve: TermStructure,
    credit_curve: CreditCurve,
) -> Tuple[float, float]:
    """
    使用二叉树对可转债定价，返回 (价格, 在 S0 处的 Delta)。

    严谨特征：
    - 股票价格服从 GBM，在 CRR 树上离散；
    - 票息以 coupon_freq 指定的频率支付；
    - 到期支付面值及最后票息；
    - 每个节点均考虑“继续持有债券 vs 转股 vs 赎回/回售”的最优决策；
    - 信用风险通过信用利差近似折现 (r + spread) 进入；
    - Delta 通过根节点上一层的有限差分 (V_u - V_d)/(S_u - S_d) 估算。
    """
    face_value = contract.face_value
    T = contract.maturity
    coupon_rate = contract.coupon_rate
    m = contract.coupon_freq
    if m <= 0:
        raise ValueError("coupon_freq 必须为正整数")

    dt_coupon = 1.0 / m
    coupon_amount = face_value * coupon_rate / m

    stock_tree, u, d, p, dt = build_stock_tree(S0, T, steps, vol, r_curve, q_curve)

    def discount_factor(t: float) -> float:
        r_t = r_curve.r(t)
        s_t = credit_curve.spread(t)
        return math.exp(-(r_t + s_t) * dt)

    cb_tree = np.zeros_like(stock_tree)

    last_step = steps
    for j in range(last_step + 1):
        S_T = stock_tree[last_step, j]
        conv_value = contract.conversion_ratio * S_T
        bond_redemption = face_value + coupon_amount
        values = [bond_redemption, conv_value]

        if contract.call_price is not None:
            values.append(contract.call_price)
        if contract.put_price is not None:
            values.append(contract.put_price)

        cb_tree[last_step, j] = max(values)

    for i in range(last_step - 1, -1, -1):
        t = i * dt
        # “是否恰逢票息支付时点”的判断，会有一定数值误差，这里用近似比较
        is_coupon_time = math.isclose((T - t) % dt_coupon, 0.0, abs_tol=1e-8)

        for j in range(i + 1):
            S_ij = stock_tree[i, j]

            continuation_value = (
                discount_factor(t)
                * (p * cb_tree[i + 1, j] + (1.0 - p) * cb_tree[i + 1, j + 1])
            )

            if is_coupon_time:
                continuation_value += coupon_amount

            conv_value = contract.conversion_ratio * S_ij
            values = [continuation_value, conv_value]

            if (
                contract.call_price is not None
                and contract.call_barrier is not None
                and S_ij >= contract.call_barrier
            ):
                values.append(contract.call_price)

            if (
                contract.put_price is not None
                and contract.put_barrier is not None
                and S_ij <= contract.put_barrier
            ):
                values.append(contract.put_price)

            cb_tree[i, j] = max(values)

    V_u = cb_tree[1, 0]
    V_d = cb_tree[1, 1]
    S_u = stock_tree[1, 0]
    S_d = stock_tree[1, 1]
    delta = (V_u - V_d) / (S_u - S_d)

    price = cb_tree[0, 0]
    return float(price), float(delta)

