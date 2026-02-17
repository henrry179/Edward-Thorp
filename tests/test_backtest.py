"""
测试回测模块
"""
import numpy as np
import pandas as pd
import pytest

from cb_arb.params import ConvertibleBondContract, TermStructure, CreditCurve
from cb_arb.signals import MispricingSignalConfig
from cb_arb.backtest import CBArbBacktester


def _simulate_gbm_path(S0, r, q, vol, dates, seed=42):
    dt = 1.0 / 252.0
    n = len(dates)
    rng = np.random.default_rng(seed)
    shocks = rng.normal(0.0, np.sqrt(dt), size=n)
    prices = [S0]
    for eps in shocks[1:]:
        s_prev = prices[-1]
        s_new = s_prev * np.exp((r - q - 0.5 * vol**2) * dt + vol * eps)
        prices.append(s_new)
    return pd.Series(prices, index=dates, name="stock")


def _make_cb_market(stock_series, face=100.0, conversion_ratio=1.0, seed=123):
    years = np.linspace(0.0, 1.0, len(stock_series))
    bond_floor = face * np.exp(-0.01 * years)
    conv_part = 0.4 * conversion_ratio * stock_series.values
    cb_theoretical = bond_floor + conv_part
    rng = np.random.default_rng(seed)
    noise = 0.02 * rng.standard_normal(len(stock_series))
    return pd.Series(
        cb_theoretical * (1.0 + noise),
        index=stock_series.index,
        name="cb_market",
    )


def _make_backtester():
    contract = ConvertibleBondContract(
        face_value=100.0,
        coupon_rate=0.03,
        maturity=3.0,
        conversion_ratio=1.0,
        issue_price=100.0,
        call_price=None,
        put_price=None,
        coupon_freq=2,
    )
    r_curve = TermStructure(rate_fn=lambda t: 0.02)
    q_curve = TermStructure(rate_fn=lambda t: 0.01)
    credit_curve = CreditCurve(spread_fn=lambda t: 0.03)
    signal_cfg = MispricingSignalConfig(lookback=40, entry_z=-1.5, exit_z=-0.5)
    return CBArbBacktester(
        contract=contract,
        r_curve=r_curve,
        q_curve=q_curve,
        credit_curve=credit_curve,
        vol=0.25,
        steps=50,
        signal_cfg=signal_cfg,
        initial_cb_face=100_000.0,
    )


class TestCBArbBacktester:
    def test_run_returns_dataframe_with_expected_columns(self):
        dates = pd.date_range("2020-01-01", periods=100, freq="B")
        stock = _simulate_gbm_path(100.0, 0.02, 0.01, 0.25, dates)
        cb_market = _make_cb_market(stock)
        backtester = _make_backtester()
        result = backtester.run(cb_market_price=cb_market, stock_price=stock)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 100
        for col in ["mispricing", "zscore", "signal", "pnl", "cum_pnl"]:
            assert col in result.columns
        assert result["signal"].isin([0, 1]).all()
        assert abs(result["cum_pnl"].iloc[-1] - result["pnl"].sum()) < 1e-6

    def test_run_cum_pnl_is_cumsum_of_pnl(self):
        dates = pd.date_range("2020-01-01", periods=50, freq="B")
        stock = _simulate_gbm_path(100.0, 0.02, 0.01, 0.25, dates)
        cb_market = _make_cb_market(stock)
        backtester = _make_backtester()
        result = backtester.run(cb_market_price=cb_market, stock_price=stock)
        cum_pnl = result["cum_pnl"].values
        pnl_cumsum = result["pnl"].fillna(0).values.cumsum()
        np.testing.assert_allclose(cum_pnl, pnl_cumsum, rtol=1e-9, atol=1e-9)
