"""Flask API routes for MA Golden Cross Backtest System."""

from datetime import datetime
from flask import Blueprint, request, jsonify

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from data.fetcher import fetch_stock_data
from indicators.ma import calculate_ma, detect_crossover
from backtest.engine import run_backtest

from .schemas import (
    BacktestResponse,
    HealthResponse,
    Trade,
    BacktestResult,
    OHLCV,
    MASignals,
)

api_bp = Blueprint("api", __name__, url_prefix="/api")

API_VERSION = "1.0.0"


@api_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify(HealthResponse(status="healthy", version=API_VERSION).model_dump())


@api_bp.route("/backtest", methods=["GET"])
def backtest():
    """Execute MA golden cross backtest with given parameters."""
    symbol = request.args.get("symbol")
    start = request.args.get("start")
    end = request.args.get("end")
    short_ma = request.args.get("short_ma", 5, type=int)
    long_ma = request.args.get("long_ma", 20, type=int)

    if not all([symbol, start, end]):
        return jsonify(
            {"error": "Missing required parameters: symbol, start, end"}
        ), 400

    try:
        start_date = datetime.strptime(start, "%Y-%m-%d").date()
        end_date = datetime.strptime(end, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    try:
        df = fetch_stock_data(symbol, start, end)
        if df.empty:
            return jsonify({"error": f"No data found for symbol {symbol}"}), 404

        df = calculate_ma(df, short_ma, long_ma)
        short_col = f"ma_{short_ma}"
        long_col = f"ma_{long_ma}"
        df = detect_crossover(df, short_col, long_col)

        result = run_backtest(df, short_col=short_col, long_col=long_col)

        ohlcv_list = [
            OHLCV(
                date=row["date"],
                open=row["open"],
                high=row["high"],
                low=row["low"],
                close=row["close"],
                volume=int(row["volume"]),
            ).model_dump()
            for _, row in df.iterrows()
        ]

        short_ma_list = df[short_col].tolist()
        long_ma_list = df[long_col].tolist()
        golden_crosses = df[df["signal"] == "golden_cross"]["date"].tolist()
        death_crosses = df[df["signal"] == "death_cross"]["date"].tolist()

        trades_list = [Trade(**t).model_dump() for t in result["trades"]]
        backtest_result = BacktestResult(
            total_trades=result["total_trades"],
            win_rate=result["win_rate"],
            total_profit=result["total_profit"],
            max_drawdown=result["max_drawdown"],
            trades=trades_list,
        ).model_dump()

        response = BacktestResponse(
            symbol=symbol,
            start_date=start,
            end_date=end,
            short_ma=short_ma,
            long_ma=long_ma,
            backtest_result=backtest_result,
            ohlcv=ohlcv_list,
            ma_signals=MASignals(
                short_ma=short_ma_list,
                long_ma=long_ma_list,
                golden_crosses=golden_crosses,
                death_crosses=death_crosses,
            ).model_dump(),
        )

        return jsonify(response.model_dump())

    except Exception as e:
        return jsonify({"error": str(e)}), 500
