"""
测试信号模块
"""
import numpy as np
import pandas as pd
import pytest

from cb_arb.params import ConvertibleBondContract, TermStructure, CreditCurve
from cb_arb.signals import (
    compute_mispricing_series,
    add_zscore_and_signals,
    MispricingSignalConfig,
)


def _make_contract():
    return ConvertibleBondContract(
        face_value=100.0,
        coupon_rate=0.03,
        maturity=3.0,
        conversion_ratio=1.0,
        issue_price=100.0,
        coupon_freq=2,
    )


def _make_curves():
    return (
        TermStructure(rate_fn=lambda t: 0.02),
        TermStructure(rate_fn=lambda t: 0.01),
        CreditCurve(spread_fn=lambda t: 0.03),
    )


class TestComputeMispricingSeries:
    def test_output_columns_and_index(self):
        dates = pd.date_range("2020-01-01", periods=20, freq="B")
        stock = pd.Series(100.0, index=dates)
        cb_market = pd.Series(99.0, index=dates)
        r_curve, q_curve, credit_curve = _make_curves()
        df = compute_mispricing_series(
            cb_market_price=cb_market,
            stock_price=stock,
            contract=_make_contract(),
            r_curve=r_curve,
            q_curve=q_curve,
            credit_curve=credit_curve,
            vol=0.25,
            steps=50,
        )
        assert df.index.equals(dates)
        assert "cb_market" in df.columns
        assert "stock" in df.columns
        assert "cb_fair" in df.columns
        assert "mispricing" in df.columns
        assert (df["mispricing"] == df["cb_fair"] - df["cb_market"]).all()

    def test_index_mismatch_raises(self):
        dates1 = pd.date_range("2020-01-01", periods=10, freq="B")
        dates2 = pd.date_range("2020-01-02", periods=10, freq="B")
        stock = pd.Series(100.0, index=dates1)
        cb_market = pd.Series(99.0, index=dates2)
        r_curve, q_curve, credit_curve = _make_curves()
        with pytest.raises(ValueError):
            compute_mispricing_series(
                cb_market_price=cb_market,
                stock_price=stock,
                contract=_make_contract(),
                r_curve=r_curve,
                q_curve=q_curve,
                credit_curve=credit_curve,
                vol=0.25,
                steps=50,
            )


class TestAddZscoreAndSignals:
    def test_adds_zscore_and_signal(self):
        dates = pd.date_range("2020-01-01", periods=100, freq="B")
        np.random.seed(42)
        mispricing = np.random.randn(100).cumsum() * 0.1 + 1.0
        df = pd.DataFrame({"mispricing": mispricing}, index=dates)
        cfg = MispricingSignalConfig(lookback=20, entry_z=-1.5, exit_z=-0.5)
        out = add_zscore_and_signals(df, cfg)
        assert "zscore" in out.columns
        assert "signal" in out.columns
        assert out["signal"].isin([0, 1]).all()

    def test_requires_mispricing_column(self):
        df = pd.DataFrame({"x": [1, 2, 3]})
        cfg = MispricingSignalConfig()
        with pytest.raises(ValueError):
            add_zscore_and_signals(df, cfg)
