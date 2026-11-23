"""
Tests for Function 2: compare_prices()
"""

import pytest
from src.price_analysis import compare_prices


@pytest.fixture
def sample_product():
    return {
        "id": "test_headphones",
        "name": "Test Wireless ANC",
        "mrp": 12000,
        "current_price": 9000,
        "market_prices": [
            {"source": "Amazon", "price": 8000, "in_stock": True},
            {"source": "Flipkart", "price": 8500, "in_stock": True},
            {"source": "Croma", "price": 9000, "in_stock": True}
        ]
    }


def test_compare_prices_lowest_price(sample_product):
    # Lowest market price is 8000. User offers 7500 (lower)
    result = compare_prices(sample_product, 7500)
    assert result["success"] is True
    assert result["lowest_market_price"] == 8000
    assert result["competitiveness_tier"] == "EXCELLENT"
    assert result["is_competitive"] is True
    assert result["difference_from_lowest"] == -500.0


def test_compare_prices_fair(sample_product):
    # Average is (8000 + 8500 + 9000)/3 = 8500. User offers 8400 (between 8000 and 8500)
    result = compare_prices(sample_product, 8400)
    assert result["success"] is True
    assert result["competitiveness_tier"] in ["FAIR", "GOOD"]
    assert result["is_competitive"] is True


def test_compare_prices_overpriced(sample_product):
    # User offers 11000 (well above 8500 avg and 8000 min)
    result = compare_prices(sample_product, 11000)
    assert result["success"] is True
    assert result["competitiveness_tier"] == "OVERPRICED"
    assert result["is_competitive"] is False
    assert result["difference_from_lowest"] == 3000.0


def test_compare_prices_invalid_input(sample_product):
    # Negative price
    result_neg = compare_prices(sample_product, -500)
    assert result_neg["success"] is False

    # Zero price
    result_zero = compare_prices(sample_product, 0)
    assert result_zero["success"] is False


def test_compare_prices_missing_market_data():
    empty_product = {
        "id": "empty_prod",
        "name": "Empty Prod",
        "mrp": 0,
        "current_price": 0,
        "market_prices": []
    }
    result = compare_prices(empty_product, 5000)
    assert result["success"] is True
    assert result["competitiveness_tier"] == "UNKNOWN"
    assert result["market_samples_count"] == 0
