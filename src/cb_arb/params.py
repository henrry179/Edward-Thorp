from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class TermStructure:
    """
    简化版期限结构：给定时间 t (年)，返回对应年化利率 r(t) 或股利率 q(t)。

    为了保持数学严谨性，这里使用一个可注入的函数 rate_fn:
        rate_fn: Callable[[float], float]
    用户可以根据需要构造平坦曲线、分段常数曲线或插值曲线。
    """

    rate_fn: Callable[[float], float]

    def r(self, t: float) -> float:
        return float(self.rate_fn(t))


@dataclass
class CreditCurve:
    """
    信用曲线：给定时间 t (年)，返回年化信用利差或违约强度近似。

    在本项目初始版本中，我们采用“信用利差近似折现”的做法：
        discount rate ≈ r(t) + spread(t)
    后续可以扩展为显式违约树或强度模型。
    """

    spread_fn: Callable[[float], float]

    def spread(self, t: float) -> float:
        return float(self.spread_fn(t))


@dataclass
class ConvertibleBondContract:
    """
    可转债合约的基本参数，兼顾严谨性与教学清晰度。
    """

    face_value: float  # 票面，例如 100
    coupon_rate: float  # 年化票息率，例如 0.03
    maturity: float  # 到期时间（年）
    conversion_ratio: float  # 每张债对应的可转股股数
    issue_price: float  # 发行价/面值价格

    # 赎回/回售条款（如无则留空）
    call_price: Optional[float] = None
    put_price: Optional[float] = None
    call_barrier: Optional[float] = None
    put_barrier: Optional[float] = None

    # 票息频率，例如 1=年付, 2=半年付, 4=季付
    coupon_freq: int = 1

