"""
Flask API routes for MA Golden Cross Backtest System.
"""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from backend.data.fetcher import fetch_stock_data, DataFetchError, validate_date_range
from backend.indicators.ma import calculate_ma, MAError
from backend.backtest.engine import run_backtest, BacktestError, BacktestResult
from backend.api.schemas import BacktestRequest, ErrorResponse, ErrorCode


api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint.

    Returns:
        JSON: {"status": "healthy", "service": "ma-golden-cross-api"}

    Error Responses:
        None (always returns 200 if service is running)
    """
    return jsonify(
        {
            "status": "healthy",
            "service": "ma-golden-cross-api",
        }
    )


@api_bp.route("/backtest", methods=["GET"])
def get_backtest():
    """
    Run golden cross backtest for given parameters.

    Query Parameters:
        symbol (str, required): Stock ticker (e.g., "2330.TW", "AAPL")
        start_date (str, required): Start date in "YYYY-MM-DD" format
        end_date (str, required): End date in "YYYY-MM-DD" format
        short_ma (int, optional): Short MA period (default: 5, min: 2)
        long_ma (int, optional): Long MA period (default: 20, min: 5)
        initial_capital (float, optional): Starting capital (default: 100000.0)

    Returns:
        200: BacktestResponse JSON
        400: ErrorResponse if validation fails
        404: ErrorResponse if stock data not found
        500: ErrorResponse if server error occurs

    Success Response Format (200):
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
                "winning_trades": 3,
                "win_rate": 0.625,
                "total_profit": 15000.0,
                "max_drawdown": 0.0523
            },
            "trades": [
                {
                    "entry_date": "2024-02-15",
                    "entry_price": 182.50,
                    "exit_date": "2024-03-01",
                    "exit_price": 188.20,
                    "profit": 571.0,
                    "profit_pct": 0.0312,
                    "type": "buy",
                    "holding_days": 14
                }
            ],
            "equity_curve": [
                {"date": "2024-02-15", "capital": 100000.0},
                {"date": "2024-03-01", "capital": 100571.0}
            ],
            "klines": [...],
            "ma_short": [...],
            "ma_long": [...],
            "crosses": [...]
        }

    Error Response Format (all errors):
        {
            "error": true,
            "code": "VALIDATION_ERROR",
            "message": "Human-readable error message",
            "details": {"field": "specific error info"}
        }
    """
    try:
        # Parse and validate query parameters
        symbol = request.args.get("symbol")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        short_ma = request.args.get("short_ma", "5")
        long_ma = request.args.get("long_ma", "20")
        initial_capital = request.args.get("initial_capital", "100000.0")

        # Validate required parameters
        missing = []
        if not symbol:
            missing.append("symbol")
        if not start_date:
            missing.append("start_date")
        if not end_date:
            missing.append("end_date")

        if missing:
            return jsonify(
                ErrorResponse(
                    error=True,
                    code=ErrorCode.MISSING_PARAMETER,
                    message=f"Missing required parameters: {', '.join(missing)}",
                    details={"missing_fields": missing},
                ).model_dump()
            ), 400

        # Parse types
        try:
            short_ma_int = int(short_ma)
            long_ma_int = int(long_ma)
            initial_capital_float = float(initial_capital)
        except ValueError as e:
            return jsonify(
                ErrorResponse(
                    error=True,
                    code=ErrorCode.INVALID_TYPE,
                    message="short_ma, long_ma must be integers; initial_capital must be numeric",
                    details={"error": str(e)},
                ).model_dump()
            ), 400

        # Validate using Pydantic
        try:
            req = BacktestRequest(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                short_ma=short_ma_int,
                long_ma=long_ma_int,
                initial_capital=initial_capital_float,
            )
        except ValidationError as e:
            # Convert Pydantic errors to our format
            details = {}
            for err in e.errors():
                field = ".".join(str(loc) for loc in err["loc"])
                details[field] = err["msg"]
            return jsonify(
                ErrorResponse(
                    error=True,
                    code=ErrorCode.VALIDATION_ERROR,
                    message="Request validation failed",
                    details=details,
                ).model_dump()
            ), 400

        # Validate date range
        try:
            validate_date_range(req.start_date, req.end_date)
        except DataFetchError as e:
            return jsonify(
                ErrorResponse(
                    error=True,
                    code=ErrorCode.INVALID_DATE_RANGE,
                    message=str(e),
                ).model_dump()
            ), 400

        # Fetch stock data
        try:
            stock_data = fetch_stock_data(
                symbol=req.symbol,
                start_date=req.start_date,
                end_date=req.end_date,
            )
        except DataFetchError as e:
            error_msg = str(e)
            if "No data returned" in error_msg or "Invalid" in error_msg:
                return jsonify(
                    ErrorResponse(
                        error=True,
                        code=ErrorCode.INVALID_SYMBOL,
                        message=f"Invalid stock symbol provided: {req.symbol}",
                    ).model_dump()
                ), 404
            return jsonify(
                ErrorResponse(
                    error=True,
                    code=ErrorCode.DATA_FETCH_ERROR,
                    message=error_msg,
                ).model_dump()
            ), 404

        # Calculate MAs
        try:
            ma_result = calculate_ma(
                df=stock_data.df,
                short_window=req.short_ma,
                long_window=req.long_ma,
            )
        except (MAError, ValueError) as e:
            return jsonify(
                ErrorResponse(
                    error=True,
                    code=ErrorCode.MA_CALCULATION_ERROR,
                    message=str(e),
                ).model_dump()
            ), 400

        # Run backtest
        try:
            result = run_backtest(
                df=stock_data.df,
                ma_short=ma_result.ma_short,
                ma_long=ma_result.ma_long,
                symbol=req.symbol,
                start_date=req.start_date,
                end_date=req.end_date,
                short_ma=req.short_ma,
                long_ma=req.long_ma,
                initial_capital=req.initial_capital,
            )
        except BacktestError as e:
            return jsonify(
                ErrorResponse(
                    error=True,
                    code=ErrorCode.BACKTEST_ERROR,
                    message=str(e),
                ).model_dump()
            ), 400

        # Build response with all required fields
        response_data = _build_response(result, stock_data.df, ma_result, req)
        return jsonify(response_data), 200

    except Exception as e:
        # Catch-all for unexpected errors
        return jsonify(
            ErrorResponse(
                error=True,
                code=ErrorCode.INTERNAL_ERROR,
                message=f"Internal server error: {str(e)}",
            ).model_dump()
        ), 500


def _build_response(
    result: BacktestResult, df, ma_result, req: BacktestRequest
) -> dict:
    """Build the complete response dictionary."""
    from backend.backtest.engine import CrossType

    # Prepare klines data
    klines = []
    for _, row in df.iterrows():
        klines.append(
            {
                "date": str(row["Date"]),
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": int(row["Volume"]) if "Volume" in row else 0,
            }
        )

    # Prepare MA series (convert to list, preserving NaN)
    ma_short_list = [
        float(x) if not (hasattr(x, "isna") and x.isna()) else None
        for x in ma_result.ma_short.tolist()
    ]
    ma_long_list = [
        float(x) if not (hasattr(x, "isna") and x.isna()) else None
        for x in ma_result.ma_long.tolist()
    ]

    # Detect and prepare crosses
    crosses = []
    if len(ma_short_list) > 1:
        for i in range(1, len(ma_short_list)):
            prev_short = ma_short_list[i - 1]
            curr_short = ma_short_list[i]
            prev_long = ma_long_list[i - 1]
            curr_long = ma_long_list[i]

            if (
                prev_short is None
                or curr_short is None
                or prev_long is None
                or curr_long is None
            ):
                continue

            # Golden cross: short crosses above long
            if prev_short <= prev_long and curr_short > curr_long:
                crosses.append(
                    {
                        "date": klines[i]["date"] if i < len(klines) else None,
                        "type": CrossType.GOLDEN.value,
                        "price": klines[i]["close"] if i < len(klines) else None,
                        "ma_short": curr_short,
                        "ma_long": curr_long,
                        "action": "BUY",
                    }
                )
            # Death cross: short crosses below long
            elif prev_short >= prev_long and curr_short < curr_long:
                crosses.append(
                    {
                        "date": klines[i]["date"] if i < len(klines) else None,
                        "type": CrossType.DEATH.value,
                        "price": klines[i]["close"] if i < len(klines) else None,
                        "ma_short": curr_short,
                        "ma_long": curr_long,
                        "action": "SELL",
                    }
                )

    # Prepare equity curve with correct field name
    equity_curve = [
        {"date": eq["date"], "capital": eq["value"]} for eq in result.equity_curve
    ]

    # Prepare trades with correct field names
    trades = []
    for t in result.trades:
        trades.append(
            {
                "entry_date": t.entry_date,
                "entry_price": round(t.entry_price, 2),
                "exit_date": t.exit_date,
                "exit_price": round(t.exit_price, 2),
                "profit": round(t.profit_amount, 2),
                "profit_pct": round(t.profit_pct, 4),
                "type": t.trade_type.value,
                "holding_days": t.holding_days,
            }
        )

    # Build summary
    summary = {
        "total_trades": result.summary.total_trades,
        "winning_trades": result.summary.winning_trades,
        "losing_trades": result.summary.losing_trades,
        "win_rate": round(result.summary.win_rate, 4),
        "total_profit": round(result.summary.total_profit, 2),
        "max_drawdown": round(result.summary.max_drawdown, 4),
    }

    return {
        "symbol": result.symbol,
        "start_date": result.start_date,
        "end_date": result.end_date,
        "short_ma": result.short_ma,
        "long_ma": result.long_ma,
        "initial_capital": result.initial_capital,
        "final_capital": result.final_capital,
        "summary": summary,
        "trades": trades,
        "equity_curve": equity_curve,
        "klines": klines,
        "ma_short": ma_short_list,
        "ma_long": ma_long_list,
        "crosses": crosses,
    }
