from dataclasses import dataclass

import pandas as pd

from .cb_pricing import price_convertible_bond_binomial
from .params import ConvertibleBondContract, TermStructure, CreditCurve


@dataclass
class MispricingSignalConfig:
    lookback: int = 60
    entry_z: float = -1.5
    exit_z: float = -0.5


def compute_mispricing_series(
    cb_market_price: pd.Series,
    stock_price: pd.Series,
    contract: ConvertibleBondContract,
    r_curve: TermStructure,
    q_curve: TermStructure,
    credit_curve: CreditCurve,
    vol: float,
    steps: int,
) -> pd.DataFrame:
    """
    使用二叉树 fair value 与市场价格之差构造错定价时间序列。
    """
    if not cb_market_price.index.equals(stock_price.index):
        raise ValueError("cb_market_price 与 stock_price 的索引必须一致")

    fair_values = []
    for date, S_t in stock_price.items():
        fair, _ = price_convertible_bond_binomial(
            S0=float(S_t),
            contract=contract,
            steps=steps,
            vol=vol,
            r_curve=r_curve,
            q_curve=q_curve,
            credit_curve=credit_curve,
        )
        fair_values.append(fair)

    df = pd.DataFrame(
        {
            "cb_market": cb_market_price.values,
            "stock": stock_price.values,
            "cb_fair": fair_values,
        },
        index=cb_market_price.index,
    )
    df["mispricing"] = df["cb_fair"] - df["cb_market"]
    return df


def add_zscore_and_signals(
    df: pd.DataFrame,
    cfg: MispricingSignalConfig,
) -> pd.DataFrame:
    """
    为错定价序列添加 Z-score 与简单的“入场/离场”信号。
    signal 约定：
      - 1: 建立“多 CB + 空 Stock”的市场中性组合；
      - 0: 空仓。
    """
    if "mispricing" not in df.columns:
        raise ValueError("DataFrame 需包含列 'mispricing'")

    mp = df["mispricing"]
    rolling_mean = mp.rolling(cfg.lookback, min_periods=cfg.lookback // 2).mean()
    rolling_std = mp.rolling(cfg.lookback, min_periods=cfg.lookback // 2).std()

    df["zscore"] = (mp - rolling_mean) / rolling_std

    signal = []
    current_pos = 0
    for z in df["zscore"]:
        if current_pos == 0:
            if z < cfg.entry_z:
                current_pos = 1
        else:
            if z > cfg.exit_z:
                current_pos = 0
        signal.append(current_pos)

    df["signal"] = signal
    return df

