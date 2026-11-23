"""
Tests for investigate_purchase() composed workflow
"""

import pytest
from src.purchase_workflow import investigate_purchase


def test_investigate_purchase_normal_product():
    # Sony WH-CH720N for 8999
    res = investigate_purchase("Sony WH-CH720N", 8999)
    assert res["success"] is True
    assert res["product"] is not None
    assert res["product"]["name"] == "Sony WH-CH720N"
    assert res["verdict"] in ["BUY", "WAIT"]
    assert res["value_score"] > 50
    assert "product_identification" in res["completed_steps"]
    assert "price_comparison" in res["completed_steps"]
    assert "calculate_value_score" in res["completed_steps"]
    assert res["confidence"] > 0.6


def test_investigate_purchase_product_not_found():
    res = investigate_purchase("NonExistentSuperGadget9999XYZ", 5000)
    assert res["success"] is False
    assert res["product"] is None
    assert "product_identification" in res["failed_steps"]
    assert res["verdict"] == "AVOID"


def test_investigate_purchase_insufficient_reviews():
    # AcousticPro Echo X1 (Scenario 4)
    res = investigate_purchase("AcousticPro Echo X1", 4900)
    assert res["success"] is True
    assert res["review_analysis"]["is_data_sufficient"] is False
    assert any("zero" in w.lower() or "insufficient" in w.lower() for w in res["warnings"])
    # Confidence should be downgraded
    assert res["confidence"] < 0.90


def test_investigate_purchase_missing_price_data():
    # HyperDrive Nova 5 (Scenario 5)
    res = investigate_purchase("HyperDrive Nova 5", 25000)
    assert res["success"] is True
    assert res["price_analysis"]["competitiveness_tier"] == "UNKNOWN"
    assert res["confidence"] < 0.90
