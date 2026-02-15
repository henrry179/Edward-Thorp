from dataclasses import dataclass
from typing import List

import pandas as pd

from .cb_pricing import price_convertible_bond_binomial
from .params import ConvertibleBondContract, TermStructure, CreditCurve


@dataclass
class HedgeState:
    date: pd.Timestamp
    cb_position_face: float
    stock_price: float
    cb_price: float
    cb_delta: float
    hedge_shares: float
    portfolio_value: float


class DeltaHedger:
    """
    基于严格可转债定价结果进行 Delta 对冲的引擎。
    """

    def __init__(
        self,
        contract: ConvertibleBondContract,
        r_curve: TermStructure,
        q_curve: TermStructure,
        credit_curve: CreditCurve,
        vol: float,
        steps: int,
        initial_cb_face: float,
    ):
        self.contract = contract
        self.r_curve = r_curve
        self.q_curve = q_curve
        self.credit_curve = credit_curve
        self.vol = vol
        self.steps = steps
        self.initial_cb_face = initial_cb_face

    def compute_hedge_ratio(self, cb_delta: float, stock_price: float) -> float:
        """
        使用 CB Delta 计算需要卖空的股票股数。
        为教学简化，直接用面值作为名义，不考虑脏价与应计利息。
        """
        if stock_price <= 0:
            raise ValueError("stock_price 必须为正")
        notional = self.initial_cb_face
        hedge_shares = (notional * cb_delta) / stock_price
        return hedge_shares

    def run_daily_hedging(
        self,
        stock_series: pd.Series,
    ) -> List[HedgeState]:
        """
        对一条股票价格时间序列执行日频 Delta 对冲模拟。

        注意：这里为了突出“定价-对冲”链路，将定价时间 t 近似为 0，
        即认为各日重新定价时，剩余到期时间一致，便于教学。
        更严谨的版本可以将时间 t 显式传入定价函数。
        """
        history: List[HedgeState] = []
        cb_face = self.initial_cb_face

        hedge_shares = 0.0
        for date, S_t in stock_series.items():
            price, delta = price_convertible_bond_binomial(
                S0=S_t,
                contract=self.contract,
                steps=self.steps,
                vol=self.vol,
                r_curve=self.r_curve,
                q_curve=self.q_curve,
                credit_curve=self.credit_curve,
            )

            cb_price = price * (cb_face / self.contract.face_value)
            hedge_shares = self.compute_hedge_ratio(delta, S_t)
            portfolio_value = cb_price - hedge_shares * S_t

            state = HedgeState(
                date=pd.Timestamp(date),
                cb_position_face=cb_face,
                stock_price=float(S_t),
                cb_price=float(cb_price),
                cb_delta=float(delta),
                hedge_shares=float(hedge_shares),
                portfolio_value=float(portfolio_value),
            )
            history.append(state)

        return history

