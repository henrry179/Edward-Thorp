"""
测试 Delta 对冲模块
"""
import numpy as np
import pandas as pd
import pytest

from cb_arb.params import ConvertibleBondContract, TermStructure, CreditCurve
from cb_arb.delta_hedging import DeltaHedger, HedgeState


def _make_contract():
    return ConvertibleBondContract(
        face_value=100.0,
        coupon_rate=0.03,
        maturity=3.0,
        conversion_ratio=1.0,
        issue_price=100.0,
        coupon_freq=2,
    )


def _make_curves(r=0.02, q=0.01, spread=0.03):
    return (
        TermStructure(rate_fn=lambda t: r),
        TermStructure(rate_fn=lambda t: q),
        CreditCurve(spread_fn=lambda t: spread),
    )


class TestDeltaHedger:
    def test_compute_hedge_ratio(self):
        r_curve, q_curve, credit_curve = _make_curves()
        hedger = DeltaHedger(
            contract=_make_contract(),
            r_curve=r_curve,
            q_curve=q_curve,
            credit_curve=credit_curve,
            vol=0.25,
            steps=50,
            initial_cb_face=100_000.0,
        )
        # Delta=0.5, 面值 100000, 股价 100 -> 对冲股数 = 100000 * 0.5 / 100 = 500
        shares = hedger.compute_hedge_ratio(cb_delta=0.5, stock_price=100.0)
        assert abs(shares - 500.0) < 1e-6

    def test_compute_hedge_ratio_invalid_price(self):
        r_curve, q_curve, credit_curve = _make_curves()
        hedger = DeltaHedger(
            contract=_make_contract(),
            r_curve=r_curve,
            q_curve=q_curve,
            credit_curve=credit_curve,
            vol=0.25,
            steps=50,
            initial_cb_face=100_000.0,
        )
        with pytest.raises(ValueError):
            hedger.compute_hedge_ratio(cb_delta=0.5, stock_price=0.0)

    def test_run_daily_hedging_returns_list_of_hedge_state(self):
        r_curve, q_curve, credit_curve = _make_curves()
        hedger = DeltaHedger(
            contract=_make_contract(),
            r_curve=r_curve,
            q_curve=q_curve,
            credit_curve=credit_curve,
            vol=0.25,
            steps=50,
            initial_cb_face=100_000.0,
        )
        dates = pd.date_range("2020-01-01", periods=10, freq="B")
        stock_series = pd.Series(100.0 + np.arange(10) * 0.5, index=dates)
        history = hedger.run_daily_hedging(stock_series)
        assert len(history) == 10
        for h in history:
            assert isinstance(h, HedgeState)
            assert h.cb_position_face == 100_000.0
            assert h.stock_price > 0
            assert h.hedge_shares >= 0
