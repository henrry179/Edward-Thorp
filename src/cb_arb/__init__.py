"""
cb_arb: Edward Thorp 风格可转债套利学习库

核心组件包括：
- 严谨的可转债合约与期限结构参数定义（params）
- 基于二叉树的可转债定价与 Delta 计算（cb_pricing）
- Delta 对冲引擎（delta_hedging）
- 错定价信号与 Z-score 生成（signals）
- 策略级回测框架（backtest）
"""

from .params import ConvertibleBondContract, TermStructure, CreditCurve
from .cb_pricing import price_convertible_bond_binomial

__all__ = [
    "ConvertibleBondContract",
    "TermStructure",
    "CreditCurve",
    "price_convertible_bond_binomial",
]

