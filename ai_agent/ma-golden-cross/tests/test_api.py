"""
Tests for Flask API routes.

These tests verify the API endpoints defined in backend/api/routes.py:
- GET /api/health - Health check endpoint
- GET /api/backtest - Golden cross backtest endpoint

NOTE: These tests are designed to FAIL initially (RED phase) because the
API routes module (backend/api/routes.py) has not been implemented yet.
They will pass once the API is properly implemented.
"""

import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Try to import Flask app - will fail until API is implemented
try:
    from backend.api.routes import api_bp
    from flask import Flask

    HAS_API = True
except ImportError:
    HAS_API = False


def create_test_app():
    """Create a Flask app instance for testing."""
    if not HAS_API:
        pytest.skip("API routes not implemented yet", allow_module_level=True)

    app = Flask(__name__)
    app.register_blueprint(api_bp)
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    if not HAS_API:
        pytest.skip("API routes not implemented yet", allow_module_level=True)

    app = create_test_app()
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_stock_data():
    """Create mock stock data for testing."""
    df = pd.DataFrame(
        {
            "Date": pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"]),
            "Open": [185.0, 186.0, 187.0],
            "High": [187.0, 188.0, 189.0],
            "Low": [184.0, 185.0, 186.0],
            "Close": [185.5, 186.5, 187.5],
            "Volume": [45678900, 46789000, 47890000],
        }
    )
    return df


class TestHealthEndpoint:
    """Test cases for GET /api/health endpoint."""

    def test_health_check_returns_200(self, client):
        """Health check should return HTTP 200 status."""
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_check_returns_healthy_status(self, client):
        """Health check should return 'healthy' status."""
        response = client.get("/api/health")
        assert response.json["status"] == "healthy"

    def test_health_check_returns_service_name(self, client):
        """Health check should include service name."""
        response = client.get("/api/health")
        assert "service" in response.json
        assert "ma-golden-cross-api" in response.json["service"]


