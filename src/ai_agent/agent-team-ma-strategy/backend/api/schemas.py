"""Request/Response schemas for MA Golden Cross Backtest API."""

from datetime import date
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


class BacktestQuery(BaseModel):
    """Query parameters for backtest endpoint."""

    symbol: str = Field(..., description="Stock symbol (e.g., '2330.TW', 'AAPL')")
    start: date = Field(..., description="Start date")
    end: date = Field(..., description="End date")
    short_ma: int = Field(default=5, ge=1, le=365, description="Short-term MA window")
    long_ma: int = Field(default=20, ge=1, le=365, description="Long-term MA window")


class Trade(BaseModel):
    """Single trade record."""

    entry_date: str
    entry_price: float
    exit_date: str
    exit_price: float
    profit: float
    type: str


class BacktestResult(BaseModel):
    """Backtest execution result."""

    total_trades: int
    win_rate: float
    total_profit: float
    max_drawdown: float
    trades: List[Trade]


class OHLCV(BaseModel):
    """Single OHLCV bar."""

    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int


class MASignals(BaseModel):
    """MA indicator signals."""

    short_ma: List[float]
    long_ma: List[float]
    golden_crosses: List[str]
    death_crosses: List[str]


class BacktestResponse(BaseModel):
    """Full backtest API response."""

    symbol: str
    start_date: str
    end_date: str
    short_ma: int
    long_ma: int
    backtest_result: BacktestResult
    ohlcv: List[OHLCV]
    ma_signals: MASignals


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
