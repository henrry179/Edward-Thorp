from dataclasses import dataclass

import pandas as pd

from .delta_hedging import DeltaHedger
from .params import ConvertibleBondContract, TermStructure, CreditCurve
from .signals import (
    MispricingSignalConfig,
    compute_mispricing_series,
    add_zscore_and_signals,
)


@dataclass
class DailyPnL:
    date: pd.Timestamp
    portfolio_value: float
    pnl: float
    position: int


class CBArbBacktester:
    """
    严谨版可转债套利策略回测器：
    - 利用树模型定价 + 错定价 Z-score 信号
    - 在 signal==1 的时期维持 Delta 对冲仓位
    - signal==0 的时期空仓
    """

    def __init__(
        self,
        contract: ConvertibleBondContract,
        r_curve: TermStructure,
        q_curve: TermStructure,
        credit_curve: CreditCurve,
        vol: float,
        steps: int,
        signal_cfg: MispricingSignalConfig,
        initial_cb_face: float,
    ):
        self.contract = contract
        self.r_curve = r_curve
        self.q_curve = q_curve
        self.credit_curve = credit_curve
        self.vol = vol
        self.steps = steps
        self.signal_cfg = signal_cfg
        self.initial_cb_face = initial_cb_face

    def run(
        self,
        cb_market_price: pd.Series,
        stock_price: pd.Series,
    ) -> pd.DataFrame:
        """
        回测整体流程：
        1. 计算 fair value 与 mispricing、Z-score、signal；
        2. 使用 DeltaHedger 对股票路径进行日频对冲，得到“原始组合价值轨迹”；
        3. 对 signal==1 的日期启用该组合价值，signal==0 的日期组合价值视为 0；
        4. 由组合价值差分得到每日 PnL 与累计 PnL。
        """
        df = compute_mispricing_series(
            cb_market_price,
            stock_price,
            self.contract,
            self.r_curve,
            self.q_curve,
            self.credit_curve,
            self.vol,
            self.steps,
        )
        df = add_zscore_and_signals(df, self.signal_cfg)

        hedger = DeltaHedger(
            contract=self.contract,
            r_curve=self.r_curve,
            q_curve=self.q_curve,
            credit_curve=self.credit_curve,
            vol=self.vol,
            steps=self.steps,
            initial_cb_face=self.initial_cb_face,
        )

        hedge_history = hedger.run_daily_hedging(stock_price)
        hedge_df = pd.DataFrame(
            {
                "date": [h.date for h in hedge_history],
                "portfolio_value_raw": [h.portfolio_value for h in hedge_history],
            }
        ).set_index("date")

        portfolio_values = []
        prev_value = 0.0

        for date, row in df.iterrows():
            signal = int(row["signal"])

            if signal == 1:
                pv = float(hedge_df.loc[date, "portfolio_value_raw"])
            else:
                pv = 0.0

            pnl = pv - prev_value
            portfolio_values.append(
                {
                    "date": date,
                    "portfolio_value": pv,
                    "pnl": pnl,
                    "position": signal,
                }
            )
            prev_value = pv

        pnl_df = pd.DataFrame(portfolio_values).set_index("date")
        pnl_df["cum_pnl"] = pnl_df["pnl"].cumsum()

        # 将信号和 PnL 信息并入结果，便于分析
        return df.join(pnl_df, how="left")

