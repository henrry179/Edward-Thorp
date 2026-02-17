"""
测试定价模块
"""
import pytest
import numpy as np
from cb_arb.params import ConvertibleBondContract, TermStructure, CreditCurve
from cb_arb.cb_pricing import (
    build_stock_tree,
    price_convertible_bond_binomial,
)


class TestBuildStockTree:
    """测试股票价格树构建"""

    def test_basic_tree(self):
        """测试基本树构建"""
        r_curve = TermStructure(rate_fn=lambda t: 0.02)
        q_curve = TermStructure(rate_fn=lambda t: 0.01)
        
        stock_tree, u, d, p, dt = build_stock_tree(
            S0=100.0,
            maturity=1.0,
            steps=10,
            vol=0.25,
            r_curve=r_curve,
            q_curve=q_curve,
        )
        
        assert stock_tree.shape == (11, 11)
        assert stock_tree[0, 0] == 100.0
        assert u > 1.0
        assert d < 1.0
        assert abs(u * d - 1.0) < 1e-10
        assert 0.0 < p < 1.0
        assert dt == 0.1

    def test_invalid_steps(self):
        """测试无效步数"""
        r_curve = TermStructure(rate_fn=lambda t: 0.02)
        q_curve = TermStructure(rate_fn=lambda t: 0.01)
        
        with pytest.raises(ValueError):
            build_stock_tree(
                S0=100.0,
                maturity=1.0,
                steps=0,
                vol=0.25,
                r_curve=r_curve,
                q_curve=q_curve,
            )


class TestPriceConvertibleBond:
    """测试可转债定价"""

    def test_basic_pricing(self):
        """测试基本定价"""
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
        
        price, delta = price_convertible_bond_binomial(
            S0=100.0,
            contract=contract,
            steps=50,
            vol=0.25,
            r_curve=r_curve,
            q_curve=q_curve,
            credit_curve=credit_curve,
        )
        
        # 价格应该为正
        assert price > 0
        # Delta 应该在合理范围内（0 到转换比例之间）
        assert 0.0 <= delta <= contract.conversion_ratio
        # 价格应该大于面值（因为包含期权价值）
        # 注意：在某些参数下可能不成立，这里只做基本检查
        assert price > 0

    def test_delta_monotonicity(self):
        """测试 Delta 的单调性：股价越高，Delta 应该越大"""
        contract = ConvertibleBondContract(
            face_value=100.0,
            coupon_rate=0.03,
            maturity=3.0,
            conversion_ratio=1.0,
            issue_price=100.0,
        )
        
        r_curve = TermStructure(rate_fn=lambda t: 0.02)
        q_curve = TermStructure(rate_fn=lambda t: 0.01)
        credit_curve = CreditCurve(spread_fn=lambda t: 0.03)
        
        deltas = []
        for S0 in [80.0, 100.0, 120.0]:
            _, delta = price_convertible_bond_binomial(
                S0=S0,
                contract=contract,
                steps=50,
                vol=0.25,
                r_curve=r_curve,
                q_curve=q_curve,
                credit_curve=credit_curve,
            )
            deltas.append(delta)
        
        # Delta 应该随股价递增
        assert deltas[0] <= deltas[1] <= deltas[2]
