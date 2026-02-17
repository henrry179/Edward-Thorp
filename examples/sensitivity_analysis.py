"""
参数敏感性分析示例

展示不同参数（波动率、利率、信用利差等）对可转债价格和 Delta 的影响。
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

from cb_arb.params import ConvertibleBondContract, TermStructure, CreditCurve
from cb_arb.cb_pricing import price_convertible_bond_binomial
from examples.utils import get_figures_dir, get_data_dir


def analyze_volatility_sensitivity():
    """分析波动率敏感性"""
    contract = ConvertibleBondContract(
        face_value=100.0,
        coupon_rate=0.03,
        maturity=3.0,
        conversion_ratio=1.0,
        issue_price=100.0,
        coupon_freq=2,
    )
    
    r_curve = TermStructure(rate_fn=lambda t: 0.02)
    q_curve = TermStructure(rate_fn=lambda t: 0.01)
    credit_curve = CreditCurve(spread_fn=lambda t: 0.03)
    
    S0 = 100.0
    volatilities = np.linspace(0.10, 0.50, 20)
    prices = []
    deltas = []
    
    for vol in volatilities:
        price, delta = price_convertible_bond_binomial(
            S0=S0,
            contract=contract,
            steps=50,
            vol=vol,
            r_curve=r_curve,
            q_curve=q_curve,
            credit_curve=credit_curve,
        )
        prices.append(price)
        deltas.append(delta)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    ax1.plot(volatilities, prices, 'b-', linewidth=2)
    ax1.set_xlabel('波动率')
    ax1.set_ylabel('可转债价格')
    ax1.set_title('可转债价格 vs 波动率')
    ax1.grid(True, alpha=0.3)
    
    ax2.plot(volatilities, deltas, 'g-', linewidth=2)
    ax2.set_xlabel('波动率')
    ax2.set_ylabel('Delta')
    ax2.set_title('Delta vs 波动率')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 保存图片
    figures_dir = get_figures_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fig_path = figures_dir / f"volatility_sensitivity_{timestamp}.png"
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    print(f"图片已保存到: {fig_path}")
    
    # 保存数据
    data_dir = get_data_dir()
    data_df = pd.DataFrame({
        'volatility': volatilities,
        'price': prices,
        'delta': deltas
    })
    csv_path = data_dir / f"volatility_sensitivity_{timestamp}.csv"
    data_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"数据已保存到: {csv_path}")
    
    plt.show()
    
    print("观察：")
    print("- 波动率越高，期权价值越大，可转债价格越高")
    print("- Delta 对波动率的敏感性取决于股价相对于转换价格的位置")


def analyze_interest_rate_sensitivity():
    """分析利率敏感性"""
    contract = ConvertibleBondContract(
        face_value=100.0,
        coupon_rate=0.03,
        maturity=3.0,
        conversion_ratio=1.0,
        issue_price=100.0,
        coupon_freq=2,
    )
    
    q_curve = TermStructure(rate_fn=lambda t: 0.01)
    credit_curve = CreditCurve(spread_fn=lambda t: 0.03)
    
    S0 = 100.0
    vol = 0.25
    interest_rates = np.linspace(0.00, 0.06, 20)
    prices = []
    deltas = []
    
    for r in interest_rates:
        r_curve = TermStructure(rate_fn=lambda t: r)
        price, delta = price_convertible_bond_binomial(
            S0=S0,
            contract=contract,
            steps=50,
            vol=vol,
            r_curve=r_curve,
            q_curve=q_curve,
            credit_curve=credit_curve,
        )
        prices.append(price)
        deltas.append(delta)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    ax1.plot(interest_rates, prices, 'b-', linewidth=2)
    ax1.set_xlabel('无风险利率')
    ax1.set_ylabel('可转债价格')
    ax1.set_title('可转债价格 vs 无风险利率')
    ax1.grid(True, alpha=0.3)
    
    ax2.plot(interest_rates, deltas, 'g-', linewidth=2)
    ax2.set_xlabel('无风险利率')
    ax2.set_ylabel('Delta')
    ax2.set_title('Delta vs 无风险利率')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 保存图片
    figures_dir = get_figures_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fig_path = figures_dir / f"interest_rate_sensitivity_{timestamp}.png"
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    print(f"图片已保存到: {fig_path}")
    
    # 保存数据
    data_dir = get_data_dir()
    data_df = pd.DataFrame({
        'interest_rate': interest_rates,
        'price': prices,
        'delta': deltas
    })
    csv_path = data_dir / f"interest_rate_sensitivity_{timestamp}.csv"
    data_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"数据已保存到: {csv_path}")
    
    plt.show()
    
    print("观察：")
    print("- 利率对可转债价格的影响是复杂的：")
    print("  * 利率上升会降低债券部分的现值（负面影响）")
    print("  * 但会提高期权价值（正面影响，因为折现率上升）")
    print("- 净效应取决于可转债是更偏向债券还是更偏向期权")


def analyze_credit_spread_sensitivity():
    """分析信用利差敏感性"""
    contract = ConvertibleBondContract(
        face_value=100.0,
        coupon_rate=0.03,
        maturity=3.0,
        conversion_ratio=1.0,
        issue_price=100.0,
        coupon_freq=2,
    )
    
    r_curve = TermStructure(rate_fn=lambda t: 0.02)
    q_curve = TermStructure(rate_fn=lambda t: 0.01)
    
    S0 = 100.0
    vol = 0.25
    credit_spreads = np.linspace(0.00, 0.10, 20)
    prices = []
    deltas = []
    
    for spread in credit_spreads:
        credit_curve = CreditCurve(spread_fn=lambda t: spread)
        price, delta = price_convertible_bond_binomial(
            S0=S0,
            contract=contract,
            steps=50,
            vol=vol,
            r_curve=r_curve,
            q_curve=q_curve,
            credit_curve=credit_curve,
        )
        prices.append(price)
        deltas.append(delta)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    ax1.plot(credit_spreads, prices, 'b-', linewidth=2)
    ax1.set_xlabel('信用利差')
    ax1.set_ylabel('可转债价格')
    ax1.set_title('可转债价格 vs 信用利差')
    ax1.grid(True, alpha=0.3)
    
    ax2.plot(credit_spreads, deltas, 'g-', linewidth=2)
    ax2.set_xlabel('信用利差')
    ax2.set_ylabel('Delta')
    ax2.set_title('Delta vs 信用利差')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 保存图片
    figures_dir = get_figures_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fig_path = figures_dir / f"credit_spread_sensitivity_{timestamp}.png"
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    print(f"图片已保存到: {fig_path}")
    
    # 保存数据
    data_dir = get_data_dir()
    data_df = pd.DataFrame({
        'credit_spread': credit_spreads,
        'price': prices,
        'delta': deltas
    })
    csv_path = data_dir / f"credit_spread_sensitivity_{timestamp}.csv"
    data_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"数据已保存到: {csv_path}")
    
    plt.show()
    
    print("观察：")
    print("- 信用利差上升会降低可转债价格（因为折现率上升）")
    print("- 信用利差主要影响债券部分，对深度实值期权的 Delta 影响较小")


def main():
    """主函数"""
    print("=" * 60)
    print("参数敏感性分析")
    print("=" * 60)
    
    print("\n1. 波动率敏感性分析")
    analyze_volatility_sensitivity()
    
    print("\n2. 利率敏感性分析")
    analyze_interest_rate_sensitivity()
    
    print("\n3. 信用利差敏感性分析")
    analyze_credit_spread_sensitivity()
    
    print("\n分析完成！")


if __name__ == "__main__":
    main()
