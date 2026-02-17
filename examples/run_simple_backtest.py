import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

from cb_arb.params import ConvertibleBondContract, TermStructure, CreditCurve
from cb_arb.signals import MispricingSignalConfig
from cb_arb.backtest import CBArbBacktester
from examples.utils import get_figures_dir, get_data_dir


def simulate_gbm_path(
    S0: float,
    r: float,
    q: float,
    vol: float,
    dates: pd.DatetimeIndex,
    seed: int = 42,
) -> pd.Series:
    """
    生成一条 GBM 股票价格路径，用于教学与回测演示。
    """
    dt = 1.0 / 252.0
    n = len(dates)

    rng = np.random.default_rng(seed)
    shocks = rng.normal(0.0, np.sqrt(dt), size=n)

    prices = [S0]
    for eps in shocks[1:]:
        s_prev = prices[-1]
        s_new = s_prev * np.exp((r - q - 0.5 * vol ** 2) * dt + vol * eps)
        prices.append(s_new)

    return pd.Series(prices, index=dates, name="stock")


def main():
    # 1) 构造模拟市场数据
    dates = pd.date_range("2020-01-01", periods=250, freq="B")
    S0 = 100.0
    r = 0.02
    q = 0.01
    vol = 0.25

    stock_series = simulate_gbm_path(S0, r, q, vol, dates)

    face = 100.0
    conversion_ratio = 1.0

    # 基于“纯债 + 折扣转股价值”生成一个理论可转债价格，并添加噪声作为市场价
    years = np.linspace(0.0, 1.0, len(dates))
    bond_floor = face * np.exp(-0.01 * years)
    conv_part = 0.4 * conversion_ratio * stock_series.values
    cb_theoretical = bond_floor + conv_part
    rng = np.random.default_rng(123)
    noise = 0.02 * rng.standard_normal(len(dates))
    cb_market = pd.Series(
        cb_theoretical * (1.0 + noise),
        index=dates,
        name="cb_market",
    )

    # 2) 构建可转债合约与期限结构
    contract = ConvertibleBondContract(
        face_value=face,
        coupon_rate=0.03,
        maturity=3.0,
        conversion_ratio=conversion_ratio,
        issue_price=100.0,
        call_price=None,
        put_price=None,
        coupon_freq=2,
    )

    r_curve = TermStructure(rate_fn=lambda t: r)
    q_curve = TermStructure(rate_fn=lambda t: q)
    credit_curve = CreditCurve(spread_fn=lambda t: 0.03)

    # 3) 策略与回测配置
    steps = 50
    signal_cfg = MispricingSignalConfig(
        lookback=40,
        entry_z=-1.5,
        exit_z=-0.5,
    )
    initial_cb_face = 100_000.0

    backtester = CBArbBacktester(
        contract=contract,
        r_curve=r_curve,
        q_curve=q_curve,
        credit_curve=credit_curve,
        vol=vol,
        steps=steps,
        signal_cfg=signal_cfg,
        initial_cb_face=initial_cb_face,
    )

    result = backtester.run(cb_market_price=cb_market, stock_price=stock_series)

    print(result[["mispricing", "zscore", "signal", "pnl", "cum_pnl"]].tail())

    # 保存回测结果数据到 CSV
    data_dir = get_data_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = data_dir / f"backtest_result_{timestamp}.csv"
    result.to_csv(csv_path, encoding='utf-8-sig')
    print(f"\n回测结果已保存到: {csv_path}")

    # 4) 画出累计收益与股票价格，用于观测市场中性效果
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(result.index, result["cum_pnl"], label="CB Arb Cum PnL", color="C0")
    ax1.set_ylabel("Cum PnL", color="C0")
    ax1.tick_params(axis="y", labelcolor="C0")

    ax2 = ax1.twinx()
    ax2.plot(stock_series.index, stock_series.values, label="Stock Price", color="C1", alpha=0.5)
    ax2.set_ylabel("Stock Price", color="C1")
    ax2.tick_params(axis="y", labelcolor="C1")

    fig.suptitle("Convertible Arbitrage Backtest (Simulated Data)")
    fig.tight_layout()
    
    # 保存图片
    figures_dir = get_figures_dir()
    fig_path = figures_dir / f"backtest_result_{timestamp}.png"
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    print(f"图片已保存到: {fig_path}")
    
    plt.show()


if __name__ == "__main__":
    main()

