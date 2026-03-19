from dataclasses import dataclass


@dataclass(frozen=True)
class StrategyConfig:
    start_date: str = "2010-01-01"
    end_date: str | None = None
    ma_window: int = 30
    breakout_window: int = 20
    volume_window: int = 20
    relative_strength_window: int = 4
    top_n: int = 10
    flat_tolerance: float = 0.01
    require_52_week_high: bool = False
    commission_rate: float = 0.001425
    tax_rate: float = 0.003
    discount: float = 0.3
    initial_capital: float = 100000.0
