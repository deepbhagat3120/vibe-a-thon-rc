"""
Unit tests for product_search, discount_analysis, spec_comparison, and value_scoring.
"""

import pytest
from src.product_search import search_product
from src.discount_analysis import find_discounts
from src.spec_comparison import compare_specs
from src.value_scoring import calculate_value_score


def test_search_product_exact_and_fuzzy():
    # Exact / clean match
    res = search_product("Sony WH-CH720N")
    assert res["found"] is True
    assert res["product"]["id"] == "prod_sony_wh_ch720n"

    # Fuzzy match with lowercase / partial
    res_fuzzy = search_product("macbook air m2")
    assert res_fuzzy["found"] is True
    assert res_fuzzy["product"]["brand"] == "Apple"

    # Not found
    res_missing = search_product("NonExistentGadgetXYZ")
    assert res_missing["found"] is False
    assert len(res_missing["candidate_names"]) > 0


def test_find_discounts_calculation():
    product = {
        "id": "p_disc",
        "current_price": 10000,
        "mrp": 12000,
        "discounts": [
            {"type": "bank", "description": "10% bank discount", "percent": 10, "max_discount": 800, "code": "BANK10"},
            {"type": "coupon", "description": "Flat 300 coupon", "amount": 300, "code": "SAVE300"}
        ]
    }
    res = find_discounts(product, base_price=10000)
    assert res["success"] is True
    assert res["has_discounts"] is True
    # Bank saving is min(10% of 10000, 800) = 800. Coupon saving = 300. Total = 1100.
    assert res["total_savings"] == 1100.0
    assert res["effective_price"] == 8900.0
    assert len(res["assumptions"]) >= 2


def test_compare_specs():
    target = {
        "name": "Headphone A",
        "category": "Headphones",
        "current_price": 5000,
        "specifications": {
            "battery_life_hours": 35,
            "weight_grams": 190,
            "noise_cancellation": "Active"
        }
    }
    alternatives = [
        {
            "name": "Headphone B",
            "price": 6000,
            "specifications": {
                "battery_life_hours": 20,
                "weight_grams": 250
            }
        }
    ]
    res = compare_specs(target, alternatives)
    assert res["success"] is True
    assert "battery life" in str(res["compared_attributes"]).lower()
    assert len(res["key_strengths"]) > 0


def test_calculate_value_score():
    data = {
        "product": {"pros": ["Great ANC", "Light"], "cons": ["Plastic"]},
        "price_analysis": {"competitiveness_tier": "EXCELLENT", "difference_percent_lowest": -5.0},
        "review_analysis": {"is_data_sufficient": True, "dataset_rating": 4.5, "sentiment_distribution": {"positive": 80.0, "negative": 5.0}},
        "spec_comparison": {"key_strengths": ["Longer battery"], "key_tradeoffs": []}
    }
    res = calculate_value_score(data)
    score = res["overall_score"]
    assert 0 <= score <= 100
    assert score >= 75  # Excellent price + high rating + positive sentiment should score high
    assert "explanation" in res
