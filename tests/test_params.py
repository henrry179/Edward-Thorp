"""
测试参数定义模块
"""
import pytest
from cb_arb.params import (
    ConvertibleBondContract,
    TermStructure,
    CreditCurve,
)


class TestTermStructure:
    """测试期限结构"""

    def test_flat_curve(self):
        """测试平坦曲线"""
        curve = TermStructure(rate_fn=lambda t: 0.02)
        assert curve.r(0.0) == 0.02
        assert curve.r(1.0) == 0.02
        assert curve.r(5.0) == 0.02

    def test_time_dependent_curve(self):
        """测试时间依赖曲线"""
        curve = TermStructure(rate_fn=lambda t: 0.02 + 0.01 * t)
        assert curve.r(0.0) == 0.02
        assert curve.r(1.0) == 0.03
        assert curve.r(2.0) == 0.04


class TestCreditCurve:
    """测试信用曲线"""

    def test_flat_spread(self):
        """测试平坦信用利差"""
        curve = CreditCurve(spread_fn=lambda t: 0.03)
        assert curve.spread(0.0) == 0.03
        assert curve.spread(1.0) == 0.03
        assert curve.spread(5.0) == 0.03


class TestConvertibleBondContract:
    """测试可转债合约"""

    def test_basic_contract(self):
        """测试基本合约参数"""
        contract = ConvertibleBondContract(
            face_value=100.0,
            coupon_rate=0.03,
            maturity=3.0,
            conversion_ratio=1.0,
            issue_price=100.0,
        )
        assert contract.face_value == 100.0
        assert contract.coupon_rate == 0.03
        assert contract.maturity == 3.0
        assert contract.conversion_ratio == 1.0
        assert contract.call_price is None
        assert contract.put_price is None

    def test_contract_with_call_put(self):
        """测试带赎回回售条款的合约"""
        contract = ConvertibleBondContract(
            face_value=100.0,
            coupon_rate=0.03,
            maturity=3.0,
            conversion_ratio=1.0,
            issue_price=100.0,
            call_price=110.0,
            put_price=95.0,
            call_barrier=120.0,
            put_barrier=80.0,
        )
        assert contract.call_price == 110.0
        assert contract.put_price == 95.0
        assert contract.call_barrier == 120.0
        assert contract.put_barrier == 80.0