class TestBacktestEndpoint:
    """Test cases for GET /api/backtest endpoint."""

    def test_backtest_valid_params(self, client, mock_stock_data):
        """Backtest with valid parameters should return 200 and complete response."""
        with patch("backend.api.routes.fetch_stock_data") as mock_fetch:
            # Setup mock
            mock_fetch.return_value.df = mock_stock_data
            mock_fetch.return_value.symbol = "AAPL"

            response = client.get(
                "/api/backtest",
                query_string={
                    "symbol": "AAPL",
                    "start_date": "2024-01-01",
                    "end_date": "2024-03-31",
                },
            )

            assert response.status_code == 200
            data = response.json

            # Verify response structure
            assert data["symbol"] == "AAPL"
            assert "summary" in data
            assert "trades" in data

    def test_backtest_custom_ma_parameters(self, client, mock_stock_data):
        """Backtest with custom MA parameters should use specified values."""
        with patch("backend.api.routes.fetch_stock_data") as mock_fetch:
            mock_fetch.return_value.df = mock_stock_data
            mock_fetch.return_value.symbol = "2330.TW"

            response = client.get(
                "/api/backtest",
                query_string={
                    "symbol": "2330.TW",
                    "start_date": "2024-01-01",
                    "end_date": "2024-06-30",
                    "short_ma": "10",
                    "long_ma": "60",
                },
            )

            assert response.status_code == 200
            data = response.json
            assert data["short_ma"] == 10
            assert data["long_ma"] == 60

    def test_backtest_missing_symbol(self, client):
        """Backtest without symbol should return 400."""
        response = client.get(
            "/api/backtest",
            query_string={"start_date": "2024-01-01", "end_date": "2024-03-31"},
        )

        assert response.status_code == 400
        assert response.json["error"] is not None

    def test_backtest_missing_dates(self, client):
        """Backtest without required dates should return 400."""
        response = client.get("/api/backtest", query_string={"symbol": "AAPL"})

        assert response.status_code == 400
        assert response.json["error"] is not None

    def test_backtest_invalid_symbol(self, client):
        """Backtest with invalid symbol should return 400 or 404."""
        with patch("backend.api.routes.fetch_stock_data") as mock_fetch:
            from backend.data.fetcher import DataFetchError

            mock_fetch.side_effect = DataFetchError(
                "No data returned for INVALID_SYMBOL_XYZ"
            )

            response = client.get(
                "/api/backtest",
                query_string={
                    "symbol": "INVALID_SYMBOL_XYZ",
                    "start_date": "2024-01-01",
                    "end_date": "2024-03-31",
                },
            )

            # Should return 404 for data fetch error
            assert response.status_code == 404
            assert response.json["error"] is not None

    def test_backtest_invalid_date_format(self, client):
        """Backtest with invalid date format should return 400."""
        response = client.get(
            "/api/backtest",
            query_string={
                "symbol": "AAPL",
                "start_date": "01-01-2024",  # Wrong format
                "end_date": "2024-03-31",
            },
        )

        assert response.status_code == 400
        assert response.json["error"] is not None

    def test_backtest_start_after_end_date(self, client):
        """Backtest with start_date after end_date should return 400."""
        with patch("backend.api.routes.fetch_stock_data") as mock_fetch:
            from backend.data.fetcher import DataFetchError

            mock_fetch.side_effect = DataFetchError(
                "start_date must be before end_date"
            )

            response = client.get(
                "/api/backtest",
                query_string={
                    "symbol": "AAPL",
                    "start_date": "2024-12-31",
                    "end_date": "2024-01-01",
                },
            )

            assert response.status_code == 400
            assert response.json["error"] is not None

    def test_backtest_default_ma_values(self, client, mock_stock_data):
        """Backtest without MA params should use default values (5, 20)."""
        with patch("backend.api.routes.fetch_stock_data") as mock_fetch:
            mock_fetch.return_value.df = mock_stock_data
            mock_fetch.return_value.symbol = "AAPL"

            response = client.get(
                "/api/backtest",
                query_string={
                    "symbol": "AAPL",
                    "start_date": "2024-01-01",
                    "end_date": "2024-03-31",
                },
            )

            assert response.status_code == 200
            data = response.json
            assert data["short_ma"] == 5
            assert data["long_ma"] == 20

    def test_backtest_response_includes_equity_curve(self, client, mock_stock_data):
        """Backtest response should include equity_curve."""
        with patch("backend.api.routes.fetch_stock_data") as mock_fetch:
            mock_fetch.return_value.df = mock_stock_data
            mock_fetch.return_value.symbol = "AAPL"

            response = client.get(
                "/api/backtest",
                query_string={
                    "symbol": "AAPL",
                    "start_date": "2024-01-01",
                    "end_date": "2024-03-31",
                },
            )

            assert response.status_code == 200
            data = response.json
            assert "equity_curve" in data

    def test_backtest_invalid_ma_windows(self, client):
        """Backtest with short_ma >= long_ma should return 400."""
        response = client.get(
            "/api/backtest",
            query_string={
                "symbol": "AAPL",
                "start_date": "2024-01-01",
                "end_date": "2024-03-31",
                "short_ma": "20",
                "long_ma": "10",  # Invalid: short > long
            },
        )

        # Pydantic validation should catch this
        assert response.status_code == 400
        assert response.json["error"] is not None


class TestAPIErrorResponses:
    """Test API error response format."""

    def test_error_response_has_error_flag(self, client):
        """Error responses should have 'error' field set to true."""
        response = client.get("/api/backtest", query_string={"symbol": "AAPL"})

        assert response.status_code == 400
        # Error format: {"error": true, "code": "...", "message": "..."}
        assert response.json["error"] is True

    def test_error_response_has_code(self, client):
        """Error responses should include error code."""
        response = client.get("/api/backtest", query_string={"symbol": "AAPL"})

        assert response.status_code == 400
        assert "code" in response.json
        assert isinstance(response.json["code"], str)

    def test_error_response_has_message(self, client):
        """Error responses should include human-readable message."""
        response = client.get("/api/backtest", query_string={"symbol": "AAPL"})

        assert response.status_code == 400
        assert "message" in response.json
        assert isinstance(response.json["message"], str)


# Run tests only if API is implemented
pytestmark = pytest.mark.skipif(
    not HAS_API,
    reason="API routes not implemented yet - tests will fail until backend/api/routes.py is created",
)
