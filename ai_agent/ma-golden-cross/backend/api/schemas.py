"""
Pydantic schemas for request/response validation.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ErrorCode(str, Enum):
    """Standardized error codes."""

    MISSING_PARAMETER = "MISSING_PARAMETER"
    INVALID_TYPE = "INVALID_TYPE"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_DATE_RANGE = "INVALID_DATE_RANGE"
    DATA_FETCH_ERROR = "DATA_FETCH_ERROR"
    MA_CALCULATION_ERROR = "MA_CALCULATION_ERROR"
    BACKTEST_ERROR = "BACKTEST_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    INVALID_SYMBOL = "INVALID_SYMBOL"


class BacktestRequest(BaseModel):
    """Request schema for backtest endpoint."""

    symbol: str = Field(
        ...,
        description="Stock ticker symbol (e.g., '2330.TW', 'AAPL')",
        min_length=1,
        max_length=20,
        examples=["AAPL", "2330.TW", "MSFT"],
    )
    start_date: str = Field(
        ...,
        description="Start date in YYYY-MM-DD format",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        examples=["2024-01-01", "2023-06-15"],
    )
    end_date: str = Field(
        ...,
        description="End date in YYYY-MM-DD format",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        examples=["2024-12-31", "2024-06-30"],
    )
    short_ma: int = Field(
        default=5,
        description="Short-term MA period (default: 5)",
        ge=2,
        le=200,
        examples=[5, 10, 7],
    )
    long_ma: int = Field(
        default=20,
        description="Long-term MA period (default: 20)",
        ge=5,
        le=500,
        examples=[20, 50, 60],
    )
    initial_capital: float = Field(
        default=100000.0,
        description="Initial capital for backtest",
        ge=1000.0,
        le=100000000.0,
        examples=[100000.0, 50000.0],
    )

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Ensure dates are in correct format."""
        from datetime import datetime

        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid date format: {v}. Use YYYY-MM-DD")
        return v

    @field_validator("long_ma")
    @classmethod
    def validate_ma_windows(cls, v: int, info) -> int:
        """Ensure short_ma < long_ma."""
        short_ma = info.data.get("short_ma")
        if short_ma is not None and v <= short_ma:
            raise ValueError(
                f"long_ma ({v}) must be greater than short_ma ({short_ma})"
            )
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "symbol": "AAPL",
                    "start_date": "2024-01-01",
                    "end_date": "2024-12-31",
                    "short_ma": 5,
                    "long_ma": 20,
                    "initial_capital": 100000.0,
                }
            ]
        }
    }


class TradeSchema(BaseModel):
    """Individual trade in backtest result."""

    entry_date: str
    entry_price: float
    exit_date: str
    exit_price: float
    profit: float = Field(alias="profit_amount")
    profit_pct: float
    type: str = Field(alias="trade_type")
    holding_days: int

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "examples": [
                {
                    "entry_date": "2024-02-15",
                    "entry_price": 182.50,
                    "exit_date": "2024-03-01",
                    "exit_price": 188.20,
                    "profit": 571.0,
                    "profit_pct": 0.0312,
                    "type": "buy",
                    "holding_days": 14,
                }
            ]
        },
    }


class SummarySchema(BaseModel):
    """Summary statistics for backtest."""

    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_profit: float
    max_drawdown: float


class EquityPointSchema(BaseModel):
    """Single point in equity curve."""

    date: str
    capital: float


class KlineSchema(BaseModel):
    """OHLCV K-line data point."""

    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int


class CrossSchema(BaseModel):
    """MA cross event."""

    date: str
    type: str
    price: float
    ma_short: Optional[float] = None
    ma_long: Optional[float] = None
    action: str


class BacktestResponse(BaseModel):
    """Response schema for successful backtest."""

    symbol: str
    start_date: str
    end_date: str
    short_ma: int
    long_ma: int
    initial_capital: float
    final_capital: float
    summary: SummarySchema
    trades: list[TradeSchema]
    equity_curve: list[EquityPointSchema]
    klines: list[KlineSchema] = Field(default_factory=list)
    ma_short: list[Optional[float]] = Field(default_factory=list)
    ma_long: list[Optional[float]] = Field(default_factory=list)
    crosses: list[CrossSchema] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "symbol": "AAPL",
                    "start_date": "2024-01-01",
                    "end_date": "2024-12-31",
                    "short_ma": 5,
                    "long_ma": 20,
                    "initial_capital": 100000.0,
                    "final_capital": 112345.67,
                    "summary": {
                        "total_trades": 8,
                        "winning_trades": 5,
                        "losing_trades": 3,
                        "win_rate": 0.625,
                        "total_profit": 15000.0,
                        "max_drawdown": 0.0523,
                    },
                    "trades": [],
                    "equity_curve": [],
                    "klines": [],
                    "ma_short": [],
                    "ma_long": [],
                    "crosses": [],
                }
            ]
        }
    }


class ErrorResponse(BaseModel):
    """Standardized error response."""

    error: bool = True
    code: ErrorCode
    message: str
    details: Optional[dict] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "error": True,
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": {"symbol": "Field required"},
                }
            ]
        }
    }
